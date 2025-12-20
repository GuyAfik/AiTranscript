"""
YouTube Transcript Service

This service handles extraction of transcripts from YouTube videos using video URLs.

Responsibilities:
- Validate YouTube URL format
- Extract video ID from URL
- Fetch transcript using youtube-transcript-api
- Handle multiple language transcripts
- Error handling for unavailable transcripts

Dependencies:
- youtube-transcript-api
"""

import logging
from typing import Optional, List, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    NotTranslatable,
    TranslationLanguageNotAvailable,
    YouTubeRequestFailed
)
from src.utils.validators import validate_youtube_url, extract_video_id_from_url

logger = logging.getLogger(__name__)


class YouTubeService:
    """
    Service for extracting transcripts from YouTube videos.
    
    This service provides methods to validate YouTube URLs, extract video IDs,
    and fetch transcripts in multiple languages.
    """
    
    def __init__(self) -> None:
        """Initialize the YouTube service."""
        logger.info("YouTube service initialized")
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID string
            
        Raises:
            ValueError: If URL is invalid or video ID cannot be extracted
        """
        if not validate_youtube_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        video_id = extract_video_id_from_url(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")
        
        logger.info(f"Extracted video ID: {video_id}")
        return video_id
    
    def get_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fetch transcript from YouTube video.
        
        Args:
            video_id: YouTube video ID
            languages: Preferred languages (default: ['en'])
            
        Returns:
            Dictionary containing:
                - text: Full transcript text
                - language: Detected language
                - duration: Video duration in seconds
                - segments: Individual transcript segments
                
        Raises:
            Exception: If transcript is unavailable or fetch fails
        """
        if languages is None:
            languages = ['en']
        
        try:
            logger.info(f"Fetching transcript for video ID: {video_id}")
            
            # Fetch transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get transcript in preferred languages
            transcript = None
            detected_language = None
            
            try:
                # Try to find manually created transcript first
                for lang in languages:
                    try:
                        transcript = transcript_list.find_manually_created_transcript([lang])
                        detected_language = lang
                        logger.info(f"Found manually created transcript in language: {lang}")
                        break
                    except NoTranscriptFound:
                        continue
                
                # If no manual transcript, try generated
                if transcript is None:
                    for lang in languages:
                        try:
                            transcript = transcript_list.find_generated_transcript([lang])
                            detected_language = lang
                            logger.info(f"Found generated transcript in language: {lang}")
                            break
                        except NoTranscriptFound:
                            continue
                
                # If still no transcript, get any available
                if transcript is None:
                    transcript = transcript_list.find_transcript(languages)
                    detected_language = transcript.language_code
                    logger.info(f"Found transcript in language: {detected_language}")
                    
            except NoTranscriptFound:
                raise Exception(f"No transcript found for video {video_id} in languages: {languages}")
            
            # Fetch the actual transcript data
            transcript_data = transcript.fetch()
            
            # Combine all text segments
            full_text = " ".join([entry['text'] for entry in transcript_data])
            
            # Calculate duration (last segment's start time + duration)
            duration = 0.0
            if transcript_data:
                last_segment = transcript_data[-1]
                duration = last_segment['start'] + last_segment.get('duration', 0)
            
            result = {
                'text': full_text,
                'language': detected_language or transcript.language_code,
                'duration': duration,
                'segments': transcript_data
            }
            
            logger.info(f"Successfully fetched transcript: {len(full_text)} characters, {len(transcript_data)} segments")
            return result
            
        except TranscriptsDisabled:
            error_msg = f"Transcripts are disabled for video: {video_id}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except VideoUnavailable:
            error_msg = f"Video is unavailable: {video_id}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except YouTubeRequestFailed as e:
            error_msg = f"YouTube request failed: {str(e)}. Please try again later."
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except NoTranscriptFound:
            error_msg = f"No transcript available for video: {video_id}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Error fetching transcript for video {video_id}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_available_languages(self, video_id: str) -> List[str]:
        """
        Get list of available transcript languages for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of available language codes
            
        Raises:
            Exception: If video not found or languages cannot be retrieved
        """
        try:
            logger.info(f"Fetching available languages for video: {video_id}")
            
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Get all available language codes
            languages = []
            for transcript in transcript_list:
                languages.append(transcript.language_code)
            
            logger.info(f"Available languages for {video_id}: {languages}")
            return languages
            
        except TranscriptsDisabled:
            error_msg = f"Transcripts are disabled for video: {video_id}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except VideoUnavailable:
            error_msg = f"Video is unavailable: {video_id}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Error fetching available languages for video {video_id}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_transcript_from_url(
        self,
        url: str,
        languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to get transcript directly from URL.
        
        Args:
            url: YouTube video URL
            languages: Preferred languages (default: ['en'])
            
        Returns:
            Dictionary containing transcript data
            
        Raises:
            Exception: If URL is invalid or transcript cannot be fetched
        """
        video_id = self.extract_video_id(url)
        return self.get_transcript(video_id, languages)