"""Script para popular banco SQLite com dados mock"""
import sqlite3
from datetime import datetime, timedelta
import random
from pathlib import Path

# Configuração
DB_PATH = "./data/customers.db"


def create_tables(conn):
    """Cria tabelas se não existirem"""
    cursor = conn.cursor()
    
    # Tabela users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            account_status TEXT NOT NULL,
            plan TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            created_at TEXT NOT NULL
        )
    """)
    
    # Tabela transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()


def seed_users(conn):
    """Adiciona usuários fake para testes manuais e automatizados"""
    cursor = conn.cursor()
    
    users = [
        # --- TEST ARCHETYPES (Cruciais para comprehensive_test.py) ---
        
        # 1. Happy Customer: Satisfeito, saldo alto, tudo funcionando
        ("happy_customer", "Ana Feliz", "ana.feliz@email.com", "active", "premium", 15250.00, "2023-01-15"),
        
        # 2. Blocked User: Conta bloqueada, suspeita de fraude
        ("blocked_user", "Carlos Bloqueado", "carlos.block@email.com", "blocked", "basic", 0.00, "2023-02-10"),
        
        # 3. Struggling Merchant: Alto volume de vendas, mas transfere tudo (saldo baixo).
        ("broke_merchant", "Pedro Quebrado", "pedro.quebrado@email.com", "active", "basic", 0.00, "2023-06-15"),
        
        # 4. New User: Onboarding, pendente de verificação
        ("empty_user", "Marina Nova", "marina.nova@email.com", "active", "basic", 0.00, "2024-01-20"),
        
        # --- GENERIC USERS ---
        ("client789", "João Silva - Restaurante", "joao.silva@email.com", "active", "premium", 1250.50, "2023-01-15"),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO users (user_id, name, email, account_status, plan, balance, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, users)
    
    # Update block reason for blocked_user (if schema allowed, but for now we simulate via status)
    # If we had a block_reason column, we'd update it here.
    # checking schema... create_tables doesn't have block_reason.
    # Let's add it dynamically if we want better realism, or just rely on 'blocked' status.
    # The tool 'get_user_info' checks 'block_reason' column if status is blocked.
    # We should ensure the table has it or the tool handles it.
    # Looking at create_tables, it does NOT have block_reason.
    # Let's alter table to add it safely.
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN block_reason TEXT")
    except sqlite3.OperationalError:
        pass # Column likely exists
        
    cursor.execute("UPDATE users SET block_reason = 'Suspicious Activity Detected' WHERE user_id = 'blocked_user'")
    
    conn.commit()
    print(f"[OK] {len(users)} usuarios inseridos")


def seed_transactions(conn):
    """Adiciona transações com padrões específicos para cada arquétipo"""
    cursor = conn.cursor()
    
    transactions = []
    
    # --- 1. Happy Customer: Healthy Mix ---
    for i in range(5):
        transactions.append((
            f"tx_happy_{i}", "happy_customer", 
            random.uniform(100, 500), "credit", "completed", 
            (datetime.now() - timedelta(days=i)).isoformat()
        ))
    
    # --- 2. Blocked User: Failed Transactions ---
    transactions.append((
        "tx_blocked_1", "blocked_user", 
        5000.00, "transfer_out", "failed", 
        (datetime.now() - timedelta(minutes=30)).isoformat()
    ))
    transactions.append((
         "tx_blocked_2", "blocked_user", 
         120.00, "pix", "completed", # Old successful tx
         (datetime.now() - timedelta(days=60)).isoformat()
    ))
    
    # --- 3. Struggling Merchant: High Velocity (Sales IN, Pix OUT) ---
    # Sales (Money coming in)
    for i in range(3):
         transactions.append((
            f"tx_struggle_in_{i}", "broke_merchant", 
            random.uniform(200, 800), "credit", "completed", 
            (datetime.now() - timedelta(hours=i*2)).isoformat()
        ))
    # Transfers (Money going out - draining balance)
    transactions.append((
        "tx_struggle_out_1", "broke_merchant", 
        1500.00, "pix_out", "completed", 
        (datetime.now() - timedelta(hours=1)).isoformat()
    ))
    
    # --- 4. New User: No transactions ---
    # (Intentionally empty)
    
    cursor.executemany("""
        INSERT OR REPLACE INTO transactions 
        (transaction_id, user_id, amount, type, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, transactions)
    
    # Add failure reason for blocked user (schema update needed?)
    try:
        cursor.execute("ALTER TABLE transactions ADD COLUMN failure_reason TEXT")
    except sqlite3.OperationalError:
        pass
        
    cursor.execute("UPDATE transactions SET failure_reason = 'Account Blocked' WHERE transaction_id = 'tx_blocked_1'")
    
    conn.commit()
    print(f"[OK] {len(transactions)} transacoes inseridas")


def seed_if_empty():
    """
    Verifica se banco está vazio e popula se necessário
    
    Chamado automaticamente no startup da aplicação
    """
    # Criar diretório data se não existir
    Path("./data").mkdir(exist_ok=True)
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabelas se não existirem
    create_tables(conn)
    
    # Verificar se já tem dados
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"[OK] Banco ja populado com {count} usuarios")
        conn.close()
        return
    
    print("=== Banco vazio, iniciando seed...")
    
    # Seed
    seed_users(conn)
    seed_transactions(conn)
    
    conn.close()
    print("[OK] Seed completo!")


def main():
    """Executa o seed (chamado manualmente ou no startup)"""
    print("=== Iniciando seed do banco de dados...")
    
    # Criar diretório data se não existir
    Path("./data").mkdir(exist_ok=True)
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    
    # Criar tabelas
    create_tables(conn)
    print("[OK] Tabelas criadas")
    
    # Seed
    seed_users(conn)
    seed_transactions(conn)
    
    conn.close()
    print("[OK] Seed completo!")


if __name__ == "__main__":
    main()

