import streamlit as st
import asyncio
import time
import pandas as pd
import plotly.express as px
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.let_it_rain import rain
from streamlit_lottie import st_lottie
import requests
import json
import random

from utils.llm_utils import generate_learning_snippet, generate_recommendation
from utils.audio_utils import generate_audio, get_audio_duration
from utils.data_utils import track_event, save_audio_metadata
from utils.language_utils import get_translation
from templates.recommendation_templates import get_trending_topics, get_topic_categories, get_curated_playlists
from config import DEFAULT_SNIPPET_DURATION

def app():
    """Discover page with topic recommendations and exploration tools"""
    
    # Get session state
    if 'session' not in st.session_state:
        st.error("Session not initialized. Please return to the home page.")
        if st.button("Go to Home"):
            switch_page("app")
        return
    
    if 'current_playlist' not in st.session_state:
        st.session_state.current_playlist = []
    
    # Page title with animation
    colored_header(
        label=get_translation('discover_new_topics', st.session_state.language),
        description=get_translation('explore_and_expand', st.session_state.language),
        color_name="blue-70"
    )
    
    # Try to load lottie animation
    try:
        with open('static/img/explore-animation.json', 'r') as f:
            lottie_data = json.load(f)
    except:
        # Fallback to URL if file doesn't exist
        try:
            lottie_url = "https://assets3.lottiefiles.com/packages/lf20_khzniaya.json"
            lottie_data = requests.get(lottie_url).json()
        except:
            lottie_data = None
    
    # Display animation if available
    if lottie_data:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st_lottie(lottie_data, height=200, key="lottie")
    
    # Main discover tabs
    tabs = st.tabs([
        "Categories", 
        "Trending Topics", 
        "Curated Playlists", 
        "Interactive Explorer",
        "Learning Paths"
    ])
    
    with tabs[0]:
        display_categories()
    
    with tabs[1]:
        display_trending_topics()
    
    with tabs[2]:
        display_curated_playlists()
    
    with tabs[3]:
        display_interactive_explorer()
    
    with tabs[4]:
        display_learning_paths()

def display_categories():
    """Display topic categories"""
    
    # Get categories for the current language
    categories = get_topic_categories(st.session_state.language)
    
    # Create tabs for each category
    category_tabs = st.tabs(list(categories.keys()))
    
    for i, (category, topics) in enumerate(categories.items()):
        with category_tabs[i]:
            # Display category description
            st.markdown(get_category_description(category))
            
            # Display topics with visual cards
            display_topics_grid(topics, 3, key_prefix=f"category_{category}")

def display_trending_topics():
    """Display trending topics"""
    
    # Get trending topics for the current language
    trending = get_trending_topics(st.session_state.language)
    
    # Add visual header
    st.subheader("📈 " + get_translation('trending_now', st.session_state.language))
    st.markdown(get_translation('trending_description', st.session_state.language))
    
    # Display trending topics visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create data for visualization
        df = pd.DataFrame({
            'Topic': trending[:8],
            'Popularity': [random.randint(50, 100) for _ in range(min(8, len(trending)))]
        })
        
        # Sort by popularity
        df = df.sort_values('Popularity', ascending=False)
        
        # Create horizontal bar chart
        fig = px.bar(
            df, 
            x='Popularity', 
            y='Topic',
            orientation='h',
            color='Popularity',
            color_continuous_scale=px.colors.sequential.Viridis,
            title="Trending Topics"
        )
        
        # Update layout
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title=None,
            yaxis_title=None
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader(get_translation('add_trending_topics', st.session_state.language))
        
        # Create a multi-select for trending topics
        selected_topics = st.multiselect(
            get_translation('select_topics', st.session_state.language),
            trending,
            key="trending_topics_select"
        )
        
        # Add button for selected topics
        if selected_topics and st.button(get_translation('add_selected', st.session_state.language), key="add_trending"):
            with st.spinner(get_translation('generating_snippets', st.session_state.language)):
                add_topics_to_playlist(selected_topics)

def display_curated_playlists():
    """Display curated playlists"""
    
    # Get curated playlists for the current language
    curated = get_curated_playlists(st.session_state.language)
    
    # Display each playlist as an expander
    for playlist_name, topics in curated.items():
        with st.expander(playlist_name, expanded=False):
            # Display playlist details
            total_duration = len(topics) * DEFAULT_SNIPPET_DURATION
            st.markdown(f"**{len(topics)} topics • {total_duration} mins**")
            
            # Display topics
            for i, topic in enumerate(topics):
                st.markdown(f"{i+1}. {topic}")
            
            # Add playlists controls
            col1, col2 = st.columns(2)
            
            with col1:
                # Preview button shows topics in a more visual way
                if st.button(get_translation('preview', st.session_state.language), key=f"preview_{playlist_name}"):
                    st.session_state.preview_playlist = {
                        'name': playlist_name,
                        'topics': topics
                    }
                    st.rerun()
            
            with col2:
                # Add all button adds all topics to the playlist
                if st.button(get_translation('add_all', st.session_state.language), key=f"add_all_{playlist_name}"):
                    with st.spinner(get_translation('generating_snippets', st.session_state.language)):
                        add_topics_to_playlist(topics)
                        
                        # Track event
                        track_event("curated_playlist_selected", {
                            "playlist_name": playlist_name,
                            "topic_count": len(topics),
                            "language": st.session_state.language
                        })
                        
                        # Create a celebratory effect
                        rain(
                            emoji="🎉",
                            font_size=54,
                            falling_speed=5,
                            animation_length=1,
                        )
    
    # Display playlist preview if selected
    if 'preview_playlist' in st.session_state:
        st.divider()
        st.subheader(f"Preview: {st.session_state.preview_playlist['name']}")
        
        # Display topics in a more visual way
        display_topics_grid(st.session_state.preview_playlist['topics'], 4, key_prefix=f"preview_{st.session_state.preview_playlist['name']}")
        
        # Add button to add all from preview
        if st.button(get_translation('add_all_from_preview', st.session_state.language)):
            with st.spinner(get_translation('generating_snippets', st.session_state.language)):
                add_topics_to_playlist(st.session_state.preview_playlist['topics'])
                
                # Close preview
                st.session_state.pop('preview_playlist')
                st.rerun()
        
        # Close preview
        if st.button(get_translation('close_preview', st.session_state.language)):
            st.session_state.pop('preview_playlist')
            st.rerun()

def display_interactive_explorer():
    """Display interactive topic explorer with recommendations"""
    
    st.subheader("🧭 " + get_translation('interactive_explorer', st.session_state.language))
    st.markdown(get_translation('explorer_description', st.session_state.language))
    
    # Initialize explorer state
    if 'explorer_state' not in st.session_state:
        st.session_state.explorer_state = {
            'seed_topic': "",
            'recommendations': [],
            'history': [],
            'selected_topic': None
        }
    
    # Input for seed topic
    col1, col2 = st.columns([3, 1])
    
    with col1:
        seed_topic = st.text_input(
            get_translation('enter_topic', st.session_state.language),
            value=st.session_state.explorer_state['seed_topic'],
            key="explorer_seed"
        )
    
    with col2:
        if st.button(get_translation('explore', st.session_state.language), key="explorer_button"):
            if seed_topic:
                st.session_state.explorer_state['seed_topic'] = seed_topic
                st.session_state.explorer_state['history'].append(seed_topic)
                
                # Get recommendations
                with st.spinner(get_translation('generating_recommendations', st.session_state.language)):
                    run_interactive_exploration(seed_topic)
    
    # Display recommendations
    if st.session_state.explorer_state['recommendations']:
        st.divider()
        st.subheader(get_translation('related_topics', st.session_state.language))
        
        # Display recommendations in an interactive grid
        display_topics_grid(st.session_state.explorer_state['recommendations'], 3, key_prefix="explorer", explorer_mode=True)
    
    # Display exploration history
    if len(st.session_state.explorer_state['history']) > 1:
        st.divider()
        st.subheader(get_translation('exploration_history', st.session_state.language))
        
        # Display as a flowchart
        history = st.session_state.explorer_state['history']
        
        # Create nodes and edges for diagram
        nodes = [{"id": i, "label": topic} for i, topic in enumerate(history)]
        edges = [{"from": i, "to": i+1} for i in range(len(history)-1)]
        
        # Display as a list with option to jump back
        for i, topic in enumerate(history):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"{i+1}. **{topic}**")
            
            with col2:
                if i < len(history) - 1:  # Not the current topic
                    if st.button(get_translation('jump_back', st.session_state.language), key=f"jump_{i}"):
                        # Truncate history and re-explore
                        st.session_state.explorer_state['history'] = history[:i+1]
                        st.session_state.explorer_state['seed_topic'] = topic
                        run_interactive_exploration(topic)
                        st.rerun()

def display_learning_paths():
    """Display learning paths for guided learning"""
    
    st.subheader("🛤️ " + get_translation('learning_paths', st.session_state.language))
    st.markdown(get_translation('learning_paths_description', st.session_state.language))
    
    # Define some learning paths
    learning_paths = {
        "Data Science Fundamentals": [
            "Introduction to Statistics",
            "Basics of Python Programming",
            "Data Visualization Principles",
            "Introduction to Machine Learning",
            "Data Cleaning Techniques"
        ],
        "Web Development Journey": [
            "HTML and CSS Basics",
            "JavaScript Fundamentals",
            "Responsive Web Design",
            "Introduction to React",
            "Backend Basics with Node.js"
        ],
        "Financial Literacy": [
            "Understanding Personal Finance",
            "Introduction to Investing",
            "Budgeting Strategies",
            "Retirement Planning Basics",
            "Understanding Credit Scores"
        ],
        "Sustainable Living": [
            "Introduction to Sustainability",
            "Reducing Household Waste",
            "Sustainable Food Choices",
            "Energy Conservation at Home",
            "Ethical Consumption Practices"
        ]
    }
    
    # Display learning paths
    path_cols = st.columns(2)
    
    for i, (path_name, topics) in enumerate(learning_paths.items()):
        with path_cols[i % 2]:
            st.markdown(f"### {path_name}")
            
            # Progress visualization
            progress = 0
            
            # Create progress visualization
            progress_html = f"""
            <div style="background-color: #383838; border-radius: 10px; height: 20px; width: 100%; margin-bottom: 10px;">
                <div style="background-color: #1DB954; border-radius: 10px; height: 20px; width: {progress}%;"></div>
            </div>
            <p>{progress}% Complete</p>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
            
            # Display path topics with step numbers
            for j, topic in enumerate(topics):
                st.markdown(f"**Step {j+1}:** {topic}")
            
            # Add button for this path
            if st.button(get_translation('start_path', st.session_state.language), key=f"path_{i}"):
                with st.spinner(get_translation('preparing_path', st.session_state.language)):
                    # Generate first topic in the path
                    add_topics_to_playlist([topics[0]])
                    
                    # Track event
                    track_event("learning_path_started", {
                        "path_name": path_name,
                        "topic_count": len(topics),
                        "language": st.session_state.language
                    })
                    
                    # Show success message
                    st.success(get_translation('path_started', st.session_state.language))
                    
                    # Create a celebratory effect
                    rain(
                        emoji="🚀",
                        font_size=54,
                        falling_speed=5,
                        animation_length=1,
                    )

def display_topics_grid(topics, columns, key_prefix="topic_grid", explorer_mode=False):
    """Display topics in a grid layout with visual cards"""
    
    # Create columns
    cols = st.columns(columns)
    
    for i, topic in enumerate(topics):
        with cols[i % columns]:
            # Create card style
            st.markdown(f"""
            <div style="background-color: #282828; border-radius: 10px; padding: 15px; 
                margin-bottom: 15px; border-left: 5px solid #1DB954;">
                <h3 style="margin-top: 0;">{topic}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Add button functionality
            if explorer_mode:
                # In explorer mode, clicking explores related topics
                if st.button(get_translation('explore_this', st.session_state.language), key=f"{key_prefix}_explore_topic_{topic}_{i}"):
                    st.session_state.explorer_state['seed_topic'] = topic
                    st.session_state.explorer_state['history'].append(topic)
                    
                    with st.spinner(get_translation('exploring', st.session_state.language)):
                        run_interactive_exploration(topic)
                        st.rerun()
                
                # Add to playlist button
                if st.button(get_translation('add_to_playlist', st.session_state.language), key=f"{key_prefix}_add_explore_{topic}_{i}"):
                    with st.spinner(get_translation('generating_snippet', st.session_state.language)):
                        add_topics_to_playlist([topic])
            else:
                # Regular add button
                if st.button(get_translation('add', st.session_state.language), key=f"{key_prefix}_add_topic_{topic}_{i}"):
                    with st.spinner(get_translation('generating_snippet', st.session_state.language)):
                        add_topics_to_playlist([topic])

def add_topics_to_playlist(topics):
    """Add topics to the playlist"""
    
    # Track event
    track_event("topics_added", {
        "topic_count": len(topics),
        "topics": topics,
        "language": st.session_state.language
    })
    
    # Run loop to handle async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Create snippets for each topic
        for topic in topics:
            with st.spinner(f"{get_translation('generating_snippet', st.session_state.language)} {topic}..."):
                # Generate snippet
                snippet = loop.run_until_complete(generate_learning_snippet(
                    topic, 
                    DEFAULT_SNIPPET_DURATION, 
                    st.session_state.language
                ))
                
                if snippet:
                    # Generate audio
                    audio_path = generate_audio(
                        snippet['content'], 
                        snippet['title'], 
                        st.session_state.language
                    )
                    
                    if audio_path:
                        # Get audio duration
                        duration = get_audio_duration(audio_path)
                        
                        # Save audio metadata
                        audio_metadata = save_audio_metadata(snippet['id'], audio_path, duration)
                        
                        # Update snippet with audio information
                        snippet['audio_path'] = audio_path
                        snippet['audio_duration'] = duration
                        
                        # Add to playlist and session
                        if 'current_playlist' in st.session_state:
                            st.session_state.current_playlist.append(snippet)
                        else:
                            st.session_state.current_playlist = [snippet]
                            
                        # Add to session
                        st.session_state.session.add_snippet(snippet)
                        
                        # Show success message
                        st.success(f"'{topic}' {get_translation('added_to_playlist', st.session_state.language)}")
                    else:
                        st.error(f"Failed to generate audio for '{topic}'")
                else:
                    st.error(f"Failed to generate snippet for '{topic}'")
    finally:
        loop.close()
    
    return True

def run_interactive_exploration(topic):
    """Run interactive exploration for a topic"""
    
    # Run loop to handle async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Generate recommendations
        recommendations = loop.run_until_complete(generate_recommendation(
            [topic], 
            6, 
            st.session_state.language
        ))
        
        # Update explorer state
        st.session_state.explorer_state['recommendations'] = recommendations
        
        # Track event
        track_event("topic_explored", {
            "topic": topic,
            "language": st.session_state.language
        })
    finally:
        loop.close()
    
    return True

def get_category_description(category):
    """Get description for a category"""
    
    descriptions = {
        "Science": "Explore the wonders of the natural world, from quantum physics to biology and beyond.",
        "History": "Journey through time and discover the events and people that shaped our world.",
        "Technology": "Learn about cutting-edge innovations and the fundamentals of our digital world.",
        "Arts & Culture": "Dive into the rich tapestry of human creativity and expression.",
        "Health & Wellness": "Discover ways to improve your physical and mental wellbeing.",
        "Environment & Sustainability": "Learn about our planet and how to protect it for future generations.",
        "Psychology & Behavior": "Understand the human mind and what drives our actions and decisions.",
        "Business & Economics": "Explore how markets work and the principles behind successful organizations.",
        "Philosophy & Ethics": "Contemplate the big questions about existence, knowledge, and morality.",
        "Language & Communication": "Discover the fascinating world of languages and effective communication.",
    }
    
    # Default description if category not found
    return descriptions.get(category, f"Explore interesting topics in {category}.")

if __name__ == "__main__":
    app()