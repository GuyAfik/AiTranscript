"""
YouTube Transcript Service

This service handles extraction of transcripts from YouTube videos using video URLs.

Responsibilities:
- Validate YouTube URL format
- Extract video ID from URL
- Fetch transcript using youtube-transcript-api
- Fallback to audio download + Whisper transcription if transcript unavailable
- Handle multiple language transcripts
- Error handling for unavailable transcripts

Dependencies:
- youtube-transcript-api
- yt-dlp (for audio download fallback)
"""

import logging
import os
import tempfile
from typing import Optional, List, Dict, Any
from pathlib import Path
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
from src.utils.file_handler import cleanup_temp_files

logger = logging.getLogger(__name__)


class YouTubeService:
    """
    Service for extracting transcripts from YouTube videos.
    
    This service provides methods to validate YouTube URLs, extract video IDs,
    and fetch transcripts in multiple languages. If transcript API fails,
    it falls back to downloading audio and using Whisper transcription.
    """
    
    def __init__(self, audio_service=None) -> None:
        """
        Initialize the YouTube service.
        
        Args:
            audio_service: Optional AudioTranscriptionService instance for fallback
        """
        self.audio_service = audio_service
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
    
    def _download_youtube_audio(self, video_id: str, output_path: str) -> str:
        """
        Download YouTube video audio using yt-dlp.
        
        Args:
            video_id: YouTube video ID
            output_path: Directory to save the audio file
            
        Returns:
            Path to the downloaded audio file
            
        Raises:
            Exception: If download fails
        """
        try:
            import yt_dlp
            
            logger.info(f"Downloading audio for video ID: {video_id}")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }
            
            # Download audio
            url = f"https://www.youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
            # Find the downloaded file
            audio_file = os.path.join(output_path, f"{video_id}.mp3")
            
            if not os.path.exists(audio_file):
                raise Exception(f"Downloaded audio file not found: {audio_file}")
            
            logger.info(f"Successfully downloaded audio to: {audio_file}")
            return audio_file
            
        except Exception as e:
            error_msg = f"Failed to download YouTube audio: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _transcribe_with_whisper(
        self,
        video_id: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fallback method: Download YouTube audio and transcribe with Whisper.
        
        Args:
            video_id: YouTube video ID
            language: Language code for transcription
            
        Returns:
            Dictionary containing transcription results
            
        Raises:
            Exception: If audio service is not available or transcription fails
        """
        if self.audio_service is None:
            raise Exception("Audio service not available for fallback transcription")
        
        temp_dir = None
        audio_file = None
        
        try:
            logger.info(f"Using Whisper fallback for video ID: {video_id}")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="youtube_audio_")
            
            # Download audio
            audio_file = self._download_youtube_audio(video_id, temp_dir)
            
            # Transcribe with Whisper
            result = self.audio_service.transcribe_file(audio_file, language)
            
            # Add source information
            result['source'] = 'whisper_fallback'
            result['video_id'] = video_id
            
            logger.info(f"Successfully transcribed with Whisper fallback: {len(result['text'])} characters")
            return result
            
        except Exception as e:
            error_msg = f"Whisper fallback failed for video {video_id}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        finally:
            # Clean up temporary files
            if audio_file and os.path.exists(audio_file):
                try:
                    cleanup_temp_files(audio_file)
                except Exception as e:
                    logger.warning(f"Error cleaning up audio file {audio_file}: {e}")
            
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Error cleaning up temp directory {temp_dir}: {e}")
    
    def get_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None,
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch transcript from YouTube video with automatic fallback.
        
        Args:
            video_id: YouTube video ID
            languages: Preferred languages (default: ['en'])
            use_fallback: Whether to use Whisper fallback if transcript API fails
            
        Returns:
            Dictionary containing:
                - text: Full transcript text
                - language: Detected language
                - duration: Video duration in seconds
                - segments: Individual transcript segments
                - source: 'youtube_api' or 'whisper_fallback'
                
        Raises:
            Exception: If transcript is unavailable and fallback fails or is disabled
        """
        if languages is None:
            languages = ['en']
        
        try:
            logger.info(f"Fetching transcript for video ID: {video_id}")
            
            # Try to fetch transcript using YouTube API
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
                'segments': transcript_data,
                'source': 'youtube_api',
                'video_id': video_id
            }
            
            logger.info(f"Successfully fetched transcript from YouTube API: {len(full_text)} characters, {len(transcript_data)} segments")
            return result
            
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable,
                YouTubeRequestFailed, AttributeError) as e:
            # Log the API error
            api_error = f"YouTube Transcript API error for video {video_id}: {type(e).__name__}: {str(e)}"
            logger.warning(api_error)
            
            # Try fallback if enabled
            if use_fallback and self.audio_service is not None:
                logger.info(f"Attempting Whisper fallback for video {video_id}")
                try:
                    # Use first language from list for Whisper, or None for auto-detect
                    whisper_lang = languages[0] if languages and languages[0] != 'en' else None
                    return self._transcribe_with_whisper(video_id, whisper_lang)
                except Exception as fallback_error:
                    error_msg = f"Both YouTube API and Whisper fallback failed for video {video_id}. API error: {api_error}. Fallback error: {str(fallback_error)}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            else:
                # No fallback available or disabled
                if not use_fallback:
                    error_msg = f"YouTube Transcript API failed and fallback is disabled: {api_error}"
                else:
                    error_msg = f"YouTube Transcript API failed and no audio service available for fallback: {api_error}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error fetching transcript for video {video_id}: {str(e)}"
            logger.error(error_msg)
            
            # Try fallback for unexpected errors too
            if use_fallback and self.audio_service is not None:
                logger.info(f"Attempting Whisper fallback after unexpected error for video {video_id}")
                try:
                    whisper_lang = languages[0] if languages and languages[0] != 'en' else None
                    return self._transcribe_with_whisper(video_id, whisper_lang)
                except Exception as fallback_error:
                    final_error = f"Both YouTube API and Whisper fallback failed. Original error: {str(e)}. Fallback error: {str(fallback_error)}"
                    logger.error(final_error)
                    raise Exception(final_error)
            else:
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
        languages: Optional[List[str]] = None,
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Convenience method to get transcript directly from URL with fallback support.
        
        Args:
            url: YouTube video URL
            languages: Preferred languages (default: ['en'])
            use_fallback: Whether to use Whisper fallback if transcript API fails
            
        Returns:
            Dictionary containing transcript data
            
        Raises:
            Exception: If URL is invalid or transcript cannot be fetched
        """
        video_id = self.extract_video_id(url)
        return self.get_transcript(video_id, languages, use_fallback)