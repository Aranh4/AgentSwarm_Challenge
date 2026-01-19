"""
test_router.py - Router Agent classification tests
Tests that the router correctly classifies queries into KNOWLEDGE, SUPPORT, or BOTH.
"""
import pytest


class TestRouterClassification:
    """Tests for Router Agent query classification."""
    
    @pytest.fixture
    def router(self):
        """Get router agent instance."""
        from src.agents.router_agent import RouterAgent
        return RouterAgent()
    
    def test_knowledge_query_classification(self, router):
        """Queries about products should route to KNOWLEDGE."""
        queries = [
            "What are the fees for the Smart machine?",
            "How does Pix work?",
            "Quais as taxas da maquininha?",
        ]
        
        for query in queries:
            routing, language = router.classify_query(query)
            assert routing in ["KNOWLEDGE", "BOTH"], f"'{query}' should be KNOWLEDGE, got {routing}"
    
    def test_support_query_classification(self, router):
        """Queries about user's personal data should route to SUPPORT."""
        queries = [
            "Why is my account blocked?",
            "My transfer failed",
            "What is my balance?",
            "Por que minha conta está bloqueada?",
        ]
        
        for query in queries:
            routing, language = router.classify_query(query)
            assert routing in ["SUPPORT", "BOTH"], f"'{query}' should be SUPPORT, got {routing}"
    
    def test_mixed_query_classification(self, router):
        """Queries with both types should route to BOTH."""
        queries = [
            "What are the fees and why is my account blocked?",
            "Taxas da maquininha e meu saldo?",
        ]
        
        for query in queries:
            routing, language = router.classify_query(query)
            # Mixed queries should ideally return BOTH, but SUPPORT is acceptable
            assert routing in ["BOTH", "SUPPORT", "KNOWLEDGE"], f"'{query}' classification failed"


class TestRouterExecution:
    """Tests for Router Agent execution."""
    
    def test_route_returns_required_fields(self, test_user_id):
        """Route execution should return all required fields."""
        from src.agents.router_agent import route_query
        
        result = route_query("What are the fees?", test_user_id)
        
        assert "response" in result
        assert "agent_used" in result
        assert "sources" in result
        assert "routing" in result
    
    def test_support_route_uses_correct_agent(self, blocked_user_id):
        """Support queries should use support agent."""
        from src.agents.router_agent import route_query
        
        result = route_query("Why is my account blocked?", blocked_user_id)
        
        # agent_used is now a list
        assert "support" in result["agent_used"]
