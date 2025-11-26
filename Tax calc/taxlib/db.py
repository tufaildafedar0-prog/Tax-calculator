"""
SQLite database operations for persisting user PAN data and financial inputs.
"""

import sqlite3
from datetime import datetime

DB_FILE = "tax_calculator.db"


def _get_connection():
    """
    Get or create SQLite connection and initialize schema.

    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS pan_users (
        pan TEXT PRIMARY KEY,
        income REAL,
        deductions REAL,
        emi REAL,
        age INTEGER,
        timestamp TEXT
    )
    ''')
    conn.commit()
    return conn


def save_pan_data_db(pan, income, deductions, emi, age):
    """
    Save or update PAN user data in the database.

    Args:
        pan (str): PAN number
        income (float): Annual income
        deductions (float): Total deductions
        emi (float): Monthly EMI
        age (int): Age
    """
    conn = _get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
    INSERT INTO pan_users (pan, income, deductions, emi, age, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(pan) DO UPDATE SET
        income=excluded.income,
        deductions=excluded.deductions,
        emi=excluded.emi,
        age=excluded.age,
        timestamp=excluded.timestamp
    ''', (pan, income, deductions, emi, age, now))
    conn.commit()
    conn.close()


def get_pan_data_db(pan):
    """
    Retrieve saved PAN user data from the database.

    Args:
        pan (str): PAN number

    Returns:
        dict: {income, deductions, emi, age} or empty dict if not found
    """
    conn = _get_connection()
    c = conn.cursor()
    c.execute("SELECT income, deductions, emi, age FROM pan_users WHERE pan=?", (pan,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"income": row[0], "deductions": row[1], "emi": row[2], "age": row[3]}
    return {}
