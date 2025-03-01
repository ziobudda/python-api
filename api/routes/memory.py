from fastapi import APIRouter, Depends, Query, HTTPException, Path
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from api.utils.responses import success_response, error_response
from api.utils.auth import token_dependency
from api.utils.memory import MemorySystem, Interaction, InteractionCreate, InteractionResponse, InteractionsListResponse
from config import settings

logger = logging.getLogger(__name__)

# Inizializzazione del sistema memory
memory_system = MemorySystem.get_instance(settings.MEMORY_CONFIG_PATH)
memory_manager = memory_system.memory_manager

# Creazione del router
router = APIRouter(prefix="/api/memory", tags=["Memory"])

@router.post("/interactions", response_model=Dict[str, Any])
async def create_interaction(
    interaction: InteractionCreate,
    token: str = token_dependency
):
    """
    Registra una nuova interazione nel sistema memory.
    
    Args:
        interaction: I dati dell'interazione da registrare
        
    Returns:
        Dict: Risposta con l'ID dell'interazione creata
    """
    try:
        logger.info(f"Registrazione nuova interazione: {interaction.command}")
        
        # Registra l'interazione
        interaction_id = memory_manager.record_interaction(
            agent_id=interaction.agent_id,
            command=interaction.command,
            prompt=interaction.prompt,
            response=interaction.response,
            cost=interaction.cost,
            metadata=interaction.metadata
        )
        
        # Recupera l'interazione per restituirla
        created_interaction = memory_manager.get_interaction(interaction_id)
        
        if not created_interaction:
            return error_response(
                message="Interazione creata ma impossibile recuperarla",
                error_type="MemoryRetrievalError"
            )
        
        # Converti l'interazione in formato di risposta
        response_data = {
            "id": created_interaction.id,
            "timestamp": created_interaction.timestamp.isoformat(),
            "agent_id": created_interaction.agent_id,
            "command": created_interaction.command,
            "prompt": created_interaction.prompt,
            "response": created_interaction.response,
            "cost": created_interaction.cost,
            "metadata": created_interaction.metadata or {}
        }
        
        return success_response(
            data=response_data,
            message=f"Interazione registrata con successo: {interaction_id}"
        )
    except Exception as e:
        logger.error(f"Errore nella registrazione dell'interazione: {str(e)}")
        return error_response(
            message=f"Impossibile registrare l'interazione: {str(e)}",
            error_type="MemoryError"
        )

@router.get("/interactions/{interaction_id}", response_model=Dict[str, Any])
async def get_interaction(
    interaction_id: str = Path(..., description="ID dell'interazione da recuperare"),
    token: str = token_dependency
):
    """
    Recupera una specifica interazione dal sistema memory.
    
    Args:
        interaction_id: ID dell'interazione da recuperare
        
    Returns:
        Dict: Risposta con i dettagli dell'interazione
    """
    try:
        logger.info(f"Richiesta interazione: {interaction_id}")
        
        # Recupera l'interazione
        interaction = memory_manager.get_interaction(interaction_id)
        
        if not interaction:
            return error_response(
                message=f"Interazione non trovata: {interaction_id}",
                error_type="InteractionNotFound",
                status_code=404
            )
        
        # Converti l'interazione in formato di risposta
        response_data = {
            "id": interaction.id,
            "timestamp": interaction.timestamp.isoformat(),
            "agent_id": interaction.agent_id,
            "command": interaction.command,
            "prompt": interaction.prompt,
            "response": interaction.response,
            "cost": interaction.cost,
            "metadata": interaction.metadata or {}
        }
        
        return success_response(
            data=response_data
        )
    except Exception as e:
        logger.error(f"Errore nel recupero dell'interazione {interaction_id}: {str(e)}")
        return error_response(
            message=f"Errore nel recupero dell'interazione: {str(e)}",
            error_type="MemoryRetrievalError"
        )

@router.get("/interactions", response_model=Dict[str, Any])
async def list_interactions(
    agent_id: Optional[str] = Query(None, description="Filtra per ID dell'agent"),
    command: Optional[str] = Query(None, description="Filtra per comando"),
    limit: int = Query(10, description="Numero massimo di risultati", ge=1, le=100),
    token: str = token_dependency
):
    """
    Recupera una lista di interazioni dal sistema memory, con possibilità di filtraggio.
    
    Args:
        agent_id: Filtra per ID dell'agent
        command: Filtra per comando
        limit: Numero massimo di risultati da restituire
        
    Returns:
        Dict: Risposta con la lista delle interazioni
    """
    try:
        logger.info(f"Richiesta lista interazioni (agent_id={agent_id}, command={command}, limit={limit})")
        
        # Recupera le interazioni in base ai filtri
        if agent_id and command:
            interactions = memory_manager.find_by_command_and_agent(command, agent_id, limit)
        elif agent_id:
            interactions = memory_manager.find_recent_interactions(limit, agent_id)
        else:
            interactions = memory_manager.find_recent_interactions(limit)
        
        # Converti le interazioni in formato di risposta
        response_data = []
        for interaction in interactions:
            response_data.append({
                "id": interaction.id,
                "timestamp": interaction.timestamp.isoformat(),
                "agent_id": interaction.agent_id,
                "command": interaction.command,
                "prompt": interaction.prompt,
                "response": interaction.response,
                "cost": interaction.cost,
                "metadata": interaction.metadata or {}
            })
        
        return success_response(
            data={
                "interactions": response_data,
                "count": len(response_data)
            },
            message=f"Recuperate {len(response_data)} interazioni"
        )
    except Exception as e:
        logger.error(f"Errore nel recupero della lista di interazioni: {str(e)}")
        return error_response(
            message=f"Impossibile recuperare le interazioni: {str(e)}",
            error_type="MemoryListError"
        )

@router.get("/interactions/recent", response_model=Dict[str, Any])
async def recent_interactions(
    limit: int = Query(5, description="Numero massimo di risultati", ge=1, le=50),
    agent_id: Optional[str] = Query(None, description="Filtra per ID dell'agent"),
    token: str = token_dependency
):
    """
    Recupera le interazioni più recenti dal sistema memory.
    
    Args:
        limit: Numero massimo di risultati da restituire
        agent_id: Filtra per ID dell'agent
        
    Returns:
        Dict: Risposta con la lista delle interazioni più recenti
    """
    try:
        logger.info(f"Richiesta interazioni recenti (limit={limit}, agent_id={agent_id})")
        
        # Recupera le interazioni recenti
        interactions = memory_manager.find_recent_interactions(limit, agent_id)
        
        # Converti le interazioni in formato di risposta
        response_data = []
        for interaction in interactions:
            response_data.append({
                "id": interaction.id,
                "timestamp": interaction.timestamp.isoformat(),
                "agent_id": interaction.agent_id,
                "command": interaction.command,
                "prompt": interaction.prompt,
                "response": interaction.response,
                "cost": interaction.cost,
                "metadata": interaction.metadata or {}
            })
        
        return success_response(
            data={
                "interactions": response_data,
                "count": len(response_data)
            },
            message=f"Recuperate {len(response_data)} interazioni recenti"
        )
    except Exception as e:
        logger.error(f"Errore nel recupero delle interazioni recenti: {str(e)}")
        return error_response(
            message=f"Impossibile recuperare le interazioni recenti: {str(e)}",
            error_type="MemoryRecentError"
        )

@router.get("/interactions/by-date", response_model=Dict[str, Any])
async def interactions_by_date(
    year: int = Query(..., description="Anno (es. 2024)"),
    month: int = Query(..., description="Mese (1-12)"),
    day: int = Query(..., description="Giorno (1-31)"),
    agent_id: Optional[str] = Query(None, description="Filtra per ID dell'agent"),
    token: str = token_dependency
):
    """
    Recupera le interazioni di una specifica data dal sistema memory.
    
    Args:
        year: Anno della data
        month: Mese della data
        day: Giorno della data
        agent_id: Filtra per ID dell'agent
        
    Returns:
        Dict: Risposta con la lista delle interazioni della data specificata
    """
    try:
        # Valida la data
        try:
            target_date = datetime(year, month, day)
        except ValueError as e:
            return error_response(
                message=f"Data non valida: {str(e)}",
                error_type="InvalidDateError",
                status_code=400
            )
        
        logger.info(f"Richiesta interazioni per data: {target_date.date()}")
        
        # Recupera le interazioni per la data
        interactions = memory_manager.find_interactions_by_date(target_date)
        
        # Filtra per agent_id se specificato
        if agent_id:
            interactions = [i for i in interactions if i.agent_id == agent_id]
        
        # Converti le interazioni in formato di risposta
        response_data = []
        for interaction in interactions:
            response_data.append({
                "id": interaction.id,
                "timestamp": interaction.timestamp.isoformat(),
                "agent_id": interaction.agent_id,
                "command": interaction.command,
                "prompt": interaction.prompt,
                "response": interaction.response,
                "cost": interaction.cost,
                "metadata": interaction.metadata or {}
            })
        
        return success_response(
            data={
                "interactions": response_data,
                "count": len(response_data),
                "date": target_date.date().isoformat()
            },
            message=f"Recuperate {len(response_data)} interazioni per la data {target_date.date()}"
        )
    except Exception as e:
        logger.error(f"Errore nel recupero delle interazioni per data: {str(e)}")
        return error_response(
            message=f"Impossibile recuperare le interazioni per data: {str(e)}",
            error_type="MemoryDateError"
        )

@router.get("/interactions/search", response_model=Dict[str, Any])
async def search_interactions(
    query: str = Query(..., description="Testo da cercare in prompt e risposte"),
    limit: int = Query(10, description="Numero massimo di risultati", ge=1, le=100),
    agent_id: Optional[str] = Query(None, description="Filtra per ID dell'agent"),
    token: str = token_dependency
):
    """
    Cerca nelle interazioni per testo contenuto nei prompt o nelle risposte.
    
    Args:
        query: Testo da cercare
        limit: Numero massimo di risultati da restituire
        agent_id: Filtra per ID dell'agent
        
    Returns:
        Dict: Risposta con la lista delle interazioni che contengono il testo cercato
    """
    try:
        logger.info(f"Ricerca interazioni con query: '{query}'")
        
        # Cerca nelle interazioni
        query_lower = query.lower()
        
        def search_filter(interaction: Interaction) -> bool:
            # Filtra per agent_id se specificato
            if agent_id and interaction.agent_id != agent_id:
                return False
            
            # Cerca nella prompt
            if query_lower in interaction.prompt.lower():
                return True
                
            # Cerca nella risposta
            if query_lower in interaction.response.lower():
                return True
                
            # Cerca nel comando
            if query_lower in interaction.command.lower():
                return True
            
            return False
        
        # Recupera tutte le interazioni e filtra
        all_interactions = memory_manager.storage.find_interactions(
            lambda x: True,  # Prendi tutte le interazioni
            None  # Senza limiti
        )
        
        # Filtra e limita i risultati
        matching_interactions = []
        for interaction in all_interactions:
            if search_filter(interaction):
                matching_interactions.append(interaction)
                if len(matching_interactions) >= limit:
                    break
        
        # Ordina per timestamp decrescente
        matching_interactions.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Converti le interazioni in formato di risposta
        response_data = []
        for interaction in matching_interactions:
            response_data.append({
                "id": interaction.id,
                "timestamp": interaction.timestamp.isoformat(),
                "agent_id": interaction.agent_id,
                "command": interaction.command,
                "prompt": interaction.prompt,
                "response": interaction.response,
                "cost": interaction.cost,
                "metadata": interaction.metadata or {}
            })
        
        return success_response(
            data={
                "interactions": response_data,
                "count": len(response_data),
                "query": query
            },
            message=f"Trovate {len(response_data)} interazioni per la query '{query}'"
        )
    except Exception as e:
        logger.error(f"Errore nella ricerca di interazioni: {str(e)}")
        return error_response(
            message=f"Impossibile completare la ricerca: {str(e)}",
            error_type="MemorySearchError"
        )
