"""
Upload Feature View

This module handles the UI rendering for the file upload transcription feature.
"""

import streamlit as st
import logging
from typing import Dict, Any
from src.ui.components import UIComponents
from src.upload.service import transcribe_uploaded_file
from src.common.ai_processing import process_with_ai

logger = logging.getLogger(__name__)


def render_upload_view(settings: Dict[str, Any]) -> None:
    """
    Render the file upload tab.

    Args:
        settings: User settings dictionary
    """
    uploaded_file = UIComponents.render_upload_tab()

    if st.button("🚀 Transcribe File", key="upload_btn", disabled=st.session_state.processing):
        if not uploaded_file:
            st.error("❌ Please upload an audio file")
        else:
            # Reset previous results
            st.session_state.transcript_result = None
            st.session_state.summary_result = None
            st.session_state.key_points = None
            st.session_state.refined_message = None

            process_audio_file(uploaded_file, settings)


def process_audio_file(uploaded_file, settings: Dict[str, Any]) -> None:
    """
    Process uploaded audio file and transcribe.

    Args:
        uploaded_file: Streamlit UploadedFile object
        settings: User settings dictionary
    """
    try:
        st.session_state.processing = True

        with st.spinner("💾 Saving uploaded file..."):
            # Note: Saving is handled in service now, but we might want to show spinner here
            pass

        with st.spinner(f"🎯 Transcribing audio with Whisper ({settings['model_size']} model)..."):
            result = transcribe_uploaded_file(uploaded_file, settings)

            st.session_state.transcript_result = result["text"]

            st.success(
                f"✅ Transcription complete! "
                f"({len(result['text'])} characters, "
                f"language: {result['language']})"
            )
            logger.info(f"Audio transcribed: {len(result['text'])} characters")

        # Process with AI if using local LLM or if API key is available for OpenAI
        if settings.get("ai_provider") == "local" or settings.get("api_key"):
            process_with_ai(st.session_state.transcript_result, settings)
        else:
            st.warning("⚠️ API key not provided for OpenAI. Skipping AI processing.")

    except Exception as e:
        logger.error(f"Error processing audio file: {e}")
        UIComponents.render_error_message(
            str(e),
            suggestions=[
                "Check if the audio file format is supported",
                "Ensure the file is not corrupted",
                "Try converting the file to WAV or MP3 format",
            ],
        )
    finally:
        st.session_state.processing = False
