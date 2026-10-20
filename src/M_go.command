#!/bin/bash
cd "$(dirname "$0")"

# Vérification de l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo "[ERREUR] Le répertoire d'environnement virtuel .venv n'existe pas."
    echo "Veuillez exécuter M_install_requirements.command pour initialiser l'environnement."
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
fi

# Activation de l'environnement virtuel
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERREUR] Échec de l'activation de l'environnement virtuel."
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
fi

#Confirmation d'activation
echo "[INFO] Environnement virtuel activé avec succès."

# Exécution du proxy (en local seulement; utiliser --host 0.0.0.0 pour l'exposer au réseau local)
echo "[INFO] Démarrage de proxy.py..."
python3 -m uvicorn proxy:app --host 127.0.0.1 --port 11434
if [ $? -ne 0 ]; then
    echo "[ERREUR] L'exécution du script a échoué."
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
fi
