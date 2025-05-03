def get_learning_prompt(topic, target_word_count, language='fr'):
    """
    Génère un prompt pour la création d'un snippet d'apprentissage.
    Adapté pour prendre en compte la langue cible.
    """
    prompts = {
        'fr': f"""
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
        Écrivez tout le contenu en français.
        """,
        
        'en': f"""
        Create an engaging learning snippet about: {topic}.
        
        Guidelines:
        1. Start with a catchy title beginning with '# '
        2. Write content of about {target_word_count} words (for about 5 minutes of audio)
        3. Use a conversational tone, as if speaking to a curious friend
        4. Structure the content with an introduction, key points, and conclusion
        5. Include 2-3 surprising or lesser-known facts
        6. Avoid excessive technical jargon, but don't oversimplify
        7. End with a thought-provoking reflection or question
        
        The content should be informative, fascinating, and easy to follow when listened to.
        Write all content in English.
        """,
        
        'es': f"""
        Crea un fragmento de aprendizaje interesante sobre: {topic}.
        
        Directrices:
        1. Comienza con un título atractivo que empiece con '# '
        2. Escribe un contenido de aproximadamente {target_word_count} palabras (para unos 5 minutos de audio)
        3. Utiliza un tono conversacional, como si hablaras con un amigo curioso
        4. Estructura el contenido con una introducción, puntos clave y conclusión
        5. Incluye 2-3 datos sorprendentes o menos conocidos
        6. Evita la jerga técnica excesiva, pero no simplifiques demasiado
        7. Termina con una reflexión o pregunta que invite a la reflexión
        
        El contenido debe ser informativo, fascinante y fácil de seguir cuando se escucha.
        Escribe todo el contenido en español.
        """,
        
        'de': f"""
        Erstellen Sie einen fesselnden Lernschnipsel über: {topic}.
        
        Richtlinien:
        1. Beginnen Sie mit einem einprägsamen Titel, der mit '# ' beginnt
        2. Schreiben Sie einen Inhalt von etwa {target_word_count} Wörtern (für etwa 5 Minuten Audio)
        3. Verwenden Sie einen lockeren Gesprächston, als ob Sie mit einem neugierigen Freund sprechen würden
        4. Strukturieren Sie den Inhalt mit einer Einleitung, Schlüsselpunkten und einer Schlussfolgerung
        5. Fügen Sie 2-3 überraschende oder weniger bekannte Fakten hinzu
        6. Vermeiden Sie übermäßigen technischen Fachjargon, aber vereinfachen Sie nicht zu sehr
        7. Enden Sie mit einer zum Nachdenken anregenden Reflexion oder Frage
        
        Der Inhalt sollte informativ und faszinierend sein und beim Zuhören leicht zu folgen sein.
        Schreiben Sie den gesamten Inhalt auf Deutsch.
        """,
        
        'it': f"""
        Crea uno snippet di apprendimento coinvolgente sull'argomento: {topic}.
        
        Linee guida:
        1. Inizia con un titolo accattivante che inizi con '# '
        2. Scrivi un contenuto di circa {target_word_count} parole (per circa 5 minuti di audio)
        3. Usa un tono conversazionale, come se stessi parlando con un amico curioso
        4. Struttura il contenuto con un'introduzione, punti chiave e una conclusione
        5. Includi 2-3 fatti sorprendenti o meno conosciuti
        6. Evita un eccessivo gergo tecnico, ma non semplificare troppo
        7. Concludi con una riflessione o una domanda stimolante
        
        Il contenuto deve essere informativo, affascinante e facile da seguire durante l'ascolto.
        Scrivi tutto il contenuto in italiano.
        """,
        
        'ja': f"""
        以下のトピックについて魅力的な学習スニペットを作成してください: {topic}
        
        ガイドライン:
        1. '# 'で始まるキャッチーなタイトルから始めてください
        2. 約{target_word_count}語のコンテンツを書いてください（約5分の音声用）
        3. 好奇心旺盛な友人に話しかけるような会話調を使用してください
        4. 導入、要点、結論でコンテンツを構成してください
        5. 2〜3の驚くべき事実や知られていない情報を含めてください
        6. 過度な専門用語は避けながらも、単純化しすぎないでください
        7. 思考を促す考察や質問で締めくくってください
        
        コンテンツは聞いたときに情報豊富で魅力的、そして理解しやすいものにしてください。
        すべての内容を日本語で書いてください。
        """,
        
        'zh': f"""
        创建一个关于以下主题的引人入胜的学习片段: {topic}
        
        指导方针:
        1. 以以'# '开头的吸引人的标题开始
        2. 撰写约{target_word_count}个词的内容（大约5分钟的音频）
        3. 使用对话式语调，就像在和一个好奇的朋友交谈
        4. 用引言、要点和结论来构建内容
        5. 包含2-3个令人惊讶或鲜为人知的事实
        6. 避免过多的技术术语，但也不要过度简化
        7. 以一个引人深思的反思或问题作为结束
        
        内容应该具有信息性、引人入胜，并且在听时容易理解。
        所有内容请用中文书写。
        """
    }
    
    # Utiliser le prompt pour la langue spécifiée, ou default en anglais
    return prompts.get(language, prompts['en'])

def get_recommendation_prompt(previous_topics, count, language='fr'):
    """
    Génère un prompt pour obtenir des recommandations de sujets.
    Adapté pour prendre en compte la langue cible.
    """
    topics_str = ', '.join(previous_topics)
    
    prompts = {
        'fr': f"""
        En fonction des sujets suivants consultés par l'utilisateur:
        {topics_str}
        
        Suggérez {count} nouveau(x) sujet(s) qui pourrai(en)t l'intéresser. 
        Pour chaque sujet, donnez simplement le titre du sujet, sans explication.
        
        Assurez-vous que les sujets sont:
        1. Liés aux intérêts exprimés, mais suffisamment différents pour élargir les horizons
        2. Spécifiques et concrets plutôt que vagues
        3. Intrigants et susceptibles de susciter la curiosité
        
        Formatez chaque sujet comme un élément de liste avec un tiret.
        Répondez en français.
        """,
        
        'en': f"""
        Based on the following topics the user has viewed:
        {topics_str}
        
        Suggest {count} new topic(s) that might interest them.
        For each topic, simply provide the title of the topic, without explanation.
        
        Make sure the topics are:
        1. Related to the expressed interests, but different enough to broaden horizons
        2. Specific and concrete rather than vague
        3. Intriguing and likely to spark curiosity
        
        Format each topic as a list item with a dash.
        Respond in English.
        """,
        
        'es': f"""
        Según los siguientes temas que el usuario ha consultado:
        {topics_str}
        
        Sugiere {count} nuevo(s) tema(s) que puedan interesarle.
        Para cada tema, simplemente proporcione el título del tema, sin explicación.
        
        Asegúrate de que los temas sean:
        1. Relacionados con los intereses expresados, pero lo suficientemente diferentes para ampliar horizontes
        2. Específicos y concretos en lugar de vagos
        3. Intrigantes y con probabilidad de despertar curiosidad
        
        Formatea cada tema como un elemento de lista con un guión.
        Responde en español.
        """,
        
        'de': f"""
        Basierend auf den folgenden Themen, die der Benutzer angesehen hat:
        {topics_str}
        
        Schlagen Sie {count} neue(s) Thema(n) vor, das/die ihn interessieren könnte(n).
        Geben Sie für jedes Thema nur den Titel des Themas an, ohne Erklärung.
        
        Stellen Sie sicher, dass die Themen:
        1. Mit den ausgedrückten Interessen zusammenhängen, aber unterschiedlich genug sind, um den Horizont zu erweitern
        2. Spezifisch und konkret statt vage sind
        3. Faszinierend sind und wahrscheinlich Neugier wecken
        
        Formatieren Sie jedes Thema als Listenelement mit einem Bindestrich.
        Antworten Sie auf Deutsch.
        """,
        
        'it': f"""
        In base ai seguenti argomenti visualizzati dall'utente:
        {topics_str}
        
        Suggerisci {count} nuovi argomenti che potrebbero interessargli.
        Per ogni argomento, fornisci semplicemente il titolo dell'argomento, senza spiegazione.
        
        Assicurati che gli argomenti siano:
        1. Correlati agli interessi espressi, ma abbastanza diversi per ampliare gli orizzonti
        2. Specifici e concreti piuttosto che vaghi
        3. Intriganti e probabilmente in grado di suscitare curiosità
        
        Formatta ogni argomento come elemento di un elenco con un trattino.
        Rispondi in italiano.
        """,
        
        'ja': f"""
        ユーザーが閲覧した以下のトピックに基づいて:
        {topics_str}
        
        興味を持つかもしれない{count}個の新しいトピックを提案してください。
        各トピックについて、説明なしでトピックのタイトルのみを提供してください。
        
        トピックが以下の条件を満たしていることを確認してください:
        1. 表現された興味に関連していますが、視野を広げるのに十分に異なっている
        2. 漠然としたものではなく、具体的で明確である
        3. 興味をそそり、好奇心を呼び起こす可能性がある
        
        各トピックをダッシュ付きのリスト項目としてフォーマットしてください。
        日本語で回答してください。
        """,
        
        'zh': f"""
        根据用户浏览过的以下主题:
        {topics_str}
        
        建议{count}个可能感兴趣的新主题。
        对于每个主题，只需提供主题的标题，无需解释。
        
        确保主题是:
        1. 与表达的兴趣相关，但足够不同以拓宽视野
        2. 具体明确而非模糊
        3. 引人入胜且可能引起好奇心
        
        将每个主题格式化为带破折号的列表项。
        请用中文回答。
        """
    }
    
    # Utiliser le prompt pour la langue spécifiée, ou default en anglais
    return prompts.get(language, prompts['en'])