"""
Pytest fixtures for the CloudWalk Agent Swarm tests.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load env before anything else
from src.env_loader import *  # noqa


@pytest.fixture
def test_user_id():
    """Standard test user ID from mock DB."""
    return "client789"


@pytest.fixture
def blocked_user_id():
    """Blocked user ID for testing account status."""
    return "user_blocked"


@pytest.fixture
def sample_queries():
    """Sample queries for testing different routing scenarios."""
    return {
        "knowledge": [
            "Quais as taxas da maquininha smart?",
            "How does Pix work?",
            "What are the fees for credit card transactions?"
        ],
        "support": [
            "Por que minha conta está bloqueada?",
            "My transfer failed",
            "What is my balance?"
        ],
        "mixed": [
            "Quais as taxas e por que minha conta está bloqueada?",
            "What are the fees and why can't I login?"
        ]
    }
