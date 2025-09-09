import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from agents.core.base import AgentMessage, AgentType
from agents.general_qa.agent import GeneralQAAgent


@pytest.mark.asyncio
async def test_general_qa_agent_mock():
    """测试通用问答助手的框架功能（使用mock）"""
    agent = GeneralQAAgent()
    
    # Mock LLM响应
    mock_response = AsyncMock()
    mock_response.content = "这是一个测试响应"
    
    with patch.object(agent.llm, 'invoke', return_value=mock_response):
        message = AgentMessage(
            id="test-1",
            content="测试问题",
            agent_type=AgentType.GENERAL_QA,
            timestamp=None
        )
        
        response = await agent.process(message)
        
        assert response.success is True
        assert response.content is not None
        assert response.agent_type == AgentType.GENERAL_QA


@pytest.mark.asyncio
async def test_general_qa_capabilities():
    """测试智能体能力列表"""
    agent = GeneralQAAgent()
    
    capabilities = agent.get_capabilities()
    
    assert isinstance(capabilities, list)
    assert len(capabilities) > 0
    assert "通用知识问答" in capabilities
    assert "基于LangGraph的智能对话管理" in capabilities


@pytest.mark.asyncio
async def test_invalid_input_handling():
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


def test_conversation_state_structure():
    """测试对话状态结构"""
    from agents.general_qa.agent import ConversationState
    
    # 验证类型定义
    assert 'messages' in ConversationState.__annotations__
    assert 'current_agent' in ConversationState.__annotations__
    assert 'context' in ConversationState.__annotations__
    assert 'needs_specialist' in ConversationState.__annotations__
    assert 'specialist_type' in ConversationState.__annotations__
    assert 'user_intent' in ConversationState.__annotations__


def test_agent_initialization():
    """测试智能体初始化"""
    agent = GeneralQAAgent()
    
    assert agent.agent_type == AgentType.GENERAL_QA
    assert agent.name == "通用问答助手"
    assert agent.description is not None
    assert agent.graph is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])