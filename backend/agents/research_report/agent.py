from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List
import time


class ResearchReportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.RESEARCH_REPORT,
            name="智能研报智能体",
            description="专业的研究报告撰写助手，支持各类研究报告的深度分析和撰写"
        )
        self.llm = ChatOpenAI(temperature=0.4, model="gpt-3.5-turbo")

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
            system_prompt = """你是一个专业的研究报告撰写助手。你精通：
1. 市场调研报告
2. 行业分析报告
3. 可行性研究报告
4. 竞争分析报告
5. 技术调研报告

请按照专业研报标准撰写：
- 执行摘要：核心观点和结论
- 研究背景：问题和目标
- 研究方法：数据来源和分析方法
- 主体分析：详细分析和论证
- 结论建议：明确的结论和可操作建议
- 附录：支撑数据和参考资料

语言要客观、准确、逻辑严密，数据要有说服力。"""

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
                content=f"生成研究报告时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def get_capabilities(self) -> List[str]:
        return [
            "市场调研报告",
            "行业分析报告",
            "可行性研究",
            "竞争分析",
            "技术调研"
        ]