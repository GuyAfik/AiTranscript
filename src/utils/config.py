"""
Configuration Management

This module handles loading and validating configuration from environment variables.

Responsibilities:
- Load environment variables
- Validate configuration
- Provide default values
- Manage API keys and settings
"""

import os
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration manager for AiTranscript application.
    
    Loads configuration from environment variables and provides
    validation and default values.
    """
    
    def __init__(self, env_file: Optional[str] = None) -> None:
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional)
        """
        # Load environment variables from .env file if it exists
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from default location
            env_path = Path.cwd() / '.env'
            if env_path.exists():
                load_dotenv(env_path)
        
        self._load_config()
        logger.info("Configuration loaded successfully")
    
    def _load_config(self) -> None:
        """Load all configuration values from environment variables."""
        
        # OpenAI Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.openai_max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
        
        # Whisper Configuration
        self.whisper_model_size = os.getenv('WHISPER_MODEL_SIZE', 'base')
        self.whisper_device = os.getenv('WHISPER_DEVICE', 'cpu')
        
        # Application Settings
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
        self.temp_file_retention_hours = int(os.getenv('TEMP_FILE_RETENTION_HOURS', '1'))
        self.supported_audio_formats = os.getenv(
            'SUPPORTED_AUDIO_FORMATS',
            'mp3,wav,m4a,ogg,flac'
        ).split(',')
        
        # Streamlit Configuration
        self.streamlit_server_port = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
        self.streamlit_server_address = os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost')
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration values.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate Whisper model size
        valid_models = ['tiny', 'base', 'small', 'medium', 'large']
        if self.whisper_model_size not in valid_models:
            errors.append(
                f"Invalid WHISPER_MODEL_SIZE: {self.whisper_model_size}. "
                f"Must be one of: {', '.join(valid_models)}"
            )
        
        # Validate device
        valid_devices = ['cpu', 'cuda']
        if self.whisper_device not in valid_devices:
            errors.append(
                f"Invalid WHISPER_DEVICE: {self.whisper_device}. "
                f"Must be one of: {', '.join(valid_devices)}"
            )
        
        # Validate file size
        if self.max_file_size_mb <= 0:
            errors.append(f"MAX_FILE_SIZE_MB must be positive, got: {self.max_file_size_mb}")
        
        # Validate retention hours
        if self.temp_file_retention_hours <= 0:
            errors.append(
                f"TEMP_FILE_RETENTION_HOURS must be positive, got: {self.temp_file_retention_hours}"
            )
        
        # Validate max tokens
        if self.openai_max_tokens <= 0:
            errors.append(f"OPENAI_MAX_TOKENS must be positive, got: {self.openai_max_tokens}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Configuration validation passed")
        else:
            logger.error(f"Configuration validation failed: {errors}")
        
        return is_valid, errors
    
    def has_openai_key(self) -> bool:
        """
        Check if OpenAI API key is configured.
        
        Returns:
            True if API key is set, False otherwise
        """
        return bool(self.openai_api_key and self.openai_api_key.strip())
    
    def get_summary(self) -> dict:
        """
        Get a summary of current configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        return {
            'openai_model': self.openai_model,
            'openai_key_set': self.has_openai_key(),
            'whisper_model_size': self.whisper_model_size,
            'whisper_device': self.whisper_device,
            'max_file_size_mb': self.max_file_size_mb,
            'supported_formats': self.supported_audio_formats
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """
    Get the global configuration instance.
    
    Args:
        reload: If True, reload configuration from environment
        
    Returns:
        Config instance
    """
    global _config
    
    if _config is None or reload:
        _config = Config()
    
    return _config