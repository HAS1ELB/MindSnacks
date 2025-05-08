import streamlit as st
import os
import json
import time
import random
from datetime import datetime
from pathlib import Path
import uuid
import logging
from streamlit_lottie import st_lottie
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from streamlit_extras.let_it_rain import rain

# Import utilities
from utils.language_utils import get_translation, get_languages_for_display
from utils.data_utils import (
    track_event, UserSession, memory_cache
)
from utils.auth_utils import user_manager
from config import (
    APP_TITLE, APP_DESCRIPTION, APP_EMOJI, 
    DEFAULT_LANGUAGE, DEFAULT_THEME, APP_INFO,
    save_client_config
)
from components.notifications import notifications

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MindsnacksApp:
    """Main application class for Mindsnacks v2"""
    
    def __init__(self):
        """Initialize application"""
        # Set page configuration
        st.set_page_config(
            page_title=APP_TITLE,
            page_icon=APP_EMOJI,
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Save client-side configuration
        save_client_config()
        
        # Initialize session state
        self._init_session_state()
        
        # Apply custom styling
        self._apply_custom_styling()
    
    def _init_session_state(self):
        """Initialize session state variables"""
        # Language setting
        if 'language' not in st.session_state:
            st.session_state.language = DEFAULT_LANGUAGE
        
        # Theme setting
        if 'theme' not in st.session_state:
            st.session_state.theme = DEFAULT_THEME
            
        # User session
        if 'session' not in st.session_state:
            st.session_state.session = UserSession()
        
        # Current page
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'home'
        
        # Playlist
        if 'current_playlist' not in st.session_state:
            st.session_state.current_playlist = []
    
    def _apply_custom_styling(self):
        """Apply custom CSS styling and define theme-specific colors"""
        theme = st.session_state.theme
        
        if theme == 'light':
            st.session_state.theme_colors = {
                "sidebar_icon": "#4a4a4a",      # Darker grey
                "sidebar_text": "#333333",      # Dark grey
                "sidebar_hover_bg": "#e6e6e6",  # Lighter grey for hover
                "sidebar_selected_bg": "#1DB954",# Accent green for selected
                "sidebar_selected_text": "#ffffff" # White text for selected
            }
            theme_css_path = Path('static/css/light.css')
        else: # Dark theme
            st.session_state.theme_colors = {
                "sidebar_icon": "#b0b0b0",      # Softer white/light grey
                "sidebar_text": "#d0d0d0",      # Light grey
                "sidebar_hover_bg": "#33373d",  # Darker grey for hover
                "sidebar_selected_bg": "#1DB954",# Accent green for selected
                "sidebar_selected_text": "#ffffff" # White text for selected
            }
            theme_css_path = Path('static/css/dark.css')
            
        # Default to dark theme if file doesn't exist
        if not theme_css_path.exists() and theme == 'dark': # Ensure this only runs for dark theme if dark.css is missing
            # Create a basic dark.css if it's missing
            os.makedirs(Path('static/css'), exist_ok=True) # Ensure directory exists
            with open('static/css/dark.css', 'w') as f:
                f.write("""
                /* Dark theme CSS */
                .stApp {
                    background-color: #121212;
                    color: #f0f0f0;
                }
                .stButton button {
                    background-color: #1DB954;
                    color: white;
                    border-radius: 20px;
                }
                .stButton button:hover {
                    background-color: #1ED760;
                }
                .sidebar .sidebar-content {
                    background-color: #121212;
                }
                /* Add more styles as needed */
                """)
        
        # Apply common CSS
        st.markdown("""
        <style>
        /* Common CSS for both themes */
        .stApp {
            font-family: 'Roboto', sans-serif;
        }
        .stButton button {
            border-radius: 20px;
            padding: 0.3rem 1rem;
            font-weight: 500;
        }
        .sidebar .sidebar-content {
            padding: 1rem;
        }
        /* Logo styling */
        .app-logo {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
        }
        .app-logo img {
            max-width: 150px;
        }
        /* Cards */
        .st-card {
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Apply theme-specific CSS if file exists
        if theme_css_path.exists():
            with open(theme_css_path) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render sidebar with navigation"""
        with st.sidebar:
            # App title/logo
            st.markdown(f"<h1 style='text-align: center;'>{APP_EMOJI} {APP_TITLE}</h1>", unsafe_allow_html=True)
            
            # Display user info if logged in
            if st.session_state.session.is_authenticated:
                user = st.session_state.session.get_user() # Assuming get_user() is a method that returns a dict-like object
                st.markdown(f"### {get_translation('welcome', st.session_state.language)}, {user.get('username', 'User')}")
            
            # Navigation menu
            selected = option_menu(
                menu_title=None,
                options=[
                    get_translation("home", st.session_state.language),
                    get_translation("discover", st.session_state.language),
                    get_translation("library", st.session_state.language),
                    get_translation("quiz", st.session_state.language),
                    get_translation("create", st.session_state.language),
                    get_translation("profile", st.session_state.language),
                    get_translation("settings", st.session_state.language),
                ],
                icons=["house", "search", "collection", "question-circle", "pencil-square", "person", "gear"],
                menu_icon="cast",
                default_index=0,
                orientation="vertical",
                styles={
                    "container": {"padding": "0px !important", "background-color": "transparent"},
                    "icon": {"color": st.session_state.theme_colors["sidebar_icon"], "font-size": "20px"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "3px 0px", # Reduced vertical margin slightly
                        "padding": "10px 15px",
                        "color": st.session_state.theme_colors["sidebar_text"],
                        "--hover-color": st.session_state.theme_colors["sidebar_hover_bg"],
                        "border-radius": "8px",
                    },
                    "nav-link-selected": {
                        "background-color": st.session_state.theme_colors["sidebar_selected_bg"],
                        "color": st.session_state.theme_colors["sidebar_selected_text"],
                        "font-weight": "600", # Semi-bold
                    },
                }
            )
            
            # Handle navigation
            if selected == get_translation("home", st.session_state.language):
                st.session_state.current_page = "home"
            elif selected == get_translation("discover", st.session_state.language):
                switch_page("discover")
            elif selected == get_translation("library", st.session_state.language):
                switch_page("library") 
            elif selected == get_translation("quiz", st.session_state.language):
                switch_page("quiz")
            elif selected == get_translation("create", st.session_state.language):
                switch_page("create")
            elif selected == get_translation("profile", st.session_state.language):
                switch_page("profile")
            elif selected == get_translation("settings", st.session_state.language):
                switch_page("settings")
            
            # Language selector
            st.divider()
            languages = get_languages_for_display()
            col1, col2 = st.columns(2)
            with col1:
                selected_language = st.selectbox(
                    get_translation("language_settings", st.session_state.language),
                    options=list(languages.keys()),
                    format_func=lambda x: languages[x],
                    index=list(languages.keys()).index(st.session_state.language),
                    key="language_selector"
                )
                
                if selected_language != st.session_state.language:
                    st.session_state.language = selected_language
                    st.rerun()
            
            # Theme selector
            with col2:
                selected_theme = st.selectbox(
                    get_translation("theme", st.session_state.language),
                    options=["dark", "light"],
                    format_func=lambda x: get_translation(f"{x}_mode", st.session_state.language),
                    index=0 if st.session_state.theme == "dark" else 1,
                    key="theme_selector"
                )
                
                if selected_theme != st.session_state.theme:
                    st.session_state.theme = selected_theme
                    st.rerun()
            
            # App version at the bottom
            st.divider()
            st.caption(f"v{APP_INFO['version']} | {APP_INFO['release_date']}")
    
    def render_landing_page(self):
        """Render home/landing page"""
        # Welcome header
        colored_header(
            label=get_translation("welcome", st.session_state.language),
            description=get_translation("welcome_subtitle", st.session_state.language),
            color_name="blue-70"
        )
        
        # Try to load animation
        try:
            with open('static/img/animations/welcome.json', 'r') as f:
                lottie_data = json.load(f)
            
            # Display animation
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st_lottie(lottie_data, height=300, key="welcome_animation")
        except:
            # Fallback if animation file doesn't exist
            logo_url = "https://img.icons8.com/color/240/000000/headphones--v2.png"
            st.image(logo_url, width=150)
        
        # Introduction section
        st.markdown("""
        ## What is Mindsnacks?
        
        Mindsnacks is your audio learning companion, delivering bite-sized educational content on any topic you're curious about. It's like Spotify, but for learning!
        
        ### Key Features:
        - **Discover** interesting topics across various fields
        - **Listen** to audio snippets while on the go
        - **Create** your own custom learning content
        - **Quiz** yourself to test your knowledge
        - **Track** your learning journey
        """)
        
        # Show sample topics
        st.divider()
        st.markdown("## Sample Topics to Explore")
        
        sample_topics = [
            "Quantum Computing Basics",
            "The Renaissance Period",
            "Artificial Intelligence Ethics", 
            "Contemporary Art Movements",
            "Mindfulness and Meditation",
            "Sustainable Urban Planning"
        ]
        
        # Display topics in a grid
        cols = st.columns(3)
        for i, topic in enumerate(sample_topics):
            with cols[i % 3]:
                st.markdown(f"""
                <div style='background-color: #282828; border-radius: 10px; padding: 15px; 
                    margin-bottom: 15px; border-left: 5px solid #1DB954;'>
                    <h3 style='margin-top: 0;'>{topic}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(get_translation("explore", st.session_state.language), key=f"explore_{i}"):
                    # Set the topic in session state and navigate to Discover page
                    st.session_state.explore_topic = topic
                    switch_page("discover")
        
        # Recent updates section
        st.divider()
        st.markdown("## What's New")
        
        updates = [
            {"title": "Offline Mode", "description": "Download content for offline learning"},
            {"title": "New Languages", "description": "Added support for Portuguese, Russian, and Korean"},
            {"title": "Learning Paths", "description": "Follow curated learning journeys on various topics"}
        ]
        
        for update in updates:
            st.markdown(f"""
            <div style='background-color: #1E1E1E; border-radius: 10px; padding: 10px; margin-bottom: 10px;'>
                <h4 style='margin-top: 0;'>{update['title']}</h4>
                <p>{update['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Easter egg - achievement notification on 10% of visits
        if random.random() < 0.1:
            notifications.add_success(
                "You've unlocked the 'Curious Mind' achievement!",
                title="Achievement Unlocked"
            )
            rain(
                emoji="🎉",
                font_size=54,
                falling_speed=5,
                animation_length=1,
            )
    
    def run(self):
        """Run the application"""
        # Track page view for analytics
        track_event("page_view", {"page": "home"})
        
        # Render sidebar
        self.render_sidebar()
        
        # Render current page
        if st.session_state.current_page == "home":
            self.render_landing_page()
        
        # Handle notifications (this will display any queued notifications)
        notifications.render_notification_center()

# Initialize and run the app
if __name__ == "__main__":
    app = MindsnacksApp()
    app.run()