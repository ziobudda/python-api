# Documentazione Sistema Memory per Python API REST

## Panoramica

Il sistema Memory è un componente integrato nel progetto Python API REST che fornisce funzionalità di memorizzazione e recupero delle interazioni. Implementa un pattern singleton per garantire un'unica istanza del sistema di memoria e supporta diversi tipi di storage, attualmente principalmente basati su file JSON.

## Struttura del Sistema

Il sistema Memory è composto dai seguenti moduli principali:

```
api/utils/memory/
├── __init__.py           # Esporta le classi principali
├── interfaces.py         # Definisce le interfacce
├── manager.py            # Gestisce le operazioni di memoria
├── memory_system.py      # Implementa il pattern singleton
├── models.py             # Definisce i modelli di dati
└── storage/              # Implementazioni dello storage
    ├── __init__.py
    ├── factory.py        # Factory per creare istanze di storage
    └── file_memory.py    # Implementazione basata su file
```

## Componenti Principali

### MemorySystem

La classe `MemorySystem` è il punto di ingresso principale del sistema memory. Implementa il pattern singleton per garantire che esista un'unica istanza del sistema nella applicazione. Gestisce la configurazione, crea e mantiene gli storage e i manager di memoria.

```python
# Ottenere l'istanza singleton
memory_system = MemorySystem.get_instance("config/memory.yaml")

# Ottenere il memory manager predefinito
manager = memory_system.memory_manager

# Ottenere un memory manager per uno storage specifico
custom_manager = memory_system.get_memory_manager("custom_storage")
```

### MemoryManager

La classe `MemoryManager` fornisce metodi per registrare, cercare e recuperare interazioni. Ogni manager è associato a un'istanza specifica di storage.

```python
# Registrare una nuova interazione
interaction_id = manager.record_interaction(
    agent_id="agent1",
    command="analyze_image",
    prompt="Descrivi questa immagine",
    response="L'immagine mostra un paesaggio montano...",
    cost=0.02,
    metadata={"image_id": "img123", "model": "gpt-4-vision"}
)

# Recuperare interazioni recenti
recent_interactions = manager.find_recent_interactions(limit=10, agent_id="agent1")

# Recuperare un'interazione specifica
interaction = manager.get_interaction(interaction_id)

# Cercare interazioni per data
date_interactions = manager.find_interactions_by_date(datetime.now())
```

### Interaction

La classe `Interaction` rappresenta una singola interazione memorizzata nel sistema. Contiene tutte le informazioni relative all'interazione inclusi ID, timestamp, agent, comando, prompt, risposta e metadati.

```python
interaction = Interaction(
    id="550e8400-e29b-41d4-a716-446655440000",
    timestamp=datetime.now(),
    agent_id="agent1",
    command="analyze_text",
    prompt="Analizza questo testo...",
    response="Il testo contiene...",
    cost=0.01,
    metadata={"chars": 1500}
)
```

### Storage

Il sistema supporta diverse implementazioni di storage attraverso l'interfaccia `MemoryStorageInterface`. Attualmente è implementato il `FileMemory` che memorizza le interazioni in un file JSON.

```python
# Creazione manuale di uno storage file (normalmente gestito da MemorySystem)
file_storage = FileMemory(file_path="data/memory/interactions.json")
```

## Configurazione

Il sistema memory si configura attraverso un file YAML. Ecco un esempio di configurazione:

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
    analytics:
      type: file
      path: data/memory/analytics.json
```

## Caratteristiche Principali

### 1. Memorizzazione Persistente

Il sistema memorizza le interazioni in modo persistente, attualmente utilizzando file JSON. Ogni interazione viene salvata con un ID univoco generato automaticamente, un timestamp e tutti i dettagli dell'interazione.

### 2. Backup Automatico

Il sistema implementa un meccanismo di backup automatico per i file di storage. Viene creata una copia del file prima di ogni operazione di scrittura, con timestamp nel nome per facilitare il recupero in caso di problemi.

### 3. Pattern Singleton

Il sistema utilizza il pattern singleton per garantire che esista un'unica istanza del sistema memory nell'applicazione, evitando duplicazioni e inconsistenze.

### 4. Gestione Multi-storage

È possibile configurare e utilizzare diversi storage contemporaneamente, ciascuno con il proprio manager. Questo permette di separare le interazioni per scopi diversi (es. debug, analytics, ecc.).

### 5. Ricerca e Filtri

Il sistema offre funzionalità avanzate di ricerca e filtro:
- Ricerca per ID
- Ricerca per comando e agent
- Ricerca per data
- Recupero delle interazioni più recenti
- Filtri personalizzati tramite predicati

### 6. Gestione Errori

Implementa una gestione completa degli errori con logging dettagliato per facilitare il debug e garantire la robustezza del sistema anche in caso di problemi con i file di storage.

## Utilizzo nell'API REST

Il sistema memory viene integrato nell'API REST attraverso endpoint dedicati che consentono di registrare nuove interazioni, recuperare interazioni esistenti e cercare interazioni in base a diversi criteri.

## Estendibilità

Il sistema è progettato per essere facilmente estendibile:

1. **Nuovi tipi di storage**: È possibile implementare nuovi tipi di storage (es. database) implementando l'interfaccia `MemoryStorageInterface`.

2. **Nuove funzionalità di ricerca**: È possibile aggiungere nuovi metodi di ricerca nel `MemoryManager` per supportare casi d'uso specifici.

3. **Integrazione con altri sistemi**: Il pattern singleton e l'interfaccia di programmazione pulita facilitano l'integrazione con altri componenti dell'applicazione.
