import logging
import random
from typing import Optional, Dict, List, Union

logger = logging.getLogger(__name__)

class ProxyManager:
    """
    Gestisce un pool di proxy per distribuire le richieste e evitare blocchi.
    """
    def __init__(self, proxy_list: List[Dict[str, str]] = None):
        """
        Inizializza il gestore proxy con una lista di proxy.
        
        Args:
            proxy_list: Lista di proxy nel formato [{"server": "http://proxy.example.com:8080", "username": "user", "password": "pass"}]
                        Se None, non verrà utilizzato alcun proxy.
        """
        self.proxy_list = proxy_list or []
        self.current_index = 0
        logger.info(f"ProxyManager inizializzato con {len(self.proxy_list)} proxy")
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """
        Restituisce il prossimo proxy dalla lista in modalità round-robin.
        
        Returns:
            Dict con le info del proxy o None se non ci sono proxy configurati
        """
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        logger.debug(f"Utilizzando proxy: {proxy['server']}")
        return proxy
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """
        Restituisce un proxy casuale dalla lista.
        
        Returns:
            Dict con le info del proxy o None se non ci sono proxy configurati
        """
        if not self.proxy_list:
            return None
        
        proxy = random.choice(self.proxy_list)
        logger.debug(f"Utilizzando proxy casuale: {proxy['server']}")
        return proxy
    
    def format_proxy_for_playwright(self, proxy: Dict[str, str]) -> Dict[str, Union[str, Dict[str, str]]]:
        """
        Formatta le informazioni del proxy nel formato richiesto da Playwright.
        
        Args:
            proxy: Dizionario con le informazioni del proxy
            
        Returns:
            Dizionario formattato per Playwright
        """
        playwright_proxy = {
            "server": proxy["server"]
        }
        
        if "username" in proxy and "password" in proxy:
            playwright_proxy["username"] = proxy["username"]
            playwright_proxy["password"] = proxy["password"]
        
        return playwright_proxy

# Lista di proxy di esempio (da sostituire con quelli reali)
# Questi sono solo esempi e non funzioneranno
SAMPLE_PROXIES = [
    # Formato: {"server": "http://host:port", "username": "user", "password": "pass"}
    # Lasciare vuota per non utilizzare proxy
]

# Istanza singleton del ProxyManager
proxy_manager = ProxyManager(SAMPLE_PROXIES)
