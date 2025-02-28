import asyncio
import base64
import random
from typing import Dict, List, Optional, Union
from playwright.async_api import async_playwright, Browser, Page, Playwright, BrowserContext, Route
import logging
from .proxy_manager import proxy_manager

logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Gestisce l'istanza del browser per l'automazione web.
    Implementa un pattern singleton per riutilizzare l'istanza del browser.
    """
    _instance = None
    _browser: Optional[Browser] = None
    _playwright: Optional[Playwright] = None
    
    @classmethod
    async def get_instance(cls) -> "BrowserManager":
        """
        Ottiene o crea un'istanza di BrowserManager.
        
        Returns:
            BrowserManager: Un'istanza del gestore del browser
        """
        if cls._instance is None:
            cls._instance = BrowserManager()
            await cls._instance._initialize()
        return cls._instance
    
    async def _initialize(self):
        """
        Inizializza Playwright e il browser.
        """
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ],
                firefox_user_prefs={
                    "dom.webdriver.enabled": False,
                    "useAutomationExtension": False,
                    "media.autoplay.default": 0,
                    "media.volume_scale": "0.0"
                },
                chromium_sandbox=False
            )
            logger.info("Browser inizializzato con successo")
        except Exception as e:
            logger.error(f"Errore durante l'inizializzazione del browser: {str(e)}")
            # Assicurati di chiudere le risorse in caso di errore
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            raise
    
    async def new_page(self) -> Page:
        """
        Crea una nuova pagina nel browser.
        
        Returns:
            Page: Una nuova istanza di pagina del browser
        """
        if not self._browser:
            await self._initialize()
        return await self._browser.new_page()
    
    async def new_stealth_context(
        self, 
        locale: str = "it-IT", 
        timezone: str = "Europe/Rome",
        use_proxy: bool = False
    ) -> BrowserContext:
        """
        Crea un nuovo contesto browser con impostazioni che aiutano a eludere il rilevamento.
        
        Args:
            locale: La localizzazione da usare
            timezone: Il fuso orario da impostare
            use_proxy: Se utilizzare un proxy dal pool
            
        Returns:
            BrowserContext: Un nuovo contesto browser stealth
        """
        if not self._browser:
            await self._initialize()
        
        # Lista di user agent comuni (aggiornati regolarmente)
        common_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]
        
        # Parametri di base
        context_params = {
            "viewport": {"width": random.choice([1366, 1920, 1440, 1536]), "height": random.choice([768, 1080, 900, 864])},
            "user_agent": random.choice(common_user_agents),
            "locale": locale,
            "timezone_id": timezone,
            "color_scheme": random.choice(["light", "dark", "no-preference"]),
            "device_scale_factor": random.choice([1, 2]) if random.random() > 0.7 else 1,
            "is_mobile": False,
            "has_touch": random.random() > 0.8,  # 20% di probabilità di avere un touchscreen
            "bypass_csp": True  # Utile per l'iniezione di script
        }
        
        # Aggiungi un proxy casuale se richiesto
        if use_proxy:
            proxy = proxy_manager.get_random_proxy()
            if proxy:
                context_params["proxy"] = proxy_manager.format_proxy_for_playwright(proxy)
        
        # Crea il contesto
        context = await self._browser.new_context(**context_params)
        
        # Aggiungi JavaScript per mascherare i segni dell'automazione
        await context.add_init_script("""
        () => {
            // Sovrascrivi le proprietà che potrebbero rivelare l'automazione
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'languages', { get: () => ['it-IT', 'it', 'en-US', 'en'] });
            
            // Fingerprint canvas diverso
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            CanvasRenderingContext2D.prototype.getImageData = function(x, y, width, height) {
                const imageData = originalGetImageData.call(this, x, y, width, height);
                const pixels = imageData.data;
                // Modifica leggermente i pixel per evitare fingerprinting
                for (let i = 0; i < pixels.length; i += 4) {
                    pixels[i] = pixels[i] + Math.floor(Math.random() * 3) - 1;  // R
                    pixels[i+1] = pixels[i+1] + Math.floor(Math.random() * 3) - 1;  // G
                    pixels[i+2] = pixels[i+2] + Math.floor(Math.random() * 3) - 1;  // B
                }
                return imageData;
            };
            
            // Modifica i permessi
            const originalPermissions = navigator.permissions;
            navigator.permissions.query = async (param) => {
                if (param.name === 'notifications' || param.name === 'clipboard-read' || param.name === 'clipboard-write') {
                    return { state: "prompt", onchange: null };
                }
                return originalPermissions.query(param);
            };
            
            // Nasconde Playwright/Headless
            window.chrome = { runtime: {} };
            window.navigator.chrome = { runtime: {} };
        }
        """)
        
        return context
    
    async def close(self):
        """
        Chiude il browser e le risorse associate.
        """
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        BrowserManager._instance = None
        logger.info("Browser chiuso con successo")

async def simulate_human_behavior(page: Page):
    """
    Simula il comportamento umano sulla pagina.
    
    Args:
        page: La pagina del browser
    """
    # Simula movimenti casuali del mouse
    for _ in range(random.randint(2, 5)):
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        await page.mouse.move(x, y, steps=random.randint(3, 10))
        await asyncio.sleep(random.uniform(0.1, 0.3))

async def random_scrolling(page: Page):
    """
    Simula lo scrolling casuale su una pagina.
    
    Args:
        page: La pagina del browser
    """
    # Simula scrolling casuale
    scrolls = random.randint(2, 5)
    for _ in range(scrolls):
        scroll_amount = random.randint(100, 800)
        await page.mouse.wheel(0, scroll_amount)
        await asyncio.sleep(random.uniform(0.3, 1.0))
    
    # A volte torna indietro
    if random.random() > 0.7:
        await page.mouse.wheel(0, -random.randint(100, 400))
        await asyncio.sleep(random.uniform(0.3, 0.7))

async def handle_route(route: Route):
    """
    Gestisce le richieste di rete con ritardi casuali per simulare comportamento umano.
    
    Args:
        route: L'oggetto route di Playwright
    """
    # Ignora o rallenta in base al tipo di risorsa
    resource_type = route.request.resource_type
    
    # Esegui le richieste essenziali senza ritardi
    if resource_type in ["document", "xhr", "fetch"]:
        await route.continue_()
    # Rallenta le risorse non critiche
    elif resource_type in ["image", "stylesheet", "media"]:
        await asyncio.sleep(random.uniform(0.05, 0.2))
        await route.continue_()
    # Blocca risorse inutili per velocizzare
    elif resource_type in ["font", "websocket", "other"]:
        if random.random() > 0.5:  # 50% di possibilità di caricare
            await route.continue_()
        else:
            await route.abort()
    else:
        await route.continue_()

async def load_page(
    url: str,
    wait_for_load: bool = True,
    screenshot: bool = False,
    wait_time: int = 0,
    viewport: Optional[Dict[str, int]] = None,
    user_agent: Optional[str] = None,
    evaluate_js: Optional[str] = None,
    use_stealth: bool = True,
    use_proxy: bool = False,
    extract_seo_tags: bool = True,
    extract_structured_data: bool = True
) -> Dict:
    """
    Carica una pagina web utilizzando un browser reale e restituisce informazioni sulla pagina.
    
    Args:
        url: URL della pagina da caricare
        wait_for_load: Se attendere che la pagina sia completamente caricata
        screenshot: Se acquisire uno screenshot della pagina
        wait_time: Tempo di attesa aggiuntivo in millisecondi dopo il caricamento
        viewport: Dimensioni personalizzate della finestra del browser
        user_agent: User-Agent personalizzato
        evaluate_js: Codice JavaScript da eseguire sulla pagina
        use_stealth: Se utilizzare tecniche stealth per evitare rilevamento bot
        use_proxy: Se utilizzare un proxy dal pool
        
    Returns:
        Dict: Informazioni sulla pagina caricata
    """
    page = None
    browser_context = None
    
    try:
        # Ottieni l'istanza del browser manager
        browser_manager = await BrowserManager.get_instance()
        
        if use_stealth:
            # Crea un contesto stealth
            browser_context = await browser_manager.new_stealth_context(use_proxy=use_proxy)
            page = await browser_context.new_page()
            
            # Aggiungi comportamento umano simulato
            await simulate_human_behavior(page)
        else:
            # Crea una pagina standard
            page = await browser_manager.new_page()
            
            # Configura la pagina base
            if viewport:
                await page.set_viewport_size(viewport)
            if user_agent:
                await page.set_extra_http_headers({"User-Agent": user_agent})
        
        # Aggiungi pause casuali tra le richieste di rete per sembrare più umano
        await page.route("**/*", lambda route: handle_route(route))
        
        # Carica la pagina
        logger.info(f"Caricamento pagina: {url}")
        response = await page.goto(url, wait_until="networkidle" if wait_for_load else "commit")
        
        # Attendi ulteriormente se richiesto
        if wait_time > 0:
            await asyncio.sleep(wait_time / 1000)
        
        # Simula scrolling casuale
        if use_stealth:
            await random_scrolling(page)
        
        # Ottieni i contenuti della pagina
        html = await page.content()
        title = await page.title()
        
        # Estrai separatamente head e body
        html_parts = await page.evaluate("""
        () => {
            return {
                head: document.head.outerHTML,
                body: document.body.outerHTML
            };
        }
        """)
        
        # Verifica se siamo stati bloccati
        if "detected unusual traffic" in html or "robot" in html.lower() or "captcha" in html.lower():
            logger.warning(f"Possibile blocco rilevato durante il caricamento di {url}")
        
        # Esegui JavaScript personalizzato se fornito
        js_result = None
        if evaluate_js:
            js_result = await page.evaluate(evaluate_js)
        
        # Acquisisce uno screenshot se richiesto
        screenshot_data = None
        if screenshot:
            screenshot_bytes = await page.screenshot(full_page=True)
            screenshot_data = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        # Raccogli i cookies
        cookies = await page.context.cookies()
        
        # Estrai i meta tag SEO e dati strutturati se richiesto
        seo_tags = {}
        structured_data = {}
        seo_analysis = {}
        if extract_seo_tags:
            # Estrai Open Graph tags
            og_tags = await page.evaluate("""
            () => {
                const ogTags = {};
                document.querySelectorAll('meta[property^="og:"]').forEach(tag => {
                    const property = tag.getAttribute('property');
                    const content = tag.getAttribute('content');
                    if (property && content) {
                        ogTags[property] = content;
                    }
                });
                return ogTags;
            }
            """)
            
            # Estrai Twitter Card tags
            twitter_tags = await page.evaluate("""
            () => {
                const twitterTags = {};
                document.querySelectorAll('meta[name^="twitter:"]').forEach(tag => {
                    const name = tag.getAttribute('name');
                    const content = tag.getAttribute('content');
                    if (name && content) {
                        twitterTags[name] = content;
                    }
                });
                return twitterTags;
            }
            """)
            
            # Estrai altri meta tag importanti
            other_meta_tags = await page.evaluate("""
            () => {
                const metaTags = {};
                const importantTags = ['description', 'keywords', 'author', 'robots', 'viewport', 'canonical'];
                
                // Meta tags con attributo name
                document.querySelectorAll('meta[name]').forEach(tag => {
                    const name = tag.getAttribute('name');
                    const content = tag.getAttribute('content');
                    if (importantTags.includes(name) && content) {
                        metaTags[name] = content;
                    }
                });
                
                // Link canonical
                const canonical = document.querySelector('link[rel="canonical"]');
                if (canonical) {
                    metaTags['canonical'] = canonical.getAttribute('href');
                }
                
                return metaTags;
            }
            """)
            
            # Estrai elementi principali per analisi SEO
            seo_analysis = await page.evaluate("""
            () => {
                const analysis = {
                    images: [],
                    headings: {
                        h1: [],
                        h2: [],
                        h3: [],
                        h4: [],
                        h5: [],
                        h6: []
                    },
                    links: {
                        internal: [],
                        external: [],
                        total: 0
                    },
                    text_statistics: {
                        word_count: 0,
                        paragraph_count: 0
                    },
                    keywords: {}
                };
                
                // Analisi immagini
                document.querySelectorAll('img').forEach(img => {
                    const imgData = {
                        src: img.getAttribute('src'),
                        alt: img.getAttribute('alt') || '',
                        width: img.getAttribute('width') || img.clientWidth,
                        height: img.getAttribute('height') || img.clientHeight,
                        has_alt: img.hasAttribute('alt') && img.getAttribute('alt').trim() !== ''
                    };
                    analysis.images.push(imgData);
                });
                
                // Analisi headings
                for (let i = 1; i <= 6; i++) {
                    document.querySelectorAll(`h${i}`).forEach(heading => {
                        analysis.headings[`h${i}`].push(heading.textContent.trim());
                    });
                }
                
                // Analisi link
                const currentHost = window.location.hostname;
                document.querySelectorAll('a[href]').forEach(link => {
                    const href = link.getAttribute('href');
                    try {
                        const url = new URL(href, window.location.origin);
                        const isExternal = url.hostname !== currentHost && url.hostname !== '';
                        const linkData = {
                            url: url.href,
                            text: link.textContent.trim(),
                            nofollow: link.getAttribute('rel')?.includes('nofollow') || false,
                            isExternal: isExternal
                        };
                        
                        if (isExternal) {
                            analysis.links.external.push(linkData);
                        } else if (url.hostname === currentHost || url.hostname === '') {
                            analysis.links.internal.push(linkData);
                        }
                    } catch (e) {
                        // Ignora URL non validi
                    }
                });
                analysis.links.total = analysis.links.internal.length + analysis.links.external.length;
                
                // Analisi testo
                const bodyText = document.body.innerText;
                const words = bodyText.split(/\s+/).filter(word => word.length > 0);
                analysis.text_statistics.word_count = words.length;
                analysis.text_statistics.paragraph_count = document.querySelectorAll('p').length;
                
                // Analisi semplice delle parole chiave (conta frequenza parole, escludi stop words)
                const stopWords = ['il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una', 'e', 'ed', 'o', 'per', 'con', 'su', 'in', 'da', 'di', 'a', 'al', 'alla', 'allo', 'ai', 'agli', 'alle', 'del', 'dello', 'della', 'dei', 'degli', 'delle', 'che', 'chi', 'cui', 'non', 'come', 'dove', 'quando', 'perché', 'quindi', 'questo', 'questa', 'questi', 'queste', 'quello', 'quella', 'quelli', 'quelle', 'è', 'se', 'più', 'quale', 'quanto', 'quanta', 'quanti', 'quante', 'così', 'ecco', 'allora', 'the', 'and', 'of', 'to', 'in', 'is', 'for', 'by', 'with', 'that', 'this', 'on', 'from', 'at', 'it', 'as', 'an', 'are', 'or', 'not', 'be'];
                
                const wordFrequency = {};
                words.forEach(word => {
                    word = word.toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, '');
                    if (word.length > 3 && !stopWords.includes(word)) {
                        if (wordFrequency[word]) {
                            wordFrequency[word]++;
                        } else {
                            wordFrequency[word] = 1;
                        }
                    }
                });
                
                // Ordina per frequenza e prendi i primi 20
                const sortedWords = Object.entries(wordFrequency)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 20);
                    
                analysis.keywords = Object.fromEntries(sortedWords);
                
                return analysis;
            }
            """)
            
            # Raccogli tutti i tag SEO
            seo_tags = {
                "og_tags": og_tags,
                "twitter_tags": twitter_tags,
                "meta_tags": other_meta_tags,
                "analysis": seo_analysis
            }
            
        # Estrai dati strutturati (JSON-LD, Microdata, RDFa)
        if extract_structured_data:
            # Estrai JSON-LD
            json_ld = await page.evaluate("""
            () => {
                const jsonLdScripts = [];
                document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
                    try {
                        const content = JSON.parse(script.textContent);
                        jsonLdScripts.push(content);
                    } catch (e) {
                        // Ignora JSON non valido
                    }
                });
                return jsonLdScripts;
            }
            """)
            
            # Estrai Microdata (semplificato)
            microdata = await page.evaluate("""
            () => {
                const microdataElements = [];
                document.querySelectorAll('[itemscope]').forEach(element => {
                    const item = {
                        type: element.getAttribute('itemtype') || null,
                        id: element.getAttribute('itemid') || null,
                        properties: {}
                    };
                    
                    element.querySelectorAll('[itemprop]').forEach(prop => {
                        const name = prop.getAttribute('itemprop');
                        let value;
                        
                        if (prop.tagName === 'META') {
                            value = prop.getAttribute('content');
                        } else if (prop.tagName === 'IMG') {
                            value = prop.getAttribute('src');
                        } else if (prop.tagName === 'A') {
                            value = prop.getAttribute('href');
                        } else if (prop.tagName === 'TIME') {
                            value = prop.getAttribute('datetime') || prop.textContent;
                        } else {
                            value = prop.textContent;
                        }
                        
                        item.properties[name] = value;
                    });
                    
                    microdataElements.push(item);
                });
                return microdataElements;
            }
            """)
            
            # Raccogli tutti i dati strutturati
            structured_data = {
                "json_ld": json_ld,
                "microdata": microdata
            }
            
        # Crea la risposta
        result = {
            "url": url,
            "final_url": page.url,  # URL finale dopo eventuali reindirizzamenti
            "status": response.status if response else None,
            "title": title,
            "html": {
                "full": html,
                "head": html_parts["head"],
                "body": html_parts["body"]
            },
            "cookies": cookies,
            "headers": dict(response.headers) if response else {},
            "seo_tags": seo_tags,
            "structured_data": structured_data
        }
        
        if js_result:
            result["js_result"] = js_result
            
        if screenshot_data:
            result["screenshot"] = screenshot_data
        
        # Chiudi la pagina e il contesto
        if browser_context:
            await browser_context.close()
        else:
            await page.close()
        
        return result
    except Exception as e:
        logger.error(f"Errore durante il caricamento della pagina {url}: {str(e)}")
        # Assicurati di gestire le risorse in caso di errore
        try:
            if browser_context:
                await browser_context.close()
            elif page:
                await page.close()
        except:
            pass
        
        # Rilancia l'eccezione per gestirla a livello superiore
        raise
