from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from agents.core.llm_manager import get_llm
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import List, Dict, Any, TypedDict
import time


class ConversationState(TypedDict):
    """对话状态"""
    messages: List[Dict[str, str]]
    current_agent: str
    context: Dict[str, Any]
    needs_specialist: bool
    specialist_type: str
    user_intent: str


class GeneralQAAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.GENERAL_QA,
            name="通用问答助手",
            description="基于LangGraph的智能通用问答助手，支持复杂对话流程和专业智能体路由"
        )
        # 使用核心的统一LLM管理器
        self.llm = get_llm()
        self.specialist_agents = {}
        self.graph = self._build_graph()

    def _build_graph(self):
        """构建对话流程图"""
        workflow = StateGraph(ConversationState)
        
        # 添加节点
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("route_specialist", self._route_specialist)
        workflow.add_node("general_response", self._general_response)
        
        # 设置入口点
        workflow.set_entry_point("analyze_intent")
        
        # 添加边
        workflow.add_conditional_edges(
            "analyze_intent",
            self._should_route_specialist,
            {
                True: "route_specialist",
                False: "general_response"
            }
        )
        
        workflow.add_edge("route_specialist", END)
        workflow.add_edge("general_response", END)
        
        return workflow.compile()
    
    def _analyze_intent(self, state: ConversationState) -> ConversationState:
        """分析用户意图"""
        latest_message = state["messages"][-1]["content"] if state["messages"] else ""
        
        # 简单的关键词检测
        specialist_keywords = {
            "发言稿": AgentType.SPEECH_WRITER,
            "新闻稿": AgentType.NEWS_WRITER,
            "公文": AgentType.OFFICIAL_DOCUMENT,
            "研报": AgentType.RESEARCH_REPORT,
            "代码": AgentType.CODE_ASSISTANT,
            "数据分析": AgentType.DATA_ANALYSIS,
        }
        
        needs_specialist = False
        specialist_type = ""
        
        content_lower = latest_message.lower()
        for keyword, agent_type in specialist_keywords.items():
            if keyword in content_lower:
                needs_specialist = True
                specialist_type = agent_type.value
                break
        
        state["needs_specialist"] = needs_specialist
        state["specialist_type"] = specialist_type
        state["user_intent"] = latest_message
        
        return state
    
    def _should_route_specialist(self, state: ConversationState) -> bool:
        """判断是否需要路由到专业智能体"""
        return state["needs_specialist"] and state["specialist_type"] in [agent.value for agent in self.specialist_agents.keys()]
    
    def _route_specialist(self, state: ConversationState) -> ConversationState:
        """路由到专业智能体"""
        specialist_type = AgentType(state["specialist_type"])
        if specialist_type in self.specialist_agents:
            specialist_agent = self.specialist_agents[specialist_type]
            # 这里可以调用专业智能体的处理方法
            state["current_agent"] = specialist_type.value
        
        return state
    
    def _general_response(self, state: ConversationState) -> ConversationState:
        """通用回答"""
        state["current_agent"] = "general_qa"
        return state

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
            # 构建初始状态
            initial_state: ConversationState = {
                "messages": [{"role": "user", "content": message.content}],
                "current_agent": "general_qa",
                "context": {},
                "needs_specialist": False,
                "specialist_type": "",
                "user_intent": message.content
            }
            
            # 运行图流程
            result = self.graph.invoke(initial_state)
            
            # 根据流程结果决定如何响应
            if result["needs_specialist"] and result["specialist_type"]:
                # 需要专业智能体处理
                specialist_type = AgentType(result["specialist_type"])
                if specialist_type in self.specialist_agents:
                    specialist_agent = self.specialist_agents[specialist_type]
                    return await specialist_agent.process(message)
                else:
                    content = f"您的请求需要{result['specialist_type']}专业智能体处理，但该智能体尚未注册。我将为您提供通用回答。"
            
            # 通用问答处理
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