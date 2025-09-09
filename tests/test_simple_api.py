#!/usr/bin/env python3
"""
简单API测试
"""

import requests
import json

BASE_URL = "http://localhost:8000"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

def test_simple_chat():
    """测试简单聊天"""
    print("测试通用问答助手...")
    
    url = f"{BASE_URL}/api/agents/chat/"
    data = {
        "message": "你好，请用中文简单回答：今天天气如何？",
        "agent_type": "general_qa"
    }
    
    try:
        print("发送请求...")
        response = requests.post(url, json=data, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 成功！")
            print(f"对话ID: {result.get('conversation_id')}")
            print(f"响应: {result.get('response', '')[:200]}...")
            return True
        else:
            print(f"✗ 失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False


def test_math_question():
    """测试数学问题"""
    print("\n测试数学问题...")
    
    url = f"{BASE_URL}/api/agents/chat/"
    data = {
        "message": "请计算：1+1=?",
        "agent_type": "general_qa"
    }
    
    try:
        response = requests.post(url, json=data, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 成功！")
            print(f"响应: {result.get('response', '')[:150]}...")
            return True
        else:
            print(f"✗ 失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False


if __name__ == "__main__":
    print("简单API功能测试")
    print("=" * 40)
    
    success_count = 0
    total_tests = 2
    
    if test_simple_chat():
        success_count += 1
    
    if test_math_question():
        success_count += 1
    
    print(f"\n测试结果: {success_count}/{total_tests} 成功")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！通用问答助手工作正常")
    else:
        print("⚠️ 部分测试失败")