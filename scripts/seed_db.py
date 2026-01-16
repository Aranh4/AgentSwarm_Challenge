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
    """Adiciona usuários fake - INCLUI client789 para testes obrigatórios"""
    cursor = conn.cursor()
    
    users = [
        # ⚠️ OBRIGATÓRIO: client789 é usado nos cenários de teste da proposta
        ("client789", "João Silva - Restaurante", "joao.silva@email.com", "active", "premium", 1250.50, "2023-01-15"),
        ("user001", "Maria Santos - Loja de Roupas", "maria.santos@email.com", "active", "basic", 3400.00, "2023-03-20"),
        ("user002", "Pedro Oliveira - Bar", "pedro.oliveira@email.com", "blocked", "premium", 0.00, "2023-02-10"),
        ("user003", "Ana Costa - E-commerce", "ana.costa@email.com", "active", "enterprise", 15000.00, "2023-04-05"),
        ("user004", "Carlos Ferreira - Freelancer", "carlos.ferreira@email.com", "pending", "basic", 0.00, "2024-01-01"),
        ("user005", "Lucia Almeida - Salão de Beleza", "lucia.almeida@email.com", "active", "premium", 560.20, "2023-06-15"),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO users (user_id, name, email, account_status, plan, balance, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, users)
    
    conn.commit()
    print(f"[OK] {len(users)} usuarios inseridos")


def seed_transactions(conn):
    """Adiciona transações fake"""
    cursor = conn.cursor()
    
    user_ids = ["client789", "user001", "user002", "user003", "user004", "user005"]
    types = ["credit", "debit", "pix", "boleto"]
    statuses = ["completed", "pending", "failed"]
    
    transactions = []
    
    for i in range(50):
        user_id = random.choice(user_ids)
        amount = round(random.uniform(10.0, 500.0), 2)
        tx_type = random.choice(types)
        status = random.choice(statuses)
        
        # Data aleatória nos últimos 30 dias
        days_ago = random.randint(0, 30)
        created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        transaction_id = f"tx_{i:04d}"
        
        transactions.append((
            transaction_id,
            user_id,
            amount,
            tx_type,
            status,
            created_at
        ))
    
    cursor.executemany("""
        INSERT OR REPLACE INTO transactions 
        (transaction_id, user_id, amount, type, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, transactions)
    
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

