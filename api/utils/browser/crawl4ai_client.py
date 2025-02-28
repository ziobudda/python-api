"""
Modulo client per interagire con Crawl4AI
Fornisce funzionalità per l'automazione del browser e l'estrazione di contenuti web.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from config import settings

logger = logging.getLogger(__name__)

async def crawl_web_page(
    url: str,
    wait_for_load: bool = True,
    wait_time: int = 0,
    extract_links: bool = True,
    extract_media: bool = True,
    css_selector: Optional[str] = None,
    exclude_external_links: bool = True,
    exclude_social_media_links: bool = True,
    exclude_external_images: bool = True,
    exclude_domains: Optional[List[str]] = None,
    screenshot: bool = False,
    pdf: bool = False,
    content_filter: Optional[str] = None,
    bm25_query: Optional[str] = None,
    user_agent: Optional[str] = None,
    viewport: Optional[Dict[str, int]] = None,
    js_code: Optional[str] = None,
    process_iframes: bool = True,
    cache_mode: str = "BYPASS"
) -> Dict[str, Any]:
    """
    Esegue il crawling di una pagina web utilizzando Crawl4AI.
    
    Args:
        url: URL della pagina da crawlare
        wait_for_load: Se attendere che la pagina sia completamente caricata
        wait_time: Tempo di attesa aggiuntivo in millisecondi dopo il caricamento
        extract_links: Se estrarre i link dalla pagina
        extract_media: Se estrarre le immagini e altri media dalla pagina
        css_selector: Selettore CSS per limitare l'estrazione a specifici elementi
        exclude_external_links: Se escludere i link esterni
        exclude_social_media_links: Se escludere i link ai social media
        exclude_external_images: Se escludere le immagini esterne
        exclude_domains: Lista di domini da escludere
        screenshot: Se acquisire uno screenshot della pagina
        pdf: Se generare un PDF della pagina
        content_filter: Tipo di filtro contenuti ('pruning', 'bm25' o None)
        bm25_query: Query per il filtro BM25 (se content_filter='bm25')
        user_agent: User-Agent personalizzato
        viewport: Dimensioni del viewport personalizzate
        js_code: Codice JavaScript da eseguire dopo il caricamento
        process_iframes: Se processare gli iframe nella pagina
        cache_mode: Modalità cache ('ENABLED', 'BYPASS', 'DISABLED', etc.)
        
    Returns:
        Dict[str, Any]: Risultati del crawling
    """
    try:
        # Configurazione del browser
        # Fornisci un user-agent predefinito se non ne viene fornito uno
        default_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        
        browser_config = BrowserConfig(
            browser_type="chromium",
            headless=True,
            verbose=True,
            # Usa lo user_agent fornito o quello predefinito
            user_agent=user_agent if user_agent else default_user_agent,
            viewport_width=viewport["width"] if viewport and "width" in viewport else 1280,
            viewport_height=viewport["height"] if viewport and "height" in viewport else 720
        )
        
        # Preparazione del content filter se richiesto
        content_filter_obj = None
        markdown_generator = None
        
        if content_filter == "pruning":
            logger.info(f"Utilizzo filtro di pruning per la pagina {url}")
            content_filter_obj = PruningContentFilter(
                threshold=0.5,
                threshold_type="fixed",
                min_word_threshold=10
            )
            markdown_generator = DefaultMarkdownGenerator(
                content_filter=content_filter_obj,
                options={"ignore_links": False, "body_width": 80}
            )
        elif content_filter == "bm25" and bm25_query:
            logger.info(f"Utilizzo filtro BM25 con query '{bm25_query}' per la pagina {url}")
            content_filter_obj = BM25ContentFilter(
                user_query=bm25_query,
                bm25_threshold=1.2
            )
            markdown_generator = DefaultMarkdownGenerator(
                content_filter=content_filter_obj,
                options={"ignore_links": False, "body_width": 80}
            )
        
        # Configurazione del crawler
        # Verifica se CacheMode è un attributo di CrawlerRunConfig
        try:
            if hasattr(CrawlerRunConfig, "CacheMode"):
                cache_mode_value = getattr(CrawlerRunConfig.CacheMode, cache_mode, None)
            else:
                # Se CacheMode non esiste, utilizza il valore stringa direttamente
                cache_mode_value = cache_mode
                logger.warning(f"CrawlerRunConfig.CacheMode non trovato, utilizzo diretto della stringa '{cache_mode}'")
                
            run_config = CrawlerRunConfig(
                word_count_threshold=10,
                exclude_external_links=exclude_external_links,
                exclude_social_media_links=exclude_social_media_links,
                exclude_external_images=exclude_external_images,
                exclude_domains=exclude_domains or [],
                process_iframes=process_iframes,
                screenshot=screenshot,
                pdf=pdf,
                wait_for=css_selector if css_selector else None,
                js_code=js_code,
                markdown_generator=markdown_generator,
                cache_mode=cache_mode_value
            )
        except Exception as config_err:
            # Fallback senza specificare esplicitamente cache_mode
            logger.warning(f"Errore nella configurazione cache_mode: {str(config_err)}, tentativo senza cache_mode")
            run_config = CrawlerRunConfig(
                word_count_threshold=10,
                exclude_external_links=exclude_external_links,
                exclude_social_media_links=exclude_social_media_links,
                exclude_external_images=exclude_external_images,
                exclude_domains=exclude_domains or [],
                process_iframes=process_iframes,
                screenshot=screenshot,
                pdf=pdf,
                wait_for=css_selector if css_selector else None,
                js_code=js_code,
                markdown_generator=markdown_generator
            )
        
        if wait_time > 0:
            # Aggiunge un delay dopo il caricamento se necessario
            run_config.delay_before_return_html = wait_time / 1000  # Converti da ms a s
        
        # Inizializza il crawler ed esegui il crawling con timeout
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                # Applica un timeout in secondi (configurabile)
                timeout = settings.CRAWL4AI_TIMEOUT
                result = await asyncio.wait_for(
                    crawler.arun(url=url, config=run_config),
                    timeout=timeout
                )
        except asyncio.TimeoutError:
            logger.error(f"Timeout durante il crawling di {url} dopo {settings.CRAWL4AI_TIMEOUT} secondi")
            return {
                "success": False,
                "error_message": f"Timeout durante il crawling dopo {settings.CRAWL4AI_TIMEOUT} secondi",
                "status_code": None
            }
            
        if not result.success:
            logger.error(f"Errore durante il crawling di {url}: {result.error_message}")
            return {
                "success": False,
                "error_message": result.error_message,
                "status_code": result.status_code if hasattr(result, "status_code") else None
            }
        
        # Prepara i risultati
        response = {
            "success": True,
            "url": url,
            "final_url": result.url if hasattr(result, "url") else url,
            "status_code": result.status_code if hasattr(result, "status_code") else None,
            "title": get_page_title(result),
            "html_length": len(result.html) if hasattr(result, "html") and result.html else 0,
            "cleaned_html_length": len(result.cleaned_html) if hasattr(result, "cleaned_html") and result.cleaned_html else 0
        }
        
        # Aggiungi markdown se disponibile
        if hasattr(result, "markdown_v2") and result.markdown_v2:
            if hasattr(result.markdown_v2, "raw_markdown") and result.markdown_v2.raw_markdown:
                response["raw_markdown"] = result.markdown_v2.raw_markdown
            
            if hasattr(result.markdown_v2, "fit_markdown") and result.markdown_v2.fit_markdown:
                response["fit_markdown"] = result.markdown_v2.fit_markdown
        
        # Aggiungi links se richiesto
        if extract_links and hasattr(result, "links") and result.links:
            # Verifica e processa gli attributi di links in maniera sicura
            response["links"] = {
                "internal": extract_links_data(result.links.get("internal", [])),
                "external": extract_links_data(result.links.get("external", []))
            }
            response["internal_links_count"] = len(result.links.get("internal", []))
            response["external_links_count"] = len(result.links.get("external", []))
        
        # Aggiungi media se richiesto
        if extract_media and hasattr(result, "media") and result.media:
            response["media"] = {
                "images": extract_media_data(result.media.get("images", [])),
                "videos": len(result.media.get("videos", [])),
                "audios": len(result.media.get("audios", []))
            }
            response["images_count"] = len(result.media.get("images", []))
        
        # Aggiungi screenshot se richiesto
        if screenshot and hasattr(result, "screenshot") and result.screenshot:
            response["screenshot"] = result.screenshot
        
        # Aggiungi PDF se richiesto
        if pdf and hasattr(result, "pdf") and result.pdf:
            response["pdf_size"] = len(result.pdf)
                
        return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Eccezione durante il crawling di {url}: {str(e)}\n{error_details}")
        return {
            "success": False,
            "error_message": f"{str(e)}",
            "debug_details": error_details if settings.DEBUG else None
        }

def get_page_title(result) -> str:
    """Estrae il titolo della pagina dal risultato"""
    # Prova a trovare il titolo nei metadati, altrimenti cerca in altre proprietà
    if hasattr(result, "metadata") and result.metadata and isinstance(result.metadata, dict) and "title" in result.metadata:
        return result.metadata["title"]
    
    # Fallback: cerca di estrarre il titolo dall'HTML se disponibile
    if hasattr(result, "html") and result.html:
        html = result.html
        title_start = html.find("<title>")
        if title_start != -1:
            title_end = html.find("</title>", title_start)
            if title_end != -1:
                return html[title_start + 7:title_end].strip()
    
    return "Nessun titolo trovato"

def extract_links_data(links: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Estrae informazioni essenziali dai link"""
    if not links or not isinstance(links, list):
        return []
        
    extracted = []
    for link in links:
        if not isinstance(link, dict):
            continue
            
        link_data = {
            "href": link.get("href", ""),
            "text": link.get("text", "")
        }
        
        # Aggiungi attributi opzionali solo se presenti e non None
        if "title" in link and link["title"] is not None:
            link_data["title"] = str(link["title"])
            
        if "base_domain" in link and link["base_domain"] is not None:
            link_data["domain"] = str(link["base_domain"])
        
        extracted.append(link_data)
    
    return extracted

def extract_media_data(media_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Estrae informazioni essenziali dagli elementi multimediali"""
    if not media_items or not isinstance(media_items, list):
        return []
        
    extracted = []
    for item in media_items:
        if not isinstance(item, dict):
            continue
            
        # Assicurati che ci sia almeno un URL sorgente
        if "src" not in item or not item["src"]:
            continue
            
        media_data = {
            "src": str(item.get("src", ""))
        }
        
        # Aggiungi attributi aggiuntivi se disponibili
        for attr in ["alt", "title", "width", "height"]:
            if attr in item and item[attr] is not None:
                # Converti numeri in stringhe per width/height se necessario
                if attr in ["width", "height"] and isinstance(item[attr], (int, float)):
                    media_data[attr] = item[attr]  # Mantieni come numero
                else:
                    media_data[attr] = str(item[attr])
        
        # Aggiungi score se disponibile
        if "score" in item and item["score"] is not None:
            if isinstance(item["score"], (int, float)):
                media_data["score"] = item["score"]
        
        extracted.append(media_data)
    
    return extracted
