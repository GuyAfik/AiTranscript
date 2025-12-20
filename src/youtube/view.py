"""
YouTube Feature View

This module handles the UI rendering for the YouTube transcription feature.
"""

import streamlit as st
import logging
from typing import Dict, Any
from src.ui.components import UIComponents
from src.youtube.service import get_youtube_transcript

logger = logging.getLogger(__name__)

def render_youtube_view(settings: Dict[str, Any]) -> None:
    """
    Render the YouTube transcription tab.

    Args:
        settings: User settings dictionary
    """
    youtube_url = UIComponents.render_youtube_tab()

    if st.button("🚀 Get Transcript", key="youtube_btn", disabled=st.session_state.processing):
        if not youtube_url:
            st.error("❌ Please enter a YouTube URL")
        else:
            # Reset previous results
            st.session_state.transcript_result = None
            st.session_state.summary_result = None
            st.session_state.key_points = None
            st.session_state.refined_message = None

            process_youtube_url(youtube_url, settings)

def process_youtube_url(url: str, settings: Dict[str, Any]) -> None:
    """
    Process YouTube URL and extract transcript.

    Args:
        url: YouTube video URL
        settings: User settings dictionary
    """
    try:
        st.session_state.processing = True

        with st.spinner("🔍 Extracting transcript from YouTube..."):
            result = get_youtube_transcript(url, settings)

            st.session_state.transcript_result = result["text"]

            # Show different success message based on source
            if result.get("source") == "whisper_fallback":
                st.success(
                    f"✅ Transcript extracted using Whisper (YouTube API unavailable)! "
                    f"({len(result['text'])} characters, language: {result['language']})"
                )
                logger.info(
                    f"YouTube transcript extracted via Whisper fallback: {len(result['text'])} characters"
                )
            else:
                st.success(
                    f"✅ Transcript extracted successfully! ({len(result['text'])} characters)"
                )
                logger.info(f"YouTube transcript extracted: {len(result['text'])} characters")

        # Process with AI if using local LLM or if API key is available for OpenAI
        # Note: This dependency on process_with_ai needs to be handled. 
        # Ideally, we should import a shared AI processing function or pass it as a callback.
        # For now, we will assume the main app handles the AI processing trigger based on state,
        # OR we can import a shared utility. Let's assume we'll create a shared utility.
        from src.common.ai_processing import process_with_ai
        
        if settings.get("ai_provider") == "local" or settings.get("api_key"):
            process_with_ai(st.session_state.transcript_result, settings)
        else:
            st.warning("⚠️ API key not provided for OpenAI. Skipping AI processing.")

    except Exception as e:
        logger.error(f"Error processing YouTube URL: {e}")
        UIComponents.render_error_message(
            str(e),
            suggestions=[
                "Check if the YouTube URL is valid",
                "Ensure the video is publicly accessible",
                "If the video is long, it may take a few minutes to download and transcribe",
                "Try a different video",
            ],
        )
    finally:
        st.session_state.processing = False