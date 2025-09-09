from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime

# 智能体类型
class AgentType(Enum):
    GENERAL_QA = "general_qa"
    SPEECH_WRITER = "speech_writer"
    NEWS_WRITER = "news_writer"
    OFFICIAL_DOCUMENT = "official_document"
    RESEARCH_REPORT = "research_report"
    CODE_ASSISTANT = "code_assistant"
    DATA_ANALYSIS = "data_analysis"


@dataclass
class AgentMessage:
    id: str
    content: str
    agent_type: AgentType
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()


@dataclass
class AgentResponse:
    success: bool
    content: str
    agent_type: AgentType
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseAgent(ABC):
    def __init__(self, agent_type: AgentType, name: str, description: str):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.id = str(uuid.uuid4())

    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentResponse:
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        pass

    def validate_input(self, message: AgentMessage) -> bool:
        return bool(message.content and message.content.strip())


class AgentState:
    def __init__(self):
        self.messages: List[AgentMessage] = []
        self.current_agent: Optional[str] = None
        self.context: Dict[str, Any] = {}
        self.session_id: str = str(uuid.uuid4())

    def add_message(self, message: AgentMessage):
        self.messages.append(message)

    def get_conversation_history(self) -> List[AgentMessage]:
        return self.messages.copy()

    def update_context(self, key: str, value: Any):
        self.context[key] = value

    def get_context(self, key: str) -> Any:
        return self.context.get(key)