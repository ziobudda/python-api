# Configurazione di Python API REST come servizio su Debian 12

## Panoramica del Progetto

Il progetto consiste in un sistema REST basato su Python che risponde a chiamate esterne fornendo dati in formato JSON. Il sistema utilizza il framework FastAPI e include funzionalità di automazione browser tramite Playwright e integrazione con Google Search.

### Struttura del Progetto

L'applicazione è organizzata secondo la seguente struttura:

```
python-api/
│
├── api/                    # Package principale delle API
│   ├── routes/             # Endpoint API organizzati per moduli 
│   │   ├── browser.py      # Endpoint per l'automazione del browser
│   │   ├── search.py       # Endpoint per le ricerche su Google
│   │   └── crawl.py        # Endpoint per il crawling
│   │
│   ├── utils/              # Utilità condivise
│   │   ├── browser/        # Modulo per l'automazione del browser
│   │   └── responses.py    # Formattatori di risposta standardizzati
│   │
│   └── __init__.py
│
├── config/                 # Configurazioni
│   ├── __init__.py
│   └── settings.py         # Impostazioni dell'applicazione
│
├── tests/                  # Test automatizzati
│
├── venv/                   # Ambiente virtuale Python
│
├── .env                    # Variabili d'ambiente
├── .gitignore              # File da escludere dal controllo versione
├── app.py                  # Punto di ingresso dell'applicazione
├── README.md               # Documentazione del progetto
├── requirements.txt        # Dipendenze del progetto
├── run.sh                  # Script per avviare l'applicazione
└── setup.sh                # Script per configurare l'ambiente
```

## Configurazione come Servizio su Debian 12

### Requisiti di Implementazione

- Server Debian 12
- Python 3
- Nginx configurato con il dominio N8NAPI.DOMAIN.EXT
- Directory del sito web: `/var/www/N8NAPI_DOMAIN_EXT/web_dir`

### Passaggi di Configurazione

#### 1. Trasferimento dei File

Trasferire i file dal sistema locale al server Debian:

```bash
cd /path/to/local/project/
rsync -av --exclude 'venv' --exclude '__pycache__' --exclude '.git' python-api/ UTENTE_N8NAPI@server-debian:/var/www/N8NAPI_DOMAIN_EXT/web_dir/
```

#### 2. Installazione delle Dipendenze di Sistema

```bash
# Aggiornamento pacchetti
sudo apt update && sudo apt upgrade -y

# Installazione delle dipendenze
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Installazione di Playwright e browser necessari
sudo apt install -y libgbm1 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
                   libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
                   libpango-1.0-0 libpangocairo-1.0-0 libnspr4 libnss3 libxss1
```

#### 3. Configurazione dell'Ambiente Python

```bash
# Configura permessi
sudo chown -R www-data:www-data /var/www/N8NAPI_DOMAIN_EXT/web_dir

# Crea e configura l'ambiente virtuale
cd /var/www/N8NAPI_DOMAIN_EXT/web_dir
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install -r requirements.txt

# Installazione e configurazione di Playwright
sudo -u www-data ./venv/bin/playwright install
```

#### 4. Configurazione del Servizio Systemd

Creare il file `/etc/systemd/system/python-api.service`:

```ini
[Unit]
Description=Python REST API Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/N8NAPI_DOMAIN_EXT/web_dir
Environment="PATH=/var/www/N8NAPI_DOMAIN_EXT/web_dir/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/var/www/N8NAPI_DOMAIN_EXT/web_dir/venv/bin/python /var/www/N8NAPI_DOMAIN_EXT/web_dir/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=python-api

# Hardening
PrivateTmp=true
ProtectSystem=full
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

#### 5. Configurazione di Nginx

Aggiornare o creare il file di configurazione Nginx in `/etc/nginx/sites-available/N8NAPI.DOMAIN.EXT`:

```nginx
server {
    listen 80;
    server_name N8NAPI.DOMAIN.EXT;

    root /var/www/N8NAPI_DOMAIN_EXT/web_dir;
    index index.html;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_read_timeout 86400;
    }

    # Per servire risorse statiche direttamente se necessario
    location /static {
        alias /var/www/N8NAPI_DOMAIN_EXT/web_dir/static;
    }

    # Configurazioni SSL, se presenti
    # listen 443 ssl;
    # ssl_certificate /etc/letsencrypt/live/N8NAPI.DOMAIN.EXT/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/N8NAPI.DOMAIN.EXT/privkey.pem;
    # include /etc/letsencrypt/options-ssl-nginx.conf;
    # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
```

Attivare la configurazione:

```bash
sudo ln -s /etc/nginx/sites-available/N8NAPI.DOMAIN.EXT /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Configurazione dell'ambiente di produzione

Aggiornare il file `.env` per l'ambiente di produzione:

```bash
sudo nano /var/www/N8NAPI_DOMAIN_EXT/web_dir/.env
```

Contenuto consigliato:

```
# Configurazione ambiente
ENV=production

# Configurazione server
HOST=127.0.0.1  # Importante: su produzione, Nginx farà da proxy
PORT=8000
LOG_LEVEL=info

# Configurazione autenticazione API
API_TOKEN=<token-sicuro-e-complesso>

# Altre configurazioni specifiche...
```

#### 7. Attivazione e avvio del servizio

```bash
# Ricarica la configurazione systemd
sudo systemctl daemon-reload

# Abilita e avvia il servizio
sudo systemctl enable python-api.service
sudo systemctl start python-api.service

# Verifica lo stato
sudo systemctl status python-api.service
```

#### 8. Verifica del funzionamento

Per verificare che l'API risponda correttamente:

```bash
curl -s -H "Authorization: Bearer <token>" "http://N8NAPI.DOMAIN.EXT/"
```

Per testare un endpoint specifico:

```bash
curl -s -H "Authorization: Bearer <token>" "http://N8NAPI.DOMAIN.EXT/api/browser/load?url=https://www.example.com"
```

### Comandi utili per la gestione del servizio

```bash
# Controllare lo stato del servizio
sudo systemctl status python-api.service

# Riavviare il servizio
sudo systemctl restart python-api.service

# Fermare il servizio
sudo systemctl stop python-api.service

# Visualizzare i log del servizio
sudo journalctl -u python-api.service

# Visualizzare i log in tempo reale
sudo journalctl -u python-api.service -f
```

### Script completo di configurazione

Per automatizzare l'installazione, è possibile utilizzare lo script seguente:

```bash
#!/bin/bash

# Directory di destinazione
WEBDIR="/var/www/N8NAPI_DOMAIN_EXT/web_dir"

# Assicurati che la directory esista
if [ ! -d "$WEBDIR" ]; then
    echo "Errore: La directory $WEBDIR non esiste."
    exit 1
fi

# Aggiornamento pacchetti
echo "Aggiornamento dei pacchetti del sistema..."
sudo apt update && sudo apt upgrade -y

# Installazione delle dipendenze
echo "Installazione delle dipendenze di sistema..."
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Installazione di Playwright e browser necessari
echo "Installazione di Playwright e browser..."
sudo apt install -y libgbm1 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libpangocairo-1.0-0 libnspr4 libnss3 libxss1

# Configurazione dei permessi
echo "Configurazione dei permessi..."
sudo chown -R www-data:www-data $WEBDIR

# Creazione dell'ambiente virtuale
echo "Configurazione ambiente virtuale Python..."
cd $WEBDIR
sudo -u www-data python3 -m venv venv

# Installazione delle dipendenze Python
echo "Installazione delle dipendenze Python..."
sudo -u www-data $WEBDIR/venv/bin/pip install -r requirements.txt

# Se usi Playwright, installalo
echo "Installazione Playwright..."
sudo -u www-data $WEBDIR/venv/bin/pip install playwright
sudo -u www-data $WEBDIR/venv/bin/playwright install

# Creazione del file di servizio systemd
echo "Creazione del file systemd..."
cat > /tmp/python-api.service << 'EOL'
[Unit]
Description=Python REST API Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/N8NAPI_DOMAIN_EXT/web_dir
Environment="PATH=/var/www/N8NAPI_DOMAIN_EXT/web_dir/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/var/www/N8NAPI_DOMAIN_EXT/web_dir/venv/bin/python /var/www/N8NAPI_DOMAIN_EXT/web_dir/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=python-api

# Hardening
PrivateTmp=true
ProtectSystem=full
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOL

sudo mv /tmp/python-api.service /etc/systemd/system/python-api.service

# Ricarica systemd e avvia il servizio
echo "Avvio del servizio..."
sudo systemctl daemon-reload
sudo systemctl enable python-api.service
sudo systemctl start python-api.service

echo "Installazione completata! Il servizio Python API è ora in esecuzione."
echo "Controlla lo stato con: sudo systemctl status python-api.service"
```

### Note sulla manutenzione

- **Aggiornamenti del codice**: Dopo aver trasferito nuove versioni del codice, riavviare il servizio con `sudo systemctl restart python-api.service`
- **Dipendenze**: Se vengono aggiunte nuove dipendenze, aggiornare l'ambiente virtuale con `sudo -u www-data /var/www/N8NAPI_DOMAIN_EXT/web_dir/venv/bin/pip install -r requirements.txt`
- **Log e debug**: Monitorare i log per rilevare eventuali errori con `sudo journalctl -u python-api.service -f`
- **Backup**: Eseguire regolarmente backup della directory del progetto
