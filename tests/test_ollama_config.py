#!/usr/bin/env python3
"""
测试Ollama配置
"""

import sys
import os
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agents.core.llm_manager import (
    configure_ollama, set_ollama_env, get_llm, 
    test_ollama_connection, get_ollama_models, llm_manager
)
from agents.core.base import AgentMessage, AgentType
from agents.general_qa.agent import GeneralQAAgent
from datetime import datetime


async def main():
    """测试Ollama配置"""
    print("Ollama配置测试")
    print("=" * 50)
    
    # 1. 测试连接
    print("1. 测试Ollama连接...")
    result = test_ollama_connection()
    if result['success']:
        print(f"✓ 连接成功，发现 {result['count']} 个模型")
        print("可用模型:")
        for model in result['models'][:5]:  # 只显示前5个
            print(f"  - {model}")
        if len(result['models']) > 5:
            print(f"  ... 还有 {len(result['models']) - 5} 个模型")
    else:
        print(f"✗ 连接失败: {result['error']}")
        return
    
    # 2. 直接配置测试
    print("\n2. 直接配置测试...")
    try:
        config = configure_ollama("qwen3:8B")
        llm = llm_manager.create_llm(config)
        print("✓ 直接配置成功")
        
        from langchain.schema import HumanMessage
        response = await llm.ainvoke([HumanMessage(content="你好，简单介绍一下你自己")])
        print(f"✓ 模型响应: {response.content[:100]}...")
        
    except Exception as e:
        print(f"✗ 直接配置失败: {e}")
    
    # 3. 环境变量配置测试
    print("\n3. 环境变量配置测试...")
    try:
        set_ollama_env("qwen3:8B")
        llm = get_llm()
        print("✓ 环境变量配置成功")
        
        from langchain.schema import HumanMessage
        response = await llm.ainvoke([HumanMessage(content="1+1等于几？")])
        print(f"✓ 模型响应: {response.content[:100]}...")
        
    except Exception as e:
        print(f"✗ 环境变量配置失败: {e}")
    
    # 4. 智能体集成测试
    print("\n4. 智能体集成测试...")
    try:
        agent = GeneralQAAgent()
        message = AgentMessage(
            id="ollama_test",
            content="请用中文解释什么是人工智能，简要回答",
            agent_type=AgentType.GENERAL_QA,
            timestamp=datetime.now()
        )
        
        response = await agent.process(message)
        print(f"✓ 智能体处理: {response.success}")
        print(f"✓ 响应内容: {response.content[:150]}...")
        print(f"✓ 执行时间: {response.execution_time:.2f}秒")
        
    except Exception as e:
        print(f"✗ 智能体集成失败: {e}")
    
    print("\n" + "=" * 50)
    print("配置方法总结:")
    print("1. 直接配置:")
    print("   from agents.core.llm_manager import configure_ollama, llm_manager")
    print("   config = configure_ollama('qwen3:8B')")
    print("   llm = llm_manager.create_llm(config)")
    print()
    print("2. 环境变量配置:")
    print("   from agents.core.llm_manager import set_ollama_env, get_llm")
    print("   set_ollama_env('qwen3:8B')")
    print("   llm = get_llm()")
    print()
    print("3. 简化配置:")
    print("   from agents.core.llm_manager import get_llm")
    print("   llm = get_llm('ollama', model='qwen3:8B')")


if __name__ == "__main__":
    asyncio.run(main())