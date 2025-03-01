# Struttura del Progetto Python API REST

## Directory Principali

```
python-api/
│
├── api/                    # Package principale delle API
│   ├── routes/             # Endpoint API organizzati per moduli
│   │   ├── __init__.py
│   │   ├── browser.py      # API per automazione browser
│   │   ├── search.py       # API per ricerca Google
│   │   ├── crawl.py        # API per web crawling
│   │   └── memory.py       # API per il sistema memory
│   │
│   ├── utils/              # Utilità condivise
│   │   ├── __init__.py
│   │   ├── auth.py         # Gestione autenticazione
│   │   ├── responses.py    # Formattatori di risposta standard
│   │   ├── browser/        # Modulo per automazione browser
│   │   └── memory/         # Sistema di memorizzazione interazioni
│   │
│   └── __init__.py
│
├── config/                 # Configurazioni
│   ├── __init__.py
│   ├── settings.py         # Impostazioni dell'applicazione
│   └── memory.yaml         # Configurazione del sistema memory
│
├── data/                   # Directory per i dati persistenti
│   └── memory/             # Dati del sistema memory
│       ├── interactions.json  # File principale di storage
│       └── backups/        # Backup automatici
│
├── tests/                  # Test automatizzati
│
├── docs/                   # Documentazione
│   └── quick-reference/    # Documenti di riferimento rapido
│
├── venv/                   # Ambiente virtuale Python
│
├── .env                    # Variabili d'ambiente (non controllato da git)
├── .gitignore              # File da escludere dal controllo versione
├── app.py                  # Punto di ingresso dell'applicazione
├── README.md               # Documentazione del progetto
├── requirements.txt        # Dipendenze del progetto
├── run.sh                  # Script per avviare l'applicazione
└── setup.sh                # Script per configurare l'ambiente
```

## File Principali e loro Scopo

### File di Base

- **app.py**: Punto di ingresso dell'applicazione
  - Configura FastAPI
  - Registra i router
  - Configura middleware e gestione errori
  - Avvia il server quando eseguito direttamente

- **.env**: Variabili d'ambiente per configurazione
  - Non controllato da git per sicurezza
  - Vedi `.env.example` per il formato

- **requirements.txt**: Elenco di tutte le dipendenze Python
  - Installabile con `pip install -r requirements.txt`

- **run.sh**: Script per avviare l'applicazione
  - Configura l'ambiente e avvia uvicorn

- **setup.sh**: Script di setup iniziale
  - Crea ambiente virtuale
  - Installa dipendenze
  - Inizializza strutture di directory necessarie

### Directory `api/routes/`

Contiene i vari router dell'API, organizzati per funzionalità:

- **browser.py**: Automazione browser con Playwright
- **search.py**: Ricerca su Google
- **crawl.py**: Web crawling e scraping
- **memory.py**: Sistema di memorizzazione delle interazioni

### Directory `api/utils/`

Contiene utility e servizi condivisi:

- **auth.py**: Gestione autenticazione con token
- **responses.py**: Formattazione standardizzata delle risposte
- **browser/**: Modulo per automazione browser
- **memory/**: Sistema di memorizzazione delle interazioni

### Directory `config/`

Contiene configurazioni dell'applicazione:

- **settings.py**: Carica e gestisce le impostazioni da variabili d'ambiente
- **memory.yaml**: Configurazione specifica per il sistema memory

## Flusso di Esecuzione

1. **Inizializzazione**: `app.py` carica configurazioni e crea l'app FastAPI
2. **Registrazione Router**: Tutti i router in `api/routes/` vengono registrati nell'app
3. **Configurazione Middleware**: Middleware CORS e altri vengono configurati
4. **Avvio Server**: Uvicorn avvia il server HTTP

## Dove Aggiungere Nuovi Componenti

- **Nuovi Endpoint API**: Creare un nuovo file in `api/routes/` seguendo il pattern esistente
- **Nuovi Servizi Utility**: Aggiungere in `api/utils/` o creare una nuova sottodirectory
- **Nuove Configurazioni**: Aggiungere in `config/settings.py` e nel file `.env`
