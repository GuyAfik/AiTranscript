"""
YouTube Feature Service

This module handles the business logic for the YouTube transcription feature.
"""

import logging
from typing import Dict, Any
from src.youtube.provider import YouTubeService
from src.common.audio_service import AudioTranscriptionService

logger = logging.getLogger(__name__)


def get_youtube_transcript(url: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process YouTube URL and extract transcript.

    Args:
        url: YouTube video URL
        settings: User settings dictionary

    Returns:
        Dictionary containing transcript result
    """
    logger.info(f"Processing YouTube URL: {url}")

    # Initialize audio service for fallback
    audio_service = AudioTranscriptionService(model_size=settings["model_size"], device="cpu")

    # Initialize YouTube service with audio service for fallback
    youtube_service = YouTubeService(audio_service=audio_service)

    # Get transcript
    languages = [settings["language"]] if settings["language"] else ["en"]
    
    # Extract time range settings
    start_time = settings.get("start_time")
    end_time = settings.get("end_time")
    
    result = youtube_service.get_transcript_from_url(
        url,
        languages,
        start_time=start_time,
        end_time=end_time
    )

    return result
