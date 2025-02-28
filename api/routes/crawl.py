"""
Endpoints per l'interazione con Crawl4AI
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl
from api.utils.responses import success_response, error_response
from api.utils.auth import token_dependency
from api.utils.browser.crawl4ai_client import crawl_web_page
import logging

logger = logging.getLogger(__name__)

# Definizione dei modelli di dati
class CrawlRequest(BaseModel):
    url: HttpUrl
    wait_for_load: bool = True
    wait_time: int = 0
    extract_links: bool = True
    extract_media: bool = True
    css_selector: Optional[str] = None
    exclude_external_links: bool = True
    exclude_social_media_links: bool = True
    exclude_external_images: bool = True
    exclude_domains: Optional[List[str]] = None
    screenshot: bool = False
    pdf: bool = False
    content_filter: Optional[str] = None
    bm25_query: Optional[str] = None
    user_agent: Optional[str] = None
    viewport: Optional[Dict[str, int]] = None
    js_code: Optional[str] = None
    process_iframes: bool = True
    cache_mode: str = "BYPASS"

# Creazione del router
router = APIRouter(prefix="/api/crawl", tags=["Crawl"])

@router.post("/page")
async def crawl_page(
    request: CrawlRequest,
    token: str = token_dependency
):
    """
    Esegue il crawling di una pagina web utilizzando Crawl4AI.
    
    Args:
        request: Parametri per il crawling della pagina
        
    Returns:
        dict: Risposta contenente i risultati del crawling
    """
    try:
        # Verifica che il content_filter sia valido se fornito
        if request.content_filter and request.content_filter not in ["pruning", "bm25", None]:
            return error_response(
                message="Il filtro contenuti deve essere 'pruning', 'bm25' o null",
                error_type="ValidationError",
                details={"content_filter": request.content_filter}
            )
        
        # Verifica che bm25_query sia fornito se content_filter è 'bm25'
        if request.content_filter == "bm25" and not request.bm25_query:
            return error_response(
                message="La query BM25 è richiesta quando si utilizza il filtro 'bm25'",
                error_type="ValidationError",
                details={"content_filter": "bm25", "bm25_query": None}
            )
            
        # Esegui il crawling utilizzando Crawl4AI
        result = await crawl_web_page(
            url=str(request.url),
            wait_for_load=request.wait_for_load,
            wait_time=request.wait_time,
            extract_links=request.extract_links,
            extract_media=request.extract_media,
            css_selector=request.css_selector,
            exclude_external_links=request.exclude_external_links,
            exclude_social_media_links=request.exclude_social_media_links,
            exclude_external_images=request.exclude_external_images,
            exclude_domains=request.exclude_domains,
            screenshot=request.screenshot,
            pdf=request.pdf,
            content_filter=request.content_filter,
            bm25_query=request.bm25_query,
            user_agent=request.user_agent,
            viewport=request.viewport,
            js_code=request.js_code,
            process_iframes=request.process_iframes,
            cache_mode=request.cache_mode
        )
        
        # Verifica se il crawling ha avuto successo
        if not result.get("success", False):
            error_msg = result.get('error_message', 'Errore sconosciuto')
            logger.error(f"Crawling fallito per {request.url}: {error_msg}")
            
            # Prepara i dettagli dell'errore
            error_details = {
                "url": str(request.url), 
                "status_code": result.get("status_code")
            }
            
            # Aggiungi debug_details se presente e in modalità debug
            if "debug_details" in result and result["debug_details"]:
                error_details["debug_details"] = result["debug_details"]
                
            return error_response(
                message=f"Impossibile completare il crawling: {error_msg}",
                error_type="CrawlError",
                details=error_details
            )
        
        # Log di successo
        logger.info(f"Crawling completato con successo per {request.url} - HTML length: {result.get('html_length', 0)}, links: {result.get('internal_links_count', 0) + result.get('external_links_count', 0)}")
        
        # Restituisci una risposta formattata con i risultati
        return success_response(
            data=result,
            message=f"Crawling completato con successo: {request.url}"
        )
    except Exception as e:
        logger.error(f"Errore durante il crawling della pagina: {str(e)}")
        return error_response(
            message=f"Impossibile eseguire il crawling della pagina: {str(e)}",
            error_type="CrawlError",
            details={"url": str(request.url)}
        )

@router.get("/page")
async def crawl_page_get(
    url: str = Query(..., description="URL della pagina da crawlare"),
    wait_for_load: bool = Query(True, description="Attendere che la pagina sia completamente caricata"),
    extract_links: bool = Query(True, description="Estrarre i link dalla pagina"),
    extract_media: bool = Query(True, description="Estrarre immagini e media dalla pagina"),
    css_selector: Optional[str] = Query(None, description="Selettore CSS per limitare l'estrazione a specifici elementi"),
    screenshot: bool = Query(False, description="Acquisire uno screenshot della pagina"),
    content_filter: Optional[str] = Query(None, description="Filtro contenuti (pruning, bm25 o null)"),
    bm25_query: Optional[str] = Query(None, description="Query per il filtro BM25 (richiesto se content_filter=bm25)"),
    token: str = token_dependency
):
    """
    Esegue il crawling di una pagina web utilizzando Crawl4AI (metodo GET).
    
    Args:
        url: URL della pagina da crawlare
        wait_for_load: Se attendere che la pagina sia completamente caricata
        extract_links: Se estrarre i link dalla pagina
        extract_media: Se estrarre immagini e media dalla pagina
        css_selector: Selettore CSS per limitare l'estrazione
        screenshot: Se acquisire uno screenshot della pagina
        content_filter: Filtro contenuti da applicare
        bm25_query: Query per il filtro BM25
        
    Returns:
        dict: Risposta contenente i risultati del crawling
    """
    try:
        # Verifica che il content_filter sia valido se fornito
        if content_filter and content_filter not in ["pruning", "bm25", None]:
            return error_response(
                message="Il filtro contenuti deve essere 'pruning', 'bm25' o null",
                error_type="ValidationError",
                details={"content_filter": content_filter}
            )
        
        # Verifica che bm25_query sia fornito se content_filter è 'bm25'
        if content_filter == "bm25" and not bm25_query:
            return error_response(
                message="La query BM25 è richiesta quando si utilizza il filtro 'bm25'",
                error_type="ValidationError",
                details={"content_filter": "bm25", "bm25_query": None}
            )
        
        # Esegui il crawling utilizzando Crawl4AI
        result = await crawl_web_page(
            url=url,
            wait_for_load=wait_for_load,
            extract_links=extract_links,
            extract_media=extract_media,
            css_selector=css_selector,
            screenshot=screenshot,
            content_filter=content_filter,
            bm25_query=bm25_query
        )
        
        # Verifica se il crawling ha avuto successo
        if not result.get("success", False):
            error_msg = result.get('error_message', 'Errore sconosciuto')
            logger.error(f"Crawling fallito per {url}: {error_msg}")
            
            # Prepara i dettagli dell'errore
            error_details = {
                "url": url, 
                "status_code": result.get("status_code")
            }
            
            # Aggiungi debug_details se presente e in modalità debug
            if "debug_details" in result and result["debug_details"]:
                error_details["debug_details"] = result["debug_details"]
                
            return error_response(
                message=f"Impossibile completare il crawling: {error_msg}",
                error_type="CrawlError",
                details=error_details
            )
        
        # Log di successo
        logger.info(f"Crawling completato con successo per {url} - HTML length: {result.get('html_length', 0)}, links: {result.get('internal_links_count', 0) + result.get('external_links_count', 0)}")
        
        # Restituisci una risposta formattata con i risultati
        return success_response(
            data=result,
            message=f"Crawling completato con successo: {url}"
        )
    except Exception as e:
        logger.error(f"Errore durante il crawling della pagina: {str(e)}")
        return error_response(
            message=f"Impossibile eseguire il crawling della pagina: {str(e)}",
            error_type="CrawlError",
            details={"url": url}
        )
