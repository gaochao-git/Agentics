from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List
import time


class OfficialDocumentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.OFFICIAL_DOCUMENT,
            name="智能公文智能体",
            description="专业的公文撰写助手，支持各类公文格式的标准化创作"
        )
        self.llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")

    async def process(self, message: AgentMessage) -> AgentResponse:
        start_time = time.time()
        
        if not self.validate_input(message):
            return AgentResponse(
                success=False,
                content="输入消息无效",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error="Invalid input"
            )

        try:
            system_prompt = """你是一个专业的公文撰写助手。你精通：
1. 通知、通报、公告
2. 请示、报告、批复
3. 函件、会议纪要
4. 规章制度、工作方案
5. 总结报告、调研报告

请严格按照公文格式规范撰写：
- 标题要准确、简洁、规范
- 主送机关要明确
- 正文要层次清楚、条理分明
- 结尾要有适当的结束语
- 落款要规范完整
- 语言要准确、严谨、简洁
- 符合党政机关公文处理工作条例要求"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message.content)
            ]

            response = await self.llm.ainvoke(messages)
            
            return AgentResponse(
                success=True,
                content=response.content,
                agent_type=self.agent_type,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=f"生成公文时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def get_capabilities(self) -> List[str]:
        return [
            "通知公告撰写",
            "请示报告",
            "函件起草",
            "会议纪要",
            "规章制度",
            "工作方案"
        ]