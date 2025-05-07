import os
from dotenv import load_dotenv
import json
import datetime

# Load environment variables from .env file
load_dotenv()

# Application version
APP_VERSION = "2.1.0"

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY") 

# Development mode
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# LLM Model Configuration
LLM_MODELS = {
    "default": "meta-llama/llama-4-scout-17b-16e-instruct",
    "fallback": "llama4-8b-fast",
    "summarization": "meta-llama/llama-4-8b-fast",
    "generation": "meta-llama/llama-4-scout-17b-16e-instruct",
}

# Available languages
AVAILABLE_LANGUAGES = {
    'fr': 'Français',
    'en': 'English',
    'es': 'Español',
    'de': 'Deutsch',
    'it': 'Italiano',
    'ja': '日本語',
    'zh': '中文',
    'ar': 'العربية',
    'pt': 'Português',  # Added new language
    'ru': 'Русский',    # Added new language
    'ko': '한국어',      # Added new language
}

# RTL languages
RTL_LANGUAGES = ['ar']

# Default application settings
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", 'en')
DEFAULT_THEME = os.getenv("DEFAULT_THEME", 'dark')
DEFAULT_SNIPPET_DURATION = 5  # minutes
MAX_SNIPPET_DURATION = 15     # minutes
MIN_SNIPPET_DURATION = 1      # minutes
WORDS_PER_MINUTE = 150

# Application Configuration
APP_TITLE = "Mindsnacks: Spotify for Learning"
APP_DESCRIPTION = "Customized audio learning snippets for curious minds"
APP_EMOJI = "🎧"

# Firebase config for user authentication (if provided)
FIREBASE_CONFIG = None
if FIREBASE_API_KEY:
    FIREBASE_CONFIG = {
        "apiKey": FIREBASE_API_KEY,
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
    }

# Directory Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
CACHE_DIR = os.path.join(STATIC_DIR, "cache")
ANALYTICS_DIR = os.path.join(STATIC_DIR, "analytics")
QUIZ_DIR = os.path.join(STATIC_DIR, "quiz")
USER_DATA_DIR = os.path.join(STATIC_DIR, "users")
EXPORT_DIR = os.path.join(STATIC_DIR, "exports")
OFFLINE_DIR = os.path.join(STATIC_DIR, "offline")
TRANSLATIONS_DIR = os.path.join(BASE_DIR, "translations")
CSS_DIR = os.path.join(STATIC_DIR, "css")
JS_DIR = os.path.join(STATIC_DIR, "js")
IMG_DIR = os.path.join(STATIC_DIR, "img")

# Ensure all necessary directories exist
for directory in [
    AUDIO_DIR, TRANSLATIONS_DIR, CACHE_DIR, ANALYTICS_DIR, 
    CSS_DIR, JS_DIR, IMG_DIR, QUIZ_DIR, USER_DATA_DIR,
    EXPORT_DIR, OFFLINE_DIR
]:
    os.makedirs(directory, exist_ok=True)

# Cache settings
CACHE_TTL = 60 * 60 * 24 * 7  # 1 week in seconds
AUDIO_CACHE_TTL = 60 * 60 * 24 * 30  # 30 days in seconds

# Audio settings
AUDIO_COMPRESSION = True
AUDIO_COMPRESSION_BITRATE = "128k"
AUDIO_FORMATS = ["mp3", "ogg", "wav"]
DEFAULT_AUDIO_FORMAT = "mp3"

# Security settings
JWT_SECRET = os.getenv("JWT_SECRET", os.urandom(24).hex())
JWT_EXPIRY = 60 * 60 * 24 * 7  # 1 week in seconds

# Social sharing
ENABLE_SOCIAL_SHARING = True
SHARING_PLATFORMS = ["twitter", "facebook", "linkedin", "whatsapp", "email"]

# Analytics
ENABLE_ANALYTICS = True
ANALYTICS_RETENTION_DAYS = 90

# User points and gamification
POINTS = {
    "snippet_created": 10,
    "playlist_created": 20,
    "quiz_completed": 15,
    "daily_login": 5,
    "share_content": 5,
    "feedback_provided": 10
}

# Achievements
ACHIEVEMENTS = [
    {"id": "first_snippet", "name": "First Snippet", "description": "Create your first learning snippet", "points": 10},
    {"id": "knowledge_explorer", "name": "Knowledge Explorer", "description": "Create snippets on 5 different topics", "points": 25},
    {"id": "polyglot", "name": "Polyglot", "description": "Use the app in 3 different languages", "points": 30},
    {"id": "quiz_master", "name": "Quiz Master", "description": "Complete 10 quizzes with a perfect score", "points": 50},
    {"id": "daily_learner", "name": "Daily Learner", "description": "Use the app for 7 consecutive days", "points": 35},
]

# App information
APP_INFO = {
    "version": APP_VERSION,
    "release_date": "May 7, 2025",
    "developers": ["HAS1ELB", "Contributors"],
    "website": "https://github.com/HAS1ELB/MindSnacks",
    "license": "MIT",
}

# Export current config for client-side use
def get_client_config():
    return {
        "app_version": APP_VERSION,
        "languages": AVAILABLE_LANGUAGES,
        "rtl_languages": RTL_LANGUAGES,
        "default_language": DEFAULT_LANGUAGE,
        "default_theme": DEFAULT_THEME,
        "enable_social_sharing": ENABLE_SOCIAL_SHARING,
        "sharing_platforms": SHARING_PLATFORMS,
        "app_title": APP_TITLE,
        "app_emoji": APP_EMOJI,
        "enable_analytics": ENABLE_ANALYTICS,
        "audio_formats": AUDIO_FORMATS,
        "default_audio_format": DEFAULT_AUDIO_FORMAT,
    }

# Save client config to JS file for client-side access
def save_client_config():
    client_config = get_client_config()
    config_path = os.path.join(JS_DIR, "config.js")
    with open(config_path, 'w') as f:
        f.write(f"const MINDSNACKS_CONFIG = {json.dumps(client_config, indent=2)};")
    
    return client_config