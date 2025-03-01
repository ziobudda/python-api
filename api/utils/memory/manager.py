# api/utils/memory/manager.py
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import Interaction
from .interfaces import MemoryStorageInterface


class MemoryManager:
    def __init__(self, storage: MemoryStorageInterface):
        self.storage = storage
        self._skip_next_save = False
        self.logger = logging.getLogger(__name__)

    def skip_next_save(self) -> None:
        """Imposta il flag per saltare la prossima operazione di salvataggio."""
        self._skip_next_save = True

    def record_interaction(
            self,
            agent_id: str,
            command: str,
            prompt: str,
            response: str,
            cost: Optional[float] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registra una nuova interazione includendo l'agent_id e opzionalmente il costo

        Args:
            agent_id (str): Identificatore dell'agent che ha generato l'interazione
            command (str): Comando originale
            prompt (str): Prompt generato
            response (str): Risposta ricevuta
            cost (Optional[float]): Costo dell'operazione se applicabile
            metadata (Optional[Dict[str, Any]]): Metadati aggiuntivi

        Returns:
            str: ID dell'interazione salvata
        """
        interaction = Interaction(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            agent_id=agent_id,
            command=command,
            prompt=prompt,
            response=response,
            cost=cost,
            metadata=metadata
        )

        if not self._skip_next_save:
            try:
                self.storage.save_interaction(interaction)
                self.logger.info(f"Interazione salvata: {interaction.id}")
            except Exception as e:
                self.logger.error(f"Errore nel salvare l'interazione: {str(e)}")

        # Reset del flag dopo l'uso
        self._skip_next_save = False

        return interaction.id

    def find_by_command_and_agent(
            self,
            command: str,
            agent_id: str,
            limit: int = 5
    ) -> List[Interaction]:
        """
        Cerca le interazioni per comando e agent_id specifico

        Args:
            command (str): Comando da cercare
            agent_id (str): ID dell'agent
            limit (int): Numero massimo di risultati

        Returns:
            List[Interaction]: Lista delle interazioni trovate
        """
        try:
            interactions = self.storage.find_interactions(
                lambda x: x.command.lower() == command.lower() and
                        x.agent_id == agent_id,
                limit
            )
            return sorted(
                interactions,
                key=lambda x: x.timestamp,
                reverse=True
            )
        except Exception as e:
            self.logger.error(f"Errore nella ricerca delle interazioni: {str(e)}")
            return []

    def find_recent_interactions(
            self,
            limit: int = 5,
            agent_id: Optional[str] = None
    ) -> List[Interaction]:
        """
        Recupera le interazioni più recenti, opzionalmente filtrate per agent_id.

        Args:
            limit (int): Numero massimo di interazioni da recuperare
            agent_id (Optional[str]): Se specificato, filtra per questo agent_id

        Returns:
            List[Interaction]: Lista delle interazioni più recenti
        """
        try:
            if agent_id:
                filter_func = lambda x: x.agent_id == agent_id
            else:
                filter_func = lambda x: True

            interactions = self.storage.find_interactions(filter_func, None)  # None per non limitare inizialmente

            # Ordina per timestamp decrescente e prendi i primi 'limit' risultati
            return sorted(
                interactions,
                key=lambda x: x.timestamp,
                reverse=True
            )[:limit]
        except Exception as e:
            self.logger.error(f"Errore nel recuperare le interazioni recenti: {str(e)}")
            return []

    def get_interaction(self, interaction_id: str) -> Optional[Interaction]:
        """
        Recupera una specifica interazione

        Args:
            interaction_id (str): ID dell'interazione

        Returns:
            Optional[Interaction]: L'interazione se trovata, None altrimenti
        """
        try:
            return self.storage.get_interaction(interaction_id)
        except Exception as e:
            self.logger.error(f"Errore nel recuperare l'interazione {interaction_id}: {str(e)}")
            return None

    def find_interactions_by_date(self, target_date: datetime) -> List[Interaction]:
        """
        Cerca le interazioni per una data specifica

        Args:
            target_date (datetime): Data per cui cercare le interazioni

        Returns:
            List[Interaction]: Lista delle interazioni trovate, ordinate per timestamp
        """
        try:
            def is_same_date(interaction_date: datetime, target: datetime) -> bool:
                return (
                    interaction_date.year == target.year and
                    interaction_date.month == target.month and
                    interaction_date.day == target.day
                )

            interactions = self.storage.find_interactions(
                lambda x: is_same_date(x.timestamp, target_date),
                None  # No limit
            )

            return sorted(
                interactions,
                key=lambda x: x.timestamp
            )
        except Exception as e:
            self.logger.error(f"Errore nel cercare interazioni per data: {str(e)}")
            return []