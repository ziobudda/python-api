# Pattern per l'Implementazione di Router

Questa guida rapida mostra come implementare un nuovo router (endpoint API) seguendo le convenzioni del progetto.

## Template di Base per un Router

```python
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from api.utils.responses import success_response, error_response
from api.utils.auth import token_dependency
import logging

# Logger specifico per il modulo
logger = logging.getLogger(__name__)

# Definizione dei modelli di dati
class RequestModel(BaseModel):
    field1: str
    field2: Optional[int] = None

class ResponseModel(BaseModel):
    id: str
    field1: str
    field2: Optional[int]
    created_at: str

# Creazione del router
router = APIRouter(prefix="/api/feature", tags=["FeatureName"])

@router.get("/resource", response_model=Dict[str, Any])
async def get_resources(
    param1: str = Query(..., description="Descrizione del parametro"),
    param2: Optional[int] = Query(None, description="Parametro opzionale"),
    token: str = token_dependency
):
    """
    Descrizione dettagliata dell'endpoint.
    
    Args:
        param1: Descrizione del parametro
        param2: Descrizione del parametro opzionale
        
    Returns:
        Dict: Risposta formattata con i dati
    """
    try:
        logger.info(f"Richiesta risorse con param1={param1}, param2={param2}")
        
        # Logica dell'endpoint...
        result = {}
        
        return success_response(
            data=result,
            message="Operazione completata con successo"
        )
    except Exception as e:
        logger.error(f"Errore nell'ottenere le risorse: {str(e)}")
        return error_response(
            message=f"Impossibile completare l'operazione: {str(e)}",
            error_type="FeatureError",
            details={"param1": param1}
        )

@router.get("/resource/{resource_id}", response_model=Dict[str, Any])
async def get_resource(
    resource_id: str = Path(..., description="ID della risorsa"),
    token: str = token_dependency
):
    """
    Recupera una risorsa specifica tramite ID.
    
    Args:
        resource_id: ID della risorsa da recuperare
        
    Returns:
        Dict: Dettagli della risorsa
    """
    try:
        logger.info(f"Richiesta risorsa: {resource_id}")
        
        # Logica per recuperare la risorsa...
        resource = None
        
        if not resource:
            return error_response(
                message=f"Risorsa non trovata: {resource_id}",
                error_type="ResourceNotFound",
                status_code=404
            )
        
        return success_response(
            data=resource
        )
    except Exception as e:
        logger.error(f"Errore nel recuperare la risorsa {resource_id}: {str(e)}")
        return error_response(
            message=f"Errore nel recupero della risorsa: {str(e)}",
            error_type="ResourceRetrievalError"
        )

@router.post("/resource", response_model=Dict[str, Any])
async def create_resource(
    resource: RequestModel,
    token: str = token_dependency
):
    """
    Crea una nuova risorsa.
    
    Args:
        resource: Dati della risorsa da creare
        
    Returns:
        Dict: Dettagli della risorsa creata
    """
    try:
        logger.info(f"Creazione nuova risorsa: {resource.field1}")
        
        # Logica per creare la risorsa...
        result = {}
        
        return success_response(
            data=result,
            message=f"Risorsa creata con successo: {result.get('id')}"
        )
    except Exception as e:
        logger.error(f"Errore nella creazione della risorsa: {str(e)}")
        return error_response(
            message=f"Impossibile creare la risorsa: {str(e)}",
            error_type="ResourceCreationError"
        )
```

## Registrazione del Router in app.py

Una volta creato il nuovo router, è necessario registrarlo in `app.py`:

```python
# Importazione del nuovo router
from api.routes.feature import router as feature_router

# Registrazione del router (aggiungere alle registrazioni esistenti)
app.include_router(feature_router)
```

## Tipi di Endpoint Comuni

### 1. Endpoint di Lettura (GET)

```python
@router.get("/resource", response_model=Dict[str, Any])
async def get_resources(
    # Parametri...
    token: str = token_dependency
):
    # Implementazione...
```

### 2. Endpoint di Lettura Singola (GET con ID)

```python
@router.get("/resource/{resource_id}", response_model=Dict[str, Any])
async def get_resource(
    resource_id: str = Path(..., description="ID della risorsa"),
    token: str = token_dependency
):
    # Implementazione...
```

### 3. Endpoint di Creazione (POST)

```python
@router.post("/resource", response_model=Dict[str, Any])
async def create_resource(
    resource: RequestModel,
    token: str = token_dependency
):
    # Implementazione...
```

### 4. Endpoint di Aggiornamento (PUT)

```python
@router.put("/resource/{resource_id}", response_model=Dict[str, Any])
async def update_resource(
    resource_id: str = Path(..., description="ID della risorsa"),
    resource: RequestModel,
    token: str = token_dependency
):
    # Implementazione...
```

### 5. Endpoint di Eliminazione (DELETE)

```python
@router.delete("/resource/{resource_id}", response_model=Dict[str, Any])
async def delete_resource(
    resource_id: str = Path(..., description="ID della risorsa"),
    token: str = token_dependency
):
    # Implementazione...
```

## Documentazione degli Endpoint

Ogni endpoint deve includere:

1. **Docstring**: Descrizione chiara dell'endpoint
2. **Args**: Descrizione di ogni parametro
3. **Returns**: Descrizione del formato di risposta

La documentazione sarà visibile nell'interfaccia Swagger UI (`/docs`).

## Pattern di Gestione Errori

Tutti gli endpoint devono seguire il pattern try/except:

```python
try:
    # Logica dell'endpoint...
    return success_response(data=result)
except Exception as e:
    logger.error(f"Messaggio errore: {str(e)}")
    return error_response(
        message=f"Messaggio per l'utente: {str(e)}",
        error_type="TipoErrore"
    )
```

## Parametri Comuni

- `token: str = token_dependency`: Per autenticazione (obbligatorio in tutti gli endpoint)
- `Query(...)`: Per parametri obbligatori nella query
- `Query(None)`: Per parametri opzionali nella query
- `Path(...)`: Per parametri nel percorso URL
