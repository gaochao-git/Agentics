from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List
import time


class SpeechWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.SPEECH_WRITER,
            name="发言稿智能体",
            description="专业的发言稿撰写助手，支持各类正式场合的发言稿创作"
        )
        self.llm = ChatOpenAI(temperature=0.6, model="gpt-3.5-turbo")

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
            system_prompt = """你是一个专业的发言稿撰写助手。你擅长：
1. 撰写各类正式场合的发言稿
2. 会议致辞、开幕词、闭幕词
3. 庆典讲话、年会发言
4. 工作汇报、述职报告
5. 学术演讲、培训讲话

请根据用户需求，创作结构清晰、逻辑严谨、语言得体的发言稿。
注意：
- 开头要有合适的称呼和问候
- 主体内容要条理清晰
- 结尾要有适当的总结和展望
- 语言要正式但不失亲和力"""

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
                content=f"生成发言稿时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def get_capabilities(self) -> List[str]:
        return [
            "会议致辞撰写",
            "庆典讲话创作",
            "工作汇报撰写",
            "学术演讲稿",
            "年会发言稿"
        ]