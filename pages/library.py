import streamlit as st
import os
import time
import asyncio
import pandas as pd
import plotly.express as px
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_card import card
from streamlit_player import st_player
import qrcode
from io import BytesIO

from utils.audio_utils import get_audio_duration, generate_waveform_data, convert_audio_format
from utils.language_utils import get_translation
from utils.data_utils import track_event
from utils.llm_utils import generate_summary, extract_keywords
import config

def app():
    """Library page showing user's learning content"""
    
    # Get session state
    if 'session' not in st.session_state:
        st.error("Session not initialized. Please return to the home page.")
        if st.button("Go to Home"):
            switch_page("app")
        return
    
    if 'current_playlist' not in st.session_state:
        st.session_state.current_playlist = []
    
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
        
    if 'filter_options' not in st.session_state:
        st.session_state.filter_options = {
            'languages': [],
            'date_range': None,
            'sort_by': 'date',
            'sort_order': 'desc'
        }
    
    if 'playback_queue' not in st.session_state:
        st.session_state.playback_queue = []
        
    if 'currently_playing' not in st.session_state:
        st.session_state.currently_playing = None
        
    if 'detailed_view' not in st.session_state:
        st.session_state.detailed_view = None
    
    # Page title
    colored_header(
        label=get_translation('my_learning_library', st.session_state.language),
        description=get_translation('manage_your_learning_content', st.session_state.language),
        color_name="violet-70"
    )
    
    # Library controls
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Search box
            st.text_input(
                get_translation('search_placeholder', st.session_state.language),
                value=st.session_state.search_query,
                key="library_search",
                on_change=lambda: setattr(st.session_state, 'search_query', st.session_state.library_search)
            )
        
        with col2:
            # Filter dropdown
            with st.expander("Filters"):
                # Language filter
                available_languages = list(set([s.get('language', 'en') for s in st.session_state.session.snippets]))
                st.multiselect(
                    "Languages",
                    options=available_languages,
                    default=st.session_state.filter_options['languages'],
                    key="filter_languages",
                    on_change=lambda: st.session_state.filter_options.update({'languages': st.session_state.filter_languages})
                )
                
                # Sort options
                sort_options = ['date', 'title', 'duration']
                st.selectbox(
                    "Sort by",
                    options=sort_options,
                    index=sort_options.index(st.session_state.filter_options['sort_by']),
                    key="sort_by",
                    on_change=lambda: st.session_state.filter_options.update({'sort_by': st.session_state.sort_by})
                )
                
                # Sort order
                sort_order = st.radio(
                    "Order",
                    options=['Ascending', 'Descending'],
                    index=1 if st.session_state.filter_options['sort_order'] == 'desc' else 0,
                    key="sort_order_radio",
                    horizontal=True,
                    on_change=lambda: st.session_state.filter_options.update(
                        {'sort_order': 'desc' if st.session_state.sort_order_radio == 'Descending' else 'asc'}
                    )
                )
        
        with col3:
            # View style
            view_options = ['Card', 'List', 'Compact']
            if 'view_style' not in st.session_state:
                st.session_state.view_style = 'Card'
                
            st.selectbox(
                "View",
                options=view_options,
                index=view_options.index(st.session_state.view_style),
                key="view_style_select",
                on_change=lambda: setattr(st.session_state, 'view_style', st.session_state.view_style_select)
            )
    
    # Get the playlist
    playlist = st.session_state.current_playlist or st.session_state.session.get_playlist()
    
    # Apply filters
    filtered_playlist = apply_filters(playlist)
    
    # Display content based on view style
    if st.session_state.view_style == 'Card':
        display_card_view(filtered_playlist)
    elif st.session_state.view_style == 'List':
        display_list_view(filtered_playlist)
    else:
        display_compact_view(filtered_playlist)
    
    # Detailed view for selected snippet
    if st.session_state.detailed_view:
        display_detailed_view(st.session_state.detailed_view)

def apply_filters(playlist):
    """Apply filters to the playlist"""
    
    filtered_playlist = playlist.copy()
    
    # Apply search filter
    if st.session_state.search_query:
        query = st.session_state.search_query.lower()
        filtered_playlist = [
            s for s in filtered_playlist 
            if query in s.get('title', '').lower() or 
               query in s.get('topic', '').lower() or 
               query in s.get('content', '').lower()
        ]
    
    # Apply language filter
    if st.session_state.filter_options['languages']:
        filtered_playlist = [
            s for s in filtered_playlist
            if s.get('language', 'en') in st.session_state.filter_options['languages']
        ]
    
    # Apply sorting
    sort_key = st.session_state.filter_options['sort_by']
    if sort_key == 'date':
        filtered_playlist.sort(key=lambda x: x.get('created_at', 0), 
                              reverse=(st.session_state.filter_options['sort_order'] == 'desc'))
    elif sort_key == 'title':
        filtered_playlist.sort(key=lambda x: x.get('title', '').lower(),
                              reverse=(st.session_state.filter_options['sort_order'] == 'desc'))
    elif sort_key == 'duration':
        filtered_playlist.sort(key=lambda x: x.get('audio_duration', 0),
                              reverse=(st.session_state.filter_options['sort_order'] == 'desc'))
    
    return filtered_playlist

def display_card_view(playlist):
    """Display playlist in card view"""
    
    if not playlist:
        st.info(get_translation('no_playlist_yet', st.session_state.language))
        return
    
    # Display results count
    st.caption(f"Showing {len(playlist)} items")
    
    # Add selection options for batch operations
    if 'selected_snippets' not in st.session_state:
        st.session_state.selected_snippets = []
    
    # Check all button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Select All"):
            st.session_state.selected_snippets = [s['id'] for s in playlist]
            st.rerun()
    
    with col2:
        if st.button("Clear Selection"):
            st.session_state.selected_snippets = []
            st.rerun()
    
    # Show batch operations if snippets are selected
    if st.session_state.selected_snippets:
        with col3:
            st.write(f"{len(st.session_state.selected_snippets)} snippets selected")
            batch_action = st.selectbox(
                "Batch Actions",
                options=["--Select--", "Export Selected", "Delete Selected"],
                key="batch_action"
            )
            
            if batch_action == "Export Selected":
                # Export functionality here
                st.success("Export feature coming soon!")
                
            elif batch_action == "Delete Selected":
                if st.button("Confirm Delete"):
                    for snippet_id in st.session_state.selected_snippets:
                        st.session_state.session.remove_snippet(snippet_id)
                    st.session_state.selected_snippets = []
                    st.rerun()
    
    # Display cards in grid
    cols = st.columns(3)
    
    for i, snippet in enumerate(playlist):
        with cols[i % 3]:
            # Get snippet info
            title = snippet.get('title', 'Untitled')
            topic = snippet.get('topic', 'No topic')
            duration = snippet.get('audio_duration', 300)
            duration_str = f"{int(duration//60)} mins {int(duration%60)} secs"
            language = snippet.get('language', 'en')
            
            # Create card
            card_clicked = card(
                title=title,
                text=f"**Topic:** {topic}\n\n**Duration:** {duration_str}\n\n**Language:** {language}",
                image=None,
                on_click=lambda s=snippet: set_detailed_view(s),
                key=f"card_{snippet['id']}"
            )
            
            # Selection checkbox
            st.checkbox(
                "Select",
                key=f"select_{snippet['id']}",
                value=snippet['id'] in st.session_state.selected_snippets,
                on_change=lambda s=snippet: toggle_snippet_selection(s['id'])
            )
            
            # Simple controls
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Play", key=f"play_{snippet['id']}"):
                    st.session_state.currently_playing = snippet
                    # Track event
                    track_event("play_snippet", {
                        "snippet_id": snippet['id'],
                        "topic": snippet['topic'],
                        "language": snippet['language']
                    })
            
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{snippet['id']}"):
                    if st.session_state.session.remove_snippet(snippet['id']):
                        # Update current playlist
                        st.session_state.current_playlist = [
                            s for s in st.session_state.current_playlist 
                            if s['id'] != snippet['id']
                        ]
                        st.rerun()

def display_list_view(playlist):
    """Display playlist in list view"""
    
    if not playlist:
        st.info(get_translation('no_playlist_yet', st.session_state.language))
        return
    
    # Display results count
    st.caption(f"Showing {len(playlist)} items")
    
    # Display each snippet
    for i, snippet in enumerate(playlist):
        with st.expander(f"{i+1}. {snippet.get('title', 'Untitled')}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Audio player
                st.audio(snippet.get('audio_path', ''))
                
                # Topic and language
                st.caption(f"**Topic:** {snippet.get('topic', 'No topic')} | **Language:** {snippet.get('language', 'en')}")
                
                # Content preview
                content_preview = snippet.get('content', '')[:300] + "..." if len(snippet.get('content', '')) > 300 else snippet.get('content', '')
                st.markdown(content_preview)
                
                # View full content button
                if st.button("View Full Content", key=f"view_{snippet['id']}"):
                    st.session_state.detailed_view = snippet
                    st.rerun()
            
            with col2:
                # Controls
                if st.button("🗑️ Delete", key=f"delete_{snippet['id']}"):
                    if st.session_state.session.remove_snippet(snippet['id']):
                        # Update current playlist
                        st.session_state.current_playlist = [
                            s for s in st.session_state.current_playlist 
                            if s['id'] != snippet['id']
                        ]
                        st.rerun()
                
                # Download button
                st.download_button(
                    label="⬇️ Download",
                    data=open(snippet.get('audio_path', ''), 'rb'),
                    file_name=f"{snippet.get('title', 'audio')}.mp3",
                    mime="audio/mp3",
                    key=f"download_{snippet['id']}"
                )
                
                # Share button
                if config.ENABLE_SOCIAL_SHARING:
                    if st.button("📤 Share", key=f"share_{snippet['id']}"):
                        show_share_options(snippet)

def display_compact_view(playlist):
    """Display playlist in compact view"""
    
    if not playlist:
        st.info(get_translation('no_playlist_yet', st.session_state.language))
        return
    
    # Display results count
    st.caption(f"Showing {len(playlist)} items")
    
    # Create a dataframe for the table
    data = []
    for snippet in playlist:
        duration = snippet.get('audio_duration', 300)
        duration_str = f"{int(duration//60)}:{int(duration%60):02d}"
        
        data.append({
            "ID": snippet['id'],
            "Title": snippet.get('title', 'Untitled'),
            "Topic": snippet.get('topic', 'No topic'),
            "Duration": duration_str,
            "Language": snippet.get('language', 'en'),
            "Created": time.strftime("%Y-%m-%d", time.localtime(snippet.get('created_at', 0)))
        })
    
    df = pd.DataFrame(data)
    
    # Use Streamlit's dataframe with row selection
    # The return value 'selected_df_rows' will be a list of dictionaries for the selected rows.
    selected_df_rows = st.dataframe(
        df,
        column_config={
            "ID": None,  # Hide ID column
            "Title": st.column_config.TextColumn(
                "Title",
                width="large"
            ),
            "Duration": st.column_config.TextColumn(
                "Duration",
                width="small"
            ),
            "Language": st.column_config.TextColumn(
                "Language",
                width="small"
            ),
        },
        hide_index=True,
        use_container_width=True,
        selection_mode="multi-row",  # Explicitly set selection mode
        on_select="rerun"  # Ensure rerun on selection
    )
    
    # Actions for selected row
    st.write("Select a row to view or play")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Play Selected"):
            if selected_df_rows and isinstance(selected_df_rows, list) and len(selected_df_rows) > 0:
                snippet_id = selected_df_rows[0]["ID"] # Access the ID from the first selected row
                snippet = next((s for s in playlist if s['id'] == snippet_id), None)
                if snippet:
                    st.session_state.currently_playing = snippet
                    st.rerun()
            else:
                st.warning("Please select a row to play.")
    
    with col2:
        if st.button("👁️ View Selected"):
            if selected_df_rows and isinstance(selected_df_rows, list) and len(selected_df_rows) > 0:
                snippet_id = selected_df_rows[0]["ID"] # Access the ID from the first selected row
                snippet = next((s for s in playlist if s['id'] == snippet_id), None)
                if snippet:
                    st.session_state.detailed_view = snippet
                    st.rerun()
            else:
                st.warning("Please select a row to view.")
    
    with col3:
        if st.button("🗑️ Delete Selected"):
            if selected_df_rows and isinstance(selected_df_rows, list) and len(selected_df_rows) > 0:
                snippet_id = selected_df_rows[0]["ID"] # Access the ID from the first selected row
                if st.session_state.session.remove_snippet(snippet_id):
                    # Update current playlist
                    st.session_state.current_playlist = [
                        s for s in st.session_state.current_playlist 
                        if s['id'] != snippet_id
                    ]
                    st.rerun()
    
    # Currently playing
    if st.session_state.currently_playing:
        st.divider()
        st.subheader("Now Playing")
        
        snippet = st.session_state.currently_playing
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{snippet.get('title', 'Untitled')}**")
            st.audio(snippet.get('audio_path', ''))
        
        with col2:
            st.caption(f"Topic: {snippet.get('topic', 'No topic')}")
            st.caption(f"Language: {snippet.get('language', 'en')}")
            
            if st.button("Stop Playing"):
                st.session_state.currently_playing = None
                st.rerun()

def display_detailed_view(snippet):
    """Display detailed view of a snippet"""
    
    st.sidebar.divider()
    st.sidebar.subheader("Snippet Details")
    
    # Close button
    if st.sidebar.button("Close Details"):
        st.session_state.detailed_view = None
        st.rerun()
    
    # Snippet info
    st.sidebar.markdown(f"**Title:** {snippet.get('title', 'Untitled')}")
    st.sidebar.markdown(f"**Topic:** {snippet.get('topic', 'No topic')}")
    st.sidebar.markdown(f"**Language:** {snippet.get('language', 'en')}")
    
    duration = snippet.get('audio_duration', 300)
    st.sidebar.markdown(f"**Duration:** {int(duration//60)} mins {int(duration%60)} secs")
    
    # Created date
    created_at = time.strftime("%Y-%m-%d %H:%M", time.localtime(snippet.get('created_at', 0)))
    st.sidebar.markdown(f"**Created:** {created_at}")
    
    # Audio controls
    st.sidebar.audio(snippet.get('audio_path', ''))
    
    # Download options
    format_options = ["mp3", "ogg", "wav"]
    selected_format = st.sidebar.selectbox("Download Format", format_options)
    
    if selected_format != "mp3":
        # Convert to selected format
        converted_path = convert_audio_format(snippet.get('audio_path', ''), selected_format)
        download_path = converted_path
    else:
        download_path = snippet.get('audio_path', '')
    
    st.sidebar.download_button(
        label="Download Audio",
        data=open(download_path, 'rb'),
        file_name=f"{snippet.get('title', 'audio')}.{selected_format}",
        mime=f"audio/{selected_format}",
        key=f"download_detailed_{snippet['id']}"
    )
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["Content", "Analysis", "Share"])
    
    with tab1:
        st.markdown(f"## {snippet.get('title', 'Untitled')}")
        st.markdown(snippet.get('content', 'No content available.'))
    
    with tab2:
        # Run async analysis
        analysis_placeholder = st.empty()
        analysis_placeholder.info("Analyzing content...")
        
        # Get or run keyword extraction
        if 'extracted_keywords' not in st.session_state:
            st.session_state.extracted_keywords = {}
        
        snippet_id = snippet['id']
        if snippet_id not in st.session_state.extracted_keywords:
            try:
                # Run in main thread since we're in Streamlit
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                keywords = loop.run_until_complete(extract_keywords(snippet.get('content', ''), 8, snippet.get('language', 'en')))
                summary = loop.run_until_complete(generate_summary(snippet.get('content', ''), 100, snippet.get('language', 'en')))
                loop.close()
                
                st.session_state.extracted_keywords[snippet_id] = {
                    'keywords': keywords,
                    'summary': summary
                }
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.session_state.extracted_keywords[snippet_id] = {
                    'keywords': [],
                    'summary': "Summary generation failed."
                }
        
        # Clear placeholder
        analysis_placeholder.empty()
        
        # Display analysis results
        analysis_data = st.session_state.extracted_keywords.get(snippet_id, {})
        
        st.subheader("Summary")
        st.markdown(analysis_data.get('summary', 'No summary available.'))
        
        st.subheader("Key Topics")
        # Display keywords as tags
        if analysis_data.get('keywords'):
            cols = st.columns(4)
            for i, keyword in enumerate(analysis_data.get('keywords', [])):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div style="background-color: #1DB954; color: white; padding: 5px 10px; 
                    border-radius: 15px; margin: 5px; display: inline-block; text-align: center;">
                    {keyword}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("No keywords available.")
        
        # Display audio waveform if available
        try:
            st.subheader("Audio Waveform")
            waveform_data = generate_waveform_data(snippet.get('audio_path', ''), 100)
            
            # Create a dataframe for the waveform
            df = pd.DataFrame({
                'position': range(len(waveform_data)),
                'amplitude': waveform_data
            })
            
            # Create the waveform chart
            fig = px.area(
                df, x='position', y='amplitude',
                color_discrete_sequence=['#1DB954'],
                labels={'position': '', 'amplitude': ''},
                height=200
            )
            
            # Update layout
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(showticklabels=False, showgrid=False),
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.write("Waveform visualization not available.")
    
    with tab3:
        if config.ENABLE_SOCIAL_SHARING:
            st.subheader("Share this content")
            
            # Generate sharing link
            share_url = f"{config.SHARE_URL_BASE}/share?id={snippet['id']}"
            st.text_input("Share link:", share_url)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(share_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO
            buffered = BytesIO()
            img.save(buffered)
            
            st.image(buffered, caption="Scan to share", width=300)
            
            # Social sharing buttons
            st.subheader("Share on social media")
            
            cols = st.columns(len(config.SHARING_PLATFORMS))
            
            for i, platform in enumerate(config.SHARING_PLATFORMS):
                with cols[i]:
                    if platform == "twitter":
                        platform_name = "Twitter"
                        share_text = f"Check out this learning snippet on {snippet.get('topic', 'Mindsnacks')}"
                        share_link = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
                    elif platform == "facebook":
                        platform_name = "Facebook"
                        share_link = f"https://www.facebook.com/sharer/sharer.php?u={share_url}"
                    elif platform == "linkedin":
                        platform_name = "LinkedIn"
                        share_link = f"https://www.linkedin.com/sharing/share-offsite/?url={share_url}"
                    elif platform == "whatsapp":
                        platform_name = "WhatsApp"
                        share_text = f"Check out this learning snippet on {snippet.get('topic', 'Mindsnacks')}"
                        share_link = f"https://wa.me/?text={share_text}%20{share_url}"
                    elif platform == "email":
                        platform_name = "Email"
                        subject = f"Learning snippet: {snippet.get('title', 'Mindsnacks')}"
                        body = f"Check out this learning snippet on {snippet.get('topic', 'Mindsnacks')}: {share_url}"
                        share_link = f"mailto:?subject={subject}&body={body}"
                    
                    st.markdown(f"[{platform_name}]({share_link})")
        else:
            st.info("Social sharing is currently disabled.")

def toggle_snippet_selection(snippet_id):
    """Toggle selection status of a snippet"""
    
    if snippet_id in st.session_state.selected_snippets:
        st.session_state.selected_snippets.remove(snippet_id)
    else:
        st.session_state.selected_snippets.append(snippet_id)

def set_detailed_view(snippet):
    """Set the detailed view snippet"""
    
    st.session_state.detailed_view = snippet
    st.rerun()

def show_share_options(snippet):
    """Show sharing options for a snippet"""
    
    if not config.ENABLE_SOCIAL_SHARING:
        return
    
    # Generate sharing link
    share_url = f"{config.SHARE_URL_BASE}/share?id={snippet['id']}"
    
    st.info(f"Share link: {share_url}")
    
    # Track sharing event
    track_event("share_snippet", {
        "snippet_id": snippet['id'],
        "topic": snippet['topic'],
    })

if __name__ == "__main__":
    app()