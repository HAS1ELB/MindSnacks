import groq
import time
import uuid
from config import GROQ_API_KEY, LLAMA4_MODEL
from templates.prompt_templates import get_learning_prompt, get_recommendation_prompt

# Initialiser le client Groq
client = groq.Groq(api_key=GROQ_API_KEY)

def generate_learning_snippet(topic, duration_minutes=5, language='fr'):
    """
    Génère un snippet d'apprentissage sur un sujet spécifique.
    """
    target_word_count = duration_minutes * 150
    
    prompt = get_learning_prompt(topic, target_word_count, language)
    
    try:
        response = client.chat.completions.create(
            model=LLAMA4_MODEL,
            messages=[
                {"role": "system", "content": "Vous êtes un expert éducatif qui crée des explications claires, engageantes et informatives sur divers sujets. Votre tâche est de générer un contenu audio de 5 minutes qui est à la fois informatif et agréable à écouter. Répondez dans la langue spécifiée par l'utilisateur."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        
        content = response.choices[0].message.content
        
        lines = content.split('\n')
        title = lines[0].replace('# ', '').strip()
        body = '\n'.join(lines[1:]).strip()
        
        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": body,
            "topic": topic,
            "target_duration": duration_minutes,
            "language": language
        }
    
    except Exception as e:
        print(f"Erreur lors de la génération du contenu: {e}")
        
        # Messages d'erreur multilingues
        error_messages = {
            'fr': f"Nous n'avons pas pu générer de contenu pour {topic} en raison d'une erreur. Veuillez réessayer plus tard.",
            'en': f"We couldn't generate content for {topic} due to an error. Please try again later.",
            'es': f"No pudimos generar contenido para {topic} debido a un error. Por favor, inténtalo más tarde.",
            'de': f"Wir konnten für {topic} aufgrund eines Fehlers keinen Inhalt generieren. Bitte versuchen Sie es später erneut.",
            'it': f"Non abbiamo potuto generare contenuti per {topic} a causa di un errore. Per favore riprova più tardi.",
            'ja': f"エラーのため、{topic}のコンテンツを生成できませんでした。後でもう一度お試しください。",
            'zh': f"由于错误，我们无法为{topic}生成内容。请稍后再试。"
        }
        
        error_message = error_messages.get(language, error_messages['en'])
        
        return {
            "id": str(uuid.uuid4()),
            "title": f"Introduction à {topic}",
            "content": error_message,
            "topic": topic,
            "target_duration": duration_minutes,
            "language": language
        }

def generate_recommendation(previous_topics, count=1, language='fr'):
    """
    Génère des recommandations de sujets basés sur les intérêts précédents de l'utilisateur.
    """
    prompt = get_recommendation_prompt(previous_topics, count, language)
    
    try:
        response = client.chat.completions.create(
            model=LLAMA4_MODEL,
            messages=[
                {"role": "system", "content": "Vous êtes un expert en recommandation de contenu éducatif. Votre tâche est de suggérer des sujets intéressants basés sur les intérêts précédents de l'utilisateur. Répondez dans la langue spécifiée par l'utilisateur."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500,
        )
        
        content = response.choices[0].message.content
        
        recommendations = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                recommendations.append(line[2:].strip())
            # Suppression de la condition qui ajoute d'autres types de texte
        
        # Si nous n'avons pas assez de recommandations, utilisons une approche alternative
        if len(recommendations) < count:
            import re
            # Essayer de trouver des points dans le texte qui pourraient être des sujets
            additional_lines = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|$)', content, re.DOTALL)
            for line in additional_lines:
                line = line.strip()
                if line and len(recommendations) < count:
                    recommendations.append(line)
        
        return recommendations[:count]
    
    except Exception as e:
        print(f"Erreur lors de la génération des recommandations: {e}")
        
        # Message par défaut dans la langue demandée
        default_messages = {
            'fr': f"Un sujet connexe à {', '.join(previous_topics[:2])}",
            'en': f"A topic related to {', '.join(previous_topics[:2])}",
            'es': f"Un tema relacionado con {', '.join(previous_topics[:2])}",
            'de': f"Ein Thema im Zusammenhang mit {', '.join(previous_topics[:2])}",
            'it': f"Un argomento correlato a {', '.join(previous_topics[:2])}",
            'ja': f"{', '.join(previous_topics[:2])}に関連するトピック",
            'zh': f"与{', '.join(previous_topics[:2])}相关的主题"
        }
        
        return [default_messages.get(language, default_messages['en'])]
