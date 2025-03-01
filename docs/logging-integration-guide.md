# Guida all'Integrazione del Sistema di Logging Configurabile

Questa guida mostra come integrare il nuovo sistema di logging configurabile nel progetto Python API REST esistente, senza modificare i file di progetto attuali.

## Panoramica

Il nuovo sistema di logging consente di:

1. Configurare la destinazione dei log (console o file) tramite il file `.env`
2. Impostare il livello di log (debug, info, warning, error, critical)
3. Configurare la rotazione dei file di log con dimensione massima e numero di backup
4. Mantenere la compatibilità con l'API di logging esistente

## Configurazione nel file `.env`

Aggiungi le seguenti variabili al tuo file `.env`:

```
# Configurazione Logging
LOG_LEVEL=debug                # Livello di log (debug, info, warning, error, critical)
LOG_TO_FILE=false              # true per salvare i log su file, false per console
LOG_FILE_PATH=logs/app.log     # Percorso del file di log
LOG_FILE_MAX_SIZE=10485760     # Dimensione massima del file in bytes (10MB)
LOG_FILE_BACKUP_COUNT=3        # Numero di file di backup da mantenere
```

## Integrazione nel Progetto

### Metodo 1: Utilizzo come Modulo Indipendente

Il modo più semplice per utilizzare il nuovo sistema di logging senza modificare i file esistenti è includerlo all'avvio dell'applicazione:

1. Copia il file `api/utils/logging_config.py` nella tua struttura di progetto
2. Crea uno script wrapper che configura il logging prima di avviare l'app principale

Esempio di script wrapper (`run_with_logging.py`):

```python
#!/usr/bin/env python
import os
import sys

# Aggiungi il percorso al progetto se necessario
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importa il modulo di configurazione del logging
from api.utils.logging_config import setup_logging

# Configura il logging
setup_logging()

# Importa e avvia l'app principale
import app

if __name__ == "__main__":
    app.main()  # Adatta questa chiamata al metodo di avvio della tua app
```

Esegui l'applicazione usando questo script invece di avviare direttamente `app.py`.

### Metodo 2: Integrazione Tramite Modulo di Avvio

Se preferisci un approccio più integrato, puoi creare un modulo di avvio:

1. Crea un file `run.py` nella directory principale del progetto
2. Questo file configura il logging e poi avvia l'applicazione 

```python
#!/usr/bin/env python
import os
import sys
import uvicorn
from api.utils.logging_config import setup_logging
from config import settings

def main():
    # Configura il logging
    setup_logging()
    
    # Avvia l'applicazione FastAPI con uvicorn
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="warning",  # Usa un livello basso per uvicorn, useremo i nostri logger
        access_log=False      # Disabilita il log di accesso di uvicorn
    )

if __name__ == "__main__":
    main()
```

### Utilizzo nei moduli esistenti

Per utilizzare il nuovo sistema di logging nei moduli esistenti, importa la funzione `get_logger`:

```python
from api.utils.logging_config import get_logger

# Crea un logger per questo modulo
logger = get_logger(__name__)

# Utilizzo
logger.info("Messaggio informativo")
logger.error("Si è verificato un errore")
```

## Testing della Configurazione

Per verificare che il sistema di logging funzioni correttamente:

1. Modifica il file `.env` impostando `LOG_TO_FILE=false` e `LOG_LEVEL=debug`
2. Avvia l'applicazione tramite lo script wrapper
3. Verifica che i log vengano visualizzati sulla console
4. Modifica il file `.env` impostando `LOG_TO_FILE=true`
5. Riavvia l'applicazione
6. Verifica che i log vengano scritti nel file specificato da `LOG_FILE_PATH`

## Note Importanti

- Assicurati che la directory specificata in `LOG_FILE_PATH` esista o sia creabile dall'applicazione
- Il sistema di logging è compatibile con i moduli che utilizzano `logging.getLogger(__name__)`
- I log vengono formattati come: `YYYY-MM-DD HH:MM:SS - module_name - LEVEL - Message`
- I file di log vengono automaticamente ruotati quando raggiungono la dimensione massima
