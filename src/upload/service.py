"""
Upload Feature Service

This module handles the business logic for the file upload transcription feature.
"""

import logging
from typing import Dict, Any
from src.common.audio_service import AudioTranscriptionService
from src.utils.file_handler import temp_file_context

logger = logging.getLogger(__name__)

def transcribe_uploaded_file(uploaded_file, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process uploaded audio file and transcribe.

    Args:
        uploaded_file: Streamlit UploadedFile object
        settings: User settings dictionary

    Returns:
        Dictionary containing transcription result
    """
    try:
        # Use context manager for temporary file handling
        # The context manager now uses NamedTemporaryFile(delete=True)
        # so the file will be automatically deleted when the context exits
        with temp_file_context(uploaded_file) as temp_file_path:
            logger.info(f"Processing uploaded file in context: {temp_file_path}")

            # Initialize audio transcription service
            audio_service = AudioTranscriptionService(
                model_size=settings["model_size"], device="cpu"  # Use CPU for compatibility
            )

            # Transcribe audio
            result = audio_service.transcribe_file(temp_file_path, language=settings["language"])
            
            return result

    except Exception as e:
        logger.error(f"Error processing audio file: {e}")
        raise e