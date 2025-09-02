from typing import Dict, List, Type, Optional
from langgraph.graph import StateGraph, END
from .base import BaseAgent, AgentType, AgentMessage, AgentResponse, AgentState
import asyncio
import time


class AgentManager:
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.graph = None
        self._build_graph()

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.agent_type] = agent
        self._build_graph()

    def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        return self.agents.get(agent_type)

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

    def _build_graph(self):
        graph = StateGraph(AgentState)
        
        for agent_type, agent in self.agents.items():
            graph.add_node(agent_type.value, self._create_agent_node(agent))

        graph.add_edge("general_qa", END)
        
        for agent_type in self.agents.keys():
            if agent_type != AgentType.GENERAL_QA:
                graph.add_edge(agent_type.value, END)

        graph.set_entry_point("general_qa")
        self.graph = graph.compile()

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
                        agent_type=agent.agent_type
                    )
                    state.add_message(result_message)
                    state.update_context(f"{agent.agent_type.value}_response", response)
                    
                except Exception as e:
                    error_message = AgentMessage(
                        id=str(uuid.uuid4()),
                        content=f"Error: {str(e)}",
                        agent_type=agent.agent_type
                    )
                    state.add_message(error_message)
                    
            return state
        return agent_node

    async def process_message(self, content: str, agent_type: AgentType = AgentType.GENERAL_QA) -> AgentResponse:
        state = AgentState()
        message = AgentMessage(
            id=str(uuid.uuid4()),
            content=content,
            agent_type=agent_type
        )
        state.add_message(message)
        state.current_agent = agent_type.value

        if agent_type in self.agents:
            agent = self.agents[agent_type]
            return await agent.process(message)
        else:
            return AgentResponse(
                success=False,
                content="Agent not found",
                agent_type=agent_type,
                execution_time=0,
                error="Agent type not registered"
            )