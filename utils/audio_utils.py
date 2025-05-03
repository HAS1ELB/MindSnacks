import os
import uuid
import asyncio
import time
from config import AUDIO_DIR, AVAILABLE_LANGUAGES
import edge_tts

# Mapping des langues aux voix Edge TTS
VOICE_MAPPING = {
    'fr': "fr-FR-HenriNeural",
    'en': "en-US-GuyNeural",
    'es': "es-ES-AlvaroNeural",
    'de': "de-DE-KillianNeural",
    'it': "it-IT-DiegoNeural",
    'ja': "ja-JP-KeitaNeural",
    'zh': "zh-CN-YunxiNeural"
}

async def _generate_edge_tts_audio(text, output_file, language='fr'):
    """Fonction asynchrone pour générer de l'audio avec edge-tts"""
    try:
        voice = VOICE_MAPPING.get(language, "fr-FR-HenriNeural")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Erreur lors de la génération edge-tts: {e}")
        return False

def generate_audio(text, title, language='fr'):
    """
    Génère un fichier audio à partir d'un texte donné en utilisant edge-tts.
    """
    try:
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        full_text = f"{title}. {text}"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(_generate_edge_tts_audio(full_text, filepath, language))
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
    """
    try:
        if os.path.exists(filepath):
            file_size_kb = os.path.getsize(filepath) / 1024
            estimated_duration = file_size_kb / 10
            return max(estimated_duration, 10)
    except Exception as e:
        print(f"Erreur lors de l'estimation de la durée audio: {e}")
    
    return 300