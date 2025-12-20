"""
AiTranscript - Main Streamlit Application

This is the main entry point for the AiTranscript application.
It provides a web interface for transcribing audio from YouTube videos,
uploaded files, or live recordings, with AI-powered summarization.

Usage:
    streamlit run app.py
"""

import streamlit as st
import logging
from typing import Dict, Any

# Import services
# Services are now used within feature modules

# Import features
from src.youtube.view import render_youtube_view
from src.upload.view import render_upload_view
from src.recording.view import render_recording_view

# Import utilities
from src.utils.config import get_config
from src.utils.file_handler import cleanup_old_temp_files
from src.ui.components import UIComponents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="AiTranscript", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded"
)


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "transcript_result" not in st.session_state:
        st.session_state.transcript_result = None
    if "summary_result" not in st.session_state:
        st.session_state.summary_result = None
    if "key_points" not in st.session_state:
        st.session_state.key_points = None
    if "refined_message" not in st.session_state:
        st.session_state.refined_message = None
    if "processing" not in st.session_state:
        st.session_state.processing = False




def main() -> None:
    """
    Main application entry point.

    This function orchestrates the Streamlit UI and coordinates between
    different services for transcription and AI processing.
    """
    # Initialize session state
    initialize_session_state()

    # Clean up old temporary files on startup
    try:
        cleanup_old_temp_files(max_age_hours=1)
    except Exception as e:
        logger.warning(f"Error cleaning up old temp files: {e}")

    # Render header
    UIComponents.render_header()

    # Render settings panel in sidebar
    settings = UIComponents.render_settings_panel()

    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📺 YouTube", "📁 Upload File", "🎤 Record Audio"])

    # Tab 1: YouTube Transcription
    with tab1:
        render_youtube_view(settings)

    # Tab 2: File Upload
    with tab2:
        render_upload_view(settings)

    # Tab 3: Voice Recording
    with tab3:
        render_recording_view(settings)

    # Display results if available
    if st.session_state.transcript_result:
        st.markdown("---")
        st.markdown("## 📊 Results")

        # Display transcript
        UIComponents.render_transcript_result(st.session_state.transcript_result)

        # Display AI results based on processing mode
        if st.session_state.summary_result:
            st.markdown("---")
            UIComponents.render_summary_result(
                st.session_state.summary_result, st.session_state.key_points
            )

        if st.session_state.refined_message:
            st.markdown("---")
            UIComponents.render_refined_message_result(
                st.session_state.transcript_result, st.session_state.refined_message
            )

        # Download buttons
        download_content = st.session_state.summary_result or st.session_state.refined_message
        UIComponents.render_download_buttons(st.session_state.transcript_result, download_content)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Built with ❤️ using Streamlit, Whisper, and OpenAI GPT"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
