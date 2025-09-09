"""
Agentics Core Module
提供智能体核心功能和工具
"""

from .llm_manager import LLMManager, get_llm, LLMConfig

__all__ = ['LLMManager', 'get_llm', 'LLMConfig']