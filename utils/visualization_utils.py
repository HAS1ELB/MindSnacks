import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from typing import List, Dict, Any, Optional, Union, Tuple
import os
import logging
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import random

# Configure logging
logger = logging.getLogger(__name__)

def create_trending_chart(topics: List[str], popularity: List[int], title: str = "Trending Topics") -> go.Figure:
    """
    Create a horizontal bar chart for trending topics
    
    Args:
        topics (list): List of topic names
        popularity (list): List of popularity scores
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    df = pd.DataFrame({
        'Topic': topics,
        'Popularity': popularity
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
        title=title
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title=None,
        yaxis_title=None,
        coloraxis_showscale=False
    )
    
    return fig

def create_topic_distribution_chart(topics: Dict[str, int], title: str = "Topic Distribution") -> go.Figure:
    """
    Create a pie chart for topic distribution
    
    Args:
        topics (dict): Dictionary of topic categories and counts
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    df = pd.DataFrame({
        'Category': list(topics.keys()),
        'Count': list(topics.values())
    })
    
    # Create pie chart
    fig = px.pie(
        df,
        values='Count',
        names='Category',
        title=title,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    # Update traces
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    return fig

def create_listening_history_chart(dates: List[str], counts: List[int], title: str = "Listening History") -> go.Figure:
    """
    Create a line chart for listening history
    
    Args:
        dates (list): List of dates
        counts (list): List of listening counts
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    df = pd.DataFrame({
        'Date': pd.to_datetime(dates),
        'Count': counts
    })
    
    # Create line chart
    fig = px.line(
        df,
        x='Date',
        y='Count',
        title=title,
        markers=True
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title=None,
        yaxis_title="Snippets Listened"
    )
    
    return fig

def create_learning_time_chart(days: List[str], minutes: List[float], title: str = "Learning Time") -> go.Figure:
    """
    Create a bar chart for learning time
    
    Args:
        days (list): List of days
        minutes (list): List of learning minutes
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    df = pd.DataFrame({
        'Day': days,
        'Minutes': minutes
    })
    
    # Create bar chart
    fig = px.bar(
        df,
        x='Day',
        y='Minutes',
        title=title,
        color='Minutes',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title=None,
        yaxis_title="Minutes",
        coloraxis_showscale=False
    )
    
    return fig

def create_quiz_performance_chart(categories: List[str], scores: List[float], title: str = "Quiz Performance") -> go.Figure:
    """
    Create a radar chart for quiz performance
    
    Args:
        categories (list): List of quiz categories
        scores (list): List of scores (0-100)
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name=title
    ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title=title,
        height=400,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    return fig

def create_progress_chart(target: int, current: int, title: str = "Progress") -> go.Figure:
    """
    Create a gauge chart for progress
    
    Args:
        target (int): Target value
        current (int): Current value
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Calculate percentage
    percentage = min(100, int((current / target) * 100)) if target > 0 else 0
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        title={"text": title},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": "#1DB954"},
            "steps": [
                {"range": [0, 50], "color": "#F8F8F8"},
                {"range": [50, 80], "color": "#E8F8E8"},
                {"range": [80, 100], "color": "#D0F0D0"}
            ],
            "threshold": {
                "line": {"color": "green", "width": 4},
                "thickness": 0.75,
                "value": 100
            }
        }
    ))
    
    # Update layout
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    return fig

def create_achievement_progress_chart(achievements: List[Dict]) -> go.Figure:
    """
    Create a progress chart for achievements
    
    Args:
        achievements (list): List of achievement dictionaries with 'name', 'points', and 'completed' keys
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Extract data
    names = [a['name'] for a in achievements]
    points = [a['points'] for a in achievements]
    completed = [1 if a.get('completed', False) else 0.3 for a in achievements]
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Add bars for total points
    fig.add_trace(go.Bar(
        y=names,
        x=points,
        orientation='h',
        marker=dict(
            color='rgba(200, 200, 200, 0.6)',
            line=dict(color='rgba(200, 200, 200, 1.0)', width=1)
        ),
        name='Total Points'
    ))
    
    # Add bars for completed/progress
    fig.add_trace(go.Bar(
        y=names,
        x=[p*c for p, c in zip(points, completed)],
        orientation='h',
        marker=dict(
            color='rgba(29, 185, 84, 0.9)',
            line=dict(color='rgba(29, 185, 84, 1.0)', width=1)
        ),
        name='Earned Points'
    ))
    
    # Update layout
    fig.update_layout(
        title="Achievement Progress",
        barmode='overlay',
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="Points"
    )
    
    return fig

def display_audio_waveform(waveform_data: List[float], color: str = "#1DB954", bgcolor: str = "#F0F0F0", height: int = 100, width: int = 300):
    """
    Display an audio waveform visualization
    
    Args:
        waveform_data (list): List of waveform amplitude values (0.0 to 1.0)
        color (str): Waveform color
        bgcolor (str): Background color
        height (int): Height in pixels
        width (int): Width in pixels
    """
    if not waveform_data:
        return
    
    # Create HTML for waveform
    svg = f"""
    <svg width="{width}" height="{height}" style="background-color: {bgcolor};">
        <g transform="translate(0, {height/2})">
    """
    
    # Calculate bar width
    bar_width = max(1, width / len(waveform_data) - 1)
    
    # Draw bars
    for i, amplitude in enumerate(waveform_data):
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
    
    # Display using Streamlit
    st.markdown(svg, unsafe_allow_html=True)

def create_worldmap_listeners(country_data: Dict[str, int]) -> folium.Map:
    """
    Create a world map visualization of listeners by country
    
    Args:
        country_data (dict): Dictionary mapping country names to listener counts
        
    Returns:
        folium.Map: Folium map object
    """
    # Create base map
    m = folium.Map(location=[0, 0], zoom_start=2, tiles="cartodb positron")
    
    # Add country-level choropleth layer
    folium.Choropleth(
        geo_data="https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json",
        name="Listeners",
        data=country_data,
        columns=["Country", "Listeners"],
        key_on="feature.properties.name",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Listeners"
    ).add_to(m)
    
    return m

def display_progress_bar(current: int, total: int, text: str = "", color: str = "#1DB954"):
    """
    Display a custom progress bar
    
    Args:
        current (int): Current value
        total (int): Total/target value
        text (str): Text to display
        color (str): Bar color
    """
    # Calculate percentage
    percentage = min(100, int((current / total) * 100)) if total > 0 else 0
    
    # Create HTML for progress bar
    html = f"""
    <div style="margin-bottom: 10px;">
        <div style="width: 100%; background-color: #f0f0f0; border-radius: 10px; height: 20px;">
            <div style="width: {percentage}%; background-color: {color}; height: 20px; border-radius: 10px;"></div>
        </div>
        <div style="font-size: 14px; margin-top: 5px;">
            {text} ({percentage}% - {current}/{total})
        </div>
    </div>
    """
    
    # Display using Streamlit
    st.markdown(html, unsafe_allow_html=True)