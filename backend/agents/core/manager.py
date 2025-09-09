from typing import Dict, List, Type, Optional
from langgraph.graph import StateGraph, END
from .base import BaseAgent, AgentType, AgentMessage, AgentResponse, AgentState
import asyncio
import time
import uuid
from datetime import datetime


class AgentManager:
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.graph = None
    # 注册智能体
    def register_agent(self, agent: BaseAgent):
        self.agents[agent.agent_type] = agent
        self._build_graph()
    # 获取智能体
    def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        return self.agents.get(agent_type)
    # 列出所有智能体
    def list_agents(self) -> List[Dict[str, str]]:
        return [
            {
                "type": agent.agent_type.value,
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.get_capabilities()
            }
            for agent in self.agents.values()
        ]
    # 构建智能体图
    def _build_graph(self):
        if not self.agents:
            return
            
        # 简化图结构，不使用复杂的边连接
        graph = StateGraph(AgentState)
        
        # 只添加节点，不设置复杂的边关系
        for agent_type, agent in self.agents.items():
            graph.add_node(agent_type.value, self._create_agent_node(agent))

        # 设置默认入口点
        if AgentType.GENERAL_QA in self.agents:
            graph.set_entry_point("general_qa")
        elif self.agents:
            # 如果没有通用问答助手，使用第一个智能体作为入口
            first_agent = list(self.agents.keys())[0]
            graph.set_entry_point(first_agent.value)

        try:
            self.graph = graph.compile()
        except Exception as e:
            print(f"Warning: Failed to compile graph: {e}")
            self.graph = None

    def _create_agent_node(self, agent: BaseAgent):
        async def agent_node(state: AgentState):
            if state.messages:
                last_message = state.messages[-1]
                start_time = time.time()
                try:
                    response = await agent.process(last_message)
                    execution_time = time.time() - start_time
                    response.execution_time = execution_time
                    
                    result_message = AgentMessage(
                        id=str(uuid.uuid4()),
                        content=response.content,
                        agent_type=agent.agent_type,
                        timestamp=datetime.now()
                    )
                    state.add_message(result_message)
                    state.update_context(f"{agent.agent_type.value}_response", response)
                    
                except Exception as e:
                    error_message = AgentMessage(
                        id=str(uuid.uuid4()),
                        content=f"Error: {str(e)}",
                        agent_type=agent.agent_type,
                        timestamp=datetime.now()
                    )
                    state.add_message(error_message)
                    
            return state
        return agent_node

    async def process_message(self, content: str, agent_type: AgentType = AgentType.GENERAL_QA) -> AgentResponse:
        if agent_type in self.agents:
            agent = self.agents[agent_type]
            message = AgentMessage(
                id=str(uuid.uuid4()),
                content=content,
                agent_type=agent_type,
                timestamp=datetime.now()
            )
            return await agent.process(message)
        else:
            return AgentResponse(
                success=False,
                content="Agent not found",
                agent_type=agent_type,
                execution_time=0,
                error="Agent type not registered"
            )