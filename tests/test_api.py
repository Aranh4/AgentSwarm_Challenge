"""
test_api.py - Basic API endpoint tests
Tests the FastAPI endpoints without LLM calls where possible.
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_returns_200(self):
        """Health check should return 200 OK."""
        from src.main import app
        client = TestClient(app)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        
    def test_health_returns_healthy_status(self):
        """Health check should return healthy status."""
        from src.main import app
        client = TestClient(app)
        
        response = client.get("/health")
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "environment" in data


class TestChatEndpoint:
    """Tests for /chat endpoint structure."""
    
    def test_chat_requires_message(self):
        """Chat should require message field."""
        from src.main import app
        client = TestClient(app)
        
        response = client.post("/chat", json={"user_id": "test"})
        
        assert response.status_code == 422  # Validation error
        
    def test_chat_requires_user_id(self):
        """Chat should require user_id field."""
        from src.main import app
        client = TestClient(app)
        
        response = client.post("/chat", json={"message": "test"})
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_response_structure(self, test_user_id):
        """Chat response should have required fields."""
        from src.main import app
        client = TestClient(app)
        
        response = client.post("/chat", json={
            "message": "Hello",
            "user_id": test_user_id
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields per PROPOSTA.md
        assert "response" in data
        assert "agent_used" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)
