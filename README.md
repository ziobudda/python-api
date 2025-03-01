# Python REST API

Un sistema in Python che risponde a chiamate esterne in modalità REST, fornendo risposte in formato JSON.

## Struttura del Progetto

```
python-api/
│
├── api/                    # Package principale delle API
│   ├── routes/             # Endpoint API organizzati per moduli
│   │   ├── browser.py      # Endpoint per automazione browser
│   │   ├── search.py       # Endpoint per ricerche su Google
│   │   ├── crawl.py        # Endpoint per crawling con Crawl4AI
│   │   └── memory.py       # Endpoint per il sistema memory
│   └── utils/              # Utilità condivise
│       ├── responses.py    # Formattatori di risposta standardizzati
│       ├── auth.py         # Gestione autenticazione
│       ├── browser/        # Modulo per automazione browser
│       │   ├── page_loader.py    # Caricamento pagine web
│       │   ├── google_search.py  # Funzionalità di ricerca Google
│       │   └── crawl4ai_client.py # Client per Crawl4AI
│       └── memory/         # Sistema di memorizzazione interazioni
│           ├── memory_system.py  # Implementazione pattern singleton
│           ├── manager.py        # Gestione operazioni di memoria
│           ├── models.py         # Modelli di dati
│           └── storage/          # Implementazioni di storage
│
├── config/                 # Configurazioni
│   ├── settings.py         # Impostazioni dell'applicazione
│   └── memory.yaml         # Configurazione del sistema memory
│
├── data/                   # Directory per dati persistenti
│   └── memory/             # Dati del sistema memory
│       ├── interactions.json  # Storage principale delle interazioni
│       └── backups/        # Backup automatici
│
├── tests/                  # Test automatizzati
│
├── venv/                   # Ambiente virtuale Python (non incluso nel controllo versione)
│
├── .env                    # Variabili d'ambiente (non incluso nel controllo versione)
├── .gitignore              # File da escludere dal controllo versione
├── app.py                  # Punto di ingresso dell'applicazione
├── README.md               # Documentazione
└── requirements.txt        # Dipendenze del progetto
```

## Requisiti

- Python 3.8 o versione successiva
- FastAPI
- Uvicorn
- Playwright (per automazione browser)
- Crawl4AI (per crawling avanzato)
- PyYAML (per configurazione memory)
- Altri pacchetti elencati in `requirements.txt`

## Installazione

1. Clona il repository:
   ```
   git clone <url-repository>
   cd python-api
   ```

2. Crea un ambiente virtuale e attivalo:
   ```
   python -m venv venv
   source venv/bin/activate  # su Windows: venv\Scripts\activate
   ```

3. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   playwright install
   ```

4. Copia il file `.env.example` in `.env` e personalizza le variabili d'ambiente secondo necessità. Assicurati di impostare un valore sicuro per `API_TOKEN`.

5. Crea le directory necessarie per il sistema memory:
   ```
   mkdir -p data/memory/backups
   ```

## Avvio dell'Applicazione

Per avviare il server in modalità sviluppo:

```
python app.py
```

Oppure utilizzando direttamente uvicorn:

```
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

L'API sarà disponibile all'indirizzo: http://localhost:8000

## Documentazione API

La documentazione interattiva delle API è disponibile ai seguenti URL:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Autenticazione

Tutte le API richiedono un token di autenticazione che deve essere passato nell'header della richiesta come `X-API-Token`.

Esempio:
```bash
curl -X GET "http://localhost:8000/api/search/google?query=python" -H "accept: application/json" -H "X-API-Token: your_secret_token_here"
```

Il token può essere configurato nel file `.env` attraverso la variabile `API_TOKEN`.

## Utilizzo

Esempi di utilizzo delle API (incluso il token di autenticazione):

### Eseguire una ricerca su Google

```bash
curl -X GET "http://localhost:8000/api/search/google?query=python&num_results=5" -H "accept: application/json" -H "X-API-Token: your_secret_token_here"
```

### Caricare una pagina web tramite browser automatizzato

```bash
curl -X GET "http://localhost:8000/api/browser/load?url=https://www.example.com&screenshot=true" -H "accept: application/json" -H "X-API-Token: your_secret_token_here"
```

### Caricare una pagina web con opzioni avanzate

```bash
curl -X POST "http://localhost:8000/api/browser/load" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -H "X-API-Token: your_secret_token_here" \
     -d '{"url":"https://www.example.com","wait_for_load":true,"screenshot":true,"wait_time":1000,"viewport":{"width":1920,"height":1080},"user_agent":"Mozilla/5.0...","evaluate_js":"return document.title;"}'
```

### Eseguire il crawling di una pagina web con Crawl4AI

```bash
curl -X GET "http://localhost:8000/api/crawl/page?url=https://www.example.com&content_filter=pruning" -H "accept: application/json" -H "X-API-Token: your_secret_token_here"
```

### Registrare una nuova interazione nel sistema memory

```bash
curl -X POST "http://localhost:8000/api/memory/interactions" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -H "X-API-Token: your_secret_token_here" \
     -d '{"agent_id":"example-agent","command":"example-command","prompt":"Esempio di prompt","response":"Esempio di risposta","cost":0.01,"metadata":{"key":"value"}}'
```

### Recuperare le interazioni recenti

```bash
curl -X GET "http://localhost:8000/api/memory/interactions/recent?limit=5" -H "accept: application/json" -H "X-API-Token: your_secret_token_here"
```

### Cercare nelle interazioni

```bash
curl -X GET "http://localhost:8000/api/memory/interactions/search?query=esempio" -H "accept: application/json" -H "X-API-Token: your_secret_token_here"
```

## Test

Per eseguire i test automatizzati:

```
pytest
```

## Funzionalità Principali

### Modulo di Ricerca Google
- Esecuzione di ricerche su Google tramite browser automatizzato
- Supporto per paginazione dei risultati
- Estrazione strutturata di titoli, URL e descrizioni
- Rimozione automatica dei duplicati tra le pagine

### Modulo di Automazione Browser
- Caricamento di pagine web tramite browser reale (Playwright)
- Acquisizione di screenshot
- Esecuzione di JavaScript personalizzato
- Supporto per varie configurazioni (viewport, user-agent)

### Modulo di Crawling con Crawl4AI
- Crawling avanzato di pagine web con supporto JavaScript
- Estrazione di link interni ed esterni
- Generazione di markdown dai contenuti HTML
- Filtri di contenuto per estrazione di informazioni rilevanti:
  - Pruning: rimuove contenuti irrilevanti in base alla densità di testo
  - BM25: filtra contenuti in base a rilevanza per una query specifica

### Sistema Memory
- Memorizzazione persistente delle interazioni API
- Recupero e ricerca delle interazioni per vari criteri (ID, data, agente, ecc.)
- Backup automatico dei dati
- Configurazione flessibile tramite YAML
- Pattern singleton per gestione efficiente delle risorse
- Supporto per multi-storage per separare diversi tipi di interazioni

## Licenza

[Inserire informazioni sulla licenza]
