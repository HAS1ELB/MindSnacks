import os
import yaml
import logging
import re
from typing import Dict, List, Any, Union, Optional
from config import TRANSLATIONS_DIR, AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE

# Configure logging
logger = logging.getLogger(__name__)

# Global cache for translations
_translations_cache = {}

def load_translations(language: str) -> Dict[str, str]:
    """
    Load translations for a language
    
    Args:
        language (str): Language code
        
    Returns:
        dict: Translation dictionary
    """
    # Check cache first
    if language in _translations_cache:
        return _translations_cache[language]
    
    # Default to English if language not available
    if language not in AVAILABLE_LANGUAGES:
        language = DEFAULT_LANGUAGE
    
    # Load translations from YAML file
    translation_path = os.path.join(TRANSLATIONS_DIR, f"{language}.yml")
    
    if not os.path.exists(translation_path):
        logger.warning(f"Translation file not found: {translation_path}")
        
        # Try to create empty translation file
        create_empty_translation_file(language)
        
        # Return empty dict
        return {}
    
    try:
        with open(translation_path, 'r', encoding='utf-8') as f:
            translations = yaml.safe_load(f)
            
            # Cache translations
            _translations_cache[language] = translations
            
            return translations
    except Exception as e:
        logger.error(f"Error loading translations for {language}: {e}")
        return {}

def get_translation(key: str, language: str, default: Optional[str] = None) -> str:
    """
    Get translation for a key
    
    Args:
        key (str): Translation key
        language (str): Language code
        default (str, optional): Default text if key not found
        
    Returns:
        str: Translated text
    """
    translations = load_translations(language)
    
    # Get translation or default
    if key in translations:
        return translations[key]
    
    # Try fallback to English
    if language != DEFAULT_LANGUAGE:
        en_translations = load_translations(DEFAULT_LANGUAGE)
        if key in en_translations:
            return en_translations[key]
    
    # Return default or key as fallback
    return default if default is not None else key

def translate_text(text: str, language: str) -> str:
    """
    Translate a text with embedded translation keys
    
    Args:
        text (str): Text with {key} placeholders
        language (str): Language code
        
    Returns:
        str: Translated text
    """
    # Find all keys in text
    keys = re.findall(r'\{([^}]+)\}', text)
    
    # Get translations
    translations = load_translations(language)
    
    # Replace keys with translations
    for key in keys:
        if key in translations:
            text = text.replace(f"{{{key}}}", translations[key])
    
    return text

def get_all_translations() -> Dict[str, Dict[str, str]]:
    """
    Get all available translations
    
    Returns:
        dict: Dictionary of all translations
    """
    all_translations = {}
    
    for language in AVAILABLE_LANGUAGES:
        all_translations[language] = load_translations(language)
    
    return all_translations

def create_empty_translation_file(language: str) -> bool:
    """
    Create an empty translation file for a language
    
    Args:
        language (str): Language code
        
    Returns:
        bool: True if file created, False otherwise
    """
    if language not in AVAILABLE_LANGUAGES:
        logger.warning(f"Unknown language: {language}")
        return False
    
    translation_path = os.path.join(TRANSLATIONS_DIR, f"{language}.yml")
    
    try:
        # Create basic structure
        translations = {
            "app_title": "Mindsnacks",
            "discover_new_topics": "Discover New Topics",
            "explore_and_expand": "Explore and expand your knowledge",
            "generate": "Generate",
            "library": "Library",
            "discover": "Discover",
            "quiz": "Quiz",
            "settings": "Settings",
            "profile": "Profile",
            "language": "Language",
            "theme": "Theme",
            "dark": "Dark",
            "light": "Light",
            "welcome": "Welcome to Mindsnacks",
            "loading": "Loading...",
            "error": "Error",
            "success": "Success"
        }
        
        # Save to file
        with open(translation_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(translations, f, allow_unicode=True)
        
        # Clear cache
        if language in _translations_cache:
            del _translations_cache[language]
        
        logger.info(f"Created empty translation file: {translation_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating translation file for {language}: {e}")
        return False

def detect_missing_translations() -> Dict[str, List[str]]:
    """
    Detect missing translations in all languages
    
    Returns:
        dict: Dictionary of missing keys per language
    """
    missing = {}
    
    # Load English translations as reference
    en_translations = load_translations(DEFAULT_LANGUAGE)
    en_keys = set(en_translations.keys())
    
    # Check each language
    for language in AVAILABLE_LANGUAGES:
        if language == DEFAULT_LANGUAGE:
            continue
        
        translations = load_translations(language)
        lang_keys = set(translations.keys())
        
        # Find missing keys
        missing_keys = en_keys - lang_keys
        
        if missing_keys:
            missing[language] = list(missing_keys)
    
    return missing

def update_translation(language: str, key: str, value: str) -> bool:
    """
    Update a translation value
    
    Args:
        language (str): Language code
        key (str): Translation key
        value (str): Translated value
        
    Returns:
        bool: True if updated, False otherwise
    """
    if language not in AVAILABLE_LANGUAGES:
        logger.warning(f"Unknown language: {language}")
        return False
    
    translation_path = os.path.join(TRANSLATIONS_DIR, f"{language}.yml")
    
    try:
        # Load existing translations
        translations = load_translations(language)
        
        # Update value
        translations[key] = value
        
        # Save to file
        with open(translation_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(translations, f, allow_unicode=True)
        
        # Update cache
        if language in _translations_cache:
            _translations_cache[language][key] = value
        
        logger.info(f"Updated translation for {language}.{key}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating translation for {language}.{key}: {e}")
        return False

def is_rtl_language(language: str) -> bool:
    """
    Check if language is right-to-left
    
    Args:
        language (str): Language code
        
    Returns:
        bool: True if RTL, False otherwise
    """
    from config import RTL_LANGUAGES
    return language in RTL_LANGUAGES

def get_languages_for_display() -> Dict[str, str]:
    """
    Get languages for display in UI
    
    Returns:
        dict: Dictionary of language codes and names
    """
    return AVAILABLE_LANGUAGES

def initialize_translations() -> bool:
    """
    Initialize all translation files
    
    Returns:
        bool: True if successful, False otherwise
    """
    success = True
    
    for language in AVAILABLE_LANGUAGES:
        translation_path = os.path.join(TRANSLATIONS_DIR, f"{language}.yml")
        
        if not os.path.exists(translation_path):
            result = create_empty_translation_file(language)
            success = success and result
    
    return success

# Initialize translations on module load
try:
    os.makedirs(TRANSLATIONS_DIR, exist_ok=True)
    initialize_translations()
except Exception as e:
    logger.error(f"Error initializing translations: {e}")