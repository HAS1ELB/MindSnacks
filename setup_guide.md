# Guide de configuration de Mindsnacks v2 dans VSCode

Ce guide vous aidera à créer la structure complète du projet Mindsnacks v2 dans VSCode.

## Étape 1: Créer le dossier principal

1. Ouvrez VSCode
2. Allez dans File > Open Folder
3. Créez un nouveau dossier nommé `improved-mindsnacks-v2`
4. Ouvrez ce dossier

## Étape 2: Créer les fichiers à la racine

Dans le dossier principal, créez les fichiers suivants:

```bash
touch app.py
touch config.py
touch requirements.txt
touch .env.example
touch README.md
```

## Étape 3: Créer la structure de dossiers

Exécutez les commandes suivantes dans le terminal de VSCode pour créer la structure de dossiers:

```bash
# Créer les dossiers principaux
mkdir -p pages utils templates components static models docs

# Créer les sous-dossiers pour static
mkdir -p static/audio static/cache static/css static/js static/img static/analytics static/quiz static/users static/exports static/offline

# Créer les sous-dossiers pour cache
mkdir -p static/cache/llm static/cache/audio

# Créer les sous-dossiers pour img
mkdir -p static/img/animations

# Créer des fichiers __init__.py dans les dossiers appropriés
touch pages/__init__.py utils/__init__.py templates/__init__.py components/__init__.py models/__init__.py

# Créer les fichiers pour les pages
touch pages/analytics.py pages/create.py pages/discover.py pages/library.py pages/profile.py pages/quiz.py pages/settings.py

# Créer les fichiers utils
touch utils/audio_utils.py utils/auth_utils.py utils/cache_utils.py utils/data_utils.py utils/export_utils.py utils/language_utils.py utils/llm_utils.py utils/visualization_utils.py

# Créer les fichiers templates
touch templates/email_templates.py templates/learning_paths.py templates/prompt_templates.py templates/recommendation_templates.py

# Créer les fichiers components
touch components/audio_player.py components/content_cards.py components/notifications.py components/quiz_components.py

# Créer les fichiers CSS
touch static/css/main.css static/css/dark.css static/css/light.css

# Créer les fichiers JS
touch static/js/app.js static/js/audio.js

# Créer les fichiers models
touch models/recommendation.py models/text_analysis.py models/user_patterns.py

# Créer les fichiers docs
touch docs/api.md docs/contributing.md docs/deployment.md docs/user_guide.md

# Créer les fichiers de traduction
touch translations/ar.yml translations/de.yml translations/en.yml translations/es.yml translations/fr.yml translations/it.yml translations/ja.yml translations/ko.yml translations/pt.yml translations/ru.yml translations/zh.yml
```

## Étape 4: Installer les dépendances

Une fois que la structure est créée, vous pouvez installer les dépendances:

1. Créez un environnement virtuel:
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. Installez les dépendances:
```bash
pip install -r requirements.txt
```

## Étape 5: Configuration de l'environnement

1. Copiez le contenu de `.env.example` dans un nouveau fichier `.env`:
```bash
cp .env.example .env
```

2. Modifiez le fichier `.env` pour ajouter vos clés API et autres configurations.

## Arborescence complète du projet

Voici à quoi devrait ressembler votre structure de projet:

```
improved-mindsnacks-v2/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .env
├── README.md
|
├── pages/
│   ├── __init__.py
│   ├── analytics.py
│   ├── create.py
│   ├── discover.py
│   ├── library.py
│   ├── profile.py
│   ├── quiz.py
│   └── settings.py
|
├── utils/
│   ├── __init__.py
│   ├── audio_utils.py
│   ├── auth_utils.py
│   ├── cache_utils.py
│   ├── data_utils.py
│   ├── export_utils.py
│   ├── language_utils.py
│   ├── llm_utils.py
│   └── visualization_utils.py
|
├── templates/
│   ├── __init__.py
│   ├── email_templates.py
│   ├── learning_paths.py
│   ├── prompt_templates.py
│   └── recommendation_templates.py
|
├── components/
│   ├── __init__.py
│   ├── audio_player.py
│   ├── content_cards.py
│   ├── notifications.py
│   └── quiz_components.py
|
├── static/
│   ├── audio/
│   ├── cache/
│   │   ├── llm/
│   │   └── audio/
│   ├── css/
│   │   ├── main.css
│   │   ├── dark.css
│   │   └── light.css
│   ├── js/
│   │   ├── app.js
│   │   └── audio.js
│   ├── img/
│   │   └── animations/
│   ├── analytics/
│   ├── quiz/
│   ├── users/
│   ├── exports/
│   └── offline/
|
├── translations/
│   ├── ar.yml
│   ├── de.yml
│   ├── en.yml
│   ├── es.yml
│   ├── fr.yml
│   ├── it.yml
│   ├── ja.yml
│   ├── ko.yml
│   ├── pt.yml
│   ├── ru.yml
│   └── zh.yml
|
├── models/
│   ├── __init__.py
│   ├── recommendation.py
│   ├── text_analysis.py
│   └── user_patterns.py
|
└── docs/
    ├── api.md
    ├── contributing.md
    ├── deployment.md
    └── user_guide.md
```

## Conseils pour le développement

- Utilisez les extensions VSCode suivantes pour faciliter le développement:
  - Python
  - Streamlit
  - YAML
  - Prettier
  - GitLens
  - Better Comments

- Configurez le linting et le formatage pour maintenir un code propre:
  - Installez `flake8` et `black`: `pip install flake8 black`
  - Créez un fichier `.vscode/settings.json` avec les configurations appropriées

- Utilisez Git pour le contrôle de version:
  ```bash
  git init
  echo "venv/" > .gitignore
  echo ".env" >> .gitignore
  echo "__pycache__/" >> .gitignore
  git add .
  git commit -m "Initial project structure"
  ```

Bonne programmation !