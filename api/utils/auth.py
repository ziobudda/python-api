from fastapi import HTTPException, Header, Depends
from typing import Optional
from config import settings
from .responses import error_response

async def verify_token(x_api_token: Optional[str] = Header(None)):
    """
    Verifica il token API nell'header della richiesta.
    
    Args:
        x_api_token: Token API fornito nell'header della richiesta
        
    Returns:
        str: Il token validato
        
    Raises:
        HTTPException: Se il token manca o non è valido
    """
    # Se manca il token nell'header
    if x_api_token is None:
        raise HTTPException(
            status_code=401,
            detail=error_response(
                message="Token di autenticazione mancante nell'header",
                error_type="AuthenticationError",
                code="missing_token"
            )
        )
    
    # Se il token non è valido
    if x_api_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail=error_response(
                message="Token di autenticazione non valido",
                error_type="AuthenticationError",
                code="invalid_token"
            )
        )
    
    return x_api_token

# Dipendenza per la verifica del token
token_dependency = Depends(verify_token)
