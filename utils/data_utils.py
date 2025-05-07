import json
import os
import time
import datetime
import logging
import uuid
import hashlib
import shutil
import pickle
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from config import (
    ANALYTICS_DIR, USER_DATA_DIR, CACHE_DIR, 
    EXPORT_DIR, POINTS, ACHIEVEMENTS,
    FIREBASE_CONFIG, JWT_SECRET, JWT_EXPIRY, CACHE_TTL
)

logger = logging.getLogger(__name__)

# Try to import Firebase if configured
firebase_admin_available = False
if FIREBASE_CONFIG:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, auth
        firebase_admin_available = True
    except ImportError:
        logger.warning("Firebase admin SDK not available. Install with 'pip install firebase-admin'")

# Try to import JWT for token generation
jwt_available = False
try:
    import jwt
    jwt_available = True
except ImportError:
    logger.warning("PyJWT not available. User tokens will not be generated.")

class MemoryCache:
    """In-memory cache with TTL support"""
    
    def __init__(self, ttl=CACHE_TTL):
        self.cache = {}
        self.ttl = ttl
        
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                # Expired
                del self.cache[key]
        return None
        
    def set(self, key, value, ttl=None):
        if ttl is None:
            ttl = self.ttl
        self.cache[key] = (value, time.time())
        
    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
            
    def clear(self):
        self.cache.clear()

# Global cache instance
memory_cache = MemoryCache()

class UserSession:
    """
    Enhanced user session management with authentication, cloud sync,
    and advanced analytics
    """
    def __init__(self, session_id=None, user_id=None):
        self.snippets = []
        self.history = []
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.start_time = time.time()
        self.preferences = {
            "favorite_topics": [],
            "language": "en",  # Default language
            "theme": "dark",   # Default theme
            "playback_speed": 1.0,  # Default playback speed
            "auto_play": False,  # Default auto-play setting
            "premium_voices": False,  # Default to standard voices
            "notifications": True,  # Enable notifications by default
            "learning_reminders": False,  # Learning reminders off by default
            "voice_index": 0,  # Default voice index
            "quiz_difficulty": "medium",  # Default quiz difficulty
        }
        self.analytics = {
            "topics_viewed": {},
            "session_duration": 0,
            "languages_used": {},
            "playlist_count": 0,
            "last_activity": time.time(),
            "daily_streak": 0,
            "last_login_date": datetime.date.today().isoformat(),
            "quiz_scores": [],
            "topics_completed": 0,
            "total_learning_time": 0,
        }
        self.achievements = []
        self.points = 0
        self.is_authenticated = False
        self.is_premium = False
        self.firebase_user = None
        
        # Attempt to load user data if user_id provided
        if self.user_id:
            self.load_user_data()
        
    def add_snippet(self, snippet):
        """
        Add a snippet to the user's snippet list and update history
        
        Args:
            snippet (dict): The snippet to add
        """
        # Check if snippet already exists
        existing_ids = [s["id"] for s in self.snippets]
        if snippet["id"] in existing_ids:
            logger.warning(f"Snippet with ID {snippet['id']} already exists, not adding duplicate")
            return False
            
        self.snippets.append(snippet)
        topic = snippet.get("topic", "unknown")
        self.history.append(topic)
        
        # Update analytics
        self.analytics["last_activity"] = time.time()
        self.analytics["topics_viewed"][topic] = self.analytics["topics_viewed"].get(topic, 0) + 1
        language = snippet.get("language", "en")
        self.analytics["languages_used"][language] = self.analytics["languages_used"].get(language, 0) + 1
        self.analytics["topics_completed"] += 1
        
        # Add audio duration to total learning time
        if "audio_duration" in snippet:
            self.analytics["total_learning_time"] += snippet["audio_duration"]
        
        # Limit history to the 20 most recent topics
        if len(self.history) > 20:
            self.history = self.history[-20:]
        
        # Award points for creating snippet
        self.add_points("snippet_created")
        
        # Check achievements
        self._check_achievements()
        
        # Log the addition of the snippet
        logger.info(f"Added snippet: {snippet['title']} (ID: {snippet['id']})")
        
        # Save user data if authenticated
        if self.is_authenticated:
            self.save_user_data()
            
        return True
    
    def get_recent_topics(self, count=5):
        """
        Get the most recently viewed topics
        
        Args:
            count (int): Number of topics to retrieve
            
        Returns:
            list: List of recent topics
        """
        return self.history[-count:] if self.history else []
    
    def get_favorite_topics(self):
        """
        Get user's favorite topics
        
        Returns:
            list: List of favorite topics
        """
        return self.preferences["favorite_topics"]
    
    def add_favorite_topic(self, topic):
        """
        Add a topic to user's favorites
        
        Args:
            topic (str): Topic to add to favorites
        """
        if topic not in self.preferences["favorite_topics"]:
            self.preferences["favorite_topics"].append(topic)
            logger.info(f"Added favorite topic: {topic}")
            
            # Save user data if authenticated
            if self.is_authenticated:
                self.save_user_data()
                
            return True
        return False
    
    def remove_favorite_topic(self, topic):
        """
        Remove a topic from user's favorites
        
        Args:
            topic (str): Topic to remove from favorites
        """
        if topic in self.preferences["favorite_topics"]:
            self.preferences["favorite_topics"].remove(topic)
            logger.info(f"Removed favorite topic: {topic}")
            
            # Save user data if authenticated
            if self.is_authenticated:
                self.save_user_data()
                
            return True
        return False
    
    def get_playlist(self):
        """
        Get the complete user playlist
        
        Returns:
            list: List of snippets in the playlist
        """
        return self.snippets
    
    def set_preference(self, key, value):
        """
        Set a user preference
        
        Args:
            key (str): Preference key
            value: Preference value
        """
        if key in self.preferences:
            self.preferences[key] = value
            logger.info(f"Set user preference: {key}={value}")
            
            # Save user data if authenticated
            if self.is_authenticated:
                self.save_user_data()
                
            return True
        return False
    
    def get_preference(self, key, default=None):
        """
        Get a user preference
        
        Args:
            key (str): Preference key
            default: Default value if preference not found
            
        Returns:
            The preference value or default if not found
        """
        return self.preferences.get(key, default)
    
    def remove_snippet(self, snippet_id):
        """
        Remove a snippet from the playlist
        
        Args:
            snippet_id (str): ID of the snippet to remove
            
        Returns:
            bool: True if snippet was removed, False otherwise
        """
        for i, snippet in enumerate(self.snippets):
            if snippet["id"] == snippet_id:
                removed = self.snippets.pop(i)
                logger.info(f"Removed snippet: {removed['title']} (ID: {removed['id']})")
                
                # Save user data if authenticated
                if self.is_authenticated:
                    self.save_user_data()
                    
                return True
        return False
    
    def update_session_analytics(self):
        """
        Update session analytics data
        """
        current_time = time.time()
        self.analytics["session_duration"] = current_time - self.start_time
        self.analytics["last_activity"] = current_time
        
        # Check for daily streak
        today = datetime.date.today().isoformat()
        if self.analytics.get("last_login_date") != today:
            # It's a new day, check if it's consecutive
            last_date = datetime.date.fromisoformat(self.analytics.get("last_login_date", today))
            today_date = datetime.date.today()
            delta = (today_date - last_date).days
            
            if delta == 1:
                # Consecutive day
                self.analytics["daily_streak"] += 1
                self.add_points("daily_login")
                
                # Check for daily streak achievement
                if self.analytics["daily_streak"] >= 7:
                    self._award_achievement("daily_learner")
            elif delta > 1:
                # Streak broken
                self.analytics["daily_streak"] = 1
                
            self.analytics["last_login_date"] = today
    
    def add_points(self, activity_type):
        """
        Add points for user activities
        
        Args:
            activity_type (str): Type of activity to award points for
        """
        if activity_type in POINTS:
            points = POINTS[activity_type]
            self.points += points
            logger.info(f"Added {points} points for {activity_type}. Total: {self.points}")
            return points
        return 0
    
    def _check_achievements(self):
        """Check and award achievements based on current stats"""
        # Check for first snippet achievement
        if len(self.snippets) == 1 and "first_snippet" not in self.achievements:
            self._award_achievement("first_snippet")
        
        # Check for knowledge explorer (5 different topics)
        topics = set(snippet.get("topic", "") for snippet in self.snippets)
        if len(topics) >= 5 and "knowledge_explorer" not in self.achievements:
            self._award_achievement("knowledge_explorer")
        
        # Check for polyglot (used 3 different languages)
        languages = set(snippet.get("language", "") for snippet in self.snippets)
        if len(languages) >= 3 and "polyglot" not in self.achievements:
            self._award_achievement("polyglot")
        
        # Quiz master is checked separately when quiz is completed
    
    def _award_achievement(self, achievement_id):
        """
        Award an achievement to the user
        
        Args:
            achievement_id (str): ID of the achievement to award
        """
        if achievement_id in [a["id"] for a in ACHIEVEMENTS] and achievement_id not in self.achievements:
            # Find achievement details
            achievement = next((a for a in ACHIEVEMENTS if a["id"] == achievement_id), None)
            
            if achievement:
                self.achievements.append(achievement_id)
                # Award points
                self.points += achievement["points"]
                
                logger.info(f"Awarded achievement: {achievement['name']} (+{achievement['points']} points)")
                
                # Return achievement details for notification
                return achievement
        return None
    
    def record_quiz_score(self, topic, score, max_score):
        """
        Record a quiz score
        
        Args:
            topic (str): Quiz topic
            score (int): Score achieved
            max_score (int): Maximum possible score
        """
        quiz_result = {
            "topic": topic,
            "score": score,
            "max_score": max_score,
            "percentage": round((score / max_score) * 100),
            "timestamp": time.time(),
            "date": datetime.datetime.now().isoformat()
        }
        
        self.analytics["quiz_scores"].append(quiz_result)
        
        # Award points
        self.add_points("quiz_completed")
        
        # Check for perfect score and quiz master achievement
        if score == max_score:
            # Count perfect scores
            perfect_scores = sum(1 for q in self.analytics["quiz_scores"] if q["score"] == q["max_score"])
            
            if perfect_scores >= 10 and "quiz_master" not in self.achievements:
                self._award_achievement("quiz_master")
        
        # Save user data if authenticated
        if self.is_authenticated:
            self.save_user_data()
            
        return quiz_result
    
    def save_session(self):
        """
        Save session data to a file
        
        Returns:
            bool: True if successfully saved, False otherwise
        """
        try:
            self.update_session_analytics()
            filename = f"session_{self.session_id}_{int(time.time())}.json"
            filepath = os.path.join(ANALYTICS_DIR, filename)
            
            session_data = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "start_time": self.start_time,
                "end_time": time.time(),
                "preferences": self.preferences,
                "analytics": self.analytics,
                "history": self.history,
                "points": self.points,
                "achievements": self.achievements,
                "snippet_count": len(self.snippets),
                "snippets": [{"id": s["id"], "title": s["title"], "topic": s["topic"], 
                              "language": s["language"]} for s in self.snippets]
            }
            
            with open(filepath, 'w') as f:
                json.dump(session_data, f)
            
            logger.info(f"Session data saved to: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def save_user_data(self):
        """
        Save user data to disk and cloud if authenticated
        
        Returns:
            bool: True if successfully saved, False otherwise
        """
        if not self.user_id:
            logger.warning("Cannot save user data: No user ID provided")
            return False
            
        try:
            self.update_session_analytics()
            
            # Create user data object
            user_data = {
                "user_id": self.user_id,
                "preferences": self.preferences,
                "analytics": self.analytics,
                "history": self.history,
                "points": self.points,
                "achievements": self.achievements,
                "last_updated": time.time(),
                "is_premium": self.is_premium,
                "snippets": self.snippets
            }
            
            # Save to disk
            user_dir = os.path.join(USER_DATA_DIR, self.user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            filepath = os.path.join(user_dir, "user_data.json")
            with open(filepath, 'w') as f:
                json.dump(user_data, f)
                
            # Save to cloud if Firebase available
            if firebase_admin_available and self.firebase_user:
                try:
                    # Get Firestore database
                    db = firestore.client()
                    
                    # Use separate collections for different data
                    db.collection('users').document(self.user_id).set({
                        'preferences': self.preferences,
                        'analytics': self.analytics,
                        'points': self.points,
                        'achievements': self.achievements,
                        'is_premium': self.is_premium,
                        'last_updated': firestore.SERVER_TIMESTAMP
                    })
                    
                    # Store snippets in a subcollection to handle large data
                    snippets_ref = db.collection('users').document(self.user_id).collection('snippets')
                    
                    # Use batch write for efficiency
                    batch = db.batch()
                    for snippet in self.snippets:
                        snippet_ref = snippets_ref.document(snippet['id'])
                        batch.set(snippet_ref, snippet)
                        
                    batch.commit()
                    
                    logger.info(f"User data saved to cloud for user: {self.user_id}")
                    
                except Exception as e:
                    logger.error(f"Error saving user data to cloud: {e}")
            
            logger.info(f"User data saved to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return False
    
    def load_user_data(self):
        """
        Load user data from disk or cloud
        
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        if not self.user_id:
            logger.warning("Cannot load user data: No user ID provided")
            return False
            
        try:
            # Try to load from cache first
            cached_data = memory_cache.get(f"user_data_{self.user_id}")
            if cached_data:
                logger.info(f"Loaded user data from cache for user: {self.user_id}")
                self._apply_user_data(cached_data)
                return True
                
            # Try cloud first if Firebase available
            if firebase_admin_available and self.firebase_user:
                try:
                    db = firestore.client()
                    user_doc = db.collection('users').document(self.user_id).get()
                    
                    if user_doc.exists:
                        user_data = user_doc.to_dict()
                        
                        # Load snippets from subcollection
                        snippets = []
                        snippets_ref = db.collection('users').document(self.user_id).collection('snippets')
                        for snippet_doc in snippets_ref.stream():
                            snippets.append(snippet_doc.to_dict())
                            
                        user_data['snippets'] = snippets
                        
                        # Apply loaded data
                        self._apply_user_data(user_data)
                        
                        # Cache user data
                        memory_cache.set(f"user_data_{self.user_id}", user_data)
                        
                        logger.info(f"Loaded user data from cloud for user: {self.user_id}")
                        return True
                        
                except Exception as e:
                    logger.error(f"Error loading user data from cloud: {e}")
            
            # Try local storage as fallback
            filepath = os.path.join(USER_DATA_DIR, self.user_id, "user_data.json")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    user_data = json.load(f)
                    
                # Apply loaded data
                self._apply_user_data(user_data)
                
                # Cache user data
                memory_cache.set(f"user_data_{self.user_id}", user_data)
                
                logger.info(f"Loaded user data from disk for user: {self.user_id}")
                return True
            
            logger.warning(f"No user data found for user: {self.user_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
            return False
    
    def _apply_user_data(self, user_data):
        """
        Apply loaded user data to the session
        
        Args:
            user_data (dict): User data to apply
        """
        # Apply preferences
        if 'preferences' in user_data:
            self.preferences.update(user_data['preferences'])
            
        # Apply analytics
        if 'analytics' in user_data:
            self.analytics.update(user_data['analytics'])
            
        # Apply history
        if 'history' in user_data:
            self.history = user_data['history']
            
        # Apply points
        if 'points' in user_data:
            self.points = user_data['points']
            
        # Apply achievements
        if 'achievements' in user_data:
            self.achievements = user_data['achievements']
            
        # Apply premium status
        if 'is_premium' in user_data:
            self.is_premium = user_data['is_premium']
            
        # Apply snippets (if present)
        if 'snippets' in user_data:
            self.snippets = user_data['snippets']
    
    def authenticate(self, firebase_user=None):
        """
        Authenticate user session
        
        Args:
            firebase_user: Firebase user object if using Firebase auth
            
        Returns:
            str: Authentication token or None if authentication failed
        """
        if firebase_user:
            self.firebase_user = firebase_user
            self.user_id = firebase_user.uid
            self.is_authenticated = True
            
            # Load user data
            self.load_user_data()
            
            # Generate JWT token if available
            if jwt_available:
                token_data = {
                    "user_id": self.user_id,
                    "email": firebase_user.email,
                    "exp": int(time.time()) + JWT_EXPIRY
                }
                token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")
                return token
                
            return "authenticated"
        
        return None
    
    def logout(self):
        """
        Logout user and save session data
        
        Returns:
            bool: True if logout was successful
        """
        # Save final state
        self.save_session()
        if self.is_authenticated:
            self.save_user_data()
            
        # Clear user data
        self.is_authenticated = False
        self.firebase_user = None
        
        return True
    
    def export_data(self, export_format='json'):
        """
        Export user data
        
        Args:
            export_format (str): Format to export ('json' or 'pickle')
            
        Returns:
            str: Path to exported file
        """
        try:
            # Prepare export data
            export_data = {
                "user_id": self.user_id,
                "preferences": self.preferences,
                "analytics": self.analytics,
                "history": self.history,
                "points": self.points,
                "achievements": self.achievements,
                "snippets": self.snippets,
                "export_date": datetime.datetime.now().isoformat(),
                "app_version": "2.1.0"
            }
            
            # Create export directory
            os.makedirs(EXPORT_DIR, exist_ok=True)
            
            # Generate filename
            timestamp = int(time.time())
            user_identifier = self.user_id if self.user_id else self.session_id
            
            if export_format == 'json':
                filename = f"mindsnacks_export_{user_identifier}_{timestamp}.json"
                filepath = os.path.join(EXPORT_DIR, filename)
                
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2)
                    
            elif export_format == 'pickle':
                filename = f"mindsnacks_export_{user_identifier}_{timestamp}.pkl"
                filepath = os.path.join(EXPORT_DIR, filename)
                
                with open(filepath, 'wb') as f:
                    pickle.dump(export_data, f)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            logger.info(f"Exported user data to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return None
    
    def import_data(self, filepath):
        """
        Import user data from file
        
        Args:
            filepath (str): Path to import file
            
        Returns:
            bool: True if import was successful
        """
        try:
            # Determine format based on file extension
            if filepath.endswith('.json'):
                with open(filepath, 'r') as f:
                    import_data = json.load(f)
            elif filepath.endswith('.pkl'):
                with open(filepath, 'rb') as f:
                    import_data = pickle.load(f)
            else:
                raise ValueError(f"Unsupported import file format: {filepath}")
            
            # Apply imported data
            self._apply_user_data(import_data)
            
            # Save imported data
            if self.is_authenticated:
                self.save_user_data()
                
            logger.info(f"Imported user data from: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing user data: {e}")
            return False

def save_audio_metadata(snippet_id, audio_path, duration):
    """
    Save metadata for an audio file
    
    Args:
        snippet_id (str): ID of the snippet
        audio_path (str): Path to the audio file
        duration (float): Duration of the audio in seconds
        
    Returns:
        dict: Metadata dictionary
    """
    metadata = {
        "snippet_id": snippet_id,
        "path": audio_path,
        "duration": duration,
        "created_at": time.time(),
        "created_date": datetime.datetime.now().isoformat()
    }
    
    metadata_path = f"{audio_path}.json"
    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        logger.info(f"Audio metadata saved: {metadata_path}")
    except Exception as e:
        logger.error(f"Error saving audio metadata: {e}")
    
    return metadata

def track_event(event_name, properties=None):
    """
    Track an analytics event
    
    Args:
        event_name (str): Name of the event
        properties (dict): Properties associated with the event
    """
    try:
        event_data = {
            "event": event_name,
            "timestamp": time.time(),
            "date": datetime.datetime.now().isoformat(),
            "properties": properties or {}
        }
        
        # Create events directory
        os.makedirs(os.path.join(ANALYTICS_DIR, "events"), exist_ok=True)
        
        filename = f"event_{int(time.time())}_{uuid.uuid4().hex[:8]}.json"
        filepath = os.path.join(ANALYTICS_DIR, "events", filename)
        
        with open(filepath, 'w') as f:
            json.dump(event_data, f, indent=2)
        
        logger.debug(f"Event tracked: {event_name}")
        
        # If Firebase available, track event in cloud
        if firebase_admin_available:
            try:
                db = firestore.client()
                db.collection('events').add(event_data)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error tracking event: {e}")

def get_analytics_summary():
    """
    Get a summary of analytics data
    
    Returns:
        dict: Analytics summary
    """
    try:
        events_dir = os.path.join(ANALYTICS_DIR, "events")
        if not os.path.exists(events_dir):
            return {"error": "No analytics data available"}
        
        # Use cached summary if available
        cached_summary = memory_cache.get("analytics_summary")
        if cached_summary:
            return cached_summary
        
        event_files = [f for f in os.listdir(events_dir) if f.endswith('.json')]
        
        # Sort by timestamp in filename
        event_files.sort(reverse=True)
        
        events = []
        for file in event_files[:500]:  # Limit to last 500 events for performance
            try:
                with open(os.path.join(events_dir, file), 'r') as f:
                    events.append(json.load(f))
            except:
                continue
        
        # Analyze events
        event_types = {}
        event_by_day = {}
        popular_topics = {}
        language_usage = {}
        
        for event in events:
            # Count event types
            event_type = event.get("event", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Group by day
            event_date = event.get("date", "")[:10]  # Just the date part
            if event_date:
                event_by_day[event_date] = event_by_day.get(event_date, 0) + 1
                
            # Count popular topics
            properties = event.get("properties", {})
            if event_type == "snippet_created" and "topic" in properties:
                topic = properties["topic"]
                popular_topics[topic] = popular_topics.get(topic, 0) + 1
                
            # Count language usage
            if "language" in properties:
                language = properties["language"]
                language_usage[language] = language_usage.get(language, 0) + 1
        
        # Process data for charts
        days = sorted(list(event_by_day.keys()))
        event_counts = [event_by_day.get(day, 0) for day in days]
        
        # Sort popular topics
        popular_topics_sorted = sorted(
            popular_topics.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Create summary
        summary = {
            "total_events": len(events),
            "event_types": event_types,
            "event_by_day": {
                "days": days,
                "counts": event_counts
            },
            "popular_topics": dict(popular_topics_sorted),
            "language_usage": language_usage,
            "last_event": events[0] if events else None,
            "generated_at": datetime.datetime.now().isoformat()
        }
        
        # Cache summary
        memory_cache.set("analytics_summary", summary, ttl=3600)  # Cache for 1 hour
        
        return summary
    except Exception as e:
        logger.error(f"Error generating analytics summary: {e}")
        return {"error": str(e)}