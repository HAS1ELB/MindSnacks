import os
import uuid
import asyncio
import time
from config import AUDIO_DIR, AVAILABLE_LANGUAGES
import edge_tts

# Mapping des langues aux voix Edge TTS
VOICE_MAPPING = {
    'fr': ["fr-FR-HenriNeural", "fr-FR-DeniseNeural", "fr-FR-BrigitteNeural"],
    'en': ["en-US-GuyNeural", "en-US-JennyNeural"],
    'es': ["es-ES-AlvaroNeural", "es-ES-ElviraNeural"],
    'de': ["de-DE-KillianNeural", "de-DE-KatjaNeural"],
    'it': ["it-IT-DiegoNeural", "it-IT-ElsaNeural"],
    'ja': ["ja-JP-KeitaNeural", "ja-JP-NanamiNeural"],
    'zh': ["zh-CN-YunxiNeural", "zh-CN-XiaoxiaoNeural"]
}

async def _generate_edge_tts_audio(text, output_file, language='fr', voice_index=0):
    """Fonction asynchrone pour générer de l'audio avec edge-tts"""
    try:
        voices = VOICE_MAPPING.get(language, ["fr-FR-HenriNeural"])
        voice = voices[voice_index % len(voices)]  # Sélectionner une voix spécifique
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Erreur lors de la génération edge-tts: {e}")
        return False
   
import re
from num2words import num2words 
def clean_text_for_tts(text, language='fr'):
    """
    Nettoie le texte pour la synthèse vocale en supprimant les marqueurs et en convertissant les nombres.
    """
    # Supprimer les puces et numéros de liste
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)  # Supprime - ou *
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Supprime 1., 2., etc.
    
    # Convertir les nombres en mots dans la langue cible
    def replace_number(match):
        num = int(match.group(0))
        try:
            return num2words(num, lang=language)
        except:
            return str(num)  # Fallback si num2words ne supporte pas la langue
    
    text = re.sub(r'\b\d+\b', replace_number, text)
    
    # Supprimer les symboles indésirables (#, *, etc.)
    text = re.sub(r'[#*]', '', text)
    
    # Remplacer les sauts de ligne par des pauses naturelles
    text = re.sub(r'\n+', '. ', text).strip()
    
    return text

def generate_audio(text, title, language='fr'):
    """
    Génère un fichier audio à partir d'un texte donné en utilisant edge-tts.
    """
    try:
        # Nettoyer le titre et le texte
        cleaned_title = clean_text_for_tts(title, language)
        cleaned_text = clean_text_for_tts(text, language)
        
        # Ajouter une pause après le titre
        full_text = f"{cleaned_title}. {cleaned_text}"
        
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
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