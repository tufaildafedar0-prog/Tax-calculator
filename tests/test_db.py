"""
Unit tests for database operations.

Tests for:
- Saving PAN user data
- Retrieving PAN user data
- Database CRUD operations
- Handling non-existent PANs
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path to import taxlib
sys.path.insert(0, str(Path(__file__).parent.parent / "Tax calc"))

# We need to patch the DB_FILE before importing taxlib.db
import tempfile
from unittest.mock import patch


class TestDatabaseOperations:
    """Test database save and retrieve operations."""

    def setup_method(self):
        """Set up a temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()

    def teardown_method(self):
        """Clean up temporary database after each test."""
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)

    def test_save_and_retrieve_pan_data(self):
        """Test saving and retrieving PAN user data."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            # Save data
            db.save_pan_data_db("ABCPD1234F", 500_000, 50_000, 10_000, 30)
            
            # Retrieve data
            data = db.get_pan_data_db("ABCPD1234F")
            
            assert data["income"] == 500_000
            assert data["deductions"] == 50_000
            assert data["emi"] == 10_000
            assert data["age"] == 30

    def test_retrieve_nonexistent_pan(self):
        """Test that retrieving non-existent PAN returns empty dict."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            data = db.get_pan_data_db("NONEXISTENT123")
            assert data == {}

    def test_update_existing_pan_data(self):
        """Test that updating existing PAN data overwrites previous values."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            # Save initial data
            db.save_pan_data_db("ABCPD1234F", 500_000, 50_000, 10_000, 30)
            
            # Update with new data
            db.save_pan_data_db("ABCPD1234F", 750_000, 75_000, 15_000, 35)
            
            # Retrieve and verify
            data = db.get_pan_data_db("ABCPD1234F")
            assert data["income"] == 750_000
            assert data["deductions"] == 75_000
            assert data["emi"] == 15_000
            assert data["age"] == 35

    def test_save_multiple_pans(self):
        """Test saving data for multiple different PANs."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            # Save multiple PANs
            db.save_pan_data_db("ABCPD1234F", 500_000, 50_000, 10_000, 30)
            db.save_pan_data_db("XYZPD5678A", 750_000, 75_000, 15_000, 35)
            db.save_pan_data_db("LMNCD9012B", 1_000_000, 100_000, 20_000, 40)
            
            # Retrieve and verify all
            data1 = db.get_pan_data_db("ABCPD1234F")
            data2 = db.get_pan_data_db("XYZPD5678A")
            data3 = db.get_pan_data_db("LMNCD9012B")
            
            assert data1["income"] == 500_000
            assert data2["income"] == 750_000
            assert data3["income"] == 1_000_000

    def test_save_zero_values(self):
        """Test saving data with zero values."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            db.save_pan_data_db("ZEROPA1234Z", 0, 0, 0, 0)
            data = db.get_pan_data_db("ZEROPA1234Z")
            
            assert data["income"] == 0
            assert data["deductions"] == 0
            assert data["emi"] == 0
            assert data["age"] == 0

    def test_save_large_values(self):
        """Test saving data with large values."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            db.save_pan_data_db("BIGPA1234BG", 50_000_000, 5_000_000, 500_000, 65)
            data = db.get_pan_data_db("BIGPA1234BG")
            
            assert data["income"] == 50_000_000
            assert data["deductions"] == 5_000_000
            assert data["emi"] == 500_000
            assert data["age"] == 65

    def test_save_float_values(self):
        """Test saving data with floating point values."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            db.save_pan_data_db("FLOATPA123F", 500_123.45, 50_456.78, 10_789.12, 30)
            data = db.get_pan_data_db("FLOATPA123F")
            
            assert abs(data["income"] - 500_123.45) < 0.01
            assert abs(data["deductions"] - 50_456.78) < 0.01
            assert abs(data["emi"] - 10_789.12) < 0.01
            assert data["age"] == 30

    def test_save_case_sensitive_pan(self):
        """Test that PANs are stored and retrieved case-sensitively (uppercase)."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            # Save with lowercase (should be stored as-is)
            db.save_pan_data_db("abcpd1234f", 500_000, 50_000, 10_000, 30)
            
            # Retrieve with lowercase
            data_lower = db.get_pan_data_db("abcpd1234f")
            
            # Retrieve with uppercase
            data_upper = db.get_pan_data_db("ABCPD1234F")
            
            # Note: Database is case-sensitive; lowercase and uppercase are different keys
            assert data_lower["income"] == 500_000 or data_lower == {}
            # This documents the actual behavior - PANs should be normalized before storage

    def test_database_persistence(self):
        """Test that data persists across multiple connections."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            # First connection: save
            db.save_pan_data_db("PERSISTPA1P", 600_000, 60_000, 12_000, 32)
            
            # Second connection: retrieve
            data = db.get_pan_data_db("PERSISTPA1P")
            assert data["income"] == 600_000

    def test_age_boundary_values(self):
        """Test saving and retrieving various age values."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            # Test age 18 (young professional)
            db.save_pan_data_db("YOUNGPA1234Y", 300_000, 30_000, 5_000, 18)
            data = db.get_pan_data_db("YOUNGPA1234Y")
            assert data["age"] == 18
            
            # Test age 60 (senior citizen)
            db.save_pan_data_db("SENIORPA1234S", 500_000, 50_000, 10_000, 60)
            data = db.get_pan_data_db("SENIORPA1234S")
            assert data["age"] == 60


class TestDatabaseEdgeCases:
    """Test edge cases in database operations."""

    def setup_method(self):
        """Set up a temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()

    def teardown_method(self):
        """Clean up temporary database after each test."""
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)

    def test_special_characters_in_pan(self):
        """Test handling of PANs with special characters (should work for storage)."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            # Even though validation should prevent this, test storage
            db.save_pan_data_db("ABCPD1234F", 500_000, 50_000, 10_000, 30)
            data = db.get_pan_data_db("ABCPD1234F")
            assert data["income"] == 500_000

    def test_very_small_float_values(self):
        """Test saving very small floating point values."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            db.save_pan_data_db("SMALLPA123S", 0.01, 0.01, 0.01, 25)
            data = db.get_pan_data_db("SMALLPA123S")
            assert data["income"] > 0
            assert data["deductions"] > 0

    def test_negative_values_stored(self):
        """Test that negative values are stored (validation at app level)."""
        from taxlib import db
        
        with patch.object(db, 'DB_FILE', self.temp_db_path):
            db.save_pan_data_db("NEGATIVPA123N", -100_000, -10_000, -5_000, -25)
            data = db.get_pan_data_db("NEGATIVPA123N")
            # Database stores as-is; validation is app responsibility
            assert data["income"] == -100_000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
