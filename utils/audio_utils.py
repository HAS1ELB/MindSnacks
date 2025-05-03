# utils/audio_utils.py
import os
import uuid
import asyncio
import time
import re
from num2words import num2words
from config import AUDIO_DIR, AVAILABLE_LANGUAGES
import edge_tts
from gtts import gTTS

# Mapping des langues aux voix Edge TTS (prioriser ar-SA-ZariyahNeural pour l'arabe)
VOICE_MAPPING = {
    'fr': ["fr-FR-HenriNeural", "fr-FR-DeniseNeural", "fr-FR-BrigitteNeural"],
    'en': ["en-US-GuyNeural", "en-US-JennyNeural"],
    'es': ["es-ES-AlvaroNeural", "es-ES-ElviraNeural"],
    'de': ["de-DE-KillianNeural", "de-DE-KatjaNeural"],
    'it': ["it-IT-DiegoNeural", "it-IT-ElsaNeural"],
    'ja': ["ja-JP-KeitaNeural", "ja-JP-NanamiNeural"],
    'zh': ["zh-CN-YunxiNeural", "zh-CN-XiaoxiaoNeural"],
    'ar': ["ar-SA-ZariyahNeural", "ar-SA-NaayfNeural"]  # Prioriser ZariyahNeural
}

async def _generate_edge_tts_audio(text, output_file, language='fr', voice_index=0):
    """Fonction asynchrone pour générer de l'audio avec edge-tts"""
    try:
        voices = VOICE_MAPPING.get(language, ["fr-FR-HenriNeural"])
        voice = voices[voice_index % len(voices)]  # Sélectionner une voix spécifique
        # Vérifier que le texte n'est pas vide
        if not text or text.isspace():
            print(f"Erreur: Le texte pour la synthèse vocale est vide.")
            return False
        
        # Debugging: Afficher le texte et la voix utilisée
        print(f"Génération audio avec voix: {voice}, langue: {language}")
        print(f"Texte envoyé à edge-tts: {text[:100]}...")  # Limiter à 100 caractères pour le log
        
        # Créer un Communicate avec des paramètres explicites
        communicate = edge_tts.Communicate(text, voice, rate="+0%", volume="+0%")
        await communicate.save(output_file)
        
        # Vérifier si le fichier a été créé et n'est pas vide
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"Fichier audio généré avec succès: {output_file}")
            time.sleep(1)  # Pause pour finalisation du fichier
            return True
        else:
            print(f"Erreur: Aucun fichier audio généré à {output_file} ou fichier vide.")
            return False
            
    except Exception as e:
        print(f"Erreur lors de la génération edge-tts avec voix {voice}: {str(e)}")
        return False

def clean_text_for_tts(text, language='fr'):
    """
    Nettoie le texte pour la synthèse vocale en supprimant les marqueurs et en convertissant les nombres.
    """
    if not text:
        print("Erreur: Le texte fourni est vide.")
        return ""
    
    # Supprimer les puces et numéros de liste
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)  # Supprime - ou *
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Supprime 1., 2., etc.
    
    # Convertir les nombres en mots dans la langue cible
    def replace_number(match):
        num = int(match.group(0))
        try:
            # Fallback en anglais pour l'arabe (num2words ne supporte pas l'arabe)
            target_lang = language if language != 'ar' else 'en'
            return num2words(num, lang=target_lang)
        except:
            return str(num)  # Fallback si num2words échoue
    
    text = re.sub(r'\b\d+\b', replace_number, text)
    
    # Supprimer les symboles indésirables (#, *, etc.)
    text = re.sub(r'[#*]', '', text)
    
    # Pour l'arabe, filtrer les caractères non pris en charge
    if language == 'ar':
        # Conserver les caractères arabes, espaces, ponctuation de base, et chiffres arabes
        text = re.sub(r'[^\u0600-\u06FF\u0660-\u0669\s.,!?]', '', text)
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
    
    # Remplacer les sauts de ligne par des pauses naturelles
    text = re.sub(r'\n+', '. ', text).strip()
    
    # Vérifier si le texte nettoyé est toujours valide
    if not text:
        print("Erreur: Le texte nettoyé est vide après traitement.")
        return "Texte par défaut pour la synthèse vocale."
    
    return text

# import streamlit as st  # Already imported at the top

# Remove @st.cache_data for debugging
def generate_audio(text, title, language='fr'):
    """
    Génère un fichier audio à partir d'un texte donné en utilisant edge-tts avec un fallback à gTTS pour l'arabe.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Generating audio for title: {title}, language: {language}")
    
    try:
        # Nettoyer le titre et le texte
        cleaned_title = clean_text_for_tts(title, language)
        cleaned_text = clean_text_for_tts(text, language)
        
        # Vérifier si le texte nettoyé est valide
        if not cleaned_text or not cleaned_title:
            logger.error("Erreur: Le texte ou le titre nettoyé est vide après traitement.")
            return None
        
        # Debugging: Afficher le texte nettoyé
        logger.info(f"Titre nettoyé: {cleaned_title}")
        logger.info(f"Texte nettoyé: {cleaned_text[:100]}...")
        
        # Ajouter une pause après le titre
        full_text = f"{cleaned_title}. {cleaned_text}"
        
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Essayer chaque voix disponible pour la langue avec edge-tts
        voices = VOICE_MAPPING.get(language, ["fr-FR-HenriNeural"])
        for i, voice in enumerate(voices):
            logger.info(f"Tentative avec la voix {voice} ({i+1}/{len(voices)})...")
            success = loop.run_until_complete(_generate_edge_tts_audio(full_text, filepath, language, voice_index=i))
            if success:
                loop.close()
                logger.info(f"Audio generation successful: {filepath}")
                return filepath
        
        # Si edge-tts échoue pour toutes les voix et que la langue est arabe, utiliser gTTS comme fallback
        if language == 'ar':
            logger.info("Échec avec edge-tts, tentative avec gTTS pour l'arabe...")
            tts = gTTS(text=full_text, lang='ar')
            tts.save(filepath)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                logger.info(f"Fichier audio généré avec succès via gTTS: {filepath}")
                loop.close()
                return filepath
            else:
                logger.error("Échec de la génération audio avec gTTS.")
        
        # Si toutes les tentatives échouent
        logger.error("Échec de la génération audio avec toutes les méthodes disponibles.")
        loop.close()
        return None
            
    except Exception as e:
        logger.error(f"Erreur grave lors de la génération audio: {str(e)}")
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