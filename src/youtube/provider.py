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
from src.utils.validators import validate_youtube_url, extract_video_id_from_url
from src.utils.file_handler import cleanup_temp_files
from src.utils.time_utils import parse_time_string

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

    def _download_youtube_audio(
        self,
        video_id: str,
        output_path: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Download YouTube video audio using yt-dlp.

        Args:
            video_id: YouTube video ID
            output_path: Directory to save the audio file
            start_time: Optional start time (e.g. "1:30" or "90")
            end_time: Optional end time (e.g. "2:30" or "150")

        Returns:
            Tuple of (Path to the downloaded audio file, Video title)

        Raises:
            Exception: If download fails
        """
        try:
            import yt_dlp

            logger.info(f"Downloading audio for video ID: {video_id}")

            # Parse time range
            start_seconds = parse_time_string(str(start_time)) if start_time else None
            end_seconds = parse_time_string(str(end_time)) if end_time else None

            # Configure yt-dlp options
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": os.path.join(output_path, "%(id)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
            }

            # Add download ranges if specified
            if start_seconds is not None or end_seconds is not None:
                logger.info(f"Downloading range: {start_seconds}s to {end_seconds}s")

                def download_range_func(info, ydl):
                    return [
                        {
                            "start_time": start_seconds if start_seconds is not None else 0,
                            "end_time": end_seconds
                            if end_seconds is not None
                            else info.get("duration"),
                        }
                    ]

                ydl_opts["download_ranges"] = download_range_func
                # Force keyframes at cuts for better precision
                ydl_opts["force_keyframes_at_cuts"] = True

            # Download audio
            url = f"https://www.youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get("title", "Unknown Title")

            # Find the downloaded file
            audio_file = os.path.join(output_path, f"{video_id}.mp3")

            if not os.path.exists(audio_file):
                raise Exception(f"Downloaded audio file not found: {audio_file}")

            logger.info(f"Successfully downloaded audio to: {audio_file}")
            return audio_file, video_title

        except Exception as e:
            error_msg = f"Failed to download YouTube audio: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _transcribe_with_whisper(
        self,
        video_id: str,
        language: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fallback method: Download YouTube audio and transcribe with Whisper.

        Args:
            video_id: YouTube video ID
            language: Language code for transcription
            start_time: Optional start time
            end_time: Optional end time

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
            audio_file, video_title = self._download_youtube_audio(
                video_id, temp_dir, start_time, end_time
            )

            # Transcribe with Whisper
            result = self.audio_service.transcribe_file(audio_file, language)

            # Add source information
            result["source"] = "whisper_fallback"
            result["video_id"] = video_id
            result["title"] = video_title

            logger.info(
                f"Successfully transcribed with Whisper fallback: {len(result['text'])} characters"
            )
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
        use_fallback: bool = True,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch transcript from YouTube video by downloading audio and using Whisper.

        Note: The 'use_fallback' parameter is kept for compatibility but ignored,
        as this method now always uses the audio download + Whisper approach.

        Args:
            video_id: YouTube video ID
            languages: Preferred languages (default: ['en'])
            use_fallback: Ignored (kept for compatibility)
            start_time: Optional start time
            end_time: Optional end time

        Returns:
            Dictionary containing:
                - text: Full transcript text
                - language: Detected language
                - duration: Video duration in seconds
                - segments: Individual transcript segments
                - source: 'whisper_audio'
                - video_id: Video ID

        Raises:
            Exception: If audio download or transcription fails
        """
        if languages is None:
            languages = ["en"]

        try:
            logger.info(f"Processing video ID: {video_id} via audio download")

            if self.audio_service is None:
                raise Exception("Audio service not available for transcription")

            # Use first language from list for Whisper, or None for auto-detect
            whisper_lang = languages[0] if languages and languages[0] != "en" else None

            # Reuse the existing logic which does exactly what we want:
            # 1. Create temp dir
            # 2. Download audio
            # 3. Transcribe with Whisper
            # 4. Cleanup
            result = self._transcribe_with_whisper(
                video_id, whisper_lang, start_time, end_time
            )

            # Update source to reflect this is now the primary method
            result["source"] = "whisper_audio"

            return result

        except Exception as e:
            error_msg = f"Error processing video {video_id}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_available_languages(self, video_id: str) -> List[str]:
        """
        Get list of available transcript languages for a video.

        Note: Since we are now using Whisper for all transcriptions, we don't rely on
        YouTube's available captions. Whisper can detect the language automatically.

        Args:
            video_id: YouTube video ID

        Returns:
            List of available language codes (always returns ['auto-detect'] as we use Whisper)
        """
        return ["auto-detect"]

    def get_transcript_from_url(
        self,
        url: str,
        languages: Optional[List[str]] = None,
        use_fallback: bool = True,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Convenience method to get transcript directly from URL with fallback support.

        Args:
            url: YouTube video URL
            languages: Preferred languages (default: ['en'])
            use_fallback: Whether to use Whisper fallback if transcript API fails
            start_time: Optional start time
            end_time: Optional end time

        Returns:
            Dictionary containing transcript data

        Raises:
            Exception: If URL is invalid or transcript cannot be fetched
        """
        video_id = self.extract_video_id(url)
        return self.get_transcript(
            video_id, languages, use_fallback, start_time, end_time
        )
