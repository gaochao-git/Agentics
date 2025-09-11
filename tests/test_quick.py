#!/usr/bin/env python3
"""
快速智能体功能测试
"""

import requests
import json

BASE_URL = "http://localhost:8000"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

def test_agent_simple(agent_type, description):
    """简单测试智能体"""
    print(f"Testing {description}...")
    
    url = f"{BASE_URL}/api/agents/chat/"
    data = {
        "message": "Hello, please respond in Chinese briefly.",
        "agent_type": agent_type
    }
    
    try:
        response = requests.post(url, json=data, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ SUCCESS - {agent_type}")
            return True
        else:
            print(f"✗ FAILED - {agent_type}: {response.status_code}")
            print(f"Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ EXCEPTION - {agent_type}: {e}")
        return False

def main():
    print("Quick Agent Test")
    print("=" * 30)
    
    # 简化的测试用例
    agents = [
        ("general_qa", "General QA"),
        ("speech_writer", "Speech Writer"), 
        ("news_writer", "News Writer"),
        ("code_assistant", "Code Assistant"),
        ("data_analysis", "Data Analysis"),
        ("official_document", "Official Document"),
        ("research_report", "Research Report")
    ]
    
    success_count = 0
    total_tests = len(agents)
    
    for agent_type, description in agents:
        if test_agent_simple(agent_type, description):
            success_count += 1
    
    print(f"\nResult: {success_count}/{total_tests} agents working")
    
    if success_count == total_tests:
        print("🎉 All agents are functional!")
    else:
        print(f"⚠️ {total_tests - success_count} agents have issues")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()