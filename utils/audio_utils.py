import os
import time
import uuid
import tempfile
from gtts import gTTS
from config import TTS_LANGUAGE, AUDIO_DIR

def generate_audio(text, title):
    """
    Génère un fichier audio à partir d'un texte donné en utilisant gTTS.
    
    Args:
        text (str): Le texte à convertir en audio
        title (str): Le titre du snippet, utilisé pour nommer le fichier
    
    Returns:
        str: Le chemin du fichier audio généré
    """
    try:
        # Générer un nom de fichier unique
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        # Préparer le texte pour la synthèse vocale
        full_text = f"{title}. {text}"
        
        # Générer l'audio avec gTTS
        tts = gTTS(text=full_text, lang=TTS_LANGUAGE, slow=False)
        tts.save(filepath)
        
        return filepath
    
    except Exception as e:
        print(f"Erreur lors de la génération audio: {e}")
        return None

def get_audio_duration(filepath):
    """
    Obtient la durée d'un fichier audio en secondes.
    
    Args:
        filepath (str): Le chemin du fichier audio
    
    Returns:
        float: La durée en secondes
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(filepath)
        return len(audio) / 1000.0  # Convertir millisecondes en secondes
    except Exception as e:
        print(f"Erreur lors de l'obtention de la durée audio: {e}")
        # Estimer la durée basée sur le nombre de caractères (approximativement)
        # Un locuteur lit environ 150 mots par minute, soit environ 750 caractères
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            # Une estimation très approximative
            return max(300, file_size / 10000)  # Au moins 5 minutes
        return 300  # Par défaut 5 minutes