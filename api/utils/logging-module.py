import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import settings

def setup_logging():
    """
    Configura il sistema di logging in base alle impostazioni nel file .env.
    
    Legge le seguenti variabili d'ambiente:
    - LOG_LEVEL: Livello di log (debug, info, warning, error, critical)
    - LOG_TO_FILE: Se True, scrive i log su file invece che su console
    - LOG_FILE_PATH: Percorso del file di log (default: logs/app.log)
    - LOG_FILE_MAX_SIZE: Dimensione massima del file di log in bytes (default: 10MB)
    - LOG_FILE_BACKUP_COUNT: Numero di file di backup da mantenere (default: 3)
    
    Returns:
        logging.Logger: Logger root configurato
    """
    # Ottieni le configurazioni dal file .env
    log_level_str = os.getenv("LOG_LEVEL", "info").upper()
    log_to_file = os.getenv("LOG_TO_FILE", "False").lower() in ["true", "1", "yes"]
    log_file_path = os.getenv("LOG_FILE_PATH", "logs/app.log")
    log_file_max_size = int(os.getenv("LOG_FILE_MAX_SIZE", 10 * 1024 * 1024))  # 10MB default
    log_file_backup_count = int(os.getenv("LOG_FILE_BACKUP_COUNT", 3))
    
    # Converti la stringa del livello nel valore numerico corrispondente
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Crea un formatter comune
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configura il logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Rimuovi handler esistenti per evitare duplicati
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    if log_to_file:
        # Assicurati che la directory dei log esista
        log_dir = os.path.dirname(log_file_path)
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Crea un file handler con rotazione
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=log_file_max_size,
            backupCount=log_file_backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)
        
        print(f"Logging configurato per scrivere su file: {log_file_path}")
    else:
        # Crea un console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)
        
        print(f"Logging configurato per scrivere su console")
    
    # Crea un logger per questo modulo
    logger = logging.getLogger(__name__)
    logger.info(f"Logging inizializzato con livello: {log_level_str}")
    
    return root_logger

def get_logger(name):
    """
    Ottiene un logger configurato per il modulo specificato.
    
    Args:
        name (str): Nome del modulo (normalmente __name__)
        
    Returns:
        logging.Logger: Logger configurato
    """
    return logging.getLogger(name)
