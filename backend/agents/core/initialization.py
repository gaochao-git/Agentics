from agents.core.manager import AgentManager
from agents.general_qa.agent import GeneralQAAgent
from agents.speech_writer.agent import SpeechWriterAgent
from agents.news_writer.agent import NewsWriterAgent
from agents.official_document.agent import OfficialDocumentAgent
from agents.research_report.agent import ResearchReportAgent
from agents.code_assistant.agent import CodeAssistantAgent
from agents.data_analysis.agent import DataAnalysisAgent


def initialize_agents():
    manager = AgentManager()
    
    general_qa_agent = GeneralQAAgent()
    speech_writer_agent = SpeechWriterAgent()
    news_writer_agent = NewsWriterAgent()
    official_document_agent = OfficialDocumentAgent()
    research_report_agent = ResearchReportAgent()
    code_assistant_agent = CodeAssistantAgent()
    data_analysis_agent = DataAnalysisAgent()
    
    manager.register_agent(general_qa_agent)
    manager.register_agent(speech_writer_agent)
    manager.register_agent(news_writer_agent)
    manager.register_agent(official_document_agent)
    manager.register_agent(research_report_agent)
    manager.register_agent(code_assistant_agent)
    manager.register_agent(data_analysis_agent)
    
    general_qa_agent.register_specialist_agent(speech_writer_agent.agent_type, speech_writer_agent)
    general_qa_agent.register_specialist_agent(news_writer_agent.agent_type, news_writer_agent)
    general_qa_agent.register_specialist_agent(official_document_agent.agent_type, official_document_agent)
    general_qa_agent.register_specialist_agent(research_report_agent.agent_type, research_report_agent)
    general_qa_agent.register_specialist_agent(code_assistant_agent.agent_type, code_assistant_agent)
    general_qa_agent.register_specialist_agent(data_analysis_agent.agent_type, data_analysis_agent)
    
    return manager


agent_manager = initialize_agents()