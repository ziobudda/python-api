# Sistema di Autenticazione API

Questo documento descrive il sistema di autenticazione utilizzato nelle API del progetto, basato su token API.

## Panoramica

Il sistema utilizza un meccanismo di autenticazione semplice basato su token API. Ogni richiesta alle API deve includere un token valido per essere autorizzata.

## Implementazione

L'autenticazione è gestita dal modulo `api.utils.auth` che fornisce la dipendenza FastAPI `token_dependency` da utilizzare in tutti gli endpoint.

### File `api/utils/auth.py`

```python
from fastapi import Header, HTTPException, Depends
from config import settings
import logging

logger = logging.getLogger(__name__)

async def verify_token(x_api_token: str = Header(..., description="API Token di autenticazione")) -> str:
    """
    Verifica il token API per l'autenticazione.
    
    Args:
        x_api_token: Token API fornito nell'header della richiesta
        
    Returns:
        str: Il token se valido
        
    Raises:
        HTTPException: Se il token non è valido o mancante
    """
    if not x_api_token:
        logger.warning("Tentativo di accesso senza token")
        raise HTTPException(
            status_code=401,
            detail="API Token mancante"
        )
    
    if x_api_token != settings.API_TOKEN:
        logger.warning(f"Tentativo di accesso con token non valido: {x_api_token}")
        raise HTTPException(
            status_code=401,
            detail="API Token non valido"
        )
    
    return x_api_token

# Dipendenza per l'autenticazione da utilizzare negli endpoint
token_dependency = Depends(verify_token)
```

## Configurazione

Il token API valido è configurato in `config/settings.py` e viene caricato dalla variabile d'ambiente `API_TOKEN`:

```python
# Configurazione autenticazione API
API_TOKEN = os.getenv("API_TOKEN", "default_insecure_token")
```

Per sicurezza, in produzione è necessario impostare un token complesso e sicuro nel file `.env`.

## Utilizzo negli Endpoint

Ogni endpoint che richiede autenticazione deve includere la dipendenza `token_dependency`:

```python
from api.utils.auth import token_dependency

@router.get("/api/protected-resource")
async def get_protected_resource(token: str = token_dependency):
    # Logica dell'endpoint
    return {"message": "Accesso autorizzato"}
```

## Inclusione del Token nelle Richieste

I client che effettuano richieste alle API devono includere il token nell'header HTTP `X-API-Token`:

```
X-API-Token: your-api-token-here
```

### Esempio con cURL

```bash
curl -X GET "http://localhost:8000/api/protected-resource" \
     -H "X-API-Token: your-api-token-here"
```

### Esempio con Python Requests

```python
import requests

API_URL = "http://localhost:8000/api/protected-resource"
API_TOKEN = "your-api-token-here"

headers = {
    "X-API-Token": API_TOKEN
}

response = requests.get(API_URL, headers=headers)
```

## Risposte di Errore per Autenticazione

Se l'autenticazione fallisce, l'API restituirà una risposta di errore con status code 401:

```json
{
  "detail": "API Token non valido"
}
```

o

```json
{
  "detail": "API Token mancante"
}
```

## Best Practices per la Sicurezza

1. **Token Complessi**: Usa token lunghi e complessi in produzione
2. **Rotazione dei Token**: Cambia periodicamente i token per migliorare la sicurezza
3. **HTTPS**: Utilizza sempre HTTPS in produzione per proteggere il token durante la trasmissione
4. **Variabili d'Ambiente**: Non inserire mai i token direttamente nel codice
5. **Monitoraggio**: Monitora e registra tentativi di accesso non autorizzati

## Estensioni Future del Sistema di Autenticazione

Il sistema attuale è semplice ma funzionale per API interne. Possibili estensioni future includono:

1. **Autenticazione basata su JWT**: Per supportare informazioni di utente e scadenza
2. **Supporto per più token/client**: Per gestire diversi client con autorizzazioni diverse
3. **Rate limiting per token**: Per limitare il numero di richieste per client
4. **Registrazione automatica degli utilizzi**: Per tracciare l'utilizzo dell'API per client
