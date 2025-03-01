# Formato Standard delle Risposte API

Tutte le API nel progetto seguono un formato di risposta standardizzato per garantire coerenza e prevedibilità. Questo documento descrive il formato delle risposte e come utilizzare le funzioni di utility per generarle.

## Formato di Base

### Risposta di Successo

Tutte le risposte di successo seguono questo formato:

```json
{
  "success": true,
  "data": {
    // Contenuto specifico della risposta
  },
  "message": "Messaggio opzionale di successo"
}
```

### Risposta di Errore

Tutte le risposte di errore seguono questo formato:

```json
{
  "success": false,
  "error": {
    "message": "Descrizione dell'errore",
    "type": "TipoErrore",
    "details": {
      // Dettagli opzionali aggiuntivi sull'errore
    }
  }
}
```

## Funzioni di Utility

Il modulo `api.utils.responses` fornisce funzioni helper per generare risposte nel formato standard:

```python
from api.utils.responses import success_response, error_response
```

### Funzione `success_response`

```python
def success_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = 200
) -> JSONResponse:
    """Genera una risposta di successo standardizzata"""
```

### Funzione `error_response`

```python
def error_response(
    message: str,
    error_type: str = "GenericError",
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> JSONResponse:
    """Genera una risposta di errore standardizzata"""
```

## Esempi di Utilizzo

### Risposta di Successo Semplice

```python
@router.get("/api/items")
async def get_items():
    items = [
        {"id": "1", "name": "Item 1"},
        {"id": "2", "name": "Item 2"}
    ]
    
    return success_response(
        data=items,
        message="Items recuperati con successo"
    )
```

Risultato:
```json
{
  "success": true,
  "data": [
    {"id": "1", "name": "Item 1"},
    {"id": "2", "name": "Item 2"}
  ],
  "message": "Items recuperati con successo"
}
```

### Risposta di Successo con Dati Strutturati

```python
@router.get("/api/dashboard")
async def get_dashboard():
    return success_response(
        data={
            "stats": {
                "users": 120,
                "active": 45
            },
            "recent_activity": [
                {"user": "user1", "action": "login"},
                {"user": "user2", "action": "purchase"}
            ]
        },
        message="Dashboard caricata con successo"
    )
```

### Risposta di Errore Semplice

```python
@router.get("/api/items/{item_id}")
async def get_item(item_id: str):
    item = find_item(item_id)
    
    if not item:
        return error_response(
            message=f"Item non trovato: {item_id}",
            error_type="ItemNotFound",
            status_code=404
        )
    
    return success_response(data=item)
```

Risultato (caso di errore):
```json
{
  "success": false,
  "error": {
    "message": "Item non trovato: 123",
    "type": "ItemNotFound"
  }
}
```

### Risposta di Errore con Dettagli

```python
@router.post("/api/validate")
async def validate_data(data: Dict[str, Any]):
    validation_errors = []
    
    if "name" not in data:
        validation_errors.append("Campo 'name' mancante")
    
    if "email" in data and not is_valid_email(data["email"]):
        validation_errors.append("Email non valida")
    
    if validation_errors:
        return error_response(
            message="Errore di validazione",
            error_type="ValidationError",
            details={"errors": validation_errors},
            status_code=400
        )
    
    # Procedi con la logica se non ci sono errori
    return success_response(
        message="Dati validi",
        data={"valid": True}
    )
```

Risultato (caso di errore):
```json
{
  "success": false,
  "error": {
    "message": "Errore di validazione",
    "type": "ValidationError",
    "details": {
      "errors": [
        "Campo 'name' mancante",
        "Email non valida"
      ]
    }
  }
}
```

## Codici di Stato HTTP Comuni

Le funzioni `success_response` e `error_response` accettano un parametro `status_code` per impostare il codice di stato HTTP della risposta:

- **200 OK**: Richiesta completata con successo
- **201 Created**: Risorsa creata con successo
- **400 Bad Request**: Errore client (payload invalido, parametri mancanti)
- **401 Unauthorized**: Autenticazione necessaria
- **403 Forbidden**: Client autenticato ma non autorizzato
- **404 Not Found**: Risorsa non trovata
- **409 Conflict**: Conflitto con lo stato attuale della risorsa
- **422 Unprocessable Entity**: Payload valido ma semanticamente errato
- **429 Too Many Requests**: Rate limiting
- **500 Internal Server Error**: Errore server generico

## Pattern di Utilizzo nei Router

Tutti gli endpoint devono utilizzare queste funzioni per formattare le risposte:

```python
@router.get("/api/resource")
async def get_resource(token: str = token_dependency):
    try:
        # Logica dell'endpoint
        result = {"data": "valore"}
        
        return success_response(
            data=result,
            message="Operazione completata con successo"
        )
    except ResourceNotFoundException as e:
        return error_response(
            message=str(e),
            error_type="ResourceNotFound",
            status_code=404
        )
    except ValidationException as e:
        return error_response(
            message=str(e),
            error_type="ValidationError",
            details=e.details,
            status_code=400
        )
    except Exception as e:
        logger.error(f"Errore imprevisto: {str(e)}")
        return error_response(
            message="Si è verificato un errore interno",
            error_type="InternalError",
            status_code=500
        )
```

## Convenzioni per i Tipi di Errore

Utilizzare tipi di errore significativi che identificano chiaramente il problema:

- `NotFoundError`: Risorsa non trovata
- `ValidationError`: Dati di input non validi
- `AuthenticationError`: Problemi di autenticazione
- `AuthorizationError`: Problemi di autorizzazione
- `RateLimitExceeded`: Limite di richieste superato
- `ExternalServiceError`: Errore in un servizio esterno
- `DatabaseError`: Problema con il database
- `TimeoutError`: Operazione scaduta
