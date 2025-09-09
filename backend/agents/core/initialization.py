# 全局智能体管理器实例
_agent_manager = None


def get_agent_manager():
    """获取全局智能体管理器实例"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = create_agent_manager()
    return _agent_manager


def create_agent_manager():
    """创建并配置智能体管理器"""
    from .manager import AgentManager
    from ..general_qa.agent import GeneralQAAgent
    from .llm_manager import set_ollama_env
    
    # 设置使用Ollama
    set_ollama_env("qwen3:8B")
    print("✓ 已配置使用本地Ollama模型 qwen3:8B")
    
    manager = AgentManager()
    
    try:
        # 创建通用问答智能体
        general_qa_agent = GeneralQAAgent()
        manager.register_agent(general_qa_agent)
        print("✓ 通用问答智能体注册成功")
        
        # 尝试导入并注册其他智能体
        try:
            from ..speech_writer.agent import SpeechWriterAgent
            speech_writer_agent = SpeechWriterAgent()
            manager.register_agent(speech_writer_agent)
            general_qa_agent.register_specialist_agent(speech_writer_agent.agent_type, speech_writer_agent)
            print("✓ 发言稿写作智能体注册成功")
        except ImportError as e:
            print(f"⚠ 发言稿写作智能体未找到: {e}")
        
        try:
            from ..news_writer.agent import NewsWriterAgent
            news_writer_agent = NewsWriterAgent()
            manager.register_agent(news_writer_agent)
            general_qa_agent.register_specialist_agent(news_writer_agent.agent_type, news_writer_agent)
            print("✓ 新闻稿写作智能体注册成功")
        except ImportError as e:
            print(f"⚠ 新闻稿写作智能体未找到: {e}")
        
        try:
            from ..official_document.agent import OfficialDocumentAgent
            official_document_agent = OfficialDocumentAgent()
            manager.register_agent(official_document_agent)
            general_qa_agent.register_specialist_agent(official_document_agent.agent_type, official_document_agent)
            print("✓ 公文写作智能体注册成功")
        except ImportError as e:
            print(f"⚠ 公文写作智能体未找到: {e}")
        
        try:
            from ..research_report.agent import ResearchReportAgent
            research_report_agent = ResearchReportAgent()
            manager.register_agent(research_report_agent)
            general_qa_agent.register_specialist_agent(research_report_agent.agent_type, research_report_agent)
            print("✓ 研报写作智能体注册成功")
        except ImportError as e:
            print(f"⚠ 研报写作智能体未找到: {e}")
        
        try:
            from ..code_assistant.agent import CodeAssistantAgent
            code_assistant_agent = CodeAssistantAgent()
            manager.register_agent(code_assistant_agent)
            general_qa_agent.register_specialist_agent(code_assistant_agent.agent_type, code_assistant_agent)
            print("✓ 代码助手智能体注册成功")
        except ImportError as e:
            print(f"⚠ 代码助手智能体未找到: {e}")
        
        try:
            from ..data_analysis.agent import DataAnalysisAgent
            data_analysis_agent = DataAnalysisAgent()
            manager.register_agent(data_analysis_agent)
            general_qa_agent.register_specialist_agent(data_analysis_agent.agent_type, data_analysis_agent)
            print("✓ 数据分析智能体注册成功")
        except ImportError as e:
            print(f"⚠ 数据分析智能体未找到: {e}")
        
    except Exception as e:
        print(f"智能体初始化出错: {e}")
        # 如果出错，至少确保有一个通用问答智能体
        if not manager.agents:
            from ..general_qa.agent import GeneralQAAgent
            general_qa_agent = GeneralQAAgent()
            manager.register_agent(general_qa_agent)
    
    print(f"智能体系统初始化完成，注册了 {len(manager.agents)} 个智能体")
    return manager


def initialize_agents():
    """初始化智能体系统"""
    return get_agent_manager()


# 延迟初始化，只在首次调用时创建
def lazy_get_agent_manager():
    """延迟获取智能体管理器，避免Django启动时出错"""
    return get_agent_manager()