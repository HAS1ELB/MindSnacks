import os
import sys
import logging
import unittest
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MindsnacksAppTest(unittest.TestCase):
    """Test case for Mindsnacks v2 app"""
    
    def setUp(self):
        """Set up test environment"""
        # Ensure we're in the correct directory
        self.base_dir = Path(__file__).parent
        self.static_dir = self.base_dir / "static"
        self.test_directories = [
            self.static_dir / "audio",
            self.static_dir / "cache" / "llm",
            self.static_dir / "cache" / "audio",
            self.static_dir / "exports",
            self.static_dir / "users",
        ]
    
    def test_directory_structure(self):
        """Test that the necessary directories exist"""
        # Check each required directory
        for directory in self.test_directories:
            self.assertTrue(
                directory.exists() or directory.parent.exists(),
                f"Directory {directory} does not exist and could not be created"
            )
    
    def test_app_imports(self):
        """Test that all required modules can be imported"""
        try:
            import streamlit
            import pandas
            import plotly
            import groq
            import pydub
            import asyncio
            import gtts
            import yaml
            import langchain
            logger.info("All required libraries can be imported")
        except ImportError as e:
            self.fail(f"Failed to import required library: {e}")
    
    def test_config_file(self):
        """Test that the config file exists and can be imported"""
        try:
            import config
            logger.info("Config file loaded successfully")
            
            # Check essential config variables
            self.assertIsNotNone(getattr(config, "APP_TITLE", None))
            self.assertIsNotNone(getattr(config, "APP_VERSION", None))
            self.assertIsNotNone(getattr(config, "DEFAULT_LANGUAGE", None))
            self.assertIsNotNone(getattr(config, "LLM_MODELS", None))
        except Exception as e:
            self.fail(f"Failed to load config: {e}")
    
    def test_page_files(self):
        """Test that all required page files exist"""
        required_pages = [
            "discover.py",
            "library.py",
            "quiz.py",
            "create.py",
            "settings.py",
            "profile.py"
        ]
        
        pages_dir = self.base_dir / "pages"
        
        for page in required_pages:
            page_path = pages_dir / page
            self.assertTrue(
                page_path.exists(),
                f"Page file {page} does not exist"
            )
    
    def test_main_app_file(self):
        """Test that the main app.py file exists"""
        app_file = self.base_dir / "app.py"
        self.assertTrue(
            app_file.exists(),
            "Main app.py file does not exist"
        )
    
    def test_translations(self):
        """Test that the translation files exist"""
        translations_dir = self.base_dir / "translations"
        
        # Check for essential language files
        essential_languages = ["en.yml", "fr.yml", "es.yml"]
        
        for lang_file in essential_languages:
            lang_path = translations_dir / lang_file
            self.assertTrue(
                lang_path.exists(),
                f"Translation file {lang_file} does not exist"
            )

if __name__ == "__main__":
    unittest.main()