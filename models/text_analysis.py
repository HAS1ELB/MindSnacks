from typing import List, Dict, Any, Optional, Tuple, Union
import re
import nltk
import logging
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Configure logging
logger = logging.getLogger(__name__)

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextAnalysis:
    """
    Tools for analyzing and extracting information from text content
    """
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10, language: str = 'english') -> List[Tuple[str, float]]:
        """
        Extract keywords from text using TF-IDF
        
        Args:
            text (str): Input text
            max_keywords (int): Maximum number of keywords to extract
            language (str): Language for stopwords
            
        Returns:
            list: List of (keyword, score) tuples
        """
        try:
            # Handle language mapping for NLTK
            lang_map = {
                'en': 'english',
                'fr': 'french',
                'es': 'spanish',
                'de': 'german',
                'it': 'italian',
            }
            nltk_lang = lang_map.get(language, language)
            
            # Get stopwords for the language
            try:
                stop_words = set(stopwords.words(nltk_lang))
            except:
                # Fallback to English if language not available
                stop_words = set(stopwords.words('english'))
            
            # Tokenize text
            words = word_tokenize(text.lower())
            
            # Remove stopwords and punctuation
            words = [word for word in words if word.isalnum() and word not in stop_words]
            
            # Calculate word frequencies
            word_freq = Counter(words)
            
            # Create a corpus with just this document
            corpus = [text]
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=max_keywords*2,  # Extract more than needed to filter later
                stop_words=nltk_lang
            )
            
            # Get TF-IDF scores
            tfidf_matrix = vectorizer.fit_transform(corpus)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get scores for the first (and only) document
            tfidf_scores = zip(feature_names, tfidf_matrix.toarray()[0])
            
            # Sort by score and get top keywords
            sorted_keywords = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
            
            # Filter out single characters and return top keywords
            filtered_keywords = [(word, score) for word, score in sorted_keywords if len(word) > 1]
            
            return filtered_keywords[:max_keywords]
        
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    @staticmethod
    def extract_key_sentences(text: str, max_sentences: int = 3) -> List[str]:
        """
        Extract key sentences from text
        
        Args:
            text (str): Input text
            max_sentences (int): Maximum number of sentences to extract
            
        Returns:
            list: List of key sentences
        """
        try:
            # Split into sentences
            sentences = sent_tokenize(text)
            
            # If few sentences, return all
            if len(sentences) <= max_sentences:
                return sentences
            
            # Create keyword dictionary
            keywords = TextAnalysis.extract_keywords(text, max_keywords=20)
            keyword_dict = {word: score for word, score in keywords}
            
            # Score sentences based on keywords
            sentence_scores = []
            
            for sentence in sentences:
                score = 0
                words = word_tokenize(sentence.lower())
                
                for word in words:
                    if word in keyword_dict:
                        score += keyword_dict[word]
                
                # Normalize by sentence length to prevent bias towards longer sentences
                if len(words) > 0:
                    score = score / len(words)
                
                sentence_scores.append((sentence, score))
            
            # Sort by score and get top sentences
            sorted_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)
            top_sentences = [sentence for sentence, score in sorted_sentences[:max_sentences]]
            
            # Return sentences in original order
            ordered_sentences = [s for s in sentences if s in top_sentences]
            
            return ordered_sentences
        
        except Exception as e:
            logger.error(f"Error extracting key sentences: {e}")
            return []
    
    @staticmethod
    def generate_summary(text: str, max_length: int = 200) -> str:
        """
        Generate a summary of text
        
        Args:
            text (str): Input text
            max_length (int): Maximum length of summary in words
            
        Returns:
            str: Summary text
        """
        try:
            # If text is already short, return it
            words = text.split()
            if len(words) <= max_length:
                return text
            
            # Extract key sentences
            num_sentences = max(3, int(max_length / 20))  # Estimate sentences needed
            key_sentences = TextAnalysis.extract_key_sentences(text, max_sentences=num_sentences)
            
            # Combine sentences
            summary = ' '.join(key_sentences)
            
            # Truncate if still too long
            summary_words = summary.split()
            if len(summary_words) > max_length:
                summary = ' '.join(summary_words[:max_length])
                
                # Add ellipsis if truncated mid-sentence
                if not summary.endswith('.'):
                    summary += '...'
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return text[:200] + '...' if len(text) > 200 else text
    
    @staticmethod
    def analyze_readability(text: str) -> Dict[str, Any]:
        """
        Analyze readability of text
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Readability metrics
        """
        try:
            # Count words, sentences, and syllables
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            word_count = len([w for w in words if w.isalnum()])
            sentence_count = len(sentences)
            
            # Estimate syllables (simple approximation)
            syllable_count = 0
            for word in words:
                if word.isalnum():
                    word = word.lower()
                    if word.endswith('e'):
                        word = word[:-1]
                    count = len(re.findall('[aeiou]', word))
                    syllable_count += max(1, count)
            
            # Calculate metrics
            if sentence_count == 0 or word_count == 0:
                return {
                    'word_count': word_count,
                    'sentence_count': sentence_count,
                    'average_words_per_sentence': 0,
                    'flesch_reading_ease': 0,
                    'readability_level': 'Unknown'
                }
            
            avg_words_per_sentence = word_count / sentence_count
            avg_syllables_per_word = syllable_count / word_count
            
            # Flesch Reading Ease
            flesch = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
            flesch = max(0, min(100, flesch))  # Clamp to 0-100
            
            # Determine readability level
            if flesch >= 90:
                level = 'Very Easy'
            elif flesch >= 80:
                level = 'Easy'
            elif flesch >= 70:
                level = 'Fairly Easy'
            elif flesch >= 60:
                level = 'Standard'
            elif flesch >= 50:
                level = 'Fairly Difficult'
            elif flesch >= 30:
                level = 'Difficult'
            else:
                level = 'Very Difficult'
            
            return {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'average_words_per_sentence': round(avg_words_per_sentence, 1),
                'flesch_reading_ease': round(flesch, 1),
                'readability_level': level
            }
        
        except Exception as e:
            logger.error(f"Error analyzing readability: {e}")
            return {
                'word_count': 0,
                'sentence_count': 0,
                'average_words_per_sentence': 0,
                'flesch_reading_ease': 0,
                'readability_level': 'Error'
            }
    
    @staticmethod
    def analyze_sentiment(text: str) -> Dict[str, Any]:
        """
        Simple sentiment analysis of text
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Sentiment analysis results
        """
        try:
            # This is a very simple implementation
            # In a real application, use a proper NLP library or service
            
            # Load positive and negative word lists
            positive_words = set([
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                'happy', 'joy', 'love', 'best', 'positive', 'beautiful', 'nice',
                'awesome', 'superb', 'outstanding', 'perfect', 'ideal', 'impressive'
            ])
            
            negative_words = set([
                'bad', 'terrible', 'awful', 'horrible', 'worst', 'poor', 'negative',
                'sad', 'hate', 'dislike', 'disappointing', 'failure', 'failed',
                'problem', 'difficult', 'wrong', 'trouble', 'unfortunate', 'ugly'
            ])
            
            # Tokenize and normalize
            words = word_tokenize(text.lower())
            
            # Count positive and negative words
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            # Calculate sentiment score (-1 to 1)
            total_count = positive_count + negative_count
            if total_count > 0:
                sentiment_score = (positive_count - negative_count) / total_count
            else:
                sentiment_score = 0
            
            # Determine sentiment label
            if sentiment_score > 0.2:
                sentiment = 'positive'
            elif sentiment_score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': round(sentiment_score, 2),
                'positive_count': positive_count,
                'negative_count': negative_count
            }
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0,
                'positive_count': 0,
                'negative_count': 0
            }
    
    @staticmethod
    def generate_quiz_question(text: str, topic: str) -> Dict[str, Any]:
        """
        Generate a simple quiz question from text
        
        Args:
            text (str): Content text
            topic (str): Topic of the content
            
        Returns:
            dict: Quiz question dictionary
        """
        try:
            # Extract key sentences
            key_sentences = TextAnalysis.extract_key_sentences(text, max_sentences=5)
            
            if not key_sentences:
                return {}
            
            # Choose a random sentence for the question
            import random
            sentence = random.choice(key_sentences)
            
            # Extract potential keywords
            keywords = TextAnalysis.extract_keywords(sentence, max_keywords=3)
            
            if not keywords:
                return {}
            
            # Choose a keyword to remove
            keyword, _ = random.choice(keywords)
            
            # Create question
            question_text = sentence.replace(keyword, "________")
            question_text = f"Complete the following: {question_text}"
            
            # Create options
            options = {
                "A": keyword,  # Correct answer
            }
            
            # Add distractors from other keywords
            all_keywords = TextAnalysis.extract_keywords(text, max_keywords=10)
            distractors = [word for word, _ in all_keywords if word != keyword][:3]
            
            if len(distractors) < 3:
                # If not enough distractors, add some generic ones
                generic_distractors = ["none of these", "all of the above", "cannot be determined"]
                distractors.extend(generic_distractors[:3 - len(distractors)])
            
            # Assign options
            option_labels = ["B", "C", "D"]
            for i, distractor in enumerate(distractors[:3]):
                options[option_labels[i]] = distractor
            
            # Create question dictionary
            question = {
                "question": question_text,
                "options": options,
                "answer": "A",
                "explanation": f"The correct answer is '{keyword}' which completes the sentence from the text about {topic}."
            }
            
            return question
        
        except Exception as e:
            logger.error(f"Error generating quiz question: {e}")
            return {}