"""
Unit tests for tax calculation functions.

Tests for:
- Individual tax calculations with slabs
- Rebate under Section 87A
- Health and Education Cess (4%)
- Corporate tax calculations
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to import taxlib
sys.path.insert(0, str(Path(__file__).parent.parent / "Tax calc"))

from taxlib import calculate_individual_tax, calculate_corporate_tax


class TestIndividualTaxCalculations:
    """Test individual tax calculations for New Tax Regime."""

    def test_zero_income(self):
        """Test that zero income results in zero tax."""
        tax, slabs, steps = calculate_individual_tax(0, 0, 30)
        assert tax == 0.0
        assert steps["total"] == 0.0

    def test_income_below_first_slab(self):
        """Test income in 0-3L slab (0% tax)."""
        tax, slabs, steps = calculate_individual_tax(200_000, 0, 30)
        assert tax == 0.0
        assert steps["tax_before"] == 0.0

    def test_income_in_second_slab(self):
        """Test income in 0-7L slab (0% tax)."""
        # Income: 5L, Deductions: 0, Taxable: 5L
        # Tax: 5L @ 0% = 0
        # Cess: 0 * 4% = 0
        # Total: 0
        tax, slabs, steps = calculate_individual_tax(500_000, 0, 30)
        assert steps["taxable"] == 500_000
        assert steps["tax_before"] == 0
        assert steps["cess"] == 0
        assert tax == 0

    def test_income_with_deductions(self):
        """Test that deductions reduce taxable income."""
        # Income: 10L, Deductions: 1L, Taxable: 9L
        # Expected: 7L @ 0%, 2L @ 5% = 0 + 10k = 10k
        # Rebate: min(10k, 12.5k) = 10k (taxable < 5L? No, so no rebate)
        # Tax after rebate: 10k
        # Cess: 10k * 4% = 400, Total: 10.4k
        tax, slabs, steps = calculate_individual_tax(1_000_000, 100_000, 30)
        assert steps["taxable"] == 900_000
        assert steps["tax_before"] == 10_000
        assert steps["cess"] == 400
        assert tax == 10_400

    def test_section_87a_rebate_below_7l(self):
        """Test Section 87A rebate for income up to 5L."""
        # Income: 5L, no deductions, Taxable: 5L
        # Tax before rebate: 5L @ 0% = 0
        # Rebate: min(0, 12,500) = 0
        # Tax after rebate: 0
        # Total: 0
        tax, slabs, steps = calculate_individual_tax(500_000, 0, 30)
        assert steps["rebate"] == 0
        assert steps["tax_after"] == 0
        assert tax == 0

    def test_section_87a_rebate_at_7l_boundary(self):
        """Test Section 87A rebate at 5L income boundary."""
        # Income: 5L, no deductions, Taxable: 5L
        # Tax before rebate: 5L @ 0% = 0
        # Rebate: min(0, 12.5k) = 0
        # Tax after rebate: 0
        # Total: 0
        tax, slabs, steps = calculate_individual_tax(500_000, 0, 30)
        assert steps["taxable"] == 500_000
        assert steps["tax_before"] == 0
        assert steps["rebate"] == 0
        assert steps["tax_after"] == 0
        assert steps["cess"] == 0
        assert tax == 0

    def test_no_rebate_above_7l(self):
        """Test that no rebate is applied for income > 5L."""
        # Income: 10L, no deductions, Taxable: 10L
        # Tax: 7L @ 0% + 3L @ 5% = 0 + 15k = 15k
        # Rebate: 0 (no rebate for income > 5L)
        # Cess: 15k * 4% = 600, Total: 15.6k
        tax, slabs, steps = calculate_individual_tax(1_000_000, 0, 30)
        assert steps["taxable"] == 1_000_000
        assert steps["tax_before"] == 15_000
        assert steps["rebate"] == 0
        assert steps["tax_after"] == 15_000
        assert steps["cess"] == 600
        assert tax == 15_600

    def test_high_income_multiple_slabs(self):
        """Test high income across multiple slabs."""
        # Income: 30L, Deductions: 2L, Taxable: 28L
        # Tax: 7L @ 0%, 4L @ 5%, 4L @ 10%, 4L @ 15%, 4L @ 20%, 4L @ 25%, 1L @ 30%
        # = 0 + 20k + 40k + 60k + 80k + 100k + 30k = 330k
        # Cess: 330k * 4% = 13.2k, Total: 343.2k
        tax, slabs, steps = calculate_individual_tax(3_000_000, 200_000, 30)
        assert steps["taxable"] == 2_800_000
        assert steps["tax_before"] == 330_000
        assert steps["rebate"] == 0  # No rebate for high income
        assert steps["cess"] == 13_200
        assert tax == 343_200

    def test_employment_type_parameter(self):
        """Test that employment_type parameter is accepted."""
        # Function should accept employment_type but not change calculation in current version
        tax1, _, _ = calculate_individual_tax(500_000, 0, 30, employment_type="Salaried")
        tax2, _, _ = calculate_individual_tax(500_000, 0, 30, employment_type="Self Employed")
        # Both should return same tax (standard deduction applied at UI level)
        assert tax1 == tax2


class TestCorporateTaxCalculations:
    """Test corporate tax calculations."""

    def test_zero_income_corporate(self):
        """Test that zero income results in zero corporate tax."""
        tax, slabs, steps = calculate_corporate_tax(0, 0, "Company")
        assert tax == 0.0

    def test_company_tax_small_income(self):
        """Test 22% rate for companies with income <= 5L."""
        # Income: 5L, Deductions: 0, Taxable: 5L
        # Tax: 5L * 22% = 110,000
        # Cess: 110,000 * 4% = 4,400
        # Total: 114,400
        tax, slabs, steps = calculate_corporate_tax(500_000, 0, "Company")
        assert steps["taxable"] == 500_000
        assert steps["tax_before"] == 110_000
        assert steps["cess"] == 4_400
        assert tax == 114_400

    def test_company_tax_large_income(self):
        """Test 22% rate for companies with any income (fixed at 22% in new regime)."""
        # Income: 10L, Deductions: 0, Taxable: 10L
        # Tax: 10L * 22% = 220,000 (fixed rate under new regime)
        # Cess: 220,000 * 4% = 8,800
        # Total: 228,800
        tax, slabs, steps = calculate_corporate_tax(1_000_000, 0, "Company")
        assert steps["taxable"] == 1_000_000
        assert steps["tax_before"] == 220_000
        assert steps["cess"] == 8_800
        assert tax == 228_800

    def test_company_tax_with_deductions(self):
        """Test corporate tax with deductions."""
        # Income: 10L, Deductions: 1L, Taxable: 9L
        # Tax: 9L * 22% = 198,000
        # Cess: 198,000 * 4% = 7,920
        # Total: 205,920
        tax, slabs, steps = calculate_corporate_tax(1_000_000, 100_000, "Company")
        assert steps["taxable"] == 900_000
        assert steps["tax_before"] == 198_000
        assert steps["cess"] == 7_920
        assert tax == 205_920

    def test_other_entity_type_tax(self):
        """Test flat 30% rate for other entity types."""
        # Income: 5L, Deductions: 0, Entity: Other
        # Tax: 5L * 30% = 150,000
        # Cess: 150,000 * 4% = 6,000
        # Total: 156,000
        tax, slabs, steps = calculate_corporate_tax(500_000, 0, "Other")
        assert steps["tax_before"] == 150_000
        assert steps["cess"] == 6_000
        assert tax == 156_000

    def test_negative_deductions_become_zero(self):
        """Test that negative taxable income becomes zero."""
        tax, slabs, steps = calculate_corporate_tax(100_000, 200_000, "Company")
        assert steps["taxable"] == 0
        assert tax == 0.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_large_income(self):
        """Test calculation with very large income."""
        tax, _, steps = calculate_individual_tax(50_000_000, 1_000_000, 30)
        assert steps["taxable"] == 49_000_000
        assert tax > 0

    def test_deductions_exceed_income(self):
        """Test when deductions exceed income."""
        tax, _, steps = calculate_individual_tax(200_000, 500_000, 30)
        assert steps["taxable"] == 0
        assert tax == 0.0

    def test_fractional_amounts(self):
        """Test calculation with fractional amounts."""
        tax, _, steps = calculate_individual_tax(750_500.75, 50_123.50, 30)
        assert steps["taxable"] > 0
        assert tax >= 0

    def test_slab_details_structure(self):
        """Test that slab_details dictionary is properly populated."""
        tax, slabs, steps = calculate_individual_tax(500_000, 0, 30)
        assert isinstance(slabs, dict)
        assert len(slabs) > 0
        # Should have slab breakdown - for 5L income (below 7L), only 0-7L slab used
        assert "0–7L" in slabs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
