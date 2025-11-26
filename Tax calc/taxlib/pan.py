"""
PAN validation and entity type detection.
"""

import re


def validate_pan(pan):
    """
    Validate PAN format.

    Args:
        pan (str): PAN string

    Returns:
        bool: True if valid, False otherwise

    Format: ^[A-Z]{5}[0-9]{4}[A-Z]$
    Example: ABCDP1234F
    """
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return bool(re.match(pattern, pan.upper()))


def get_pan_entity_type(pan):
    """
    Detect entity type from PAN 4th character.

    Args:
        pan (str): PAN string

    Returns:
        str: "Individual" (P), "Company" (C), or "Other"

    PAN Format: AAAA[X]NNNNC
    - Position 3 (0-indexed) indicates entity type:
      - 'P' → Individual
      - 'C' → Company
      - anything else → Other
    """
    c = pan[3].upper()
    if c == 'P':
        return "Individual"
    elif c == 'C':
        return "Company"
    else:
        return "Other"
