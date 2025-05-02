import os
import uuid
import asyncio
import time
from config import AUDIO_DIR
import edge_tts

async def _generate_edge_tts_audio(text, output_file):
    """Fonction asynchrone pour générer de l'audio avec edge-tts"""
    try:
        voice = "fr-FR-HenriNeural"  # Voix française masculine par défaut
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        # Attendre un moment pour s'assurer que le fichier est bien écrit
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Erreur lors de la génération edge-tts: {e}")
        return False

def generate_audio(text, title):
    """
    Génère un fichier audio à partir d'un texte donné en utilisant edge-tts.
    Version simplifiée qui n'utilise pas de fichier temporaire ni FFmpeg.

    Args:
        text (str): Le texte à convertir en audio
        title (str): Le titre du snippet (utilisé pour le nom de fichier)

    Returns:
        str: Le chemin du fichier audio généré, ou None en cas d'échec
    """
    try:
        # Préparer le chemin de sortie
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        # Préparer le texte avec le titre
        full_text = f"{title}. {text}"
        
        # Exécuter la fonction asynchrone
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(_generate_edge_tts_audio(full_text, filepath))
        loop.close()
        
        if success and os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return filepath
        else:
            print("Échec de la génération audio avec edge-tts")
            return None
            
    except Exception as e:
        print(f"Erreur grave lors de la génération audio: {e}")
        return None

def get_audio_duration(filepath):
    """
    Obtient la durée d'un fichier audio en secondes.
    Version simplifiée qui renvoie une durée estimée.

    Args:
        filepath (str): Le chemin du fichier audio

    Returns:
        float: La durée en secondes (estimée)
    """
    try:
        # Si le fichier existe, estimer la durée basée sur sa taille
        if os.path.exists(filepath):
            # Estimation très approximative: ~10Ko par seconde pour du MP3
            file_size_kb = os.path.getsize(filepath) / 1024
            estimated_duration = file_size_kb / 10
            return max(estimated_duration, 10)  # Au moins 10 secondes
    except Exception as e:
        print(f"Erreur lors de l'estimation de la durée audio: {e}")
    
    # Valeur par défaut
    return 300  # 5 minutes par défaut
