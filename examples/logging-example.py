import sys
import os

# Aggiungi la directory principale al path per poter importare i moduli del progetto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.utils.logging_config import setup_logging, get_logger

def main():
    # Configura il logging all'avvio dell'applicazione
    setup_logging()
    
    # Ottieni un logger per questo modulo
    logger = get_logger(__name__)
    
    # Esempi di utilizzo dei diversi livelli di log
    logger.debug("Questo è un messaggio di DEBUG")
    logger.info("Questo è un messaggio di INFO")
    logger.warning("Questo è un messaggio di WARNING")
    logger.error("Questo è un messaggio di ERROR")
    logger.critical("Questo è un messaggio di CRITICAL")
    
    # Esempio di logging con dati contestuali
    user_id = "user123"
    action = "login"
    logger.info(f"Utente {user_id} ha eseguito l'azione: {action}")
    
    # Esempio di logging di eccezioni
    try:
        # Simuliamo un errore
        result = 1 / 0
    except Exception as e:
        logger.exception(f"Si è verificato un errore durante l'elaborazione: {str(e)}")

if __name__ == "__main__":
    main()
