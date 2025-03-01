from fastapi import FastAPI, Request, Depends
from api.utils.auth import token_dependency
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from config import settings
from api.utils.logging_config import setup_logging, get_logger

# Configura il sistema di logging
setup_logging()

# Ottieni un logger per questo modulo
logger = get_logger(__name__)

# Importazione dei router
# Le API items sono state rimosse
from api.routes.browser import router as browser_router
from api.routes.search import router as search_router
from api.routes.crawl import router as crawl_router
from api.routes.memory import router as memory_router

# Inizializzazione dell'applicazione FastAPI
app = FastAPI(
    title="Python REST API",
    description="Sistema Python che risponde a chiamate esterne in modalità REST con risposte in formato JSON",
    version="0.1.0"
)

# Configurazione CORS per consentire richieste cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, specificare i domini consentiti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrazione dei router
# Router items rimosso
app.include_router(browser_router)
app.include_router(search_router)
app.include_router(crawl_router)
app.include_router(memory_router)

# Endpoint di base per verificare che l'API funzioni
@app.get("/", tags=["Health"])
async def root():
    """
    Endpoint di base per verificare lo stato dell'API.
    
    Returns:
        dict: Un semplice messaggio di stato
    """
    logger.info("Endpoint root chiamato")
    return {"status": "online", "message": "Il servizio API è attivo"}

# Gli endpoints di esempio sono stati rimossi

# Gestione errori personalizzata
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Gestore globale delle eccezioni che formatta tutte le risposte di errore
    in un formato JSON coerente.
    
    Args:
        request: L'oggetto richiesta
        exc: L'eccezione sollevata
        
    Returns:
        JSONResponse: Risposta di errore formattata
    """
    logger.error(f"Eccezione non gestita: {type(exc).__name__}: {str(exc)}")
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

# Middleware per il logging delle richieste HTTP
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    logger.info(f"Richiesta ricevuta: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Risposta inviata: {response.status_code}")
    return response

# Avvio dell'applicazione se eseguita direttamente
if __name__ == "__main__":
    logger.info(f"Avvio dell'applicazione su {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="warning",  # Utilizziamo un livello basso per uvicorn e usiamo il nostro sistema di logging
        access_log=False      # Disabilitiamo il log di accesso di uvicorn poiché usiamo il nostro middleware
    )
