from typing import List, Dict, Any, Optional
import random

def get_learning_prompt(topic: str, word_count: int, language: str = 'en') -> str:
    """
    Generate prompt for learning snippet generation
    
    Args:
        topic (str): The topic to generate content about
        word_count (int): Target word count
        language (str): Language code
        
    Returns:
        str: Generated prompt
    """
    prompts = {
        'en': f"""Create an engaging, educational snippet on "{topic}". 
        The content should be approximately {word_count} words long, conversational, and accessible to a general audience.
        Start with a brief introduction, followed by several interesting points or facts about the topic.
        Include some surprising or lesser-known information to maintain interest.
        Use a friendly, conversational tone as if explaining to a curious friend.
        Avoid jargon unless necessary, and explain any technical terms.
        Format the content with a clear title using a # heading, followed by coherent paragraphs.
        Conclude with a thought-provoking reflection or question.
        DO NOT include any metadata, citations, or instructions in the output.""",
        
        'fr': f"""Créez un extrait éducatif engageant sur "{topic}".
        Le contenu doit faire environ {word_count} mots, être conversationnel et accessible à un public général.
        Commencez par une brève introduction, suivie de plusieurs points ou faits intéressants sur le sujet.
        Incluez des informations surprenantes ou peu connues pour maintenir l'intérêt.
        Utilisez un ton amical et conversationnel comme si vous expliquiez à un ami curieux.
        Évitez le jargon sauf si nécessaire, et expliquez tous les termes techniques.
        Formatez le contenu avec un titre clair en utilisant un en-tête #, suivi de paragraphes cohérents.
        Concluez avec une réflexion ou une question qui fait réfléchir.
        N'incluez PAS de métadonnées, de citations ou d'instructions dans la sortie.""",
        
        'es': f"""Crea un fragmento educativo atractivo sobre "{topic}".
        El contenido debe tener aproximadamente {word_count} palabras, ser conversacional y accesible para una audiencia general.
        Comienza con una breve introducción, seguida de varios puntos o hechos interesantes sobre el tema.
        Incluye información sorprendente o menos conocida para mantener el interés.
        Usa un tono amigable y conversacional como si le explicaras a un amigo curioso.
        Evita la jerga a menos que sea necesario, y explica cualquier término técnico.
        Formatea el contenido con un título claro usando un encabezado #, seguido de párrafos coherentes.
        Concluye con una reflexión o pregunta que invite a la reflexión.
        NO incluyas metadatos, citas o instrucciones en la salida.""",
        
        'de': f"""Erstellen Sie einen ansprechenden, lehrreichen Schnipsel zum Thema "{topic}".
        Der Inhalt sollte ungefähr {word_count} Wörter lang, gesprächig und für ein allgemeines Publikum zugänglich sein.
        Beginnen Sie mit einer kurzen Einführung, gefolgt von mehreren interessanten Punkten oder Fakten zum Thema.
        Fügen Sie einige überraschende oder weniger bekannte Informationen hinzu, um das Interesse aufrechtzuerhalten.
        Verwenden Sie einen freundlichen, gesprächigen Ton, als ob Sie einem neugierigen Freund etwas erklären würden.
        Vermeiden Sie Fachjargon, es sei denn, es ist notwendig, und erklären Sie alle technischen Begriffe.
        Formatieren Sie den Inhalt mit einem klaren Titel unter Verwendung einer #-Überschrift, gefolgt von zusammenhängenden Absätzen.
        Schließen Sie mit einer zum Nachdenken anregenden Reflexion oder Frage ab.
        Fügen Sie KEINE Metadaten, Zitate oder Anweisungen in die Ausgabe ein.""",
        
        'it': f"""Crea uno snippet educativo coinvolgente su "{topic}".
        Il contenuto dovrebbe essere lungo circa {word_count} parole, colloquiale e accessibile a un pubblico generale.
        Inizia con una breve introduzione, seguita da diversi punti o fatti interessanti sull'argomento.
        Includi alcune informazioni sorprendenti o meno note per mantenere l'interesse.
        Usa un tono amichevole e colloquiale come se stessi spiegando a un amico curioso.
        Evita il gergo a meno che non sia necessario, e spiega qualsiasi termine tecnico.
        Formatta il contenuto con un titolo chiaro usando un'intestazione #, seguito da paragrafi coerenti.
        Concludi con una riflessione o una domanda stimolante.
        NON includere metadati, citazioni o istruzioni nell'output.""",
        
        'ja': f""""{topic}"についての魅力的で教育的なスニペットを作成してください。
        コンテンツは約{word_count}単語の長さで、会話的で一般の視聴者にアクセスしやすいものでなければなりません。
        簡単な紹介から始めて、トピックに関するいくつかの興味深いポイントや事実を続けてください。
        興味を維持するために、いくつかの驚くべきまたはあまり知られていない情報を含めてください。
        好奇心旺盛な友人に説明するように、フレンドリーで会話的な口調を使用してください。
        専門用語は必要でない限り避け、専門用語を説明してください。
        #見出しを使用した明確なタイトルで内容をフォーマットし、それに続いて一貫性のある段落を付けてください。
        思考を促す反省や質問で締めくくります。
        出力にメタデータ、引用、または指示を含めないでください。""",
        
        'zh': f"""创建一个关于"{topic}"的引人入胜的教育片段。
        内容应该大约有{word_count}个字，对话式的，容易被一般观众理解。
        从简短的介绍开始，然后是关于这个主题的几个有趣的点或事实。
        包括一些令人惊讶或鲜为人知的信息，以保持兴趣。
        使用友好的、对话的语气，就像在向好奇的朋友解释一样。
        除非必要，否则避免使用行话，并解释任何技术术语。
        使用#标题格式化内容，标题清晰，然后是连贯的段落。
        以发人深省的反思或问题结束。
        不要在输出中包含任何元数据、引用或说明。""",
        
        'ar': f"""قم بإنشاء مقتطف تعليمي جذاب حول "{topic}".
        يجب أن يكون المحتوى بطول {word_count} كلمة تقريبًا، وبأسلوب محادثة، ومتاح للجمهور العام.
        ابدأ بمقدمة موجزة، متبوعة بعدة نقاط أو حقائق مثيرة للاهتمام حول الموضوع.
        قم بتضمين بعض المعلومات المفاجئة أو الأقل شهرة للحفاظ على الاهتمام.
        استخدم لهجة ودية ومحادثة كما لو كنت تشرح لصديق فضولي.
        تجنب المصطلحات التقنية إلا إذا كان ذلك ضروريًا، واشرح أي مصطلحات فنية.
        قم بتنسيق المحتوى بعنوان واضح باستخدام عنوان #، متبوعًا بفقرات متماسكة.
        اختتم بتأمل أو سؤال يحث على التفكير.
        لا تضمن أي بيانات وصفية أو اقتباسات أو تعليمات في الإخراج."""
    }
    
    # Default to English if language not available
    return prompts.get(language, prompts['en'])

def get_recommendation_prompt(previous_topics: List[str], count: int, language: str = 'en') -> str:
    """
    Generate prompt for topic recommendations
    
    Args:
        previous_topics (list): List of topics the user has previously viewed
        count (int): Number of recommendations to generate
        language (str): Language code
        
    Returns:
        str: Generated prompt
    """
    topics_str = ", ".join(previous_topics[:5])  # Limit to first 5 topics
    
    prompts = {
        'en': f"""Based on the following topics that a user has shown interest in:
        {topics_str}
        
        Please recommend exactly {count} new and interesting topics that the user might want to learn about next.
        The recommendations should be related to the user's interests but introduce new concepts or areas.
        Provide diverse recommendations that branch out in different directions from the core interests.
        
        Format your response as a simple bullet point list with no additional text:
        - Topic 1
        - Topic 2
        etc.""",
        
        'fr': f"""En fonction des sujets suivants qui ont intéressé un utilisateur:
        {topics_str}
        
        Veuillez recommander exactement {count} nouveaux sujets intéressants que l'utilisateur pourrait vouloir étudier ensuite.
        Les recommandations doivent être liées aux intérêts de l'utilisateur mais introduire de nouveaux concepts ou domaines.
        Fournissez des recommandations diverses qui s'étendent dans différentes directions à partir des intérêts principaux.
        
        Formatez votre réponse sous forme de liste à puces simple sans texte supplémentaire:
        - Sujet 1
        - Sujet 2
        etc.""",
        
        'es': f"""Basado en los siguientes temas que han interesado a un usuario:
        {topics_str}
        
        Por favor, recomienda exactamente {count} temas nuevos e interesantes que el usuario podría querer aprender a continuación.
        Las recomendaciones deben estar relacionadas con los intereses del usuario pero introducir nuevos conceptos o áreas.
        Proporciona recomendaciones diversas que se ramifiquen en diferentes direcciones a partir de los intereses principales.
        
        Formatea tu respuesta como una simple lista de viñetas sin texto adicional:
        - Tema 1
        - Tema 2
        etc.""",
        
        'de': f"""Basierend auf den folgenden Themen, für die ein Benutzer Interesse gezeigt hat:
        {topics_str}
        
        Bitte empfehlen Sie genau {count} neue und interessante Themen, über die der Benutzer als nächstes lernen möchte.
        Die Empfehlungen sollten mit den Interessen des Benutzers zusammenhängen, aber neue Konzepte oder Bereiche einführen.
        Geben Sie vielfältige Empfehlungen, die sich in verschiedene Richtungen von den Kerninteressen verzweigen.
        
        Formatieren Sie Ihre Antwort als einfache Aufzählungsliste ohne zusätzlichen Text:
        - Thema 1
        - Thema 2
        usw.""",
        
        'it': f"""In base ai seguenti argomenti che hanno interessato un utente:
        {topics_str}
        
        Si prega di consigliare esattamente {count} nuovi e interessanti argomenti che l'utente potrebbe voler imparare successivamente.
        I consigli dovrebbero essere correlati agli interessi dell'utente ma introdurre nuovi concetti o aree.
        Fornisci consigli diversificati che si diramano in diverse direzioni dagli interessi principali.
        
        Formatta la tua risposta come un semplice elenco puntato senza testo aggiuntivo:
        - Argomento 1
        - Argomento 2
        ecc.""",
        
        'ja': f"""ユーザーが関心を示した以下のトピックに基づいて：
        {topics_str}
        
        ユーザーが次に学びたいと思うかもしれない{count}個の新しい興味深いトピックを推薦してください。
        推奨事項はユーザーの興味に関連しているべきですが、新しい概念や分野を紹介するものでなければなりません。
        核心的な興味から異なる方向に分岐する多様な推奨事項を提供してください。
        
        回答を追加のテキストなしの単純な箇条書きリストとして整形してください：
        - トピック1
        - トピック2
        など""",
        
        'zh': f"""根据用户表示对以下主题感兴趣：
        {topics_str}
        
        请推荐恰好{count}个用户可能想要下一步学习的新的有趣主题。
        推荐应该与用户的兴趣相关，但引入新的概念或领域。
        提供多样化的推荐，从核心兴趣向不同方向扩展。
        
        请将您的回答格式化为简单的项目符号列表，不要添加额外的文字：
        - 主题1
        - 主题2
        等等""",
        
        'ar': f"""بناءً على الموضوعات التالية التي أظهر المستخدم اهتمامًا بها:
        {topics_str}
        
        يرجى التوصية بـ {count} موضوعات جديدة ومثيرة للاهتمام قد يرغب المستخدم في معرفة المزيد عنها.
        يجب أن تكون التوصيات مرتبطة باهتمامات المستخدم ولكنها تقدم مفاهيم أو مجالات جديدة.
        قدم توصيات متنوعة تتفرع في اتجاهات مختلفة من الاهتمامات الأساسية.
        
        قم بتنسيق ردك كقائمة نقطية بسيطة بدون نص إضافي:
        - الموضوع 1
        - الموضوع 2
        إلخ."""
    }
    
    # Default to English if language not available
    return prompts.get(language, prompts['en'])

def get_quiz_prompt(topic: str, question_count: int, language: str = 'en', difficulty: str = 'medium', content: str = "") -> str:
    """
    Generate prompt for quiz questions
    
    Args:
        topic (str): Topic for quiz
        question_count (int): Number of questions to generate
        language (str): Language code
        difficulty (str): Quiz difficulty (easy, medium, hard)
        content (str): Content to base questions on
        
    Returns:
        str: Generated prompt
    """
    difficulty_descriptions = {
        'easy': {
            'en': 'simple recall of basic facts',
            'fr': 'simple rappel des faits de base',
            'es': 'recuerdo simple de hechos básicos',
            'de': 'einfaches Abrufen grundlegender Fakten',
            'it': 'semplice richiamo di fatti basilari',
            'ja': '基本的な事実の単純な想起',
            'zh': '简单回忆基本事实',
            'ar': 'استرجاع بسيط للحقائق الأساسية'
        },
        'medium': {
            'en': 'understanding of concepts and simple application',
            'fr': 'compréhension des concepts et application simple',
            'es': 'comprensión de conceptos y aplicación simple',
            'de': 'Verständnis von Konzepten und einfache Anwendung',
            'it': 'comprensione dei concetti e semplice applicazione',
            'ja': '概念の理解と簡単な応用',
            'zh': '理解概念和简单应用',
            'ar': 'فهم المفاهيم والتطبيق البسيط'
        },
        'hard': {
            'en': 'complex application, analysis, and deeper understanding',
            'fr': 'application complexe, analyse et compréhension approfondie',
            'es': 'aplicación compleja, análisis y comprensión más profunda',
            'de': 'komplexe Anwendung, Analyse und tieferes Verständnis',
            'it': 'applicazione complessa, analisi e comprensione più profonda',
            'ja': '複雑な応用、分析、より深い理解',
            'zh': '复杂应用、分析和更深入的理解',
            'ar': 'التطبيق المعقد والتحليل والفهم الأعمق'
        }
    }
    
    # Get difficulty description in the specified language
    difficulty_desc = difficulty_descriptions.get(difficulty, {}).get(language, difficulty_descriptions[difficulty]['en'])
    
    prompts = {
        'en': f"""Create {question_count} multiple-choice quiz questions about "{topic}" at {difficulty} difficulty level ({difficulty_desc}).
        
        Each question should have:
        1. A clear, concise question
        2. Four answer options (A, B, C, D)
        3. The correct answer 
        4. A brief explanation of why that answer is correct
        
        {"Base the questions on this content: " + content if content else ""}
        
        Format each question as follows:

        Q1: [Question text]
        A: [Option A]
        B: [Option B]
        C: [Option C]
        D: [Option D]
        Answer: [Correct letter]
        Explanation: [Brief explanation]

        Ensure questions test different aspects of the topic and promote learning.""",
        
        'fr': f"""Créez {question_count} questions de quiz à choix multiples sur "{topic}" au niveau de difficulté {difficulty} ({difficulty_desc}).
        
        Chaque question doit avoir:
        1. Une question claire et concise
        2. Quatre options de réponse (A, B, C, D)
        3. La bonne réponse
        4. Une brève explication de pourquoi cette réponse est correcte
        
        {"Basez les questions sur ce contenu: " + content if content else ""}
        
        Formatez chaque question comme suit:

        Q1: [Texte de la question]
        A: [Option A]
        B: [Option B]
        C: [Option C]
        D: [Option D]
        Answer: [Lettre correcte]
        Explanation: [Brève explication]

        Assurez-vous que les questions testent différents aspects du sujet et favorisent l'apprentissage.""",
        
        'es': f"""Crea {question_count} preguntas de cuestionario de opción múltiple sobre "{topic}" en el nivel de dificultad {difficulty} ({difficulty_desc}).
        
        Cada pregunta debe tener:
        1. Una pregunta clara y concisa
        2. Cuatro opciones de respuesta (A, B, C, D)
        3. La respuesta correcta
        4. Una breve explicación de por qué esa respuesta es correcta
        
        {"Basa las preguntas en este contenido: " + content if content else ""}
        
        Formatea cada pregunta de la siguiente manera:

        Q1: [Texto de la pregunta]
        A: [Opción A]
        B: [Opción B]
        C: [Opción C]
        D: [Opción D]
        Answer: [Letra correcta]
        Explanation: [Breve explicación]

        Asegúrate de que las preguntas prueben diferentes aspectos del tema y promuevan el aprendizaje.""",
        
        'de': f"""Erstellen Sie {question_count} Multiple-Choice-Quizfragen zu "{topic}" auf dem Schwierigkeitsgrad {difficulty} ({difficulty_desc}).
        
        Jede Frage sollte haben:
        1. Eine klare, prägnante Frage
        2. Vier Antwortmöglichkeiten (A, B, C, D)
        3. Die richtige Antwort
        4. Eine kurze Erklärung, warum diese Antwort richtig ist
        
        {"Basieren Sie die Fragen auf diesem Inhalt: " + content if content else ""}
        
        Formatieren Sie jede Frage wie folgt:

        Q1: [Fragetext]
        A: [Option A]
        B: [Option B]
        C: [Option C]
        D: [Option D]
        Answer: [Korrekter Buchstabe]
        Explanation: [Kurze Erklärung]

        Stellen Sie sicher, dass die Fragen verschiedene Aspekte des Themas testen und das Lernen fördern.""",
        
        'it': f"""Crea {question_count} domande a scelta multipla sul tema "{topic}" al livello di difficoltà {difficulty} ({difficulty_desc}).
        
        Ogni domanda dovrebbe avere:
        1. Una domanda chiara e concisa
        2. Quattro opzioni di risposta (A, B, C, D)
        3. La risposta corretta
        4. Una breve spiegazione del perché quella risposta è corretta
        
        {"Basa le domande su questo contenuto: " + content if content else ""}
        
        Formatta ogni domanda come segue:

        Q1: [Testo della domanda]
        A: [Opzione A]
        B: [Opzione B]
        C: [Opzione C]
        D: [Opzione D]
        Answer: [Lettera corretta]
        Explanation: [Breve spiegazione]

        Assicurati che le domande testino diversi aspetti dell'argomento e promuovano l'apprendimento.""",
        
        'ja': f""""{topic}"に関する{question_count}つの多肢選択クイズ問題を、{difficulty}の難易度({difficulty_desc})で作成してください。
        
        各質問には以下が必要です：
        1. 明確で簡潔な質問
        2. 4つの回答オプション（A、B、C、D）
        3. 正解
        4. その回答が正しい理由の簡単な説明
        
        {"この内容に基づいて質問を作成してください: " + content if content else ""}
        
        次のように各質問をフォーマットしてください：

        Q1: [質問文]
        A: [オプションA]
        B: [オプションB]
        C: [オプションC]
        D: [オプションD]
        Answer: [正解の文字]
        Explanation: [簡単な説明]

        質問がトピックのさまざまな側面をテストし、学習を促進することを確認してください。""",
        
        'zh': f"""创建{question_count}个关于"{topic}"的多项选择题，难度为{difficulty}({difficulty_desc})。
        
        每个问题应包含：
        1. 一个清晰、简洁的问题
        2. 四个答案选项（A、B、C、D）
        3. 正确答案
        4. 简短解释为什么该答案正确
        
        {"根据这些内容出题: " + content if content else ""}
        
        按以下格式出每个问题：

        Q1: [问题文本]
        A: [选项A]
        B: [选项B]
        C: [选项C]
        D: [选项D]
        Answer: [正确的字母]
        Explanation: [简要解释]

        确保问题测试主题的不同方面并促进学习。""",
        
        'ar': f"""قم بإنشاء {question_count} أسئلة اختبار متعددة الخيارات حول "{topic}" بمستوى صعوبة {difficulty} ({difficulty_desc}).
        
        يجب أن يحتوي كل سؤال على:
        1. سؤال واضح وموجز
        2. أربعة خيارات للإجابة (أ، ب، ج، د)
        3. الإجابة الصحيحة
        4. شرح موجز لسبب صحة هذه الإجابة
        
        {"استند بالأسئلة على هذا المحتوى: " + content if content else ""}
        
        قم بتنسيق كل سؤال على النحو التالي:

        Q1: [نص السؤال]
        A: [الخيار أ]
        B: [الخيار ب]
        C: [الخيار ج]
        D: [الخيار د]
        Answer: [الحرف الصحيح]
        Explanation: [شرح موجز]

        تأكد من أن الأسئلة تختبر جوانب مختلفة من الموضوع وتعزز التعلم."""
    }
    
    # Default to English if language not available
    return prompts.get(language, prompts['en'])

def get_summarization_prompt(text: str, max_length: int, language: str = 'en') -> str:
    """
    Generate prompt for text summarization
    
    Args:
        text (str): Text to summarize
        max_length (int): Maximum length of summary in words
        language (str): Language code
        
    Returns:
        str: Generated prompt
    """
    prompts = {
        'en': f"""Summarize the following text in approximately {max_length} words or less. 
        Capture the main ideas and important details while maintaining clarity.
        Do not include personal opinions or interpretations that aren't in the original text.
        
        TEXT TO SUMMARIZE:
        {text}""",
        
        'fr': f"""Résumez le texte suivant en environ {max_length} mots ou moins.
        Capturez les idées principales et les détails importants tout en maintenant la clarté.
        N'incluez pas d'opinions personnelles ou d'interprétations qui ne figurent pas dans le texte original.
        
        TEXTE À RÉSUMER:
        {text}""",
        
        'es': f"""Resume el siguiente texto en aproximadamente {max_length} palabras o menos.
        Captura las ideas principales y los detalles importantes manteniendo la claridad.
        No incluyas opiniones personales o interpretaciones que no estén en el texto original.
        
        TEXTO A RESUMIR:
        {text}""",
        
        'de': f"""Fassen Sie den folgenden Text in ungefähr {max_length} Wörtern oder weniger zusammen.
        Erfassen Sie die Hauptideen und wichtigen Details, während Sie die Klarheit bewahren.
        Fügen Sie keine persönlichen Meinungen oder Interpretationen hinzu, die nicht im Originaltext enthalten sind.
        
        ZU ZUSAMMENFASSENDER TEXT:
        {text}""",
        
        'it': f"""Riassumi il seguente testo in circa {max_length} parole o meno.
        Cattura le idee principali e i dettagli importanti mantenendo la chiarezza.
        Non includere opinioni personali o interpretazioni che non sono nel testo originale.
        
        TESTO DA RIASSUMERE:
        {text}""",
        
        'ja': f"""以下のテキストを約{max_length}語以下で要約してください。
        明確さを維持しながら、主なアイデアと重要な詳細を捉えてください。
        原文にない個人的な意見や解釈を含めないでください。
        
        要約するテキスト：
        {text}""",
        
        'zh': f"""请用大约{max_length}字或更少的文字概括以下文本。
        在保持清晰度的同时，捕捉主要思想和重要细节。
        不要包含原文中没有的个人意见或解释。
        
        要概括的文本：
        {text}""",
        
        'ar': f"""لخص النص التالي في حوالي {max_length} كلمة أو أقل.
        التقط الأفكار الرئيسية والتفاصيل المهمة مع الحفاظ على الوضوح.
        لا تضمن آراء شخصية أو تفسيرات غير موجودة في النص الأصلي.
        
        النص المراد تلخيصه:
        {text}"""
    }
    
    # Default to English if language not available
    return prompts.get(language, prompts['en'])