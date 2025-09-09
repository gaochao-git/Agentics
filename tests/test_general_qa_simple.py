#!/usr/bin/env python3
"""
通用问答助手简单测试
这个测试不需要OpenAI API密钥，主要用于验证代码结构和框架
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agents.core.base import AgentType
from agents.general_qa.agent import GeneralQAAgent


def test_basic_structure():
    """测试基本结构"""
    print("测试1: 智能体基本结构...")
    
    try:
        agent = GeneralQAAgent()
        print(f"✓ 智能体创建成功: {agent.name}")
        print(f"✓ 智能体类型: {agent.agent_type}")
        print(f"✓ 智能体描述: {agent.description}")
        
        capabilities = agent.get_capabilities()
        print(f"✓ 能力列表: {len(capabilities)} 项")
        for cap in capabilities:
            print(f"  - {cap}")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    
    return True


def test_conversation_state():
    """测试对话状态结构"""
    print("\n测试2: 对话状态结构...")
    
    try:
        from agents.general_qa.agent import ConversationState
        
        # 验证类型定义存在
        annotations = ConversationState.__annotations__
        required_keys = ['messages', 'current_agent', 'context', 'needs_specialist', 'specialist_type', 'user_intent']
        
        for key in required_keys:
            if key in annotations:
                print(f"✓ {key}: {annotations[key]}")
            else:
                print(f"✗ 缺少 {key}")
                return False
                
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    
    return True


def test_imports():
    """测试导入"""
    print("\n测试3: 模块导入测试...")
    
    try:
        # 测试LangGraph相关导入
        from langgraph.graph import StateGraph, END
        print("✓ LangGraph导入成功")
        
        # 测试类型定义
        from typing import List, Dict, Any, TypedDict
        print("✓ 类型定义导入成功")
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    
    return True


def test_agent_registration():
    """测试智能体注册功能"""
    print("\n测试4: 智能体注册功能...")
    
    try:
        agent = GeneralQAAgent()
        
        # 测试注册方法存在
        assert hasattr(agent, 'register_specialist_agent')
        print("✓ 注册方法存在")
        
        # 测试注册表初始化
        assert hasattr(agent, 'specialist_agents')
        print("✓ 专业智能体表已初始化")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    
    return True


def main():
    """运行所有测试"""
    print("通用问答助手框架测试")
    print("=" * 50)
    
    tests = [
        test_basic_structure,
        test_conversation_state,
        test_imports,
        test_agent_registration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！通用问答助手框架正常")
    else:
        print("✗ 部分测试失败，请检查配置")


if __name__ == "__main__":
    main()