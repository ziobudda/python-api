# Piano di Integrazione del Sistema Memory in Python API REST

## Informazioni di base

### Directory di partenza (codice sorgente)
Il sistema di memory da integrare si trova attualmente in:
```
/Users/michel/LAVORI/ziobuddalabs/agents/lista_intelligente/src/core/memory/
```

### Directory di destinazione (progetto target)
Il progetto Python API REST in cui integrare il sistema memory si trova in:
```
/Users/michel/LAVORI/ziobuddalabs/python-api/
```

## 1. Creazione della struttura di base per il modulo memory
- Creare una directory `memory` all'interno di `api/utils`
- Copiare i file principali dal sistema esistente al nuovo modulo
- Adattare le importazioni e le dipendenze

## 2. Implementazione dell'endpoint `/api/memory`
- Creare il modulo `api/routes/memory.py` per gli endpoint
- Implementare le operazioni CRUD per le interazioni
- Definire i modelli di dati Pydantic per le richieste e le risposte

## 3. Configurazione
- Aggiungere le impostazioni specifiche per la memory nel file `config/settings.py`
- Creare un file di configurazione YAML per il sistema di memory

## 4. Integrazione con il sistema esistente
- Aggiornare `app.py` per includere il nuovo router
- Garantire che l'autenticazione e la formattazione delle risposte siano coerenti

## 5. Testing
- Creare test per verificare il corretto funzionamento degli endpoint
- Testare le interazioni tra il sistema memory e il resto dell'API

## 6. Documentazione
- Aggiornare la documentazione per includere le nuove funzionalità
- Fornire esempi di utilizzo degli endpoint memory

## Dettagli di implementazione

### 1. Creazione della struttura di base per il modulo memory

#### 1.1 File da copiare dalla directory sorgente alla destinazione
Copiare i seguenti file/directory dalla sorgente:
```
/Users/michel/LAVORI/ziobuddalabs/agents/lista_intelligente/src/core/memory/__init__.py
/Users/michel/LAVORI/ziobuddalabs/agents/lista_intelligente/src/core/memory/interfaces.py
/Users/michel/LAVORI/ziobuddalabs/agents/lista_intelligente/src/core/memory/manager.py
/Users/michel/LAVORI/ziobuddalabs/agents/lista_intelligente/src/core/memory/memory_system.py
/Users/michel/LAVORI/ziobuddalabs/agents/lista_intelligente/src/core/memory/models.py
/Users/michel/LAVORI/ziobuddalabs/agents/lista_intelligente/src/core/memory/storage/
```

#### 1.2 Struttura delle directory da creare nella destinazione
```
/Users/michel/LAVORI/ziobuddalabs/python-api/api/utils/memory/
├── __init__.py
├── interfaces.py
├── manager.py
├── memory_system.py
├── models.py
└── storage/
    ├── __init__.py
    ├── factory.py
    └── file_memory.py
```

#### 1.3 Adattamento dei file
- Modificare le importazioni per riflettere la nuova struttura
- Adattare le classi per funzionare nel nuovo ambiente

### 2. Implementazione dell'endpoint `/api/memory`

#### 2.1 Creazione del file `api/routes/memory.py`
- Definire il router per gli endpoint memory
- Implementare endpoint per:
  - `GET /api/memory/interactions` - Elenco delle interazioni
  - `GET /api/memory/interactions/{interaction_id}` - Dettagli di un'interazione
  - `POST /api/memory/interactions` - Registrazione di una nuova interazione
  - `GET /api/memory/interactions/search` - Ricerca di interazioni
  - `GET /api/memory/interactions/recent` - Interazioni recenti
  - `GET /api/memory/interactions/by-date` - Interazioni per data

#### 2.2 Definizione dei modelli di dati Pydantic
- Modello `InteractionCreate` per la creazione di interazioni
- Modello `InteractionResponse` per la risposta

### 3. Configurazione

#### 3.1 Aggiornamento di `config/settings.py`
```python
# Configurazione Memory
MEMORY_CONFIG_PATH = os.getenv("MEMORY_CONFIG_PATH", "config/memory.yaml")
MEMORY_ACTIVE_STORAGE = os.getenv("MEMORY_ACTIVE_STORAGE", "default")
```

#### 3.2 Creazione del file di configurazione YAML
Creare `config/memory.yaml` con configurazione simile a:
```yaml
memory:
  active_storage: default
  storages:
    default:
      type: file
      path: data/memory/interactions.json
      backup:
        enabled: true
        backup_dir: data/memory/backups
        max_backups: 10
        interval_days: 7
```

### 4. Integrazione con il sistema esistente

#### 4.1 Aggiornamento di `app.py`
```python
# Importare il nuovo router
from api.routes.memory import router as memory_router

# Registrare il router
app.include_router(memory_router)
```

#### 4.2 Coerenza di autenticazione e risposta
- Utilizzare `token_dependency` per autenticazione
- Usare `success_response` e `error_response` per formattazione uniforme

### 5. Testing

#### 5.1 Test degli endpoint
Creare `tests/test_memory.py` con test per ogni endpoint:
- Test creazione interazione
- Test recupero interazione
- Test ricerca interazioni
- Test gestione errori

### 6. Documentazione

#### 6.1 Documentazione API
Aggiornare `docs/` con:
- Descrizione del sistema memory
- Dettagli sugli endpoint
- Esempi di richieste e risposte

#### 6.2 Aggiornamento README
Includere informazioni sul nuovo modulo memory nel README principale
