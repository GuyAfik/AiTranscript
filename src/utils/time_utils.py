"""
Time Utility Functions

This module provides utility functions for handling time-related operations,
such as parsing time strings into seconds.
"""

import re
from typing import Optional


def parse_time_string(time_str: str) -> Optional[int]:
    """
    Parse a time string into seconds.

    Supported formats:
    - "SS" (e.g., "90")
    - "MM:SS" (e.g., "1:30")
    - "HH:MM:SS" (e.g., "1:01:30")

    Args:
        time_str: Time string to parse

    Returns:
        Number of seconds as integer, or None if invalid format
    """
    if not time_str:
        return None

    time_str = time_str.strip()

    # Check for simple seconds
    if time_str.isdigit():
        return int(time_str)

    # Check for MM:SS or HH:MM:SS
    # Allow single digit for hours/minutes/seconds
    parts = time_str.split(":")
    
    try:
        if len(parts) == 2:
            # MM:SS
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:
            # HH:MM:SS
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        pass

    return None