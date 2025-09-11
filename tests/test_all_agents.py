#!/usr/bin/env python3
"""
测试所有智能体功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

def test_agent(agent_type, test_message, description):
    """测试指定类型的智能体"""
    print(f"\n测试{description}...")
    
    url = f"{BASE_URL}/api/agents/chat/"
    data = {
        "message": test_message,
        "agent_type": agent_type
    }
    
    try:
        print("发送请求...")
        response = requests.post(url, json=data, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 成功！")
            print(f"对话ID: {result.get('conversation_id')}")
            print(f"响应: {result.get('response', '')[:200]}...")
            if result.get('metadata'):
                print(f"元数据: {result.get('metadata')}")
            return True
        else:
            print(f"✗ 失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def main():
    print("智能体功能全面测试")
    print("=" * 50)
    
    # 测试用例定义
    test_cases = [
        {
            "agent_type": "general_qa",
            "message": "请简单介绍一下人工智能的发展历史",
            "description": "通用问答助手"
        },
        {
            "agent_type": "speech_writer", 
            "message": "帮我写一份公司年会的致辞稿，大约5分钟，面向全体员工",
            "description": "发言稿写作智能体"
        },
        {
            "agent_type": "news_writer",
            "message": "帮我写一份关于公司新产品发布的新闻稿",
            "description": "新闻稿写作智能体"
        },
        {
            "agent_type": "code_assistant",
            "message": "用Python写一个简单的计算器函数，支持四则运算",
            "description": "代码助手智能体"
        },
        {
            "agent_type": "data_analysis",
            "message": "请分析电商平台的用户购买行为数据，需要包含数据可视化方案",
            "description": "数据分析智能体"
        },
        {
            "agent_type": "official_document",
            "message": "起草一份关于办公室搬迁的通知",
            "description": "公文写作智能体"
        },
        {
            "agent_type": "research_report",
            "message": "撰写一份关于人工智能行业发展现状的研究报告",
            "description": "研报写作智能体"
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_tests}] ", end="")
        if test_agent(
            test_case["agent_type"], 
            test_case["message"], 
            test_case["description"]
        ):
            success_count += 1
        
        # 添加延迟避免请求过于频繁
        if i < total_tests:
            time.sleep(2)
    
    print(f"\n" + "=" * 50)
    print(f"测试结果: {success_count}/{total_tests} 成功")
    
    if success_count == total_tests:
        print("🎉 所有智能体测试通过！")
    else:
        print(f"⚠️  {total_tests - success_count} 个智能体测试失败")
        
    # 输出失败的智能体
    if success_count < total_tests:
        print("\n失败的智能体:")
        for i, test_case in enumerate(test_cases):
            # 这里简化处理，实际需要记录每个测试的结果
            pass
    
    return success_count == total_tests

if __name__ == "__main__":
    main()