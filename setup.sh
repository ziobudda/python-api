#!/bin/bash

# Attivazione dell'ambiente virtuale
source venv/bin/activate

# Installazione delle dipendenze
pip install -r requirements.txt

echo "Ambiente configurato con successo!"
echo "Per avviare l'API, esegui: python app.py"
