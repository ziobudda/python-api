# api/utils/memory/storage/factory.py
from typing import Dict
from .file_memory import FileMemory
from ..interfaces import MemoryStorageInterface


class MemoryStorageFactory:
    """Factory per creare istanze di storage della memoria"""

    @staticmethod
    def create_storage(config: Dict) -> MemoryStorageInterface:
        """
        Crea una nuova istanza di storage basata sulla configurazione

        Args:
            config: Dizionario di configurazione che specifica tipo e parametri dello storage

        Returns:
            MemoryStorageInterface: Istanza dello storage configurato

        Raises:
            ValueError: Se il tipo di storage non è supportato
        """
        storage_type = config.get('type')

        if storage_type == 'file':
            return FileMemory(
                file_path=config['path']
            )

        raise ValueError(f"Tipo di storage non supportato: {storage_type}")