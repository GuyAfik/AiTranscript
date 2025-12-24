"""
Audio Transcription Service

This service handles audio file processing and transcription using local Whisper model.

Responsibilities:
- Accept multiple audio formats (mp3, wav, m4a, ogg, flac)
- Convert audio to compatible format if needed
- Load and manage Whisper model
- Transcribe audio to text
- Handle temporary file storage
- Clean up temporary files

Model Size Options:
- tiny: Fastest, least accurate (~1GB RAM)
- base: Balanced (default) (~1GB RAM)
- small: Better accuracy (~2GB RAM)
- medium: High accuracy (~5GB RAM)
- large: Best accuracy (~10GB RAM)

Dependencies:
- openai-whisper
- ffmpeg-python (for audio format conversion)
- pydub (audio processing)
"""

import logging
from typing import Union, Optional, Dict, Any
from pathlib import Path
import whisper
from src.utils.validators import validate_audio_file
from src.utils.file_handler import temp_file_context, get_audio_duration

logger = logging.getLogger(__name__)


class AudioTranscriptionService:
    """
    Service for transcribing audio files and live recordings using local Whisper model.

    This service manages the Whisper model lifecycle and provides methods for
    transcribing various audio formats.
    """

    # Class-level model cache to avoid reloading
    _model_cache: Dict[str, Any] = {}

    def __init__(self, model_size: str = "base", device: str = "cpu") -> None:
        """
        Initialize the audio transcription service.

        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            device: Device to run model on ('cpu' or 'cuda')
        """
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if model_size not in valid_models:
            logger.warning(f"Invalid model size '{model_size}', defaulting to 'base'")
            model_size = "base"

        self.model_size = model_size
        self.device = device
        self.model = None

        logger.info(
            f"Audio transcription service initialized with model: {model_size}, device: {device}"
        )

    def load_model(self) -> Any:
        """
        Load the Whisper model with caching.

        Returns:
            Loaded Whisper model instance

        Raises:
            Exception: If model loading fails
        """
        try:
            # Check if model is already cached
            cache_key = f"{self.model_size}_{self.device}"
            if cache_key in self._model_cache:
                logger.info(f"Using cached Whisper model: {self.model_size}")
                self.model = self._model_cache[cache_key]
                return self.model

            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")

            # Load model
            self.model = whisper.load_model(self.model_size, device=self.device)

            # Cache the model
            self._model_cache[cache_key] = self.model

            logger.info(f"Successfully loaded Whisper model: {self.model_size}")
            return self.model

        except Exception as e:
            error_msg = f"Failed to load Whisper model '{self.model_size}': {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def transcribe_file(
        self, audio_file: Union[str, Path], language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.

        Args:
            audio_file: Path to audio file
            language: Language code (None for auto-detect)

        Returns:
            Dictionary containing:
                - text: Full transcription
                - language: Detected language
                - segments: Timestamped segments
                - duration: Audio duration

        Raises:
            Exception: If transcription fails
        """
        try:
            file_path = str(audio_file)

            # Validate audio file
            is_valid, error_msg = validate_audio_file(file_path)
            if not is_valid:
                raise ValueError(f"Invalid audio file: {error_msg}")

            logger.info(f"Transcribing audio file: {file_path}")

            # Load model if not already loaded
            if self.model is None:
                self.load_model()

            # Transcribe with Whisper
            transcribe_options = {"fp16": False if self.device == "cpu" else True, "verbose": False}

            if language:
                transcribe_options["language"] = language

            # Use faster-whisper if available for better performance on large files
            # For now, we stick to standard whisper but we could optimize here
            result = self.model.transcribe(file_path, **transcribe_options)

            # Get audio duration
            try:
                duration = get_audio_duration(file_path)
            except Exception as e:
                logger.warning(f"Could not get audio duration: {e}")
                # Fallback to last segment time if available
                duration = 0.0
                if result.get("segments"):
                    last_segment = result["segments"][-1]
                    duration = last_segment.get("end", 0.0)

            # Format response
            response = {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": duration,
            }

            logger.info(
                f"Transcription complete: {len(response['text'])} characters, language: {response['language']}"
            )
            return response

        except Exception as e:
            error_msg = f"Error transcribing audio file {audio_file}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def transcribe_audio_data(
        self, audio_bytes: bytes, language: Optional[str] = None, file_extension: str = ".wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio from bytes data.

        Args:
            audio_bytes: Audio data as bytes
            language: Language code (None for auto-detect)
            file_extension: File extension for temporary file (default: .wav)

        Returns:
            Dictionary containing transcription results

        Raises:
            Exception: If transcription fails
        """
        try:
            logger.info("Transcribing audio from bytes data")

            # Use context manager for temporary file
            with temp_file_context(
                audio_bytes, filename=f"audio{file_extension}"
            ) as temp_file_path:
                # Transcribe the temporary file
                result = self.transcribe_file(temp_file_path, language)
                return result

        except Exception as e:
            error_msg = f"Error transcribing audio data: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_size": self.model_size,
            "device": self.device,
            "loaded": self.model is not None,
            "cached": f"{self.model_size}_{self.device}" in self._model_cache,
        }

    @classmethod
    def clear_model_cache(cls) -> None:
        """
        Clear the model cache to free up memory.
        """
        cls._model_cache.clear()
        logger.info("Cleared Whisper model cache")
