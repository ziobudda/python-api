import logging
import asyncio
import base64
import random
from typing import List, Dict, Any, Optional
from .page_loader import BrowserManager

logger = logging.getLogger(__name__)

async def search_google(
    query: str, 
    lang: str = "it", 
    num_results: int = 5,
    sleep_interval: float = 2.0,
    retry_count: int = 2,
    max_pages: int = 1  # Nuovo parametro per il numero massimo di pagine da consultare
) -> Dict[str, Any]:
    """
    Esegue una ricerca su Google e restituisce i risultati, supportando la paginazione.
    
    Args:
        query: La query di ricerca
        lang: Lingua dei risultati (es: it, en, fr)
        num_results: Numero di risultati da restituire per pagina (max 20)
        sleep_interval: Pausa in secondi tra le richieste per evitare blocchi
        retry_count: Numero di tentativi in caso di errore
        max_pages: Numero massimo di pagine da consultare (default 1)
        
    Returns:
        Dict: Informazioni sui risultati della ricerca
    """
    last_error = None
    
    for attempt in range(retry_count + 1):
        page = None
        browser_context = None
        all_results = []  # Lista per accumulare i risultati di tutte le pagine
        
        try:
            # Log tentativo corrente se c'è stato un retry
            if attempt > 0:
                logger.info(f"Tentativo {attempt}/{retry_count} per la ricerca '{query}'")
            
            # Limita il numero di risultati per pagina a 20 per evitare problemi di performance
            results_per_page = min(num_results, 20)
            
            # Ottieni l'istanza del browser manager
            browser_manager = await BrowserManager.get_instance()
            
            # Parametri per l'URL della ricerca
            country_code = lang.split('-')[0] if '-' in lang else lang
            
            # Crea una nuova pagina con un contesto più simile a un browser reale ma ottimizzato per le prestazioni
            browser_context = await browser_manager._browser.new_context(
                viewport={"width": 1366, "height": 768},  # Dimensioni più piccole per velocizzare il rendering
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                locale=lang,
                timezone_id="Europe/Rome",
                color_scheme="light",  # Light è più comune
                device_scale_factor=1.0,
                is_mobile=False,
                has_touch=False,
                reduced_motion="reduce",  # Riduce le animazioni
                accept_downloads=False  # Non abbiamo bisogno di scaricare nulla
            )
            
            # Imposta cookie per apparire come un utente che ha già visitato Google
            await browser_context.add_cookies([
                {
                    "name": "CONSENT", 
                    "value": f"YES+cb.{int(asyncio.get_event_loop().time() - 100000)}", 
                    "domain": ".google.com", 
                    "path": "/"
                },
                {
                    "name": "NID", 
                    "value": "511=abcdefghijklmnopqrstuvwxyz", 
                    "domain": ".google.com", 
                    "path": "/"
                }
            ])
            
            page = await browser_context.new_page()
            
            # Blocca le risorse non necessarie per velocizzare
            await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,otf}", 
                            lambda route: route.abort())
            
            # Variabili per tenere traccia della paginazione
            current_page = 0
            stats_text = ""
            screenshot_base64 = None
            
            # Loop di paginazione
            while current_page < max_pages:
                # Calcola l'offset di paginazione (10 risultati per pagina su Google)
                start_index = current_page * 10
                
                # Costruisci l'URL per la pagina corrente dei risultati
                google_url = f"https://www.google.com/search?q={query}&hl={lang}&pws=0&gl={country_code}"
                
                # Aggiungi parametro start per la paginazione (eccetto per la prima pagina)
                if start_index > 0:
                    google_url += f"&start={start_index}"
                
                logger.info(f"Avvio ricerca Google pagina {current_page + 1} di {max_pages}: {google_url}")
                
                # Usiamo domcontentloaded invece di networkidle per velocizzare
                await page.goto(google_url, wait_until="domcontentloaded", timeout=30000)
                
                # Attesa minima per caricamento
                await asyncio.sleep(sleep_interval / 2)  # Riduciamo l'attesa
                
                # Ottieni il contenuto HTML della pagina
                html_content = await page.content()
                logger.debug(f"Lunghezza HTML ottenuto (pagina {current_page + 1}): {len(html_content)} caratteri")
                
                # Verifica se siamo stati bloccati
                if "detected unusual traffic" in html_content or "violazione dei Termini di servizio" in html_content or "solving the above CAPTCHA" in html_content:
                    logger.error("Rilevato blocco di Google - risposta anti-scraping ricevuta")
                    screenshot = await page.screenshot(full_page=True)
                    return {
                        "query": query,
                        "results": all_results,  # Restituisci i risultati accumulati finora
                        "stats": "ERRORE: Google ha bloccato la richiesta",
                        "screenshot": base64.b64encode(screenshot).decode('utf-8'),
                        "html": html_content[:1000],  # prime 1000 caratteri per debug
                        "pages_fetched": current_page
                    }
                
                # Aggiorniamo i selettori per adattarli alla struttura attuale di Google
                # Prova con diversi selettori per i risultati di ricerca
                selectors = [
                    "div.g", 
                    "div.MjjYud",
                    "div[data-snf='x']", 
                    "div.v7W49e",
                    "div.Gx5Zad",
                    "div[data-sotr='r']",
                    "div.tF2Cxc",
                    "div.yuRUbf",
                    "div[jscontroller]"
                ]
                
                results = []
                search_results = []
                
                # Prova ogni selettore finché non troviamo risultati
                for selector in selectors:
                    search_results = await page.query_selector_all(selector)
                    logger.info(f"Selettore '{selector}' ha trovato {len(search_results)} risultati nella pagina {current_page + 1}")
                    
                    if len(search_results) > 0:
                        break
                
                # Se ancora non abbiamo risultati, proviamo un approccio più generico
                if len(search_results) == 0:
                    logger.warning(f"Nessun risultato trovato con i selettori standard nella pagina {current_page + 1}, utilizzo approccio generico")
                    
                    # Ottieni tutti i link dalla pagina
                    all_links = await page.query_selector_all("a[href^='http']")
                    
                    # Filtra i link che sembrano essere risultati di ricerca
                    for link in all_links:
                        href = await link.get_attribute("href")
                        
                        # Ignora link Google e link non pertinenti
                        if (href and 
                            "google.com" not in href and 
                            not href.startswith("https://accounts.") and
                            not href.startswith("https://support.") and
                            not href.startswith("https://maps.")):
                            
                            # Trova il testo più vicino che potrebbe essere un titolo
                            heading = await link.query_selector("h3") or link
                            title_text = await heading.inner_text() if heading else "No title"
                            
                            # Trova la descrizione (testo vicino al link)
                            description = ""
                            try:
                                # Tenta di ottenere il testo circostante
                                parent = await link.evaluate("el => el.closest('div') || el.parentElement")
                                if parent:
                                    parent_text = await page.evaluate("el => el.textContent", parent)
                                    description = parent_text.replace(title_text, "").strip()
                            except Exception as e:
                                logger.warning(f"Errore nell'estrazione della descrizione: {e}")
                            
                            # Aggiunge il risultato se ha un titolo non vuoto
                            if title_text and title_text.strip():
                                result_item = {
                                    "title": title_text.strip(),
                                    "url": href,
                                    "description": description,
                                    "page": current_page + 1
                                }
                                
                                # Evita duplicati controllando gli URL già presenti
                                if not any(r["url"] == href for r in all_results):
                                    results.append(result_item)
                                
                                # Limita il numero di risultati per pagina
                                if len(results) >= results_per_page:
                                    break
                else:
                    # Elabora i risultati utilizzando il selettore che ha funzionato
                    for i, result in enumerate(search_results):
                        if i >= results_per_page:
                            break
                            
                        # Proviamo diversi selettori per i componenti di risultato
                        title_selectors = ["h3", "a h3", "div h3", "h3.LC20lb"]
                        link_selectors = ["a[href]", "a[ping]", "h3 a", "div > a", "a.cz88Hc"]
                        desc_selectors = ["div.VwiC3b", "div[data-sncf='1']", "div[role='link'] div", "div.yi8zzc"]
                        
                        # Cerca titolo
                        title_element = None
                        for sel in title_selectors:
                            title_element = await result.query_selector(sel)
                            if title_element:
                                break
                        
                        # Cerca link
                        link_element = None
                        for sel in link_selectors:
                            link_element = await result.query_selector(sel)
                            if link_element:
                                break
                        
                        # Cerca descrizione
                        desc_element = None
                        for sel in desc_selectors:
                            desc_element = await result.query_selector(sel)
                            if desc_element:
                                break
                        
                        # Estrai i dati
                        title = "Titolo non disponibile"
                        if title_element:
                            try:
                                title = await title_element.inner_text()
                            except Exception as e:
                                logger.warning(f"Errore nell'estrazione del titolo: {e}")
                        
                        url = None
                        if link_element:
                            try:
                                url = await link_element.get_attribute("href")
                            except Exception as e:
                                logger.warning(f"Errore nell'estrazione dell'URL: {e}")
                        
                        description = ""
                        if desc_element:
                            try:
                                description = await desc_element.inner_text()
                            except Exception as e:
                                logger.warning(f"Errore nell'estrazione della descrizione: {e}")
                        
                        # Aggiungi informazioni sulla pagina di provenienza
                        result_item = {
                            "title": title,
                            "url": url,
                            "description": description,
                            "page": current_page + 1
                        }
                        
                        # Evita duplicati controllando gli URL già presenti
                        if url and not any(r.get("url") == url for r in all_results):
                            results.append(result_item)
                
                # Logga il numero di risultati trovati
                logger.info(f"Trovati {len(results)} risultati nella pagina {current_page + 1} per la query '{query}'")
                
                # Aggiungi i risultati di questa pagina all'elenco completo
                all_results.extend(results)
                
                # Se è la prima pagina, cattura le statistiche e uno screenshot
                if current_page == 0:
                    # Cattura informazioni sul tempo di ricerca e numero totale di risultati stimati
                    stats_selectors = ["div#result-stats", "div[aria-level='3']", "#result-stats"]
                    
                    for selector in stats_selectors:
                        stats_element = await page.query_selector(selector)
                        if stats_element:
                            try:
                                stats_text = await stats_element.inner_text()
                                if stats_text:
                                    break
                            except:
                                pass
                    
                    # Prendi uno screenshot della prima pagina per debugging
                    try:
                        screenshot = await page.screenshot(full_page=False)
                        screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
                    except Exception as ss_err:
                        logger.error(f"Errore durante la cattura dello screenshot: {ss_err}")
                
                # Verifica se esistono più pagine
                # Cerca il pulsante "Avanti" o i link di paginazione
                has_next_page = False
                next_page_selectors = [
                    "a#pnnext", 
                    "a[aria-label='Pagina successiva']",
                    "a[aria-label='Page suivante']",
                    "a[aria-label='Next page']",
                    "a[aria-label='Next']",
                    "a.nBDE1b.G5eFlf"
                ]
                
                for selector in next_page_selectors:
                    next_button = await page.query_selector(selector)
                    if next_button:
                        has_next_page = True
                        break
                
                # Se non ci sono più pagine o abbiamo raggiunto il numero massimo di risultati, esci dal ciclo
                if not has_next_page or len(all_results) >= num_results * max_pages:
                    logger.info(f"Nessuna pagina successiva trovata o numero massimo di risultati raggiunto dopo la pagina {current_page + 1}")
                    break
                
                # Aspetta tra le pagine per evitare di essere identificati come bot
                await asyncio.sleep(sleep_interval)
                
                # Passa alla pagina successiva
                current_page += 1
            
            # Chiudi il contesto del browser e la pagina
            await browser_context.close()
            
            # Restituisci i risultati
            return {
                "query": query,
                "results": all_results,
                "stats": stats_text,
                "screenshot": screenshot_base64,
                "html_snippet": html_content[:500] if len(all_results) == 0 else None,  # Solo per debug se non ci sono risultati
                "pages_fetched": current_page + 1
            }
        
        except Exception as e:
            last_error = e
            # Chiudi la pagina e il contesto in caso di errore
            if browser_context:
                try:
                    await browser_context.close()
                except Exception as close_error:
                    logger.warning(f"Errore durante la chiusura del contesto: {close_error}")
            
            # Gestisci eventuali errori
            logger.warning(f"Errore durante il tentativo {attempt + 1} della ricerca: {e}")
            
            # Se è l'ultimo tentativo, rilancia l'eccezione
            if attempt == retry_count:
                logger.error(f"Tutti i tentativi falliti per la ricerca '{query}': {str(last_error)}")
                raise last_error
            
            # Attendi prima del prossimo tentativo
            retry_delay = sleep_interval * (attempt + 1)  # Aumento progressivo del tempo di attesa
            logger.info(f"Attesa di {retry_delay} secondi prima del prossimo tentativo...")
            await asyncio.sleep(retry_delay)
    
    # Non dovremmo mai arrivare qui, ma nel caso restituiamo un errore
    raise Exception(f"Ricerca fallita dopo {retry_count} tentativi: {str(last_error) if last_error else 'Errore sconosciuto'}")
