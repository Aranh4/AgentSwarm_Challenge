"""
Database Initialization Script
Creates and populates the mock SQLite database for Customer Support testing.
"""

import sqlite3
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "data/customers.db"

def init_db():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    logger.info("Creating tables...")
    
    # Tables
    cursor.executescript("""
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS cards;
        
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            account_status TEXT DEFAULT 'active',
            block_reason TEXT
        );
        
        CREATE TABLE transactions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            type TEXT, -- 'pix_in', 'pix_out', 'card_sale', 'payout', 'transfer'
            amount REAL,
            status TEXT, -- 'completed', 'failed', 'pending'
            failure_reason TEXT,
            created_at DATETIME,
            counterparty TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        
        CREATE TABLE cards (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            last_4 TEXT,
            status TEXT, -- 'active', 'blocked'
            limit_amount REAL,
            used_amount REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    
    logger.info("Populating mock data...")
    
    # Mock Users
    users = [
        ('client789', 'Carlos Silva', 1250.50, 'active', None),
        ('user_blocked', 'Maria Blocked', 0.00, 'blocked', 'Suspicious activity detected'),
        ('jane_doe', 'Jane Doe', 5000.00, 'active', None)
    ]
    cursor.executemany("INSERT INTO users VALUES (?,?,?,?,?)", users)
    
    # Mock Transactions for client789
    now = datetime.now()
    transactions = [
        # Recent failed transfer
        ('tx_001', 'client789', 'transfer', 500.00, 'failed', 'Insufficient funds', (now - timedelta(hours=2)).isoformat(), 'Joao Santos'),
        # Successful Pix In
        ('tx_002', 'client789', 'pix_in', 100.00, 'completed', None, (now - timedelta(days=1)).isoformat(), 'Maria Souza'),
        # Payout
        ('tx_003', 'client789', 'payout', 2500.00, 'completed', None, (now - timedelta(days=2)).isoformat(), 'InfinitePay Settlement'),
        # Pending
        ('tx_004', 'client789', 'pix_out', 50.00, 'pending', None, (now - timedelta(minutes=10)).isoformat(), 'Pharmacy ABC')
    ]
    cursor.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)", transactions)
    
    # Mock Cards for client789
    cards = [
        ('card_001', 'client789', '4242', 'active', 2000.00, 1500.00)
    ]
    cursor.executemany("INSERT INTO cards VALUES (?,?,?,?,?,?)", cards)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
