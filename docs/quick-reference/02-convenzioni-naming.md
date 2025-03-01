# Convenzioni di Naming e Organizzazione

## Convenzioni Generali

- **snake_case**: Utilizzato per variabili, funzioni, metodi, moduli e package
- **CamelCase**: Utilizzato per classi e modelli Pydantic
- **UPPERCASE**: Utilizzato per costanti e variabili d'ambiente

## Struttura dei File di Router

I file di router seguono uno schema comune:

```python
# 1. Importazioni
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from api.utils.responses import success_response, error_response
from api.utils.auth import token_dependency
# Importazioni specifiche del modulo...

# 2. Logger dedicato al modulo
logger = logging.getLogger(__name__)

# 3. Modelli Pydantic
class RequestModel(BaseModel):
    field1: str
    field2: Optional[int] = None
    # ...

class ResponseModel(BaseModel):
    id: str
    field1: str
    # ...

# 4. Istanziazione del Router
router = APIRouter(prefix="/api/feature", tags=["FeatureName"])

# 5. Definizione degli Endpoint
@router.get("/resource")
async def get_resource(
    # Parametri...
    token: str = token_dependency
):
    """Docstring che descrive l'endpoint"""
    try:
        # Logica dell'endpoint
        return success_response(data=result)
    except Exception as e:
        return error_response(
            message=f"Errore descrittivo: {str(e)}",
            error_type="ErrorType"
        )
```

## Organizzazione dei Moduli

### Directory dei Router

Ogni router è organizzato per funzionalità, in genere seguendo questa struttura di base:

- **`browser.py`**: Funzionalità di automazione browser
- **`search.py`**: Funzionalità di ricerca
- **`memory.py`**: Funzionalità del sistema memory
- **`crawl.py`**: Funzionalità di crawling

### Struttura dei Nomi di Endpoint

Gli endpoint API seguono una struttura RESTful:

- **Collezioni di Risorse**: Plurale
  - `GET /api/memory/interactions`
  - `POST /api/memory/interactions`

- **Risorse Specifiche**: Singolare con ID
  - `GET /api/memory/interactions/{interaction_id}`

- **Operazioni su Collezioni**: Verbo dopo la collezione
  - `GET /api/memory/interactions/search`
  - `GET /api/memory/interactions/recent`

### Prefissi di Log

I messaggi di log utilizzano prefissi standard:

- **Info**: Operazioni normali
  - `logger.info(f"Richiesta lista interazioni (agent_id={agent_id})")`

- **Warning**: Situazioni anomale ma non critiche
  - `logger.warning(f"Rate limit superato per il client {client_id}")`

- **Error**: Errori che richiedono attenzione
  - `logger.error(f"Errore durante la ricerca: {str(e)}")`

## Convenzioni per i Modelli Pydantic

- **Request Models**: Suffisso descrittivo + Input specifico
  - `CreateInteractionRequest`
  - `SearchQuery`

- **Response Models**: Suffisso descrittivo + Output specifico
  - `InteractionResponse`
  - `SearchResults`

## Convenzioni per i Tipi di Errore

I tipi di errore seguono il pattern `NomeFeature` + `ErrorType`:

- `MemoryError`
- `MemoryRetrievalError`
- `SearchTimeout`
- `GoogleBlockError`

## Convenzioni per le Variabili d'Ambiente

Le variabili d'ambiente sono in UPPERCASE e utilizzano prefissi per il raggruppamento:

- `GOOGLE_DEFAULT_LANG`
- `GOOGLE_MAX_RESULTS`
- `MEMORY_CONFIG_PATH`
- `MEMORY_ACTIVE_STORAGE`
