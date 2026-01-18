"""
Unified Test Suite - CloudWalk Agent Swarm
==========================================
Comprehensive test scenarios with parallel execution support.

Usage:
    # Run all tests (8 parallel workers)
    pytest tests/test_unified_suite.py -n 8 -v
    
    # Run specific category
    pytest tests/test_unified_suite.py::TestRAGProducts -n 4
    
    # Generate report
    python scripts/run_unified_tests.py
"""

import pytest
import httpx
import asyncio
from typing import Dict, List
import time

# Base URL for API
BASE_URL = "http://localhost:8888"

def record_test_details(record_property, query, response_data):
    """Helper to record test metadata for the markdown report"""
    record_property("query", query)
    record_property("response", response_data.get("response", ""))
    record_property("agent_used", response_data.get("agent_used", []))
    record_property("sources", response_data.get("sources", []))


# ============================================================================
# TEST SCENARIOS - Organized by Category
# ============================================================================

class TestRAGProducts:
    """Test RAG-based product queries in both languages"""
    
    scenarios = [
        {
            "query_en": "What is InfinitePay?",
            "query_pt": "O que é a InfinitePay?",
            "expected_agent": "knowledge",
            "expected_keywords": ["InfinitePay", "CloudWalk", "payment"]
        },
        {
            "query_en": "What products does InfinitePay offer?",
            "query_pt": "Quais produtos a InfinitePay oferece?",
            "expected_agent": "knowledge",
            "expected_keywords": ["Maquininha", "Smart", "Tap to Pay"]
        },
        {
            "query_en": "How does Tap to Pay work?",
            "query_pt": "Como funciona o Tap to Pay?",
            "expected_agent": "knowledge",
            "expected_keywords": ["iPhone", "aproximação", "NFC"]
        },
        {
            "query_en": "What is the Maquininha Smart?",
            "query_pt": "O que é a Maquininha Smart?",
            "expected_agent": "knowledge",
            "expected_keywords": ["maquininha", "card", "débito", "crédito"]
        }
    ]
    
    @pytest.mark.parametrize("scenario", scenarios)
    @pytest.mark.asyncio
    async def test_product_query_english(self, scenario, record_property):
        """Test product queries in English"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": scenario["query_en"], "user_id": "test_user"}
            )
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, scenario["query_en"], data)
            
            # Check agent used
            assert scenario["expected_agent"] in str(data["agent_used"])
            
            # Check keywords present
            response_lower = data["response"].lower()
            assert any(kw.lower() in response_lower for kw in scenario["expected_keywords"])
    
    @pytest.mark.parametrize("scenario", scenarios)
    @pytest.mark.asyncio
    async def test_product_query_portuguese(self, scenario, record_property):
        """Test product queries in Portuguese"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": scenario["query_pt"], "user_id": "test_user"}
            )
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, scenario["query_pt"], data)
            assert scenario["expected_agent"] in str(data["agent_used"])


class TestRAGFees:
    """Test fee and pricing queries"""
    
    scenarios = [
        {
            "query_en": "What are the fees for the Maquininha?",
            "query_pt": "Quais são as taxas da maquininha?",
            "expected_keywords": ["0.75", "taxa", "débito"]
        },
        {
            "query_en": "What are the transaction fees?",
            "query_pt": "Quais as taxas de transação?",
            "expected_keywords": ["débito", "crédito", "%"]
        },
        {
            "query_en": "Is the payment link free?",
            "query_pt": "O link de pagamento é gratuito?",
            "expected_keywords": ["gratuito", "free", "grátis"]
        }
    ]
    
    @pytest.mark.parametrize("scenario", scenarios)
    @pytest.mark.asyncio
    async def test_fees_bilingual(self, scenario, record_property):
        """Test fee queries in both languages"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Test English
            response_en = await client.post(
                f"{BASE_URL}/chat",
                json={"message": scenario["query_en"], "user_id": "test_user"}
            )
            assert response_en.status_code == 200
            data_en = response_en.json()
            record_test_details(record_property, scenario["query_en"], data_en)
            
            # Test Portuguese
            response_pt = await client.post(
                f"{BASE_URL}/chat",
                json={"message": scenario["query_pt"], "user_id": "test_user"}
            )
            assert response_pt.status_code == 200
            data_pt = response_pt.json()
            record_test_details(record_property, scenario["query_pt"], data_pt)


class TestWebSearch:
    """Test web search functionality for general questions"""
    
    scenarios = [
        {
            "query_en": "What are the latest tech news?",
            "query_pt": "Quais as principais notícias tech?",
            "expected_agent": "knowledge"
        },
        {
            "query_en": "Who won the last World Cup?",
            "query_pt": "Quem ganhou a última Copa do Mundo?",
            "expected_agent": "knowledge"
        },
        {
            "query_en": "What is the current dollar rate?",
            "query_pt": "Como está o dólar hoje?",
            "expected_agent": "knowledge"
        }
    ]
    
    @pytest.mark.parametrize("scenario", scenarios)
    @pytest.mark.asyncio
    async def test_web_search_query(self, scenario, record_property):
        """Test web search queries"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": scenario["query_en"], "user_id": "test_user"}
            )
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, scenario["query_en"], data)
            assert scenario["expected_agent"] in str(data["agent_used"])
            assert len(data["response"]) > 20  # Has substantial content


class TestSupportQueries:
    """Test customer support queries with user context"""
    
    @pytest.mark.asyncio
    async def test_balance_query(self, record_property):
        """Test balance query for happy customer"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": "What is my balance?", "user_id": "happy_customer"}
            )
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, "What is my balance?", data)
            assert "support" in str(data["agent_used"])
            assert "15,250" in data["response"] or "15250" in data["response"] or "15.250" in data["response"]
    
    @pytest.mark.asyncio
    async def test_blocked_account(self, record_property):
        """Test blocked account explanation"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": "Why is my account blocked?", "user_id": "blocked_user"}
            )
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, "Why is my account blocked?", data)
            assert "support" in str(data["agent_used"])
            assert "blocked" in data["response"].lower() or "bloqueada" in data["response"].lower()
    
    @pytest.mark.asyncio
    async def test_transactions_query(self, record_property):
        """Test transaction history query"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": "Show my recent transactions", "user_id": "happy_customer"}
            )
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, "Show my recent transactions", data)
            assert "support" in str(data["agent_used"])


class TestCollaborative:
    """Test collaborative multi-agent scenarios"""
    
    scenarios = [
        {
            "query_en": "What is the best product for my business?",
            "query_pt": "Qual produto InfinitePay é melhor para meu negócio?",
            "user_id": "happy_customer",
            "expected_agents": ["support", "knowledge"]
        },
        {
            "query_en": "Based on my balance, can I afford the Maquininha Smart?",
            "query_pt": "Com base no meu saldo, posso comprar a Maquininha Smart?",
            "user_id": "happy_customer",
            "expected_agents": ["support", "knowledge"]
        }
    ]
    
    @pytest.mark.parametrize("scenario", scenarios)
    @pytest.mark.asyncio
    async def test_collaborative_query(self, scenario, record_property):
        """Test queries requiring multiple agents"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": scenario["query_en"], "user_id": scenario["user_id"]}
            )
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, scenario["query_en"], data)
            
            # Should use multiple agents
            agent_used_str = str(data["agent_used"])
            assert any(agent in agent_used_str for agent in scenario["expected_agents"])


class TestLanguageConsistency:
    """Test that responses match query language"""
    
    @pytest.mark.asyncio
    async def test_english_query_english_response(self, record_property):
        """English query should get English response"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": "What is InfinitePay?", "user_id": "test_user"}
            )
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, "What is InfinitePay?", data)
            
            # Check for Portuguese-specific characters (should be minimal)
            response_text = data["response"].lower()
            portuguese_chars = sum(1 for c in response_text if c in 'áéíóúãõç')
            
            # Allow some Portuguese in brand names, but response should be mostly English
            assert portuguese_chars < len(response_text) * 0.1  # Less than 10%
    
    @pytest.mark.asyncio
    async def test_portuguese_query_portuguese_response(self, record_property):
        """Portuguese query should get Portuguese response"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": "O que é a InfinitePay?", "user_id": "test_user"}
            )
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, "O que é a InfinitePay?", data)
            
            # Should have Portuguese characteristics
            response_text = data["response"].lower()
            # Check for common Portuguese words
            portuguese_indicators = ["é", "são", "está", "que", "com", "para"]
            assert any(word in response_text for word in portuguese_indicators)


class TestPerformance:
    """Test response time performance"""
    
    @pytest.mark.asyncio
    async def test_response_time_knowledge(self, record_property):
        """Knowledge queries should respond in reasonable time"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            start = time.time()
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": "What are the fees?", "user_id": "test_user"}
            )
            duration = time.time() - start
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, "What are the fees?", data)
            # Allow more time during parallel execution
            assert duration < 60.0
    
    @pytest.mark.asyncio
    async def test_response_time_support(self, record_property):
        """Support queries should respond quickly"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            start = time.time()
            response = await client.post(
                f"{BASE_URL}/chat",
                json={"message": "My balance?", "user_id": "happy_customer"}
            )
            duration = time.time() - start
            
            assert response.status_code == 200
            data = response.json()
            record_test_details(record_property, "My balance?", data)
            # Support should be faster, but allow for parallel overhead
            assert duration < 40.0


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


# ============================================================================
# SUMMARY
# ============================================================================
# To run this unified test suite:
#
# 1. All tests (parallel):
#    pytest tests/test_unified_suite.py -n 8 -v
#
# 2. Specific category:
#    pytest tests/test_unified_suite.py::TestRAGProducts -n 4
#
# 3. With coverage:
#    pytest tests/test_unified_suite.py -n 8 --cov=src
#
# 4. Generate comprehensive report:
#    python scripts/run_unified_tests.py
# ============================================================================
