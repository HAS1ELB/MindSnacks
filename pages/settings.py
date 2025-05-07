import streamlit as st
import os
import time
import json
import shutil
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page

from utils.language_utils import get_translation, get_languages_for_display
from utils.data_utils import track_event
from utils.cache_utils import disk_cache
from utils.audio_utils import get_available_voices
from config import (
    APP_INFO, DEFAULT_THEME, DEFAULT_LANGUAGE, 
    AUDIO_FORMATS, DEFAULT_AUDIO_FORMAT
)

def app():
    """Settings page for configuring app preferences"""
    
    # Get session state
    if 'session' not in st.session_state:
        st.error("Session not initialized. Please return to the home page.")
        if st.button("Go to Home"):
            switch_page("app")
        return
    
    # Page title
    colored_header(
        label=get_translation('settings_title', st.session_state.language),
        description="",
        color_name="green-70"
    )
    
    # Initialize settings state if needed
    if 'settings_state' not in st.session_state:
        st.session_state.settings_state = {
            'language': st.session_state.language,
            'theme': st.session_state.theme,
            'voice_index': 0,
            'playback_speed': 1.0,
            'audio_quality': 'medium',
            'audio_format': DEFAULT_AUDIO_FORMAT,
            'changes_made': False
        }
    
    # Settings form
    with st.form("settings_form"):
        # Application Settings section
        st.markdown(f"### {get_translation('app_settings', st.session_state.language)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Language selector
            languages = get_languages_for_display()
            selected_language = st.selectbox(
                get_translation('language_settings', st.session_state.language),
                options=list(languages.keys()),
                format_func=lambda x: languages[x],
                index=list(languages.keys()).index(st.session_state.settings_state['language']),
                key="settings_language"
            )
            
            if selected_language != st.session_state.settings_state['language']:
                st.session_state.settings_state['language'] = selected_language
                st.session_state.settings_state['changes_made'] = True
        
        with col2:
            # Theme selector
            selected_theme = st.selectbox(
                get_translation('theme', st.session_state.language),
                options=["dark", "light"],
                format_func=lambda x: get_translation(f"{x}_mode", st.session_state.language),
                index=0 if st.session_state.settings_state['theme'] == "dark" else 1,
                key="settings_theme"
            )
            
            if selected_theme != st.session_state.settings_state['theme']:
                st.session_state.settings_state['theme'] = selected_theme
                st.session_state.settings_state['changes_made'] = True
        
        # Audio Settings section
        st.markdown(f"### {get_translation('audio_settings', st.session_state.language)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Voice selection
            voices = get_available_voices(st.session_state.settings_state['language'])
            voice_options = []
            
            # Format voice options
            if voices and st.session_state.settings_state['language'] in voices:
                standard_voices = voices[st.session_state.settings_state['language']].get('standard', [])
                voice_options = [f"Voice {i+1}" for i in range(len(standard_voices))]
            
            # Default if no voices available
            if not voice_options:
                voice_options = ["Default Voice"]
            
            selected_voice = st.selectbox(
                get_translation('voice_selection', st.session_state.language),
                options=range(len(voice_options)),
                format_func=lambda x: voice_options[x],
                index=min(st.session_state.settings_state['voice_index'], len(voice_options) - 1),
                key="settings_voice"
            )
            
            if selected_voice != st.session_state.settings_state['voice_index']:
                st.session_state.settings_state['voice_index'] = selected_voice
                st.session_state.settings_state['changes_made'] = True
            
            # Audio format selection
            format_options = AUDIO_FORMATS
            selected_format = st.selectbox(
                "Audio Format",
                options=format_options,
                index=format_options.index(st.session_state.settings_state['audio_format']),
                key="settings_format"
            )
            
            if selected_format != st.session_state.settings_state['audio_format']:
                st.session_state.settings_state['audio_format'] = selected_format
                st.session_state.settings_state['changes_made'] = True
        
        with col2:
            # Playback speed
            speed_options = [0.75, 1.0, 1.25, 1.5, 2.0]
            speed_labels = {
                0.75: "0.75x (Slower)",
                1.0: "1.0x (Normal)",
                1.25: "1.25x",
                1.5: "1.5x",
                2.0: "2.0x (Faster)"
            }
            
            selected_speed = st.selectbox(
                get_translation('playback_speed', st.session_state.language),
                options=speed_options,
                format_func=lambda x: speed_labels[x],
                index=speed_options.index(st.session_state.settings_state['playback_speed']),
                key="settings_speed"
            )
            
            if selected_speed != st.session_state.settings_state['playback_speed']:
                st.session_state.settings_state['playback_speed'] = selected_speed
                st.session_state.settings_state['changes_made'] = True
            
            # Audio quality
            quality_options = ["low", "medium", "high"]
            quality_labels = {
                "low": get_translation('low', st.session_state.language),
                "medium": get_translation('medium', st.session_state.language),
                "high": get_translation('high', st.session_state.language)
            }
            
            selected_quality = st.selectbox(
                get_translation('quality', st.session_state.language),
                options=quality_options,
                format_func=lambda x: quality_labels[x],
                index=quality_options.index(st.session_state.settings_state['audio_quality']),
                key="settings_quality"
            )
            
            if selected_quality != st.session_state.settings_state['audio_quality']:
                st.session_state.settings_state['audio_quality'] = selected_quality
                st.session_state.settings_state['changes_made'] = True
        
        # Storage section
        st.markdown(f"### {get_translation('storage', st.session_state.language)}")
        
        # Get cache stats
        cache_stats = disk_cache.get_stats()
        cache_size_mb = (cache_stats.get('llm_size', 0) + cache_stats.get('audio_size', 0)) / (1024 * 1024)
        
        st.markdown(f"""
        **Cache Size:** {cache_size_mb:.2f} MB
        
        **Items in Cache:**
        - LLM Responses: {cache_stats.get('llm_count', 0)}
        - Audio Files: {cache_stats.get('audio_count', 0)}
        """)
        
        # Clear cache checkbox
        clear_cache = st.checkbox(get_translation('clear_cache', st.session_state.language), key="clear_cache")
        
        # Submit button
        submitted = st.form_submit_button(get_translation('save_settings', st.session_state.language))
        
        if submitted:
            # Apply settings
            st.session_state.language = st.session_state.settings_state['language']
            st.session_state.theme = st.session_state.settings_state['theme']
            
            # Save settings to user session
            st.session_state.session.save_settings({
                'language': st.session_state.settings_state['language'],
                'theme': st.session_state.settings_state['theme'],
                'voice_index': st.session_state.settings_state['voice_index'],
                'playback_speed': st.session_state.settings_state['playback_speed'],
                'audio_quality': st.session_state.settings_state['audio_quality'],
                'audio_format': st.session_state.settings_state['audio_format']
            })
            
            # Clear cache if requested
            if clear_cache:
                disk_cache.clear()
                st.session_state.settings_state['clear_cache'] = False
            
            # Track event
            track_event("settings_updated", {
                "language": st.session_state.language,
                "theme": st.session_state.theme,
                "voice_index": st.session_state.settings_state['voice_index'],
                "playback_speed": st.session_state.settings_state['playback_speed'],
                "audio_quality": st.session_state.settings_state['audio_quality'],
                "audio_format": st.session_state.settings_state['audio_format'],
                "cache_cleared": clear_cache
            })
            
            # Show success message
            st.success(get_translation('settings_saved', st.session_state.language))
            
            # Reset changes made flag
            st.session_state.settings_state['changes_made'] = False
            
            # Rerun to apply changes
            time.sleep(1)  # Brief pause to show success message
            st.rerun()
    
    # App information section
    st.divider()
    st.markdown(f"### {get_translation('app_info', st.session_state.language)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **{get_translation('version', st.session_state.language)}:** {APP_INFO['version']}
        
        **Release Date:** {APP_INFO['release_date']}
        
        **Developers:** {', '.join(APP_INFO['developers'])}
        
        **License:** {APP_INFO['license']}
        """)
    
    with col2:
        st.markdown(f"""
        **Website:** [{APP_INFO['website']}]({APP_INFO['website']})
        
        **{get_translation('help', st.session_state.language)}:** [Documentation](https://github.com/yourusername/mindsnacks-v2/docs)
        
        **{get_translation('feedback', st.session_state.language)}:** [Send Feedback](mailto:feedback@mindsnacks.app)
        """)

if __name__ == "__main__":
    app()