import pytest
from fastapi.testclient import TestClient
from app import app
from datetime import datetime, timedelta
import uuid

client = TestClient(app)

# Token di autenticazione per i test
AUTH_TOKEN = "default_insecure_token"  # Valore predefinito in development

# Headers per le richieste autenticate
AUTH_HEADERS = {"X-API-Token": AUTH_TOKEN}

# Funzione di utility per generare una nuova interazione per i test
def create_test_interaction(agent_id="test_agent", command="test_command"):
    """
    Crea una nuova interazione di test e restituisce la risposta e l'ID dell'interazione creata
    """
    unique_id = str(uuid.uuid4())[:8]
    interaction_data = {
        "agent_id": f"{agent_id}_{unique_id}",
        "command": f"{command}_{unique_id}",
        "prompt": f"Test prompt {unique_id}",
        "response": f"Test response {unique_id}",
        "cost": 0.01,
        "metadata": {
            "test_key": "test_value",
            "run_id": unique_id
        }
    }
    
    response = client.post(
        "/api/memory/interactions",
        json=interaction_data,
        headers=AUTH_HEADERS
    )
    
    if response.status_code != 200:
        pytest.fail(f"Errore nella creazione dell'interazione di test: {response.json()}")
    
    return response, response.json()["data"]["id"]

def test_create_interaction():
    """
    Test per verificare che la route POST /api/memory/interactions funzioni correttamente.
    """
    # Crea una nuova interazione
    unique_id = str(uuid.uuid4())[:8]
    interaction_data = {
        "agent_id": f"test_agent_{unique_id}",
        "command": "test_command",
        "prompt": "Test prompt",
        "response": "Test response",
        "cost": 0.01,
        "metadata": {
            "test_key": "test_value",
            "run_id": unique_id
        }
    }
    
    response = client.post(
        "/api/memory/interactions",
        json=interaction_data,
        headers=AUTH_HEADERS
    )
    
    # Verifica la risposta
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["agent_id"] == interaction_data["agent_id"]
    assert data["data"]["command"] == interaction_data["command"]
    assert data["data"]["prompt"] == interaction_data["prompt"]
    assert data["data"]["response"] == interaction_data["response"]
    assert data["data"]["cost"] == interaction_data["cost"]
    assert data["data"]["metadata"]["test_key"] == interaction_data["metadata"]["test_key"]
    assert "id" in data["data"]
    assert "timestamp" in data["data"]

def test_get_interaction():
    """
    Test per verificare che la route GET /api/memory/interactions/{interaction_id} funzioni correttamente.
    """
    # Prima crea una nuova interazione
    create_response, interaction_id = create_test_interaction()
    
    # Ora ottieni l'interazione per ID
    response = client.get(
        f"/api/memory/interactions/{interaction_id}",
        headers=AUTH_HEADERS
    )
    
    # Verifica la risposta
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == interaction_id
    assert "timestamp" in data["data"]
    assert "agent_id" in data["data"]
    assert "command" in data["data"]
    assert "prompt" in data["data"]
    assert "response" in data["data"]
    assert "cost" in data["data"]
    assert "metadata" in data["data"]
    assert isinstance(data["data"]["metadata"], dict)

def test_get_nonexistent_interaction():
    """
    Test per verificare che la route GET /api/memory/interactions/{interaction_id} 
    restituisca 404 per interazioni non esistenti.
    """
    nonexistent_id = "non_existent_id_12345"
    
    response = client.get(
        f"/api/memory/interactions/{nonexistent_id}",
        headers=AUTH_HEADERS
    )
    
    # Verifica che la risposta sia 404
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["type"] == "InteractionNotFound"

def test_list_interactions():
    """
    Test per verificare che la route GET /api/memory/interactions funzioni correttamente.
    """
    # Crea alcune interazioni per assicurarsi che ci siano dati da recuperare
    create_test_interaction()
    create_test_interaction()
    
    # Ottieni la lista delle interazioni
    response = client.get(
        "/api/memory/interactions",
        headers=AUTH_HEADERS
    )
    
    # Verifica la risposta
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "interactions" in data["data"]
    assert "count" in data["data"]
    assert isinstance(data["data"]["interactions"], list)
    assert data["data"]["count"] > 0
    
    # Verifica la struttura di un'interazione della lista
    interaction = data["data"]["interactions"][0]
    assert "id" in interaction
    assert "timestamp" in interaction
    assert "agent_id" in interaction
    assert "command" in interaction
    assert "prompt" in interaction
    assert "response" in interaction
    assert "cost" in interaction
    assert "metadata" in interaction

def test_list_interactions_with_filter():
    """
    Test per verificare che la route GET /api/memory/interactions 
    funzioni correttamente con i filtri.
    """
    # Crea un'interazione specifica per il test con filtro
    unique_agent = f"filter_agent_{str(uuid.uuid4())[:8]}"
    unique_command = f"filter_command_{str(uuid.uuid4())[:8]}"
    create_response, interaction_id = create_test_interaction(agent_id=unique_agent, command=unique_command)
    
    # Test filtro per agent_id
    response_agent = client.get(
        f"/api/memory/interactions?agent_id={unique_agent}",
        headers=AUTH_HEADERS
    )
    
    # Verifica filtro per agent_id
    assert response_agent.status_code == 200
    data_agent = response_agent.json()
    assert data_agent["success"] is True
    assert len(data_agent["data"]["interactions"]) > 0
    assert all(i["agent_id"] == unique_agent for i in data_agent["data"]["interactions"])
    
    # Test filtro per command e agent_id
    response_command = client.get(
        f"/api/memory/interactions?agent_id={unique_agent}&command={unique_command}",
        headers=AUTH_HEADERS
    )
    
    # Verifica filtro per command e agent_id
    assert response_command.status_code == 200
    data_command = response_command.json()
    assert data_command["success"] is True
    assert len(data_command["data"]["interactions"]) > 0
    assert all(i["agent_id"] == unique_agent and i["command"] == unique_command 
               for i in data_command["data"]["interactions"])

def test_recent_interactions():
    """
    Test per verificare che la route GET /api/memory/interactions/recent funzioni correttamente.
    """
    # Crea alcune interazioni recenti
    create_test_interaction()
    create_test_interaction()
    
    # Ottieni le interazioni recenti
    response = client.get(
        "/api/memory/interactions/recent?limit=5",
        headers=AUTH_HEADERS
    )
    
    # Verifica la risposta
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "interactions" in data["data"]
    assert "count" in data["data"]
    assert isinstance(data["data"]["interactions"], list)
    assert 0 < len(data["data"]["interactions"]) <= 5

def test_interactions_by_date():
    """
    Test per verificare che la route GET /api/memory/interactions/by-date funzioni correttamente.
    """
    # Crea un'interazione (che avrà la data di oggi)
    create_test_interaction()
    
    # Ottieni la data di oggi
    today = datetime.now()
    
    # Richiesta per le interazioni di oggi
    response = client.get(
        f"/api/memory/interactions/by-date?year={today.year}&month={today.month}&day={today.day}",
        headers=AUTH_HEADERS
    )
    
    # Verifica la risposta
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "interactions" in data["data"]
    assert "count" in data["data"]
    assert "date" in data["data"]
    assert isinstance(data["data"]["interactions"], list)
    assert len(data["data"]["interactions"]) > 0

def test_interactions_by_invalid_date():
    """
    Test per verificare che la route GET /api/memory/interactions/by-date 
    gestisca correttamente date non valide.
    """
    # Richiesta con una data non valida
    response = client.get(
        "/api/memory/interactions/by-date?year=2024&month=13&day=32",
        headers=AUTH_HEADERS
    )
    
    # Verifica che la risposta indichi un errore
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["type"] == "InvalidDateError"

def test_search_interactions():
    """
    Test per verificare che la route GET /api/memory/interactions/search funzioni correttamente.
    """
    # Crea un'interazione con contenuto specifico per la ricerca
    unique_term = f"searchable_term_{str(uuid.uuid4())[:8]}"
    interaction_data = {
        "agent_id": "search_agent",
        "command": "search_command",
        "prompt": f"This is a test prompt with {unique_term} to search for",
        "response": "Generic response",
        "cost": 0.01,
        "metadata": {"test": "search"}
    }
    
    create_response = client.post(
        "/api/memory/interactions",
        json=interaction_data,
        headers=AUTH_HEADERS
    )
    
    assert create_response.status_code == 200
    
    # Esegui la ricerca
    response = client.get(
        f"/api/memory/interactions/search?query={unique_term}",
        headers=AUTH_HEADERS
    )
    
    # Verifica la risposta
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "interactions" in data["data"]
    assert "count" in data["data"]
    assert "query" in data["data"]
    assert data["data"]["query"] == unique_term
    assert isinstance(data["data"]["interactions"], list)
    assert len(data["data"]["interactions"]) > 0
    
    # Verifica che il termine di ricerca sia presente in almeno un'interazione
    found = False
    for interaction in data["data"]["interactions"]:
        if unique_term in interaction["prompt"] or unique_term in interaction["response"]:
            found = True
            break
    assert found, f"Il termine di ricerca '{unique_term}' non è stato trovato nei risultati"

def test_authentication_required():
    """
    Test per verificare che gli endpoint del sistema memory richiedano autenticazione.
    """
    # Prova ad accedere senza token
    endpoints = [
        "/api/memory/interactions",
        "/api/memory/interactions/recent",
        "/api/memory/interactions/search?query=test"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)  # Senza header di autenticazione
        assert response.status_code == 401, f"L'endpoint {endpoint} non richiede autenticazione come previsto"
