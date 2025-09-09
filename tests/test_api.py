#!/usr/bin/env python3
"""
测试API接口
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

# 设置请求头
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

def test_chat_api():
    """测试聊天API"""
    print("测试聊天API...")
    
    url = f"{BASE_URL}/api/agents/chat/"
    data = {
        "message": "你好，请简单介绍一下你自己",
        "agent_type": "general_qa"
    }
    
    try:
        print("发送请求...")
        start_time = time.time()
        response = requests.post(url, json=data, headers=HEADERS, timeout=30)
        end_time = time.time()
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 请求成功")
            print(f"对话ID: {result.get('conversation_id')}")
            print(f"智能体类型: {result.get('agent_type')}")
            print(f"成功状态: {result.get('success')}")
            print(f"执行时间: {result.get('execution_time'):.2f}秒")
            print(f"响应内容: {result.get('response', '')[:200]}...")
            
            return result.get('conversation_id')
        else:
            print(f"✗ 请求失败")
            print(f"错误信息: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("✗ 请求超时")
        return None
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return None


def test_agents_list():
    """测试智能体列表API"""
    print("\n测试智能体列表API...")
    
    url = f"{BASE_URL}/api/agents/list/"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            agents = response.json()
            print(f"✓ 获取成功，找到 {len(agents)} 个智能体")
            for agent in agents:
                print(f"  - {agent.get('name')} ({agent.get('type')})")
        else:
            print(f"✗ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")


def test_conversation_with_ollama():
    """测试与Ollama的对话"""
    print("\n测试与Ollama模型的连续对话...")
    
    conversation_id = None
    
    messages = [
        "你好，我想了解一下人工智能",
        "能详细说说机器学习吗？",
        "谢谢你的解释"
    ]
    
    for i, message in enumerate(messages):
        print(f"\n第 {i+1} 轮对话:")
        print(f"用户: {message}")
        
        url = f"{BASE_URL}/api/agents/chat/"
        data = {
            "message": message,
            "agent_type": "general_qa"
        }
        
        if conversation_id:
            data["conversation_id"] = conversation_id
        
        try:
            start_time = time.time()
            response = requests.post(url, json=data, headers=HEADERS, timeout=60)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                conversation_id = result.get('conversation_id')
                print(f"智能体: {result.get('response', '')[:150]}...")
                print(f"响应时间: {end_time - start_time:.2f}秒")
            else:
                print(f"✗ 请求失败: {response.text}")
                break
                
        except Exception as e:
            print(f"✗ 请求异常: {e}")
            break


def main():
    """主测试函数"""
    print("API接口测试")
    print("=" * 50)
    
    # 测试智能体列表
    test_agents_list()
    
    # 测试单次对话
    conversation_id = test_chat_api()
    
    # 测试连续对话
    if conversation_id:
        test_conversation_with_ollama()
    
    print("\n" + "=" * 50)
    print("测试完成")


if __name__ == "__main__":
    main()