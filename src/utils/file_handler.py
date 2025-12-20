"""
File Handling Utilities

This module provides utilities for file operations including temporary file
management, cleanup, and file conversions.

Responsibilities:
- Manage temporary file storage
- Clean up temporary files
- Handle file conversions
- Provide safe file operations
"""

import os
import logging
import tempfile
import time
from typing import Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    # Logger will be initialized after this import, so we can't use it here

logger = logging.getLogger(__name__)


def save_uploaded_file(uploaded_file, filename: Optional[str] = None) -> str:
    """
    Save an uploaded file to temporary storage.
    
    Args:
        uploaded_file: Streamlit UploadedFile object or bytes
        filename: Optional original filename (used to preserve extension)
        
    Returns:
        Path to saved file as string
        
    Raises:
        Exception: If file cannot be saved
    """
    try:
        # Determine file extension
        suffix = ""
        if filename:
            suffix = Path(filename).suffix
        elif hasattr(uploaded_file, 'name'):
            suffix = Path(uploaded_file.name).suffix
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            prefix="aitranscript_"
        )
        
        # Write content
        if hasattr(uploaded_file, 'read'):
            # Streamlit UploadedFile object
            temp_file.write(uploaded_file.read())
        elif isinstance(uploaded_file, bytes):
            # Raw bytes
            temp_file.write(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {type(uploaded_file)}")
        
        temp_file.close()
        
        logger.info(f"Saved uploaded file to: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Error saving uploaded file: {e}")
        raise Exception(f"Failed to save uploaded file: {str(e)}")


def cleanup_temp_files(file_path: Union[str, Path]) -> None:
    """
    Delete a temporary file safely.
    
    Args:
        file_path: Path to file to delete
    """
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Error cleaning up file {file_path}: {e}")


def get_audio_duration(file_path: str) -> float:
    """
    Get audio duration in seconds.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds (0.0 if pydub not available)
        
    Raises:
        Exception: If duration cannot be determined
    """
    if not PYDUB_AVAILABLE:
        logger.warning("pydub not available - returning 0.0 for audio duration")
        return 0.0
    
    try:
        audio = AudioSegment.from_file(file_path)
        duration_seconds = len(audio) / 1000.0  # pydub returns milliseconds
        logger.info(f"Audio duration for {file_path}: {duration_seconds:.2f} seconds")
        return duration_seconds
    except Exception as e:
        logger.error(f"Error getting audio duration for {file_path}: {e}")
        raise Exception(f"Failed to get audio duration: {str(e)}")


def create_temp_directory() -> Path:
    """
    Create a temporary directory for file operations.
    
    Returns:
        Path to created temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="aitranscript_"))
    logger.info(f"Created temporary directory: {temp_dir}")
    return temp_dir


def cleanup_old_temp_files(max_age_hours: int = 1) -> int:
    """
    Clean up old temporary files in the system temp directory.
    
    Args:
        max_age_hours: Maximum age of files to keep (in hours)
        
    Returns:
        Number of files deleted
    """
    try:
        temp_dir = Path(tempfile.gettempdir())
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        # Find and delete old aitranscript temp files
        for file_path in temp_dir.glob("aitranscript_*"):
            try:
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted old temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Error deleting temp file {file_path}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old temporary files")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error during temp file cleanup: {e}")
        return 0


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
        
    Raises:
        Exception: If file size cannot be determined
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
        
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {e}")
        raise Exception(f"Failed to get file size: {str(e)}")


def convert_audio_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert audio file to WAV format for better compatibility.
    
    Args:
        input_path: Path to input audio file
        output_path: Optional path for output file (auto-generated if None)
        
    Returns:
        Path to converted WAV file (or original if pydub not available)
        
    Raises:
        Exception: If conversion fails
    """
    if not PYDUB_AVAILABLE:
        logger.warning("pydub not available - returning original file path")
        return input_path
    
    try:
        audio = AudioSegment.from_file(input_path)
        
        if output_path is None:
            # Create temp file with .wav extension
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav",
                prefix="aitranscript_converted_"
            )
            output_path = temp_file.name
            temp_file.close()
        
        # Export as WAV
        audio.export(output_path, format="wav")
        logger.info(f"Converted audio to WAV: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error converting audio to WAV: {e}")
        raise Exception(f"Failed to convert audio: {str(e)}")


def save_bytes_to_temp_file(audio_bytes: bytes, suffix: str = ".wav") -> str:
    """
    Save audio bytes to a temporary file.
    
    Args:
        audio_bytes: Audio data as bytes
        suffix: File extension (default: .wav)
        
    Returns:
        Path to saved temporary file
        
    Raises:
        Exception: If file cannot be saved
    """
    try:
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            prefix="aitranscript_recording_"
        )
        temp_file.write(audio_bytes)
        temp_file.close()
        
        logger.info(f"Saved audio bytes to temporary file: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Error saving audio bytes to temp file: {e}")
        raise Exception(f"Failed to save audio bytes: {str(e)}")