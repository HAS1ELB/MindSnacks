from typing import Dict, List, Any
import random

def get_topic_categories(language: str = 'en') -> Dict[str, List[str]]:
    """
    Get topic categories with examples
    
    Args:
        language (str): Language code
        
    Returns:
        dict: Dictionary of categories and topics
    """
    categories = {
        'en': {
            "Science": [
                "Quantum Computing Basics",
                "Climate Change Causes and Effects",
                "The Human Microbiome",
                "Astronomy: Exoplanets and Alien Life",
                "Neuroscience and Memory Formation",
                "CRISPR Gene Editing Technology",
                "Theories of Biological Evolution",
                "The Physics of Black Holes",
                "Renewable Energy Solutions",
                "Marine Biology and Ocean Conservation"
            ],
            "History": [
                "Ancient Egyptian Civilization",
                "The Renaissance Period",
                "World War II Major Turning Points",
                "The Rise and Fall of the Roman Empire",
                "Industrial Revolution and Its Impact",
                "History of Human Rights Movements",
                "Ancient Chinese Dynasties",
                "The Cold War Era",
                "Indigenous Peoples' Histories",
                "The Space Race"
            ],
            "Technology": [
                "Artificial Intelligence Ethics",
                "Blockchain Beyond Cryptocurrency",
                "Internet of Things Applications",
                "5G Technology and Its Impact",
                "Virtual and Augmented Reality",
                "Cybersecurity Fundamentals",
                "Machine Learning Algorithms",
                "Cloud Computing Architecture",
                "Robotics and Automation",
                "Digital Privacy in the Modern Age"
            ],
            "Arts & Culture": [
                "Contemporary Art Movements",
                "Classical Music Appreciation",
                "Film Theory and Analysis",
                "World Literature Masterpieces",
                "Architecture Through the Ages",
                "Indigenous Art Forms",
                "The History of Photography",
                "Dance Styles Around the World",
                "Theater and Dramatic Arts",
                "Fashion as Cultural Expression"
            ],
            "Health & Wellness": [
                "Nutrition Science Fundamentals",
                "Mindfulness and Meditation",
                "Exercise Physiology",
                "Sleep Science and Optimization",
                "Mental Health Awareness",
                "Preventive Healthcare Practices",
                "Alternative Medicine Approaches",
                "The Science of Aging",
                "Stress Management Techniques",
                "Immune System Function"
            ],
            "Environment & Sustainability": [
                "Sustainable Urban Planning",
                "Biodiversity Conservation",
                "Circular Economy Models",
                "Water Resource Management",
                "Sustainable Agriculture Practices",
                "Plastic Pollution Solutions",
                "Climate Resilience Strategies",
                "Renewable Energy Transitions",
                "Forest Ecosystem Services",
                "Carbon Footprint Reduction"
            ],
            "Psychology & Behavior": [
                "Cognitive Biases and Decision Making",
                "The Psychology of Happiness",
                "Child Development Stages",
                "Behavioral Economics",
                "Social Psychology Experiments",
                "Personality Theories",
                "The Science of Habit Formation",
                "Emotional Intelligence",
                "Cross-Cultural Psychology",
                "The Neuroscience of Addiction"
            ],
            "Business & Economics": [
                "Fundamentals of Investing",
                "Entrepreneurship Basics",
                "Global Economic Systems",
                "Marketing Psychology",
                "Sustainable Business Models",
                "Principles of Management",
                "Financial Literacy Essentials",
                "Economic Inequality Causes",
                "Digital Economy Transformations",
                "Supply Chain Management"
            ],
            "Philosophy & Ethics": [
                "Introduction to Moral Philosophy",
                "Eastern Philosophical Traditions",
                "Ethics in the Digital Age",
                "Existentialism and Meaning",
                "Philosophy of Mind",
                "Political Philosophy",
                "The Ethics of Artificial Intelligence",
                "Ancient Greek Philosophers",
                "Free Will and Determinism",
                "Contemporary Ethical Dilemmas"
            ],
            "Language & Communication": [
                "The Evolution of Human Language",
                "Effective Public Speaking",
                "Nonverbal Communication",
                "Language Learning Strategies",
                "Writing and Storytelling Techniques",
                "Digital Communication Skills",
                "Linguistic Diversity",
                "The Art of Negotiation",
                "Intercultural Communication",
                "Media Literacy"
            ]
        },
        'fr': {
            "Science": [
                "Bases de l'informatique quantique",
                "Causes et effets du changement climatique",
                "Le microbiome humain",
                "Astronomie : Exoplanètes et vie extraterrestre",
                "Neurosciences et formation de la mémoire",
                "Technologie d'édition génétique CRISPR",
                "Théories de l'évolution biologique",
                "La physique des trous noirs",
                "Solutions d'énergie renouvelable",
                "Biologie marine et conservation des océans"
            ],
            "Histoire": [
                "La civilisation de l'Égypte ancienne",
                "La période de la Renaissance",
                "Les tournants majeurs de la Seconde Guerre mondiale",
                "L'ascension et la chute de l'Empire romain",
                "La Révolution industrielle et son impact",
                "Histoire des mouvements des droits humains",
                "Les dynasties chinoises anciennes",
                "L'ère de la Guerre froide",
                "Histoires des peuples autochtones",
                "La course à l'espace"
            ],
            "Technologie": [
                "Éthique de l'intelligence artificielle",
                "La blockchain au-delà de la cryptomonnaie",
                "Applications de l'Internet des objets",
                "La technologie 5G et son impact",
                "Réalité virtuelle et augmentée",
                "Fondamentaux de la cybersécurité",
                "Algorithmes d'apprentissage automatique",
                "Architecture de l'informatique en nuage",
                "Robotique et automatisation",
                "La vie privée numérique à l'ère moderne"
            ],
            "Arts et Culture": [
                "Mouvements d'art contemporain",
                "Appréciation de la musique classique",
                "Théorie et analyse cinématographique",
                "Chefs-d'œuvre de la littérature mondiale",
                "L'architecture à travers les âges",
                "Formes d'art autochtones",
                "L'histoire de la photographie",
                "Styles de danse à travers le monde",
                "Théâtre et arts dramatiques",
                "La mode comme expression culturelle"
            ],
            "Santé et Bien-être": [
                "Fondamentaux de la science de la nutrition",
                "Pleine conscience et méditation",
                "Physiologie de l'exercice",
                "Science du sommeil et optimisation",
                "Sensibilisation à la santé mentale",
                "Pratiques de soins préventifs",
                "Approches de médecine alternative",
                "La science du vieillissement",
                "Techniques de gestion du stress",
                "Fonction du système immunitaire"
            ]
        },
        'es': {
            "Ciencia": [
                "Fundamentos de la computación cuántica",
                "Causas y efectos del cambio climático",
                "El microbioma humano",
                "Astronomía: Exoplanetas y vida alienígena",
                "Neurociencia y formación de la memoria",
                "Tecnología de edición genética CRISPR",
                "Teorías de la evolución biológica",
                "La física de los agujeros negros",
                "Soluciones de energía renovable",
                "Biología marina y conservación oceánica"
            ],
            "Historia": [
                "La civilización del antiguo Egipto",
                "El período del Renacimiento",
                "Puntos de inflexión de la Segunda Guerra Mundial",
                "El auge y caída del Imperio Romano",
                "La Revolución Industrial y su impacto",
                "Historia de los movimientos de derechos humanos",
                "Dinastías chinas antiguas",
                "La era de la Guerra Fría",
                "Historias de los pueblos indígenas",
                "La carrera espacial"
            ],
            "Tecnología": [
                "Ética de la inteligencia artificial",
                "Blockchain más allá de las criptomonedas",
                "Aplicaciones del Internet de las cosas",
                "Tecnología 5G y su impacto",
                "Realidad virtual y aumentada",
                "Fundamentos de ciberseguridad",
                "Algoritmos de aprendizaje automático",
                "Arquitectura de computación en la nube",
                "Robótica y automatización",
                "Privacidad digital en la era moderna"
            ]
        }
    }
    
    # Default to English if language not available
    return categories.get(language, categories['en'])

def get_trending_topics(language: str = 'en') -> List[str]:
    """
    Get trending topics
    
    Args:
        language (str): Language code
        
    Returns:
        list: List of trending topics
    """
    topics = {
        'en': [
            "Artificial Intelligence and Ethics",
            "Climate Change Solutions",
            "Mental Health Awareness",
            "Sustainable Living Practices",
            "Quantum Computing Applications",
            "Remote Work Productivity",
            "Blockchain and Digital Currency",
            "Space Exploration Advancements",
            "Immunology and Vaccines",
            "Financial Independence Strategies",
            "Renewable Energy Technologies",
            "Digital Privacy Protection",
            "Mindfulness and Meditation",
            "Sustainable Agriculture",
            "Electric Vehicle Revolution"
        ],
        'fr': [
            "Intelligence artificielle et éthique",
            "Solutions au changement climatique",
            "Sensibilisation à la santé mentale",
            "Pratiques de vie durable",
            "Applications de l'informatique quantique",
            "Productivité du travail à distance",
            "Blockchain et monnaie numérique",
            "Avancées en exploration spatiale",
            "Immunologie et vaccins",
            "Stratégies d'indépendance financière",
            "Technologies d'énergie renouvelable",
            "Protection de la vie privée numérique",
            "Pleine conscience et méditation",
            "Agriculture durable",
            "Révolution des véhicules électriques"
        ],
        'es': [
            "Inteligencia artificial y ética",
            "Soluciones al cambio climático",
            "Conciencia sobre salud mental",
            "Prácticas de vida sostenible",
            "Aplicaciones de la computación cuántica",
            "Productividad del trabajo remoto",
            "Blockchain y moneda digital",
            "Avances en exploración espacial",
            "Inmunología y vacunas",
            "Estrategias de independencia financiera",
            "Tecnologías de energía renovable",
            "Protección de la privacidad digital",
            "Mindfulness y meditación",
            "Agricultura sostenible",
            "Revolución de los vehículos eléctricos"
        ]
    }
    
    # Default to English if language not available
    topic_list = topics.get(language, topics['en'])
    
    # Randomize the order for variety
    random.shuffle(topic_list)
    
    return topic_list

def get_curated_playlists(language: str = 'en') -> Dict[str, List[str]]:
    """
    Get curated playlists
    
    Args:
        language (str): Language code
        
    Returns:
        dict: Dictionary of playlist names and topics
    """
    playlists = {
        'en': {
            "Future Technologies": [
                "Quantum Computing Basics",
                "Neural Interfaces and Brain-Computer Connections",
                "Synthetic Biology Applications",
                "Advanced Robotics and Automation",
                "Space Colonization Challenges"
            ],
            "Personal Development Essentials": [
                "The Science of Habit Formation",
                "Effective Time Management Strategies",
                "Emotional Intelligence Development",
                "Critical Thinking Skills",
                "Strategies for Lifelong Learning"
            ],
            "Understanding Our World": [
                "Climate Science Fundamentals",
                "Global Economic Systems Explained",
                "Cultural Anthropology Basics",
                "Modern Geopolitics Overview",
                "Biodiversity and Conservation"
            ],
            "Health and Longevity": [
                "Nutrition Science Fundamentals",
                "The Science of Healthy Aging",
                "Exercise Physiology Basics",
                "Sleep Science and Optimization",
                "Stress Management Techniques"
            ],
            "Art and Creativity": [
                "The Psychology of Creativity",
                "Modern Art Movements",
                "Music Theory Fundamentals",
                "Creative Writing Techniques",
                "Digital Art and Design Basics"
            ]
        },
        'fr': {
            "Technologies du Futur": [
                "Bases de l'informatique quantique",
                "Interfaces neurales et connexions cerveau-ordinateur",
                "Applications de la biologie synthétique",
                "Robotique avancée et automatisation",
                "Défis de la colonisation spatiale"
            ],
            "Essentiels du Développement Personnel": [
                "La science de la formation des habitudes",
                "Stratégies efficaces de gestion du temps",
                "Développement de l'intelligence émotionnelle",
                "Compétences en pensée critique",
                "Stratégies pour l'apprentissage tout au long de la vie"
            ],
            "Comprendre Notre Monde": [
                "Fondamentaux de la science du climat",
                "Systèmes économiques mondiaux expliqués",
                "Bases de l'anthropologie culturelle",
                "Aperçu de la géopolitique moderne",
                "Biodiversité et conservation"
            ],
            "Santé et Longévité": [
                "Fondamentaux de la science de la nutrition",
                "La science du vieillissement en bonne santé",
                "Bases de la physiologie de l'exercice",
                "Science du sommeil et optimisation",
                "Techniques de gestion du stress"
            ],
            "Art et Créativité": [
                "La psychologie de la créativité",
                "Mouvements d'art moderne",
                "Fondamentaux de la théorie musicale",
                "Techniques d'écriture créative",
                "Bases de l'art numérique et du design"
            ]
        },
        'es': {
            "Tecnologías del Futuro": [
                "Fundamentos de la computación cuántica",
                "Interfaces neurales y conexiones cerebro-computadora",
                "Aplicaciones de biología sintética",
                "Robótica avanzada y automatización",
                "Desafíos de la colonización espacial"
            ],
            "Esenciales del Desarrollo Personal": [
                "La ciencia de la formación de hábitos",
                "Estrategias efectivas de gestión del tiempo",
                "Desarrollo de la inteligencia emocional",
                "Habilidades de pensamiento crítico",
                "Estrategias para el aprendizaje permanente"
            ],
            "Entendiendo Nuestro Mundo": [
                "Fundamentos de la ciencia climática",
                "Sistemas económicos globales explicados",
                "Fundamentos de antropología cultural",
                "Panorama de la geopolítica moderna",
                "Biodiversidad y conservación"
            ]
        }
    }
    
    # Default to English if language not available
    return playlists.get(language, playlists['en'])