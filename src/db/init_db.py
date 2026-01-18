"""
Database Initialization Script
Creates and populates the mock SQLite database for Customer Support testing.

Archetypes:
- happy_customer: Active customer with positive balance and successful transactions
- blocked_user: Account blocked due to fraud
- broke_merchant: Active merchant with zero balance and failed transactions
- new_user: New user with no history
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
            user_id TEXT PRIMARY KEY,
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
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
        
        CREATE TABLE cards (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            last_4 TEXT,
            status TEXT, -- 'active', 'blocked'
            limit_amount REAL,
            used_amount REAL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
    """)
    
    logger.info("Populating mock data with 4 archetypes...")
    
    now = datetime.now()
    
    # ============================================================
    # ARCHETYPE 1: happy_customer - Cliente Satisfeito
    # ============================================================
    cursor.execute(
        "INSERT INTO users VALUES (?,?,?,?,?)",
        ('happy_customer', 'Ana Feliz', 15250.00, 'active', None)
    )
    
    happy_transactions = [
        ('tx_happy_001', 'happy_customer', 'pix_out', 500.00, 'completed', None, 
         (now - timedelta(hours=3)).isoformat(), 'Loja ABC'),
        ('tx_happy_002', 'happy_customer', 'card_sale', 1200.00, 'completed', None, 
         (now - timedelta(days=1)).isoformat(), 'Cliente Maria'),
        ('tx_happy_003', 'happy_customer', 'pix_in', 3000.00, 'completed', None, 
         (now - timedelta(days=2)).isoformat(), 'Cliente XYZ'),
        ('tx_happy_004', 'happy_customer', 'payout', 5000.00, 'completed', None, 
         (now - timedelta(days=3)).isoformat(), 'InfinitePay Settlement'),
    ]
    cursor.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)", happy_transactions)
    
    cursor.execute(
        "INSERT INTO cards VALUES (?,?,?,?,?,?)",
        ('card_happy_001', 'happy_customer', '1234', 'active', 10000.00, 2000.00)
    )
    
    # ============================================================
    # ARCHETYPE 2: blocked_user - Usuário Bloqueado
    # ============================================================
    cursor.execute(
        "INSERT INTO users VALUES (?,?,?,?,?)",
        ('blocked_user', 'Carlos Bloqueado', 0.00, 'blocked', 'Atividade fraudulenta detectada')
    )
    
    blocked_transactions = [
        ('tx_blocked_001', 'blocked_user', 'pix_out', 10000.00, 'failed', 'Account blocked', 
         (now - timedelta(hours=1)).isoformat(), 'Conta Suspeita'),
        ('tx_blocked_002', 'blocked_user', 'pix_in', 500.00, 'completed', None, 
         (now - timedelta(days=5)).isoformat(), 'João Silva'),
    ]
    cursor.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)", blocked_transactions)
    
    cursor.execute(
        "INSERT INTO cards VALUES (?,?,?,?,?,?)",
        ('card_blocked_001', 'blocked_user', '5678', 'blocked', 5000.00, 5000.00)
    )
    
    # ============================================================
    # ARCHETYPE 3: broke_merchant - Comerciante Sem Saldo
    # ============================================================
    cursor.execute(
        "INSERT INTO users VALUES (?,?,?,?,?)",
        ('broke_merchant', 'Pedro Quebrado', 0.00, 'active', None)
    )
    
    broke_transactions = [
        ('tx_broke_001', 'broke_merchant', 'transfer', 1000.00, 'failed', 'Insufficient funds', 
         (now - timedelta(hours=2)).isoformat(), 'Fornecedor ABC'),
        ('tx_broke_002', 'broke_merchant', 'pix_out', 200.00, 'failed', 'Insufficient funds', 
         (now - timedelta(hours=5)).isoformat(), 'Aluguel Loja'),
        ('tx_broke_003', 'broke_merchant', 'card_sale', 150.00, 'completed', None, 
         (now - timedelta(days=1)).isoformat(), 'Cliente Pedro'),
        ('tx_broke_004', 'broke_merchant', 'payout', 2500.00, 'pending', None, 
         (now - timedelta(minutes=30)).isoformat(), 'InfinitePay Settlement'),
    ]
    cursor.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)", broke_transactions)
    
    cursor.execute(
        "INSERT INTO cards VALUES (?,?,?,?,?,?)",
        ('card_broke_001', 'broke_merchant', '9999', 'active', 3000.00, 3000.00)  # Limite estourado
    )
    
    # ============================================================
    # ARCHETYPE 4: new_user - Usuário Novo
    # ============================================================
    cursor.execute(
        "INSERT INTO users VALUES (?,?,?,?,?)",
        ('empty_user', 'Marina Nova', 0.00, 'active', None)
    )
    # No transactions and no cards for new_user
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH} with 4 archetypes")
    logger.info("  - happy_customer: Ana Feliz (active, R$ 15.250)")
    logger.info("  - blocked_user: Carlos Bloqueado (blocked)")
    logger.info("  - broke_merchant: Pedro Quebrado (active, R$ 0)")
    logger.info("  - new_user: Marina Nova (active, no history)")

if __name__ == "__main__":
    init_db()
