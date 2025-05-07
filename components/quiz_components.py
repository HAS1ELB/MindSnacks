import streamlit as st
from typing import Dict, List, Any, Optional, Callable, Union
import random
import time

class QuizGenerator:
    """Component for generating and managing quizzes"""
    
    def __init__(self, key_prefix: str = "quiz_gen"):
        """
        Initialize quiz generator
        
        Args:
            key_prefix (str): Prefix for component keys
        """
        self.key_prefix = key_prefix
        
        # Initialize quiz state in session if needed
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state for quiz"""
        # Quiz questions
        if f"{self.key_prefix}_questions" not in st.session_state:
            st.session_state[f"{self.key_prefix}_questions"] = []
        
        # Current question index
        if f"{self.key_prefix}_current_index" not in st.session_state:
            st.session_state[f"{self.key_prefix}_current_index"] = 0
        
        # User responses
        if f"{self.key_prefix}_responses" not in st.session_state:
            st.session_state[f"{self.key_prefix}_responses"] = {}
        
        # Quiz completed flag
        if f"{self.key_prefix}_completed" not in st.session_state:
            st.session_state[f"{self.key_prefix}_completed"] = False
        
        # Quiz score
        if f"{self.key_prefix}_score" not in st.session_state:
            st.session_state[f"{self.key_prefix}_score"] = 0
    
    def set_questions(self, questions: List[Dict[str, Any]]):
        """
        Set quiz questions
        
        Args:
            questions (list): List of question dictionaries
        """
        # Reset quiz state
        st.session_state[f"{self.key_prefix}_questions"] = questions
        st.session_state[f"{self.key_prefix}_current_index"] = 0
        st.session_state[f"{self.key_prefix}_responses"] = {}
        st.session_state[f"{self.key_prefix}_completed"] = False
        st.session_state[f"{self.key_prefix}_score"] = 0
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """
        Get the current question
        
        Returns:
            dict: Current question or None if no questions
        """
        questions = st.session_state[f"{self.key_prefix}_questions"]
        index = st.session_state[f"{self.key_prefix}_current_index"]
        
        if not questions or index >= len(questions):
            return None
        
        return questions[index]
    
    def record_response(self, question_id: str, response: str):
        """
        Record user's response to a question
        
        Args:
            question_id (str): Question ID
            response (str): User's response
        """
        st.session_state[f"{self.key_prefix}_responses"][question_id] = response
    
    def next_question(self):
        """Move to the next question"""
        current_index = st.session_state[f"{self.key_prefix}_current_index"]
        questions = st.session_state[f"{self.key_prefix}_questions"]
        
        if current_index < len(questions) - 1:
            st.session_state[f"{self.key_prefix}_current_index"] = current_index + 1
        else:
            # Reached the end of the quiz
            st.session_state[f"{self.key_prefix}_completed"] = True
            self._calculate_score()
    
    def previous_question(self):
        """Move to the previous question"""
        current_index = st.session_state[f"{self.key_prefix}_current_index"]
        
        if current_index > 0:
            st.session_state[f"{self.key_prefix}_current_index"] = current_index - 1
    
    def is_completed(self) -> bool:
        """
        Check if quiz is completed
        
        Returns:
            bool: True if completed, False otherwise
        """
        return st.session_state[f"{self.key_prefix}_completed"]
    
    def get_score(self) -> int:
        """
        Get quiz score
        
        Returns:
            int: Score out of 100
        """
        return st.session_state[f"{self.key_prefix}_score"]
    
    def _calculate_score(self):
        """Calculate quiz score"""
        questions = st.session_state[f"{self.key_prefix}_questions"]
        responses = st.session_state[f"{self.key_prefix}_responses"]
        
        if not questions:
            st.session_state[f"{self.key_prefix}_score"] = 0
            return
        
        # Count correct answers
        correct_count = 0
        
        for question in questions:
            question_id = question.get("id", "")
            correct_answer = question.get("answer", "")
            
            if question_id in responses and responses[question_id] == correct_answer:
                correct_count += 1
        
        # Calculate percentage score
        score = int((correct_count / len(questions)) * 100)
        st.session_state[f"{self.key_prefix}_score"] = score
    
    def render_question(self, on_answer: Optional[Callable] = None):
        """
        Render the current question
        
        Args:
            on_answer (callable, optional): Function to call when an answer is submitted
        """
        # Get current question
        question = self.get_current_question()
        
        if not question:
            st.warning("No questions available.")
            return
        
        # Extract question data
        question_id = question.get("id", "")
        question_text = question.get("question", "")
        options = question.get("options", {})
        
        # Check if user has already answered this question
        responses = st.session_state[f"{self.key_prefix}_responses"]
        previous_response = responses.get(question_id)
        
        # Display question number and text
        questions = st.session_state[f"{self.key_prefix}_questions"]
        current_index = st.session_state[f"{self.key_prefix}_current_index"]
        
        st.markdown(f"### Question {current_index + 1} of {len(questions)}")
        st.markdown(f"**{question_text}**")
        
        # Display options as radio buttons
        selected_option = st.radio(
            "Select your answer:",
            options=list(options.keys()),
            format_func=lambda x: f"{x}: {options.get(x, '')}",
            index=list(options.keys()).index(previous_response) if previous_response in options else 0,
            key=f"{self.key_prefix}_q{question_id}"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_index > 0:
                if st.button("Previous", key=f"{self.key_prefix}_prev_btn"):
                    self.previous_question()
                    st.rerun()
        
        with col2:
            if st.button("Submit Answer", key=f"{self.key_prefix}_submit_btn"):
                # Record response
                self.record_response(question_id, selected_option)
                
                # Call callback if provided
                if on_answer:
                    on_answer(question_id, selected_option)
                
                # Move to next question
                self.next_question()
                st.rerun()
        
        with col3:
            if st.button("Skip", key=f"{self.key_prefix}_skip_btn"):
                # Move to next question without recording
                self.next_question()
                st.rerun()
    
    def render_results(self, on_restart: Optional[Callable] = None, on_review: Optional[Callable] = None):
        """
        Render quiz results
        
        Args:
            on_restart (callable, optional): Function to call when restart button is clicked
            on_review (callable, optional): Function to call when review button is clicked
        """
        # Get quiz data
        questions = st.session_state[f"{self.key_prefix}_questions"]
        responses = st.session_state[f"{self.key_prefix}_responses"]
        score = st.session_state[f"{self.key_prefix}_score"]
        
        # Display score
        st.markdown(f"## Quiz Results")
        
        # Score visualization
        self._render_score_gauge(score)
        
        # Score details
        correct_count = sum(1 for q in questions if q.get("id") in responses and responses[q.get("id")] == q.get("answer"))
        
        st.markdown(f"You answered **{correct_count}** out of **{len(questions)}** questions correctly.")
        
        # Performance assessment
        if score >= 90:
            st.success("Excellent! You have a great understanding of this topic.")
        elif score >= 70:
            st.success("Good job! You have a solid understanding of this topic.")
        elif score >= 50:
            st.warning("You're making progress. Review the topics you missed to improve your understanding.")
        else:
            st.error("You might need more study on this topic. Consider reviewing the content again.")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Restart Quiz", key=f"{self.key_prefix}_restart_btn"):
                # Reset current index but keep questions
                st.session_state[f"{self.key_prefix}_current_index"] = 0
                st.session_state[f"{self.key_prefix}_responses"] = {}
                st.session_state[f"{self.key_prefix}_completed"] = False
                
                # Call callback if provided
                if on_restart:
                    on_restart()
                
                st.rerun()
        
        with col2:
            if st.button("Review Answers", key=f"{self.key_prefix}_review_btn"):
                # Call callback if provided
                if on_review:
                    on_review()
    
    def render_answer_review(self):
        """Render a review of all questions with correct answers"""
        # Get quiz data
        questions = st.session_state[f"{self.key_prefix}_questions"]
        responses = st.session_state[f"{self.key_prefix}_responses"]
        
        st.markdown("## Answer Review")
        
        # Display each question with correct answer
        for i, question in enumerate(questions):
            question_id = question.get("id", "")
            question_text = question.get("question", "")
            options = question.get("options", {})
            correct_answer = question.get("answer", "")
            explanation = question.get("explanation", "")
            
            # User's response
            user_response = responses.get(question_id, "Not answered")
            
            # Create container for question
            with st.container():
                st.markdown(f"### Question {i + 1}: {question_text}")
                
                # Display all options
                for option_key, option_text in options.items():
                    if option_key == correct_answer:
                        st.markdown(f"✅ **{option_key}: {option_text}** (Correct Answer)")
                    elif option_key == user_response:
                        st.markdown(f"❌ **{option_key}: {option_text}** (Your Answer)")
                    else:
                        st.markdown(f"  {option_key}: {option_text}")
                
                # Display explanation if available
                if explanation:
                    st.info(f"**Explanation:** {explanation}")
                
                st.markdown("---")
    
    def _render_score_gauge(self, score: int):
        """
        Render a gauge visualization for the score
        
        Args:
            score (int): Score out of 100
        """
        # HTML/CSS for gauge
        html = f"""
        <div style="text-align: center;">
            <div style="display: inline-block; position: relative; width: 200px; height: 100px; overflow: hidden;">
                <div style="background-color: #ddd; height: 100px; width: 200px; border-radius: 100px 100px 0 0;"></div>
                <div style="position: absolute; top: 0; left: 0; background-color: {'#1DB954' if score >= 70 else '#ff9800' if score >= 50 else '#f44336'}; height: 100px; width: 200px; border-radius: 100px 100px 0 0; transform-origin: bottom center; transform: rotate(calc(180deg * {score}/100)) scale(0.99);"></div>
                <div style="position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 10px; height: 50px; background-color: #333; transform-origin: bottom center;  transform: rotate(calc(180deg * {score}/100));"></div>
                <div style="position: absolute; bottom: 0; width: 30px; height: 30px; background-color: #333; left: 50%; transform: translateX(-50%); border-radius: 50%;"></div>
                <div style="position: absolute; bottom: 15px; width: 200px; text-align: center; font-size: 30px; font-weight: bold; color: #333;">{score}%</div>
            </div>
        </div>
        """
        
        st.markdown(html, unsafe_allow_html=True)

class QuizTimer:
    """Timer component for quizzes"""
    
    def __init__(self, key_prefix: str = "quiz_timer"):
        """
        Initialize quiz timer
        
        Args:
            key_prefix (str): Prefix for component keys
        """
        self.key_prefix = key_prefix
        
        # Initialize timer state
        if f"{self.key_prefix}_start_time" not in st.session_state:
            st.session_state[f"{self.key_prefix}_start_time"] = None
        
        if f"{self.key_prefix}_elapsed" not in st.session_state:
            st.session_state[f"{self.key_prefix}_elapsed"] = 0
        
        if f"{self.key_prefix}_running" not in st.session_state:
            st.session_state[f"{self.key_prefix}_running"] = False
    
    def start(self):
        """Start the timer"""
        if not st.session_state[f"{self.key_prefix}_running"]:
            st.session_state[f"{self.key_prefix}_start_time"] = time.time()
            st.session_state[f"{self.key_prefix}_running"] = True
    
    def stop(self):
        """Stop the timer"""
        if st.session_state[f"{self.key_prefix}_running"]:
            # Add elapsed time
            elapsed = time.time() - st.session_state[f"{self.key_prefix}_start_time"]
            st.session_state[f"{self.key_prefix}_elapsed"] += elapsed
            st.session_state[f"{self.key_prefix}_running"] = False
    
    def reset(self):
        """Reset the timer"""
        st.session_state[f"{self.key_prefix}_start_time"] = None
        st.session_state[f"{self.key_prefix}_elapsed"] = 0
        st.session_state[f"{self.key_prefix}_running"] = False
    
    def get_elapsed(self) -> float:
        """
        Get elapsed time in seconds
        
        Returns:
            float: Elapsed time in seconds
        """
        elapsed = st.session_state[f"{self.key_prefix}_elapsed"]
        
        # Add current running time if timer is active
        if st.session_state[f"{self.key_prefix}_running"]:
            current = time.time() - st.session_state[f"{self.key_prefix}_start_time"]
            elapsed += current
        
        return elapsed
    
    def render(self):
        """Render the timer"""
        elapsed = self.get_elapsed()
        
        # Format as minutes and seconds
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        # Display timer
        st.markdown(f"⏱️ **Time:** {minutes:02d}:{seconds:02d}")
        
        # Update every second
        st.rerun()