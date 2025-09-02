from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List
import time


class NewsWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.NEWS_WRITER,
            name="新闻稿智能体",
            description="专业的新闻稿撰写助手，支持各类新闻稿件的创作"
        )
        self.llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")

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
            system_prompt = """你是一个专业的新闻稿撰写助手。你擅长：
1. 企业新闻稿撰写
2. 产品发布新闻
3. 人事变动公告
4. 业务合作新闻
5. 活动报道新闻

请根据用户需求，创作具有新闻价值、结构完整的新闻稿。
遵循新闻写作规范：
- 标题要吸引人且准确
- 导语要简洁明了，包含5W1H要素
- 正文要客观真实，层次分明
- 结尾要有适当的总结或展望
- 语言要准确、简洁、生动"""

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
                content=f"生成新闻稿时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def get_capabilities(self) -> List[str]:
        return [
            "企业新闻稿",
            "产品发布新闻",
            "人事公告",
            "合作新闻",
            "活动报道"
        ]