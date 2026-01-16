"""
Test Report Generator
Automatically tests the Agent Swarm with various scenarios and generates a detailed markdown report.
"""

import requests
import time
from datetime import datetime
from typing import List, Dict
import json

BASE_URL = "http://localhost:8000"

# Test Scenarios
TEST_SCENARIOS = [
    # Knowledge Agent - InfinitePay Products
    {
        "category": "Knowledge - Product Info",
        "user_id": "client789",
        "tests": [
            "What is InfinitePay?",
            "What products does InfinitePay offer?",
            "What is the Maquininha Smart?",
            "Tell me about InfiniteTap",
            "What is Tap to Pay on Phone?",
        ]
    },
    # Knowledge Agent - Fees & Rates
    {
        "category": "Knowledge - Fees & Rates",
        "user_id": "client789",
        "tests": [
            "What are the transaction fees?",
            "How much does the Maquininha Smart cost?",
            "What are the rates for credit card transactions?",
            "Are there any monthly fees?",
            "What is the cost of Tap to Pay?",
        ]
    },
    # Knowledge Agent - Comparisons
    {
        "category": "Knowledge - Competitive Analysis",
        "user_id": "client789",
        "tests": [
            "How does InfinitePay compare to competitors?",
            "Is InfinitePay cheaper than other payment providers?",
            "What makes InfinitePay better than alternatives?",
        ]
    },
    # Support Agent - Account Info
    {
        "category": "Support - Account Information",
        "user_id": "client789",
        "tests": [
            "What is my account balance?",
            "Show me my account status",
            "Am I verified?",
            "What is my user ID?",
        ]
    },
    # Support Agent - Transactions
    {
        "category": "Support - Transaction History",
        "user_id": "client789",
        "tests": [
            "Show me my recent transactions",
            "What was my last transaction?",
            "Did I receive any payments today?",
            "Why did my last transaction fail?",
        ]
    },
    # Mixed Queries (Both Agents)
    {
        "category": "Mixed - Knowledge + Support",
        "user_id": "client789",
        "tests": [
            "What are the fees and what is my current balance?",
            "Can I use Tap to Pay? Check my account status",
            "Show my transactions and explain the fees",
        ]
    },
    # Language Consistency - Portuguese
    {
        "category": "Language - Portuguese",
        "user_id": "client789",
        "tests": [
            "Quais são as taxas da InfinitePay?",
            "Quanto custa a Maquininha Smart?",
            "Qual é o meu saldo?",
            "Mostre minhas transações recentes",
        ]
    },
    # Language Consistency - English
    {
        "category": "Language - English",
        "user_id": "client789",
        "tests": [
            "What are InfinitePay's fees?",
            "How much does the Smart POS cost?",
            "What is my balance?",
            "Show my recent transactions",
        ]
    },
]

def run_test(message: str, user_id: str) -> Dict:
    """Run a single test query through the API"""
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message, "user_id": user_id},
            timeout=45
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "response": data.get("response", ""),
                "agent_used": data.get("agent_used", "unknown"),
                "sources": data.get("sources", []),
                "elapsed_ms": int(elapsed * 1000),
                "response_length": len(data.get("response", ""))
            }
        else:
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}",
                "response": response.text[:200],
                "elapsed_ms": int(elapsed * 1000)
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "elapsed_ms": 0
        }

def generate_report(results: List[Dict]) -> str:
    """Generate markdown report from test results"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Agent Swarm Test Report

**Generated:** {timestamp}  
**Total Tests:** {len(results)}

---

## Executive Summary

"""
    
    # Calculate stats
    total_tests = len(results)
    successful = sum(1 for r in results if r["result"]["status"] == "success")
    failed = total_tests - successful
    avg_time = sum(r["result"]["elapsed_ms"] for r in results) / total_tests if total_tests > 0 else 0
    
    report += f"""
- ✅ **Successful:** {successful}/{total_tests} ({successful/total_tests*100:.1f}%)
- ❌ **Failed:** {failed}/{total_tests}
- ⏱️  **Average Response Time:** {avg_time:.0f}ms

---

## Detailed Results

"""
    
    current_category = None
    
    for idx, test_result in enumerate(results, 1):
        category = test_result["category"]
        query = test_result["query"]
        user_id = test_result["user_id"]
        result = test_result["result"]
        
        # Category header
        if category != current_category:
            report += f"\n### {category}\n\n"
            current_category = category
        
        # Test header
        status_icon = "✅" if result["status"] == "success" else "❌"
        report += f"#### {status_icon} Test #{idx}: \"{query}\"\n\n"
        
        if result["status"] == "success":
            report += f"**Agent:** {result['agent_used']}  \n"
            report += f"**Response Time:** {result['elapsed_ms']}ms  \n"
            report += f"**Response Length:** {result['response_length']} chars  \n\n"
            
            # Response preview
            response_preview = result["response"][:300]
            if len(result["response"]) > 300:
                response_preview += "..."
            
            report += f"**Response:**\n> {response_preview}\n\n"
            
            # Sources
            if result.get("sources"):
                report += f"**Sources:** {len(result['sources'])} URLs\n"
                for source in result["sources"][:3]:  # Show max 3 sources
                    report += f"- {source}\n"
                report += "\n"
        else:
            report += f"**Error:** {result.get('error', 'Unknown error')}  \n"
            report += f"**Details:** {result.get('response', 'No details')}  \n\n"
        
        report += "---\n\n"
    
    # Agent Performance Analysis
    report += "\n## Agent Performance Analysis\n\n"
    
    agent_stats = {}
    for test_result in results:
        if test_result["result"]["status"] == "success":
            agent = test_result["result"]["agent_used"]
            if agent not in agent_stats:
                agent_stats[agent] = {"count": 0, "total_time": 0, "total_length": 0}
            
            agent_stats[agent]["count"] += 1
            agent_stats[agent]["total_time"] += test_result["result"]["elapsed_ms"]
            agent_stats[agent]["total_length"] += test_result["result"]["response_length"]
    
    for agent, stats in agent_stats.items():
        avg_time = stats["total_time"] / stats["count"]
        avg_length = stats["total_length"] / stats["count"]
        
        report += f"### {agent}\n"
        report += f"- **Queries Handled:** {stats['count']}\n"
        report += f"- **Avg Response Time:** {avg_time:.0f}ms\n"
        report += f"- **Avg Response Length:** {avg_length:.0f} chars\n\n"
    
    # Language Analysis
    report += "\n## Language Consistency Check\n\n"
    
    pt_queries = [r for r in results if r["category"].startswith("Language - Portuguese")]
    en_queries = [r for r in results if r["category"].startswith("Language - English")]
    
    report += f"**Portuguese Queries:** {len(pt_queries)} tested\n"
    report += f"**English Queries:** {len(en_queries)} tested\n\n"
    
    report += "> Note: Manual review recommended to verify language consistency in responses.\n\n"
    
    # Recommendations
    report += "\n## Recommendations\n\n"
    
    if failed > 0:
        report += f"- ⚠️  {failed} test(s) failed - investigate error logs\n"
    
    if avg_time > 2000:
        report += f"- ⚠️  Average response time is {avg_time:.0f}ms - consider optimization\n"
    
    if avg_time < 1500:
        report += f"- ✅ Response times are good (avg {avg_time:.0f}ms)\n"
    
    if successful == total_tests:
        report += f"- ✅ All tests passed successfully!\n"
    
    return report

def main():
    print("=" * 70)
    print("🧪 AGENT SWARM - COMPREHENSIVE TEST REPORT GENERATOR")
    print("=" * 70)
    print()
    
    # Check API health
    print("1. Checking API health...")
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            print("   ✅ API is healthy\n")
        else:
            print(f"   ❌ API returned status {health.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to API: {e}")
        return
    
    # Run all tests
    print("2. Running test scenarios...\n")
    
    all_results = []
    test_count = 0
    
    for scenario in TEST_SCENARIOS:
        category = scenario["category"]
        user_id = scenario["user_id"]
        
        print(f"   📋 {category}")
        
        for query in scenario["tests"]:
            test_count += 1
            print(f"      [{test_count}] {query[:50]}...")
            
            result = run_test(query, user_id)
            
            all_results.append({
                "category": category,
                "query": query,
                "user_id": user_id,
                "result": result
            })
            
            # Brief pause between requests
            time.sleep(0.5)
    
    print(f"\n   ✅ Completed {test_count} tests\n")
    
    # Generate report
    print("3. Generating markdown report...")
    
    report_content = generate_report(all_results)
    
    # Save report
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"test_report_{timestamp_file}.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"   ✅ Report saved to: {report_path}\n")
    
    # Summary
    successful = sum(1 for r in all_results if r["result"]["status"] == "success")
    print("=" * 70)
    print(f"📊 SUMMARY: {successful}/{test_count} tests passed")
    print(f"📄 Report: {report_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
