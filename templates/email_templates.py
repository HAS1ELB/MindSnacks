from typing import Dict, Any
import datetime

def get_welcome_email(username: str, language: str = 'en') -> Dict[str, str]:
    """
    Generate welcome email template
    
    Args:
        username (str): User's name
        language (str): Language code
        
    Returns:
        dict: Email template with subject and body
    """
    templates = {
        'en': {
            'subject': 'Welcome to Mindsnacks! 🎧',
            'body': f"""
Hello {username},

Welcome to Mindsnacks - your personal audio learning assistant!

We're excited to have you join our community of curious minds. With Mindsnacks, you can:

- Create personalized learning snippets on any topic
- Build playlists tailored to your interests
- Test your knowledge with customized quizzes
- Access your content across devices

To get started, here are a few tips:
1. Visit the Discover page to explore trending topics
2. Try generating your first snippet about a topic you're curious about
3. Check out the Learning Paths for guided educational journeys

If you have any questions, feel free to reply to this email or check our Help Center.

Happy learning!

The Mindsnacks Team
"""
        },
        
        'fr': {
            'subject': 'Bienvenue sur Mindsnacks! 🎧',
            'body': f"""
Bonjour {username},

Bienvenue sur Mindsnacks - votre assistant personnel d'apprentissage audio !

Nous sommes ravis de vous voir rejoindre notre communauté d'esprits curieux. Avec Mindsnacks, vous pouvez :

- Créer des extraits d'apprentissage personnalisés sur n'importe quel sujet
- Constituer des playlists adaptées à vos centres d'intérêt
- Tester vos connaissances avec des quiz personnalisés
- Accéder à votre contenu sur tous vos appareils

Pour commencer, voici quelques conseils :
1. Visitez la page Découvrir pour explorer les sujets tendance
2. Essayez de générer votre premier extrait sur un sujet qui vous intéresse
3. Consultez les Parcours d'Apprentissage pour des trajets éducatifs guidés

Si vous avez des questions, n'hésitez pas à répondre à cet email ou à consulter notre Centre d'Aide.

Bon apprentissage !

L'équipe Mindsnacks
"""
        },
        
        'es': {
            'subject': '¡Bienvenido a Mindsnacks! 🎧',
            'body': f"""
Hola {username},

Bienvenido a Mindsnacks - ¡tu asistente personal de aprendizaje de audio!

Estamos emocionados de que te unas a nuestra comunidad de mentes curiosas. Con Mindsnacks, puedes:

- Crear fragmentos de aprendizaje personalizados sobre cualquier tema
- Construir listas de reproducción adaptadas a tus intereses
- Poner a prueba tus conocimientos con cuestionarios personalizados
- Acceder a tu contenido en todos los dispositivos

Para comenzar, aquí tienes algunos consejos:
1. Visita la página Descubrir para explorar temas tendencia
2. Intenta generar tu primer fragmento sobre un tema que te interese
3. Consulta las Rutas de Aprendizaje para viajes educativos guiados

Si tienes alguna pregunta, no dudes en responder a este correo o consultar nuestro Centro de Ayuda.

¡Feliz aprendizaje!

El equipo de Mindsnacks
"""
        },
        
        'de': {
            'subject': 'Willkommen bei Mindsnacks! 🎧',
            'body': f"""
Hallo {username},

Willkommen bei Mindsnacks - deinem persönlichen Audio-Lernassistenten!

Wir freuen uns, dass du dich unserer Gemeinschaft neugieriger Köpfe anschließt. Mit Mindsnacks kannst du:

- Personalisierte Lernschnipsel zu jedem Thema erstellen
- Playlists erstellen, die auf deine Interessen zugeschnitten sind
- Dein Wissen mit angepassten Quizzen testen
- Auf deine Inhalte auf allen Geräten zugreifen

Um zu beginnen, hier einige Tipps:
1. Besuche die Entdecken-Seite, um Trendthemen zu erkunden
2. Versuche, deinen ersten Schnipsel zu einem Thema zu erstellen, das dich interessiert
3. Schau dir die Lernpfade für geführte Bildungsreisen an

Wenn du Fragen hast, antworte einfach auf diese E-Mail oder besuche unser Hilfezentrum.

Frohes Lernen!

Das Mindsnacks-Team
"""
        },
        
        'it': {
            'subject': 'Benvenuto su Mindsnacks! 🎧',
            'body': f"""
Ciao {username},

Benvenuto su Mindsnacks - il tuo assistente personale per l'apprendimento audio!

Siamo entusiasti di averti nella nostra comunità di menti curiose. Con Mindsnacks, puoi:

- Creare snippet di apprendimento personalizzati su qualsiasi argomento
- Costruire playlist su misura per i tuoi interessi
- Testare le tue conoscenze con quiz personalizzati
- Accedere ai tuoi contenuti su tutti i dispositivi

Per iniziare, ecco alcuni suggerimenti:
1. Visita la pagina Scopri per esplorare gli argomenti di tendenza
2. Prova a generare il tuo primo snippet su un argomento che ti incuriosisce
3. Dai un'occhiata ai Percorsi di Apprendimento per viaggi educativi guidati

Se hai domande, sentiti libero di rispondere a questa email o consultare il nostro Centro Assistenza.

Buon apprendimento!

Il Team Mindsnacks
"""
        },
        
        'ja': {
            'subject': 'Mindsnacksへようこそ！🎧',
            'body': f"""
こんにちは、{username}さん

パーソナルオーディオ学習アシスタント、Mindsnacksへようこそ！

好奇心旺盛な仲間のコミュニティに参加していただき、大変うれしく思います。Mindsnacksでは、次のことができます：

- あらゆるトピックについてパーソナライズされた学習スニペットを作成
- あなたの興味に合わせたプレイリストの構築
- カスタマイズされたクイズで知識をテスト
- あらゆるデバイスからコンテンツにアクセス

始めるためのヒントをいくつか紹介します：
1. 「発見」ページを訪れて、トレンドのトピックを探索
2. 興味のあるトピックについて最初のスニペットを生成してみる
3. ガイド付き教育の旅のために学習パスをチェック

質問がある場合は、このメールに返信するか、ヘルプセンターをご確認ください。

楽しい学習を！

Mindsnacksチーム
"""
        },
        
        'zh': {
            'subject': '欢迎使用Mindsnacks！🎧',
            'body': f"""
你好，{username}

欢迎使用Mindsnacks - 你的个人音频学习助手！

我们很高兴你加入我们好奇心强的社区。使用Mindsnacks，你可以：

- 创建任何主题的个性化学习片段
- 建立符合你兴趣的播放列表
- 通过定制的测验测试你的知识
- 在各种设备上访问你的内容

开始使用的一些提示：
1. 访问"发现"页面，探索热门主题
2. 尝试生成关于你感兴趣主题的第一个片段
3. 查看学习路径，获取引导式教育旅程

如果你有任何问题，随时回复此邮件或查看我们的帮助中心。

快乐学习！

Mindsnacks团队
"""
        },
        
        'ar': {
            'subject': 'مرحباً بك في مايندسناكس! 🎧',
            'body': f"""
مرحباً {username}،

مرحباً بك في مايندسناكس - مساعدك الشخصي للتعلم الصوتي!

نحن متحمسون لانضمامك إلى مجتمعنا من العقول الفضولية. مع مايندسناكس، يمكنك:

- إنشاء مقتطفات تعليمية مخصصة حول أي موضوع
- بناء قوائم تشغيل مصممة حسب اهتماماتك
- اختبار معرفتك من خلال اختبارات مخصصة
- الوصول إلى المحتوى الخاص بك عبر الأجهزة المختلفة

للبدء، إليك بعض النصائح:
1. قم بزيارة صفحة الاكتشاف لاستكشاف المواضيع الرائجة
2. جرب إنشاء أول مقتطف لك حول موضوع أنت فضولي بشأنه
3. تحقق من مسارات التعلم للرحلات التعليمية الموجهة

إذا كانت لديك أي أسئلة، فلا تتردد في الرد على هذا البريد الإلكتروني أو التحقق من مركز المساعدة لدينا.

تعلم سعيد!

فريق مايندسناكس
"""
        }
    }
    
    # Default to English if language not available
    return templates.get(language, templates['en'])

def get_new_feature_email(username: str, feature_name: str, feature_description: str, language: str = 'en') -> Dict[str, str]:
    """
    Generate new feature announcement email template
    
    Args:
        username (str): User's name
        feature_name (str): Name of new feature
        feature_description (str): Description of new feature
        language (str): Language code
        
    Returns:
        dict: Email template with subject and body
    """
    templates = {
        'en': {
            'subject': f'New Feature: {feature_name} is here! 🎉',
            'body': f"""
Hello {username},

We're excited to announce that we've just launched a new feature: {feature_name}!

{feature_description}

Log in to your Mindsnacks account to check it out. We'd love to hear your feedback on this new addition.

Happy learning!

The Mindsnacks Team
"""
        },
        
        'fr': {
            'subject': f'Nouvelle Fonctionnalité : {feature_name} est là ! 🎉',
            'body': f"""
Bonjour {username},

Nous sommes ravis d'annoncer que nous venons de lancer une nouvelle fonctionnalité : {feature_name} !

{feature_description}

Connectez-vous à votre compte Mindsnacks pour la découvrir. Nous aimerions avoir votre avis sur cette nouveauté.

Bon apprentissage !

L'équipe Mindsnacks
"""
        },
        
        'es': {
            'subject': f'Nueva Función: ¡{feature_name} ya está aquí! 🎉',
            'body': f"""
Hola {username},

Nos complace anunciar que acabamos de lanzar una nueva función: ¡{feature_name}!

{feature_description}

Inicia sesión en tu cuenta de Mindsnacks para probarlo. Nos encantaría conocer tu opinión sobre esta nueva incorporación.

¡Feliz aprendizaje!

El equipo de Mindsnacks
"""
        },
        
        'de': {
            'subject': f'Neues Feature: {feature_name} ist da! 🎉',
            'body': f"""
Hallo {username},

Wir freuen uns, bekannt geben zu können, dass wir gerade ein neues Feature eingeführt haben: {feature_name}!

{feature_description}

Melde dich bei deinem Mindsnacks-Konto an, um es auszuprobieren. Wir würden gerne dein Feedback zu dieser Neuerung hören.

Frohes Lernen!

Das Mindsnacks-Team
"""
        }
    }
    
    # Default to English if language not available
    return templates.get(language, templates['en'])

def get_streak_reminder_email(username: str, days_streak: int, language: str = 'en') -> Dict[str, str]:
    """
    Generate streak reminder email template
    
    Args:
        username (str): User's name
        days_streak (int): Current streak in days
        language (str): Language code
        
    Returns:
        dict: Email template with subject and body
    """
    templates = {
        'en': {
            'subject': f'Don\'t break your {days_streak}-day learning streak! 🔥',
            'body': f"""
Hello {username},

Wow! You've been learning with Mindsnacks for {days_streak} days in a row - that's impressive!

However, we noticed you haven't logged in today yet. Don't break your streak! Take just 5 minutes to listen to a quick snippet or create a new one.

Remember, consistent learning leads to better retention and understanding.

Keep the momentum going!

The Mindsnacks Team
"""
        },
        
        'fr': {
            'subject': f'Ne brisez pas votre série d\'apprentissage de {days_streak} jours ! 🔥',
            'body': f"""
Bonjour {username},

Wow ! Vous apprenez avec Mindsnacks depuis {days_streak} jours d'affilée - c'est impressionnant !

Cependant, nous avons remarqué que vous ne vous êtes pas encore connecté aujourd'hui. Ne brisez pas votre série ! Prenez juste 5 minutes pour écouter un extrait rapide ou en créer un nouveau.

Rappelez-vous, un apprentissage régulier mène à une meilleure rétention et compréhension.

Gardez cet élan !

L'équipe Mindsnacks
"""
        },
        
        'es': {
            'subject': f'¡No rompas tu racha de aprendizaje de {days_streak} días! 🔥',
            'body': f"""
Hola {username},

¡Guau! Has estado aprendiendo con Mindsnacks durante {days_streak} días consecutivos - ¡eso es impresionante!

Sin embargo, notamos que aún no has iniciado sesión hoy. ¡No rompas tu racha! Tómate solo 5 minutos para escuchar un fragmento rápido o crear uno nuevo.

Recuerda, el aprendizaje constante conduce a una mejor retención y comprensión.

¡Mantén el impulso!

El equipo de Mindsnacks
"""
        },
        
        'de': {
            'subject': f'Unterbreche deine {days_streak}-tägige Lernserie nicht! 🔥',
            'body': f"""
Hallo {username},

Wow! Du lernst seit {days_streak} Tagen in Folge mit Mindsnacks - das ist beeindruckend!

Allerdings haben wir bemerkt, dass du dich heute noch nicht angemeldet hast. Brich deine Serie nicht ab! Nimm dir nur 5 Minuten Zeit, um einen kurzen Schnipsel zu hören oder einen neuen zu erstellen.

Denk daran, kontinuierliches Lernen führt zu besserer Merkfähigkeit und besserem Verständnis.

Behalte den Schwung bei!

Das Mindsnacks-Team
"""
        }
    }
    
    # Default to English if language not available
    return templates.get(language, templates['en'])

def get_digest_email(username: str, top_topics: list, recommended_topics: list, language: str = 'en') -> Dict[str, str]:
    """
    Generate weekly digest email template
    
    Args:
        username (str): User's name
        top_topics (list): List of top trending topics
        recommended_topics (list): List of recommended topics for the user
        language (str): Language code
        
    Returns:
        dict: Email template with subject and body
    """
    # Format current date
    date = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Format topics as bullet points
    top_topics_formatted = "\n".join([f"- {topic}" for topic in top_topics[:5]])
    recommended_topics_formatted = "\n".join([f"- {topic}" for topic in recommended_topics[:5]])
    
    templates = {
        'en': {
            'subject': f'Your Weekly Learning Digest - {date}',
            'body': f"""
Hello {username},

Here's your Mindsnacks weekly digest for {date}:

**Top Trending Topics This Week:**
{top_topics_formatted}

**Recommended Just For You:**
{recommended_topics_formatted}

We've also added new content to our Learning Paths and updated our quiz database with new questions.

Log in now to explore these topics and continue your learning journey!

Happy learning!

The Mindsnacks Team
"""
        },
        
        'fr': {
            'subject': f'Votre Résumé d\'Apprentissage Hebdomadaire - {date}',
            'body': f"""
Bonjour {username},

Voici votre résumé hebdomadaire Mindsnacks pour le {date} :

**Sujets Tendance Cette Semaine :**
{top_topics_formatted}

**Recommandé Juste Pour Vous :**
{recommended_topics_formatted}

Nous avons également ajouté du nouveau contenu à nos Parcours d'Apprentissage et mis à jour notre base de données de quiz avec de nouvelles questions.

Connectez-vous maintenant pour explorer ces sujets et poursuivre votre parcours d'apprentissage !

Bon apprentissage !

L'équipe Mindsnacks
"""
        },
        
        'es': {
            'subject': f'Tu Resumen Semanal de Aprendizaje - {date}',
            'body': f"""
Hola {username},

Aquí está tu resumen semanal de Mindsnacks para el {date}:

**Temas Tendencia Esta Semana:**
{top_topics_formatted}

**Recomendado Solo Para Ti:**
{recommended_topics_formatted}

También hemos añadido nuevo contenido a nuestras Rutas de Aprendizaje y actualizado nuestra base de datos de cuestionarios con nuevas preguntas.

¡Inicia sesión ahora para explorar estos temas y continuar tu viaje de aprendizaje!

¡Feliz aprendizaje!

El equipo de Mindsnacks
"""
        },
        
        'de': {
            'subject': f'Dein Wöchentlicher Lern-Digest - {date}',
            'body': f"""
Hallo {username},

Hier ist dein wöchentlicher Mindsnacks-Digest für den {date}:

**Top-Trendthemen Diese Woche:**
{top_topics_formatted}

**Speziell Für Dich Empfohlen:**
{recommended_topics_formatted}

Wir haben auch neue Inhalte zu unseren Lernpfaden hinzugefügt und unsere Quiz-Datenbank mit neuen Fragen aktualisiert.

Melde dich jetzt an, um diese Themen zu erkunden und deine Lernreise fortzusetzen!

Frohes Lernen!

Das Mindsnacks-Team
"""
        }
    }
    
    # Default to English if language not available
    return templates.get(language, templates['en'])