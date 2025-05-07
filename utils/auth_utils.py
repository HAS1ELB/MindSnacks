import os
import time
import json
import uuid
import logging
import streamlit as st
import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET, JWT_EXPIRY, USER_DATA_DIR, FIREBASE_CONFIG

# Configure logging
logger = logging.getLogger(__name__)

# Try to import firebase if configured
firebase_auth = None
if FIREBASE_CONFIG:
    try:
        import firebase_admin
        from firebase_admin import credentials, auth
        
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_CONFIG)
            firebase_admin.initialize_app(cred)
        
        firebase_auth = auth
        logger.info("Firebase authentication initialized")
    except ImportError:
        logger.warning("Firebase admin SDK not installed. Install with: pip install firebase-admin")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")

class UserManager:
    """User authentication and profile management"""
    
    def __init__(self):
        self.user_data_dir = USER_DATA_DIR
        os.makedirs(self.user_data_dir, exist_ok=True)
    
    def create_user(self, username, email, password=None, provider="local"):
        """
        Create a new user
        
        Args:
            username (str): Username
            email (str): Email address
            password (str, optional): Password (not stored directly)
            provider (str): Authentication provider
            
        Returns:
            dict: User profile
        """
        user_id = str(uuid.uuid4())
        
        # Check if username or email already exists
        if self._username_exists(username):
            logger.warning(f"Username already exists: {username}")
            return None
            
        if self._email_exists(email):
            logger.warning(f"Email already exists: {email}")
            return None
        
        # Create user profile
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "provider": provider,
            "created_at": time.time(),
            "last_login": time.time(),
            "preferences": {
                "language": st.session_state.get("language", "en"),
                "theme": st.session_state.get("theme", "dark"),
                "voice_index": 0,
                "premium_voice": False
            },
            "stats": {
                "snippets_created": 0,
                "snippets_listened": 0,
                "quizzes_taken": 0,
                "points": 0,
                "achievements": []
            }
        }
        
        # Save user profile
        self._save_user(user)
        logger.info(f"Created new user: {username}")
        
        return user
    
    def _save_user(self, user):
        """Save user profile"""
        user_file = os.path.join(self.user_data_dir, f"{user['id']}.json")
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
    
    def _username_exists(self, username):
        """Check if username already exists"""
        for filename in os.listdir(self.user_data_dir):
            if filename.endswith('.json'):
                user_file = os.path.join(self.user_data_dir, filename)
                try:
                    with open(user_file, 'r') as f:
                        user = json.load(f)
                        if user.get('username') == username:
                            return True
                except:
                    pass
        return False
    
    def _email_exists(self, email):
        """Check if email already exists"""
        for filename in os.listdir(self.user_data_dir):
            if filename.endswith('.json'):
                user_file = os.path.join(self.user_data_dir, filename)
                try:
                    with open(user_file, 'r') as f:
                        user = json.load(f)
                        if user.get('email') == email:
                            return True
                except:
                    pass
        return False
    
    def get_user(self, user_id):
        """Get user profile by ID"""
        user_file = os.path.join(self.user_data_dir, f"{user_id}.json")
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to get user {user_id}: {e}")
        return None
    
    def get_user_by_email(self, email):
        """Get user profile by email"""
        for filename in os.listdir(self.user_data_dir):
            if filename.endswith('.json'):
                user_file = os.path.join(self.user_data_dir, filename)
                try:
                    with open(user_file, 'r') as f:
                        user = json.load(f)
                        if user.get('email') == email:
                            return user
                except:
                    pass
        return None
    
    def update_user(self, user_id, updates):
        """Update user profile"""
        user = self.get_user(user_id)
        if user:
            # Update user data
            for key, value in updates.items():
                if key in user:
                    if isinstance(user[key], dict) and isinstance(value, dict):
                        # Merge dictionaries for nested objects
                        user[key].update(value)
                    else:
                        user[key] = value
            
            # Save updated profile
            self._save_user(user)
            logger.info(f"Updated user: {user_id}")
            return user
        return None
    
    def authenticate(self, email, password):
        """
        Authenticate user with email and password
        
        Args:
            email (str): Email address
            password (str): Password
            
        Returns:
            dict: User profile if authentication successful, None otherwise
        """
        # In a real system, we would validate the password hash
        # For this demo, we'll just check if the user exists
        user = self.get_user_by_email(email)
        if user:
            # Update last login
            user['last_login'] = time.time()
            self._save_user(user)
            logger.info(f"User authenticated: {email}")
            return user
        return None
    
    def generate_token(self, user_id):
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRY)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        return token
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = payload.get('user_id')
            return self.get_user(user_id)
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
        return None
    
    def award_points(self, user_id, action, extra_points=0):
        """
        Award points to user for actions
        
        Args:
            user_id (str): User ID
            action (str): Action name (from config.POINTS)
            extra_points (int): Additional points to award
            
        Returns:
            int: New points total
        """
        from config import POINTS
        
        user = self.get_user(user_id)
        if not user:
            return 0
        
        # Get points for action
        points = POINTS.get(action, 0) + extra_points
        
        if points > 0:
            # Update user stats
            current_points = user['stats'].get('points', 0)
            user['stats']['points'] = current_points + points
            
            # Save user profile
            self._save_user(user)
            logger.info(f"Awarded {points} points to user {user_id} for {action}")
            
            # Check for achievements
            self._check_achievements(user_id)
            
            return user['stats']['points']
        
        return user['stats'].get('points', 0)
    
    def _check_achievements(self, user_id):
        """Check and award achievements"""
        from config import ACHIEVEMENTS
        
        user = self.get_user(user_id)
        if not user:
            return
        
        # Get current achievements
        current_achievements = user['stats'].get('achievements', [])
        new_achievements = []
        
        # Check each achievement
        for achievement in ACHIEVEMENTS:
            # Skip already earned achievements
            if achievement['id'] in [a['id'] for a in current_achievements]:
                continue
            
            # Check achievement conditions
            if achievement['id'] == 'first_snippet' and user['stats'].get('snippets_created', 0) >= 1:
                new_achievements.append(achievement)
                
            elif achievement['id'] == 'knowledge_explorer':
                # Count unique topics
                # This would require tracking topic history
                pass
                
            elif achievement['id'] == 'polyglot':
                # This would require tracking language history
                pass
                
            elif achievement['id'] == 'quiz_master' and user['stats'].get('quizzes_taken', 0) >= 10:
                new_achievements.append(achievement)
                
            elif achievement['id'] == 'daily_learner':
                # This would require tracking daily login streak
                pass
        
        # Award achievements
        if new_achievements:
            # Add new achievements
            user['stats']['achievements'].extend(new_achievements)
            
            # Award points
            total_points = sum(a['points'] for a in new_achievements)
            user['stats']['points'] = user['stats'].get('points', 0) + total_points
            
            # Save user profile
            self._save_user(user)
            logger.info(f"Awarded {len(new_achievements)} achievements to user {user_id}")

# Create singleton instance
user_manager = UserManager()