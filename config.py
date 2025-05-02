import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Clés API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configuration Llama4
LLAMA4_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# Configuration TTS
TTS_LANGUAGE = "fr"  # Langue française par défaut

# Configuration de l'application
APP_TITLE = "Spotify for Learning"
APP_DESCRIPTION = "Générateur de snippets d'apprentissage personnalisés de 5 minutes"
AUDIO_DIR = "static/audio"

# Assurer que le répertoire audio existe
os.makedirs(AUDIO_DIR, exist_ok=True)
