"""
Recording Feature Service

This module handles the business logic for the voice recording transcription feature.
"""

import logging
from typing import Dict, Any
from src.common.audio_service import AudioTranscriptionService

logger = logging.getLogger(__name__)


def transcribe_recording(audio_bytes: bytes, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process recorded audio and transcribe.

    Args:
        audio_bytes: Audio data as bytes
        settings: User settings dictionary

    Returns:
        Dictionary containing transcription result
    """
    try:
        # Initialize audio transcription service
        audio_service = AudioTranscriptionService(model_size=settings["model_size"], device="cpu")

        # Transcribe audio bytes
        result = audio_service.transcribe_audio_data(
            audio_bytes, language=settings["language"], file_extension=".wav"
        )

        return result

    except Exception as e:
        logger.error(f"Error processing audio recording: {e}")
        raise e
