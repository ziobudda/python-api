# Esempi di Utilizzo del Sistema Memory

Questo documento fornisce esempi pratici di utilizzo del sistema Memory integrato nell'API REST Python. I seguenti esempi mostrano come interagire con gli endpoint del sistema Memory da diversi linguaggi di programmazione.

## Esempio Base in Python

Ecco un esempio semplice in Python per registrare e recuperare interazioni utilizzando il sistema Memory:

```python
import requests
import json
from datetime import datetime

# Configurazione di base
API_URL = "http://localhost:8000"
API_TOKEN = "your_api_token_here"  # Sostituire con il token effettivo

# Headers standard per tutte le richieste
headers = {
    "X-API-Token": API_TOKEN,
    "Content-Type": "application/json"
}

def create_interaction(agent_id, command, prompt, response, cost=None, metadata=None):
    """
    Crea una nuova interazione nel sistema memory
    """
    payload = {
        "agent_id": agent_id,
        "command": command,
        "prompt": prompt,
        "response": response,
        "cost": cost,
        "metadata": metadata or {}
    }
    
    response = requests.post(
        f"{API_URL}/api/memory/interactions",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Interazione creata con ID: {result['data']['id']}")
        return result['data']['id']
    else:
        print(f"Errore nella creazione dell'interazione: {response.text}")
        return None

def get_interaction(interaction_id):
    """
    Recupera un'interazione specifica per ID
    """
    response = requests.get(
        f"{API_URL}/api/memory/interactions/{interaction_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Errore nel recupero dell'interazione: {response.text}")
        return None

def get_recent_interactions(limit=5, agent_id=None):
    """
    Recupera le interazioni più recenti
    """
    params = {"limit": limit}
    if agent_id:
        params["agent_id"] = agent_id
        
    response = requests.get(
        f"{API_URL}/api/memory/interactions/recent",
        params=params,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['data']['interactions']
    else:
        print(f"Errore nel recupero delle interazioni recenti: {response.text}")
        return []

def search_interactions(query, limit=10, agent_id=None):
    """
    Cerca nelle interazioni per testo contenuto in prompt o risposte
    """
    params = {
        "query": query,
        "limit": limit
    }
    if agent_id:
        params["agent_id"] = agent_id
        
    response = requests.get(
        f"{API_URL}/api/memory/interactions/search",
        params=params,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['data']['interactions']
    else:
        print(f"Errore nella ricerca delle interazioni: {response.text}")
        return []

def get_interactions_by_date(year, month, day, agent_id=None):
    """
    Recupera le interazioni per una data specifica
    """
    params = {
        "year": year,
        "month": month,
        "day": day
    }
    if agent_id:
        params["agent_id"] = agent_id
        
    response = requests.get(
        f"{API_URL}/api/memory/interactions/by-date",
        params=params,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['data']['interactions']
    else:
        print(f"Errore nel recupero delle interazioni per data: {response.text}")
        return []

# Esempio di utilizzo completo
if __name__ == "__main__":
    # 1. Creazione di una nuova interazione
    interaction_id = create_interaction(
        agent_id="example-agent",
        command="text-analysis",
        prompt="Analizza il seguente testo: 'Python è un linguaggio di programmazione versatile'",
        response="Il testo parla di Python come linguaggio di programmazione, evidenziandone la versatilità.",
        cost=0.005,
        metadata={
            "model": "gpt-4",
            "tokens": 120,
            "processing_time_ms": 450
        }
    )
    
    if interaction_id:
        # 2. Recupero dell'interazione appena creata
        interaction = get_interaction(interaction_id)
        print(f"\nDettagli dell'interazione creata:")
        print(f"ID: {interaction['id']}")
        print(f"Timestamp: {interaction['timestamp']}")
        print(f"Agent: {interaction['agent_id']}")
        print(f"Comando: {interaction['command']}")
        print(f"Costo: {interaction['cost']}")
        
        # 3. Recupero delle interazioni recenti
        print("\nInterazioni recenti:")
        recent = get_recent_interactions(limit=3)
        for i, interaction in enumerate(recent, 1):
            print(f"  {i}. [{interaction['timestamp']}] {interaction['command']} - {interaction['prompt'][:40]}...")
        
        # 4. Ricerca di interazioni
        print("\nRicerca di interazioni con 'Python':")
        search_results = search_interactions("Python")
        for i, interaction in enumerate(search_results, 1):
            print(f"  {i}. {interaction['command']} - {interaction['prompt'][:40]}...")
        
        # 5. Interazioni per data corrente
        today = datetime.now()
        print(f"\nInterazioni per oggi ({today.year}-{today.month}-{today.day}):")
        today_interactions = get_interactions_by_date(today.year, today.month, today.day)
        for i, interaction in enumerate(today_interactions, 1):
            print(f"  {i}. {interaction['command']} - {interaction['agent_id']}")
```

## Esempio di integrazione con ricerca Google

Questo esempio mostra come integrare il sistema Memory con la funzionalità di ricerca Google per memorizzare automaticamente le ricerche effettuate:

```python
import requests
import json
import time

API_URL = "http://localhost:8000"
API_TOKEN = "your_api_token_here"

headers = {
    "X-API-Token": API_TOKEN,
    "Content-Type": "application/json"
}

def perform_google_search(query, num_results=5, lang="it"):
    """
    Esegue una ricerca su Google e registra l'interazione
    """
    start_time = time.time()
    
    # Esegui la ricerca su Google
    search_params = {
        "query": query,
        "num_results": num_results,
        "lang": lang
    }
    
    search_response = requests.get(
        f"{API_URL}/api/search/google",
        params=search_params,
        headers=headers
    )
    
    if search_response.status_code != 200:
        print(f"Errore nella ricerca: {search_response.text}")
        return None
    
    search_data = search_response.json()
    
    # Calcola il tempo di esecuzione
    execution_time = time.time() - start_time
    
    # Registra l'interazione nel sistema memory
    memory_payload = {
        "agent_id": "search-client",
        "command": "google_search",
        "prompt": f"Ricerca Google: {query}",
        "response": json.dumps({
            "results_count": len(search_data["data"]["results"]),
            "stats": search_data["data"].get("stats", ""),
            "first_result": search_data["data"]["results"][0] if search_data["data"]["results"] else {}
        }, ensure_ascii=False),
        "metadata": {
            "query": query,
            "num_results": num_results,
            "lang": lang,
            "execution_time_s": round(execution_time, 3),
            "results_count": len(search_data["data"]["results"])
        }
    }
    
    memory_response = requests.post(
        f"{API_URL}/api/memory/interactions",
        json=memory_payload,
        headers=headers
    )
    
    if memory_response.status_code == 200:
        memory_data = memory_response.json()
        print(f"Interazione memorizzata con ID: {memory_data['data']['id']}")
    else:
        print(f"Errore nella memorizzazione dell'interazione: {memory_response.text}")
    
    return search_data["data"]

# Esempio di utilizzo
search_results = perform_google_search("Python programmazione tutorial", num_results=3)

if search_results:
    print("\nRisultati della ricerca:")
    for i, result in enumerate(search_results["results"], 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   {result['description'][:100]}...")
        print()

# Recupera le ricerche precedenti
previous_searches = requests.get(
    f"{API_URL}/api/memory/interactions",
    params={"agent_id": "search-client", "command": "google_search"},
    headers=headers
).json()

print("\nRicerche precedenti:")
for i, interaction in enumerate(previous_searches["data"]["interactions"], 1):
    metadata = interaction.get("metadata", {})
    print(f"{i}. Query: {metadata.get('query', 'N/A')}")
    print(f"   Timestamp: {interaction['timestamp']}")
    print(f"   Risultati trovati: {metadata.get('results_count', 'N/A')}")
    print()
```

## Esempio in JavaScript/Node.js

Ecco un esempio di utilizzo del sistema Memory da Node.js:

```javascript
const axios = require('axios');

// Configurazione di base
const API_URL = 'http://localhost:8000';
const API_TOKEN = 'your_api_token_here';

// Headers standard per tutte le richieste
const headers = {
  'X-API-Token': API_TOKEN,
  'Content-Type': 'application/json'
};

// Funzione per creare una nuova interazione
async function createInteraction(agent_id, command, prompt, response, cost = null, metadata = {}) {
  try {
    const payload = {
      agent_id,
      command,
      prompt,
      response,
      cost,
      metadata
    };
    
    const result = await axios.post(
      `${API_URL}/api/memory/interactions`,
      payload,
      { headers }
    );
    
    console.log(`Interazione creata con ID: ${result.data.data.id}`);
    return result.data.data.id;
  } catch (error) {
    console.error('Errore nella creazione dell\'interazione:', error.response?.data || error.message);
    return null;
  }
}

// Funzione per recuperare le interazioni recenti
async function getRecentInteractions(limit = 5, agent_id = null) {
  try {
    const params = { limit };
    if (agent_id) params.agent_id = agent_id;
    
    const response = await axios.get(
      `${API_URL}/api/memory/interactions/recent`,
      { params, headers }
    );
    
    return response.data.data.interactions;
  } catch (error) {
    console.error('Errore nel recupero delle interazioni recenti:', error.response?.data || error.message);
    return [];
  }
}

// Esempio di utilizzo
async function run() {
  // Creazione di una nuova interazione
  const interactionId = await createInteraction(
    'nodejs-client',
    'text-processing',
    'Elabora questo testo: "JavaScript è un linguaggio di programmazione versatile"',
    'Il testo descrive JavaScript come un linguaggio di programmazione versatile.',
    0.003,
    {
      framework: 'Node.js',
      version: '16.x',
      processing_time_ms: 320
    }
  );
  
  if (interactionId) {
    // Recupero delle interazioni recenti
    console.log('\nInterazioni recenti:');
    const recentInteractions = await getRecentInteractions(3);
    
    recentInteractions.forEach((interaction, index) => {
      console.log(`${index + 1}. [${interaction.timestamp}] ${interaction.command}`);
      console.log(`   Agent: ${interaction.agent_id}`);
      console.log(`   Prompt: ${interaction.prompt.substring(0, 50)}...`);
      console.log();
    });
  }
}

run().catch(error => console.error('Errore:', error));
```

## Esempio di Script per Analisi dei Dati

Questo script dimostra come utilizzare le API del sistema Memory per analizzare i dati memorizzati:

```python
import requests
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import Counter

API_URL = "http://localhost:8000"
API_TOKEN = "your_api_token_here"

headers = {
    "X-API-Token": API_TOKEN
}

def get_interactions_for_period(days=7):
    """
    Recupera le interazioni degli ultimi X giorni
    """
    all_interactions = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        
        response = requests.get(
            f"{API_URL}/api/memory/interactions/by-date",
            params={
                "year": date.year,
                "month": date.month,
                "day": date.day
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            all_interactions.extend(data["data"]["interactions"])
    
    return all_interactions

def analyze_interactions(interactions):
    """
    Analizza le interazioni e restituisce statistiche
    """
    # Conteggio per tipo di comando
    commands = Counter([interaction["command"] for interaction in interactions])
    
    # Conteggio per agent
    agents = Counter([interaction["agent_id"] for interaction in interactions])
    
    # Calcolo costo totale
    total_cost = sum(interaction.get("cost", 0) or 0 for interaction in interactions)
    
    # Analisi temporale (interazioni per giorno)
    days = {}
    for interaction in interactions:
        date = interaction["timestamp"].split("T")[0]  # Estrai solo la data
        days[date] = days.get(date, 0) + 1
    
    return {
        "total_interactions": len(interactions),
        "commands": dict(commands),
        "agents": dict(agents),
        "total_cost": total_cost,
        "interactions_per_day": dict(sorted(days.items()))
    }

# Recupera e analizza le interazioni degli ultimi 7 giorni
interactions = get_interactions_for_period(7)
stats = analyze_interactions(interactions)

# Stampa le statistiche
print(f"Analisi delle interazioni degli ultimi 7 giorni:")
print(f"Totale interazioni: {stats['total_interactions']}")
print(f"Costo totale: ${stats['total_cost']:.4f}")

print("\nComandi più frequenti:")
for command, count in sorted(stats['commands'].items(), key=lambda x: x[1], reverse=True):
    print(f"  {command}: {count}")

print("\nAgent più attivi:")
for agent, count in sorted(stats['agents'].items(), key=lambda x: x[1], reverse=True):
    print(f"  {agent}: {count}")

# Crea un grafico delle interazioni per giorno
days = list(stats['interactions_per_day'].keys())
counts = list(stats['interactions_per_day'].values())

plt.figure(figsize=(10, 6))
plt.bar(days, counts)
plt.title('Interazioni per giorno')
plt.xlabel('Data')
plt.ylabel('Numero di interazioni')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('interactions_per_day.png')
plt.close()

print("\nGrafico salvato come 'interactions_per_day.png'")
```

## Integrazione in cURL

Esempi di utilizzo con cURL per script shell:

```bash
#!/bin/bash

API_URL="http://localhost:8000"
API_TOKEN="your_api_token_here"

# Funzione per registrare una nuova interazione
create_interaction() {
    local agent_id="$1"
    local command="$2"
    local prompt="$3"
    local response="$4"
    
    curl -s -X POST "${API_URL}/api/memory/interactions" \
         -H "X-API-Token: ${API_TOKEN}" \
         -H "Content-Type: application/json" \
         -d "{
             \"agent_id\": \"${agent_id}\",
             \"command\": \"${command}\",
             \"prompt\": \"${prompt}\",
             \"response\": \"${response}\",
             \"metadata\": {
                 \"source\": \"bash-script\",
                 \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"
             }
         }"
}

# Funzione per recuperare le interazioni recenti
get_recent_interactions() {
    local limit="${1:-5}"
    local agent_id="$2"
    local params="limit=${limit}"
    
    if [ -n "$agent_id" ]; then
        params="${params}&agent_id=${agent_id}"
    fi
    
    curl -s -X GET "${API_URL}/api/memory/interactions/recent?${params}" \
         -H "X-API-Token: ${API_TOKEN}" | jq '.data.interactions'
}

# Esempio: Registrazione di un'interazione da un comando shell
command_output=$(ls -la)
create_interaction "bash-client" "shell-command" "ls -la" "$command_output"

# Esempio: Recupero delle interazioni recenti
echo "Interazioni recenti:"
get_recent_interactions 3 "bash-client"
```

## Integrazione con API REST di Terze Parti

Questo esempio mostra come integrare il sistema Memory con API di terze parti per tracciare le chiamate:

```python
import requests
import json
import uuid
import time

API_URL = "http://localhost:8000"
API_TOKEN = "your_api_token_here"

# API esterna di esempio (OpenWeather)
WEATHER_API_KEY = "your_weather_api_key"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

headers = {
    "X-API-Token": API_TOKEN,
    "Content-Type": "application/json"
}

def get_weather(city):
    """
    Ottiene dati meteo e registra l'interazione
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Parametri per l'API meteo
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "it"
    }
    
    # Chiama l'API meteo
    try:
        weather_response = requests.get(WEATHER_API_URL, params=params)
        weather_data = weather_response.json()
        success = weather_response.status_code == 200
        execution_time = time.time() - start_time
        
        # Prepara il prompt e la risposta per la memorizzazione
        prompt = f"Richiesta meteo per la città: {city}"
        
        if success:
            temp = weather_data.get("main", {}).get("temp", "N/A")
            conditions = weather_data.get("weather", [{}])[0].get("description", "N/A")
            response_text = f"Temperatura: {temp}°C, Condizioni: {conditions}"
        else:
            error_msg = weather_data.get("message", "Errore sconosciuto")
            response_text = f"Errore nella richiesta meteo: {error_msg}"
        
        # Memorizza l'interazione
        memory_payload = {
            "agent_id": "weather-client",
            "command": "get_weather",
            "prompt": prompt,
            "response": response_text,
            "metadata": {
                "city": city,
                "request_id": request_id,
                "success": success,
                "status_code": weather_response.status_code,
                "execution_time_s": round(execution_time, 3)
            }
        }
        
        memory_response = requests.post(
            f"{API_URL}/api/memory/interactions",
            json=memory_payload,
            headers=headers
        )
        
        if memory_response.status_code == 200:
            memory_data = memory_response.json()
            print(f"Interazione memorizzata con ID: {memory_data['data']['id']}")
        
        return {
            "success": success,
            "data": weather_data if success else None,
            "error": None if success else weather_data.get("message"),
            "interaction_recorded": memory_response.status_code == 200
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Memorizza anche gli errori
        memory_payload = {
            "agent_id": "weather-client",
            "command": "get_weather",
            "prompt": f"Richiesta meteo per la città: {city}",
            "response": f"Errore nella chiamata API: {str(e)}",
            "metadata": {
                "city": city,
                "request_id": request_id,
                "success": False,
                "error": str(e),
                "execution_time_s": round(execution_time, 3)
            }
        }
        
        try:
            memory_response = requests.post(
                f"{API_URL}/api/memory/interactions",
                json=memory_payload,
                headers=headers
            )
        except:
            pass
        
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "interaction_recorded": False
        }

# Esempio di utilizzo
cities = ["Roma", "Milano", "Napoli", "CittàInesistente"]

for city in cities:
    print(f"\nOttengo il meteo per {city}...")
    result = get_weather(city)
    
    if result["success"]:
        weather = result["data"]
        main = weather.get("main", {})
        weather_desc = weather.get("weather", [{}])[0]
        
        print(f"Temperatura: {main.get('temp')}°C")
        print(f"Condizioni: {weather_desc.get('description')}")
        print(f"Umidità: {main.get('humidity')}%")
    else:
        print(f"Errore: {result['error']}")

# Recupera le ultime interazioni con l'API meteo
print("\nUltime interazioni con l'API meteo:")
weather_interactions = requests.get(
    f"{API_URL}/api/memory/interactions",
    params={
        "agent_id": "weather-client",
        "command": "get_weather",
        "limit": 10
    },
    headers=headers
).json()

for i, interaction in enumerate(weather_interactions["data"]["interactions"], 1):
    metadata = interaction.get("metadata", {})
    success = metadata.get("success", False)
    status = "✅" if success else "❌"
    
    print(f"{i}. {status} {metadata.get('city', 'N/A')} - {interaction['timestamp']}")
    if not success:
        print(f"   Errore: {metadata.get('error', 'N/A')}")
    print(f"   Tempo di esecuzione: {metadata.get('execution_time_s', 'N/A')}s")
```

## Note su Sicurezza e Best Practices

1. **Token di API**: Non includere mai il token API direttamente nel codice. Utilizzare variabili d'ambiente o file di configurazione protetti.

2. **Dati Sensibili**: Evitare di memorizzare dati personali sensibili nei campi `prompt` o `response`. Se necessario, pseudonimizzare o offuscare i dati.

3. **Rate Limiting**: Implementare rate limiting nelle chiamate successive al sistema Memory per evitare sovraccarichi.

4. **Gestione Errori**: Implementare sempre una gestione completa degli errori, come mostrato negli esempi.

5. **Backup**: Per applicazioni critiche, implementare backup periodici del file di storage JSON.

6. **Ottimizzazione delle Query**: Per set di dati molto grandi, utilizzare filtri specifici (agent_id, command) per ridurre il carico sul sistema.

7. **Metadati Utili**: Utilizzare il campo `metadata` per arricchire le interazioni con informazioni contestuali che potrebbero essere utili per analisi future.

## Conclusione

Il sistema Memory offre un modo flessibile e potente per memorizzare e recuperare interazioni all'interno dell'API REST Python. Gli esempi presentati in questo documento mostrano come integrarlo in diverse applicazioni e linguaggi di programmazione.

Utilizzando il sistema Memory, è possibile implementare funzionalità come:
- Tracciamento completo delle chiamate API
- Analisi dell'utilizzo e delle prestazioni
- Registrazione di errori e problemi
- Monitoraggio dei costi
- Audit delle interazioni
- Ottimizzazione basata sui dati storici

Per ulteriori dettagli sulle API disponibili, consultare la documentazione completa degli endpoint Memory nella documentazione principale dell'API REST.
