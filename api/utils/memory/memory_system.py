# api/utils/memory/memory_system.py
import datetime
import logging
from typing import Dict, Optional, List
import os
import yaml
from threading import Lock

from .models import Interaction
from .interfaces import MemoryStorageInterface
from .storage import MemoryStorageFactory
from .manager import MemoryManager


class MemorySystem:
    _instance: Optional['MemorySystem'] = None
    _initialized: bool = False
    _storage_managers: Dict[str, MemoryManager] = {}
    _locks: Dict[str, Lock] = {}

    def __new__(cls, config_path: str = "config/memory.yaml") -> 'MemorySystem':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = "config/memory.yaml") -> None:
        # Evita reinizializzazione se già inizializzato
        if MemorySystem._initialized:
            return

        self.logger = logging.getLogger(__name__)

        # Carica configurazione
        self.config = self._load_config(config_path)

        # Setup del sistema
        self._setup_system()

        # Inizializza storage predefinito
        storage_config = self.config["memory"]["storages"][
            self.config["memory"]["active_storage"]
        ]
        self.storage = MemoryStorageFactory.create_storage(storage_config)

        # Crea memory manager predefinito
        self.manager = MemoryManager(self.storage)
        
        # Inizializza dizionario per storage aggiuntivi
        self._storage_managers = {}
        self._locks = {}

        MemorySystem._initialized = True
        self.logger.info("Sistema Memory inizializzato con successo")

    def _load_config(self, config_path: str) -> Dict:
        """Carica la configurazione da file YAML"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Errore nel caricare la configurazione memory: {str(e)}")
            # Configurazione di fallback
            return {
                "memory": {
                    "active_storage": "default",
                    "storages": {
                        "default": {
                            "type": "file",
                            "path": "data/memory/interactions.json"
                        }
                    }
                }
            }

    def _setup_system(self) -> None:
        """Setup iniziale del sistema di memoria"""
        try:
            for storage_name, storage_config in self.config["memory"]["storages"].items():
                if storage_config["type"] == "file":
                    # Crea directory per il file
                    os.makedirs(os.path.dirname(storage_config["path"]), exist_ok=True)

                    # Se i backup sono abilitati, crea directory backup
                    if storage_config.get("backup", {}).get("enabled", False):
                        os.makedirs(storage_config["backup"]["backup_dir"], exist_ok=True)
        except Exception as e:
            self.logger.error(f"Errore nel setup del sistema memory: {str(e)}")

    @property
    def memory_manager(self) -> MemoryManager:
        """Restituisce l'istanza del memory manager predefinito"""
        return self.manager

    def get_memory_manager(self, storage_name: str = None) -> MemoryManager:
        """
        Restituisce un memory manager specifico o quello predefinito.
        
        Args:
            storage_name: Nome dello storage da utilizzare. Se None, restituisce il manager predefinito.
        
        Returns:
            MemoryManager: Il manager richiesto
        
        Raises:
            KeyError: Se lo storage richiesto non esiste nella configurazione
        """
        if storage_name is None:
            return self.manager

        if storage_name not in self._storage_managers:
            # Verifica che lo storage esista in configurazione
            if storage_name not in self.config["memory"]["storages"]:
                raise KeyError(f"Storage '{storage_name}' non trovato nella configurazione")

            # Crea nuovo storage e manager
            storage_config = self.config["memory"]["storages"][storage_name]
            storage = MemoryStorageFactory.create_storage(storage_config)
            
            # Crea lock per questo storage
            self._locks[storage_name] = Lock()
            
            # Crea e memorizza il nuovo manager
            self._storage_managers[storage_name] = MemoryManager(storage)

        return self._storage_managers[storage_name]

    @classmethod
    def get_instance(cls, config_path: str = "config/memory.yaml") -> 'MemorySystem':
        """Metodo per ottenere l'istanza singleton"""
        if cls._instance is None:
            cls._instance = MemorySystem(config_path)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Resetta il singleton - utile principalmente per testing"""
        cls._instance = None
        cls._initialized = False

    def get_interaction(self, interaction_id: str) -> Optional[Interaction]:
        """
        Recupera una specifica interazione

        Args:
            interaction_id (str): ID dell'interazione

        Returns:
            Optional[Interaction]: L'interazione se trovata, None altrimenti
        """
        return self.storage.get_interaction(interaction_id)

    def find_interactions_by_date(self, target_date: datetime) -> List[Interaction]:
        """
        Cerca le interazioni per una data specifica

        Args:
            target_date (datetime): Data per cui cercare le interazioni

        Returns:
            List[Interaction]: Lista delle interazioni trovate, ordinate per timestamp
        """
        interactions = self.storage.find_interactions(
            lambda x: self.is_same_date(x.timestamp, target_date),
            None  # No limit
        )

        return sorted(
            interactions,
            key=lambda x: x.timestamp
        )

    @staticmethod
    def is_same_date(interaction_date: datetime, target: datetime) -> bool:
        return (
            interaction_date.year == target.year and
            interaction_date.month == target.month and
            interaction_date.day == target.day
        )