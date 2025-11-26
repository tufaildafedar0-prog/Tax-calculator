"""
Unit tests for PAN validation and entity type detection.

Tests for:
- PAN format validation
- Entity type detection (Individual, Company, Other)
- Edge cases and invalid formats
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to import taxlib
sys.path.insert(0, str(Path(__file__).parent.parent / "Tax calc"))

from taxlib import validate_pan, get_pan_entity_type


class TestPANValidation:
    """Test PAN format validation."""

    def test_valid_individual_pan(self):
        """Test valid Individual PAN with P at position 3."""
        assert validate_pan("ABCPD1234F") is True

    def test_valid_company_pan(self):
        """Test valid Company PAN with C at position 3."""
        assert validate_pan("ABCCD1234F") is True

    def test_valid_other_pan(self):
        """Test valid PAN with other character at position 3."""
        assert validate_pan("ABCXD1234F") is True

    def test_invalid_lowercase_pan(self):
        """Test that lowercase PAN is converted and validated."""
        # Should be case-insensitive
        assert validate_pan("abcpd1234f") is True

    def test_invalid_short_pan(self):
        """Test that short PAN fails validation."""
        assert validate_pan("ABCD1234F") is False

    def test_invalid_long_pan(self):
        """Test that long PAN fails validation."""
        assert validate_pan("ABCDX12345F") is False

    def test_invalid_all_letters(self):
        """Test that all-letter PAN fails validation."""
        assert validate_pan("ABCDEFGHIJ") is False

    def test_invalid_all_numbers(self):
        """Test that all-number PAN fails validation."""
        assert validate_pan("12345678901") is False

    def test_invalid_special_characters(self):
        """Test that PAN with special characters fails."""
        assert validate_pan("ABC@D1234F") is False
        assert validate_pan("ABCD-1234F") is False

    def test_invalid_spaces(self):
        """Test that PAN with spaces fails."""
        assert validate_pan("ABCD D1234F") is False

    def test_empty_pan(self):
        """Test that empty PAN fails."""
        assert validate_pan("") is False

    def test_valid_pan_format_exact_length(self):
        """Test valid PAN with exactly 10 characters."""
        # Format: 5 letters + 4 digits + 1 letter
        assert validate_pan("AAAAA0000A") is True
        assert validate_pan("ZZZZZ9999Z") is True

    def test_pan_numbers_in_wrong_position(self):
        """Test that numbers in letter positions fail."""
        assert validate_pan("ABC1D1234F") is False  # Number at position 3
        assert validate_pan("1BCDP1234F") is False  # Number at position 0

    def test_pan_letters_in_number_positions(self):
        """Test that letters in number positions fail."""
        assert validate_pan("ABCDPABCDF") is False  # Letters instead of numbers
        assert validate_pan("ABCDP123AF") is False  # Letter in middle of number block


class TestPANEntityTypeDetection:
    """Test PAN entity type detection."""

    def test_individual_pan_detection(self):
        """Test detection of Individual PAN (P at position 3)."""
        assert get_pan_entity_type("ABCPD1234F") == "Individual"

    def test_company_pan_detection(self):
        """Test detection of Company PAN (C at position 3)."""
        assert get_pan_entity_type("ABCCD1234F") == "Company"

    def test_other_pan_detection(self):
        """Test detection of Other entity type (other characters at position 3)."""
        assert get_pan_entity_type("ABCXD1234F") == "Other"
        assert get_pan_entity_type("ABCAD1234F") == "Other"
        assert get_pan_entity_type("ABCZD1234F") == "Other"

    def test_entity_type_case_insensitive(self):
        """Test that entity type detection is case-insensitive."""
        assert get_pan_entity_type("abcpd1234f") == "Individual"
        assert get_pan_entity_type("abccd1234f") == "Company"
        assert get_pan_entity_type("abcxd1234f") == "Other"

    def test_entity_type_numeric_character(self):
        """Test entity type with numeric character at position 3 (Other)."""
        # Position 3 should be a letter, but if numeric, it's "Other"
        # Note: This would fail PAN validation, so it's an edge case
        # Testing the function's behavior on invalid input
        assert get_pan_entity_type("ABC1D1234F") == "Other"  # '1' is not P or C

    def test_entity_type_lowercase_p(self):
        """Test that lowercase 'p' is detected as Individual."""
        assert get_pan_entity_type("abcpd1234f") == "Individual"

    def test_entity_type_lowercase_c(self):
        """Test that lowercase 'c' is detected as Company."""
        assert get_pan_entity_type("abccd1234f") == "Company"

    def test_all_alphabet_position_3_variants(self):
        """Test all alphabet characters at position 3."""
        # P and C should be recognized; others should be "Other"
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            pan = f"ABC{char}D1234F"
            if char == "P":
                assert get_pan_entity_type(pan) == "Individual"
            elif char == "C":
                assert get_pan_entity_type(pan) == "Company"
            else:
                assert get_pan_entity_type(pan) == "Other"


class TestPANIntegration:
    """Integration tests for validation and entity detection."""

    def test_valid_pan_and_entity_detection_individual(self):
        """Test that valid Individual PAN passes validation and is detected correctly."""
        pan = "ABCPD1234F"
        assert validate_pan(pan) is True
        assert get_pan_entity_type(pan) == "Individual"

    def test_valid_pan_and_entity_detection_company(self):
        """Test that valid Company PAN passes validation and is detected correctly."""
        pan = "ABCCD1234F"
        assert validate_pan(pan) is True
        assert get_pan_entity_type(pan) == "Company"

    def test_real_world_pan_formats(self):
        """Test with realistic PAN patterns."""
        # Realistic Individual PAN (P at position 3)
        ind_pan = "AAAPA0000A"
        assert validate_pan(ind_pan) is True
        assert get_pan_entity_type(ind_pan) == "Individual"

        # Realistic Company PAN (C at position 3)
        co_pan = "AAACA0000A"
        assert validate_pan(co_pan) is True
        assert get_pan_entity_type(co_pan) == "Company"

    def test_pan_validation_fails_before_entity_detection(self):
        """Test that invalid PAN should be caught before entity detection.
        
        Note: Entity detection function doesn't validate format,
        so we test the workflow separately.
        """
        invalid_pan = "INVALID"
        assert validate_pan(invalid_pan) is False
        # Entity detection may still work on partial input (implementation detail)
        # but validation is the primary check


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
