# api/utils/memory/interfaces.py
from typing import List, Optional, Callable
from .models import Interaction


class MemoryStorageInterface:
    """Interfaccia base per i sistemi di storage della memoria"""

    def save_interaction(self, interaction: Interaction) -> None:
        """
        Salva una nuova interazione

        Args:
            interaction: L'interazione da salvare
        """
        raise NotImplementedError

    def get_interaction(self, interaction_id: str) -> Optional[Interaction]:
        """
        Recupera una specifica interazione per ID

        Args:
            interaction_id: ID dell'interazione

        Returns:
            Optional[Interaction]: L'interazione se trovata, None altrimenti
        """
        raise NotImplementedError

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
        raise NotImplementedError