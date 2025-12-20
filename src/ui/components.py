"""
Reusable UI Components

This module provides reusable Streamlit UI components for the AiTranscript application.

Components:
- Result display sections
- Progress indicators
- File upload widgets
- Recording controls
- Settings panels
"""

from typing import Optional, Dict, Any, List
import streamlit as st
from datetime import datetime


class UIComponents:
    """
    Collection of reusable UI components for the Streamlit interface.
    """
    
    @staticmethod
    def render_header() -> None:
        """
        Render the application header.
        """
        st.title("🎙️ AiTranscript")
        st.markdown("### Voice Transcription & AI Cleanup")
        st.markdown(
            "Transform audio into text with AI-powered summarization. "
            "Support for YouTube videos, audio files, and live recordings."
        )
        st.markdown("---")
    
    @staticmethod
    def render_settings_panel() -> Dict[str, Any]:
        """
        Render the settings panel with configuration options.
        
        Returns:
            Dictionary of user settings
        """
        with st.sidebar:
            st.header("⚙️ Settings")
            
            # Whisper model selection
            st.subheader("Transcription")
            model_size = st.selectbox(
                "Whisper Model Size",
                options=["tiny", "base", "small", "medium", "large"],
                index=1,  # Default to 'base'
                help="Larger models are more accurate but slower. 'base' is recommended for most use cases."
            )
            
            # Language selection
            language = st.selectbox(
                "Language",
                options=["auto-detect", "en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh"],
                index=0,
                help="Select language for transcription. 'auto-detect' works for most cases."
            )
            
            st.markdown("---")
            
            # AI settings
            st.subheader("AI Processing")
            
            # Processing mode selection
            processing_mode = st.radio(
                "Processing Mode",
                options=["summarize", "refine"],
                format_func=lambda x: "📊 Summarize Content" if x == "summarize" else "✨ Refine Message",
                help="Choose how to process the transcript:\n"
                     "- Summarize: Get a clear summary of the content\n"
                     "- Refine: Improve your message for better communication"
            )
            
            # Mode-specific settings
            if processing_mode == "summarize":
                summary_style = st.selectbox(
                    "Summary Style",
                    options=["concise", "detailed", "bullet"],
                    index=0,
                    help="Choose how the AI should summarize the transcript."
                )
                
                generate_key_points = st.checkbox(
                    "Generate Key Points",
                    value=True,
                    help="Extract main takeaways from the transcript."
                )
            else:  # refine mode
                summary_style = None
                generate_key_points = False
                
                message_tone = st.selectbox(
                    "Message Tone",
                    options=["professional", "friendly", "formal", "casual"],
                    index=0,
                    help="Choose the tone for your refined message."
                )
                
                recipient_context = st.text_input(
                    "Recipient (optional)",
                    placeholder="e.g., my boss, a client, a friend",
                    help="Provide context about who will receive this message for better refinement."
                )
            
            st.markdown("---")
            
            # AI Provider selection
            st.subheader("AI Provider")
            ai_provider = st.selectbox(
                "Provider",
                options=["local", "openai"],
                format_func=lambda x: "🏠 Local LLM (Ollama)" if x == "local" else "☁️ OpenAI (GPT)",
                index=0,  # Default to local
                help="Choose your AI provider. Local LLM runs on your machine (free, private). OpenAI requires API key."
            )
            
            # Model selection based on provider
            if ai_provider == "local":
                ai_model = st.selectbox(
                    "Model",
                    options=["llama2", "llama3", "mistral", "phi", "codellama"],
                    index=0,
                    help="Select local model. Make sure it's installed: ollama pull <model>"
                )
                api_key = None  # No API key needed for local
                st.info("ℹ️ Using local LLM - no API key required. Make sure Ollama is running.")
            else:  # openai
                ai_model = st.selectbox(
                    "Model",
                    options=["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
                    index=0,
                    help="Select OpenAI model. GPT-4 is more capable but slower and more expensive."
                )
                api_key = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    help="Enter your OpenAI API key. Get one at platform.openai.com"
                )
                
                if not api_key:
                    st.warning("⚠️ OpenAI API key required for OpenAI provider")
            
            settings = {
                "model_size": model_size,
                "language": None if language == "auto-detect" else language,
                "processing_mode": processing_mode,
                "ai_provider": ai_provider,
                "ai_model": ai_model,
                "api_key": api_key
            }
            
            # Add mode-specific settings
            if processing_mode == "summarize":
                settings["summary_style"] = summary_style
                settings["generate_key_points"] = generate_key_points
            else:  # refine mode
                settings["message_tone"] = message_tone
                settings["recipient_context"] = recipient_context if recipient_context else None
            
            return settings
    
    @staticmethod
    def render_youtube_tab() -> Optional[str]:
        """
        Render the YouTube input tab.
        
        Returns:
            YouTube URL if provided, None otherwise
        """
        st.markdown("### 📺 YouTube Video Transcription")
        st.markdown("Enter a YouTube URL to extract and summarize its transcript.")
        
        url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste the URL of any YouTube video with available captions"
        )
        
        if url:
            st.info(f"📎 URL: {url}")
        
        return url if url else None
    
    @staticmethod
    def render_upload_tab() -> Optional[Any]:
        """
        Render the file upload tab.
        
        Returns:
            Uploaded file object if provided, None otherwise
        """
        st.markdown("### 📁 Audio File Upload")
        st.markdown("Upload an audio file to transcribe and summarize.")
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=["mp3", "wav", "m4a", "ogg", "flac"],
            help="Supported formats: MP3, WAV, M4A, OGG, FLAC (max 100MB)"
        )
        
        if uploaded_file:
            # Display file info
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.success(f"✅ File uploaded: {uploaded_file.name} ({file_size_mb:.2f} MB)")
            
            # Audio player
            st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
        
        return uploaded_file
    
    @staticmethod
    def render_recording_tab() -> Optional[bytes]:
        """
        Render the voice recording tab.
        
        Returns:
            Recorded audio bytes if available, None otherwise
        """
        st.markdown("### 🎤 Live Voice Recording")
        st.markdown("Record audio directly from your microphone.")
        
        # Try to import audio recorder
        try:
            from audio_recorder_streamlit import audio_recorder
            
            # Initialize recorder key in session state
            if 'recorder_key' not in st.session_state:
                st.session_state.recorder_key = 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("🎙️ Click the microphone button to start/stop recording")
            with col2:
                if st.button("🗑️ Clear", help="Clear the current recording"):
                    st.session_state.recorder_key += 1
                    st.rerun()
            
            audio_bytes = audio_recorder(
                text="",
                recording_color="#e74c3c",
                neutral_color="#3498db",
                icon_name="microphone",
                icon_size="3x",
                key=f"audio_recorder_{st.session_state.recorder_key}"
            )
            
            # Only show audio player when we have audio
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                return audio_bytes
            
            return None
            
        except ImportError:
            st.warning(
                "⚠️ Audio recorder not available. "
                "Install with: `pip install audio-recorder-streamlit`"
            )
            st.info(
                "Alternatively, you can upload a pre-recorded audio file "
                "using the 'Upload File' tab."
            )
            return None
    
    @staticmethod
    def render_transcript_result(transcript: str, title: str = "📝 Full Transcript") -> None:
        """
        Render the transcript result section.
        
        Args:
            transcript: Transcript text to display
            title: Section title
        """
        with st.expander(title, expanded=True):
            st.markdown(transcript)
            
            # Word count
            word_count = len(transcript.split())
            st.caption(f"📊 Word count: {word_count:,}")
    
    @staticmethod
    def render_summary_result(summary: str, key_points: Optional[List[str]] = None) -> None:
        """
        Render the AI summary and key points section.
        
        Args:
            summary: Summary text
            key_points: List of key points (optional)
        """
        st.markdown("### ✨ AI Summary")
        st.markdown(summary)
        
        if key_points:
            st.markdown("### 🔑 Key Points")
            for i, point in enumerate(key_points, 1):
                st.markdown(f"{i}. {point}")
    
    @staticmethod
    def render_refined_message_result(original: str, refined: str) -> None:
        """
        Render the refined message result with before/after comparison.
        
        Args:
            original: Original transcript text
            refined: Refined message text
        """
        st.markdown("### ✨ Refined Message")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Original")
            with st.container():
                st.markdown(
                    f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px; '
                    f'border-left: 4px solid #ff6b6b;">{original}</div>',
                    unsafe_allow_html=True
                )
        
        with col2:
            st.markdown("#### ✅ Refined")
            with st.container():
                st.markdown(
                    f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px; '
                    f'border-left: 4px solid #51cf66;">{refined}</div>',
                    unsafe_allow_html=True
                )
        
        # Copy button for refined message
        st.markdown("---")
        st.markdown("**📋 Ready to send:**")
        st.code(refined, language=None)
    
    @staticmethod
    def render_download_buttons(transcript: str, summary: Optional[str] = None) -> None:
        """
        Render download buttons for transcript and summary.
        
        Args:
            transcript: Transcript text
            summary: Summary text (optional)
        """
        st.markdown("---")
        st.markdown("### 💾 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download transcript
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            transcript_filename = f"transcript_{timestamp}.txt"
            
            st.download_button(
                label="📄 Download Transcript",
                data=transcript,
                file_name=transcript_filename,
                mime="text/plain"
            )
        
        with col2:
            # Download summary if available
            if summary:
                summary_filename = f"summary_{timestamp}.txt"
                
                st.download_button(
                    label="📋 Download Summary",
                    data=summary,
                    file_name=summary_filename,
                    mime="text/plain"
                )
    
    @staticmethod
    def render_progress_indicator(message: str) -> None:
        """
        Render a progress indicator with message.
        
        Args:
            message: Progress message to display
        """
        with st.spinner(message):
            pass
    
    @staticmethod
    def render_error_message(error: str, suggestions: Optional[List[str]] = None) -> None:
        """
        Render an error message with optional suggestions.
        
        Args:
            error: Error message
            suggestions: List of suggested actions (optional)
        """
        st.error(f"❌ {error}")
        
        if suggestions:
            st.markdown("**Suggestions:**")
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")
    
    @staticmethod
    def render_info_box(title: str, content: str, icon: str = "ℹ️") -> None:
        """
        Render an informational box.
        
        Args:
            title: Box title
            content: Box content
            icon: Icon to display
        """
        st.info(f"{icon} **{title}**\n\n{content}")