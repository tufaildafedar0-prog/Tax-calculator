import os
import sys
import tempfile
import sqlite3
import pytest

# Ensure the project package path ("Tax calc/Tax calc") is on sys.path so tests
# can import the `taxlib` package when running from repository root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGE_PATH = os.path.join(PROJECT_ROOT, 'Tax calc')
if PACKAGE_PATH not in sys.path:
    sys.path.insert(0, PACKAGE_PATH)

from taxlib import calculate_individual_tax, calculate_corporate_tax
from taxlib.db import DB_FILE, save_pan_data_db, get_pan_data_db


def test_individual_and_db_roundtrip(tmp_path, monkeypatch):
    # Use an isolated DB file in the temp directory
    db_file = tmp_path / "test_db.sqlite"

    # Monkeypatch the DB_FILE constant used by db module
    monkeypatch.setattr('taxlib.db.DB_FILE', str(db_file))

    pan = "ABCDP1234F"
    income = 850000.0
    deductions = 75000.0
    emi = 10000.0
    age = 30

    # Save to DB
    save_pan_data_db(pan, income, deductions, emi, age)

    # Retrieve and verify
    data = get_pan_data_db(pan)
    assert data, "Expected data to be returned from DB"
    assert data["income"] == pytest.approx(income)
    assert data["deductions"] == pytest.approx(deductions)
    assert data["emi"] == pytest.approx(emi)
    assert data["age"] == age

    # Calculate tax using the same inputs
    total_tax, slab, steps = calculate_individual_tax(income, deductions, age)

    # Basic sanity checks for tax calculation
    assert steps["gross"] == pytest.approx(income)
    assert steps["deductions"] == pytest.approx(deductions)
    assert steps["taxable"] == pytest.approx(max(0, income - deductions))
    assert total_tax >= 0


def test_corporate_tax_basic():
    gross = 6_000_000
    deductions = 0
    total_tax, slab, steps = calculate_corporate_tax(gross, deductions, "Company")

    # For gross > 5,000,000 rate should be 30%
    expected_tax_before = (gross - deductions) * 0.30
    expected_total = round(expected_tax_before * 1.04, 2)

    assert steps["tax_before"] == pytest.approx(round(expected_tax_before, 2))
    assert steps["total"] == pytest.approx(expected_total)
