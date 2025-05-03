import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Clés API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configuration Llama4
LLAMA4_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# Langues disponibles
AVAILABLE_LANGUAGES = {
    'fr': 'Français',
    'en': 'English',
    'es': 'Español',
    'de': 'Deutsch',
    'it': 'Italiano',
    'ja': '日本語',
    'zh': '中文'
}

# Configuration TTS par défaut
DEFAULT_LANGUAGE = 'fr'

# Configuration de l'application
APP_TITLE = "Spotify for Learning"
APP_DESCRIPTION = "Générateur de snippets d'apprentissage personnalisés de 5 minutes"
AUDIO_DIR = "static/audio"

# Configuration des chemins
TRANSLATIONS_DIR = "translations"

# Assurer que les répertoires nécessaires existent
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSLATIONS_DIR, exist_ok=True)