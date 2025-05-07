import streamlit as st
import time
import json
import random
from datetime import datetime
import pandas as pd
import plotly.express as px
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page

from utils.language_utils import get_translation
from utils.data_utils import track_event, get_user_stats
from utils.export_utils import export_stats
from components.content_cards import render_achievement_card
from utils.visualization_utils import (
    create_listening_history_chart, 
    create_quiz_performance_chart,
    create_topic_distribution_chart,
    display_progress_bar
)

def app():
    """Profile page for viewing stats and achievements"""
    
    # Get session state
    if 'session' not in st.session_state:
        st.error("Session not initialized. Please return to the home page.")
        if st.button("Go to Home"):
            switch_page("app")
        return
    
    # Check if user is authenticated
    if not st.session_state.session.is_authenticated():
        st.warning("Please log in to view your profile.")
        if st.button("Log In"):
            # In a real app, this would redirect to login
            pass
        return
    
    # Get user info
    user = st.session_state.session.get_user()
    
    # Page title
    colored_header(
        label=get_translation('profile_title', st.session_state.language),
        description=f"{user.get('username', 'User')}",
        color_name="orange-70"
    )
    
    # Initialize profile state if needed
    if 'profile_state' not in st.session_state:
        st.session_state.profile_state = {
            'tab': 'stats',
            'stats_loaded': False,
            'stats_data': None,
            'stats_loading': False
        }
    
    # Profile tabs
    tabs = st.tabs([
        get_translation('learning_stats', st.session_state.language),
        get_translation('achievements', st.session_state.language),
        get_translation('account_settings', st.session_state.language)
    ])
    
    # Learning Stats tab
    with tabs[0]:
        display_learning_stats(user)
    
    # Achievements tab
    with tabs[1]:
        display_achievements(user)
    
    # Account Settings tab
    with tabs[2]:
        display_account_settings(user)

def display_learning_stats(user):
    """Display learning statistics for the user"""
    
    # Load stats if not already loaded
    if not st.session_state.profile_state['stats_loaded'] and not st.session_state.profile_state['stats_loading']:
        st.session_state.profile_state['stats_loading'] = True
        
        with st.spinner("Loading your stats..."):
            # Get user stats data (simulated here)
            stats = get_user_stats(user.get('id', 'default'))
            
            # Store stats data
            st.session_state.profile_state['stats_data'] = stats
            st.session_state.profile_state['stats_loaded'] = True
            st.session_state.profile_state['stats_loading'] = False
    
    # Display stats if loaded
    if st.session_state.profile_state['stats_loaded']:
        stats = st.session_state.profile_state['stats_data']
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(get_translation('topics_explored', st.session_state.language), stats.get('topics_explored', 0))
        
        with col2:
            st.metric(get_translation('snippets_created', st.session_state.language), stats.get('snippets_created', 0))
        
        with col3:
            # Format listening time nicely
            listening_hours = stats.get('listening_time', 0) / 3600  # convert seconds to hours
            st.metric(get_translation('listening_time', st.session_state.language), f"{listening_hours:.1f} hrs")
        
        with col4:
            quiz_count = stats.get('quizzes_taken', 0)
            avg_score = stats.get('avg_quiz_score', 0)
            st.metric(get_translation('quizzes_taken', st.session_state.language), 
                      f"{quiz_count} ({avg_score}%)")
        
        # Learning streak visualization
        streak_days = stats.get('learning_streak', 0)
        
        st.markdown(f"### {get_translation('learning_streak', st.session_state.language)}")
        
        # Create a visual streak display
        streak_html = f"""
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="font-size: 2rem; font-weight: bold; margin-right: 15px;">{streak_days}</div>
            <div>{get_translation('days', st.session_state.language)}</div>
        </div>
        <div style="display: flex; margin-bottom: 20px;">
        """
        
        # Add last 7 days boxes
        today = datetime.now()
        for i in range(7, 0, -1):
            active = i <= streak_days
            day_color = "#1DB954" if active else "#555"
            streak_html += f"""
            <div style="display: flex; flex-direction: column; align-items: center; margin-right: 10px;">
                <div style="width: 25px; height: 25px; background-color: {day_color}; border-radius: 5px; margin-bottom: 5px;"></div>
                <div style="font-size: 0.8rem;">{(today.day - i) % 30 + 1}</div>
            </div>
            """
        
        streak_html += """
        </div>
        """
        
        st.markdown(streak_html, unsafe_allow_html=True)
        
        # Charts section
        st.markdown("### Analytics")
        
        # Topic distribution chart
        topic_data = stats.get('topic_distribution', {
            'Science': 12,
            'History': 8,
            'Technology': 15,
            'Arts': 5,
            'Health': 7
        })
        
        # Create a DataFrame for the chart
        df = pd.DataFrame({
            'Topic': list(topic_data.keys()),
            'Count': list(topic_data.values())
        })
        
        # Create pie chart
        fig = px.pie(
            df,
            values='Count',
            names='Topic',
            title=get_translation('topics_explored', st.session_state.language),
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        # Update layout
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Listening history chart
        dates = stats.get('listening_dates', [
            '2023-05-01', '2023-05-02', '2023-05-03', '2023-05-04', 
            '2023-05-05', '2023-05-06', '2023-05-07'
        ])
        
        counts = stats.get('listening_counts', [
            3, 5, 2, 7, 4, 6, 8
        ])
        
        # Create line chart
        fig2 = create_listening_history_chart(dates, counts)
        
        # Display chart
        st.plotly_chart(fig2, use_container_width=True)
        
        # Quiz performance chart
        if quiz_count > 0:
            # Get quiz data
            quiz_categories = stats.get('quiz_categories', [
                'Science', 'History', 'Technology', 'Arts', 'Health'
            ])
            
            quiz_scores = stats.get('quiz_scores', [
                85, 70, 90, 65, 75
            ])
            
            # Create radar chart
            fig3 = create_quiz_performance_chart(quiz_categories, quiz_scores)
            
            # Display chart
            st.plotly_chart(fig3, use_container_width=True)
        
        # Export button
        st.divider()
        if st.button(get_translation('export_data', st.session_state.language)):
            # Export stats data
            export_path = export_stats(stats, format='json')
            
            if export_path:
                # Offer download (in a real app, this would provide a download link)
                st.success(get_translation('success_export', st.session_state.language))
                
                # Format path for display
                export_filename = export_path.split('/')[-1]
                st.markdown(f"Your data has been exported to: **{export_filename}**")
                
                # Track event
                track_event("stats_exported", {
                    "format": "json",
                    "user_id": user.get('id', 'default')
                })
            else:
                st.error("Failed to export data. Please try again.")
    
    # Show loading message if stats are being loaded
    elif st.session_state.profile_state['stats_loading']:
        st.info("Loading your learning statistics...")
    
    # Show error message if stats failed to load
    else:
        st.error("Failed to load statistics. Please try refreshing the page.")
        
        if st.button("Retry"):
            st.session_state.profile_state['stats_loaded'] = False
            st.rerun()

def display_achievements(user):
    """Display user achievements"""
    
    # Get achievements data (simulated here)
    achievements = [
        {
            "id": "first_snippet",
            "name": "First Snippet",
            "description": "Create your first learning snippet",
            "points": 10,
            "completed": True,
            "date_earned": "2023-04-15"
        },
        {
            "id": "knowledge_explorer",
            "name": "Knowledge Explorer",
            "description": "Create snippets on 5 different topics",
            "points": 25,
            "completed": True,
            "date_earned": "2023-04-20"
        },
        {
            "id": "polyglot",
            "name": "Polyglot",
            "description": "Use the app in 3 different languages",
            "points": 30,
            "completed": False,
            "progress": 0.6  # 60% complete
        },
        {
            "id": "quiz_master",
            "name": "Quiz Master",
            "description": "Complete 10 quizzes with a perfect score",
            "points": 50,
            "completed": False,
            "progress": 0.3  # 30% complete
        },
        {
            "id": "daily_learner",
            "name": "Daily Learner",
            "description": "Use the app for 7 consecutive days",
            "points": 35,
            "completed": True,
            "date_earned": "2023-05-01"
        },
        {
            "id": "creator",
            "name": "Content Creator",
            "description": "Create 20 learning snippets",
            "points": 40,
            "completed": False,
            "progress": 0.5  # 50% complete
        }
    ]
    
    # Calculate total points
    total_points = sum(a["points"] for a in achievements if a.get("completed", False))
    
    # Display points summary
    st.markdown(f"### {get_translation('achievements', st.session_state.language)}")
    st.markdown(f"**Total Points:** {total_points}")
    
    # Progress to next level
    level = total_points // 100 + 1
    next_level = level + 1
    points_needed = next_level * a100 - total_points
    
    # Display level progress
    st.markdown(f"**Level:** {level}")
    
    # Create progress bar
    progress_percentage = total_points % 100 / 100
    st.progress(progress_percentage)
    st.caption(f"{points_needed} points needed for Level {next_level}")
    
    # Display achievements
    st.markdown("### Earned Achievements")
    
    # Split into completed and in-progress
    completed_achievements = [a for a in achievements if a.get("completed", False)]
    in_progress_achievements = [a for a in achievements if not a.get("completed", False)]
    
    # Display completed achievements
    if completed_achievements:
        for achievement in completed_achievements:
            render_achievement_card(achievement, is_completed=True)
    else:
        st.info("No achievements earned yet. Keep learning to earn achievements!")
    
    # Display in-progress achievements
    if in_progress_achievements:
        st.markdown("### In Progress")
        
        for achievement in in_progress_achievements:
            # Display achievement with progress
            st.markdown(f"""
            <div style="background-color: #282828; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 5px solid #555555;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin-top: 0; margin-bottom: 5px;">{achievement['name']}</h3>
                        <p style="color: #cccccc; margin-top: 0;">{achievement['description']}</p>
                    </div>
                    <div style="text-align: center;">
                        <div style="background-color: #555555; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center;">
                            <span style="color: white; font-weight: bold;">{achievement['points']}</span>
                        </div>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <div style="background-color: #555555; height: 10px; border-radius: 5px; margin-top: 5px;">
                        <div style="background-color: #1DB954; height: 10px; border-radius: 5px; width: {int(achievement.get('progress', 0) * 100)}%;"></div>
                    </div>
                    <p style="font-size: 12px; margin-top: 5px; text-align: right;">{int(achievement.get('progress', 0) * 100)}% complete</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_account_settings(user):
    """Display account settings"""
    
    # Account information
    st.markdown("### Account Information")
    
    # User info
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Username", value=user.get('username', ''), disabled=True)
        st.text_input("Email", value=user.get('email', ''), disabled=True)
    
    with col2:
        st.text_input("Member since", value=user.get('created_at', '2023-04-01'), disabled=True)
        st.text_input("Last login", value=user.get('last_login', '2023-05-07'), disabled=True)
    
    # Profile settings
    st.markdown("### Profile Settings")
    
    # Edit profile form
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            display_name = st.text_input("Display Name", value=user.get('display_name', user.get('username', '')))
        
        with col2:
            bio = st.text_area("Bio", value=user.get('bio', ''), height=100)
        
        # Submit button
        if st.form_submit_button("Update Profile"):
            # Update user profile (in a real app)
            st.success(get_translation('success_updated', st.session_state.language))
            
            # Track event
            track_event("profile_updated", {
                "user_id": user.get('id', 'default')
            })
    
    # Danger zone
    st.divider()
    st.markdown("### Danger Zone")
    
    # Delete account button (with confirmation)
    delete_col1, delete_col2 = st.columns([1, 3])
    
    with delete_col1:
        if st.button(get_translation('delete_account', st.session_state.language), 
                   type="secondary", use_container_width=True):
            # Set state for confirmation
            st.session_state.profile_state['confirm_delete'] = True
            st.rerun()
    
    # Show confirmation dialog
    if st.session_state.profile_state.get('confirm_delete'):
        with st.container():
            st.warning("Are you sure you want to delete your account? This action cannot be undone.")
            
            confirm_col1, confirm_col2 = st.columns(2)
            
            with confirm_col1:
                if st.button("Yes, Delete My Account", type="secondary", use_container_width=True):
                    # In a real app, this would actually delete the account
                    st.success("Account deletion initiated. Logging out...")
                    
                    # Track event
                    track_event("account_deleted", {
                        "user_id": user.get('id', 'default')
                    })
                    
                    # Simulate logout and redirect
                    time.sleep(2)
                    switch_page("app")
            
            with confirm_col2:
                if st.button("Cancel", use_container_width=True):
                    # Reset confirmation state
                    st.session_state.profile_state['confirm_delete'] = False
                    st.rerun()

if __name__ == "__main__":
    app()