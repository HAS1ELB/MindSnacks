import os
import uuid
from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY, AUDIO_DIR

# Initialiser le client ElevenLabs
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def generate_audio(text, title):
    """
    Génère un fichier audio à partir d'un texte donné en utilisant ElevenLabs.

    Args:
        text (str): Le texte à convertir en audio
        title (str): Le titre du snippet (utilisé pour le nom de fichier)

    Returns:
        str: Le chemin du fichier audio généré, ou None en cas d'échec
    """
    try:
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        # Générer l'audio depuis ElevenLabs
        audio_stream = client.generate(
            text=f"{title}. {text}",
            voice="Rachel",  # Tu peux changer cette voix ou la rendre dynamique
            model="eleven_monolingual_v1",
            output_format="mp3_44100_128"
        )

        # Combiner les chunks de stream
        audio_bytes = b"".join(audio_stream)

        # Sauvegarder le fichier
        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        return filepath

    except Exception as e:
        print(f"Erreur lors de la génération audio ElevenLabs: {e}")
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
        return len(audio) / 1000.0  # millisecondes → secondes
    except Exception as e:
        print(f"Erreur lors de l'obtention de la durée audio: {e}")
        return 300  # Valeur par défaut : 5 minutes
