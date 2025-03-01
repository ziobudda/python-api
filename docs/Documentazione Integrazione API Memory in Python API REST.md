# Documentazione Integrazione API Memory in Python API REST

## Panoramica

Questa documentazione descrive gli endpoint REST implementati per il sistema Memory, che fornisce funzionalità di memorizzazione e recupero delle interazioni per il progetto Python API REST. Il sistema Memory permette di registrare in modo persistente tutte le interazioni, inclusi comandi, prompt, risposte e metadati associati, e di recuperarle tramite vari metodi di ricerca e filtraggio.

## Endpoints API

Il sistema Memory espone i seguenti endpoint REST, tutti sotto il prefisso `/api/memory`:

### 1. Registrazione di una nuova interazione

**Endpoint**: `POST /api/memory/interactions`

**Descrizione**: Registra una nuova interazione nel sistema memory.

**Parametri di richiesta**:
```json
{
  "agent_id": "string",     // Identificatore dell'agent chiamante
  "command": "string",      // Comando o funzione eseguita
  "prompt": "string",       // Prompt o input fornito
  "response": "string",     // Risposta o output generato
  "cost": 0.0,             // Opzionale: costo dell'operazione
  "metadata": {}           // Opzionale: metadati aggiuntivi dell'interazione
}
```

**Esempio di richiesta**:
```json
{
  "agent_id": "search-agent",
  "command": "google_search",
  "prompt": "Cerca notizie recenti sull'intelligenza artificiale",
  "response": "Ho trovato i seguenti risultati: 1. Nuovi sviluppi in AI generativa...",
  "cost": 0.05,
  "metadata": {
    "query": "notizie recenti intelligenza artificiale",
    "results_count": 10,
    "execution_time_ms": 1250
  }
}
```

**Risposta di successo**:
```json
{
  "success": true,
  "data": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "timestamp": "2024-03-01T15:23:45.123456",
    "agent_id": "search-agent",
    "command": "google_search",
    "prompt": "Cerca notizie recenti sull'intelligenza artificiale",
    "response": "Ho trovato i seguenti risultati: 1. Nuovi sviluppi in AI generativa...",
    "cost": 0.05,
    "metadata": {
      "query": "notizie recenti intelligenza artificiale",
      "results_count": 10,
      "execution_time_ms": 1250
    }
  },
  "message": "Interazione registrata con successo: f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

### 2. Recupero di una specifica interazione

**Endpoint**: `GET /api/memory/interactions/{interaction_id}`

**Descrizione**: Recupera i dettagli di una specifica interazione tramite il suo ID.

**Parametri del percorso**:
- `interaction_id`: ID univoco dell'interazione da recuperare

**Esempio di richiesta**:
```
GET /api/memory/interactions/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

**Risposta di successo**:
```json
{
  "success": true,
  "data": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "timestamp": "2024-03-01T15:23:45.123456",
    "agent_id": "search-agent",
    "command": "google_search",
    "prompt": "Cerca notizie recenti sull'intelligenza artificiale",
    "response": "Ho trovato i seguenti risultati: 1. Nuovi sviluppi in AI generativa...",
    "cost": 0.05,
    "metadata": {
      "query": "notizie recenti intelligenza artificiale",
      "results_count": 10,
      "execution_time_ms": 1250
    }
  }
}
```

**Risposta di errore** (interazione non trovata):
```json
{
  "success": false,
  "error": {
    "message": "Interazione non trovata: f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "type": "InteractionNotFound"
  }
}
```

### 3. Elenco delle interazioni

**Endpoint**: `GET /api/memory/interactions`

**Descrizione**: Recupera un elenco di interazioni con possibilità di filtraggio.

**Parametri di query**:
- `agent_id` (opzionale): Filtra per ID dell'agent
- `command` (opzionale): Filtra per comando
- `limit` (opzionale, default=10): Numero massimo di risultati da restituire

**Esempio di richiesta**:
```
GET /api/memory/interactions?agent_id=search-agent&command=google_search&limit=5
```

**Risposta di successo**:
```json
{
  "success": true,
  "data": {
    "interactions": [
      {
        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "timestamp": "2024-03-01T15:23:45.123456",
        "agent_id": "search-agent",
        "command": "google_search",
        "prompt": "Cerca notizie recenti sull'intelligenza artificiale",
        "response": "Ho trovato i seguenti risultati: 1. Nuovi sviluppi in AI generativa...",
        "cost": 0.05,
        "metadata": {
          "query": "notizie recenti intelligenza artificiale",
          "results_count": 10,
          "execution_time_ms": 1250
        }
      },
      // Altri risultati...
    ],
    "count": 3
  },
  "message": "Recuperate 3 interazioni"
}
```

### 4. Interazioni recenti

**Endpoint**: `GET /api/memory/interactions/recent`

**Descrizione**: Recupera le interazioni più recenti dal sistema memory.

**Parametri di query**:
- `limit` (opzionale, default=5): Numero massimo di risultati da restituire
- `agent_id` (opzionale): Filtra per ID dell'agent

**Esempio di richiesta**:
```
GET /api/memory/interactions/recent?limit=3&agent_id=search-agent
```

**Risposta di successo**:
```json
{
  "success": true,
  "data": {
    "interactions": [
      // Interazioni più recenti in ordine cronologico inverso
    ],
    "count": 3
  },
  "message": "Recuperate 3 interazioni recenti"
}
```

### 5. Interazioni per data

**Endpoint**: `GET /api/memory/interactions/by-date`

**Descrizione**: Recupera le interazioni di una specifica data dal sistema memory.

**Parametri di query**:
- `year`: Anno della data (es. 2024)
- `month`: Mese della data (1-12)
- `day`: Giorno della data (1-31)
- `agent_id` (opzionale): Filtra per ID dell'agent

**Esempio di richiesta**:
```
GET /api/memory/interactions/by-date?year=2024&month=3&day=1&agent_id=search-agent
```

**Risposta di successo**:
```json
{
  "success": true,
  "data": {
    "interactions": [
      // Interazioni della data specificata
    ],
    "count": 8,
    "date": "2024-03-01"
  },
  "message": "Recuperate 8 interazioni per la data 2024-03-01"
}
```

**Risposta di errore** (data non valida):
```json
{
  "success": false,
  "error": {
    "message": "Data non valida: month must be in 1..12",
    "type": "InvalidDateError"
  }
}
```

### 6. Ricerca nelle interazioni

**Endpoint**: `GET /api/memory/interactions/search`

**Descrizione**: Cerca nelle interazioni per testo contenuto nei prompt, risposte o comandi.

**Parametri di query**:
- `query`: Testo da cercare
- `limit` (opzionale, default=10): Numero massimo di risultati da restituire
- `agent_id` (opzionale): Filtra per ID dell'agent

**Esempio di richiesta**:
```
GET /api/memory/interactions/search?query=intelligenza%20artificiale&limit=5
```

**Risposta di successo**:
```json
{
  "success": true,
  "data": {
    "interactions": [
      // Interazioni che contengono il testo cercato
    ],
    "count": 5,
    "query": "intelligenza artificiale"
  },
  "message": "Trovate 5 interazioni per la query 'intelligenza artificiale'"
}
```

## Autenticazione

Tutti gli endpoint richiedono autenticazione tramite token API. Il token deve essere fornito nell'header HTTP `X-API-Token`:

```
X-API-Token: <your-api-token>
```

Richieste senza token valido riceveranno una risposta 401 Unauthorized.

## Formato delle Risposte

### Risposta di Successo

Tutte le risposte di successo seguono il seguente formato:

```json
{
  "success": true,
  "data": {
    // Dati specifici dell'endpoint
  },
  "message": "Messaggio descrittivo dell'operazione completata" // Opzionale
}
```

### Risposta di Errore

Tutte le risposte di errore seguono il seguente formato:

```json
{
  "success": false,
  "error": {
    "message": "Descrizione dettagliata dell'errore",
    "type": "TipoErrore",
    "details": { /* Dettagli aggiuntivi opzionali */ }
  }
}
```

## Codici di Stato HTTP

- **200 OK**: Richiesta completata con successo
- **400 Bad Request**: Parametri di richiesta non validi
- **401 Unauthorized**: Token di autenticazione mancante o non valido
- **404 Not Found**: Risorsa non trovata
- **500 Internal Server Error**: Errore interno del server

## Modelli di Dati

### Interaction

```json
{
  "id": "string",             // ID univoco dell'interazione
  "timestamp": "string",      // Data e ora in formato ISO 8601
  "agent_id": "string",       // Identificatore dell'agent
  "command": "string",        // Comando o funzione eseguita
  "prompt": "string",         // Prompt o input fornito
  "response": "string",       // Risposta o output generato
  "cost": 0.0,               // Costo dell'operazione (opzionale)
  "metadata": {}             // Metadati aggiuntivi (opzionale)
}
```

## Esempi di Utilizzo

### Registrazione di un'interazione dopo una ricerca Google

```python
import requests
import json

API_URL = "http://localhost:8000"
API_TOKEN = "your_api_token"

headers = {
    "X-API-Token": API_TOKEN,
    "Content-Type": "application/json"
}

# Effettua una ricerca Google
search_response = requests.get(
    f"{API_URL}/api/search/google?query=notizie+oggi",
    headers=headers
).json()

if search_response["success"]:
    # Registra l'interazione nel sistema memory
    memory_data = {
        "agent_id": "search-client",
        "command": "google_search",
        "prompt": "Cerca: notizie oggi",
        "response": json.dumps(search_response["data"], ensure_ascii=False),
        "metadata": {
            "query": "notizie oggi",
            "results_count": len(search_response["data"]["results"]),
            "client_ip": "192.168.1.100"
        }
    }
    
    memory_response = requests.post(
        f"{API_URL}/api/memory/interactions",
        headers=headers,
        json=memory_data
    ).json()
    
    print(f"Interazione memorizzata con ID: {memory_response['data']['id']}")
```

### Recupero delle interazioni recenti per un agent

```python
import requests

API_URL = "http://localhost:8000"
API_TOKEN = "your_api_token"

headers = {
    "X-API-Token": API_TOKEN,
}

# Recupera le 5 interazioni più recenti per un agent specifico
response = requests.get(
    f"{API_URL}/api/memory/interactions/recent?limit=5&agent_id=search-client",
    headers=headers
).json()

if response["success"]:
    interactions = response["data"]["interactions"]
    print(f"Recuperate {len(interactions)} interazioni recenti:")
    
    for i, interaction in enumerate(interactions, 1):
        print(f"\n--- Interazione {i} ---")
        print(f"ID: {interaction['id']}")
        print(f"Data: {interaction['timestamp']}")
        print(f"Comando: {interaction['command']}")
        print(f"Prompt: {interaction['prompt'][:50]}...")
```

## Considerazioni sulla Sicurezza

- Tutti gli endpoint sono protetti da autenticazione tramite token
- Il sistema memory è progettato per memorizzare dati potenzialmente sensibili, quindi è importante garantire che:
  - I file di storage siano adeguatamente protetti a livello di sistema operativo
  - L'accesso agli endpoint sia limitato a client autorizzati
  - Le comunicazioni siano crittografate tramite HTTPS in ambienti di produzione

## Considerazioni sulle Prestazioni

- Per ottimizzare le prestazioni con grandi volumi di dati:
  - Utilizzare il parametro `limit` per limitare il numero di risultati restituiti
  - Filtrare le ricerche il più possibile utilizzando `agent_id` e altri parametri
  - Considerare l'uso di date specifiche con l'endpoint `by-date` invece di recuperare tutte le interazioni

## Limitazioni Attuali

- Lo storage attuale è basato su file JSON, che potrebbe avere limiti di prestazioni con volumi di dati molto grandi
- La ricerca full-text è implementata in modo semplice e potrebbe non essere ottimale per grandi dataset
- Non è possibile eseguire query complesse o aggregazioni sui dati memorizzati

## Estensioni Future

- Implementazione di storage basati su database (MongoDB, PostgreSQL)
- Supporto per ricerca full-text avanzata con indicizzazione
- Funzionalità di aggregazione e analisi dei dati memorizzati
- Supporto per eliminazione e aggiornamento delle interazioni
- Funzionalità di esportazione dati in vari formati (CSV, JSON)
- Supporto per una console web di amministrazione
