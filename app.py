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
from pathlib import Path
from typing import Optional, Dict, Any

# Import services
from src.services.youtube_service import YouTubeService
from src.services.audio_service import AudioTranscriptionService
from src.services.ai_service import AICleanupService

# Import utilities
from src.utils.config import get_config
from src.utils.file_handler import save_uploaded_file, cleanup_temp_files, cleanup_old_temp_files
from src.ui.components import UIComponents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="AiTranscript",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if 'transcript_result' not in st.session_state:
        st.session_state.transcript_result = None
    if 'summary_result' not in st.session_state:
        st.session_state.summary_result = None
    if 'key_points' not in st.session_state:
        st.session_state.key_points = None
    if 'refined_message' not in st.session_state:
        st.session_state.refined_message = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


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
            # Initialize audio service for fallback
            audio_service = AudioTranscriptionService(
                model_size=settings['model_size'],
                device='cpu'
            )
            
            # Initialize YouTube service with audio service for fallback
            youtube_service = YouTubeService(audio_service=audio_service)
            
            # Get transcript
            languages = [settings['language']] if settings['language'] else ['en']
            result = youtube_service.get_transcript_from_url(url, languages)
            
            st.session_state.transcript_result = result['text']
            
            # Show different success message based on source
            if result.get('source') == 'whisper_fallback':
                st.success(
                    f"✅ Transcript extracted using Whisper (YouTube API unavailable)! "
                    f"({len(result['text'])} characters, language: {result['language']})"
                )
                logger.info(f"YouTube transcript extracted via Whisper fallback: {len(result['text'])} characters")
            else:
                st.success(f"✅ Transcript extracted successfully! ({len(result['text'])} characters)")
                logger.info(f"YouTube transcript extracted: {len(result['text'])} characters")
        
        # Process with AI if using local LLM or if API key is available for OpenAI
        if settings.get('ai_provider') == 'local' or settings.get('api_key'):
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
                "Try a different video"
            ]
        )
    finally:
        st.session_state.processing = False


def process_audio_file(uploaded_file, settings: Dict[str, Any]) -> None:
    """
    Process uploaded audio file and transcribe.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        settings: User settings dictionary
    """
    temp_file_path = None
    try:
        st.session_state.processing = True
        
        with st.spinner("💾 Saving uploaded file..."):
            # Save uploaded file to temp location
            temp_file_path = save_uploaded_file(uploaded_file)
            logger.info(f"Saved uploaded file: {temp_file_path}")
        
        with st.spinner(f"🎯 Transcribing audio with Whisper ({settings['model_size']} model)..."):
            # Initialize audio transcription service
            audio_service = AudioTranscriptionService(
                model_size=settings['model_size'],
                device='cpu'  # Use CPU for compatibility
            )
            
            # Transcribe audio
            result = audio_service.transcribe_file(
                temp_file_path,
                language=settings['language']
            )
            
            st.session_state.transcript_result = result['text']
            
            st.success(
                f"✅ Transcription complete! "
                f"({len(result['text'])} characters, "
                f"language: {result['language']})"
            )
            logger.info(f"Audio transcribed: {len(result['text'])} characters")
        
        # Process with AI if using local LLM or if API key is available for OpenAI
        if settings.get('ai_provider') == 'local' or settings.get('api_key'):
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
                "Try converting the file to WAV or MP3 format"
            ]
        )
    finally:
        # Clean up temporary file
        if temp_file_path:
            try:
                cleanup_temp_files(temp_file_path)
            except Exception as e:
                logger.warning(f"Error cleaning up temp file: {e}")
        
        st.session_state.processing = False


def process_audio_recording(audio_bytes: bytes, settings: Dict[str, Any]) -> None:
    """
    Process recorded audio and transcribe.
    
    Args:
        audio_bytes: Audio data as bytes
        settings: User settings dictionary
    """
    try:
        st.session_state.processing = True
        
        with st.spinner(f"🎯 Transcribing recording with Whisper ({settings['model_size']} model)..."):
            # Initialize audio transcription service
            audio_service = AudioTranscriptionService(
                model_size=settings['model_size'],
                device='cpu'
            )
            
            # Transcribe audio bytes
            result = audio_service.transcribe_audio_data(
                audio_bytes,
                language=settings['language'],
                file_extension=".wav"
            )
            
            st.session_state.transcript_result = result['text']
            
            st.success(
                f"✅ Recording transcribed! "
                f"({len(result['text'])} characters, "
                f"language: {result['language']})"
            )
            logger.info(f"Recording transcribed: {len(result['text'])} characters")
        
        # Process with AI if using local LLM or if API key is available for OpenAI
        if settings.get('ai_provider') == 'local' or settings.get('api_key'):
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
                "Ensure the recording is not too short"
            ]
        )
    finally:
        st.session_state.processing = False


def process_with_ai(transcript: str, settings: Dict[str, Any]) -> None:
    """
    Process transcript with AI for summarization or message refinement.
    
    Args:
        transcript: Transcript text
        settings: User settings dictionary
    """
    try:
        # Initialize AI service with selected provider and model
        ai_service = AICleanupService(
            api_key=settings.get('api_key'),
            model=settings.get('ai_model', 'llama2' if settings.get('ai_provider') == 'local' else get_config().openai_model),
            provider=settings.get('ai_provider', 'local')
        )
        
        processing_mode = settings.get('processing_mode', 'summarize')
        
        if processing_mode == 'summarize':
            # Summarization mode
            with st.spinner("🤖 Generating AI summary..."):
                summary = ai_service.summarize_text(
                    transcript,
                    style=settings['summary_style']
                )
                st.session_state.summary_result = summary
                
                # Generate key points if requested
                if settings['generate_key_points']:
                    with st.spinner("🔑 Extracting key points..."):
                        key_points = ai_service.generate_key_points(transcript)
                        st.session_state.key_points = key_points
                
                st.success("✅ AI summarization complete!")
                logger.info("AI summarization completed")
        
        else:  # refine mode
            # Message refinement mode
            with st.spinner("✨ Refining your message..."):
                refined = ai_service.refine_message(
                    transcript,
                    tone=settings.get('message_tone', 'professional'),
                    recipient_context=settings.get('recipient_context')
                )
                st.session_state.refined_message = refined
                
                st.success("✅ Message refined successfully!")
                logger.info("Message refinement completed")
    
    except Exception as e:
        logger.error(f"Error in AI processing: {e}")
        UIComponents.render_error_message(
            f"AI processing failed: {str(e)}",
            suggestions=[
                "Check if your OpenAI API key is valid",
                "Ensure you have sufficient API credits",
                "Try again in a few moments"
            ]
        )


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
    tab1, tab2, tab3 = st.tabs([
        "📺 YouTube",
        "📁 Upload File",
        "🎤 Record Audio"
    ])
    
    # Tab 1: YouTube Transcription
    with tab1:
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
    
    # Tab 2: File Upload
    with tab2:
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
    
    # Tab 3: Voice Recording
    with tab3:
        audio_bytes = UIComponents.render_recording_tab()
        
        if audio_bytes and st.button("🚀 Transcribe Recording", key="record_btn", disabled=st.session_state.processing):
            # Reset previous results
            st.session_state.transcript_result = None
            st.session_state.summary_result = None
            st.session_state.key_points = None
            st.session_state.refined_message = None
            
            process_audio_recording(audio_bytes, settings)
    
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
                st.session_state.summary_result,
                st.session_state.key_points
            )
        
        if st.session_state.refined_message:
            st.markdown("---")
            UIComponents.render_refined_message_result(
                st.session_state.transcript_result,
                st.session_state.refined_message
            )
        
        # Download buttons
        download_content = st.session_state.summary_result or st.session_state.refined_message
        UIComponents.render_download_buttons(
            st.session_state.transcript_result,
            download_content
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Built with ❤️ using Streamlit, Whisper, and OpenAI GPT"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()