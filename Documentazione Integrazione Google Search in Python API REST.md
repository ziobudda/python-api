# Documentazione Integrazione Google Search in Python API REST

## Panoramica

Questa integrazione estende il sistema Python API REST con la capacità di eseguire ricerche su Google e restituire i risultati in formato JSON. L'implementazione utilizza Playwright per automatizzare le interazioni browser e recuperare i risultati della ricerca in modo robusto, evitando i blocchi anti-scraping di Google. La funzionalità include ora il supporto per la paginazione, consentendo di ottenere un maggior numero di risultati.

## Funzionalità Principali

- Ricerca su Google con parametri personalizzabili
- **Paginazione dei risultati** con supporto fino a 10 pagine di ricerca
- Estrazione strutturata di titoli, URL e descrizioni dei risultati
- **Indicazione della pagina di provenienza** per ogni risultato
- **Rimozione automatica dei duplicati** tra le pagine
- Gestione automatica dei tentativi in caso di errore
- Sistema anti-blocco avanzato
- Rate limiting per evitare blocchi di Google
- Supporto per screenshot e informazioni di debug

## Endpoint API

### `GET /api/search/google`

Esegue una ricerca su Google e restituisce i risultati formattati.

**Parametri**:

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| query | string | (richiesto) | La query di ricerca |
| lang | string | "it" | Lingua dei risultati (es: it, en, fr) |
| num_results | integer | 5 | Numero di risultati da restituire per pagina (max 20) |
| **max_pages** | integer | 1 | **Numero massimo di pagine da consultare (max 10)** |
| sleep_interval | float | 2.0 | Pausa in secondi tra le richieste |
| include_screenshot | boolean | false | Se includere uno screenshot nella risposta |
| use_stealth | boolean | true | Utilizzare tecniche stealth per evitare blocchi |
| use_proxy | boolean | false | Utilizzare un proxy se configurato |
| retry_count | integer | 2 | Numero di tentativi in caso di errore |

**Esempio di richiesta**:

```
GET /api/search/google?query=notizie%20oggi&num_results=3&max_pages=2&lang=it
```

**Risposta di successo**:

```json
{
  "success": true,
  "data": {
    "query": "notizie oggi",
    "results": [
      {
        "title": "Ultime notizie del giorno - Corriere della Sera",
        "url": "https://www.corriere.it/",
        "description": "Le notizie di oggi dall'Italia e dal mondo. Ultime news su cronaca, politica, economia e sport con foto, immagini e video.",
        "page": 1
      },
      {
        "title": "Notizie - la Repubblica",
        "url": "https://www.repubblica.it/",
        "description": "Notizie e approfondimenti di cronaca, politica, economia e sport.",
        "page": 1
      },
      {
        "title": "Giornale di Brescia",
        "url": "https://www.giornaledibrescia.it/",
        "description": "Il Giornale di Brescia ha notizie di oggi, cronaca, meteo e molto altro.",
        "page": 1
      },
      {
        "title": "ANSA: Agenzia Nazionale Stampa Associata",
        "url": "https://www.ansa.it/",
        "description": "Agenzia di stampa italiana. Notizie, foto, video e approfondimenti di cronaca, politica, economia, sport.",
        "page": 2
      },
      {
        "title": "Il Sole 24 ORE: notizie di economia, finanza, borsa",
        "url": "https://www.ilsole24ore.com/",
        "description": "News di economia, cronaca italiana ed estera, quotazioni borsa in tempo reale e di finanza, norme e tributi, assicurazioni.",
        "page": 2
      },
      {
        "title": "Il Fatto Quotidiano",
        "url": "https://www.ilfattoquotidiano.it/",
        "description": "Informazione indipendente, notizie esclusive, inchieste, opinioni e approfondimenti su oggi Italia e mondo.",
        "page": 2
      }
    ],
    "stats": "Circa 1.830.000.000 risultati (0,56 secondi)",
    "pages_fetched": 2
  },
  "message": "Ricerca completata con successo: notizie oggi (6 risultati da 2 pagine)"
}
```

**Risposta di errore**:

```json
{
  "success": false,
  "error": {
    "message": "Google ha rilevato attività insolita e ha bloccato la richiesta. Riprova più tardi.",
    "type": "GoogleBlockError",
    "details": {
      "query": "notizie oggi"
    }
  }
}
```

### `POST /api/search/google`

Endpoint con la stessa funzionalità della versione GET, ma accetta parametri nel corpo della richiesta.

## Implementazione Tecnica

### Componenti Principali

1. **Browser Automation**:
   - Utilizza Playwright per emulare un browser reale
   - Implementa tecniche stealth per evitare il rilevamento come bot
   - Gestisce cookie, user-agent e altre impostazioni per apparire come un utente umano

2. **Paginazione**:
   - Rilevamento automatico dei link "Avanti" o di paginazione
   - Navigazione sequenziale tra le pagine di risultati
   - Combina i risultati di più pagine, mantenendo l'indicazione della provenienza
   - Rimuove automaticamente i risultati duplicati tra diverse pagine

3. **Estrazione Dati**:
   - Utilizza selettori CSS flessibili per adattarsi ai cambiamenti del layout di Google
   - Implementa meccanismi di fallback per garantire l'estrazione dei risultati
   - Mantiene la tracciabilità della provenienza di ogni risultato (numero di pagina)

4. **Gestione Errori**:
   - Sistema di retry con backoff esponenziale
   - Rilevamento di blocchi e CAPTCHA
   - Logging dettagliato per diagnostica

4. **Ottimizzazione Prestazioni**:
   - Blocco di risorse non necessarie (immagini, CSS, font)
   - Parametri di caricamento ottimizzati
   - Strategia di caching per ridurre le richieste
   - Pausa calibrata tra le pagine per evitare comportamenti sospetti

### Anti-Detection

L'implementazione include diverse tecniche per evitare il rilevamento da parte di Google:

- **Browser Fingerprinting**: Modifica delle proprietà del browser per apparire come un utente reale
- **Comportamento Umano**: Simulazione di pause, movimenti del mouse e scrolling
- **Parametri URL**: Utilizzo di parametri che disabilitano personalizzazioni
- **Cookie Management**: Impostazione di cookie per simulare una sessione esistente
- **Paginazione Naturale**: Attesa tra il caricamento delle pagine successivamente

## Configurazione

Le impostazioni per questa funzionalità sono configurabili tramite il file `.env`:

```
# Google Search specifiche
GOOGLE_DEFAULT_LANG=it
GOOGLE_MAX_RESULTS=20
GOOGLE_MAX_PAGES=10
GOOGLE_SLEEP_INTERVAL=2.0
BROWSER_STEALTH_MODE=True
USE_PROXIES=False
SEARCH_TIMEOUT=90
SEARCH_RATE_LIMIT=10
SEARCH_COOLDOWN=60
```

## Best Practices

1. **Rate Limiting**: Limita il numero di richieste per evitare blocchi di Google
2. **Paginazione Ragionevole**: Utilizza max_pages con valori bassi (1-3) per ricerche frequenti
3. **Proxy Rotation**: Per uso intensivo, configura proxy rotanti
4. **Robustezza**: Implementa il controllo di errori nella tua applicazione client
5. **Rispetto dei ToS**: Utilizza questa funzionalità in modo responsabile e in conformità con i Termini di Servizio di Google

## Limitazioni Conosciute

1. Google può occasionalmente bloccare le richieste nonostante le tecniche anti-detection
2. I selettori CSS potrebbero richiedere aggiornamenti se Google modifica il suo layout
3. Performance influenzate dalla connessione internet e dalle risorse del server
4. Un numero elevato di pagine richieste può aumentare la probabilità di blocchi

## Alternative

Per applicazioni che richiedono affidabilità elevata o volumi significativi, considera:

1. **Google Custom Search API**: API ufficiale di Google (richiede chiave API e ha limiti di utilizzo)
2. **SerpAPI**: Servizio di terze parti con elevata affidabilità (soluzione a pagamento)
