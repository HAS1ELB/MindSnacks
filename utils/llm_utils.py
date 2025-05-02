import groq
import time
import uuid
from config import GROQ_API_KEY, LLAMA4_MODEL
from templates.prompt_templates import get_learning_prompt, get_recommendation_prompt

# Initialiser le client Groq
client = groq.Groq(api_key=GROQ_API_KEY)

def generate_learning_snippet(topic, duration_minutes=5):
    """
    Génère un snippet d'apprentissage sur un sujet spécifique.
    
    Args:
        topic (str): Le sujet pour lequel générer un snippet d'apprentissage
        duration_minutes (int): Durée cible en minutes pour le snippet audio
    
    Returns:
        dict: Dictionnaire contenant le titre et le contenu du snippet
    """
    # Estimer le nombre de mots pour la durée cible (environ 150 mots/minute pour l'audio)
    target_word_count = duration_minutes * 150
    
    # Construire le prompt pour le LLM
    prompt = get_learning_prompt(topic, target_word_count)
    
    try:
        # Appeler l'API Groq avec Llama4
        response = client.chat.completions.create(
            model=LLAMA4_MODEL,
            messages=[
                {"role": "system", "content": "Vous êtes un expert éducatif qui crée des explications claires, engageantes et informatives sur divers sujets. Votre tâche est de générer un contenu audio de 5 minutes qui est à la fois informatif et agréable à écouter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        
        # Extraire et traiter la réponse
        content = response.choices[0].message.content
        
        # Extraire le titre et le contenu
        lines = content.split('\n')
        title = lines[0].replace('# ', '').strip()
        body = '\n'.join(lines[1:]).strip()
        
        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": body,
            "topic": topic,
            "target_duration": duration_minutes,
        }
    
    except Exception as e:
        print(f"Erreur lors de la génération du contenu: {e}")
        return {
            "id": str(uuid.uuid4()),
            "title": f"Introduction à {topic}",
            "content": f"Nous n'avons pas pu générer de contenu pour {topic} en raison d'une erreur. Veuillez réessayer plus tard.",
            "topic": topic,
            "target_duration": duration_minutes,
        }

def generate_recommendation(previous_topics, count=1):
    """
    Génère des recommandations de sujets basés sur les intérêts précédents de l'utilisateur.
    
    Args:
        previous_topics (list): Liste des sujets précédemment demandés par l'utilisateur
        count (int): Nombre de recommandations à générer
    
    Returns:
        list: Liste des sujets recommandés
    """
    prompt = get_recommendation_prompt(previous_topics, count)
    
    try:
        # Appeler l'API Groq avec Llama4
        response = client.chat.completions.create(
            model=LLAMA4_MODEL,
            messages=[
                {"role": "system", "content": "Vous êtes un expert en recommandation de contenu éducatif. Votre tâche est de suggérer des sujets intéressants basés sur les intérêts précédents de l'utilisateur."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500,
        )
        
        # Extraire et traiter la réponse
        content = response.choices[0].message.content
        
        # Extraire les recommandations (supposant un format de liste)
        recommendations = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                recommendations.append(line[2:].strip())
            elif line.startswith('#'):
                continue
            elif line and not line.startswith('```'):
                recommendations.append(line)
        
        # Limiter au nombre demandé
        return recommendations[:count]
    
    except Exception as e:
        print(f"Erreur lors de la génération des recommandations: {e}")
        return [f"Un sujet connexe à {', '.join(previous_topics[:2])}"]