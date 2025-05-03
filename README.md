# Mindsnacks: Spotify for Learning

## Project Description

Mindsnacks is an innovative web application designed to deliver customized, 5-minute audio learning snippets, akin to a "Spotify for Learning." Users can create personalized playlists by entering topics of interest, explore trending topics, or discover new subjects across various categories. The app supports multiple languages (French, English, Spanish, German, Italian, Japanese, Chinese, and Arabic) and uses text-to-speech (TTS) technology to convert educational content into engaging audio files. Built with Streamlit, the application leverages the Grok API for content generation and Edge TTS for high-quality audio output, with a fallback to gTTS for Arabic.

The app is currently deployed and accessible at [https://has1elb-mindsnacks-app-kvbioi.streamlit.app/](https://has1elb-mindsnacks-app-kvbioi.streamlit.app/).

## Features

* **Custom Playlist Creation** : Users can input topics to generate audio snippets tailored to their interests.
* **Multilingual Support** : Content and interface available in 8 languages with RTL support for Arabic.
* **Discover Tab** : Offers curated trending topics and categorized subjects for exploration.
* **Recommendation Engine** : Suggests new topics based on user history.
* **Audio Download** : Users can download generated audio files in MP3 format.
* **Responsive UI** : Streamlit-based interface with a Spotify-inspired dark theme and intuitive navigation.

## Setup Instructions

To run the Mindsnacks application locally, follow these steps:

1. **Clone the Repository** :

```bash
   git clone https://github.com/HAS1ELB/MindSnacks
   cd MindSnacks
```

1. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install Dependencies** : Install the required packages listed in `requirements.txt`:

```bash
   pip install -r requirements.txt
```

1. **Configure Environment Variables** : Create a `.env` file in the project root and add your Grok API key:

```bash
   GROQ_API_KEY=your_grok_api_key
```

   Obtain the API key from [https://x.ai/api](https://x.ai/api).

1. **Run the Application** : Launch the Streamlit app:

```bash
   streamlit run app.py
```

   The app will be accessible at `http://localhost:8501` in your browser.

1. **Directory Setup** : Ensure the `static/audio` and `translations` directories exist. These are automatically created if missing, as specified in `config.py`.

## List of Dependencies

The project dependencies are listed in `requirements.txt`:

```
streamlit==1.28.0
groq>=0.9.0
python-dotenv==1.0.0
requests==2.31.0
pydub==0.25.1
numpy==1.26.0
gtts==2.3.2
elevenlabs==1.0.0
edge-tts
pyyaml==6.0.1
num2words==0.5.14
```

## Environment Files

* `.env`: Stores sensitive information like `GROQ_API_KEY`. Ensure this file is not committed to version control (add to `.gitignore`).
* **Directory Structure** :

```
  has1elb-mindsnacks/
  ├── app.py
  ├── config.py
  ├── requirements.txt
  ├── README.md
  ├── static/
  │   └── css/
  │       └── style.css
  ├── templates/
  │   ├── prompt_templates.py
  │   └── recommendation_templates.py
  ├── translations/
  │   ├── already_added.yml
  │   ├── ar.yml
  │   ├── de.yml
  │   ├── en.yml
  │   ├── es.yml
  │   ├── fr.yml
  │   ├── it.yml
  │   ├── ja.yml
  │   ├── playlist_already_generated.yml
  │   └── zh.yml
  └── utils/
      ├── __init__.py
      ├── audio_utils.py
      ├── data_utils.py
      ├── language_utils.py
      └── llm_utils.py
```

## Deployment

The Mindsnacks application is deployed and publicly accessible at the following URL:

 **Live Application** : [https://has1elb-mindsnacks-app-kvbioi.streamlit.app/](https://has1elb-mindsnacks-app-kvbioi.streamlit.app/)

The app is hosted on Streamlit Cloud, ensuring reliable access for users. Any updates to the codebase require redeployment to reflect changes on the live site.

## Usage

1. **Select Language** : Choose your preferred language from the sidebar.
2. **Create Playlist** : In the "Create Playlist" tab, enter topics (one per line) and select the duration per topic (3-10 minutes). Click "Generate my Playlist" to create audio snippets.
3. **Explore Library** : The "My Library" tab displays your generated playlists with options to play, view text, or download audio.
4. **Discover Topics** : The "Discover" tab offers trending topics and categorized subjects to add to your playlist.

## Notes

* **Arabic Support** : Uses Edge TTS with `ar-SA-ZariyahNeural` voice and falls back to gTTS for robust audio generation.
* **Caching** : Translation files are cached in memory to improve performance.
* **Error Handling** : The app includes logging and fallback mechanisms for content generation and audio synthesis failures.
* **Deployment** : The app is hosted on Streamlit Cloud. Local changes require redeployment to update the live version.

## Contributing

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License.

## Contact

For issues or inquiries, please open an issue on the repository or contact the maintainer at [elbahraouihassan54@gmail.com](mailto:elbahraouihassan54@gmail.com)
