from typing import Any, Dict, Optional, Union, List

def success_response(
    data: Union[Dict[str, Any], List[Any], Any], 
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crea una risposta di successo standardizzata in formato JSON.
    
    Args:
        data: I dati da includere nella risposta
        message: Un messaggio opzionale
        meta: Metadati opzionali
        
    Returns:
        Dict: Risposta di successo formattata
    """
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
        
    if meta:
        response["meta"] = meta
        
    return response

def error_response(
    message: str,
    error_type: Optional[str] = None,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crea una risposta di errore standardizzata in formato JSON.
    
    Args:
        message: Messaggio di errore
        error_type: Tipo di errore
        code: Codice di errore opzionale
        details: Dettagli aggiuntivi sull'errore
        
    Returns:
        Dict: Risposta di errore formattata
    """
    error = {
        "message": message
    }
    
    if error_type:
        error["type"] = error_type
        
    if code:
        error["code"] = code
        
    if details:
        error["details"] = details
        
    return {
        "success": False,
        "error": error
    }
