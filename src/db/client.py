"""
Database Client Module
Provides functions to interact with the SQLite database.
"""

import sqlite3
import logging
from typing import Dict, List, Optional
from src.config import settings

logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self):
        self.db_path = settings.sqlite_db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Fetch user details by ID"""
        logger.info(f"[DB] Fetching User: {user_id}")
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
        finally:
            conn.close()

    def get_transactions(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Fetch recent transactions for a user"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching transactions for {user_id}: {e}")
            return []
        finally:
            conn.close()

    def get_cards(self, user_id: str) -> List[Dict]:
        """Fetch cards for a user"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM cards WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching cards for {user_id}: {e}")
            return []
        finally:
            conn.close()

# Singleton instance
db_client = DatabaseClient()
