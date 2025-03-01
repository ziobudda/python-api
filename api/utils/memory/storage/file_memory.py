# api/utils/memory/storage/file_memory.py
import json
import os
import logging
from typing import List, Callable, Optional
from datetime import datetime
import shutil
from datetime import datetime

from ..models import Interaction
from ..interfaces import MemoryStorageInterface


class FileMemory(MemoryStorageInterface):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Assicura che il file di storage esista"""
        if not os.path.exists(self.file_path):
            try:
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                self._save_interactions([])
                self.logger.info(f"Creato nuovo file di storage in {self.file_path}")
            except Exception as e:
                self.logger.error(f"Errore nel creare il file di storage: {str(e)}")

    def _load_interactions(self) -> List[Interaction]:
        """Carica tutte le interazioni dal file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Interaction.from_dict(item) for item in data]
        except json.JSONDecodeError:
            self.logger.warning(f"Errore di decodifica JSON dal file {self.file_path}. Restituisco lista vuota.")
            return []
        except Exception as e:
            self.logger.error(f"Errore nel caricamento delle interazioni: {str(e)}")
            return []

    def _save_interactions(self, interactions: List[Interaction]) -> None:
        """Salva tutte le interazioni nel file"""
        try:
            # Crea backup se il file esiste già
            if os.path.exists(self.file_path):
                backup_dir = os.path.join(os.path.dirname(self.file_path), "backups")
                os.makedirs(backup_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.basename(self.file_path)
                backup_path = os.path.join(backup_dir, f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}")
                shutil.copy2(self.file_path, backup_path)
                
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(
                    [interaction.to_dict() for interaction in interactions],
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            self.logger.error(f"Errore nel salvare le interazioni: {str(e)}")

    def save_interaction(self, interaction: Interaction) -> None:
        """
        Salva una nuova interazione

        Args:
            interaction: L'interazione da salvare
        """
        interactions = self._load_interactions()
        interactions.append(interaction)
        self._save_interactions(interactions)

    def get_interaction(self, interaction_id: str) -> Optional[Interaction]:
        """
        Recupera una specifica interazione per ID

        Args:
            interaction_id: ID dell'interazione

        Returns:
            Optional[Interaction]: L'interazione se trovata, None altrimenti
        """
        interactions = self._load_interactions()
        for interaction in interactions:
            if interaction.id == interaction_id:
                return interaction
        return None

    def find_interactions(
            self,
            predicate: Callable[[Interaction], bool],
            limit: Optional[int] = None
    ) -> List[Interaction]:
        """
        Cerca interazioni che soddisfano un predicato

        Args:
            predicate: Funzione che definisce il criterio di ricerca
            limit: Numero massimo di risultati (None per nessun limite)

        Returns:
            List[Interaction]: Lista delle interazioni che soddisfano il predicato
        """
        interactions = self._load_interactions()
        filtered = [i for i in interactions if predicate(i)]

        if limit is not None:
            return filtered[:limit]
        return filtered