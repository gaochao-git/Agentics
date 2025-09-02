from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List
import time


class GeneralQAAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.GENERAL_QA,
            name="通用问答助手",
            description="处理通用知识问答，并可以调用其他专业智能体的能力"
        )
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
        self.specialist_agents = {}

    def register_specialist_agent(self, agent_type: AgentType, agent: BaseAgent):
        self.specialist_agents[agent_type] = agent

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
            content = message.content.lower()
            
            specialist_routing = {
                "发言稿": AgentType.SPEECH_WRITER,
                "新闻稿": AgentType.NEWS_WRITER,
                "公文": AgentType.OFFICIAL_DOCUMENT,
                "研报": AgentType.RESEARCH_REPORT,
                "代码": AgentType.CODE_ASSISTANT,
                "数据分析": AgentType.DATA_ANALYSIS,
            }

            for keyword, specialist_type in specialist_routing.items():
                if keyword in content and specialist_type in self.specialist_agents:
                    specialist_agent = self.specialist_agents[specialist_type]
                    return await specialist_agent.process(message)

            system_prompt = """你是一个专业的通用问答助手。你可以：
1. 回答各种通用知识问题
2. 提供建议和指导
3. 协助解决问题
4. 当用户需要专业服务时，引导其使用相应的专业智能体

请用中文回答，保持专业和友好的语调。"""

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
                content=f"处理请求时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def get_capabilities(self) -> List[str]:
        return [
            "通用知识问答",
            "问题解答",
            "建议咨询",
            "专业智能体路由"
        ]