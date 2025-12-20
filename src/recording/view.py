"""
Recording Feature View

This module handles the UI rendering for the voice recording transcription feature.
"""

import streamlit as st
import logging
from typing import Dict, Any
from src.ui.components import UIComponents
from src.recording.service import transcribe_recording
from src.common.ai_processing import process_with_ai

logger = logging.getLogger(__name__)


def render_recording_view(settings: Dict[str, Any]) -> None:
    """
    Render the voice recording tab.

    Args:
        settings: User settings dictionary
    """
    audio_bytes = UIComponents.render_recording_tab()

    if audio_bytes and st.button(
        "🚀 Transcribe Recording", key="record_btn", disabled=st.session_state.processing
    ):
        # Reset previous results
        st.session_state.transcript_result = None
        st.session_state.summary_result = None
        st.session_state.key_points = None
        st.session_state.refined_message = None

        process_audio_recording(audio_bytes, settings)


def process_audio_recording(audio_bytes: bytes, settings: Dict[str, Any]) -> None:
    """
    Process recorded audio and transcribe.

    Args:
        audio_bytes: Audio data as bytes
        settings: User settings dictionary
    """
    try:
        st.session_state.processing = True

        with st.spinner(
            f"🎯 Transcribing recording with Whisper ({settings['model_size']} model)..."
        ):
            result = transcribe_recording(audio_bytes, settings)

            st.session_state.transcript_result = result["text"]

            st.success(
                f"✅ Recording transcribed! "
                f"({len(result['text'])} characters, "
                f"language: {result['language']})"
            )
            logger.info(f"Recording transcribed: {len(result['text'])} characters")

        # Process with AI if using local LLM or if API key is available for OpenAI
        if settings.get("ai_provider") == "local" or settings.get("api_key"):
            process_with_ai(st.session_state.transcript_result, settings)
        else:
            st.warning("⚠️ API key not provided for OpenAI. Skipping AI processing.")

    except Exception as e:
        logger.error(f"Error processing audio recording: {e}")
        UIComponents.render_error_message(
            str(e),
            suggestions=[
                "Try recording again",
                "Check your microphone permissions",
                "Ensure the recording is not too short",
            ],
        )
    finally:
        st.session_state.processing = False
