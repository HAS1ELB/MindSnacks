import streamlit as st
import time
import os
import uuid
from utils.llm_utils import generate_learning_snippet, generate_recommendation
from utils.audio_utils import generate_audio, get_audio_duration
from utils.data_utils import UserSession, save_audio_metadata
from templates.recommendation_templates import get_trending_topics, get_topic_categories
from config import APP_TITLE, APP_DESCRIPTION, AUDIO_DIR

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
    </style>
    """, unsafe_allow_html=True)

# Initialisation de la session
if 'session' not in st.session_state:
    st.session_state.session = UserSession()

if 'current_playlist' not in st.session_state:
    st.session_state.current_playlist = []

def create_playlist(topics, duration_per_topic=5):
    """
    Crée une playlist de snippets d'apprentissage basés sur les sujets fournis.
    
    Args:
        topics (list): Liste des sujets pour la playlist
        duration_per_topic (int): Durée en minutes pour chaque snippet
        
    Returns:
        list: Liste des snippets générés avec leurs métadonnées
    """
    playlist = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, topic in enumerate(topics):
        # Mettre à jour la barre de progression
        progress = (i) / len(topics)
        progress_bar.progress(progress)
        status_text.text(f"Génération du snippet {i+1}/{len(topics)}: {topic}")
        
        # Générer le contenu du snippet
        snippet = generate_learning_snippet(topic, duration_per_topic)
        
        # Générer l'audio
        status_text.text(f"Conversion en audio pour: {snippet['title']}")
        audio_path = generate_audio(snippet['content'], snippet['title'])
        
        if audio_path:
            # Obtenir la durée de l'audio
            duration = get_audio_duration(audio_path)
            
            # Sauvegarder les métadonnées
            audio_metadata = save_audio_metadata(snippet['id'], audio_path, duration)
            
            # Ajouter le chemin audio au snippet
            snippet['audio_path'] = audio_path
            snippet['audio_duration'] = duration
            
            # Ajouter à la playlist
            playlist.append(snippet)
            
            # Ajouter à la session utilisateur
            st.session_state.session.add_snippet(snippet)
    
    # Terminer la barre de progression
    progress_bar.progress(1.0)
    status_text.text("Playlist générée avec succès!")
    
    return playlist

def parse_user_input(input_text):
    """
    Analyse l'entrée utilisateur pour extraire une liste de sujets.
    
    Args:
        input_text (str): Le texte saisi par l'utilisateur
        
    Returns:
        list: Liste des sujets extraits
    """
    lines = input_text.strip().split('\n')
    topics = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Supprimer les tirets ou astérisques au début des lignes (format liste)
            if line.startswith('-') or line.startswith('*'):
                line = line[1:].strip()
            
            # Supprimer les numéros au début des lignes
            if line[0].isdigit() and line[1:3] in ['. ', ') ']:
                line = line[3:].strip()
                
            topics.append(line)
    
    return topics

def display_playlist(playlist):
    """
    Affiche la playlist avec des contrôles de lecture.
    
    Args:
        playlist (list): Liste des snippets à afficher
    """
    st.subheader("Votre Playlist d'Apprentissage")
    
    for i, snippet in enumerate(playlist):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div class="playlist-item">
                <div class="snippet-title">{i+1}. {snippet['title']}</div>
                <div class="snippet-duration">Durée: {int(snippet['audio_duration'] // 60)}:{int(snippet['audio_duration'] % 60):02d}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Afficher le lecteur audio
            st.audio(snippet['audio_path'])
            
            # Option pour afficher le contenu textuel
            with st.expander("Voir le contenu textuel"):
                st.write(snippet['content'])
        
        with col2:
            # Boutons d'action pour chaque snippet
            st.download_button(
                label="Télécharger",
                data=open(snippet['audio_path'], 'rb'),
                file_name=f"{snippet['title']}.mp3",
                mime="audio/mp3"
            )

def main():
    st.title("🎧 Spotify for Learning")
    st.markdown(APP_DESCRIPTION)
    
    tab1, tab2, tab3 = st.tabs(["Créer une Playlist", "Ma Bibliothèque", "Découvrir"])
    
    with tab1:
        st.header("Créer votre Playlist Personnalisée")
        
        # Entrée utilisateur
        user_input = st.text_area(
            "Entrez les sujets que vous souhaitez apprendre (un par ligne):",
            height=150,
            placeholder="Exemple:\n- L'histoire de la Révolution française\n- Comment fonctionne la photosynthèse\n- Les bases de la cryptographie\n..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            duration_per_topic = st.slider(
                "Durée par sujet (minutes):",
                min_value=3,
                max_value=10,
                value=5,
                step=1
            )
        
        with col2:
            total_duration = st.empty()
            if user_input:
                topics = parse_user_input(user_input)
                estimated_time = len(topics) * duration_per_topic
                total_duration.info(f"Durée totale estimée: {estimated_time} minutes")
        
        # Bouton pour générer la playlist
        if st.button("Générer ma Playlist"):
            if user_input:
                topics = parse_user_input(user_input)
                if topics:
                    with st.spinner("Génération de votre playlist personnalisée..."):
                        playlist = create_playlist(topics, duration_per_topic)
                        st.session_state.current_playlist = playlist
                        st.rerun()
                else:
                    st.error("Veuillez entrer au moins un sujet.")
            else:
                st.error("Veuillez entrer au moins un sujet.")
        
        # Afficher les recommandations basées sur l'historique
        if st.session_state.session.history:
            st.subheader("Vous pourriez aussi être intéressé par:")
            recent_topics = st.session_state.session.get_recent_topics()
            recommendations = generate_recommendation(recent_topics, 3)
            
            for i, rec in enumerate(recommendations):
                st.markdown(f"""
                <div style="background-color: #282828; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                    {rec}
                </div>
                """, unsafe_allow_html=True)
                
                # Bouton pour ajouter à la liste
                if st.button(f"Ajouter à ma liste", key=f"add_rec_{i}"):
                    current_input = user_input.strip()
                    new_input = current_input + f"\n- {rec}" if current_input else f"- {rec}"
                    st.experimental_set_query_params(user_input=new_input)
                    st.rerun()
    
    with tab2:
        st.header("Ma Bibliothèque d'Apprentissage")
        
        # Afficher la playlist actuelle
        if st.session_state.current_playlist:
            display_playlist(st.session_state.current_playlist)
        elif st.session_state.session.snippets:
            display_playlist(st.session_state.session.get_playlist())
        else:
            st.info("Vous n'avez pas encore créé de playlist. Allez dans l'onglet 'Créer une Playlist' pour commencer.")
    
    with tab3:
        st.header("Découvrir de Nouveaux Sujets")
        
        # Afficher les catégories de sujets
        categories = get_topic_categories()
        
        for category, topics in categories.items():
            with st.expander(category):
                for topic in topics:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="background-color: #282828; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                            {topic}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("Ajouter", key=f"add_{category}_{topic}"):
                            # Créer un snippet unique pour ce sujet
                            with st.spinner(f"Génération du snippet sur {topic}..."):
                                playlist = create_playlist([topic], duration_per_topic=5)
                                
                                # Ajouter à la playlist actuelle
                                if 'current_playlist' in st.session_state:
                                    st.session_state.current_playlist.extend(playlist)
                                else:
                                    st.session_state.current_playlist = playlist
                                
                                st.success(f"'{topic}' ajouté à votre playlist!")
                                st.rerun()

if __name__ == "__main__":
    main()