from typing import List, Dict, Any, Optional, Tuple
import random
import logging
import json
import os
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logger = logging.getLogger(__name__)

class RecommendationModel:
    """
    Model for generating content recommendations based on user history and preferences
    """
    
    def __init__(self, model_file: Optional[str] = None):
        """
        Initialize recommendation model
        
        Args:
            model_file (str, optional): Path to pre-trained model file
        """
        self.user_vectors = {}
        self.content_vectors = {}
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8,
            stop_words='english'
        )
        
        # Load pre-trained model if provided
        if model_file and os.path.exists(model_file):
            self.load_model(model_file)
    
    def train(self, content_items: List[Dict[str, Any]], user_histories: Dict[str, List[str]]):
        """
        Train the recommendation model
        
        Args:
            content_items (list): List of content items with 'id', 'title', 'content', 'topic'
            user_histories (dict): Dict mapping user IDs to lists of content IDs they've interacted with
        """
        try:
            # Convert content items to documents for vectorization
            content_docs = {}
            content_ids = []
            documents = []
            
            for item in content_items:
                item_id = item.get('id')
                if not item_id:
                    continue
                
                # Combine text fields for better representation
                doc = f"{item.get('title', '')} {item.get('topic', '')} {item.get('content', '')}"
                content_docs[item_id] = doc
                content_ids.append(item_id)
                documents.append(doc)
            
            # Fit vectorizer on all documents
            if documents:
                X = self.vectorizer.fit_transform(documents)
                
                # Create content vectors
                for i, item_id in enumerate(content_ids):
                    self.content_vectors[item_id] = X[i]
                
                # Generate user vectors based on their history
                for user_id, history in user_histories.items():
                    self._update_user_vector(user_id, history)
                
                logger.info(f"Trained recommendation model with {len(content_items)} items and {len(user_histories)} users")
            else:
                logger.warning("No documents provided for training")
        
        except Exception as e:
            logger.error(f"Error training recommendation model: {e}")
    
    def update(self, user_id: str, content_id: str, interaction_type: str = 'view'):
        """
        Update model with a new user interaction
        
        Args:
            user_id (str): User ID
            content_id (str): Content ID
            interaction_type (str): Type of interaction ('view', 'like', 'dislike', etc.)
        """
        try:
            # Get user history
            if user_id not in self.user_vectors:
                self._update_user_vector(user_id, [content_id])
            else:
                # Add to user history and update vector
                history = self._get_user_history(user_id)
                
                # Add new interaction if not already in history
                if content_id not in history:
                    history.append(content_id)
                    self._update_user_vector(user_id, history)
            
            logger.debug(f"Updated user vector for {user_id} with {content_id}")
        
        except Exception as e:
            logger.error(f"Error updating recommendation model: {e}")
    
    def recommend(self, user_id: str, num_recommendations: int = 5, 
                 exclude_ids: Optional[List[str]] = None) -> List[str]:
        """
        Generate recommendations for a user
        
        Args:
            user_id (str): User ID
            num_recommendations (int): Number of recommendations to generate
            exclude_ids (list, optional): List of content IDs to exclude
            
        Returns:
            list: List of recommended content IDs
        """
        try:
            if user_id not in self.user_vectors:
                # No user data, return random recommendations
                return self._random_recommendations(num_recommendations, exclude_ids)
            
            # Get user vector
            user_vector = self.user_vectors[user_id]
            
            # Calculate similarity scores with all content items
            scores = []
            for content_id, content_vector in self.content_vectors.items():
                # Skip if in exclude list
                if exclude_ids and content_id in exclude_ids:
                    continue
                
                # Calculate similarity score
                similarity = cosine_similarity(user_vector, content_vector)[0][0]
                scores.append((content_id, similarity))
            
            # Sort by similarity score and get top N
            scores.sort(key=lambda x: x[1], reverse=True)
            recommendations = [content_id for content_id, _ in scores[:num_recommendations]]
            
            logger.debug(f"Generated {len(recommendations)} recommendations for user {user_id}")
            
            # If not enough recommendations, add some random ones
            if len(recommendations) < num_recommendations:
                additional = self._random_recommendations(
                    num_recommendations - len(recommendations),
                    exclude_ids + recommendations if exclude_ids else recommendations
                )
                recommendations.extend(additional)
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._random_recommendations(num_recommendations, exclude_ids)
    
    def recommend_similar(self, content_id: str, num_recommendations: int = 5,
                        exclude_ids: Optional[List[str]] = None) -> List[str]:
        """
        Find similar content to a given item
        
        Args:
            content_id (str): Content ID to find similar items for
            num_recommendations (int): Number of recommendations to generate
            exclude_ids (list, optional): List of content IDs to exclude
            
        Returns:
            list: List of similar content IDs
        """
        try:
            if content_id not in self.content_vectors:
                # Content not found, return random recommendations
                return self._random_recommendations(num_recommendations, exclude_ids)
            
            # Get content vector
            content_vector = self.content_vectors[content_id]
            
            # Calculate similarity scores with all other content items
            scores = []
            for other_id, other_vector in self.content_vectors.items():
                # Skip if same item or in exclude list
                if other_id == content_id:
                    continue
                
                if exclude_ids and other_id in exclude_ids:
                    continue
                
                # Calculate similarity score
                similarity = cosine_similarity(content_vector, other_vector)[0][0]
                scores.append((other_id, similarity))
            
            # Sort by similarity score and get top N
            scores.sort(key=lambda x: x[1], reverse=True)
            recommendations = [content_id for content_id, _ in scores[:num_recommendations]]
            
            logger.debug(f"Generated {len(recommendations)} similar items to {content_id}")
            
            # If not enough recommendations, add some random ones
            if len(recommendations) < num_recommendations:
                additional = self._random_recommendations(
                    num_recommendations - len(recommendations),
                    exclude_ids + recommendations if exclude_ids else recommendations
                )
                recommendations.extend(additional)
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error finding similar content: {e}")
            return self._random_recommendations(num_recommendations, exclude_ids)
    
    def save_model(self, model_file: str):
        """
        Save model to file
        
        Args:
            model_file (str): Path to save model file
        """
        try:
            # Convert sparse matrices to lists for serialization
            serializable_content_vectors = {}
            for content_id, vector in self.content_vectors.items():
                serializable_content_vectors[content_id] = vector.toarray().tolist()[0]
            
            serializable_user_vectors = {}
            for user_id, vector in self.user_vectors.items():
                serializable_user_vectors[user_id] = vector.toarray().tolist()[0]
            
            # Create model data
            model_data = {
                'content_vectors': serializable_content_vectors,
                'user_vectors': serializable_user_vectors,
                'vectorizer_vocabulary': self.vectorizer.vocabulary_,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to file
            with open(model_file, 'w') as f:
                json.dump(model_data, f)
            
            logger.info(f"Saved recommendation model to {model_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving recommendation model: {e}")
            return False
    
    def load_model(self, model_file: str):
        """
        Load model from file
        
        Args:
            model_file (str): Path to model file
        """
        try:
            with open(model_file, 'r') as f:
                model_data = json.load(f)
            
            # Load vectorizer vocabulary
            self.vectorizer = TfidfVectorizer(vocabulary=model_data.get('vectorizer_vocabulary', {}))
            
            # Load content vectors
            self.content_vectors = {}
            for content_id, vector_list in model_data.get('content_vectors', {}).items():
                self.content_vectors[content_id] = np.array([vector_list])
            
            # Load user vectors
            self.user_vectors = {}
            for user_id, vector_list in model_data.get('user_vectors', {}).items():
                self.user_vectors[user_id] = np.array([vector_list])
            
            logger.info(f"Loaded recommendation model from {model_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading recommendation model: {e}")
            return False
    
    def _update_user_vector(self, user_id: str, history: List[str]):
        """
        Update user vector based on interaction history
        
        Args:
            user_id (str): User ID
            history (list): List of content IDs the user has interacted with
        """
        try:
            # Get content vectors for items in history
            history_vectors = []
            for content_id in history:
                if content_id in self.content_vectors:
                    history_vectors.append(self.content_vectors[content_id])
            
            if history_vectors:
                # Combine vectors (average)
                user_vector = sum(history_vectors) / len(history_vectors)
                self.user_vectors[user_id] = user_vector
            else:
                logger.warning(f"No valid content vectors found for user {user_id}'s history")
        
        except Exception as e:
            logger.error(f"Error updating user vector: {e}")
    
    def _get_user_history(self, user_id: str) -> List[str]:
        """
        Get user interaction history (this is a placeholder - in a real system, 
        this would retrieve from a database)
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of content IDs the user has interacted with
        """
        # This is just a placeholder implementation
        # In a real system, this would retrieve from a database
        return []
    
    def _random_recommendations(self, num_recommendations: int, exclude_ids: Optional[List[str]] = None) -> List[str]:
        """
        Generate random recommendations
        
        Args:
            num_recommendations (int): Number of recommendations to generate
            exclude_ids (list, optional): List of content IDs to exclude
            
        Returns:
            list: List of random content IDs
        """
        # Get all available content IDs
        all_ids = list(self.content_vectors.keys())
        
        # Remove excluded IDs
        if exclude_ids:
            all_ids = [cid for cid in all_ids if cid not in exclude_ids]
        
        # Get random selection
        if all_ids:
            return random.sample(all_ids, min(num_recommendations, len(all_ids)))
        else:
            return []

# Create singleton instance
recommendation_model = RecommendationModel()