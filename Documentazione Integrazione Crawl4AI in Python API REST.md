# Documentazione Integrazione Crawl4AI in Python API REST

## Panoramica

Questa integrazione estende il sistema Python API REST con la capacità di eseguire il crawling di pagine web utilizzando la libreria Crawl4AI. Questo permette di estrarre contenuti strutturati e non strutturati da pagine web, con diverse opzioni di filtraggio e processamento del contenuto.

## Funzionalità Principali

- Crawling di pagine web con supporto JavaScript
- Estrazione di link interni ed esterni
- Estrazione di immagini e altri media
- Generazione di markdown dai contenuti HTML
- Supporto per filtri di contenuto tramite:
  - **Pruning**: Elimina contenuti irrilevanti in base a densità di testo e importanza
  - **BM25**: Filtra contenuti in base a rilevanza per una query specifica
- Cattura di screenshot e generazione PDF
- Supporto per selettori CSS per targetizzare specifiche sezioni
- Supporto per esecuzione di JavaScript personalizzato

## Endpoint API

### `POST /api/crawl/page`

Esegue il crawling di una pagina web con opzioni complete.

**Parametri**:

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| url | string | (richiesto) | URL della pagina da crawlare |
| wait_for_load | boolean | true | Attendere che la pagina sia completamente caricata |
| wait_time | integer | 0 | Tempo di attesa aggiuntivo in millisecondi |
| extract_links | boolean | true | Estrarre i link dalla pagina |
| extract_media | boolean | true | Estrarre immagini e media dalla pagina |
| css_selector | string | null | Selettore CSS per limitare l'estrazione |
| exclude_external_links | boolean | true | Escludere i link esterni |
| exclude_social_media_links | boolean | true | Escludere i link ai social media |
| exclude_external_images | boolean | true | Escludere le immagini esterne |
| exclude_domains | array | [] | Lista di domini da escludere |
| screenshot | boolean | false | Acquisire uno screenshot della pagina |
| pdf | boolean | false | Generare un PDF della pagina |
| content_filter | string | null | Filtro contenuti ('pruning', 'bm25' o null) |
| bm25_query | string | null | Query per il filtro BM25 |
| user_agent | string | null | User-Agent personalizzato |
| viewport | object | null | Dimensioni del viewport personalizzate |
| js_code | string | null | Codice JavaScript da eseguire |
| process_iframes | boolean | true | Processare gli iframe nella pagina |
| cache_mode | string | "BYPASS" | Modalità cache ('ENABLED', 'BYPASS', 'DISABLED') |

**Esempio di richiesta**:

```json
{
  "url": "https://www.example.com",
  "wait_for_load": true,
  "extract_links": true,
  "content_filter": "pruning",
  "screenshot": true,
  "viewport": {"width": 1280, "height": 800}
}
```

**Risposta di successo**:

```json
{
  "success": true,
  "data": {
    "success": true,
    "url": "https://www.example.com",
    "final_url": "https://www.example.com/",
    "status_code": 200,
    "title": "Example Domain",
    "html_length": 5342,
    "cleaned_html_length": 4217,
    "raw_markdown": "# Example Domain\n\nThis domain is established to be used for illustrative examples in documents.",
    "links": {
      "internal": [
        {
          "href": "/about",
          "text": "About Us"
        }
      ],
      "external": [
        {
          "href": "https://www.iana.org/domains/example",
          "text": "More information"
        }
      ]
    },
    "internal_links_count": 1,
    "external_links_count": 1,
    "media": {
      "images": [
        {
          "src": "https://www.example.com/logo.png",
          "alt": "Example Logo",
          "width": 200,
          "height": 50
        }
      ],
      "videos": 0,
      "audios": 0
    },
    "images_count": 1,
    "screenshot": "base64_encoded_image_data..."
  },
  "message": "Crawling completato con successo: https://www.example.com"
}
```

**Risposta di errore**:

```json
{
  "success": false,
  "error": {
    "message": "Impossibile completare il crawling: Timeout durante il caricamento della pagina",
    "type": "CrawlError",
    "details": {
      "url": "https://www.example.com",
      "status_code": 0
    }
  }
}
```

### `GET /api/crawl/page`

Versione semplificata del crawling con parametri passati come query string.

**Parametri**:

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| url | string | (richiesto) | URL della pagina da crawlare |
| wait_for_load | boolean | true | Attendere che la pagina sia completamente caricata |
| extract_links | boolean | true | Estrarre i link dalla pagina |
| extract_media | boolean | true | Estrarre immagini e media dalla pagina |
| css_selector | string | null | Selettore CSS per limitare l'estrazione |
| screenshot | boolean | false | Acquisire uno screenshot della pagina |
| content_filter | string | null | Filtro contenuti ('pruning', 'bm25' o null) |
| bm25_query | string | null | Query per il filtro BM25 |

**Esempio di richiesta**:

```
GET /api/crawl/page?url=https://www.example.com&content_filter=pruning&screenshot=true
```

## Implementazione Tecnica

### Componenti Principali

1. **Crawl4AI Client** (`api/utils/browser/crawl4ai_client.py`):
   - Implementa l'interfaccia con la libreria Crawl4AI
   - Gestisce la configurazione del browser e del crawler
   - Processa e formatta i risultati del crawling

2. **Router di Crawling** (`api/routes/crawl.py`):
   - Espone gli endpoint REST
   - Gestisce la validazione dei parametri
   - Formatta le risposte in formato standard

3. **Filtri di Contenuto**:
   - **Pruning**: Utilizza `PruningContentFilter` per rimuovere contenuti irrilevanti
   - **BM25**: Utilizza `BM25ContentFilter` per filtrare contenuti in base a una query

### Flusso di Esecuzione

1. La richiesta viene validata tramite Pydantic
2. Il crawler viene configurato con i parametri forniti
3. Il browser viene avviato in modalità headless
4. La pagina viene caricata ed elaborata
5. I contenuti vengono estratti e filtrati secondo le preferenze
6. La risposta viene formattata e restituita

## Best Practices

1. **Performance**:
   - Utilizzare il `css_selector` per limitare l'elaborazione a specifiche parti della pagina
   - Impostare `extract_media=false` se non si necessita dei dettagli sulle immagini
   - Utilizzare `cache_mode="ENABLED"` per pagine che cambiano raramente

2. **Robustezza**:
   - Impostare sempre un timeout adeguato
   - Gestire correttamente gli errori lato client
   - Utilizzare `wait_for_load=true` per pagine con contenuti dinamici

3. **Contenuti**:
   - Utilizzare `content_filter="pruning"` per rimuovere automaticamente elementi non rilevanti
   - Per estrazioni specifiche, utilizzare `content_filter="bm25"` con una query pertinente

## Esempio di Utilizzo

### Estrazione di Articoli con Pruning

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/api/crawl/page",
    headers={"X-API-Token": "your_api_token"},
    json={
        "url": "https://example.com/article",
        "content_filter": "pruning",
        "extract_links": True,
        "exclude_external_links": False
    }
)

result = response.json()
if result["success"]:
    # Accesso al markdown filtrato
    markdown_content = result["data"]["fit_markdown"]
    print(markdown_content)
    
    # Accesso ai link estratti
    internal_links = result["data"]["links"]["internal"]
    external_links = result["data"]["links"]["external"]
    print(f"Link interni: {len(internal_links)}, Link esterni: {len(external_links)}")
```

### Ricerca Specifica con BM25

```python
import requests

response = requests.get(
    "http://localhost:8000/api/crawl/page",
    headers={"X-API-Token": "your_api_token"},
    params={
        "url": "https://example.com/documentation",
        "content_filter": "bm25",
        "bm25_query": "installation guide",
        "screenshot": True
    }
)

result = response.json()
if result["success"]:
    # Accesso al markdown filtrato (contenente solo le parti rilevanti per "installation guide")
    relevant_content = result["data"]["fit_markdown"]
    print(relevant_content)
    
    # Salvataggio dello screenshot
    if "screenshot" in result["data"]:
        import base64
        screenshot_data = base64.b64decode(result["data"]["screenshot"])
        with open("screenshot.png", "wb") as f:
            f.write(screenshot_data)
```

## Limitazioni Conosciute

1. JavaScript complesso o SPA molto dinamiche potrebbero richiedere parametri avanzati
2. Alcuni siti potrebbero bloccare l'accesso da browser automatizzati
3. L'estrazione di contenuti altamente strutturati potrebbe richiedere selettori CSS specifici
4. I filtri di contenuto sono euristici e potrebbero non essere perfetti per tutti i casi d'uso

## Considerazioni di Sicurezza

1. L'esecuzione di JavaScript arbitrario richiede attenzione
2. Rispettare i Terms of Service dei siti web target
3. Implementare rate limiting e timeouts per evitare sovraccarichi
4. Non esporre l'API pubblicamente senza adeguata autenticazione

## Configurazione

Le impostazioni per questa funzionalità sono configurabili tramite il file `.env`:

```
# Crawl4AI specifiche
CRAWL4AI_TIMEOUT=60
CRAWL4AI_CACHE_MODE=BYPASS
CRAWL4AI_RATE_LIMIT=10
CRAWL4AI_COOLDOWN=60
```
