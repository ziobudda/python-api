#!/usr/bin/env python
"""
Script per testare il sistema di configurazione dei log.
Esegui questo script per verificare che il logging funzioni correttamente.
"""

import os
import sys
from api.utils.logging_config import setup_logging, get_logger

def main():
    # Configura il logging
    setup_logging()
    
    # Crea un logger per questo modulo
    logger = get_logger(__name__)
    
    # Ottieni informazioni sulla configurazione corrente
    log_to_file = os.getenv("LOG_TO_FILE", "False").lower() in ["true", "1", "yes"]
    log_level = os.getenv("LOG_LEVEL", "info").upper()
    log_file_path = os.getenv("LOG_FILE_PATH", "logs/app.log")
    
    print(f"Configurazione di test del logging:")
    print(f"- LOG_TO_FILE: {log_to_file}")
    print(f"- LOG_LEVEL: {log_level}")
    print(f"- LOG_FILE_PATH: {log_file_path}")
    print("-" * 50)
    
    # Test di tutti i livelli di log
    logger.debug("Questo è un messaggio di debug")
    logger.info("Questo è un messaggio informativo")
    logger.warning("Questo è un messaggio di avviso")
    logger.error("Questo è un messaggio di errore")
    logger.critical("Questo è un messaggio critico")
    
    # Test di log con eccezione
    try:
        x = 1 / 0
    except Exception as e:
        logger.exception(f"Errore di esempio: {str(e)}")
    
    # Messaggio finale
    if log_to_file:
        print(f"\nI log sono stati scritti nel file: {log_file_path}")
        print(f"Controlla il file per verificare che i messaggi siano stati registrati correttamente.")
    else:
        print("\nI log sono stati inviati alla console.")
        print("Dovresti vedere i messaggi di log sopra.")

if __name__ == "__main__":
    main()
