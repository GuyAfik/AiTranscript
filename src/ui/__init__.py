"""
UI module for AiTranscript.

This module contains Streamlit UI components and styling utilities.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .components import UIComponents

__all__ = [
    "UIComponents",
]