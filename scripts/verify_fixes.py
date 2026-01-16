"""
Targeted Verification Script
Tests specific fixes for Milestone 7 (Refinements)
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_tap_to_pay_source():
    """Test 1: Check if Tap to Pay uses RAG sources (InfinitePay)"""
    print("Test 1: Tap to Pay Source Check...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "What is Tap to Pay on Phone?", "user_id": "client789"},
            timeout=30
        )
        data = response.json()
        sources = data.get("sources", [])
        
        # Check source URLs
        has_infinitepay = any("infinitepay.io" in s for s in sources)
        
        if has_infinitepay:
            print("✅ Tap to Pay uses InfinitePay sources")
            print(f"   Sources: {sources}")
            return True
        else:
            print("❌ Tap to Pay using generic sources")
            print(f"   Sources: {sources}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_language_consistency_pt():
    """Test 2: Check PT language in structured data headers"""
    print("\nTest 2: Language Consistency (PT Headers)...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "Mostre minhas transações recentes", "user_id": "client789"},
            timeout=30
        )
        data = response.json()
        text = data.get("response", "")
        
        # Check for Portuguese headers
        has_data = "Data:" in text or "Date:" not in text
        has_tipo = "Tipo:" in text or "Type:" not in text
        
        if has_data and has_tipo:
            print("✅ Structured data headers translated to PT")
            print(f"   Preview: {text[:150]}...")
            return True
        else:
            print("❌ Structured data headers NOT translated")
            print(f"   Preview: {text[:150]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mixed_cleanup():
    """Test 3: Mixed Query Cleanup (removing 'I cannot help' messages)"""
    print("\nTest 3: Mixed Query Cleanup...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "Show my transactions and explain the fees", "user_id": "client789"},
            timeout=45
        )
        data = response.json()
        text = data.get("response", "")
        
        # Check for refusal messages
        has_refusal = "unable to assist" in text.lower() or "cannot help" in text.lower() or "support agent" in text.lower()
        
        if not has_refusal:
            print("✅ Refusal messages removed")
            return True
        else:
            print("❌ Refusal message still present")
            print(f"   Preview: {text[:200]}...")
            # We allow it if it's very minor, but ideally should be gone.
            # actually strict check for now.
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 TARGETED VERIFICATION")
    print("=" * 60)
    
    # Wait for server
    time.sleep(2)
    
    results = [
        test_tap_to_pay_source(),
        test_language_consistency_pt(),
        test_mixed_cleanup()
    ]
    
    if all(results):
        print("\n🎉 All targeted fixes verified!")
    else:
        print("\n⚠️  Some verification tests failed.")

if __name__ == "__main__":
    main()
