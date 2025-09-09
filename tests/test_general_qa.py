import pytest
import asyncio
from agents.core.base import AgentMessage, AgentType
from agents.general_qa.agent import GeneralQAAgent


@pytest.mark.asyncio
async def test_general_qa_agent_basic():
    """测试通用问答助手的基本功能"""
    agent = GeneralQAAgent()
    
    message = AgentMessage(
        id="test-1",
        content="你好，请介绍一下Python",
        agent_type=AgentType.GENERAL_QA,
        timestamp=None
    )
    
    response = await agent.process(message)
    
    assert response.success is True
    assert response.content is not None
    assert len(response.content) > 0
    assert response.agent_type == AgentType.GENERAL_QA


@pytest.mark.asyncio
async def test_general_qa_agent_routing():
    """测试智能体路由功能"""
    agent = GeneralQAAgent()
    
    # 测试发言稿路由
    message = AgentMessage(
        id="test-2",
        content="请帮我写一篇发言稿",
        agent_type=AgentType.GENERAL_QA,
        timestamp=None
    )
    
    response = await agent.process(message)
    
    assert response.success is True
    assert "发言稿" in response.content or "路由" in response.content


@pytest.mark.asyncio
async def test_general_qa_agent_capabilities():
    """测试智能体能力列表"""
    agent = GeneralQAAgent()
    
    capabilities = agent.get_capabilities()
    
    assert isinstance(capabilities, list)
    assert len(capabilities) > 0
    assert "通用知识问答" in capabilities
    assert "基于LangGraph的智能对话管理" in capabilities


@pytest.mark.asyncio
async def test_invalid_input():
    """测试无效输入处理"""
    agent = GeneralQAAgent()
    
    message = AgentMessage(
        id="test-3",
        content="",
        agent_type=AgentType.GENERAL_QA,
        timestamp=None
    )
    
    response = await agent.process(message)
    
    assert response.success is False
    assert "输入消息无效" in response.content


if __name__ == "__main__":
    pytest.main([__file__])