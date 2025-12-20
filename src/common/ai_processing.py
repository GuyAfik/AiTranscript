"""
Shared AI Processing Logic

This module contains shared logic for processing transcripts with AI.
"""

import streamlit as st
import logging
from typing import Dict, Any
from src.common.ai_service import AICleanupService
from src.utils.config import get_config
from src.ui.components import UIComponents

logger = logging.getLogger(__name__)

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
            api_key=settings.get("api_key"),
            model=settings.get(
                "ai_model",
                "llama2" if settings.get("ai_provider") == "local" else get_config().openai_model,
            ),
            provider=settings.get("ai_provider", "local"),
        )

        processing_mode = settings.get("processing_mode", "summarize")

        if processing_mode == "summarize":
            # Summarization mode
            with st.spinner("🤖 Generating AI summary..."):
                summary = ai_service.summarize_text(transcript, style=settings["summary_style"])
                st.session_state.summary_result = summary

                # Generate key points if requested
                if settings["generate_key_points"]:
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
                    tone=settings.get("message_tone", "professional"),
                    recipient_context=settings.get("recipient_context"),
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
                "Try again in a few moments",
            ],
        )