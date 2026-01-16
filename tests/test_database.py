"""
test_database.py - Database and Support Tools tests
Tests the SQLite mock database and support agent tools.
"""
import pytest


class TestDatabase:
    """Tests for SQLite database setup."""
    
    def test_database_exists(self):
        """Database file should exist."""
        from pathlib import Path
        from src.config import settings
        
        db_path = Path(settings.sqlite_db_path)
        assert db_path.exists(), f"Database should exist at {db_path}"
    
    def test_users_table_has_data(self):
        """Users table should have mock data."""
        from src.db.client import db_client
        
        user = db_client.get_user("client789")
        
        assert user is not None, "client789 should exist (required for tests)"
        assert "name" in user
        assert "balance" in user
    
    def test_blocked_user_has_reason(self):
        """Blocked user should have block reason."""
        from src.db.client import db_client
        
        user = db_client.get_user("user_blocked")
        
        assert user is not None
        assert user["account_status"] == "blocked"
        assert user["block_reason"] is not None


class TestSupportTools:
    """Tests for Support Agent tools."""
    
    def test_get_user_info_tool(self, test_user_id):
        """get_user_info tool should return user data."""
        from src.tools.support_tools import get_user_info_tool
        
        result = get_user_info_tool.run(test_user_id)
        
        assert "Name" in result or "name" in result.lower()
        assert "Balance" in result or "balance" in result.lower()
    
    def test_get_transactions_tool(self, test_user_id):
        """get_user_transactions tool should return transaction data."""
        from src.tools.support_tools import get_user_transactions_tool
        
        result = get_user_transactions_tool.run(test_user_id)
        
        # Should return some data (even if empty)
        assert isinstance(result, str)
    
    def test_get_cards_tool(self, test_user_id):
        """get_user_cards tool should return card data."""
        from src.tools.support_tools import get_user_cards_tool
        
        result = get_user_cards_tool.run(test_user_id)
        
        assert isinstance(result, str)
    
    def test_nonexistent_user_handled(self):
        """Tools should handle non-existent users gracefully."""
        from src.tools.support_tools import get_user_info_tool
        
        result = get_user_info_tool.run("nonexistent_user_xyz")
        
        assert "not found" in result.lower() or "não encontrado" in result.lower()
