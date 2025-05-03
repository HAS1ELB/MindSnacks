import json
import os
import time

class UserSession:
    """
    Gère les données de session utilisateur, y compris l'historique des snippets et des préférences.
    """
    def __init__(self):
        self.snippets = []
        self.history = []
        self.preferences = {
            "favorite_topics": [],
            "last_viewed": None,
            "language": "fr"  # Langue par défaut
        }
    
    def add_snippet(self, snippet):
        """
        Ajoute un snippet à la liste des snippets de l'utilisateur.
        """
        self.snippets.append(snippet)
        self.history.append(snippet["topic"])
        
        # Limiter l'historique aux 20 derniers sujets
        if len(self.history) > 20:
            self.history = self.history[-20:]
    
    def get_recent_topics(self, count=5):
        """
        Récupère les sujets récemment consultés par l'utilisateur.
        """
        return self.history[-count:] if self.history else []
    
    def add_favorite_topic(self, topic):
        """
        Ajoute un sujet aux favoris de l'utilisateur.
        """
        if topic not in self.preferences["favorite_topics"]:
            self.preferences["favorite_topics"].append(topic)
    
    def get_playlist(self):
        """
        Récupère la playlist complète de l'utilisateur.
        """
        return self.snippets
    
    def set_language(self, language):
        """
        Définit la langue préférée de l'utilisateur.
        """
        self.preferences["language"] = language

def save_audio_metadata(snippet_id, audio_path, duration):
    """
    Sauvegarde les métadonnées d'un fichier audio.
    """
    metadata = {
        "snippet_id": snippet_id,
        "path": audio_path,
        "duration": duration,
        "created_at": time.time()
    }
    
    metadata_path = f"{audio_path}.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    
    return metadata