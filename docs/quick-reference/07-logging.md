# Sistema di Logging

Questo documento descrive il sistema di logging utilizzato nel progetto Python API REST e le best practices per utilizzarlo in modo efficace.

## Configurazione del Logging

Il logging viene configurato nel file `app.py` all'avvio dell'applicazione:

```python
import logging
from config import settings

# Configurazione del logging
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

## Livelli di Log

Il progetto utilizza i seguenti livelli di log, in ordine crescente di severità:

- **DEBUG**: Informazioni dettagliate, utili per il debug
- **INFO**: Conferma che le cose funzionano come previsto
- **WARNING**: Indicazione che qualcosa di inaspettato è accaduto, ma l'applicazione funziona ancora
- **ERROR**: Errore che ha impedito l'esecuzione di una funzione
- **CRITICAL**: Errore grave che potrebbe impedire l'esecuzione dell'applicazione

Il livello configurato in `settings.LOG_LEVEL` determina quali messaggi vengono registrati (vengono registrati i messaggi di quel livello e superiori).

## Creazione di un Logger per un Modulo

Ogni modulo dovrebbe creare il proprio logger con il nome del modulo:

```python
import logging

logger = logging.getLogger(__name__)

# Utilizzo
logger.info("Messaggio informativo")
logger.error("Si è verificato un errore")
```

## Pattern di Logging nei Router

I router seguono un pattern comune per il logging:

```python
import logging

logger = logging.getLogger(__name__)

@router.get("/resource")
async def get_resource(param: str):
    # Log all'inizio della richiesta
    logger.info(f"Richiesta risorsa con param={param}")
    
    try:
        # Logica dell'endpoint...
        result = process_request(param)
        
        # Log di successo
        logger.info(f"Richiesta completata con successo per param={param}")
        return success_response(data=result)
    except Exception as e:
        # Log di errore
        logger.error(f"Errore durante l'elaborazione della richiesta: {str(e)}")
        return error_response(message=str(e))
```

## Best Practices per il Logging

### 1. Log Contestuali

Includere informazioni di contesto nei messaggi di log per facilitare il debug:

```python
# ✅ Buono: include informazioni di contesto
logger.info(f"Elaborazione richiesta search con query='{query}', lang={lang}")

# ❌ Insufficiente: manca il contesto
logger.info("Elaborazione richiesta search")
```

### 2. Livelli di Log Appropriati

Usare il livello di log appropriato per ogni messaggio:

```python
# DEBUG: Dettagli interni utili solo per il debug
logger.debug(f"Parametri di paginazione: limit={limit}, offset={offset}")

# INFO: Operazioni normali
logger.info(f"Richiesta search completata: trovati {count} risultati")

# WARNING: Situazioni anomale ma non critiche
logger.warning(f"Rate limit quasi raggiunto per il client {client_id}")

# ERROR: Errori che richiedono attenzione
logger.error(f"Errore durante la chiamata al servizio esterno: {str(e)}")

# CRITICAL: Problemi critici che richiedono intervento immediato
logger.critical(f"Database non disponibile: {str(e)}")
```

### 3. Struttura Coerente

Mantenere una struttura coerente nei messaggi di log:

```python
# Inizio operazione
logger.info(f"Inizio {operazione} con {parametri}")

# Fine operazione con successo
logger.info(f"{operazione} completata con successo: {risultati}")

# Errore
logger.error(f"Errore durante {operazione}: {messaggio_errore}")
```

### 4. Evitare Log Eccessivi

Evitare di loggare dati sensibili o payload di grandi dimensioni:

```python
# ✅ Buono: log di dimensioni di payload anziché il payload completo
logger.debug(f"Ricevuto payload JSON di {len(json_str)} bytes")

# ❌ Cattivo: log di payload completi
logger.debug(f"Payload ricevuto: {json_str}")
```

### 5. Logging delle Eccezioni

Utilizzare `logger.exception()` dentro i blocchi `except` per includere automaticamente lo stack trace:

```python
try:
    # Operazione che può generare un'eccezione
    result = process_data(data)
except Exception as e:
    logger.exception("Errore durante l'elaborazione dei dati")
    # Lo stack trace viene incluso automaticamente
```

## Configurazione per Ambienti Diversi

- **Sviluppo**: Livello DEBUG per massima verbosità
- **Testing**: Livello INFO per operazioni normali
- **Produzione**: Livello WARNING o superiore per ridurre il rumore

## Esempio di Configurazione in `.env`

```
# Sviluppo
LOG_LEVEL=debug

# Produzione
LOG_LEVEL=info
```

## Correlazione delle Richieste

Per tracciare l'intero ciclo di vita di una richiesta, si può generare un ID di richiesta e includerlo nei log:

```python
import uuid

@app.middleware("http")
async def add_request_id(request, call_next):
    request_id = str(uuid.uuid4())
    # Aggiungi request_id ai dati di contesto
    request.state.request_id = request_id
    
    logger.info(f"[{request_id}] Inizio richiesta {request.method} {request.url.path}")
    
    # Procedi con la richiesta
    response = await call_next(request)
    
    logger.info(f"[{request_id}] Fine richiesta: status {response.status_code}")
    
    return response
```

Poi nei router:

```python
@router.get("/resource")
async def get_resource(request: Request):
    request_id = request.state.request_id
    logger.info(f"[{request_id}] Elaborazione richiesta get_resource")
    # ...
```
