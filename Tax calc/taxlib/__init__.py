"""
TaxLib — Core tax calculation and PAN validation library for TaxFlow Pro.

Provides:
- Tax calculations (individual & corporate)
- PAN validation & entity detection
- SQLite database operations for persisting user data
"""

from .calculations import calculate_individual_tax, calculate_corporate_tax
from .pan import validate_pan, get_pan_entity_type
from .db import save_pan_data_db, get_pan_data_db

__version__ = "1.0.0"
__all__ = [
    "calculate_individual_tax",
    "calculate_corporate_tax",
    "validate_pan",
    "get_pan_entity_type",
    "save_pan_data_db",
    "get_pan_data_db",
]
