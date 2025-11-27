"""
Database module for storing fraud detection predictions
Uses SQLite for lightweight, serverless data storage
"""

import sqlite3
from datetime import datetime
import json
import os
from contextlib import contextmanager

DB_PATH = 'fraud_detection.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize database schema"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Predictions table - stores all fraud predictions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                amount REAL NOT NULL,
                merchant_state TEXT,
                merchant_city TEXT,
                merchant_category TEXT,
                mcc INTEGER,
                use_chip TEXT,
                user_id INTEGER,
                card_id INTEGER,
                is_fraud INTEGER NOT NULL,
                fraud_probability REAL NOT NULL,
                risk_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                prediction_time_ms REAL,
                model_version TEXT DEFAULT '1.0.0'
            )
        ''')

        # Create indices for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON predictions(timestamp DESC)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_is_fraud
            ON predictions(is_fraud)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_risk_level
            ON predictions(risk_level)
        ''')

        print("Database initialized successfully")

def save_prediction(prediction_data):
    """
    Save a fraud prediction to the database

    Args:
        prediction_data: Dictionary containing prediction details

    Returns:
        int: ID of the saved prediction
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO predictions (
                transaction_id, amount, merchant_state, merchant_city,
                merchant_category, mcc, use_chip, user_id, card_id,
                is_fraud, fraud_probability, risk_score, risk_level,
                prediction_time_ms, model_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction_data.get('transaction_id'),
            prediction_data.get('amount'),
            prediction_data.get('merchant_state'),
            prediction_data.get('merchant_city'),
            prediction_data.get('merchant_category'),
            prediction_data.get('mcc'),
            prediction_data.get('use_chip'),
            prediction_data.get('user_id'),
            prediction_data.get('card_id'),
            1 if prediction_data.get('is_fraud') else 0,
            prediction_data.get('fraud_probability'),
            prediction_data.get('risk_score'),
            prediction_data.get('risk_level'),
            prediction_data.get('prediction_time_ms'),
            prediction_data.get('model_version', '1.0.0')
        ))

        return cursor.lastrowid

def get_recent_predictions(limit=100):
    """Get most recent predictions"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM predictions
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_fraud_statistics(hours=24):
    """Get fraud statistics for the last N hours"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total transactions
        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count,
                   AVG(fraud_probability) as avg_fraud_prob,
                   SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END) as fraud_amount
            FROM predictions
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        ''', (hours,))

        result = cursor.fetchone()
        if result:
            return dict(result)
        return {}

def get_alerts(severity=None, limit=50):
    """Get fraud alerts (high-risk predictions)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        query = '''
            SELECT * FROM predictions
            WHERE fraud_probability >= 0.5
        '''
        params = []

        if severity:
            if severity == 'critical':
                query += ' AND fraud_probability >= 0.9'
            elif severity == 'high':
                query += ' AND fraud_probability >= 0.7 AND fraud_probability < 0.9'
            elif severity == 'medium':
                query += ' AND fraud_probability >= 0.5 AND fraud_probability < 0.7'

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_hourly_statistics(hours=24):
    """Get hourly transaction statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as transaction_count,
                SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count,
                AVG(fraud_probability) as avg_fraud_prob,
                SUM(amount) as total_amount
            FROM predictions
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            GROUP BY hour
            ORDER BY hour DESC
        ''', (hours,))

        return [dict(row) for row in cursor.fetchall()]

def get_risk_distribution():
    """Get distribution of risk levels"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                risk_level,
                COUNT(*) as count,
                AVG(fraud_probability) as avg_prob
            FROM predictions
            GROUP BY risk_level
        ''')

        return [dict(row) for row in cursor.fetchall()]

def get_merchant_statistics():
    """Get statistics by merchant location"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                merchant_state,
                merchant_city,
                COUNT(*) as transaction_count,
                SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count,
                AVG(fraud_probability) as avg_fraud_prob,
                SUM(amount) as total_amount
            FROM predictions
            WHERE merchant_state IS NOT NULL
            GROUP BY merchant_state, merchant_city
            HAVING transaction_count > 0
            ORDER BY fraud_count DESC
            LIMIT 50
        ''')

        return [dict(row) for row in cursor.fetchall()]

# Initialize database on module import
if not os.path.exists(DB_PATH):
    print(f"Creating new database at {DB_PATH}")
    init_database()
else:
    # Ensure schema is up to date
    init_database()
