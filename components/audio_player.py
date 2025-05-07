import streamlit as st
import streamlit_player as st_player
import os
import time
import base64
from typing import Optional, Callable, Dict, Any
from utils.audio_utils import get_audio_duration, generate_waveform_data

class AudioPlayer:
    """Enhanced audio player component with visualization and controls"""
    
    def __init__(self, key_prefix: str = "audio_player"):
        """
        Initialize audio player
        
        Args:
            key_prefix (str): Prefix for component keys
        """
        self.key_prefix = key_prefix
        self.current_audio = None
        self.waveform_data = None
        self.is_playing = False
        self.progress = 0
        self.duration = 0
        self.volume = 80
        self.playback_rate = 1.0
    
    def render(self, audio_path: str, title: str = None, autoplay: bool = False, 
               on_complete: Optional[Callable] = None, show_download: bool = True):
        """
        Render the audio player
        
        Args:
            audio_path (str): Path to audio file
            title (str, optional): Title to display
            autoplay (bool): Whether to autoplay the audio
            on_complete (callable, optional): Function to call when audio finishes
            show_download (bool): Whether to show download button
        """
        if not audio_path or not os.path.exists(audio_path):
            st.warning("Audio file not found.")
            return False
        
        # Get audio information
        self.current_audio = audio_path
        self.duration = get_audio_duration(audio_path)
        self.waveform_data = generate_waveform_data(audio_path, num_points=100)
        
        # Container for player
        player_container = st.container()
        
        with player_container:
            # Add title if provided
            if title:
                st.markdown(f"### {title}")
            
            # Main player row
            col1, col2 = st.columns([8, 2])
            
            with col1:
                # Use streamlit_player for playback
                file_url = f"data:audio/mp3;base64,{self._get_file_as_base64(audio_path)}"
                
                st_player.st_player(
                    url=file_url,
                    height=80,
                    playing=autoplay,
                    loop=False,
                    volume=self.volume/100,
                    key=f"{self.key_prefix}_{os.path.basename(audio_path)}"
                )
                
                # Display waveform
                self._render_waveform()
            
            with col2:
                # Control buttons
                playback_rates = [0.75, 1.0, 1.25, 1.5, 2.0]
                selected_rate = st.selectbox(
                    "Speed",
                    playback_rates,
                    index=playback_rates.index(1.0),
                    key=f"{self.key_prefix}_speed"
                )
                self.playback_rate = selected_rate
                
                # Volume control (1-100)
                self.volume = st.slider(
                    "Volume", 
                    min_value=0,
                    max_value=100,
                    value=80,
                    key=f"{self.key_prefix}_volume"
                )
                
                # Download button
                if show_download:
                    self._render_download_button(audio_path)
                
        return True
    
    def _render_waveform(self):
        """Render waveform visualization"""
        if not self.waveform_data:
            return
        
        # Create SVG waveform visualization
        width = 600
        height = 60
        bgcolor = "#1E1E1E"
        color = "#1DB954"
        
        svg = f"""
        <svg width="{width}" height="{height}" style="background-color: {bgcolor}; border-radius: 4px;">
            <g transform="translate(0, {height/2})">
        """
        
        # Calculate bar width
        bar_width = max(1, width / len(self.waveform_data) - 1)
        
        # Draw bars
        for i, amplitude in enumerate(self.waveform_data):
            # Scale amplitude to half the height
            bar_height = amplitude * (height / 2)
            
            # Calculate x position
            x = i * (bar_width + 1)
            
            # Draw bar (from center, extending both up and down)
            svg += f'<rect x="{x}" y="{-bar_height}" width="{bar_width}" height="{bar_height*2}" fill="{color}" />'
        
        svg += """
            </g>
        </svg>
        """
        
        # Display waveform
        st.markdown(svg, unsafe_allow_html=True)
    
    def _render_download_button(self, audio_path: str):
        """Render a download button for the audio file"""
        try:
            with open(audio_path, "rb") as file:
                audio_bytes = file.read()
                file_name = os.path.basename(audio_path)
                
                b64 = base64.b64encode(audio_bytes).decode()
                href = f'<a href="data:audio/mp3;base64,{b64}" download="{file_name}" style="text-decoration:none;">⬇️ Download</a>'
                st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error creating download button: {e}")
    
    def _get_file_as_base64(self, file_path: str) -> str:
        """Convert file to base64 encoding"""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                return base64.b64encode(data).decode()
        except Exception as e:
            st.error(f"Error encoding file: {e}")
            return ""

class PlaylistPlayer:
    """Playlist player component for managing multiple audio tracks"""
    
    def __init__(self, key_prefix: str = "playlist_player"):
        """
        Initialize playlist player
        
        Args:
            key_prefix (str): Prefix for component keys
        """
        self.key_prefix = key_prefix
        self.audio_player = AudioPlayer(key_prefix=f"{key_prefix}_player")
        self.current_index = 0
        self.playlist = []
    
    def set_playlist(self, playlist: list):
        """
        Set the playlist
        
        Args:
            playlist (list): List of audio items (dictionaries with 'title', 'audio_path')
        """
        self.playlist = playlist
        self.current_index = 0
    
    def render(self, autoplay: bool = False, show_playlist: bool = True):
        """
        Render the playlist player
        
        Args:
            autoplay (bool): Whether to autoplay the current track
            show_playlist (bool): Whether to show the playlist
        """
        if not self.playlist:
            st.info("No tracks in playlist.")
            return
        
        # Initialize session state for playlist if needed
        if f"{self.key_prefix}_current_index" not in st.session_state:
            st.session_state[f"{self.key_prefix}_current_index"] = 0
        
        # Get current track
        current_index = st.session_state[f"{self.key_prefix}_current_index"]
        if current_index >= len(self.playlist):
            current_index = 0
            st.session_state[f"{self.key_prefix}_current_index"] = 0
        
        current_track = self.playlist[current_index]
        
        # Create player UI
        st.markdown("## Now Playing")
        
        # Display current track info
        st.markdown(f"**{current_index + 1}/{len(self.playlist)}** - **{current_track['title']}**")
        
        # Render audio player for current track
        self.audio_player.render(
            audio_path=current_track.get('audio_path', ''),
            title=None,  # Title already displayed above
            autoplay=autoplay,
            on_complete=self._play_next_track
        )
        
        # Player controls
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("⏮️ Previous", key=f"{self.key_prefix}_prev", disabled=current_index <= 0):
                self._play_previous_track()
        
        with col2:
            # Shuffle button
            if st.button("🔀 Shuffle", key=f"{self.key_prefix}_shuffle"):
                self._shuffle_playlist()
        
        with col3:
            if st.button("⏭️ Next", key=f"{self.key_prefix}_next", disabled=current_index >= len(self.playlist) - 1):
                self._play_next_track()
        
        # Display playlist
        if show_playlist and len(self.playlist) > 1:
            self._render_playlist()
    
    def _render_playlist(self):
        """Render the playlist tracks"""
        st.markdown("## Playlist")
        
        current_index = st.session_state.get(f"{self.key_prefix}_current_index", 0)
        
        for i, track in enumerate(self.playlist):
            is_current = i == current_index
            
            # Create row for track
            col1, col2 = st.columns([8, 2])
            
            with col1:
                title = track.get('title', f"Track {i+1}")
                if is_current:
                    st.markdown(f"**▶️ {i+1}. {title}**")
                else:
                    st.markdown(f"{i+1}. {title}")
            
            with col2:
                if not is_current and st.button("Play", key=f"{self.key_prefix}_play_{i}"):
                    st.session_state[f"{self.key_prefix}_current_index"] = i
                    st.rerun()
    
    def _play_next_track(self):
        """Play the next track in the playlist"""
        current_index = st.session_state.get(f"{self.key_prefix}_current_index", 0)
        if current_index < len(self.playlist) - 1:
            st.session_state[f"{self.key_prefix}_current_index"] = current_index + 1
            st.rerun()
    
    def _play_previous_track(self):
        """Play the previous track in the playlist"""
        current_index = st.session_state.get(f"{self.key_prefix}_current_index", 0)
        if current_index > 0:
            st.session_state[f"{self.key_prefix}_current_index"] = current_index - 1
            st.rerun()
    
    def _shuffle_playlist(self):
        """Shuffle the playlist"""
        import random
        
        # Save current track
        current_index = st.session_state.get(f"{self.key_prefix}_current_index", 0)
        current_track = self.playlist[current_index] if self.playlist else None
        
        # Shuffle playlist
        if len(self.playlist) > 1:
            # Remove current track
            if current_track:
                self.playlist.pop(current_index)
            
            # Shuffle remaining tracks
            random.shuffle(self.playlist)
            
            # Add current track back at the beginning
            if current_track:
                self.playlist.insert(0, current_track)
            
            # Reset index
            st.session_state[f"{self.key_prefix}_current_index"] = 0
            st.rerun()