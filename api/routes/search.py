from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from api.utils.responses import success_response, error_response
from api.utils.auth import token_dependency
from api.utils.browser.google_search import search_google
from api.utils.logging_config import get_logger
from config import settings
import base64
import asyncio
import time
from datetime import datetime

# Ottieni un logger configurato per questo modulo
logger = get_logger(__name__)

# Definizione dei modelli di dati
class SearchResult(BaseModel):
    title: str
    url: Optional[str]
    description: Optional[str]
    page: Optional[int]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    stats: Optional[str]
    pages_fetched: Optional[int]
    debug_info: Optional[Dict[str, Any]] = None

# Sistema di rate limiting (semplice)
class RateLimiter:
    def __init__(self, rate_limit: int = 10, cooldown: int = 60):
        self.rate_limit = rate_limit
        self.cooldown = cooldown
        self.requests = []
        self.cooldown_until = None
    
    def check_limit(self, client_id: str = "default") -> bool:
        """Verifica se il client può effettuare una nuova richiesta"""
        now = time.time()
        
        # Rimuovi richieste più vecchie di un minuto
        self.requests = [r for r in self.requests if now - r["timestamp"] < 60]
        
        # Controlla se è in cooldown
        if self.cooldown_until and now < self.cooldown_until:
            cooldown_end = datetime.fromtimestamp(self.cooldown_until).strftime('%H:%M:%S')
            logger.warning(f"Client {client_id} in cooldown fino a {cooldown_end}")
            return False
        
        # Controlla il rate limit
        client_requests = [r for r in self.requests if r["client_id"] == client_id]
        if len(client_requests) >= self.rate_limit:
            logger.warning(f"Rate limit superato per il client {client_id} ({len(client_requests)}/{self.rate_limit} richieste). Impostazione cooldown di {self.cooldown} secondi.")
            self.cooldown_until = now + self.cooldown
            return False
        
        # Registra la nuova richiesta
        self.requests.append({
            "timestamp": now,
            "client_id": client_id
        })
        
        logger.debug(f"Richiesta consentita per client {client_id}. Richieste attuali: {len(client_requests) + 1}/{self.rate_limit}")
        return True

# Creazione del rate limiter
rate_limiter = RateLimiter(
    rate_limit=settings.SEARCH_RATE_LIMIT,
    cooldown=settings.SEARCH_COOLDOWN
)

# Creazione del router
router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get("/google")
async def google_search(
    query: str = Query(..., description="Query di ricerca"),
    lang: str = Query(settings.GOOGLE_DEFAULT_LANG, description="Lingua dei risultati (es: it, en, fr)"),
    num_results: int = Query(5, description="Numero di risultati da restituire per pagina", ge=1, le=settings.GOOGLE_MAX_RESULTS),
    max_pages: int = Query(1, description="Numero massimo di pagine da consultare", ge=1, le=10),
    sleep_interval: float = Query(settings.GOOGLE_SLEEP_INTERVAL, description="Pausa in secondi tra le richieste"),
    include_screenshot: bool = Query(False, description="Includere screenshot del risultato per debug"),
    use_stealth: bool = Query(settings.BROWSER_STEALTH_MODE, description="Utilizzare tecniche stealth per evitare blocchi"),
    use_proxy: bool = Query(settings.USE_PROXIES, description="Utilizzare un proxy per la richiesta"),
    retry_count: int = Query(2, description="Numero di tentativi in caso di errore"),
    token: str = token_dependency
):
    """
    Esegue una ricerca su Google e restituisce i risultati, supportando la paginazione.
    
    Args:
        query: La query di ricerca
        lang: Lingua dei risultati (es: it, en, fr)
        num_results: Numero di risultati da restituire per pagina (max 20)
        max_pages: Numero massimo di pagine da consultare (default 1, max 10)
        sleep_interval: Pausa in secondi tra le richieste
        include_screenshot: Includere screenshot del risultato per debug
        use_stealth: Utilizzare tecniche stealth per evitare blocchi
        use_proxy: Utilizzare un proxy per la richiesta
        
    Returns:
        dict: Risposta con i risultati della ricerca
    """
    # Controllo rate limiting
    if not rate_limiter.check_limit(client_id=token):
        logger.warning(f"Rate limit superato per la ricerca: '{query}'")
        return error_response(
            message="Troppe richieste. Riprova più tardi.",
            error_type="RateLimitExceeded",
            status_code=429
        )
    
    try:
        logger.info(f"Avvio ricerca Google (GET): '{query}' in lingua {lang}, max {num_results} risultati per pagina, max {max_pages} pagine")
        logger.debug(f"Parametri ricerca: sleep_interval={sleep_interval}, use_stealth={use_stealth}, use_proxy={use_proxy}, retry_count={retry_count}")
        
        # Esegui la ricerca su Google con timeout
        start_time = time.time()
        try:
            search_results = await asyncio.wait_for(
                search_google(
                    query=query,
                    lang=lang,
                    num_results=num_results,
                    sleep_interval=sleep_interval,
                    retry_count=retry_count,
                    max_pages=max_pages
                ), 
                timeout=settings.SEARCH_TIMEOUT * max_pages  # Aumenta il timeout in base al numero di pagine
            )
        except asyncio.TimeoutError:
            elapsed_time = time.time() - start_time
            logger.error(f"Timeout dopo {elapsed_time:.2f}s durante la ricerca di '{query}' (timeout: {settings.SEARCH_TIMEOUT * max_pages}s)")
            return error_response(
                message=f"La ricerca ha impiegato troppo tempo per completarsi",
                error_type="SearchTimeout",
                details={"query": query, "elapsed_seconds": round(elapsed_time, 2)}
            )
        
        # Calcola il tempo impiegato
        elapsed_time = time.time() - start_time
        
        # Log dei risultati ottenuti
        result_count = len(search_results.get("results", []))
        pages_fetched = search_results.get("pages_fetched", 1)
        logger.info(f"Ricerca completata in {elapsed_time:.2f}s: trovati {result_count} risultati in {pages_fetched} pagine per '{query}'")
        
        # Verifica se abbiamo trovato un errore specifico di Google
        if "ERRORE:" in search_results.get("stats", ""):
            logger.warning(f"Google ha bloccato la richiesta per '{query}' (possibile CAPTCHA)")
            return error_response(
                message="Google ha rilevato attività insolita e ha bloccato la richiesta. Riprova più tardi.",
                error_type="GoogleBlockError",
                details={"query": query}
            )
        
        # Prepara i dati di debug
        debug_info = None
        if include_screenshot and "screenshot" in search_results:
            logger.debug(f"Includendo screenshot nei risultati per '{query}'")
            debug_info = {
                "screenshot": search_results["screenshot"]
            }
            if "html_snippet" in search_results and search_results["html_snippet"]:
                debug_info["html_snippet"] = search_results["html_snippet"]
        
        # Formatta la risposta
        response_data = {
            "query": search_results["query"],
            "results": search_results["results"],
            "stats": search_results.get("stats", ""),
            "pages_fetched": pages_fetched
        }
        
        # Aggiungi info di debug se richiesto
        if debug_info:
            response_data["debug_info"] = debug_info
        
        # Restituisci una risposta formattata con i risultati
        return success_response(
            data=response_data,
            message=f"Ricerca completata con successo: {query} ({result_count} risultati da {pages_fetched} pagine)"
        )
    except Exception as e:
        logger.error(f"Errore durante la ricerca: {str(e)}", exc_info=True)
        return error_response(
            message=f"Impossibile completare la ricerca: {str(e)}",
            error_type="SearchError",
            details={"query": query}
        )

@router.post("/google")
async def google_search_post(
    query: str = Query(..., description="Query di ricerca"),
    lang: str = Query(settings.GOOGLE_DEFAULT_LANG, description="Lingua dei risultati (es: it, en, fr)"),
    num_results: int = Query(5, description="Numero di risultati da restituire per pagina", ge=1, le=settings.GOOGLE_MAX_RESULTS),
    max_pages: int = Query(1, description="Numero massimo di pagine da consultare", ge=1, le=10),
    sleep_interval: float = Query(settings.GOOGLE_SLEEP_INTERVAL, description="Pausa in secondi tra le richieste"),
    include_screenshot: bool = Query(False, description="Includere screenshot del risultato per debug"),
    use_stealth: bool = Query(settings.BROWSER_STEALTH_MODE, description="Utilizzare tecniche stealth per evitare blocchi"),
    use_proxy: bool = Query(settings.USE_PROXIES, description="Utilizzare un proxy per la richiesta"),
    retry_count: int = Query(2, description="Numero di tentativi in caso di errore"),
    token: str = token_dependency
):
    """
    Versione POST dell'endpoint di ricerca su Google, con supporto alla paginazione.
    
    Args:
        query: La query di ricerca
        lang: Lingua dei risultati (es: it, en, fr)
        num_results: Numero di risultati da restituire per pagina (max 20)
        max_pages: Numero massimo di pagine da consultare (default 1, max 10)
        sleep_interval: Pausa in secondi tra le richieste
        include_screenshot: Includere screenshot del risultato per debug
        use_stealth: Utilizzare tecniche stealth per evitare blocchi
        use_proxy: Utilizzare un proxy per la richiesta
        
    Returns:
        dict: Risposta con i risultati della ricerca
    """
    logger.info(f"Avvio ricerca Google (POST): '{query}' in lingua {lang}")
    # Riutilizza la funzione di ricerca esistente
    return await google_search(
        query=query, 
        lang=lang, 
        num_results=num_results,
        max_pages=max_pages,
        sleep_interval=sleep_interval, 
        include_screenshot=include_screenshot,
        use_stealth=use_stealth,
        use_proxy=use_proxy,
        retry_count=retry_count,
        token=token
    )
