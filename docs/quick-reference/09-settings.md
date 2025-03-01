# Gestione delle Configurazioni

Questo documento descrive il sistema di gestione delle configurazioni utilizzato nel progetto Python API REST.

## Panoramica

Le configurazioni dell'applicazione sono gestite centralmente tramite il modulo `config/settings.py`, che carica le impostazioni da variabili d'ambiente e dal file `.env`.

## File di Configurazione Principali

### 1. config/settings.py

Questo file è il punto centrale per tutte le configurazioni dell'applicazione:

```python
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Configurazione ambiente
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"

# Configurazione server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Configurazione autenticazione API
API_TOKEN = os.getenv("API_TOKEN", "default_insecure_token")

# Configurazione per browser e ricerche
BROWSER_STEALTH_MODE = os.getenv("BROWSER_STEALTH_MODE", "True").lower() in ["true", "1", "yes"]
USE_PROXIES = os.getenv("USE_PROXIES", "False").lower() in ["true", "1", "yes"]
SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "90"))
SEARCH_RATE_LIMIT = int(os.getenv("SEARCH_RATE_LIMIT", "10"))
SEARCH_COOLDOWN = int(os.getenv("SEARCH_COOLDOWN", "60"))

# Google Search specifiche
GOOGLE_DEFAULT_LANG = os.getenv("GOOGLE_DEFAULT_LANG", "it")
GOOGLE_MAX_RESULTS = int(os.getenv("GOOGLE_MAX_RESULTS", "20"))
GOOGLE_MAX_PAGES = int(os.getenv("GOOGLE_MAX_PAGES", "10"))
GOOGLE_SLEEP_INTERVAL = float(os.getenv("GOOGLE_SLEEP_INTERVAL", "2.0"))

# Configurazioni Crawl4AI
CRAWL4AI_TIMEOUT = int(os.getenv("CRAWL4AI_TIMEOUT", "60"))
CRAWL4AI_CACHE_MODE = os.getenv("CRAWL4AI_CACHE_MODE", "BYPASS")
CRAWL4AI_RATE_LIMIT = int(os.getenv("CRAWL4AI_RATE_LIMIT", "10"))
CRAWL4AI_COOLDOWN = int(os.getenv("CRAWL4AI_COOLDOWN", "60"))

# Configurazioni Memory
MEMORY_CONFIG_PATH = os.getenv("MEMORY_CONFIG_PATH", "config/memory.yaml")
MEMORY_ACTIVE_STORAGE = os.getenv("MEMORY_ACTIVE_STORAGE", "default")
```

### 2. .env

Il file `.env` contiene le variabili d'ambiente specifiche per l'ambiente di esecuzione. Questo file non è versionato in git per motivi di sicurezza.

Esempio di file `.env`:

```
# Ambiente
ENV=development
LOG_LEVEL=debug

# Server
HOST=127.0.0.1
PORT=8000

# Autenticazione
API_TOKEN=your_secure_token_here

# Google Search
GOOGLE_DEFAULT_LANG=it
GOOGLE_MAX_RESULTS=20
GOOGLE_SLEEP_INTERVAL=1.5

# Memory
MEMORY_CONFIG_PATH=config/memory.yaml
MEMORY_ACTIVE_STORAGE=default
```

### 3. config/memory.yaml

File di configurazione specifico per il sistema memory:

```yaml
memory:
  active_storage: default
  storages:
    default:
      type: file
      path: data/memory/interactions.json
      backup:
        enabled: true
        backup_dir: data/memory/backups
        max_backups: 10
        interval_days: 7
    analytics:
      type: file
      path: data/memory/analytics.json
      backup:
        enabled: true
        backup_dir: data/memory/backups
        max_backups: 5
        interval_days: 14
```

## Tipi di Conversione

Le variabili d'ambiente sono sempre stringhe, ma vengono convertite nel tipo appropriato:

```python
# Interi
PORT = int(os.getenv("PORT", 8000))

# Float
GOOGLE_SLEEP_INTERVAL = float(os.getenv("GOOGLE_SLEEP_INTERVAL", "2.0"))

# Booleani
DEBUG = ENV == "development"
BROWSER_STEALTH_MODE = os.getenv("BROWSER_STEALTH_MODE", "True").lower() in ["true", "1", "yes"]
```

## Accesso alle Configurazioni

Per accedere alle configurazioni in altri moduli, importare il modulo `settings`:

```python
from config import settings

# Utilizzo
api_token = settings.API_TOKEN
max_results = settings.GOOGLE_MAX_RESULTS
```

## Organizzazione delle Configurazioni

Le configurazioni sono organizzate per area funzionale:

1. **Configurazioni dell'ambiente**: `ENV`, `DEBUG`, `LOG_LEVEL`
2. **Configurazioni del server**: `HOST`, `PORT`
3. **Configurazioni di autenticazione**: `API_TOKEN`
4. **Configurazioni funzionali specifiche**: `GOOGLE_*`, `CRAWL4AI_*`, `MEMORY_*`

## File .env.example

È buona pratica fornire un file `.env.example` che mostra tutte le variabili d'ambiente disponibili senza rivelare valori sensibili:

```
# Ambiente
ENV=development
LOG_LEVEL=info

# Server
HOST=0.0.0.0
PORT=8000

# Autenticazione
API_TOKEN=your_token_here

# Google Search
GOOGLE_DEFAULT_LANG=it
GOOGLE_MAX_RESULTS=20
GOOGLE_MAX_PAGES=10
GOOGLE_SLEEP_INTERVAL=2.0

# Memory
MEMORY_CONFIG_PATH=config/memory.yaml
MEMORY_ACTIVE_STORAGE=default
```

## Aggiungere Nuove Configurazioni

Per aggiungere una nuova configurazione:

1. Aggiungerla in `config/settings.py` utilizzando `os.getenv()` con un valore predefinito
2. Aggiornare il file `.env.example` con la nuova variabile
3. Aggiungere la nuova variabile al proprio file `.env` locale

Esempio di aggiunta di una nuova configurazione:

```python
# In config/settings.py
NEW_FEATURE_ENABLED = os.getenv("NEW_FEATURE_ENABLED", "False").lower() in ["true", "1", "yes"]
NEW_FEATURE_TIMEOUT = int(os.getenv("NEW_FEATURE_TIMEOUT", "30"))
```

## Configurazioni Specifiche per Ambiente

Le configurazioni possono variare in base all'ambiente di esecuzione:

```python
# In config/settings.py
if ENV == "production":
    # Impostazioni specifiche per l'ambiente di produzione
    LOG_LEVEL = os.getenv("LOG_LEVEL", "warning")
    DEBUG = False
else:
    # Impostazioni per ambienti di sviluppo
    LOG_LEVEL = os.getenv("LOG_LEVEL", "debug")
    DEBUG = True
```

## Best Practices

1. **Valori predefiniti**: Fornire sempre valori predefiniti ragionevoli per ogni configurazione
2. **Tipi appropriati**: Convertire sempre le variabili d'ambiente nel tipo corretto
3. **Organizzazione**: Raggruppare le configurazioni per area funzionale con commenti chiari
4. **Sicurezza**: Non memorizzare valori sensibili (token, chiavi) in file versionati
5. **Documentazione**: Mantenere aggiornato il file `.env.example` con tutte le configurazioni disponibili
6. **Validazione**: Validare le configurazioni critiche all'avvio dell'applicazione

```python
# Validazione configurazione
if not settings.API_TOKEN or settings.API_TOKEN == "default_insecure_token":
    if ENV == "production":
        raise ValueError("API_TOKEN non configurato in ambiente di produzione")
    else:
        logger.warning("Utilizzo del token API predefinito in ambiente di sviluppo")
```
