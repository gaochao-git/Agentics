from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List
import time


class DataAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.DATA_ANALYSIS,
            name="数据分析智能体",
            description="专业的数据分析助手，支持数据处理、分析和可视化"
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
            system_prompt = """你是一个专业的数据分析助手。你擅长：
1. 数据清洗和预处理
2. 统计分析和建模
3. 数据可视化方案
4. 业务数据解读
5. 预测和趋势分析

请提供：
- 清晰的数据分析思路
- 适合的分析方法建议
- Python/R代码实现
- 可视化方案
- 业务洞察和建议

重点关注数据的准确性、分析的科学性和结论的实用性。"""

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
                content=f"处理数据分析请求时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def get_capabilities(self) -> List[str]:
        return [
            "数据清洗",
            "统计分析",
            "数据可视化",
            "业务分析",
            "预测建模"
        ]