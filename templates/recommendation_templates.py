def get_trending_topics(language='fr'):
    """
    Renvoie une liste de sujets tendance pour les utilisateurs sans historique.
    Adapté pour supporter plusieurs langues.
    """
    topics = {
        'fr': [
            "L'impact de l'IA sur le marché du travail",
            "Les découvertes récentes sur Mars",
            "Comment fonctionne la blockchain",
            "L'histoire des pandémies à travers les siècles",
            "Le cerveau et l'apprentissage",
            "Les océans et le changement climatique",
            "La psychologie des habitudes",
            "Les plus grandes découvertes scientifiques de la dernière décennie"
        ],
        'en': [
            "The impact of AI on the job market",
            "Recent discoveries on Mars",
            "How blockchain works",
            "The history of pandemics through the centuries",
            "The brain and learning",
            "Oceans and climate change",
            "Psychology of habits",
            "The greatest scientific discoveries of the last decade"
        ],
        'es': [
            "El impacto de la IA en el mercado laboral",
            "Descubrimientos recientes en Marte",
            "Cómo funciona la blockchain",
            "La historia de las pandemias a través de los siglos",
            "El cerebro y el aprendizaje",
            "Los océanos y el cambio climático",
            "La psicología de los hábitos",
            "Los mayores descubrimientos científicos de la última década"
        ],
        'de': [
            "Die Auswirkungen der KI auf den Arbeitsmarkt",
            "Neueste Entdeckungen auf dem Mars",
            "Wie Blockchain funktioniert",
            "Die Geschichte der Pandemien durch die Jahrhunderte",
            "Das Gehirn und das Lernen",
            "Ozeane und Klimawandel",
            "Psychologie der Gewohnheiten",
            "Die größten wissenschaftlichen Entdeckungen des letzten Jahrzehnts"
        ],
        'it': [
            "L'impatto dell'IA sul mercato del lavoro",
            "Scoperte recenti su Marte",
            "Come funziona la blockchain",
            "La storia delle pandemie attraverso i secoli",
            "Il cervello e l'apprendimento",
            "Gli oceani e il cambiamento climatico",
            "La psicologia delle abitudini",
            "Le più grandi scoperte scientifiche dell'ultimo decennio"
        ],
        'ja': [
            "AI（人工知能）の労働市場への影響",
            "火星での最近の発見",
            "ブロックチェーンの仕組み",
            "世紀を通じたパンデミックの歴史",
            "脳と学習",
            "海洋と気候変動",
            "習慣の心理学",
            "過去10年間の最も偉大な科学的発見"
        ],
        'zh': [
            "人工智能对就业市场的影响",
            "火星上的最新发现",
            "区块链是如何运作的",
            "几个世纪以来的流行病历史",
            "大脑与学习",
            "海洋与气候变化",
            "习惯心理学",
            "过去十年最重大的科学发现"
        ],
        'ar': [
            "تأثير الذكاء الاصطناعي على سوق العمل",
            "الاكتشافات الأخيرة على المريخ",
            "كيفية عمل تقنية البلوكتشين",
            "تاريخ الأوبئة عبر القرون",
            "الدماغ والتعلم",
            "المحيطات وتغير المناخ",
            "علم نفس العادات",
            "أعظم الاكتشافات العلمية في العقد الأخير"
        ]
    }
    
    return topics.get(language, topics['en'])

def get_topic_categories(language='fr'):
    """
    Renvoie des catégories de sujets pour aider les utilisateurs à choisir.
    Adapté pour supporter plusieurs langues.
    """
    categories = {
        'fr': {
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
        },
        'en': {
            "Science": [
                "Black holes and quantum gravity",
                "CRISPR and genetic modification",
                "Neuroscience and consciousness"
            ],
            "History": [
                "The fall of the Roman Empire",
                "The Silk Road",
                "The Islamic Golden Age"
            ],
            "Technology": [
                "The evolution of artificial intelligence",
                "Quantum computing explained",
                "The future of the Internet"
            ],
            "Arts & Culture": [
                "The history of jazz",
                "Expressionism in art",
                "The evolution of cinema"
            ],
            "Health & Wellness": [
                "The science of sleep",
                "Nutrition and longevity",
                "Meditation and the brain"
            ]
        },
        'es': {
            "Ciencia": [
                "Agujeros negros y gravedad cuántica",
                "CRISPR y modificación genética",
                "Neurociencia y conciencia"
            ],
            "Historia": [
                "La caída del Imperio Romano",
                "La Ruta de la Seda",
                "La Edad de Oro islámica"
            ],
            "Tecnología": [
                "La evolución de la inteligencia artificial",
                "Computación cuántica explicada",
                "El futuro de Internet"
            ],
            "Arte y Cultura": [
                "La historia del jazz",
                "El expresionismo en el arte",
                "La evolución del cine"
            ],
            "Salud y Bienestar": [
                "La ciencia del sueño",
                "Alimentación y longevidad",
                "Meditación y cerebro"
            ]
        },
        'de': {
            "Wissenschaft": [
                "Schwarze Löcher und Quantengravitation",
                "CRISPR und genetische Modifikation",
                "Neurowissenschaft und Bewusstsein"
            ],
            "Geschichte": [
                "Der Fall des Römischen Reiches",
                "Die Seidenstraße",
                "Das Islamische Goldene Zeitalter"
            ],
            "Technologie": [
                "Die Evolution der künstlichen Intelligenz",
                "Quantencomputer erklärt",
                "Die Zukunft des Internets"
            ],
            "Kunst & Kultur": [
                "Die Geschichte des Jazz",
                "Expressionismus in der Kunst",
                "Die Evolution des Kinos"
            ],
            "Gesundheit & Wohlbefinden": [
                "Die Wissenschaft des Schlafs",
                "Ernährung und Langlebigkeit",
                "Meditation und das Gehirn"
            ]
        },
        'it': {
            "Scienza": [
                "Buchi neri e gravità quantistica",
                "CRISPR e modificazione genetica",
                "Neuroscienze e coscienza"
            ],
            "Storia": [
                "La caduta dell'Impero Romano",
                "La Via della Seta",
                "L'Età d'Oro islamica"
            ],
            "Tecnologia": [
                "L'evoluzione dell'intelligenza artificiale",
                "Il computing quantistico spiegato",
                "Il futuro di Internet"
            ],
            "Arte e Cultura": [
                "La storia del jazz",
                "L'espressionismo nell'arte",
                "L'evoluzione del cinema"
            ],
            "Salute e Benessere": [
                "La scienza del sonno",
                "Alimentazione e longevità",
                "Meditazione e cervello"
            ]
        },
        'ja': {
            "科学": [
                "ブラックホールと量子重力",
                "CRISPRと遺伝子改変",
                "神経科学と意識"
            ],
            "歴史": [
                "ローマ帝国の崩壊",
                "シルクロード",
                "イスラムの黄金時代"
            ],
            "テクノロジー": [
                "人工知能の進化",
                "量子コンピューティングの解説",
                "インターネットの未来"
            ],
            "芸術と文化": [
                "ジャズの歴史",
                "芸術における表現主義",
                "映画の進化"
            ],
            "健康とウェルネス": [
                "睡眠の科学",
                "栄養と長寿",
                "瞑想と脳"
            ]
        },
        'zh': {
            "科学": [
                "黑洞和量子引力",
                "CRISPR和基因修改",
                "神经科学与意识"
            ],
            "历史": [
                "罗马帝国的衰落",
                "丝绸之路",
                "伊斯兰黄金时代"
            ],
            "技术": [
                "人工智能的演变",
                "量子计算解析",
                "互联网的未来"
            ],
            "艺术与文化": [
                "爵士乐的历史",
                "艺术中的表现主义",
                "电影的演变"
            ],
            "健康与福祉": [
                "睡眠科学",
                "营养与长寿",
                "冥想与大脑"
            ]
        },
        'ar': {
            "العلوم": [
                "الثقوب السوداء والجاذبية الكمومية",
                "CRISPR وتعديل الجينات",
                "علم الأعصاب والوعي"
            ],
            "التاريخ": [
                "سقوط الإمبراطورية الرومانية",
                "طريق الحرير",
                "العصر الذهبي الإسلامي"
            ],
            "التكنولوجيا": [
                "تطور الذكاء الاصطناعي",
                "شرح الحوسبة الكمومية",
                "مستقبل الإنترنت"
            ],
            "الفنون والثقافة": [
                "تاريخ الجاز",
                "التعبيرية في الفن",
                "تطور السينما"
            ],
            "الصحة والرفاهية": [
                "علم النوم",
                "التغذية وطول العمر",
                "التأمل والدماغ"
            ]
        }
    }
    
    return categories.get(language, categories['en'])