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
            "last_viewed": None
        }
    
    def add_snippet(self, snippet):
        """
        Ajoute un snippet à la liste des snippets de l'utilisateur.
        
        Args:
            snippet (dict): Le snippet à ajouter
        """
        self.snippets.append(snippet)
        self.history.append(snippet["topic"])
        
        # Limiter l'historique aux 20 derniers sujets
        if len(self.history) > 20:
            self.history = self.history[-20:]
    
    def get_recent_topics(self, count=5):
        """
        Récupère les sujets récemment consultés par l'utilisateur.
        
        Args:
            count (int): Le nombre de sujets à récupérer
        
        Returns:
            list: Liste des sujets récents
        """
        return self.history[-count:] if self.history else []
    
    def add_favorite_topic(self, topic):
        """
        Ajoute un sujet aux favoris de l'utilisateur.
        
        Args:
            topic (str): Le sujet à ajouter aux favoris
        """
        if topic not in self.preferences["favorite_topics"]:
            self.preferences["favorite_topics"].append(topic)
    
    def get_playlist(self):
        """
        Récupère la playlist complète de l'utilisateur.
        
        Returns:
            list: La liste des snippets de l'utilisateur
        """
        return self.snippets

def save_audio_metadata(snippet_id, audio_path, duration):
    """
    Sauvegarde les métadonnées d'un fichier audio.
    
    Args:
        snippet_id (str): L'ID du snippet associé
        audio_path (str): Le chemin du fichier audio
        duration (float): La durée du fichier audio en secondes
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