from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from api.utils.responses import success_response, error_response
from api.utils.auth import token_dependency
from api.utils.browser.page_loader import load_page
import logging

logger = logging.getLogger(__name__)

# Definizione dei modelli di dati
class BrowserRequest(BaseModel):
    url: HttpUrl
    wait_for_load: bool = True
    screenshot: bool = False
    wait_time: int = 0
    viewport: Optional[Dict[str, int]] = None
    user_agent: Optional[str] = None
    evaluate_js: Optional[str] = None
    extract_seo_tags: bool = True
    extract_structured_data: bool = True

# Creazione del router
router = APIRouter(prefix="/api/browser", tags=["Browser"])

@router.post("/load")
async def load_webpage(
    request: BrowserRequest,
    token: str = token_dependency
):
    """
    Carica una pagina web utilizzando un browser automatizzato e restituisce informazioni sulla pagina.
    
    Args:
        request: Parametri per il caricamento della pagina
        
    Returns:
        dict: Risposta contenente le informazioni sulla pagina
    """
    try:
        # Carica la pagina utilizzando un browser automatizzato
        result = await load_page(
            url=str(request.url),
            wait_for_load=request.wait_for_load,
            screenshot=request.screenshot,
            wait_time=request.wait_time,
            viewport=request.viewport,
            user_agent=request.user_agent,
            evaluate_js=request.evaluate_js,
            extract_seo_tags=request.extract_seo_tags,
            extract_structured_data=request.extract_structured_data
        )
        
        # Restituisci una risposta formattata con i risultati
        return success_response(
            data=result,
            message=f"Pagina caricata con successo: {request.url}"
        )
    except Exception as e:
        logger.error(f"Errore durante il caricamento della pagina: {str(e)}")
        return error_response(
            message=f"Impossibile caricare la pagina: {str(e)}",
            error_type="BrowserError",
            details={"url": str(request.url)}
        )

@router.get("/load")
async def load_webpage_get(
    url: str = Query(..., description="URL della pagina da caricare"),
    wait_for_load: bool = Query(True, description="Se attendere che la pagina sia completamente caricata"),
    screenshot: bool = Query(False, description="Se acquisire uno screenshot della pagina"),
    wait_time: int = Query(0, description="Tempo di attesa aggiuntivo in millisecondi dopo il caricamento"),
    extract_seo_tags: bool = Query(True, description="Se estrarre i meta tag SEO (Open Graph, Twitter, ecc.)"),
    extract_structured_data: bool = Query(True, description="Se estrarre i dati strutturati (JSON-LD, Microdata)"),
    token: str = token_dependency
):
    """
    Carica una pagina web utilizzando un browser automatizzato (metodo GET).
    
    Args:
        url: URL della pagina da caricare
        wait_for_load: Se attendere che la pagina sia completamente caricata
        screenshot: Se acquisire uno screenshot della pagina
        wait_time: Tempo di attesa aggiuntivo dopo il caricamento
        
    Returns:
        dict: Risposta contenente le informazioni sulla pagina
    """
    try:
        # Carica la pagina utilizzando un browser automatizzato
        result = await load_page(
            url=url,
            wait_for_load=wait_for_load,
            screenshot=screenshot,
            wait_time=wait_time,
            extract_seo_tags=extract_seo_tags,
            extract_structured_data=extract_structured_data
        )
        
        # Restituisci una risposta formattata con i risultati
        return success_response(
            data=result,
            message=f"Pagina caricata con successo: {url}"
        )
    except Exception as e:
        logger.error(f"Errore durante il caricamento della pagina: {str(e)}")
        return error_response(
            message=f"Impossibile caricare la pagina: {str(e)}",
            error_type="BrowserError",
            details={"url": url}
        )
