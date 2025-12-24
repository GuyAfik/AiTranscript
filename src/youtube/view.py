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
    youtube_data = UIComponents.render_youtube_tab()
    youtube_url = youtube_data.get("url")
    
    # Check if we have video info (title) which means user has verified the video
    # We can check this by looking for the video info in session state or just rely on the user flow
    # For now, let's just disable the button if no URL, but we can't easily check if "Get Info" was clicked
    # without adding more state.
    # However, the user asked to disable "Get Transcript" BEFORE fetching video info.
    # This implies a flow: Enter URL -> Click "Get Info" -> "Get Transcript" becomes enabled.
    
    # Let's check if we have a valid video ID extracted and verified
    video_verified = False
    if youtube_url:
        # We can check if the "Get Video Info" button was clicked in the component
        # But components don't return that state directly in the dict.
        # We need to modify UIComponents to return whether info was fetched or use session state.
        pass

    # Since we can't easily change the return type of render_youtube_tab without breaking other things,
    # let's rely on the fact that the user *should* click "Get Info".
    # But to strictly enforce "disable before fetch", we need state.
    
    if "youtube_video_verified" not in st.session_state:
        st.session_state.youtube_video_verified = False
        
    # If URL changes, reset verification
    if "last_youtube_url" not in st.session_state:
        st.session_state.last_youtube_url = ""
        
    if youtube_url != st.session_state.last_youtube_url:
        st.session_state.youtube_video_verified = False
        st.session_state.last_youtube_url = youtube_url

    # The button in UIComponents needs to update this state.
    # Since we can't easily modify the component's internal logic from here without passing a callback,
    # we might need to move the button logic here or update the component to return more info.
    # Let's update the component to handle the state update.
    
    # For now, let's assume the component handles the "Get Info" click and we just check the state here.
    # But wait, the component is static.
    
    # Let's enable the button only if we have a URL. The user's request "disable... before we fetch video info"
    # suggests a strict workflow.
    
    # Let's use the `youtube_data` to see if we can pass a signal.
    # Actually, the cleanest way is to move the "Get Transcript" button inside the component
    # or have the component return the verification status.
    
    # Let's look at how `render_youtube_tab` is implemented. It returns a dict.
    # We can add `video_verified` to that dict.
    
    is_verified = youtube_data.get("video_verified", False)

    if st.button("Get Transcript", key="youtube_btn", disabled=st.session_state.processing or not is_verified):
        if not youtube_url:
            st.error("❌ Please enter a YouTube URL")
        else:
            # Reset previous results
            st.session_state.transcript_result = None
            st.session_state.summary_result = None
            st.session_state.key_points = None
            st.session_state.refined_message = None

            # Add time range to settings
            settings["start_time"] = youtube_data.get("start_time")
            settings["end_time"] = youtube_data.get("end_time")

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

            # Display video title if available
            if result.get("title"):
                st.markdown(f"### 📺 {result['title']}")

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
