from typing import Dict, List, Any

def get_learning_paths(language: str = 'en') -> Dict[str, Dict[str, Any]]:
    """
    Get defined learning paths with structured progression
    
    Args:
        language (str): Language code
        
    Returns:
        dict: Dictionary of learning paths with metadata
    """
    paths = {
        'en': {
            "Data Science Fundamentals": {
                "description": "Begin your journey into the world of data science with this structured learning path covering statistics, programming, visualization, machine learning, and practical applications.",
                "difficulty": "beginner-intermediate",
                "estimated_time": "10-15 hours",
                "stages": [
                    {
                        "name": "Statistics Fundamentals",
                        "topics": [
                            "Introduction to Statistics",
                            "Probability Theory Basics",
                            "Statistical Distributions",
                            "Hypothesis Testing",
                            "Correlation and Regression"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Programming Skills",
                        "topics": [
                            "Basics of Python Programming",
                            "Data Manipulation with Pandas",
                            "NumPy for Numerical Computing",
                            "Data Structures for Data Science",
                            "Writing Efficient Code"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Data Visualization",
                        "topics": [
                            "Data Visualization Principles",
                            "Matplotlib for Python Plotting",
                            "Interactive Visualizations with Plotly",
                            "Dashboard Creation",
                            "Telling Stories with Data"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Machine Learning Basics",
                        "topics": [
                            "Introduction to Machine Learning",
                            "Supervised Learning Algorithms",
                            "Unsupervised Learning Techniques",
                            "Model Evaluation Methods",
                            "Feature Engineering"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Practical Applications",
                        "topics": [
                            "Real-world Data Science Projects",
                            "Data Cleaning Techniques",
                            "Building a Data Science Portfolio",
                            "Ethics in Data Science",
                            "Next Steps in Your Data Science Journey"
                        ],
                        "quiz": False,
                        "project": True
                    }
                ]
            },
            "Web Development Journey": {
                "description": "Learn to build modern, responsive websites from scratch with this comprehensive path covering HTML, CSS, JavaScript, and popular frameworks.",
                "difficulty": "beginner",
                "estimated_time": "12-18 hours",
                "stages": [
                    {
                        "name": "HTML Foundations",
                        "topics": [
                            "HTML and CSS Basics",
                            "HTML Document Structure",
                            "Text Formatting and Lists",
                            "HTML Forms and Inputs",
                            "Semantic HTML Elements"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "CSS Styling",
                        "topics": [
                            "CSS Selectors and Properties",
                            "Box Model and Layout",
                            "Responsive Web Design",
                            "Flexbox and Grid Systems",
                            "CSS Animations and Effects"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "JavaScript Essentials",
                        "topics": [
                            "JavaScript Fundamentals",
                            "DOM Manipulation",
                            "Event Handling",
                            "Asynchronous JavaScript",
                            "Working with APIs"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Frontend Frameworks",
                        "topics": [
                            "Introduction to React",
                            "Component-based Architecture",
                            "State Management",
                            "Routing in Single Page Applications",
                            "React Hooks and Context API"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Backend Basics",
                        "topics": [
                            "Backend Basics with Node.js",
                            "Express.js Framework",
                            "RESTful API Design",
                            "Database Integration",
                            "Deployment and Hosting"
                        ],
                        "quiz": False,
                        "project": True
                    }
                ]
            },
            "Financial Literacy": {
                "description": "Develop essential financial knowledge and skills to manage your money, build wealth, and secure your financial future with this practical learning path.",
                "difficulty": "beginner",
                "estimated_time": "8-10 hours",
                "stages": [
                    {
                        "name": "Personal Finance Basics",
                        "topics": [
                            "Understanding Personal Finance",
                            "Building a Budget That Works",
                            "Managing Debt Effectively",
                            "Banking and Financial Services",
                            "Understanding Credit Scores"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Saving and Investing",
                        "topics": [
                            "Introduction to Investing",
                            "Types of Investment Vehicles",
                            "Risk and Return Principles",
                            "Retirement Planning Basics",
                            "Asset Allocation Strategies"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Financial Planning",
                        "topics": [
                            "Setting Financial Goals",
                            "Emergency Funds and Insurance",
                            "Tax Planning Fundamentals",
                            "Major Purchase Planning",
                            "Estate Planning Essentials"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Advanced Topics",
                        "topics": [
                            "Real Estate Investing",
                            "Advanced Investment Strategies",
                            "Behavioral Finance",
                            "Wealth Building Principles",
                            "Financial Independence Strategies"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Practical Application",
                        "topics": [
                            "Creating Your Financial Plan",
                            "Financial Tools and Resources",
                            "Navigating Financial Challenges",
                            "Money and Relationships",
                            "Maintaining Financial Health"
                        ],
                        "quiz": False,
                        "project": True
                    }
                ]
            },
            "Sustainable Living": {
                "description": "Learn practical ways to reduce your environmental impact, make sustainable choices, and contribute to a healthier planet through everyday decisions.",
                "difficulty": "beginner",
                "estimated_time": "6-8 hours",
                "stages": [
                    {
                        "name": "Sustainability Basics",
                        "topics": [
                            "Introduction to Sustainability",
                            "Environmental Challenges Today",
                            "Carbon Footprint Awareness",
                            "Sustainability Metrics",
                            "Individual vs. Systemic Change"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Sustainable Home",
                        "topics": [
                            "Reducing Household Waste",
                            "Energy Conservation at Home",
                            "Water Conservation Techniques",
                            "Sustainable Cleaning",
                            "Zero-Waste Principles"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Sustainable Food",
                        "topics": [
                            "Sustainable Food Choices",
                            "Understanding Food Miles",
                            "Reducing Food Waste",
                            "Plant-based Cooking Basics",
                            "Growing Your Own Food"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Sustainable Lifestyle",
                        "topics": [
                            "Ethical Consumption Practices",
                            "Sustainable Transportation",
                            "Minimalism and Decluttering",
                            "Sustainable Fashion",
                            "Eco-friendly Travel"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Community Impact",
                        "topics": [
                            "Community Sustainability Initiatives",
                            "Environmental Advocacy",
                            "Teaching Others About Sustainability",
                            "Joining the Circular Economy",
                            "Creating Your Sustainability Action Plan"
                        ],
                        "quiz": False,
                        "project": True
                    }
                ]
            }
        },
        'fr': {
            "Fondamentaux de la Science des Données": {
                "description": "Commencez votre voyage dans le monde de la science des données avec ce parcours d'apprentissage structuré couvrant les statistiques, la programmation, la visualisation, l'apprentissage automatique et les applications pratiques.",
                "difficulty": "débutant-intermédiaire",
                "estimated_time": "10-15 heures",
                "stages": [
                    {
                        "name": "Fondamentaux des Statistiques",
                        "topics": [
                            "Introduction aux Statistiques",
                            "Bases de la Théorie des Probabilités",
                            "Distributions Statistiques",
                            "Tests d'Hypothèse",
                            "Corrélation et Régression"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Compétences en Programmation",
                        "topics": [
                            "Bases de la Programmation Python",
                            "Manipulation de Données avec Pandas",
                            "NumPy pour le Calcul Numérique",
                            "Structures de Données pour la Science des Données",
                            "Écriture de Code Efficace"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Visualisation de Données",
                        "topics": [
                            "Principes de Visualisation de Données",
                            "Matplotlib pour la Représentation Graphique en Python",
                            "Visualisations Interactives avec Plotly",
                            "Création de Tableaux de Bord",
                            "Raconter des Histoires avec les Données"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Bases de l'Apprentissage Automatique",
                        "topics": [
                            "Introduction à l'Apprentissage Automatique",
                            "Algorithmes d'Apprentissage Supervisé",
                            "Techniques d'Apprentissage Non Supervisé",
                            "Méthodes d'Évaluation de Modèles",
                            "Ingénierie des Caractéristiques"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Applications Pratiques",
                        "topics": [
                            "Projets Réels de Science des Données",
                            "Techniques de Nettoyage de Données",
                            "Construction d'un Portfolio de Science des Données",
                            "Éthique en Science des Données",
                            "Prochaines Étapes dans Votre Parcours en Science des Données"
                        ],
                        "quiz": False,
                        "project": True
                    }
                ]
            },
            "Parcours de Développement Web": {
                "description": "Apprenez à construire des sites web modernes et responsifs à partir de zéro avec ce parcours complet couvrant HTML, CSS, JavaScript et les frameworks populaires.",
                "difficulty": "débutant",
                "estimated_time": "12-18 heures",
                "stages": [
                    {
                        "name": "Fondements HTML",
                        "topics": [
                            "Bases HTML et CSS",
                            "Structure de Document HTML",
                            "Formatage de Texte et Listes",
                            "Formulaires et Entrées HTML",
                            "Éléments HTML Sémantiques"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Stylisation CSS",
                        "topics": [
                            "Sélecteurs et Propriétés CSS",
                            "Modèle de Boîte et Mise en Page",
                            "Conception Web Responsive",
                            "Systèmes Flexbox et Grid",
                            "Animations et Effets CSS"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Essentiels JavaScript",
                        "topics": [
                            "Fondamentaux JavaScript",
                            "Manipulation du DOM",
                            "Gestion des Événements",
                            "JavaScript Asynchrone",
                            "Travailler avec des API"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Frameworks Frontend",
                        "topics": [
                            "Introduction à React",
                            "Architecture Basée sur les Composants",
                            "Gestion d'État",
                            "Routage dans les Applications à Page Unique",
                            "Hooks React et API Context"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Bases du Backend",
                        "topics": [
                            "Bases du Backend avec Node.js",
                            "Framework Express.js",
                            "Conception d'API RESTful",
                            "Intégration de Base de Données",
                            "Déploiement et Hébergement"
                        ],
                        "quiz": False,
                        "project": True
                    }
                ]
            }
        },
        'es': {
            "Fundamentos de Ciencia de Datos": {
                "description": "Comienza tu viaje en el mundo de la ciencia de datos con esta ruta de aprendizaje estructurada que cubre estadísticas, programación, visualización, aprendizaje automático y aplicaciones prácticas.",
                "difficulty": "principiante-intermedio",
                "estimated_time": "10-15 horas",
                "stages": [
                    {
                        "name": "Fundamentos de Estadística",
                        "topics": [
                            "Introducción a la Estadística",
                            "Fundamentos de Teoría de Probabilidad",
                            "Distribuciones Estadísticas",
                            "Pruebas de Hipótesis",
                            "Correlación y Regresión"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Habilidades de Programación",
                        "topics": [
                            "Fundamentos de Programación Python",
                            "Manipulación de Datos con Pandas",
                            "NumPy para Cálculo Numérico",
                            "Estructuras de Datos para Ciencia de Datos",
                            "Escribiendo Código Eficiente"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Visualización de Datos",
                        "topics": [
                            "Principios de Visualización de Datos",
                            "Matplotlib para Gráficas en Python",
                            "Visualizaciones Interactivas con Plotly",
                            "Creación de Dashboards",
                            "Contando Historias con Datos"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Fundamentos de Machine Learning",
                        "topics": [
                            "Introducción al Machine Learning",
                            "Algoritmos de Aprendizaje Supervisado",
                            "Técnicas de Aprendizaje No Supervisado",
                            "Métodos de Evaluación de Modelos",
                            "Ingeniería de Características"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Aplicaciones Prácticas",
                        "topics": [
                            "Proyectos de Ciencia de Datos del Mundo Real",
                            "Técnicas de Limpieza de Datos",
                            "Creando un Portafolio de Ciencia de Datos",
                            "Ética en Ciencia de Datos",
                            "Próximos Pasos en tu Viaje de Ciencia de Datos"
                        ],
                        "quiz": False,
                        "project": True
                    }
                ]
            },
            "Viaje de Desarrollo Web": {
                "description": "Aprende a construir sitios web modernos y responsivos desde cero con esta ruta completa que cubre HTML, CSS, JavaScript y frameworks populares.",
                "difficulty": "principiante",
                "estimated_time": "12-18 horas",
                "stages": [
                    {
                        "name": "Fundamentos de HTML",
                        "topics": [
                            "Fundamentos de HTML y CSS",
                            "Estructura de Documentos HTML",
                            "Formato de Texto y Listas",
                            "Formularios e Inputs HTML",
                            "Elementos HTML Semánticos"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Estilizado con CSS",
                        "topics": [
                            "Selectores y Propiedades CSS",
                            "Modelo de Caja y Layout",
                            "Diseño Web Responsivo",
                            "Sistemas Flexbox y Grid",
                            "Animaciones y Efectos CSS"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Esenciales de JavaScript",
                        "topics": [
                            "Fundamentos de JavaScript",
                            "Manipulación del DOM",
                            "Manejo de Eventos",
                            "JavaScript Asíncrono",
                            "Trabajando con APIs"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Frameworks Frontend",
                        "topics": [
                            "Introducción a React",
                            "Arquitectura Basada en Componentes",
                            "Gestión de Estado",
                            "Enrutamiento en Aplicaciones de Página Única",
                            "React Hooks y Context API"
                        ],
                        "quiz": True
                    },
                    {
                        "name": "Fundamentos de Backend",
                        "topics": [
                            "Fundamentos de Backend con Node.js",
                            "Framework Express.js",
                            "Diseño de APIs RESTful",
                            "Integración de Bases de Datos",
                            "Despliegue y Hosting"
                        ],
                        "quiz": False,
                        "project": True
                    }
                ]
            }
        }
    }
    
    # Default to English if language not available
    return paths.get(language, paths['en'])

def get_path_progress(path_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get user progress in a learning path
    
    Args:
        path_id (str): Learning path ID
        user_id (str): User ID
        
    Returns:
        dict: User progress in the path
    """
    # In a real implementation, this would retrieve progress from a database
    # For this demo, we'll return a mock progress object
    return {
        "path_id": path_id,
        "user_id": user_id,
        "completed_topics": [],
        "completed_stages": [],
        "completed_quizzes": [],
        "overall_progress": 0,
        "last_activity": None
    }

def get_next_topic(path_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get the next recommended topic in a learning path
    
    Args:
        path_id (str): Learning path ID
        user_id (str): User ID
        
    Returns:
        dict: Next topic information
    """
    # In a real implementation, this would determine the next logical topic
    # based on user progress
    progress = get_path_progress(path_id, user_id)
    
    # Get all learning paths
    all_paths = get_learning_paths()
    
    if path_id in all_paths:
        path = all_paths[path_id]
        
        # Find the first uncompleted stage
        for stage_index, stage in enumerate(path["stages"]):
            if f"stage_{stage_index}" not in progress["completed_stages"]:
                # Find the first uncompleted topic in this stage
                for topic_index, topic in enumerate(stage["topics"]):
                    topic_id = f"stage_{stage_index}_topic_{topic_index}"
                    if topic_id not in progress["completed_topics"]:
                        return {
                            "path_id": path_id,
                            "stage_index": stage_index,
                            "stage_name": stage["name"],
                            "topic_index": topic_index,
                            "topic": topic,
                            "has_quiz": stage.get("quiz", False)
                        }
    
    # If no next topic found or path doesn't exist
    return {
        "path_id": path_id,
        "stage_index": 0,
        "stage_name": "Getting Started",
        "topic_index": 0,
        "topic": "Introduction",
        "has_quiz": False
    }