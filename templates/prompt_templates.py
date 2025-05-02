def get_learning_prompt(topic, target_word_count):
    """
    Génère un prompt pour la création d'un snippet d'apprentissage.
    
    Args:
        topic (str): Le sujet du snippet
        target_word_count (int): Le nombre de mots cible
    
    Returns:
        str: Le prompt formaté
    """
    return f"""
    Créez un snippet d'apprentissage engageant sur le sujet: {topic}.
    
    Directives:
    1. Commencez par un titre accrocheur commençant par '# '
    2. Écrivez un contenu d'environ {target_word_count} mots (pour environ 5 minutes d'audio)
    3. Utilisez un ton conversationnel, comme si vous parliez à un ami curieux
    4. Structurez le contenu avec une introduction, des points clés et une conclusion
    5. Incluez 2-3 faits surprenants ou peu connus
    6. Évitez le jargon technique excessif, mais ne simplifiez pas trop
    7. Terminez avec une réflexion ou une question qui suscite la curiosité
    
    Le contenu doit être informatif, fascinant et facile à suivre lors d'une écoute audio.
    """

def get_recommendation_prompt(previous_topics, count):
    """
    Génère un prompt pour obtenir des recommandations de sujets.
    
    Args:
        previous_topics (list): Liste des sujets précédemment consultés
        count (int): Nombre de recommandations demandées
    
    Returns:
        str: Le prompt formaté
    """
    topics_str = ', '.join(previous_topics)
    return f"""
    En fonction des sujets suivants consultés par l'utilisateur:
    {topics_str}
    
    Suggérez {count} nouveau(x) sujet(s) qui pourrai(en)t l'intéresser. 
    Pour chaque sujet, donnez simplement le titre du sujet, sans explication.
    
    Assurez-vous que les sujets sont:
    1. Liés aux intérêts exprimés, mais suffisamment différents pour élargir les horizons
    2. Spécifiques et concrets plutôt que vagues
    3. Intrigants et susceptibles de susciter la curiosité
    
    Formatez chaque sujet comme un élément de liste avec un tiret.
    """