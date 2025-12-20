"""
Input Validation Utilities

This module provides validation functions for various input types including
URLs, file formats, and data integrity checks.

Responsibilities:
- Validate YouTube URLs
- Validate audio file formats
- Check file sizes and integrity
- Validate configuration parameters
"""

import re
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_youtube_url(url: str) -> bool:
    """
    Validate if a URL is a valid YouTube URL.

    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID

    Args:
        url: URL string to validate

    Returns:
        True if valid YouTube URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    # YouTube URL patterns
    patterns = [
        r"^https?://(www\.)?youtube\.com/watch\?v=[\w-]+",
        r"^https?://youtu\.be/[\w-]+",
        r"^https?://m\.youtube\.com/watch\?v=[\w-]+",
        r"^https?://youtube\.com/watch\?v=[\w-]+",
    ]

    for pattern in patterns:
        if re.match(pattern, url):
            return True

    return False


def extract_video_id_from_url(url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL.

    Args:
        url: YouTube URL

    Returns:
        Video ID if found, None otherwise
    """
    if not validate_youtube_url(url):
        return None

    # Pattern for youtube.com/watch?v=VIDEO_ID
    match = re.search(r"[?&]v=([^&]+)", url)
    if match:
        return match.group(1)

    # Pattern for youtu.be/VIDEO_ID
    match = re.search(r"youtu\.be/([^?&]+)", url)
    if match:
        return match.group(1)

    return None


def validate_audio_file(file_path: str) -> Tuple[bool, str]:
    """
    Comprehensive validation of audio file.

    Validates:
    - File exists
    - File format is supported (mp3, wav, m4a, ogg, flac, aac)
    - File size is within limits

    Args:
        file_path: Path to audio file (string or Path object)

    Returns:
        Tuple of (is_valid, error_message)
        - (True, "") if valid
        - (False, "error message") if invalid
    """
    try:
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return False, f"File does not exist: {file_path}"

        if not path.is_file():
            return False, f"Path is not a file: {file_path}"

        # Check file format
        supported_formats = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}
        file_extension = path.suffix.lower()

        if file_extension not in supported_formats:
            return (
                False,
                f"Unsupported audio format: {file_extension}. Supported formats: {', '.join(supported_formats)}",
            )

        # Check file size (default max: 100MB)
        max_size_bytes = 100 * 1024 * 1024  # 100MB
        file_size = path.stat().st_size

        if file_size == 0:
            return False, "File is empty"

        if file_size > max_size_bytes:
            size_mb = file_size / (1024 * 1024)
            return False, f"File size ({size_mb:.1f}MB) exceeds maximum allowed size (100MB)"

        return True, ""

    except Exception as e:
        logger.error(f"Error validating audio file {file_path}: {e}")
        return False, f"Error validating file: {str(e)}"


def validate_file_size(file_path: str, max_size_mb: int = 100) -> Tuple[bool, str]:
    """
    Validate file size is within acceptable limits.

    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB (default: 100)

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return False, f"File does not exist: {file_path}"

        file_size = path.stat().st_size
        max_size_bytes = max_size_mb * 1024 * 1024

        if file_size > max_size_bytes:
            size_mb = file_size / (1024 * 1024)
            return False, f"File size ({size_mb:.1f}MB) exceeds maximum ({max_size_mb}MB)"

        return True, ""

    except Exception as e:
        logger.error(f"Error checking file size for {file_path}: {e}")
        return False, f"Error checking file size: {str(e)}"


def validate_audio_format(file_path: str) -> bool:
    """
    Check if file has a supported audio format.

    Args:
        file_path: Path to audio file

    Returns:
        True if format is supported, False otherwise
    """
    supported_formats = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}
    path = Path(file_path)
    return path.suffix.lower() in supported_formats
