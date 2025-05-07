import streamlit as st
import time
import asyncio
import random
import json
import os
import uuid
from datetime import datetime
import plotly.express as px
import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.let_it_rain import rain

from utils.llm_utils import generate_quiz_questions
from utils.data_utils import track_event
from utils.language_utils import get_translation
from config import QUIZ_DIR, ENABLE_ANALYTICS

def app():
    """Quiz page for testing knowledge from learning snippets"""
    
    # Get session state
    if 'session' not in st.session_state:
        st.error("Session not initialized. Please return to the home page.")
        if st.button("Go to Home"):
            switch_page("app")
        return
    
    # Initialize quiz state
    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = {
            'active_quiz': None,
            'current_question': 0,
            'answers': {},
            'score': 0,
            'total_questions': 0,
            'quiz_complete': False,
            'timer_start': None,
            'time_taken': 0,
            'feedback': {}
        }
    
    # Page title
    colored_header(
        label=get_translation('quiz_mode', st.session_state.language),
        description=get_translation('test_your_knowledge', st.session_state.language),
        color_name="orange-70"
    )
    
    # Main quiz flow
    if st.session_state.quiz_state['active_quiz'] is None:
        display_quiz_selection()
    elif st.session_state.quiz_state['quiz_complete']:
        display_quiz_results()
    else:
        display_active_quiz()

def display_quiz_selection():
    """Display quiz selection options"""
    
    st.subheader(get_translation('select_quiz_topic', st.session_state.language))
    
    # Two ways to select a quiz: from snippets or standalone
    tab1, tab2 = st.tabs([
        get_translation('from_my_snippets', st.session_state.language),
        get_translation('standalone_quiz', st.session_state.language)
    ])
    
    with tab1:
        # Get user's snippets
        snippets = st.session_state.session.get_playlist()
        
        if not snippets:
            st.info(get_translation('no_snippets_for_quiz', st.session_state.language))
            st.markdown(f"[{get_translation('create_snippets_first', st.session_state.language)}](#)")
        else:
            # Display snippets to choose from
            st.write(get_translation('select_snippet_for_quiz', st.session_state.language))
            
            for i, snippet in enumerate(snippets):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{i+1}. {snippet.get('title', 'Untitled')}**")
                    st.caption(f"Topic: {snippet.get('topic', 'Unknown')}")
                
                with col2:
                    if st.button(get_translation('create_quiz', st.session_state.language), key=f"quiz_snippet_{i}"):
                        with st.spinner(get_translation('creating_quiz', st.session_state.language)):
                            start_quiz_from_snippet(snippet)
    
    with tab2:
        # Option to create a quiz on any topic
        st.write(get_translation('create_standalone_quiz', st.session_state.language))
        
        # Topic input
        topic = st.text_input(get_translation('quiz_topic', st.session_state.language))
        
        # Difficulty selection
        difficulty_options = ['easy', 'medium', 'hard']
        difficulty = st.select_slider(
            get_translation('difficulty', st.session_state.language),
            options=difficulty_options,
            value='medium'
        )
        
        # Number of questions
        num_questions = st.slider(
            get_translation('number_of_questions', st.session_state.language),
            min_value=3,
            max_value=10,
            value=5
        )
        
        # Create quiz button
        if topic and st.button(get_translation('create_quiz', st.session_state.language), key="standalone_quiz"):
            with st.spinner(get_translation('creating_quiz', st.session_state.language)):
                start_standalone_quiz(topic, difficulty, num_questions)

def display_active_quiz():
    """Display the active quiz questions"""
    
    quiz = st.session_state.quiz_state['active_quiz']
    current_q = st.session_state.quiz_state['current_question']
    total_q = st.session_state.quiz_state['total_questions']
    
    # Display quiz header
    st.subheader(f"{quiz.get('title', 'Quiz')} - {get_translation('question', st.session_state.language)} {current_q + 1}/{total_q}")
    
    # Progress bar
    progress = (current_q) / total_q
    st.progress(progress)
    
    # Timer
    if st.session_state.quiz_state['timer_start'] is None:
        st.session_state.quiz_state['timer_start'] = time.time()
    
    elapsed = time.time() - st.session_state.quiz_state['timer_start']
    st.caption(f"{get_translation('time', st.session_state.language)}: {int(elapsed)} {get_translation('seconds', st.session_state.language)}")
    
    # Get current question
    if current_q < len(quiz.get('questions', [])):
        question = quiz['questions'][current_q]
        
        # Display question
        st.markdown(f"### {question.get('question', 'Question')}")
        
        # Display options
        options = question.get('options', {})
        selected_option = None
        
        for option_key, option_text in options.items():
            if st.button(f"{option_key}: {option_text}", key=f"option_{option_key}"):
                # Record answer
                st.session_state.quiz_state['answers'][current_q] = option_key
                selected_option = option_key
                
                # Check if correct
                is_correct = option_key == question.get('answer', '')
                if is_correct:
                    st.session_state.quiz_state['score'] += 1
                
                # Store feedback
                st.session_state.quiz_state['feedback'][current_q] = {
                    'selected': option_key,
                    'correct': question.get('answer', ''),
                    'is_correct': is_correct,
                    'explanation': question.get('explanation', '')
                }
                
                # Move to next question or complete quiz
                if current_q + 1 < total_q:
                    st.session_state.quiz_state['current_question'] += 1
                else:
                    # Quiz complete
                    st.session_state.quiz_state['quiz_complete'] = True
                    st.session_state.quiz_state['time_taken'] = elapsed
                    
                    # Record quiz results
                    record_quiz_results()
                
                st.rerun()
        
        # Skip button
        if st.button(get_translation('skip_question', st.session_state.language)):
            # Record as skipped
            st.session_state.quiz_state['answers'][current_q] = 'skipped'
            
            # Store feedback
            st.session_state.quiz_state['feedback'][current_q] = {
                'selected': 'skipped',
                'correct': question.get('answer', ''),
                'is_correct': False,
                'explanation': question.get('explanation', '')
            }
            
            # Move to next question or complete quiz
            if current_q + 1 < total_q:
                st.session_state.quiz_state['current_question'] += 1
            else:
                # Quiz complete
                st.session_state.quiz_state['quiz_complete'] = True
                st.session_state.quiz_state['time_taken'] = elapsed
                
                # Record quiz results
                record_quiz_results()
            
            st.rerun()
    else:
        # Fallback if we somehow don't have this question
        st.error(get_translation('question_error', st.session_state.language))
        
        # Button to complete quiz
        if st.button(get_translation('complete_quiz', st.session_state.language)):
            st.session_state.quiz_state['quiz_complete'] = True
            st.session_state.quiz_state['time_taken'] = elapsed
            st.rerun()

def display_quiz_results():
    """Display quiz results and feedback"""
    
    quiz = st.session_state.quiz_state['active_quiz']
    score = st.session_state.quiz_state['score']
    total = st.session_state.quiz_state['total_questions']
    percentage = int((score / total) * 100) if total > 0 else 0
    time_taken = st.session_state.quiz_state['time_taken']
    
    # Show celebratory effect for good scores
    if percentage >= 80:
        rain(
            emoji="🎉",
            font_size=54,
            falling_speed=5,
            animation_length=1,
        )
    
    # Results header
    st.subheader(get_translation('quiz_results', st.session_state.language))
    
    # Display score card
    st.markdown(f"""
    <div style="background-color: #282828; border-radius: 10px; padding: 20px; text-align: center;">
        <h1 style="color: #1DB954; font-size: 48px;">{score}/{total}</h1>
        <h2>{percentage}%</h2>
        <p>{get_translation('time_taken', st.session_state.language)}: {int(time_taken)} {get_translation('seconds', st.session_state.language)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance message
    if percentage >= 90:
        st.success(get_translation('excellent_performance', st.session_state.language))
    elif percentage >= 70:
        st.success(get_translation('good_performance', st.session_state.language))
    elif percentage >= 50:
        st.warning(get_translation('average_performance', st.session_state.language))
    else:
        st.error(get_translation('needs_improvement', st.session_state.language))
    
    # Question review
    st.subheader(get_translation('question_review', st.session_state.language))
    
    feedback = st.session_state.quiz_state['feedback']
    questions = quiz.get('questions', [])
    
    for i, question in enumerate(questions):
        q_feedback = feedback.get(i, {})
        is_correct = q_feedback.get('is_correct', False)
        
        # Question container
        expander_title = f"Q{i+1}: {question.get('question', 'Question')} {'✅' if is_correct else '❌'}"
        with st.expander(expander_title, expanded=False):
            # Question text
            st.markdown(f"**{question.get('question', 'Question')}**")
            
            # Options
            for option_key, option_text in question.get('options', {}).items():
                if option_key == q_feedback.get('correct', ''):
                    # Correct answer
                    st.markdown(f"✅ **{option_key}: {option_text}**")
                elif option_key == q_feedback.get('selected', ''):
                    # Selected wrong answer
                    st.markdown(f"❌ **{option_key}: {option_text}**")
                else:
                    # Other options
                    st.markdown(f"{option_key}: {option_text}")
            
            # Explanation
            if 'explanation' in q_feedback:
                st.markdown(f"**{get_translation('explanation', st.session_state.language)}:** {q_feedback['explanation']}")
    
    # Display a radar chart of topic knowledge
    if len(questions) > 0:
        st.subheader(get_translation('knowledge_areas', st.session_state.language))
        
        # Create data for the chart
        topics = ['Knowledge', 'Comprehension', 'Application', 'Analysis', 'Problem-Solving']
        
        # Randomly generate topic scores based on overall performance
        if percentage >= 80:
            scores = [random.randint(70, 100) for _ in range(len(topics))]
        elif percentage >= 60:
            scores = [random.randint(50, 90) for _ in range(len(topics))]
        else:
            scores = [random.randint(30, 70) for _ in range(len(topics))]
        
        df = pd.DataFrame({
            'Topic': topics,
            'Score': scores
        })
        
        # Create radar chart
        fig = px.line_polar(
            df, 
            r='Score', 
            theta='Topic', 
            line_close=True,
            range_r=[0, 100],
            color_discrete_sequence=['#1DB954']
        )
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(get_translation('retry_quiz', st.session_state.language)):
            # Reset quiz state but keep the same quiz
            reset_quiz_state(keep_quiz=True)
            st.rerun()
    
    with col2:
        if st.button(get_translation('new_quiz', st.session_state.language)):
            # Completely reset quiz state
            reset_quiz_state()
            st.rerun()
    
    with col3:
        if st.button(get_translation('back_to_library', st.session_state.language)):
            switch_page("library")

def start_quiz_from_snippet(snippet):
    """Start a quiz based on a snippet"""
    
    content = snippet.get('content', '')
    title = snippet.get('title', 'Quiz')
    topic = snippet.get('topic', 'General Knowledge')
    language = snippet.get('language', 'en')
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Generate quiz questions
        questions = loop.run_until_complete(generate_quiz_questions(
            topic, 
            content, 
            5,  # 5 questions by default for snippet quizzes
            language,
            'medium'  # Medium difficulty by default
        ))
        
        if questions:
            # Create quiz
            quiz = {
                'id': str(uuid.uuid4()),
                'title': f"Quiz: {title}",
                'topic': topic,
                'questions': questions,
                'language': language,
                'difficulty': 'medium',
                'source_snippet_id': snippet.get('id', None)
            }
            
            # Initialize quiz state
            reset_quiz_state()
            st.session_state.quiz_state['active_quiz'] = quiz
            st.session_state.quiz_state['total_questions'] = len(questions)
            
            # Track event
            track_event("quiz_started_from_snippet", {
                "topic": topic,
                "language": language,
                "question_count": len(questions)
            })
            
            return True
        else:
            st.error(get_translation('quiz_generation_failed', st.session_state.language))
            return False
            
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return False
    finally:
        loop.close()

def start_standalone_quiz(topic, difficulty='medium', num_questions=5):
    """Start a standalone quiz on any topic"""
    
    # Content prompt
    content = f"Create a comprehensive quiz about {topic}."
    language = st.session_state.language
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Generate quiz questions
        questions = loop.run_until_complete(generate_quiz_questions(
            topic, 
            content, 
            num_questions,
            language,
            difficulty
        ))
        
        if questions:
            # Create quiz
            quiz = {
                'id': str(uuid.uuid4()),
                'title': f"Quiz: {topic}",
                'topic': topic,
                'questions': questions,
                'language': language,
                'difficulty': difficulty,
                'source_snippet_id': None
            }
            
            # Initialize quiz state
            reset_quiz_state()
            st.session_state.quiz_state['active_quiz'] = quiz
            st.session_state.quiz_state['total_questions'] = len(questions)
            
            # Track event
            track_event("standalone_quiz_started", {
                "topic": topic,
                "language": language,
                "difficulty": difficulty,
                "question_count": len(questions)
            })
            
            return True
        else:
            st.error(get_translation('quiz_generation_failed', st.session_state.language))
            return False
            
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return False
    finally:
        loop.close()

def reset_quiz_state(keep_quiz=False):
    """Reset the quiz state"""
    
    # Preserve the active quiz if requested
    active_quiz = st.session_state.quiz_state['active_quiz'] if keep_quiz else None
    
    st.session_state.quiz_state = {
        'active_quiz': active_quiz,
        'current_question': 0,
        'answers': {},
        'score': 0,
        'total_questions': st.session_state.quiz_state['total_questions'] if keep_quiz else 0,
        'quiz_complete': False,
        'timer_start': None,
        'time_taken': 0,
        'feedback': {}
    }

def record_quiz_results():
    """Record quiz results to user history and save for analytics"""
    
    if not ENABLE_ANALYTICS:
        return
    
    quiz = st.session_state.quiz_state['active_quiz']
    score = st.session_state.quiz_state['score']
    total = st.session_state.quiz_state['total_questions']
    percentage = int((score / total) * 100) if total > 0 else 0
    time_taken = st.session_state.quiz_state['time_taken']
    
    # Record to user session
    quiz_result = st.session_state.session.record_quiz_score(
        quiz.get('topic', 'General Knowledge'),
        score,
        total
    )
    
    # Track quiz completion event
    track_event("quiz_completed", {
        "topic": quiz.get('topic', 'General Knowledge'),
        "score": score,
        "total": total,
        "percentage": percentage,
        "time_taken": time_taken,
        "difficulty": quiz.get('difficulty', 'medium'),
        "language": quiz.get('language', 'en'),
        "source_snippet_id": quiz.get('source_snippet_id', None)
    })
    
    # Save detailed quiz results
    try:
        # Create quiz directory
        quiz_id = quiz.get('id', str(uuid.uuid4()))
        quiz_dir = os.path.join(QUIZ_DIR, quiz_id)
        os.makedirs(quiz_dir, exist_ok=True)
        
        # Save full quiz results
        result_file = os.path.join(quiz_dir, f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        result_data = {
            'quiz_id': quiz_id,
            'topic': quiz.get('topic', 'General Knowledge'),
            'user_id': st.session_state.session.user_id,
            'score': score,
            'total': total,
            'percentage': percentage,
            'time_taken': time_taken,
            'difficulty': quiz.get('difficulty', 'medium'),
            'language': quiz.get('language', 'en'),
            'source_snippet_id': quiz.get('source_snippet_id', None),
            'answers': st.session_state.quiz_state['answers'],
            'feedback': st.session_state.quiz_state['feedback'],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving quiz results: {str(e)}")

if __name__ == "__main__":
    app()