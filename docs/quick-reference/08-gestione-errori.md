# Gestione degli Errori

Questo documento descrive il pattern di gestione degli errori utilizzato nel progetto Python API REST e le best practices per gestire gli errori in modo efficace e coerente.

## Pattern di Base

Tutti gli endpoint dovrebbero utilizzare un pattern try/except per catturare e gestire gli errori:

```python
@router.get("/resource")
async def get_resource():
    try:
        # Logica dell'endpoint
        result = process_data()
        return success_response(data=result)
    except Exception as e:
        logger.error(f"Errore durante l'elaborazione: {str(e)}")
        return error_response(
            message=f"Si è verificato un errore: {str(e)}",
            error_type="ProcessingError"
        )
```

## Gestione Globale degli Errori

Il progetto definisce un gestore globale delle eccezioni in `app.py` che cattura tutte le eccezioni non gestite:

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Gestore globale delle eccezioni che formatta tutte le risposte di errore
    in un formato JSON coerente.
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc)
            }
        }
    )
```

## Tipi di Errori Comuni

### 1. Errori di Validazione

```python
@router.post("/resource")
async def create_resource(data: ResourceModel):
    try:
        # Validazione custom oltre a quella di Pydantic
        if data.start_date > data.end_date:
            return error_response(
                message="La data di inizio deve essere precedente alla data di fine",
                error_type="ValidationError",
                status_code=400
            )
        
        # Procedi con la creazione...
        
    except Exception as e:
        logger.error(f"Errore durante la creazione: {str(e)}")
        return error_response(message=str(e))
```

### 2. Errori di Risorsa Non Trovata

```python
@router.get("/resource/{resource_id}")
async def get_resource(resource_id: str):
    try:
        resource = find_resource(resource_id)
        
        if not resource:
            return error_response(
                message=f"Risorsa non trovata: {resource_id}",
                error_type="ResourceNotFound",
                status_code=404
            )
        
        return success_response(data=resource)
        
    except Exception as e:
        logger.error(f"Errore durante il recupero: {str(e)}")
        return error_response(message=str(e))
```

### 3. Errori di Servizi Esterni

```python
@router.get("/external-data")
async def get_external_data():
    try:
        try:
            data = await external_service.get_data()
            return success_response(data=data)
        except ExternalServiceException as e:
            return error_response(
                message=f"Errore nel servizio esterno: {str(e)}",
                error_type="ExternalServiceError",
                status_code=502
            )
            
    except Exception as e:
        logger.error(f"Errore interno: {str(e)}")
        return error_response(
            message="Si è verificato un errore interno",
            error_type="InternalError",
            status_code=500
        )
```

## Gerarchia delle Eccezioni Personalizzate

Per una gestione più strutturata, è possibile definire una gerarchia di eccezioni personalizzate:

```python
# api/utils/exceptions.py

class APIException(Exception):
    """Classe base per le eccezioni API"""
    status_code = 500
    error_type = "APIException"
    
    def __init__(self, message, details=None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(APIException):
    """Eccezione per errori di validazione"""
    status_code = 400
    error_type = "ValidationError"

class NotFoundException(APIException):
    """Eccezione per risorse non trovate"""
    status_code = 404
    error_type = "NotFound"

class AuthenticationException(APIException):
    """Eccezione per errori di autenticazione"""
    status_code = 401
    error_type = "AuthenticationError"

class ExternalServiceException(APIException):
    """Eccezione per errori in servizi esterni"""
    status_code = 502
    error_type = "ExternalServiceError"
```

Utilizzo nel router:

```python
from api.utils.exceptions import ValidationException, NotFoundException

@router.get("/resource/{resource_id}")
async def get_resource(resource_id: str):
    try:
        resource = find_resource(resource_id)
        
        if not resource:
            raise NotFoundException(f"Risorsa non trovata: {resource_id}")
        
        return success_response(data=resource)
        
    except APIException as e:
        return error_response(
            message=e.message,
            error_type=e.error_type,
            details=e.details,
            status_code=e.status_code
        )
    except Exception as e:
        logger.error(f"Errore non gestito: {str(e)}")
        return error_response(
            message="Si è verificato un errore interno",
            error_type="InternalError",
            status_code=500
        )
```

## Errori Pydantic

FastAPI gestisce automaticamente gli errori di validazione Pydantic, ma è possibile personalizzare le risposte di errore:

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        error_msg = f"{error['loc'][-1]}: {error['msg']}"
        errors.append(error_msg)
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "type": "ValidationError",
                "message": "Errore di validazione dei dati",
                "details": {
                    "errors": errors
                }
            }
        }
    )
```

## Best Practices per la Gestione degli Errori

### 1. Messaggi di Errore Chiari

Fornire messaggi di errore chiari e informativi:

```python
# ✅ Buono: messaggio chiaro e specifico
return error_response(
    message="Nome utente già in uso: scegliere un nome diverso",
    error_type="DuplicateUserError"
)

# ❌ Insufficiente: messaggio troppo generico
return error_response(
    message="Errore di validazione",
    error_type="ValidationError"
)
```

### 2. Uso Consistente dei Tipi di Errore

Utilizzare tipi di errore consistenti in tutta l'applicazione:

```python
# Errori di validazione
"ValidationError"

# Errori di risorsa non trovata
"ResourceNotFound", "UserNotFound", "ItemNotFound"

# Errori di autenticazione/autorizzazione
"AuthenticationError", "AuthorizationError", "TokenExpired"

# Errori di servizi esterni
"ExternalServiceError", "APITimeoutError"

# Errori interni
"InternalError", "DatabaseError"
```

### 3. Gestione Differenziata delle Eccezioni

Gestire in modo differenziato i diversi tipi di eccezioni:

```python
try:
    # Logica dell'endpoint
    result = process_data()
    return success_response(data=result)
except ValidationException as e:
    return error_response(
        message=e.message,
        error_type="ValidationError",
        status_code=400
    )
except NotFoundException as e:
    return error_response(
        message=e.message,
        error_type="NotFoundError",
        status_code=404
    )
except ExternalServiceException as e:
    logger.error(f"Errore nel servizio esterno: {str(e)}")
    return error_response(
        message="Errore durante la comunicazione con un servizio esterno",
        error_type="ExternalServiceError",
        status_code=502
    )
except Exception as e:
    logger.error(f"Errore interno non gestito: {str(e)}")
    return error_response(
        message="Si è verificato un errore interno",
        error_type="InternalError",
        status_code=500
    )
```

### 4. Non Esporre Dettagli Tecnici agli Utenti

In produzione, evitare di esporre dettagli tecnici degli errori agli utenti:

```python
# Sviluppo: includi dettagli completi
return error_response(
    message=f"Errore di connessione al database: {str(e)}",
    error_type="DatabaseError",
    details={"exception": str(e), "traceback": traceback.format_exc()}
)

# Produzione: messaggio generico per l'utente, dettagli nei log
logger.error(f"Errore di connessione al database: {str(e)}\n{traceback.format_exc()}")
return error_response(
    message="Si è verificato un errore durante l'accesso ai dati",
    error_type="DatabaseError"
)
```

### 5. Log Dettagliati per Debugging

Registrare log dettagliati per facilitare il debugging:

```python
try:
    # Logica complessa
except Exception as e:
    logger.error(
        f"Errore durante l'elaborazione: {str(e)}\n"
        f"Parametri: {params}\n"
        f"Stack Trace: {traceback.format_exc()}"
    )
    return error_response(message="Si è verificato un errore durante l'elaborazione")
```
