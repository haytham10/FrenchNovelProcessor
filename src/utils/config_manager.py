"""
Configuration Manager
Handles loading and saving configuration settings
"""

import configparser
import os
from typing import Optional


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: str = "config.ini"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to config file
        """
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        
        # Create default config if doesn't exist
        if not os.path.exists(config_path):
            self.create_default_config()
        
        self.load_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config['OpenAI'] = {
            'api_key': ''
        }
        
        self.config['Gemini'] = {
            'gemini_api_key': ''
        }
        
        self.config['Processing'] = {
            'default_word_limit': '8',
            'processing_mode': 'ai_rewrite',
            'use_gemini_dev': 'false'
        }
        
        self.config['Output'] = {
            'show_original_sentences': 'true',
            'generate_processing_log': 'true'
        }
        
        self.config['GoogleSheets'] = {
            'credentials_file': 'credentials.json'
        }
        
        self.save_config()
    
    def load_config(self):
        """Load configuration from file"""
        self.config.read(self.config_path)
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            self.config.write(f)
    
    def get_api_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        try:
            key = self.config.get('OpenAI', 'api_key', fallback='')
            return key if key else None
        except:
            return None
    
    def set_api_key(self, api_key: str):
        """Set OpenAI API key"""
        if 'OpenAI' not in self.config:
            self.config['OpenAI'] = {}
        self.config['OpenAI']['api_key'] = api_key
        self.save_config()
    
    def get_word_limit(self) -> int:
        """Get default word limit"""
        try:
            return self.config.getint('Processing', 'default_word_limit', fallback=8)
        except:
            return 8
    
    def set_word_limit(self, limit: int):
        """Set default word limit"""
        if 'Processing' not in self.config:
            self.config['Processing'] = {}
        self.config['Processing']['default_word_limit'] = str(limit)
        self.save_config()
    
    def get_processing_mode(self) -> str:
        """Get processing mode"""
        try:
            return self.config.get('Processing', 'processing_mode', fallback='ai_rewrite')
        except:
            return 'ai_rewrite'
    
    def set_processing_mode(self, mode: str):
        """Set processing mode"""
        if 'Processing' not in self.config:
            self.config['Processing'] = {}
        self.config['Processing']['processing_mode'] = mode
        self.save_config()
    
    def get_show_original(self) -> bool:
        """Get show original sentences setting"""
        try:
            return self.config.getboolean('Output', 'show_original_sentences', fallback=True)
        except:
            return True
    
    def set_show_original(self, show: bool):
        """Set show original sentences setting"""
        if 'Output' not in self.config:
            self.config['Output'] = {}
        self.config['Output']['show_original_sentences'] = str(show).lower()
        self.save_config()
    
    def get_generate_log(self) -> bool:
        """Get generate processing log setting"""
        try:
            return self.config.getboolean('Output', 'generate_processing_log', fallback=True)
        except:
            return True
    
    def set_generate_log(self, generate: bool):
        """Set generate processing log setting"""
        if 'Output' not in self.config:
            self.config['Output'] = {}
        self.config['Output']['generate_processing_log'] = str(generate).lower()
        self.save_config()
    
    def get_credentials_file(self) -> str:
        """Get Google Sheets credentials file path"""
        try:
            return self.config.get('GoogleSheets', 'credentials_file', fallback='credentials.json')
        except:
            return 'credentials.json'
    
    def get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key (development only)"""
        try:
            key = self.config.get('Gemini', 'gemini_api_key', fallback='')
            return key if key else None
        except:
            return None
    
    def set_gemini_api_key(self, api_key: str):
        """Set Gemini API key"""
        if 'Gemini' not in self.config:
            self.config['Gemini'] = {}
        self.config['Gemini']['gemini_api_key'] = api_key
        self.save_config()
    
    def get_use_gemini_dev(self) -> bool:
        """Get use Gemini development flag"""
        try:
            return self.config.getboolean('Processing', 'use_gemini_dev', fallback=False)
        except:
            return False
    
    def set_use_gemini_dev(self, use_gemini: bool):
        """Set use Gemini development flag"""
        if 'Processing' not in self.config:
            self.config['Processing'] = {}
        self.config['Processing']['use_gemini_dev'] = str(use_gemini).lower()
        self.save_config()
    
    def should_use_gemini(self) -> bool:
        """Check if Gemini should be used (has key + flag enabled)"""
        return self.get_use_gemini_dev() and self.get_gemini_api_key() is not None
