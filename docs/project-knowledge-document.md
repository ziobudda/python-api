# Python API REST - Documentazione Struttura Progetto

## Panoramica

Il progetto "Python API REST" è un sistema backend basato su Python che espone diversi endpoint REST per fornire servizi come automazione browser, ricerca su Google e altri servizi di web scraping. Il framework principale utilizzato è FastAPI, che offre prestazioni elevate e supporto per documentazione automatica.

## Struttura delle Directory

```
python-api/
│
├── api/                    # Package principale delle API
│   ├── routes/             # Endpoint API organizzati per moduli
│   │   ├── __init__.py
│   │   ├── browser.py      # API per automazione browser
│   │   ├── search.py       # API per ricerca Google
│   │   └── crawl.py        # API per web crawling
│   │
│   ├── utils/              # Utilità condivise
│   │   ├── __init__.py
│   │   ├── auth.py         # Gestione autenticazione
│   │   ├── responses.py    # Formattatori di risposta standard
│   │   └── browser/        # Modulo per automazione browser
│   │
│   └── __init__.py
│
├── config/                 # Configurazioni
│   ├── __init__.py
│   └── settings.py         # Impostazioni dell'applicazione
│
├── tests/                  # Test automatizzati
│
├── venv/                   # Ambiente virtuale Python
│
├── .env                    # Variabili d'ambiente
├── .gitignore              # File da escludere dal controllo versione
├── app.py                  # Punto di ingresso dell'applicazione
├── README.md               # Documentazione del progetto
├── requirements.txt        # Dipendenze del progetto
├── run.sh                  # Script per avviare l'applicazione
└── setup.sh                # Script per configurare l'ambiente
```

## Componenti Principali

### 1. File di Base

#### app.py
- Punto di ingresso dell'applicazione
- Configura e inizializza FastAPI
- Registra i router per i diversi endpoint
- Configura middleware, gestione errori e documentazione
- Avvia il server quando eseguito direttamente

```python
# Esempio di registrazione router
app.include_router(browser_router)
app.include_router(search_router)
app.include_router(crawl_router)
```

#### config/settings.py
- Carica configurazioni da variabili d'ambiente
- Utilizza python-dotenv per caricare il file .env
- Contiene tutte le impostazioni dell'applicazione
- Formatta e valida le configurazioni

```python
# Esempio di configurazione
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
API_TOKEN = os.getenv("API_TOKEN", "default_insecure_token")
```

### 2. Modulo API

#### api/routes/
Contiene i router FastAPI organizzati per funzionalità:

- **browser.py**: API per automazione browser con Playwright
  - `POST /api/browser/load`: Carica una pagina con opzioni avanzate
  - `GET /api/browser/load`: Versione semplificata per richieste GET

- **search.py**: API per ricerche su Google
  - `POST /api/search/google`: Esegue una ricerca su Google
  - `GET /api/search/google`: Versione semplificata per richieste GET

- **crawl.py**: API per web crawling
  - Endpoint per estrarre dati da siti web

#### api/utils/
Contiene utility condivise tra diversi moduli:

- **auth.py**: Gestione autenticazione
  - Implementa `token_dependency` per verificare l'API token
  - Utilizzo come dipendenza FastAPI

```python
# Esempio di utilizzo
@router.post("/endpoint")
async def endpoint(request: RequestModel, token: str = token_dependency):
    # Logica dell'endpoint
```

- **responses.py**: Formattazione risposte
  - `success_response()`: Formatta risposte di successo
  - `error_response()`: Formatta risposte di errore

```python
# Esempio di risposta di successo
return success_response(
    data=result,
    message="Operazione completata con successo"
)

# Esempio di risposta di errore
return error_response(
    message="Errore durante l'operazione",
    error_type="OperationError",
    details={"param": value}
)
```

- **browser/**: Modulo per automazione browser
  - Utilizza Playwright per automazione

### 3. Convenzioni di Codice

#### Struttura dei File Router

Ogni file di router segue uno schema comune:
1. Import delle dipendenze
2. Definizione dei modelli di dati Pydantic
3. Creazione del router con prefisso e tag
4. Implementazione degli endpoint
5. Gestione degli errori

```python
from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel
from api.utils.responses import success_response, error_response
from api.utils.auth import token_dependency

# Modelli di dati
class RequestModel(BaseModel):
    param1: str
    param2: Optional[int] = None

# Router
router = APIRouter(prefix="/api/feature", tags=["FeatureName"])

@router.post("/endpoint")
async def endpoint(
    request: RequestModel,
    token: str = token_dependency
):
    try:
        # Logica dell'endpoint
        result = {}
        return success_response(data=result, message="Success message")
    except Exception as e:
        return error_response(
            message=f"Error message: {str(e)}",
            error_type="ErrorType",
            details={"request": request.dict()}
        )
```

#### Formato delle Risposte

Tutte le risposte seguono uno schema JSON standard:

- Risposta di successo:
```json
{
  "success": true,
  "data": { /* Dati risposta */ },
  "message": "Messaggio opzionale"
}
```

- Risposta di errore:
```json
{
  "success": false,
  "error": {
    "message": "Descrizione dell'errore",
    "type": "TipoErrore",
    "details": { /* Dettagli aggiuntivi */ }
  }
}
```

### 4. Autenticazione

Tutte le API sono protette da autenticazione tramite token. Il token viene passato tramite header HTTP `X-API-Token` e verificato dalla dipendenza `token_dependency` in `api/utils/auth.py`.

La configurazione del token avviene tramite la variabile d'ambiente `API_TOKEN` o il file `.env`.

### 5. Logging

Il sistema utilizza il modulo standard di logging di Python. Il livello di log può essere configurato tramite la variabile d'ambiente `LOG_LEVEL`.

```python
import logging
logger = logging.getLogger(__name__)

# Utilizzo
logger.info("Informational message")
logger.error("Error message")
```

## Come Estendere il Progetto

### Aggiungere un Nuovo Endpoint

1. Creare un nuovo file in `api/routes/` per il modulo
2. Definire i modelli di dati Pydantic
3. Creare il router e implementare gli endpoint
4. Registrare il router in `app.py`

### Aggiungere una Nuova Utility

1. Creare un nuovo file o sottodirectory in `api/utils/`
2. Implementare le funzionalità necessarie
3. Importare e utilizzare nei router o in altre utility

### Aggiungere Nuove Configurazioni

1. Aggiungere le nuove configurazioni in `config/settings.py`
2. Utilizzare le configurazioni nei moduli appropriati

## Best Practices

1. Utilizzare sempre `success_response()` e `error_response()` per formattare le risposte
2. Proteggere tutti gli endpoint con `token_dependency`
3. Gestire le eccezioni in tutti gli endpoint
4. Utilizzare logger per tracciare operazioni ed errori
5. Definire modelli di dati Pydantic per tutte le richieste e risposte
6. Seguire il pattern REST per le API
