# Copier ce fichier vers config.py et renseigner les vraies valeurs.
# config.py est ignoré par git (voir .gitignore) pour éviter de publier des secrets.
import os

TARGET = os.getenv("OLLAMA_PROXY_TARGET", "https://ollama.mondomaine.com")

CF_HEADERS = {
    "CF-Access-Client-Id": os.getenv("CF_ACCESS_CLIENT_ID", "REPLACE_ME"),
    "CF-Access-Client-Secret": os.getenv("CF_ACCESS_CLIENT_SECRET", "REPLACE_ME"),
}

# Identifiants pour protéger l'accès à la page de chat (HTTP Basic Auth).
UI_USERNAME = os.getenv("UI_USERNAME", "admin")
UI_PASSWORD = os.getenv("UI_PASSWORD", "changeme")

# Activer ou désactiver l'interface web locale (True par défaut)
ENABLE_UI = os.getenv("ENABLE_UI", "True").lower() == "true"

# Activer ou désactiver le verbose logging (False par défaut)
VERBOSE_LOGGING = os.getenv("VERBOSE_LOGGING", "False").lower() == "true"
