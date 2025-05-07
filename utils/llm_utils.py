import groq
import time
import uuid
import json
import logging
import os
import hashlib
import re
import asyncio
import nltk
from typing import List, Dict, Any, Optional, Union
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq

from config import (
    GROQ_API_KEY, LLM_MODELS, CACHE_DIR, 
    WORDS_PER_MINUTE, QUIZ_DIR, DEFAULT_SNIPPET_DURATION
)
from utils.data_utils import memory_cache
from templates.prompt_templates import (
    get_learning_prompt, get_recommendation_prompt,
    get_quiz_prompt, get_summarization_prompt
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Groq client
client = groq.Groq(api_key=GROQ_API_KEY)

# Initialize LangChain components
llm = ChatGroq(api_key=GROQ_API_KEY, model_name=LLM_MODELS["default"])

# Download NLTK data if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class ContentGenerationManager:
    """
    Manager class for content generation with caching, fallback models, and optimizations
    """
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
        self.default_model = LLM_MODELS["default"]
        self.fallback_model = LLM_MODELS["fallback"]
        self.temperature = 0.7
        
    def _get_cache_path(self, cache_key):
        return os.path.join(self.cache_dir, f"{cache_key}.json")
        
    def _check_cache(self, cache_key):
        """Check if content is in the cache"""
        # Check memory cache first
        cached_content = memory_cache.get(cache_key)
        if cached_content:
            logger.info(f"Cache hit (memory): {cache_key}")
            return cached_content
            
        # Check file cache
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_content = json.load(f)
                    
                # Also put in memory cache for faster access
                memory_cache.set(cache_key, cached_content)
                
                logger.info(f"Cache hit (disk): {cache_key}")
                return cached_content
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                
        return None
        
    def _save_cache(self, cache_key, content):
        """Save content to the cache"""
        try:
            # Save to memory cache
            memory_cache.set(cache_key, content)
            
            # Save to file cache
            cache_path = self._get_cache_path(cache_key)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved to cache: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            return False
    
    async def generate_content(self, prompt, model=None, temperature=None, max_tokens=1500, cache_key=None):
        """
        Generate content with caching and fallbacks
        
        Args:
            prompt (str): Prompt for the LLM
            model (str, optional): Model to use
            temperature (float, optional): Temperature parameter
            max_tokens (int): Maximum tokens to generate
            cache_key (str, optional): Custom cache key
            
        Returns:
            str: Generated content
        """
        if not model:
            model = self.default_model
            
        if temperature is None:
            temperature = self.temperature
            
        # Create cache key if not provided
        if not cache_key:
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
            cache_key = f"content_{prompt_hash}_{model.replace('/', '_')}_{temperature}_{max_tokens}"
        
        # Check cache
        cached_content = self._check_cache(cache_key)
        if cached_content:
            return cached_content
        
        try:
            logger.info(f"Generating content using model: {model}")
            
            # Make API call to Groq
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            
            # Cache the result
            self._save_cache(cache_key, content)
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating content with {model}: {e}")
            
            # Try fallback model if different from current
            if model != self.fallback_model:
                logger.info(f"Trying fallback model: {self.fallback_model}")
                try:
                    response = await asyncio.to_thread(
                        client.chat.completions.create,
                        model=self.fallback_model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    
                    content = response.choices[0].message.content
                    return content
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback model also failed: {fallback_error}")
            
            # If all fails, return error message
            return "Error generating content. Please try again later."

# Create a singleton manager instance
content_manager = ContentGenerationManager()

async def generate_learning_snippet(topic, duration_minutes=DEFAULT_SNIPPET_DURATION, language='en'):
    """
    Generate a learning snippet on a specific topic
    
    Args:
        topic (str): The topic to generate content about
        duration_minutes (int): Target duration in minutes
        language (str): Language code
        
    Returns:
        dict: Generated snippet with metadata
    """
    # Calculate target word count based on reading speed
    target_word_count = duration_minutes * WORDS_PER_MINUTE
    
    # Create cache key based on parameters
    topic_hash = hashlib.md5(topic.encode()).hexdigest()
    cache_key = f"snippet_{topic_hash}_{language}_{duration_minutes}"
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    # Check if we have a cached version
    cached_snippet = content_manager._check_cache(cache_key)
    if cached_snippet:
        logger.info(f"Using cached snippet for topic: {topic}, language: {language}")
        return cached_snippet
    
    # Get the prompt for the learning snippet
    prompt = get_learning_prompt(topic, target_word_count, language)
    
    try:
        # Log the API call
        logger.info(f"Generating snippet for topic: {topic}, language: {language}, duration: {duration_minutes}mins")
        
        # Generate content through the manager
        content = await content_manager.generate_content(
            prompt=prompt,
            model=LLM_MODELS["generation"],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse content to get title and body
        lines = content.split('\n')
        
        # Extract title (first line that starts with #)
        title_line = next((line for line in lines if line.strip().startswith('#')), None)
        if title_line:
            title = title_line.replace('#', '').strip()
            # Remove title line from content
            lines.remove(title_line)
        else:
            # If no title with # is found, use the first line
            title = lines[0].strip()
            lines.pop(0)
        
        body = '\n'.join(lines).strip()
        
        # Create snippet object
        snippet = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": body,
            "topic": topic,
            "target_duration": duration_minutes,
            "language": language,
            "created_at": time.time(),
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        
        # Cache the snippet
        content_manager._save_cache(cache_key, snippet)
        
        return snippet
    
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        
        # Multilingual error messages
        error_messages = {
            'fr': f"Nous n'avons pas pu générer de contenu pour {topic} en raison d'une erreur. Veuillez réessayer plus tard.",
            'en': f"We couldn't generate content for {topic} due to an error. Please try again later.",
            'es': f"No pudimos generar contenido para {topic} debido a un error. Por favor, inténtalo más tarde.",
            'de': f"Wir konnten für {topic} aufgrund eines Fehlers keinen Inhalt generieren. Bitte versuchen Sie es später erneut.",
            'it': f"Non abbiamo potuto generare contenuti per {topic} a causa di un errore. Per favore riprova più tardi.",
            'ja': f"エラーのため、{topic}のコンテンツを生成できませんでした。後でもう一度お試しください。",
            'zh': f"由于错误，我们无法为{topic}生成内容。请稍后再试。",
            'ar': f"لم نتمكن من إنشاء محتوى لـ {topic} بسبب خطأ. يرجى المحاولة مرة أخرى لاحقًا."
        }
        
        error_message = error_messages.get(language, error_messages['en'])
        
        # Return error snippet
        return {
            "id": str(uuid.uuid4()),
            "title": f"Introduction to {topic}",
            "content": error_message,
            "topic": topic,
            "target_duration": duration_minutes,
            "language": language,
            "error": True,
            "created_at": time.time(),
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

async def generate_recommendation(previous_topics, count=3, language='en'):
    """
    Generate topic recommendations based on user's previous interests
    
    Args:
        previous_topics (list): List of topics the user has previously viewed
        count (int): Number of recommendations to generate
        language (str): Language code
        
    Returns:
        list: List of recommended topics
    """
    # Create cache key based on parameters
    topics_hash = '_'.join(sorted(previous_topics)[:3])  # Use only the first 3 topics for caching
    cache_key = f"recommendations_{hashlib.md5(topics_hash.encode()).hexdigest()}_{language}_{count}"
    
    # Check if we have a cached version
    cached_recommendations = content_manager._check_cache(cache_key)
    if cached_recommendations:
        logger.info(f"Using cached recommendations for topics: {topics_hash}, language: {language}")
        return cached_recommendations
    
    # Get the prompt for recommendations
    prompt = get_recommendation_prompt(previous_topics, count, language)
    
    try:
        # Generate recommendations through the manager
        content = await content_manager.generate_content(
            prompt=prompt,
            temperature=0.8,
            max_tokens=500
        )
        
        # Parse recommendations
        recommendations = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                recommendations.append(line[2:].strip())
        
        # If we don't have enough recommendations, try an alternative approach
        if len(recommendations) < count:
            import re
            # Try to find points in the text that might be topics
            additional_lines = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|$)', content, re.DOTALL)
            for line in additional_lines:
                line = line.strip()
                if line and len(recommendations) < count:
                    recommendations.append(line)
        
        # Ensure we return the requested number of recommendations (or fewer if not enough)
        recommendations = recommendations[:count]
        
        # Cache the recommendations
        content_manager._save_cache(cache_key, recommendations)
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        
        # Default message in the requested language
        default_messages = {
            'fr': [f"Un sujet connexe à {', '.join(previous_topics[:2])}" for _ in range(count)],
            'en': [f"A topic related to {', '.join(previous_topics[:2])}" for _ in range(count)],
            'es': [f"Un tema relacionado con {', '.join(previous_topics[:2])}" for _ in range(count)],
            'de': [f"Ein Thema im Zusammenhang mit {', '.join(previous_topics[:2])}" for _ in range(count)],
            'it': [f"Un argomento correlato a {', '.join(previous_topics[:2])}" for _ in range(count)],
            'ja': [f"{', '.join(previous_topics[:2])}に関連するトピック" for _ in range(count)],
            'zh': [f"与{', '.join(previous_topics[:2])}相关的主题" for _ in range(count)],
            'ar': [f"موضوع متعلق بـ {', '.join(previous_topics[:2])}" for _ in range(count)]
        }
        
        return default_messages.get(language, default_messages['en'])

async def generate_quiz_questions(topic, content, question_count=5, language='en', difficulty='medium'):
    """
    Generate quiz questions based on learning content
    
    Args:
        topic (str): Topic of the content
        content (str): The learning content
        question_count (int): Number of questions to generate
        language (str): Language code
        difficulty (str): Quiz difficulty (easy, medium, hard)
        
    Returns:
        list: List of quiz questions with options and answers
    """
    # Create cache key
    content_hash = hashlib.md5(content.encode()).hexdigest()
    cache_key = f"quiz_{content_hash}_{language}_{difficulty}_{question_count}"
    
    # Check cache
    cached_quiz = content_manager._check_cache(cache_key)
    if cached_quiz:
        return cached_quiz
    
    # Get quiz prompt
    prompt = get_quiz_prompt(topic, question_count, language, difficulty, content)
    
    try:
        # Generate quiz through the manager
        quiz_content = await content_manager.generate_content(
            prompt=prompt,
            temperature=0.5,
            max_tokens=1500
        )
        
        # Parse quiz questions
        quiz_questions = []
        current_question = None
        
        for line in quiz_content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # New question starts with Q1, Q2, etc.
            if re.match(r'^Q\d+:', line):
                if current_question:
                    quiz_questions.append(current_question)
                
                # Initialize new question
                question_text = line.split(':', 1)[1].strip()
                current_question = {
                    "id": str(uuid.uuid4()),
                    "question": question_text,
                    "options": {},
                    "answer": None,
                    "explanation": None,
                    "difficulty": difficulty
                }
            
            # Option lines start with A:, B:, etc.
            elif re.match(r'^[A-D]:', line) and current_question:
                option_key = line[0]
                option_text = line[2:].strip()
                current_question["options"][option_key] = option_text
            
            # Answer line
            elif line.lower().startswith('answer:') and current_question:
                answer = line.split(':', 1)[1].strip()
                current_question["answer"] = answer
            
            # Explanation line
            elif line.lower().startswith('explanation:') and current_question:
                explanation = line.split(':', 1)[1].strip()
                current_question["explanation"] = explanation
        
        # Add the last question
        if current_question:
            quiz_questions.append(current_question)
        
        # Cache the quiz
        if quiz_questions:
            # Save to separate files for each question
            quiz_dir = os.path.join(QUIZ_DIR, topic.replace(' ', '_'))
            os.makedirs(quiz_dir, exist_ok=True)
            
            for i, question in enumerate(quiz_questions):
                question_file = os.path.join(quiz_dir, f"question_{i+1}.json")
                with open(question_file, 'w') as f:
                    json.dump(question, f, indent=2)
            
            # Cache full quiz
            content_manager._save_cache(cache_key, quiz_questions)
        
        return quiz_questions
    
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return []

async def analyze_sentiment(text, language='en'):
    """
    Analyze sentiment of a text
    
    Args:
        text (str): Text to analyze
        language (str): Language code
        
    Returns:
        dict: Sentiment analysis results
    """
    prompts = {
        'fr': f"Analysez le sentiment du texte suivant et classez-le comme positif, négatif ou neutre. Donnez également un score de sentiment de -1 (très négatif) à 1 (très positif). Texte: {text}",
        'en': f"Analyze the sentiment of the following text and classify it as positive, negative, or neutral. Also provide a sentiment score from -1 (very negative) to 1 (very positive). Text: {text}",
        'es': f"Analiza el sentimiento del siguiente texto y clasifícalo como positivo, negativo o neutro. También proporciona una puntuación de sentimiento de -1 (muy negativo) a 1 (muy positivo). Texto: {text}",
        'de': f"Analysieren Sie die Stimmung des folgenden Textes und klassifizieren Sie ihn als positiv, negativ oder neutral. Geben Sie auch eine Stimmungsbewertung von -1 (sehr negativ) bis 1 (sehr positiv) an. Text: {text}",
        'it': f"Analizza il sentimento del seguente testo e classificalo come positivo, negativo o neutro. Fornisci anche un punteggio di sentimento da -1 (molto negativo) a 1 (molto positivo). Testo: {text}",
        'ja': f"次のテキストの感情を分析し、ポジティブ、ネガティブ、またはニュートラルに分類してください。また、-1（非常にネガティブ）から1（非常にポジティブ）までの感情スコアも提供してください。テキスト: {text}",
        'zh': f"分析以下文本的情感，并将其分类为积极、消极或中性。还请提供从-1（非常消极）到1（非常积极）的情感分数。文本: {text}",
        'ar': f"حلل مشاعر النص التالي وصنفه على أنه إيجابي أو سلبي أو محايد. قدم أيضًا درجة مشاعر من -1 (سلبي للغاية) إلى 1 (إيجابي للغاية). النص: {text}"
    }
    
    prompt = prompts.get(language, prompts['en'])
    
    try:
        # Generate analysis through the manager
        result = await content_manager.generate_content(
            prompt=prompt,
            temperature=0.3,
            max_tokens=150
        )
        
        # Extract sentiment from result
        sentiment = "neutral"
        score = 0
        
        if "positif" in result.lower() or "positive" in result.lower() or "positivo" in result.lower():
            sentiment = "positive"
        elif "négatif" in result.lower() or "negative" in result.lower() or "negativo" in result.lower():
            sentiment = "negative"
        
        # Try to extract score
        score_match = re.search(r'[-+]?[0-9]*\.?[0-9]+', result)
        if score_match:
            try:
                score = float(score_match.group())
                # Ensure score is in range [-1, 1]
                score = max(min(score, 1.0), -1.0)
            except:
                pass
        
        return {
            "sentiment": sentiment,
            "score": score,
            "analysis": result
        }
    
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {
            "sentiment": "neutral",
            "score": 0,
            "analysis": "Error analyzing sentiment",
            "error": str(e)
        }

async def generate_summary(text, max_length=200, language='en'):
    """
    Generate a summary of longer text
    
    Args:
        text (str): Text to summarize
        max_length (int): Approximate maximum length of summary in words
        language (str): Language code
        
    Returns:
        str: Summarized text
    """
    # Skip if text is already short enough
    if len(text.split()) <= max_length:
        return text
    
    # Create cache key
    text_hash = hashlib.md5(text.encode()).hexdigest()
    cache_key = f"summary_{text_hash}_{language}_{max_length}"
    
    # Check cache
    cached_summary = content_manager._check_cache(cache_key)
    if cached_summary:
        return cached_summary
    
    # Get summarization prompt
    prompt = get_summarization_prompt(text, max_length, language)
    
    try:
        # Use summarization-optimized model
        summary = await content_manager.generate_content(
            prompt=prompt,
            model=LLM_MODELS["summarization"],
            temperature=0.3,
            max_tokens=max(500, max_length * 6)  # Approximate token count
        )
        
        # Cache the summary
        content_manager._save_cache(cache_key, summary)
        
        return summary
    
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        
        # Return a simple extract as fallback
        sentences = nltk.sent_tokenize(text)
        
        # Calculate how many sentences to keep
        target_sentences = max(3, len(sentences) // 3)  # At least 3 sentences or 1/3 of original
        
        simple_summary = ' '.join(sentences[:target_sentences])
        return simple_summary

async def extract_keywords(text, count=5, language='en'):
    """
    Extract key topics or concepts from text
    
    Args:
        text (str): Text to analyze
        count (int): Number of keywords to extract
        language (str): Language code
        
    Returns:
        list: Extracted keywords
    """
    prompt = f"Extract the {count} most important keywords or concepts from the following text. Return ONLY the keywords as a comma-separated list, with no additional text or explanation. Text: {text}"
    
    try:
        response = await content_manager.generate_content(
            prompt=prompt,
            temperature=0.3,
            max_tokens=100
        )
        
        # Parse the response
        keywords = [k.strip() for k in response.split(',')]
        
        # Limit to requested count
        return keywords[:count]
    
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        
        # Fallback to simple word frequency
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words (simplified list)
        stop_words = {'the', 'a', 'an', 'and', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were'}
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count occurrences
        word_counts = {}
        for word in filtered_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top words
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:count]
        
        return [word for word, _ in top_words]