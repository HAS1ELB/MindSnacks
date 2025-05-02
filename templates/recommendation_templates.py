def get_trending_topics():
    """
    Renvoie une liste de sujets tendance pour les utilisateurs sans historique.
    
    Returns:
        list: Liste des sujets tendance
    """
    return [
        "L'impact de l'IA sur le marché du travail",
        "Les découvertes récentes sur Mars",
        "Comment fonctionne la blockchain",
        "L'histoire des pandémies à travers les siècles",
        "Le cerveau et l'apprentissage",
        "Les océans et le changement climatique",
        "La psychologie des habitudes",
        "Les plus grandes découvertes scientifiques de la dernière décennie"
    ]

def get_topic_categories():
    """
    Renvoie des catégories de sujets pour aider les utilisateurs à choisir.
    
    Returns:
        dict: Dictionnaire des catégories et sujets associés
    """
    return {
        "Science": [
            "Trous noirs et gravité quantique",
            "CRISPR et modification génétique",
            "Neurosciences et conscience"
        ],
        "Histoire": [
            "La chute de l'Empire romain",
            "La route de la soie",
            "L'âge d'or islamique"
        ],
        "Technologie": [
            "L'évolution de l'intelligence artificielle",
            "Informatique quantique expliquée",
            "L'avenir de l'Internet"
        ],
        "Arts & Culture": [
            "L'histoire du jazz",
            "L'expressionnisme dans l'art",
            "L'évolution du cinéma"
        ],
        "Santé & Bien-être": [
            "La science du sommeil",
            "Alimentation et longévité",
            "Méditation et cerveau"
        ]
    }