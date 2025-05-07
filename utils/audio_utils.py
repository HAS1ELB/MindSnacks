import os
import uuid
import asyncio
import time
import re
import logging
import hashlib
import json
import io
from num2words import num2words
from config import (
    AUDIO_DIR, CACHE_DIR, AUDIO_COMPRESSION, 
    AUDIO_COMPRESSION_BITRATE, ELEVENLABS_API_KEY,
    AUDIO_FORMATS, DEFAULT_AUDIO_FORMAT
)
import edge_tts
from gtts import gTTS
from pydub import AudioSegment, effects
import requests

# Try to import ElevenLabs if API key is available
elevenlabs_available = False
if ELEVENLABS_API_KEY:
    try:
        from elevenlabs import generate, set_api_key
        set_api_key(ELEVENLABS_API_KEY)
        elevenlabs_available = True
    except ImportError:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mapping of languages to Edge TTS voices with multiple options per language
VOICE_MAPPING = {
    'fr': ["fr-FR-HenriNeural", "fr-FR-DeniseNeural", "fr-FR-BrigitteNeural", "fr-FR-AlainNeural", "fr-FR-EloiseNeural"],
    'en': ["en-US-GuyNeural", "en-US-JennyNeural", "en-US-AriaNeural", "en-GB-SoniaNeural", "en-GB-RyanNeural"],
    'es': ["es-ES-AlvaroNeural", "es-ES-ElviraNeural", "es-ES-AbrilNeural", "es-MX-JorgeNeural", "es-MX-DaliaNeural"],
    'de': ["de-DE-KillianNeural", "de-DE-KatjaNeural", "de-DE-ConradNeural", "de-AT-JonasNeural", "de-CH-LeniNeural"],
    'it': ["it-IT-DiegoNeural", "it-IT-ElsaNeural", "it-IT-IsabellaNeural", "it-IT-BenignoNeural", "it-IT-CalimeroNeural"],
    'ja': ["ja-JP-KeitaNeural", "ja-JP-NanamiNeural", "ja-JP-DaichiNeural", "ja-JP-ShioriNeural", "ja-JP-AoiNeural"],
    'zh': ["zh-CN-YunxiNeural", "zh-CN-XiaoxiaoNeural", "zh-CN-YunjianNeural", "zh-TW-YunJheNeural", "zh-CN-XiaoyiNeural"],
    'ar': ["ar-SA-ZariyahNeural", "ar-SA-HamedNeural", "ar-SA-NaayfNeural", "ar-EG-SalmaNeural", "ar-AE-FatimaNeural"],
    'pt': ["pt-BR-FranciscaNeural", "pt-PT-DuarteNeural", "pt-BR-AntonioNeural", "pt-PT-RaquelNeural", "pt-BR-BrendaNeural"],
    'ru': ["ru-RU-DmitryNeural", "ru-RU-SvetlanaNeural", "ru-RU-DariyaNeural", "ru-RU-DmitryNeural", "ru-RU-DariyaNeural"],
    'ko': ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural", "ko-KR-JiMinNeural", "ko-KR-YuJinNeural", "ko-KR-GookMinNeural"]
}

# Premium voices for ElevenLabs (if available)
ELEVENLABS_VOICES = {
    'en': ["Adam", "Domi", "Bella", "Antoni", "Thomas"],
    'fr': ["Rémi", "Charlotte", "Jean", "Sophie", "Louis"],
    'es': ["Miguel", "Valentina", "Javier", "Lucia", "Carlos"],
    'de': ["Klaus", "Helga", "Hans", "Greta", "Friedrich"],
    'it': ["Marco", "Giulia", "Lorenzo", "Isabella", "Francesco"],
}

class AudioEngine:
    """Enhanced audio engine with multiple TTS options and fallbacks"""
    
    def __init__(self, language='en', voice_index=0, premium=False):
        self.language = language
        self.voice_index = voice_index
        self.use_premium = premium and elevenlabs_available
        self.tts_service = "elevenlabs" if self.use_premium else "edge-tts"
        self.fallback_chain = ["edge-tts", "gtts"]
    
    async def _generate_edge_tts_audio(self, text, output_file):
        """Generate audio with Edge TTS"""
        try:
            voices = VOICE_MAPPING.get(self.language, ["en-US-GuyNeural"])
            voice = voices[self.voice_index % len(voices)]
            
            if not text or text.isspace():
                logger.error(f"Error: Text for speech synthesis is empty.")
                return False
            
            logger.info(f"Generating audio with {voice}, language: {self.language}")
            
            # Create a Communicate with explicit parameters
            communicate = edge_tts.Communicate(text, voice, rate="+0%", volume="+0%")
            await communicate.save(output_file)
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                logger.info(f"Edge TTS audio file generated: {output_file}")
                time.sleep(1)  # Pause for file finalization
                return True
            else:
                logger.error(f"Edge TTS failed: No file generated at {output_file} or file is empty.")
                return False
                
        except Exception as e:
            logger.error(f"Edge TTS error with voice {voice}: {str(e)}")
            return False
    
    def _generate_elevenlabs_audio(self, text, output_file):
        """Generate audio with ElevenLabs premium voices"""
        try:
            if not elevenlabs_available:
                logger.warning("ElevenLabs not available, skipping premium voice")
                return False
                
            voices = ELEVENLABS_VOICES.get(self.language, ELEVENLABS_VOICES['en'])
            voice = voices[self.voice_index % len(voices)]
            
            logger.info(f"Generating audio with ElevenLabs voice: {voice}")
            
            audio = generate(
                text=text,
                voice=voice,
                model="eleven_multilingual_v2"
            )
            
            with open(output_file, "wb") as f:
                f.write(audio)
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                logger.info(f"ElevenLabs audio file generated: {output_file}")
                return True
            else:
                logger.error(f"ElevenLabs failed: No file generated or file is empty.")
                return False
                
        except Exception as e:
            logger.error(f"ElevenLabs error: {str(e)}")
            return False
    
    def _generate_gtts_audio(self, text, output_file):
        """Generate audio with Google TTS"""
        try:
            # Map our language codes to gTTS language codes
            gtts_lang = self.language
            if self.language == 'zh':
                gtts_lang = 'zh-CN'
            elif self.language == 'ar':
                gtts_lang = 'ar'
                
            logger.info(f"Generating audio with gTTS, language: {gtts_lang}")
            
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(output_file)
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                logger.info(f"gTTS audio file generated: {output_file}")
                return True
            else:
                logger.error(f"gTTS failed: No file generated or file is empty.")
                return False
                
        except Exception as e:
            logger.error(f"gTTS error: {str(e)}")
            return False
    
    async def generate_audio(self, text, output_file):
        """Generate audio using the preferred service with fallbacks"""
        if self.use_premium:
            # Try ElevenLabs first
            success = self._generate_elevenlabs_audio(text, output_file)
            if success:
                return True
                
            # If ElevenLabs fails, continue with fallbacks
            logger.warning("Premium voice generation failed, falling back to standard voices")
        
        # Try Edge TTS
        success = await self._generate_edge_tts_audio(text, output_file)
        if success:
            return True
            
        # Try gTTS as final fallback
        logger.warning("Edge TTS failed, falling back to gTTS")
        return self._generate_gtts_audio(text, output_file)

def clean_text_for_tts(text, language='en'):
    """
    Clean and prepare text for text-to-speech synthesis
    
    Args:
        text (str): Text to clean
        language (str): Language code
        
    Returns:
        str: Cleaned text optimized for TTS
    """
    if not text:
        logger.error("Error: Provided text is empty.")
        return ""
    
    # Replace markdown headings with pauses and emphasis
    text = re.sub(r'#{1,6}\s+(.+)', r'... \1 ...', text)
    
    # Remove bullets and list numbers
    text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Convert numbers to words based on language
    def replace_number(match):
        try:
            num = int(match.group(0))
            # Use English for languages not supported by num2words
            fallback_langs = ['ar', 'zh', 'ko', 'ja']
            target_lang = 'en' if language in fallback_langs else language
            
            # Handle large numbers specially
            if num > 1000000:
                # For millions and billions, don't convert the full number
                if num % 1000000 == 0:
                    millions = num // 1000000
                    return f"{num2words(millions, lang=target_lang)} million"
                else:
                    # For complex large numbers, keep as digits
                    return str(num)
            else:
                return num2words(num, lang=target_lang)
        except:
            return str(num)
    
    text = re.sub(r'\b\d+\b', replace_number, text)
    
    # Replace common abbreviations and symbols
    abbreviations = {
        'e.g.': 'for example',
        'i.e.': 'that is',
        'etc.': 'etcetera',
        'vs.': 'versus',
        '%': 'percent',
        '&': 'and',
        '=': 'equals',
        '+': 'plus',
        '-': 'minus',
        '*': 'times',
        '/': 'divided by',
    }
    
    for abbr, replacement in abbreviations.items():
        text = text.replace(abbr, replacement)
    
    # Add pauses for better rhythm (using commas and periods)
    text = re.sub(r'([.!?])\s+', r'\1 ... ', text)
    text = re.sub(r'[:;]\s+', r', ', text)
    
    # Remove URLs and replace with placeholder
    text = re.sub(r'https?://\S+', 'link', text)
    
    # Remove special characters that TTS engines might struggle with
    text = re.sub(r'[#*_~`]', '', text)
    
    # For languages with special needs
    if language == 'ar':
        # Keep Arabic characters, spaces, and basic punctuation
        text = re.sub(r'[^\u0600-\u06FF\u0660-\u0669\s.,!?]', '', text)
    elif language in ['zh', 'ja', 'ko']:
        # Add pauses between sentences for better rhythm in Asian languages
        text = re.sub(r'([。！？，])', r'\1 ... ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Add final check for empty text
    if not text:
        logger.error("Error: Cleaned text is empty after processing.")
        return "Default text for speech synthesis."
    
    return text

def enhance_audio(input_file, output_file=None, normalize=True, adjust_speed=1.0, add_fade=True):
    """
    Enhance the audio with post-processing effects
    
    Args:
        input_file (str): Path to input audio file
        output_file (str, optional): Path to save enhanced audio
        normalize (bool): Whether to normalize audio levels
        adjust_speed (float): Speed adjustment factor
        add_fade (bool): Whether to add fade in/out effects
        
    Returns:
        str: Path to enhanced audio file
    """
    if output_file is None:
        output_file = input_file
    
    try:
        # Load audio file
        audio = AudioSegment.from_file(input_file)
        
        # Apply normalization
        if normalize:
            audio = effects.normalize(audio)
        
        # Adjust speed (without changing pitch)
        if adjust_speed != 1.0:
            # This is a simple approach - for better results would need more complex processing
            sound_with_altered_frame_rate = audio._spawn(
                audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * adjust_speed)}
            )
            audio = sound_with_altered_frame_rate.set_frame_rate(audio.frame_rate)
        
        # Add fade in/out
        if add_fade and len(audio) > 2000:  # Only if audio is longer than 2 seconds
            fade_duration = min(500, len(audio) // 10)  # 500ms or 10% of audio, whichever is shorter
            audio = audio.fade_in(fade_duration).fade_out(fade_duration)
        
        # Export enhanced audio
        audio.export(output_file, format=os.path.splitext(output_file)[1][1:])
        logger.info(f"Enhanced audio saved to: {output_file}")
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error enhancing audio: {e}")
        return input_file

def generate_audio(text, title, language='en', voice_index=0, premium=False, format=DEFAULT_AUDIO_FORMAT):
    """
    Generate audio from text with caching and enhanced options
    
    Args:
        text (str): Text content to convert to speech
        title (str): Title of the audio (used for intro and filename)
        language (str): Language code
        voice_index (int): Index of voice to use
        premium (bool): Whether to use premium voices
        format (str): Audio format (mp3, ogg, wav)
        
    Returns:
        str: Path to the generated audio file or None if generation failed
    """
    try:
        # Clean title and text
        cleaned_title = clean_text_for_tts(title, language)
        cleaned_text = clean_text_for_tts(text, language)
        
        if not cleaned_text or not cleaned_title:
            logger.error("Error: Cleaned text or title is empty after processing.")
            return None
        
        # Add pause after title and introduction
        full_text = f"{cleaned_title}. ... {cleaned_text}"
        
        # Create content hash for caching
        content_hash = hashlib.md5((full_text + language + str(voice_index) + str(premium)).encode()).hexdigest()
        
        # Check format
        if format not in AUDIO_FORMATS:
            format = DEFAULT_AUDIO_FORMAT
        
        # Create unique filename
        filename = f"{uuid.uuid4()}.{format}"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        # Check for cached version to avoid regeneration
        cache_key = f"{content_hash}.{format}"
        cache_path = os.path.join(CACHE_DIR, cache_key)
        
        if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
            logger.info(f"Using cached audio: {cache_path}")
            # Copy the cached file to the new location
            import shutil
            shutil.copy2(cache_path, filepath)
            return filepath
        
        # Create AudioEngine instance
        engine = AudioEngine(language, voice_index, premium)
        
        # Generate audio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(engine.generate_audio(full_text, filepath))
        loop.close()
        
        if not success:
            logger.error("All audio generation methods failed.")
            return None
        
        # Enhance audio quality
        enhance_audio(filepath, normalize=True, add_fade=True)
        
        # Compress audio if enabled
        if AUDIO_COMPRESSION:
            compress_audio(filepath, bitrate=AUDIO_COMPRESSION_BITRATE)
        
        # Cache the successful audio file
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            import shutil
            shutil.copy2(filepath, cache_path)
            logger.info(f"Audio cached at: {cache_path}")
        
        return filepath
            
    except Exception as e:
        logger.error(f"Critical error during audio generation: {str(e)}")
        return None
    
def get_audio_duration(filepath):
    """
    Get the duration of an audio file in seconds
    
    Args:
        filepath (str): Path to the audio file
        
    Returns:
        float: Duration in seconds
    """
    try:
        if os.path.exists(filepath):
            # Try to get actual duration with pydub
            try:
                audio = AudioSegment.from_file(filepath)
                return audio.duration_seconds
            except:
                # Fallback to estimate based on file size
                file_size_kb = os.path.getsize(filepath) / 1024
                estimated_duration = file_size_kb / 10
                return max(estimated_duration, 10)
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
    
    return 300  # Default 5 minutes

def compress_audio(input_path, output_path=None, bitrate="128k"):
    """
    Compress an audio file to reduce size while maintaining acceptable quality
    
    Args:
        input_path (str): Path to input audio file
        output_path (str, optional): Path to save compressed file. If None, overwrites input
        bitrate (str): Target bitrate for compression
        
    Returns:
        str: Path to compressed audio file
    """
    if not output_path:
        output_path = input_path
        
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format=os.path.splitext(output_path)[1][1:], bitrate=bitrate)
        logger.info(f"Compressed audio: {input_path} -> {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error compressing audio: {e}")
        return input_path

def convert_audio_format(input_path, output_format=DEFAULT_AUDIO_FORMAT):
    """
    Convert audio to a different format
    
    Args:
        input_path (str): Path to input audio file
        output_format (str): Target format (mp3, ogg, wav)
        
    Returns:
        str: Path to converted audio file
    """
    if output_format not in AUDIO_FORMATS:
        output_format = DEFAULT_AUDIO_FORMAT
        
    try:
        output_path = os.path.splitext(input_path)[0] + f".{output_format}"
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format=output_format)
        logger.info(f"Converted audio: {input_path} -> {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error converting audio format: {e}")
        return input_path

def generate_waveform_data(audio_path, num_points=100):
    """
    Generate waveform data for visualization
    
    Args:
        audio_path (str): Path to audio file
        num_points (int): Number of data points to generate
        
    Returns:
        list: List of amplitude values for waveform visualization
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        
        # Get raw audio data
        samples = audio.get_array_of_samples()
        
        # Calculate step size to get desired number of points
        step = len(samples) // num_points
        
        # Extract sample points
        waveform = []
        for i in range(0, len(samples), step):
            if len(waveform) >= num_points:
                break
            # Normalize to range between 0 and 1
            value = abs(samples[i]) / 32767.0  # Assuming 16-bit audio
            waveform.append(float(value))
        
        return waveform
    except Exception as e:
        logger.error(f"Error generating waveform data: {e}")
        return [0] * num_points

def get_available_voices(language=None):
    """
    Get list of available voices for a language
    
    Args:
        language (str, optional): Language code. If None, returns all voices
        
    Returns:
        dict: Dictionary of available voices
    """
    voices = {}
    
    # Add standard voices
    for lang, voice_list in VOICE_MAPPING.items():
        if language is None or lang == language:
            voices[lang] = {
                "standard": voice_list
            }
    
    # Add premium voices if available
    if elevenlabs_available:
        for lang, voice_list in ELEVENLABS_VOICES.items():
            if language is None or lang == language:
                if lang in voices:
                    voices[lang]["premium"] = voice_list
                else:
                    voices[lang] = {
                        "premium": voice_list
                    }
    
    return voices