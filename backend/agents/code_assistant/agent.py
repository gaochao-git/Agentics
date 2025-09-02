from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List
import time


class CodeAssistantAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.CODE_ASSISTANT,
            name="智能代码智能体",
            description="专业的代码助手，支持代码生成、分析、优化和调试"
        )
        self.llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")

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
            system_prompt = """你是一个专业的代码助手。你擅长：
1. 代码生成和编写
2. 代码审查和优化
3. Bug调试和修复
4. 代码重构和改进
5. 技术方案设计
6. 代码解释和文档

支持的编程语言包括但不限于：Python, JavaScript, TypeScript, Java, C++, Go, Rust等。

请提供：
- 清晰的代码实现
- 详细的代码注释
- 最佳实践建议
- 性能优化建议
- 安全注意事项"""

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
                content=f"处理代码请求时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def get_capabilities(self) -> List[str]:
        return [
            "代码生成",
            "代码审查",
            "Bug修复",
            "代码重构",
            "技术咨询",
            "代码解释"
        ]