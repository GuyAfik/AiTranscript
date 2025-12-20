"""
Upload Feature Service

This module handles the business logic for the file upload transcription feature.
"""

import logging
from typing import Dict, Any
from src.common.audio_service import AudioTranscriptionService
from src.utils.file_handler import save_uploaded_file, cleanup_temp_files

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
    temp_file_path = None
    try:
        # Save uploaded file to temp location
        temp_file_path = save_uploaded_file(uploaded_file)
        logger.info(f"Saved uploaded file: {temp_file_path}")

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
    finally:
        # Clean up temporary file
        if temp_file_path:
            try:
                cleanup_temp_files(temp_file_path)
            except Exception as e:
                logger.warning(f"Error cleaning up temp file: {e}")