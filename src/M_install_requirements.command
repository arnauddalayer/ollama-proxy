#!/bin/bash
cd "$(dirname "$0")"

echo "======================================================"
echo   Installation des dependances pour ollama-proxy
echo "======================================================"

# Vérifier que nous nous trouvons dans le répertoire de projet
if [ ! -f "requirements.txt" ]; then
    echo "[ERREUR] Le fichier requirements.txt n'est pas trouvé dans le répertoire actuel."
    echo "Veuillez exécuter le script à partir du répertoire de votre projet."
    exit 1
fi

# Détection et activation de Miniforge/Anaconda si présent
if [ -d "/opt/homebrew/Caskroom/miniforge/base" ]; then
    source "/opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh"
    echo "[INFO] Miniforge détecté dans /opt/homebrew/Caskroom/miniforge/."
fi

# Définition de la commande python
PYTHON_EXE="python3"

# Vérification de la présence de Python
$PYTHON_EXE --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[ERREUR] Python n'est pas détecté."
    echo "Veuillez installer Python ou Miniforge."
    exit 1
fi

echo "1. Création de l'environnement virtuel (.venv)..."
# Vérifier si le répertoire .venv existe et n'est pas vide
if [ -d ".venv" ] && [ "$(ls -A .venv)" ]; then
    echo "[INFO] L'environnement virtuel .venv existe déjà et n'est pas vide."
else
    # Si le répertoire existe mais est vide, le supprimer
    if [ -d ".venv" ]; then
        echo "[INFO] Le répertoire .venv existe mais est vide. Suppression..."
        rm -rf .venv
    fi
    # Créer le répertoire .venv
    echo "[INFO] Création de l'environnement virtuel .venv..."
    $PYTHON_EXE -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[ERREUR] Échec de la création de l'environnement virtuel."
        exit 1
    fi
fi

echo "2. Activation et installation des bibliothèques..."
# Activer l'environnement local
source .venv/bin/activate

# Mise à jour de pip et installation des dépendances
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "======================================================"
echo "  Installation terminée avec succès !"
echo "======================================================"