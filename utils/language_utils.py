import os
import yaml
import json
from config import TRANSLATIONS_DIR, AVAILABLE_LANGUAGES

# Cache pour les traductions chargées
_translations_cache = {}

def _create_default_translations():
    """
    Crée les fichiers de traduction par défaut s'ils n'existent pas.
    """
    translations = {
        'fr': {
            'app_title': 'Spotify for Learning',
            'app_description': 'Générateur de snippets d\'apprentissage personnalisés de 5 minutes',
            'create_playlist_tab': 'Créer une Playlist',
            'my_library_tab': 'Ma Bibliothèque',
            'discover_tab': 'Découvrir',
            'create_custom_playlist': 'Créer votre Playlist Personnalisée',
            'enter_topics': 'Entrez les sujets que vous souhaitez apprendre (un par ligne):',
            'topics_example': 'Exemple:\n- L\'histoire de la Révolution française\n- Comment fonctionne la photosynthèse\n- Les bases de la cryptographie\n...',
            'duration_per_topic': 'Durée par sujet (minutes):',
            'estimated_total_duration': 'Durée totale estimée',
            'minutes': 'minutes',
            'generate_playlist': 'Générer ma Playlist',
            'generating_custom_playlist': 'Génération de votre playlist personnalisée...',
            'enter_at_least_one_topic': 'Veuillez entrer au moins un sujet.',
            'you_might_also_like': 'Vous pourriez aussi être intéressé par:',
            'add_to_list': 'Ajouter à ma liste',
            'my_learning_library': 'Ma Bibliothèque d\'Apprentissage',
            'no_playlist_yet': 'Vous n\'avez pas encore créé de playlist. Allez dans l\'onglet \'Créer une Playlist\' pour commencer.',
            'discover_new_topics': 'Découvrir de Nouveaux Sujets',
            'add': 'Ajouter',
            'generating_snippet': 'Génération du snippet',
            'added_to_playlist': 'ajouté à votre playlist!',
            'your_learning_playlist': 'Votre Playlist d\'Apprentissage',
            'view_text_content': 'Voir le contenu textuel',
            'download': 'Télécharger',
            'converting_to_audio': 'Conversion en audio pour',
            'playlist_generated_success': 'Playlist générée avec succès!',
            'language': 'Langue',
            'select_language': 'Sélectionner une langue'
        },
        'en': {
            'app_title': 'Spotify for Learning',
            'app_description': 'Generator of 5-minute customized learning snippets',
            'create_playlist_tab': 'Create Playlist',
            'my_library_tab': 'My Library',
            'discover_tab': 'Discover',
            'create_custom_playlist': 'Create Your Custom Playlist',
            'enter_topics': 'Enter the topics you want to learn about (one per line):',
            'topics_example': 'Example:\n- History of the French Revolution\n- How photosynthesis works\n- Basics of cryptography\n...',
            'duration_per_topic': 'Duration per topic (minutes):',
            'estimated_total_duration': 'Estimated total duration',
            'minutes': 'minutes',
            'generate_playlist': 'Generate my Playlist',
            'generating_custom_playlist': 'Generating your custom playlist...',
            'enter_at_least_one_topic': 'Please enter at least one topic.',
            'you_might_also_like': 'You might also be interested in:',
            'add_to_list': 'Add to my list',
            'my_learning_library': 'My Learning Library',
            'no_playlist_yet': 'You haven\'t created a playlist yet. Go to the \'Create Playlist\' tab to get started.',
            'discover_new_topics': 'Discover New Topics',
            'add': 'Add',
            'generating_snippet': 'Generating snippet for',
            'added_to_playlist': 'added to your playlist!',
            'your_learning_playlist': 'Your Learning Playlist',
            'view_text_content': 'View text content',
            'download': 'Download',
            'converting_to_audio': 'Converting to audio for',
            'playlist_generated_success': 'Playlist generated successfully!',
            'language': 'Language',
            'select_language': 'Select a language'
        },
        'es': {
            'app_title': 'Spotify para Aprender',
            'app_description': 'Generador de fragmentos de aprendizaje personalizados de 5 minutos',
            'create_playlist_tab': 'Crear Lista',
            'my_library_tab': 'Mi Biblioteca',
            'discover_tab': 'Descubrir',
            'create_custom_playlist': 'Crea Tu Lista Personalizada',
            'enter_topics': 'Ingresa los temas que quieres aprender (uno por línea):',
            'topics_example': 'Ejemplo:\n- Historia de la Revolución Francesa\n- Cómo funciona la fotosíntesis\n- Fundamentos de criptografía\n...',
            'duration_per_topic': 'Duración por tema (minutos):',
            'estimated_total_duration': 'Duración total estimada',
            'minutes': 'minutos',
            'generate_playlist': 'Generar mi Lista',
            'generating_custom_playlist': 'Generando tu lista personalizada...',
            'enter_at_least_one_topic': 'Por favor ingresa al menos un tema.',
            'you_might_also_like': 'También podría interesarte:',
            'add_to_list': 'Añadir a mi lista',
            'my_learning_library': 'Mi Biblioteca de Aprendizaje',
            'no_playlist_yet': 'Aún no has creado una lista. Ve a la pestaña \'Crear Lista\' para comenzar.',
            'discover_new_topics': 'Descubrir Nuevos Temas',
            'add': 'Añadir',
            'generating_snippet': 'Generando fragmento para',
            'added_to_playlist': 'añadido a tu lista!',
            'your_learning_playlist': 'Tu Lista de Aprendizaje',
            'view_text_content': 'Ver contenido textual',
            'download': 'Descargar',
            'converting_to_audio': 'Convirtiendo a audio para',
            'playlist_generated_success': '¡Lista generada con éxito!',
            'language': 'Idioma',
            'select_language': 'Seleccionar un idioma'
        },
        'de': {
            'app_title': 'Spotify zum Lernen',
            'app_description': 'Generator für 5-minütige personalisierte Lernschnipsel',
            'create_playlist_tab': 'Playlist erstellen',
            'my_library_tab': 'Meine Bibliothek',
            'discover_tab': 'Entdecken',
            'create_custom_playlist': 'Erstellen Sie Ihre benutzerdefinierte Playlist',
            'enter_topics': 'Geben Sie die Themen ein, über die Sie lernen möchten (eines pro Zeile):',
            'topics_example': 'Beispiel:\n- Geschichte der Französischen Revolution\n- Wie die Photosynthese funktioniert\n- Grundlagen der Kryptographie\n...',
            'duration_per_topic': 'Dauer pro Thema (Minuten):',
            'estimated_total_duration': 'Geschätzte Gesamtdauer',
            'minutes': 'Minuten',
            'generate_playlist': 'Meine Playlist generieren',
            'generating_custom_playlist': 'Ihre benutzerdefinierte Playlist wird generiert...',
            'enter_at_least_one_topic': 'Bitte geben Sie mindestens ein Thema ein.',
            'you_might_also_like': 'Sie könnten auch interessiert sein an:',
            'add_to_list': 'Zu meiner Liste hinzufügen',
            'my_learning_library': 'Meine Lernbibliothek',
            'no_playlist_yet': 'Sie haben noch keine Playlist erstellt. Gehen Sie zum Tab \'Playlist erstellen\', um zu beginnen.',
            'discover_new_topics': 'Neue Themen entdecken',
            'add': 'Hinzufügen',
            'generating_snippet': 'Generierung des Snippets für',
            'added_to_playlist': 'zu Ihrer Playlist hinzugefügt!',
            'your_learning_playlist': 'Ihre Lern-Playlist',
            'view_text_content': 'Textinhalt anzeigen',
            'download': 'Herunterladen',
            'converting_to_audio': 'Konvertierung zu Audio für',
            'playlist_generated_success': 'Playlist erfolgreich generiert!',
            'language': 'Sprache',
            'select_language': 'Sprache auswählen'
        },
        'it': {
            'app_title': 'Spotify per l\'Apprendimento',
            'app_description': 'Generatore di snippet di apprendimento personalizzati di 5 minuti',
            'create_playlist_tab': 'Crea Playlist',
            'my_library_tab': 'La Mia Libreria',
            'discover_tab': 'Scopri',
            'create_custom_playlist': 'Crea La Tua Playlist Personalizzata',
            'enter_topics': 'Inserisci gli argomenti che vuoi imparare (uno per riga):',
            'topics_example': 'Esempio:\n- Storia della Rivoluzione Francese\n- Come funziona la fotosintesi\n- Basi della crittografia\n...',
            'duration_per_topic': 'Durata per argomento (minuti):',
            'estimated_total_duration': 'Durata totale stimata',
            'minutes': 'minuti',
            'generate_playlist': 'Genera la mia Playlist',
            'generating_custom_playlist': 'Generazione della tua playlist personalizzata...',
            'enter_at_least_one_topic': 'Inserisci almeno un argomento.',
            'you_might_also_like': 'Potrebbe interessarti anche:',
            'add_to_list': 'Aggiungi alla mia lista',
            'my_learning_library': 'La Mia Libreria di Apprendimento',
            'no_playlist_yet': 'Non hai ancora creato una playlist. Vai alla scheda \'Crea Playlist\' per iniziare.',
            'discover_new_topics': 'Scopri Nuovi Argomenti',
            'add': 'Aggiungi',
            'generating_snippet': 'Generazione dello snippet per',
            'added_to_playlist': 'aggiunto alla tua playlist!',
            'your_learning_playlist': 'La Tua Playlist di Apprendimento',
            'view_text_content': 'Visualizza contenuto testuale',
            'download': 'Scarica',
            'converting_to_audio': 'Conversione in audio per',
            'playlist_generated_success': 'Playlist generata con successo!',
            'language': 'Lingua',
            'select_language': 'Seleziona una lingua'
        },
        'ja': {
            'app_title': '学習のためのSpotify',
            'app_description': '5分間のカスタマイズされた学習スニペットジェネレータ',
            'create_playlist_tab': 'プレイリストを作成',
            'my_library_tab': 'マイライブラリ',
            'discover_tab': '発見',
            'create_custom_playlist': 'カスタムプレイリストを作成',
            'enter_topics': '学習したいトピックを入力してください（1行に1つ）:',
            'topics_example': '例:\n- フランス革命の歴史\n- 光合成のしくみ\n- 暗号化の基礎\n...',
            'duration_per_topic': 'トピックあたりの時間（分）:',
            'estimated_total_duration': '推定合計時間',
            'minutes': '分',
            'generate_playlist': 'プレイリストを生成',
            'generating_custom_playlist': 'カスタムプレイリストを生成中...',
            'enter_at_least_one_topic': '少なくとも1つのトピックを入力してください。',
            'you_might_also_like': 'こちらにも興味があるかもしれません:',
            'add_to_list': 'リストに追加',
            'my_learning_library': '学習ライブラリ',
            'no_playlist_yet': 'まだプレイリストを作成していません。「プレイリストを作成」タブに移動して開始してください。',
            'discover_new_topics': '新しいトピックを発見',
            'add': '追加',
            'generating_snippet': 'スニペットを生成中',
            'added_to_playlist': 'プレイリストに追加されました！',
            'your_learning_playlist': '学習プレイリスト',
            'view_text_content': 'テキスト内容を表示',
            'download': 'ダウンロード',
            'converting_to_audio': '音声に変換中',
            'playlist_generated_success': 'プレイリストが正常に生成されました！',
            'language': '言語',
            'select_language': '言語を選択'
        },
        'zh': {
            'app_title': '学习版Spotify',
            'app_description': '5分钟定制学习片段生成器',
            'create_playlist_tab': '创建播放列表',
            'my_library_tab': '我的库',
            'discover_tab': '发现',
            'create_custom_playlist': '创建自定义播放列表',
            'enter_topics': '输入您想学习的主题（每行一个）：',
            'topics_example': '示例：\n- 法国大革命的历史\n- 光合作用的原理\n- 密码学基础\n...',
            'duration_per_topic': '每个主题的时长（分钟）：',
            'estimated_total_duration': '估计总时长',
            'minutes': '分钟',
            'generate_playlist': '生成我的播放列表',
            'generating_custom_playlist': '正在生成您的自定义播放列表...',
            'enter_at_least_one_topic': '请至少输入一个主题。',
            'you_might_also_like': '您可能还对以下内容感兴趣：',
            'add_to_list': '添加到我的列表',
            'my_learning_library': '我的学习库',
            'no_playlist_yet': '您尚未创建播放列表。前往"创建播放列表"选项卡开始。',
            'discover_new_topics': '发现新主题',
            'add': '添加',
            'generating_snippet': '正在生成片段',
            'added_to_playlist': '已添加到您的播放列表！',
            'your_learning_playlist': '您的学习播放列表',
            'view_text_content': '查看文本内容',
            'download': '下载',
            'converting_to_audio': '正在转换为音频',
            'playlist_generated_success': '播放列表生成成功！',
            'language': '语言',
            'select_language': '选择语言'
        },
    'playlist_already_generated': {
        'en': 'Playlist already generated. Please clear or modify the input.',
        'fr': 'Playlist déjà généré. Veuillez effacer ou modifier l\'entrée.',
        'es': 'Lista de reproducción ya generada. Por favor, borra o modifica la entrada.',
        'ar': 'تم إنشاء قائمة التشغيل بالفعل. يرجى مسح أو تعديل الإدخال.'
    },
    'already_added': {
        'en': 'already added to playlist.',
        'fr': 'déjà ajouté à la playlist.',
        'es': 'ya añadido a la lista de reproducción.',
        'ar': 'تمت إضافته بالفعل إلى قائمة التشغيل.'
    }    
    }
    
    for lang_code, translations_dict in translations.items():
        lang_file = os.path.join(TRANSLATIONS_DIR, f"{lang_code}.yml")
        if not os.path.exists(lang_file):
            with open(lang_file, 'w', encoding='utf-8') as f:
                yaml.dump(translations_dict, f, default_flow_style=False, allow_unicode=True)

def _load_translations(lang_code):
    """
    Charge les traductions pour une langue donnée.
    """
    if lang_code in _translations_cache:
        return _translations_cache[lang_code]
    
    try:
        lang_file = os.path.join(TRANSLATIONS_DIR, f"{lang_code}.yml")
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as f:
                translations = yaml.safe_load(f)
                _translations_cache[lang_code] = translations
                return translations
    except Exception as e:
        print(f"Erreur lors du chargement des traductions pour {lang_code}: {e}")
    
    # Fallback aux traductions en anglais si la langue demandée n'existe pas
    if lang_code != 'en':
        return _load_translations('en')
    
    return {}

def get_translation(key, lang_code='fr'):
    """
    Récupère une traduction pour une clé donnée.
    """
    translations = _load_translations(lang_code)
    return translations.get(key, key)

def set_language(lang_code):
    """
    Configure la langue actuelle de l'application.
    """
    if lang_code not in AVAILABLE_LANGUAGES:
        lang_code = 'fr'  # Langue par défaut
        
    # S'assurer que les fichiers de traduction existent
    _create_default_translations()
    
    # Précharger les traductions
    _load_translations(lang_code)
    
    return lang_code