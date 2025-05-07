import streamlit as st
from typing import Dict, List, Any, Optional, Callable, Union
import time
import random

class NotificationManager:
    """
    Manage and display notifications in the app
    """
    
    def __init__(self, max_notifications: int = 5):
        """
        Initialize notification manager
        
        Args:
            max_notifications (int): Maximum number of notifications to store
        """
        self.max_notifications = max_notifications
        
        # Initialize notification state in session
        if "notifications" not in st.session_state:
            st.session_state.notifications = []
            
        if "notification_count" not in st.session_state:
            st.session_state.notification_count = 0
    
    def add(self, message: str, type: str = "info", duration: int = 5, title: Optional[str] = None):
        """
        Add a notification
        
        Args:
            message (str): Notification message
            type (str): Notification type ('info', 'success', 'warning', 'error')
            duration (int): Duration in seconds (0 for persistent)
            title (str, optional): Notification title
        """
        # Generate unique ID
        notification_id = f"notification_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create notification object
        notification = {
            "id": notification_id,
            "message": message,
            "type": type,
            "duration": duration,
            "title": title,
            "timestamp": time.time(),
            "read": False
        }
        
        # Add to state
        st.session_state.notifications.append(notification)
        st.session_state.notification_count += 1
        
        # Trim if exceeding max
        if len(st.session_state.notifications) > self.max_notifications:
            st.session_state.notifications = st.session_state.notifications[-self.max_notifications:]
    
    def add_success(self, message: str, duration: int = 5, title: Optional[str] = None):
        """Shorthand for success notification"""
        self.add(message, "success", duration, title)
    
    def add_info(self, message: str, duration: int = 5, title: Optional[str] = None):
        """Shorthand for info notification"""
        self.add(message, "info", duration, title)
    
    def add_warning(self, message: str, duration: int = 5, title: Optional[str] = None):
        """Shorthand for warning notification"""
        self.add(message, "warning", duration, title)
    
    def add_error(self, message: str, duration: int = 5, title: Optional[str] = None):
        """Shorthand for error notification"""
        self.add(message, "error", duration, title)
    
    def clear(self):
        """Clear all notifications"""
        st.session_state.notifications = []
        st.session_state.notification_count = 0
    
    def mark_read(self, notification_id: str):
        """Mark a notification as read"""
        for notif in st.session_state.notifications:
            if notif["id"] == notification_id:
                notif["read"] = True
                break
    
    def mark_all_read(self):
        """Mark all notifications as read"""
        for notif in st.session_state.notifications:
            notif["read"] = True
    
    def remove(self, notification_id: str):
        """Remove a notification"""
        st.session_state.notifications = [n for n in st.session_state.notifications if n["id"] != notification_id]
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return sum(1 for n in st.session_state.notifications if not n["read"])
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all notifications"""
        return st.session_state.notifications
    
    def get_latest(self) -> Optional[Dict[str, Any]]:
        """Get the latest notification"""
        if st.session_state.notifications:
            return st.session_state.notifications[-1]
        return None
    
    def auto_dismiss(self):
        """Auto-dismiss notifications based on duration"""
        current_time = time.time()
        st.session_state.notifications = [
            n for n in st.session_state.notifications 
            if n["duration"] == 0 or current_time - n["timestamp"] < n["duration"]
        ]
    
    def render_toast(self, notification: Dict[str, Any]):
        """
        Render a single notification as a toast
        
        Args:
            notification (dict): Notification object
        """
        message = notification.get("message", "")
        type = notification.get("type", "info")
        
        if type == "success":
            st.success(message)
        elif type == "warning":
            st.warning(message)
        elif type == "error":
            st.error(message)
        else:  # Default to info
            st.info(message)
    
    def render_notification_center(self, on_click: Optional[Callable] = None):
        """
        Render notification center UI
        
        Args:
            on_click (callable, optional): Function to call when a notification is clicked
        """
        # Auto dismiss expired notifications
        self.auto_dismiss()
        
        # Get notification count
        unread_count = self.get_unread_count()
        
        # Notification bell icon with badge
        if unread_count > 0:
            bell_icon = f"🔔 ({unread_count})"
        else:
            bell_icon = "🔔"
        
        # Create an expander for the notification center
        with st.expander(bell_icon, expanded=False):
            if not st.session_state.notifications:
                st.markdown("No notifications.")
            else:
                # Add clear all button
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("Clear All"):
                        self.clear()
                        st.rerun()
                
                # Render each notification
                for notification in reversed(st.session_state.notifications):
                    self._render_notification_card(notification, on_click)
    
    def _render_notification_card(self, notification: Dict[str, Any], on_click: Optional[Callable] = None):
        """
        Render a notification card
        
        Args:
            notification (dict): Notification object
            on_click (callable, optional): Function to call when the notification is clicked
        """
        notification_id = notification.get("id", "")
        message = notification.get("message", "")
        type = notification.get("type", "info")
        title = notification.get("title")
        timestamp = notification.get("timestamp", 0)
        read = notification.get("read", False)
        
        # Format timestamp
        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
        
        # Determine icon and color based on type
        icon_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        icon = icon_map.get(type, "ℹ️")
        
        # Create container for notification
        with st.container():
            # Style with custom HTML
            if read:
                opacity = 0.7
                background = "#333333"
            else:
                opacity = 1.0
                background = "#2A2A2A"
            
            html = f"""
            <div style="background-color: {background}; border-radius: 5px; padding: 10px; margin-bottom: 10px; opacity: {opacity}; border-left: 3px solid {'#1DB954' if type == 'success' else '#ff9800' if type == 'warning' else '#f44336' if type == 'error' else '#2196f3'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 18px; margin-right: 8px;">{icon}</span>
                        <div>
                            {f"<strong>{title}</strong><br>" if title else ""}
                            <span>{message}</span>
                        </div>
                    </div>
                    <div style="color: #999; font-size: 12px;">{formatted_time}</div>
                </div>
            </div>
            """
            
            st.markdown(html, unsafe_allow_html=True)
            
            # Actions
            col1, col2 = st.columns([4, 1])
            
            with col2:
                if st.button("Dismiss", key=f"dismiss_{notification_id}"):
                    self.remove(notification_id)
                    st.rerun()
            
            with col1:
                if not read:
                    if st.button("Mark as Read", key=f"read_{notification_id}"):
                        self.mark_read(notification_id)
                        st.rerun()
            
            # Handle click
            if on_click and st.button("View Details", key=f"view_{notification_id}"):
                self.mark_read(notification_id)
                on_click(notification)

# Create a global notification manager
notifications = NotificationManager()