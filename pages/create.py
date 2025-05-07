import streamlit as st
import asyncio
import time
import pandas as pd
import json
import os
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.let_it_rain import rain

from utils.llm_utils import generate_learning_snippet
from utils.audio_utils import generate_audio, get_audio_duration
from utils.data_utils import track_event, save_audio_metadata
from utils.language_utils import get_translation, get_languages_for_display
from components.audio_player import AudioPlayer

def app():
    """Create page for generating custom learning content"""
    
    # Get session state
    if 'session' not in st.session_state:
        st.error("Session not initialized. Please return to the home page.")
        if st.button("Go to Home"):
            switch_page("app")
        return
    
    # Page title with animation
    colored_header(
        label=get_translation('create_title', st.session_state.language),
        description=get_translation('create_subtitle', st.session_state.language),
        color_name="violet-70"
    )
    
    # Initialize form state
    if 'create_form_state' not in st.session_state:
        st.session_state.create_form_state = {
            'topic': '',
            'length': 'standard',
            'language': st.session_state.language,
            'voice_index': 0,
            'generated_content': None,
            'generated_audio_path': None,
            'generating': False,
            'audio_generating': False,
            'error': None
        }
    
    # Form layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Topic input
        topic = st.text_input(
            get_translation('enter_topic_create', st.session_state.language),
            key="create_topic",
            value=st.session_state.create_form_state['topic']
        )
        
        # Update form state
        st.session_state.create_form_state['topic'] = topic
    
    with col2:
        # Content length selection
        length_options = {
            'short': get_translation('short', st.session_state.language),
            'standard': get_translation('standard', st.session_state.language),
            'detailed': get_translation('detailed', st.session_state.language)
        }
        
        length = st.selectbox(
            get_translation('content_length', st.session_state.language),
            options=list(length_options.keys()),
            format_func=lambda x: length_options[x],
            index=list(length_options.keys()).index(st.session_state.create_form_state['length']),
            key="content_length"
        )
        
        # Update form state
        st.session_state.create_form_state['length'] = length
    
    # Advanced options expander
    with st.expander(get_translation('voice_options', st.session_state.language)):
        # Language selection
        languages = get_languages_for_display()
        selected_language = st.selectbox(
            get_translation('content_language', st.session_state.language),
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(st.session_state.create_form_state['language']),
            key="content_language"
        )
        
        # Update form state
        st.session_state.create_form_state['language'] = selected_language
        
        # Voice selection
        voice_options = [f"Voice {i+1}" for i in range(5)]
        selected_voice = st.selectbox(
            get_translation('voice_selection', st.session_state.language),
            options=range(len(voice_options)),
            format_func=lambda x: voice_options[x],
            index=st.session_state.create_form_state['voice_index'],
            key="voice_selection"
        )
        
        # Update form state
        st.session_state.create_form_state['voice_index'] = selected_voice
    
    # Generate button
    if st.button(get_translation('generate_content', st.session_state.language), key="generate_button", 
                disabled=not topic or st.session_state.create_form_state['generating']):
        
        # Mark as generating
        st.session_state.create_form_state['generating'] = True
        st.session_state.create_form_state['error'] = None
        
        # Rerun to show spinner
        st.rerun()
    
    # Display spinner while generating
    if st.session_state.create_form_state['generating'] and not st.session_state.create_form_state['generated_content']:
        with st.spinner(get_translation('generating_content', st.session_state.language)):
            # Get duration based on length setting
            duration_map = {
                'short': 2,
                'standard': 5,
                'detailed': 10
            }
            duration = duration_map.get(length, 5)
            
            # Generate content asynchronously
            try:
                # Create async loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Generate snippet
                snippet = loop.run_until_complete(generate_learning_snippet(
                    topic,
                    duration,
                    selected_language
                ))
                
                loop.close()
                
                if snippet and 'error' not in snippet:
                    # Store generated content
                    st.session_state.create_form_state['generated_content'] = snippet
                    
                    # Track event
                    track_event("content_created", {
                        "topic": topic,
                        "length": length,
                        "language": selected_language,
                        "success": True
                    })
                    
                    # Rerun to show content
                    st.rerun()
                else:
                    # Handle error
                    st.session_state.create_form_state['error'] = "Failed to generate content. Please try again."
                    st.session_state.create_form_state['generating'] = False
                    
                    # Track event
                    track_event("content_created", {
                        "topic": topic,
                        "length": length,
                        "language": selected_language,
                        "success": False
                    })
                    
                    # Rerun to show error
                    st.rerun()
            
            except Exception as e:
                # Handle exception
                st.session_state.create_form_state['error'] = f"Error: {str(e)}"
                st.session_state.create_form_state['generating'] = False
                
                # Track event
                track_event("content_created", {
                    "topic": topic,
                    "length": length,
                    "language": selected_language,
                    "success": False,
                    "error": str(e)
                })
                
                # Rerun to show error
                st.rerun()
    
    # Display error if any
    if st.session_state.create_form_state['error']:
        st.error(st.session_state.create_form_state['error'])
    
    # Display generated content
    if st.session_state.create_form_state['generated_content']:
        snippet = st.session_state.create_form_state['generated_content']
        
        st.divider()
        st.markdown(f"## {snippet['title']}")
        
        # Content display
        with st.container():
            # Text content with scrollable area
            st.markdown(
                f"""
                <div style="height: 300px; overflow-y: scroll; padding: 10px; 
                    border: 1px solid #888; border-radius: 5px; background-color: #333;">
                    {snippet['content']}
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(get_translation('edit_content', st.session_state.language), key="edit_button"):
                    # Enable editing in a text area
                    st.session_state.create_form_state['editing'] = True
                    st.rerun()
            
            with col2:
                # Generate audio button
                if st.button(get_translation('preview_audio', st.session_state.language), key="audio_button", 
                            disabled=st.session_state.create_form_state['audio_generating']):
                    
                    # Mark as generating audio
                    st.session_state.create_form_state['audio_generating'] = True
                    st.rerun()
            
            with col3:
                # Save button
                if st.button(get_translation('save_to_library', st.session_state.language), key="save_button"):
                    # Save content to library
                    if 'current_playlist' not in st.session_state:
                        st.session_state.current_playlist = []
                    
                    if snippet not in st.session_state.current_playlist:
                        # Generate audio if not already generated
                        if not st.session_state.create_form_state['generated_audio_path']:
                            with st.spinner(get_translation('generating_audio', st.session_state.language)):
                                audio_path = generate_audio(
                                    snippet['content'],
                                    snippet['title'],
                                    selected_language,
                                    st.session_state.create_form_state['voice_index']
                                )
                                
                                if audio_path:
                                    # Get audio duration
                                    duration = get_audio_duration(audio_path)
                                    
                                    # Save audio metadata
                                    audio_metadata = save_audio_metadata(snippet['id'], audio_path, duration)
                                    
                                    # Update snippet with audio information
                                    snippet['audio_path'] = audio_path
                                    snippet['audio_duration'] = duration
                                    
                                    # Store generated audio path
                                    st.session_state.create_form_state['generated_audio_path'] = audio_path
                        
                        # Add to playlist
                        st.session_state.current_playlist.append(snippet)
                        
                        # Add to session
                        st.session_state.session.add_snippet(snippet)
                        
                        # Show success message
                        st.success(get_translation('content_saved', st.session_state.language))
                        
                        # Track event
                        track_event("snippet_saved", {
                            "topic": topic,
                            "language": selected_language
                        })
                        
                        # Celebration effect
                        rain(
                            emoji="🎉",
                            font_size=54,
                            falling_speed=5,
                            animation_length=1,
                        )
                    else:
                        st.info("This content is already in your library.")
        
        # Display content editor if editing
        if st.session_state.create_form_state.get('editing'):
            st.text_area(
                "Edit Content",
                value=snippet['content'],
                height=300,
                key="content_editor"
            )
            
            if st.button("Save Edits"):
                # Update snippet content
                snippet['content'] = st.session_state.content_editor
                st.session_state.create_form_state['generated_content'] = snippet
                st.session_state.create_form_state['editing'] = False
                
                # Reset audio path to regenerate with new content
                st.session_state.create_form_state['generated_audio_path'] = None
                
                # Show success message
                st.success("Content updated successfully.")
                st.rerun()
        
        # Display audio player if generating or generated
        if st.session_state.create_form_state['audio_generating'] or st.session_state.create_form_state['generated_audio_path']:
            st.divider()
            st.markdown("## " + get_translation('preview_audio', st.session_state.language))
            
            # Generate audio if not already generated
            if st.session_state.create_form_state['audio_generating'] and not st.session_state.create_form_state['generated_audio_path']:
                with st.spinner(get_translation('generating_audio', st.session_state.language)):
                    audio_path = generate_audio(
                        snippet['content'],
                        snippet['title'],
                        selected_language,
                        st.session_state.create_form_state['voice_index']
                    )
                    
                    if audio_path:
                        # Get audio duration
                        duration = get_audio_duration(audio_path)
                        
                        # Save audio metadata
                        audio_metadata = save_audio_metadata(snippet['id'], audio_path, duration)
                        
                        # Update snippet with audio information
                        snippet['audio_path'] = audio_path
                        snippet['audio_duration'] = duration
                        
                        # Store generated audio path
                        st.session_state.create_form_state['generated_audio_path'] = audio_path
                        st.session_state.create_form_state['audio_generating'] = False
                        
                        # Update generated content
                        st.session_state.create_form_state['generated_content'] = snippet
                        
                        # Track event
                        track_event("audio_generated", {
                            "topic": topic,
                            "language": selected_language,
                            "success": True
                        })
                        
                        # Rerun to show audio player
                        st.rerun()
                    else:
                        # Handle error
                        st.error(get_translation('error_audio', st.session_state.language))
                        st.session_state.create_form_state['audio_generating'] = False
                        
                        # Track event
                        track_event("audio_generated", {
                            "topic": topic,
                            "language": selected_language,
                            "success": False
                        })
            
            # Display audio player if audio path is available
            if st.session_state.create_form_state['generated_audio_path']:
                audio_player = AudioPlayer()
                audio_player.render(
                    audio_path=st.session_state.create_form_state['generated_audio_path'],
                    title=snippet['title']
                )
    
    # Reset button at the bottom
    if st.session_state.create_form_state['generated_content']:
        if st.button(get_translation('regenerate', st.session_state.language), key="reset_button"):
            # Reset form state but keep topic and options
            topic = st.session_state.create_form_state['topic']
            length = st.session_state.create_form_state['length']
            language = st.session_state.create_form_state['language']
            voice_index = st.session_state.create_form_state['voice_index']
            
            st.session_state.create_form_state = {
                'topic': topic,
                'length': length,
                'language': language,
                'voice_index': voice_index,
                'generated_content': None,
                'generated_audio_path': None,
                'generating': False,
                'audio_generating': False,
                'error': None
            }
            
            # Rerun to reset the form
            st.rerun()

if __name__ == "__main__":
    app()