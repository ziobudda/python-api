import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Configurazione ambiente
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"

# Configurazione server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Configurazione autenticazione API
API_TOKEN = os.getenv("API_TOKEN", "default_insecure_token")

# Configurazione per browser e ricerche
BROWSER_STEALTH_MODE = os.getenv("BROWSER_STEALTH_MODE", "True").lower() in ["true", "1", "yes"]
USE_PROXIES = os.getenv("USE_PROXIES", "False").lower() in ["true", "1", "yes"]
SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "90"))  # Aumentato per supportare paginazione
SEARCH_RATE_LIMIT = int(os.getenv("SEARCH_RATE_LIMIT", "10"))  # Ricerche per minuto
SEARCH_COOLDOWN = int(os.getenv("SEARCH_COOLDOWN", "60"))  # Secondi di cooldown tra ricerche eccessive

# Google Search specifiche
GOOGLE_DEFAULT_LANG = os.getenv("GOOGLE_DEFAULT_LANG", "it")
GOOGLE_MAX_RESULTS = int(os.getenv("GOOGLE_MAX_RESULTS", "20"))  # Massimo per pagina
GOOGLE_MAX_PAGES = int(os.getenv("GOOGLE_MAX_PAGES", "10"))  # Massimo numero di pagine
GOOGLE_SLEEP_INTERVAL = float(os.getenv("GOOGLE_SLEEP_INTERVAL", "2.0"))

# Configurazioni per Crawl4AI
CRAWL4AI_TIMEOUT = int(os.getenv("CRAWL4AI_TIMEOUT", "60"))  # Timeout in secondi
CRAWL4AI_CACHE_MODE = os.getenv("CRAWL4AI_CACHE_MODE", "BYPASS")  # ENABLED, BYPASS, DISABLED
CRAWL4AI_RATE_LIMIT = int(os.getenv("CRAWL4AI_RATE_LIMIT", "10"))  # Richieste per minuto
CRAWL4AI_COOLDOWN = int(os.getenv("CRAWL4AI_COOLDOWN", "60"))  # Secondi di cooldown

# Configurazioni Memory
MEMORY_CONFIG_PATH = os.getenv("MEMORY_CONFIG_PATH", "config/memory.yaml")
MEMORY_ACTIVE_STORAGE = os.getenv("MEMORY_ACTIVE_STORAGE", "default")
