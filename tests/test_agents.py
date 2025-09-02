import pytest
from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from agents.general_qa.agent import GeneralQAAgent
import asyncio


class TestBaseAgent:
    def test_agent_initialization(self):
        agent = GeneralQAAgent()
        assert agent.agent_type == AgentType.GENERAL_QA
        assert agent.name == "通用问答助手"
        assert isinstance(agent.get_capabilities(), list)

    def test_message_validation(self):
        agent = GeneralQAAgent()
        
        # Valid message
        valid_message = AgentMessage(
            id="test",
            content="Hello",
            agent_type=AgentType.GENERAL_QA
        )
        assert agent.validate_input(valid_message) is True
        
        # Invalid message
        invalid_message = AgentMessage(
            id="test",
            content="",
            agent_type=AgentType.GENERAL_QA
        )
        assert agent.validate_input(invalid_message) is False


@pytest.mark.asyncio
class TestGeneralQAAgent:
    async def test_process_message(self):
        agent = GeneralQAAgent()
        message = AgentMessage(
            id="test",
            content="Hello, how are you?",
            agent_type=AgentType.GENERAL_QA
        )
        
        # Note: This will fail without proper API key setup
        # This is just a structure test
        assert hasattr(agent, 'process')
        assert callable(agent.process)