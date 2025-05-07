from typing import List, Dict, Any, Optional, Tuple, Union
import json
import logging
import datetime
import os
import random
from collections import Counter, defaultdict

# Configure logging
logger = logging.getLogger(__name__)

class UserPatternAnalysis:
    """
    Analyze user behavior patterns for personalization and insights
    """
    
    def __init__(self, analytics_dir: str):
        """
        Initialize user pattern analysis
        
        Args:
            analytics_dir (str): Directory for analytics data
        """
        self.analytics_dir = analytics_dir
        self.user_data = {}
        self.global_patterns = {
            'popular_topics': Counter(),
            'active_hours': Counter(),
            'completion_rates': [],
            'session_durations': [],
            'device_types': Counter(),
            'languages': Counter()
        }
        
        # Create analytics directory if it doesn't exist
        os.makedirs(analytics_dir, exist_ok=True)
    
    def load_analytics_data(self):
        """
        Load analytics data from files
        """
        try:
            # Load global analytics
            global_file = os.path.join(self.analytics_dir, 'global_patterns.json')
            if os.path.exists(global_file):
                with open(global_file, 'r') as f:
                    data = json.load(f)
                    self.global_patterns = {
                        'popular_topics': Counter(data.get('popular_topics', {})),
                        'active_hours': Counter(data.get('active_hours', {})),
                        'completion_rates': data.get('completion_rates', []),
                        'session_durations': data.get('session_durations', []),
                        'device_types': Counter(data.get('device_types', {})),
                        'languages': Counter(data.get('languages', {}))
                    }
            
            # Load user data
            user_data_dir = os.path.join(self.analytics_dir, 'users')
            os.makedirs(user_data_dir, exist_ok=True)
            
            for filename in os.listdir(user_data_dir):
                if filename.endswith('.json'):
                    user_id = filename.split('.')[0]
                    try:
                        with open(os.path.join(user_data_dir, filename), 'r') as f:
                            self.user_data[user_id] = json.load(f)
                    except Exception as e:
                        logger.error(f"Error loading data for user {user_id}: {e}")
            
            logger.info(f"Loaded analytics data for {len(self.user_data)} users")
            
        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
    
    def save_analytics_data(self):
        """
        Save analytics data to files
        """
        try:
            # Save global analytics
            global_file = os.path.join(self.analytics_dir, 'global_patterns.json')
            with open(global_file, 'w') as f:
                # Convert Counter objects to dictionaries
                global_data = {
                    'popular_topics': dict(self.global_patterns['popular_topics']),
                    'active_hours': dict(self.global_patterns['active_hours']),
                    'completion_rates': self.global_patterns['completion_rates'],
                    'session_durations': self.global_patterns['session_durations'],
                    'device_types': dict(self.global_patterns['device_types']),
                    'languages': dict(self.global_patterns['languages']),
                    'last_updated': datetime.datetime.now().isoformat()
                }
                json.dump(global_data, f, indent=2)
            
            # Save user data
            user_data_dir = os.path.join(self.analytics_dir, 'users')
            os.makedirs(user_data_dir, exist_ok=True)
            
            for user_id, data in self.user_data.items():
                user_file = os.path.join(user_data_dir, f"{user_id}.json")
                with open(user_file, 'w') as f:
                    # Add last updated timestamp
                    data['last_updated'] = datetime.datetime.now().isoformat()
                    json.dump(data, f, indent=2)
            
            logger.info(f"Saved analytics data for {len(self.user_data)} users")
            
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
    
    def track_user_event(self, user_id: str, event_type: str, event_data: Dict[str, Any]):
        """
        Track a user event
        
        Args:
            user_id (str): User ID
            event_type (str): Type of event
            event_data (dict): Event data
        """
        try:
            # Initialize user data if not exists
            if user_id not in self.user_data:
                self.user_data[user_id] = {
                    'events': [],
                    'preferences': {},
                    'stats': {},
                    'first_seen': datetime.datetime.now().isoformat(),
                    'last_active': datetime.datetime.now().isoformat()
                }
            
            # Add event to user history
            event = {
                'type': event_type,
                'timestamp': datetime.datetime.now().isoformat(),
                'data': event_data
            }
            
            self.user_data[user_id]['events'].append(event)
            self.user_data[user_id]['last_active'] = datetime.datetime.now().isoformat()
            
            # Update global patterns
            self._update_global_patterns(event_type, event_data)
            
            # Update user stats
            self._update_user_stats(user_id, event_type, event_data)
            
            # Save analytics data periodically
            # This is a simplified approach - in a real system, use a more efficient approach
            if random.random() < 0.1:  # 10% chance to save on each event
                self.save_analytics_data()
            
        except Exception as e:
            logger.error(f"Error tracking user event: {e}")
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get insights for a specific user
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User insights
        """
        try:
            if user_id not in self.user_data:
                return {}
            
            user_data = self.user_data[user_id]
            events = user_data.get('events', [])
            
            if not events:
                return {}
            
            # Find favorite topics
            topic_counter = Counter()
            for event in events:
                if event['type'] in ['content_viewed', 'content_created']:
                    topic = event['data'].get('topic')
                    if topic:
                        topic_counter[topic] += 1
            
            favorite_topics = [topic for topic, count in topic_counter.most_common(5)]
            
            # Find active hours
            active_hours = []
            for event in events:
                try:
                    timestamp = datetime.datetime.fromisoformat(event['timestamp'])
                    active_hours.append(timestamp.hour)
                except:
                    pass
            
            hour_counter = Counter(active_hours)
            peak_hour = hour_counter.most_common(1)[0][0] if hour_counter else None
            
            # Calculate session statistics
            sessions = self._identify_sessions(events)
            avg_session_duration = sum(session['duration'] for session in sessions) / len(sessions) if sessions else 0
            
            # Calculate learning progress
            completed_snippets = sum(1 for event in events if event['type'] == 'content_completed')
            quiz_completions = sum(1 for event in events if event['type'] == 'quiz_completed')
            
            # Get recent activity
            recent_events = sorted(events, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
            recent_activity = [
                {
                    'type': event['type'],
                    'timestamp': event['timestamp'],
                    'details': self._get_event_description(event)
                }
                for event in recent_events
            ]
            
            # Generate recommendations based on patterns
            learning_recommendations = self._generate_user_recommendations(user_id)
            
            return {
                'favorite_topics': favorite_topics,
                'peak_activity_hour': peak_hour,
                'avg_session_duration': round(avg_session_duration / 60, 1) if avg_session_duration else 0,  # minutes
                'completed_snippets': completed_snippets,
                'quiz_completions': quiz_completions,
                'recent_activity': recent_activity,
                'recommendations': learning_recommendations,
                'days_active': self._calculate_days_active(events),
                'user_level': self._calculate_user_level(events)
            }
            
        except Exception as e:
            logger.error(f"Error getting user insights: {e}")
            return {}
    
    def get_global_insights(self) -> Dict[str, Any]:
        """
        Get global app insights
        
        Returns:
            dict: Global insights
        """
        try:
            # Popular topics
            popular_topics = [topic for topic, count in self.global_patterns['popular_topics'].most_common(10)]
            
            # Active hours (peak times)
            active_hours = self.global_patterns['active_hours']
            peak_hours = [hour for hour, count in active_hours.most_common(3)]
            
            # Average completion rate
            avg_completion_rate = sum(self.global_patterns['completion_rates']) / len(self.global_patterns['completion_rates']) if self.global_patterns['completion_rates'] else 0
            
            # Average session duration
            avg_session_duration = sum(self.global_patterns['session_durations']) / len(self.global_patterns['session_durations']) if self.global_patterns['session_durations'] else 0
            
            # Device distribution
            device_distribution = {
                device: count / sum(self.global_patterns['device_types'].values())
                for device, count in self.global_patterns['device_types'].items()
            } if sum(self.global_patterns['device_types'].values()) > 0 else {}
            
            # Language distribution
            language_distribution = {
                language: count / sum(self.global_patterns['languages'].values())
                for language, count in self.global_patterns['languages'].items()
            } if sum(self.global_patterns['languages'].values()) > 0 else {}
            
            return {
                'popular_topics': popular_topics,
                'peak_hours': peak_hours,
                'avg_completion_rate': round(avg_completion_rate * 100, 1),  # percentage
                'avg_session_duration': round(avg_session_duration / 60, 1),  # minutes
                'device_distribution': device_distribution,
                'language_distribution': language_distribution,
                'active_users': len(self.user_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting global insights: {e}")
            return {}
    
    def get_topic_insights(self, topic: str) -> Dict[str, Any]:
        """
        Get insights for a specific topic
        
        Args:
            topic (str): Topic name
            
        Returns:
            dict: Topic insights
        """
        try:
            # Track topic views and completions
            views = 0
            completions = 0
            creation_count = 0
            quiz_attempts = 0
            quiz_scores = []
            user_comments = []
            
            # Analyze all user events for this topic
            for user_id, user_data in self.user_data.items():
                for event in user_data.get('events', []):
                    event_topic = event['data'].get('topic')
                    
                    if event_topic == topic:
                        if event['type'] == 'content_viewed':
                            views += 1
                        elif event['type'] == 'content_completed':
                            completions += 1
                        elif event['type'] == 'content_created':
                            creation_count += 1
                        elif event['type'] == 'quiz_attempted':
                            quiz_attempts += 1
                        elif event['type'] == 'quiz_completed':
                            quiz_scores.append(event['data'].get('score', 0))
                        elif event['type'] == 'comment_added':
                            comment = event['data'].get('comment')
                            if comment:
                                user_comments.append({
                                    'user_id': user_id,
                                    'comment': comment,
                                    'timestamp': event['timestamp']
                                })
            
            # Calculate completion rate
            completion_rate = completions / views if views > 0 else 0
            
            # Calculate average quiz score
            avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
            
            # Find related topics
            related_topics = self._find_related_topics(topic)
            
            return {
                'views': views,
                'completions': completions,
                'creation_count': creation_count,
                'completion_rate': round(completion_rate * 100, 1),  # percentage
                'quiz_attempts': quiz_attempts,
                'avg_quiz_score': round(avg_quiz_score, 1),
                'recent_comments': sorted(user_comments, key=lambda x: x.get('timestamp', ''), reverse=True)[:5],
                'related_topics': related_topics
            }
            
        except Exception as e:
            logger.error(f"Error getting topic insights: {e}")
            return {}
    
    def _update_global_patterns(self, event_type: str, event_data: Dict[str, Any]):
        """
        Update global pattern data
        
        Args:
            event_type (str): Type of event
            event_data (dict): Event data
        """
        try:
            # Update topic popularity
            if event_type in ['content_viewed', 'content_created']:
                topic = event_data.get('topic')
                if topic:
                    self.global_patterns['popular_topics'][topic] += 1
            
            # Update active hours
            now = datetime.datetime.now()
            self.global_patterns['active_hours'][now.hour] += 1
            
            # Update completion rates
            if event_type == 'content_completed':
                completion_rate = event_data.get('completion_rate', 1.0)
                self.global_patterns['completion_rates'].append(completion_rate)
                
                # Keep list from growing too large
                if len(self.global_patterns['completion_rates']) > 1000:
                    self.global_patterns['completion_rates'] = self.global_patterns['completion_rates'][-1000:]
            
            # Update session durations
            if event_type == 'session_ended':
                duration = event_data.get('duration', 0)
                if duration > 0:
                    self.global_patterns['session_durations'].append(duration)
                    
                    # Keep list from growing too large
                    if len(self.global_patterns['session_durations']) > 1000:
                        self.global_patterns['session_durations'] = self.global_patterns['session_durations'][-1000:]
            
            # Update device types
            device = event_data.get('device_type')
            if device:
                self.global_patterns['device_types'][device] += 1
            
            # Update languages
            language = event_data.get('language')
            if language:
                self.global_patterns['languages'][language] += 1
                
        except Exception as e:
            logger.error(f"Error updating global patterns: {e}")
    
    def _update_user_stats(self, user_id: str, event_type: str, event_data: Dict[str, Any]):
        """
        Update user statistics
        
        Args:
            user_id (str): User ID
            event_type (str): Type of event
            event_data (dict): Event data
        """
        try:
            if 'stats' not in self.user_data[user_id]:
                self.user_data[user_id]['stats'] = {}
            
            stats = self.user_data[user_id]['stats']
            
            # Initialize counters if they don't exist
            for counter in ['content_viewed', 'content_completed', 'content_created', 
                           'quiz_attempted', 'quiz_completed', 'days_active']:
                if counter not in stats:
                    stats[counter] = 0
            
            # Update appropriate counter
            if event_type in ['content_viewed', 'content_completed', 'content_created',
                             'quiz_attempted', 'quiz_completed']:
                stats[event_type] += 1
            
            # Update topic preferences
            if event_type in ['content_viewed', 'content_created']:
                topic = event_data.get('topic')
                if topic:
                    if 'topic_preferences' not in stats:
                        stats['topic_preferences'] = {}
                    
                    if topic not in stats['topic_preferences']:
                        stats['topic_preferences'][topic] = 0
                    
                    stats['topic_preferences'][topic] += 1
            
            # Update language preferences
            language = event_data.get('language')
            if language:
                if 'language_preferences' not in stats:
                    stats['language_preferences'] = {}
                
                if language not in stats['language_preferences']:
                    stats['language_preferences'][language] = 0
                
                stats['language_preferences'][language] += 1
            
            # Update daily activity
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            if 'daily_activity' not in stats:
                stats['daily_activity'] = {}
            
            if today not in stats['daily_activity']:
                stats['daily_activity'][today] = 0
                # Increment days active counter if this is a new day
                stats['days_active'] += 1
            
            stats['daily_activity'][today] += 1
            
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
    
    def _identify_sessions(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify user sessions from events
        
        Args:
            events (list): List of user events
            
        Returns:
            list: List of session dictionaries
        """
        sessions = []
        
        try:
            # Sort events by timestamp
            sorted_events = sorted(events, key=lambda x: x.get('timestamp', ''))
            
            if not sorted_events:
                return []
            
            # Session timeout threshold (30 minutes)
            timeout_threshold = 30 * 60  # seconds
            
            current_session = {
                'start': None,
                'end': None,
                'events': [],
                'duration': 0
            }
            
            for event in sorted_events:
                try:
                    timestamp = datetime.datetime.fromisoformat(event['timestamp'])
                    
                    if current_session['start'] is None:
                        # Start new session
                        current_session['start'] = timestamp
                        current_session['events'] = [event]
                    else:
                        # Check if this event is part of the current session
                        last_event = current_session['events'][-1]
                        last_timestamp = datetime.datetime.fromisoformat(last_event['timestamp'])
                        
                        time_diff = (timestamp - last_timestamp).total_seconds()
                        
                        if time_diff > timeout_threshold:
                            # End current session and start a new one
                            current_session['end'] = last_timestamp
                            current_session['duration'] = (current_session['end'] - current_session['start']).total_seconds()
                            sessions.append(current_session)
                            
                            # Start new session
                            current_session = {
                                'start': timestamp,
                                'end': None,
                                'events': [event],
                                'duration': 0
                            }
                        else:
                            # Add to current session
                            current_session['events'].append(event)
                except:
                    # Skip events with invalid timestamps
                    continue
            
            # Add the last session if it exists
            if current_session['start'] is not None:
                if len(current_session['events']) > 0:
                    last_event = current_session['events'][-1]
                    current_session['end'] = datetime.datetime.fromisoformat(last_event['timestamp'])
                    current_session['duration'] = (current_session['end'] - current_session['start']).total_seconds()
                    sessions.append(current_session)
            
        except Exception as e:
            logger.error(f"Error identifying sessions: {e}")
        
        return sessions
    
    def _get_event_description(self, event: Dict[str, Any]) -> str:
        """
        Get a human-readable description of an event
        
        Args:
            event (dict): Event dictionary
            
        Returns:
            str: Event description
        """
        event_type = event['type']
        data = event.get('data', {})
        
        if event_type == 'content_viewed':
            return f"Viewed content on '{data.get('topic', 'Unknown topic')}'"
        elif event_type == 'content_completed':
            return f"Completed content on '{data.get('topic', 'Unknown topic')}'"
        elif event_type == 'content_created':
            return f"Created content on '{data.get('topic', 'Unknown topic')}'"
        elif event_type == 'quiz_attempted':
            return f"Attempted quiz on '{data.get('topic', 'Unknown topic')}'"
        elif event_type == 'quiz_completed':
            score = data.get('score', 0)
            return f"Completed quiz on '{data.get('topic', 'Unknown topic')}' with score {score}%"
        elif event_type == 'comment_added':
            return f"Added comment on '{data.get('topic', 'Unknown topic')}'"
        else:
            return f"{event_type.replace('_', ' ').title()}"
    
    def _calculate_days_active(self, events: List[Dict[str, Any]]) -> int:
        """
        Calculate the number of days the user has been active
        
        Args:
            events (list): List of user events
            
        Returns:
            int: Number of active days
        """
        try:
            # Extract dates from event timestamps
            dates = set()
            for event in events:
                try:
                    timestamp = datetime.datetime.fromisoformat(event['timestamp'])
                    dates.add(timestamp.date())
                except:
                    continue
            
            return len(dates)
        
        except Exception as e:
            logger.error(f"Error calculating active days: {e}")
            return 0
    
    def _calculate_user_level(self, events: List[Dict[str, Any]]) -> int:
        """
        Calculate user level based on activity
        
        Args:
            events (list): List of user events
            
        Returns:
            int: User level (1-10)
        """
        try:
            # Simple level calculation based on number of events
            event_count = len(events)
            
            if event_count < 10:
                return 1
            elif event_count < 30:
                return 2
            elif event_count < 60:
                return 3
            elif event_count < 100:
                return 4
            elif event_count < 150:
                return 5
            elif event_count < 250:
                return 6
            elif event_count < 400:
                return 7
            elif event_count < 600:
                return 8
            elif event_count < 1000:
                return 9
            else:
                return 10
        
        except Exception as e:
            logger.error(f"Error calculating user level: {e}")
            return 1
    
    def _generate_user_recommendations(self, user_id: str) -> List[str]:
        """
        Generate topic recommendations based on user patterns
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of recommended topics
        """
        try:
            if user_id not in self.user_data:
                return []
            
            user_data = self.user_data[user_id]
            events = user_data.get('events', [])
            
            if not events:
                return []
            
            # Find user's favorite topics
            topic_counter = Counter()
            for event in events:
                if event['type'] in ['content_viewed', 'content_created']:
                    topic = event['data'].get('topic')
                    if topic:
                        topic_counter[topic] += 1
            
            favorite_topics = [topic for topic, count in topic_counter.most_common(3)]
            
            # Find related topics
            recommendations = []
            for topic in favorite_topics:
                related = self._find_related_topics(topic)
                recommendations.extend(related)
            
            # Remove duplicates and topics the user has already interacted with
            recommendations = [topic for topic in recommendations if topic not in topic_counter]
            
            # Return top 5 recommendations
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _find_related_topics(self, topic: str) -> List[str]:
        """
        Find topics related to a given topic
        
        Args:
            topic (str): Topic name
            
        Returns:
            list: List of related topics
        """
        try:
            # Create a map of topic co-occurrences
            topic_pairs = defaultdict(int)
            
            # Analyze all user events for co-occurring topics
            for user_data in self.user_data.values():
                # Get all topics this user has interacted with
                user_topics = set()
                for event in user_data.get('events', []):
                    if event['type'] in ['content_viewed', 'content_created']:
                        event_topic = event['data'].get('topic')
                        if event_topic:
                            user_topics.add(event_topic)
                
                # If the target topic is in user's topics, count co-occurrences
                if topic in user_topics:
                    for other_topic in user_topics:
                        if other_topic != topic:
                            topic_pairs[(topic, other_topic)] += 1
            
            # Sort co-occurring topics by frequency
            related_topics = []
            for (t1, t2), count in sorted(topic_pairs.items(), key=lambda x: x[1], reverse=True):
                if t1 == topic:
                    related_topics.append(t2)
            
            # Return top 5 related topics
            return related_topics[:5]
            
        except Exception as e:
            logger.error(f"Error finding related topics: {e}")
            return []

# Create singleton instance
user_patterns = None  # Will be initialized with proper analytics_dir