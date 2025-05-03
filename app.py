import streamlit as st
import time
import os
import uuid
from utils.llm_utils import generate_learning_snippet, generate_recommendation
from utils.audio_utils import generate_audio, get_audio_duration
from utils.data_utils import UserSession, save_audio_metadata
from templates.recommendation_templates import get_trending_topics, get_topic_categories
from config import APP_TITLE, APP_DESCRIPTION, AUDIO_DIR, AVAILABLE_LANGUAGES
from utils.language_utils import get_translation, set_language

# Configuration de la page Streamlit
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎧",
    layout="wide",
)

# CSS personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stButton > button {
        background-color: #1DB954;
        color: white;
        border-radius: 24px;
        padding: 8px 32px;
        font-weight: bold;
    }
    .playlist-item {
        background-color: #282828;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .snippet-title {
        font-size: 18px;
        font-weight: bold;
        color: #FFFFFF;
    }
    .snippet-duration {
        font-size: 14px;
        color: #B3B3B3;
    }
    .language-selector {
        position: absolute;
        top: 0;
        right: 10px;
        z-index: 1000;
    }
    /* Support RTL pour l'arabe */
    [dir="rtl"] .main, [dir="rtl"] .snippet-title, [dir="rtl"] .playlist-item {
        direction: rtl;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialisation de la session
if 'session' not in st.session_state:
    st.session_state.session = UserSession()

if 'current_playlist' not in st.session_state:
    st.session_state.current_playlist = []

# Initialisation de la langue
if 'language' not in st.session_state:
    st.session_state.language = 'fr'

def create_playlist(topics, duration_per_topic=5):
    """
    Crée une playlist de snippets d'apprentissage basés sur les sujets fournis.
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Starting playlist creation for topics: {topics}, duration_per_topic: {duration_per_topic}")
    
    playlist = []
    seen_snippet_ids = set()  # Track unique snippet IDs
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, topic in enumerate(topics):
        progress = (i) / len(topics)
        progress_bar.progress(progress)
        status_text.text(f"{get_translation('generating_snippet', st.session_state.language)} {i+1}/{len(topics)}: {topic}")
        logger.info(f"Generating snippet {i+1}/{len(topics)} for topic: {topic}")
        
        snippet = generate_learning_snippet(topic, duration_per_topic, st.session_state.language)
        if snippet['id'] in seen_snippet_ids:
            logger.warning(f"Duplicate snippet ID {snippet['id']} for topic {topic}, skipping")
            continue
        seen_snippet_ids.add(snippet['id'])
        logger.info(f"Snippet generated: ID={snippet['id']}, Title={snippet['title']}")
        
        status_text.text(f"{get_translation('converting_to_audio', st.session_state.language)}: {snippet['title']}")
        audio_path = generate_audio(snippet['content'], snippet['title'], st.session_state.language)
        logger.info(f"Audio generated for snippet ID={snippet['id']}: {audio_path}")
        
        if audio_path:
            duration = get_audio_duration(audio_path)
            audio_metadata = save_audio_metadata(snippet['id'], audio_path, duration)
            
            snippet['audio_path'] = audio_path
            snippet['audio_duration'] = duration
            
            playlist.append(snippet)
            st.session_state.session.add_snippet(snippet)
            logger.info(f"Snippet added to playlist: ID={snippet['id']}")
        else:
            logger.warning(f"No audio generated for snippet ID={snippet['id']}")
    
    progress_bar.progress(1.0)
    status_text.text(get_translation('playlist_generated_success', st.session_state.language))
    logger.info(f"Playlist creation complete: {len(playlist)} snippets")
    
    return playlist

def parse_user_input(input_text):
    """
    Analyse l'entrée utilisateur pour extraire une liste de sujets.
    """
    lines = input_text.strip().split('\n')
    topics = []
    
    for line in lines:
        line = line.strip()
        if line:
            if line.startswith('-') or line.startswith('*'):
                line = line[1:].strip()
            
            if line[0].isdigit() and line[1:3] in ['. ', ') ']:
                line = line[3:].strip()
                
            if line and line not in topics:  # Avoid duplicates
                topics.append(line)
    
    return topics

def display_playlist(playlist):
    """
    Affiche la playlist avec des contrôles de lecture.
    """
    st.subheader(get_translation('your_learning_playlist', st.session_state.language))
    
    for i, snippet in enumerate(playlist):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div class="playlist-item">
                <div class="snippet-title">{i+1}. {snippet['title']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.audio(snippet['audio_path'])
            
            with st.expander(get_translation('view_text_content', st.session_state.language)):
                st.write(snippet['content'])
        
        with col2:
            st.download_button(
            label=get_translation('download', st.session_state.language),
            data=open(snippet['audio_path'], 'rb'),
            file_name=f"{snippet['title']}.mp3",
            mime="audio/mp3",
            key=f"download_{snippet['id']}"  # Add unique key using snippet ID
        )

def language_selector():
    """
    Affiche un sélecteur de langue dans la barre latérale.
    """
    st.sidebar.title(get_translation('language', st.session_state.language))
    language = st.sidebar.selectbox(
        get_translation('select_language', st.session_state.language),
        options=list(AVAILABLE_LANGUAGES.keys()),
        format_func=lambda x: AVAILABLE_LANGUAGES[x],
        index=list(AVAILABLE_LANGUAGES.keys()).index(st.session_state.language)
    )
    
    if language != st.session_state.language:
        st.session_state.language = language
        set_language(language)
        st.rerun()

def main():
    # Appliquer la direction RTL pour l'arabe
    if st.session_state.language == 'ar':
        st.markdown('<div dir="rtl">', unsafe_allow_html=True)

    # Sélecteur de langue
    language_selector()
    
    st.title("🎧 " + get_translation('app_title', st.session_state.language))
    st.markdown(get_translation('app_description', st.session_state.language))
    
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    
    tab1, tab2, tab3 = st.tabs([
        get_translation('create_playlist_tab', st.session_state.language), 
        get_translation('my_library_tab', st.session_state.language), 
        get_translation('discover_tab', st.session_state.language)
    ])
    
    with tab1:
        st.header(get_translation('create_custom_playlist', st.session_state.language))
        
        user_input = st.text_area(
            get_translation('enter_topics', st.session_state.language),
            value=st.session_state.user_input,
            height=150,
            placeholder=get_translation('topics_example', st.session_state.language)
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            duration_per_topic = st.slider(
                get_translation('duration_per_topic', st.session_state.language),
                min_value=3,
                max_value=10,
                value=5,
                step=1,
                key="duration_per_topic_slider"
            )
        
        with col2:
            total_duration = st.empty()
            if user_input:
                topics = parse_user_input(user_input)
                estimated_time = len(topics) * duration_per_topic
                total_duration.info(f"{get_translation('estimated_total_duration', st.session_state.language)}: {estimated_time} {get_translation('minutes', st.session_state.language)}")
        
        if 'playlist_generated' not in st.session_state:
            st.session_state.playlist_generated = False
        
        if st.button(get_translation('generate_playlist', st.session_state.language), key="generate_playlist_button"):
            if user_input:
                topics = parse_user_input(user_input)
                if topics and not st.session_state.playlist_generated:
                    with st.spinner(get_translation('generating_custom_playlist', st.session_state.language)):
                        playlist = create_playlist(topics, duration_per_topic)
                        st.session_state.current_playlist = playlist
                        st.session_state.playlist_generated = True
                        st.session_state.user_input = user_input  # Preserve input
                        st.success(get_translation('playlist_generated_success', st.session_state.language))
                        time.sleep(1)  # Prevent rapid rerun
                        st.rerun()
                elif st.session_state.playlist_generated:
                    st.warning(get_translation('playlist_already_generated', st.session_state.language))
                else:
                    st.error(get_translation('enter_at_least_one_topic', st.session_state.language))
            else:
                st.error(get_translation('enter_at_least_one_topic', st.session_state.language))
        
        if st.session_state.session.history:
            st.subheader(get_translation('you_might_also_like', st.session_state.language))
            recent_topics = st.session_state.session.get_recent_topics()
            recommendations = generate_recommendation(recent_topics, 3, st.session_state.language)
            
            for i, rec in enumerate(recommendations):
                st.markdown(f"""
                <div style="background-color: #282828; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                    {rec}
                </div>
                """, unsafe_allow_html=True)
                
                if 'added_recommendations' not in st.session_state:
                    st.session_state.added_recommendations = set()

                if st.button(f"{get_translation('add_to_list', st.session_state.language)}", key=f"add_rec_{i}"):
                    if rec not in st.session_state.added_recommendations:
                        current_input = user_input.strip()
                        new_input = current_input + f"\n- {rec}" if current_input else f"- {rec}"
                        st.session_state.user_input = new_input
                        st.session_state.added_recommendations.add(rec)
                        st.success(f"'{rec}' {get_translation('added_to_playlist', st.session_state.language)}")
                    else:
                        st.warning(f"'{rec}' {get_translation('already_added', st.session_state.language)}")

    
    with tab2:
        st.header(get_translation('my_learning_library', st.session_state.language))
        
        if st.session_state.current_playlist:
            display_playlist(st.session_state.current_playlist)
        elif st.session_state.session.snippets:
            display_playlist(st.session_state.session.get_playlist())
        else:
            st.info(get_translation('no_playlist_yet', st.session_state.language))
    
    with tab3:
        st.header(get_translation('discover_new_topics', st.session_state.language))
        
        categories = get_topic_categories(st.session_state.language)
        
        for category, topics in categories.items():
            with st.expander(category):  # Remove key=f"expander_{category}"
                for topic in topics:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="background-color: #282828; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                            {topic}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button(get_translation('add', st.session_state.language), key=f"add_{category}_{topic}"):
                            if f"topic_added_{topic}" not in st.session_state:
                                with st.spinner(f"{get_translation('generating_snippet', st.session_state.language)} {topic}..."):
                                    playlist = create_playlist([topic], duration_per_topic=5)
                                    if 'current_playlist' in st.session_state:
                                        st.session_state.current_playlist.extend(playlist)
                                    else:
                                        st.session_state.current_playlist = playlist
                                    st.session_state[f"topic_added_{topic}"] = True
                                    st.success(f"'{topic}' {get_translation('added_to_playlist', st.session_state.language)}")
                                    time.sleep(1)  # Prevent rapid rerun
                                    st.rerun()
                            else:
                                st.warning(f"'{topic}' {get_translation('already_added', st.session_state.language)}")
        # Fermer la div RTL si nécessaire
    if st.session_state.language == 'ar':
        st.markdown('</div>', unsafe_allow_html=True)



if __name__ == "__main__":
    main()