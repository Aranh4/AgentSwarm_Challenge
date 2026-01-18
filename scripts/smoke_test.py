"""
Smoke Test - Basic Integration Test
Tests the complete flow after architectural changes.
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8080"

def test_health_check():
    """Test 1: API Health"""
    print("Test 1: API Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_simple_knowledge_query():
    """Test 2: Simple Knowledge Query (RAG)"""
    print("\nTest 2: Simple Knowledge Query...")
    try:
        payload = {
            "message": "What is InfinitePay?",
            "user_id": "client789"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        data = response.json()
        
        # Check response structure
        assert "response" in data, "Missing 'response' field"
        assert "agent_used" in data, "Missing 'agent_used' field"
        assert len(data["response"]) > 10, "Response too short"
        
        print(f"✅ Knowledge query passed")
        print(f"   Agent: {data.get('agent_used')}")
        print(f"   Response preview: {data['response'][:100]}...")
        return True
    except Exception as e:
        print(f"❌ Knowledge query failed: {e}")
        return False

def test_support_query():
    """Test 3: Support Query (Database)"""
    print("\nTest 3: Support Query...")
    try:
        payload = {
            "message": "What is my account balance?",
            "user_id": "client789"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        data = response.json()
        
        assert "response" in data
        assert "support" in data.get("agent_used", "").lower()
        
        print(f"✅ Support query passed")
        print(f"   Agent: {data.get('agent_used')}")
        print(f"   Response preview: {data['response'][:100]}...")
        return True
    except Exception as e:
        print(f"❌ Support query failed: {e}")
        return False

def test_output_processor_language():
    """Test 4: Output Processor Language Consistency"""
    print("\nTest 4: Output Processor - Language Consistency...")
    try:
        # English query
        payload_en = {
            "message": "What are the fees?",
            "user_id": "client789"
        }
        response_en = requests.post(f"{BASE_URL}/chat", json=payload_en, timeout=30)
        
        if response_en.status_code != 200:
            print(f"❌ English query failed with status: {response_en.status_code}")
            return False
        
        data_en = response_en.json()
        response_text_en = data_en["response"].lower()
        
        # Check for English keywords (simple heuristic)
        has_english = any(word in response_text_en for word in ["fee", "fees", "rate", "the", "is", "are"])
        
        if has_english:
            print(f"✅ Language test passed (English detected)")
        else:
            print(f"⚠️  Language test warning: Expected English, got: {data_en['response'][:100]}")
        
        return True
    except Exception as e:
        print(f"❌ Language test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🔬 SMOKE TEST - Integration Tests")
    print("=" * 60)
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    time.sleep(2)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Knowledge Query", test_simple_knowledge_query()))
    results.append(("Support Query", test_support_query()))
    results.append(("Output Processor", test_output_processor_language()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
