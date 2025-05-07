import streamlit as st
from typing import Dict, List, Any, Optional, Callable, Union
import random

def render_topic_card(topic: str, 
                    description: Optional[str] = None, 
                    image: Optional[str] = None,
                    on_click: Optional[Callable] = None,
                    key_prefix: str = "topic_card"):
    """
    Render a card for a topic
    
    Args:
        topic (str): Topic title
        description (str, optional): Topic description
        image (str, optional): URL or path to image
        on_click (callable, optional): Function to call when card is clicked
        key_prefix (str): Prefix for component keys
    """
    # Generate random key suffix for uniqueness
    key = f"{key_prefix}_{random.randint(1000, 9999)}"
    
    # Define card style
    card_style = """
    <style>
    .topic-card {
        background-color: #282828;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #1DB954;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .topic-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
    }
    .topic-card h3 {
        margin-top: 0;
        color: white;
    }
    .topic-card p {
        color: #cccccc;
        font-size: 0.9rem;
    }
    </style>
    """
    
    # Card HTML
    card_html = f"""
    <div class="topic-card" id="{key}">
        <h3>{topic}</h3>
        {"" if not description else f"<p>{description}</p>"}
    </div>
    """
    
    # Render card
    st.markdown(card_style, unsafe_allow_html=True)
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Handle click if callback provided
    if on_click and st.button("Select", key=f"{key}_button"):
        on_click(topic)

def render_snippet_card(snippet: Dict[str, Any],
                      on_play: Optional[Callable] = None,
                      on_view: Optional[Callable] = None,
                      on_quiz: Optional[Callable] = None,
                      show_quiz_button: bool = True,
                      key_prefix: str = "snippet_card"):
    """
    Render a card for an audio snippet
    
    Args:
        snippet (dict): Snippet data (title, content, audio_path, etc.)
        on_play (callable, optional): Function to call when play button is clicked
        on_view (callable, optional): Function to call when view button is clicked
        on_quiz (callable, optional): Function to call when quiz button is clicked
        show_quiz_button (bool): Whether to show the quiz button
        key_prefix (str): Prefix for component keys
    """
    # Generate random key suffix for uniqueness
    key = f"{key_prefix}_{random.randint(1000, 9999)}"
    
    # Extract snippet data
    title = snippet.get('title', 'Untitled Snippet')
    topic = snippet.get('topic', '')
    duration = snippet.get('audio_duration', 0)
    language = snippet.get('language', 'en')
    
    # Format duration
    if duration:
        duration_min = int(duration // 60)
        duration_sec = int(duration % 60)
        duration_str = f"{duration_min}:{duration_sec:02d}"
    else:
        duration_str = "—:—"
    
    # Card container
    with st.container():
        col1, col2 = st.columns([7, 3])
        
        with col1:
            st.markdown(f"### {title}")
            st.markdown(f"**Topic:** {topic}")
            st.markdown(f"**Duration:** {duration_str} | **Language:** {language.upper()}")
        
        with col2:
            # Play button
            if on_play and st.button("▶️ Play", key=f"{key}_play"):
                on_play(snippet)
            
            # View details button
            if on_view and st.button("👁️ View", key=f"{key}_view"):
                on_view(snippet)
            
            # Quiz button (optional)
            if show_quiz_button and on_quiz and st.button("❓ Quiz", key=f"{key}_quiz"):
                on_quiz(snippet)
        
        # Add a divider
        st.markdown("---")

def render_quiz_card(question: Dict[str, Any],
                   on_answer: Optional[Callable] = None,
                   show_answer: bool = False,
                   key_prefix: str = "quiz_card"):
    """
    Render a card for a quiz question
    
    Args:
        question (dict): Question data (question, options, answer, explanation)
        on_answer (callable, optional): Function to call when an answer is selected
        show_answer (bool): Whether to show the correct answer
        key_prefix (str): Prefix for component keys
    """
    # Generate random key suffix for uniqueness
    key = f"{key_prefix}_{random.randint(1000, 9999)}"
    
    # Extract question data
    question_text = question.get('question', 'No question text')
    options = question.get('options', {})
    correct_answer = question.get('answer', '')
    explanation = question.get('explanation', '')
    
    # Card container
    with st.container():
        # Question
        st.markdown(f"### {question_text}")
        
        # Options as radio buttons
        selected_option = st.radio(
            "Select your answer:",
            options.keys(),
            format_func=lambda x: f"{x}: {options.get(x, '')}",
            key=f"{key}_options"
        )
        
        # Check answer button
        if on_answer and st.button("Submit Answer", key=f"{key}_submit"):
            on_answer(selected_option)
        
        # Show answer if requested
        if show_answer:
            if selected_option == correct_answer:
                st.success(f"✅ Correct! The answer is {correct_answer}: {options.get(correct_answer, '')}")
            else:
                st.error(f"❌ Incorrect. The correct answer is {correct_answer}: {options.get(correct_answer, '')}")
            
            # Show explanation if available
            if explanation:
                st.info(f"**Explanation:** {explanation}")
        
        # Add a divider
        st.markdown("---")

def render_playlist_card(playlist: Dict[str, Any],
                       on_play: Optional[Callable] = None,
                       on_view: Optional[Callable] = None,
                       key_prefix: str = "playlist_card"):
    """
    Render a card for a playlist
    
    Args:
        playlist (dict): Playlist data (name, description, snippets)
        on_play (callable, optional): Function to call when play button is clicked
        on_view (callable, optional): Function to call when view button is clicked
        key_prefix (str): Prefix for component keys
    """
    # Generate random key suffix for uniqueness
    key = f"{key_prefix}_{random.randint(1000, 9999)}"
    
    # Extract playlist data
    name = playlist.get('name', 'Untitled Playlist')
    description = playlist.get('description', '')
    snippets = playlist.get('snippets', [])
    
    # Calculate total duration
    total_duration = sum(snippet.get('audio_duration', 0) for snippet in snippets)
    total_duration_min = int(total_duration // 60)
    
    # Card container
    with st.container():
        col1, col2 = st.columns([7, 3])
        
        with col1:
            st.markdown(f"### {name}")
            if description:
                st.markdown(description)
            st.markdown(f"**Tracks:** {len(snippets)} | **Duration:** {total_duration_min} min")
        
        with col2:
            # Play button
            if on_play and st.button("▶️ Play All", key=f"{key}_play"):
                on_play(playlist)
            
            # View details button
            if on_view and st.button("👁️ View", key=f"{key}_view"):
                on_view(playlist)
        
        # Show snippet list (collapsed)
        if snippets:
            with st.expander("View tracks"):
                for i, snippet in enumerate(snippets):
                    st.markdown(f"**{i+1}.** {snippet.get('title', 'Untitled')}")
        
        # Add a divider
        st.markdown("---")

def render_achievement_card(achievement: Dict[str, Any],
                         is_completed: bool = False,
                         key_prefix: str = "achievement_card"):
    """
    Render a card for an achievement
    
    Args:
        achievement (dict): Achievement data (name, description, points)
        is_completed (bool): Whether the achievement is completed
        key_prefix (str): Prefix for component keys
    """
    # Generate random key suffix for uniqueness
    key = f"{key_prefix}_{random.randint(1000, 9999)}"
    
    # Extract achievement data
    name = achievement.get('name', 'Untitled Achievement')
    description = achievement.get('description', '')
    points = achievement.get('points', 0)
    
    # Define card style based on completion status
    border_color = "#1DB954" if is_completed else "#555555"
    
    # Card container
    with st.container():
        # Style with custom HTML/CSS
        st.markdown(f"""
        <div style="background-color: #282828; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 5px solid {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin-top: 0; margin-bottom: 5px;">{name}</h3>
                    <p style="color: #cccccc; margin-top: 0;">{description}</p>
                </div>
                <div style="text-align: center;">
                    <div style="background-color: #1DB954; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-weight: bold;">{points}</span>
                    </div>
                    <div style="font-size: 12px; margin-top: 5px;">{"Completed" if is_completed else "Locked"}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_learning_path_card(path: Dict[str, Any],
                           progress: float = 0.0,
                           on_start: Optional[Callable] = None,
                           on_continue: Optional[Callable] = None,
                           key_prefix: str = "path_card"):
    """
    Render a card for a learning path
    
    Args:
        path (dict): Learning path data (name, description, stages)
        progress (float): Progress percentage (0.0-1.0)
        on_start (callable, optional): Function to call when start button is clicked
        on_continue (callable, optional): Function to call when continue button is clicked
        key_prefix (str): Prefix for component keys
    """
    # Generate random key suffix for uniqueness
    key = f"{key_prefix}_{random.randint(1000, 9999)}"
    
    # Extract path data
    name = path.get('name', 'Untitled Path')
    description = path.get('description', '')
    difficulty = path.get('difficulty', 'beginner')
    estimated_time = path.get('estimated_time', '')
    stages = path.get('stages', [])
    
    # Format progress percentage
    progress_percent = int(progress * 100)
    
    # Card container
    with st.container():
        st.markdown(f"### {name}")
        
        # Path metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Difficulty:** {difficulty.title()}")
        with col2:
            st.markdown(f"**Stages:** {len(stages)}")
        with col3:
            st.markdown(f"**Time:** {estimated_time}")
        
        # Description
        st.markdown(description)
        
        # Progress bar
        st.progress(progress)
        st.markdown(f"**Progress:** {progress_percent}% complete")
        
        # Action buttons
        if progress == 0:
            # Not started
            if on_start and st.button("🚀 Start Path", key=f"{key}_start"):
                on_start(path)
        else:
            # In progress
            if on_continue and st.button("▶️ Continue Learning", key=f"{key}_continue"):
                on_continue(path)
            
        # Add a divider
        st.markdown("---")