#!/usr/bin/env python3
"""
通用问答助手功能测试
测试实际的问答功能（使用模拟模式）
"""

import sys
import os
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agents.core.base import AgentType, AgentMessage, AgentResponse
from agents.general_qa.agent import GeneralQAAgent
from datetime import datetime


async def test_basic_qa():
    """测试基本问答功能"""
    print("测试1: 基本问答功能...")
    
    try:
        agent = GeneralQAAgent()
        
        # 测试通用问题
        message = AgentMessage(
            id="test_msg_1",
            content="你好，请介绍一下你自己",
            agent_type=AgentType.GENERAL_QA,
            timestamp=datetime.now()
        )
        
        response = await agent.process(message)
        
        print(f"✓ 问答处理成功")
        print(f"✓ 响应成功: {response.success}")
        print(f"✓ 响应内容: {response.content}")
        print(f"✓ 执行时间: {response.execution_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_specialist_routing():
    """测试专业智能体路由"""
    print("\n测试2: 专业智能体路由...")
    
    try:
        agent = GeneralQAAgent()
        
        # 测试包含专业关键词的消息
        messages = [
            "请帮我写一份发言稿",
            "我需要一份新闻稿",
            "帮我分析这些数据",
            "需要写代码实现功能"
        ]
        
        for i, msg_content in enumerate(messages):
            message = AgentMessage(
                id=f"test_msg_{i+2}",
                content=msg_content,
                agent_type=AgentType.GENERAL_QA,
                timestamp=datetime.now()
            )
            
            response = await agent.process(message)
            print(f"✓ 消息: '{msg_content}'")
            print(f"  响应: {response.content[:50]}...")
            
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_input_validation():
    """测试输入验证"""
    print("\n测试3: 输入验证...")
    
    try:
        agent = GeneralQAAgent()
        
        # 测试空消息
        message = AgentMessage(
            id="test_msg_empty",
            content="",
            agent_type=AgentType.GENERAL_QA,
            timestamp=datetime.now()
        )
        
        response = await agent.process(message)
        print(f"✓ 空消息处理: success={response.success}")
        
        # 测试正常消息
        message = AgentMessage(
            id="test_msg_normal",
            content="正常的问题",
            agent_type=AgentType.GENERAL_QA,
            timestamp=datetime.now()
        )
        
        response = await agent.process(message)
        print(f"✓ 正常消息处理: success={response.success}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_langgraph_workflow():
    """测试LangGraph工作流"""
    print("\n测试4: LangGraph工作流...")
    
    try:
        agent = GeneralQAAgent()
        
        # 测试图的基本结构
        print(f"✓ 图对象存在: {agent.graph is not None}")
        
        # 测试图的执行（直接调用）
        initial_state = {
            "messages": [{"role": "user", "content": "测试消息"}],
            "current_agent": "general_qa",
            "context": {},
            "needs_specialist": False,
            "specialist_type": "",
            "user_intent": "测试消息"
        }
        
        result = agent.graph.invoke(initial_state)
        print(f"✓ 图执行成功")
        print(f"✓ 结果类型: {type(result)}")
        print(f"✓ 当前智能体: {result.get('current_agent', 'unknown')}")
        print(f"✓ 需要专业智能体: {result.get('needs_specialist', False)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有功能测试"""
    print("通用问答助手功能测试")
    print("=" * 50)
    
    tests = [
        test_basic_qa,
        test_specialist_routing,
        test_input_validation,
        test_langgraph_workflow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"功能测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有功能测试通过！通用问答助手可以正常工作")
    else:
        print("✗ 部分功能测试失败，需要进一步调试")


if __name__ == "__main__":
    asyncio.run(main())