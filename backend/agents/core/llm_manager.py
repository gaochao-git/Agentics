"""
统一LLM管理器
为所有智能体提供统一的模型配置和管理功能
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, Any, Optional, Union, List, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import wraps
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor

# 支持的不同LLM提供商
LLM_PROVIDERS = {
    'openai': 'OpenAI',
    'qwen': '千问(Qwen)',
    'deepseek': 'DeepSeek',
    'claude': 'Claude',
    'ollama': 'Ollama',
    'mock': '模拟模式'
}

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM配置数据类"""
    provider: str = 'openai'
    model: str = 'gpt-3.5-turbo'
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 3
    
    # 扩展配置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 缓存时间（秒）
    enable_monitoring: bool = True
    rate_limit: Optional[int] = None  # 每分钟请求限制
    cost_tracking: bool = True
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """验证配置"""
        if self.provider not in LLM_PROVIDERS:
            raise ValueError(f"不支持的提供商: {self.provider}")
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("temperature必须在0-2之间")
        if self.max_tokens < 1:
            raise ValueError("max_tokens必须大于0")


@dataclass
class LLMUsageStats:
    """模型使用统计"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    last_used: Optional[float] = None
    error_rate: float = 0.0
    
    def update_request(self, success: bool, tokens: int, cost: float, response_time: float):
        """更新请求统计"""
        self.total_requests += 1
        self.last_used = time.time()
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            
        self.total_tokens += tokens
        self.total_cost += cost
        
        # 更新平均响应时间
        old_avg = self.average_response_time
        n = self.total_requests
        self.average_response_time = (old_avg * (n - 1) + response_time) / n
        
        # 更新错误率
        self.error_rate = self.failed_requests / self.total_requests


class BaseLLMProvider(ABC):
    """LLM提供商基类"""
    
    @abstractmethod
    def create_llm(self, config: LLMConfig):
        """创建LLM实例"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> list:
        """获取可用模型列表"""
        pass
    
    @abstractmethod
    def validate_config(self, config: LLMConfig) -> bool:
        """验证配置是否有效"""
        pass
    
    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """估算成本"""
        pass
    
    def health_check(self, config: LLMConfig) -> Dict[str, Any]:
        """健康检查"""
        try:
            is_valid = self.validate_config(config)
            return {
                'status': 'healthy' if is_valid else 'unhealthy',
                'provider': config.provider,
                'model': config.model,
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'error',
                'provider': config.provider,
                'error': str(e),
                'timestamp': time.time()
            }


class OpenAIProvider(BaseLLMProvider):
    """OpenAI提供商"""
    
    # OpenAI模型价格 (USD per 1K tokens)
    MODEL_PRICES = {
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        'gpt-3.5-turbo-16k': {'input': 0.003, 'output': 0.004},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo-preview': {'input': 0.01, 'output': 0.03},
        'gpt-4o': {'input': 0.005, 'output': 0.015},
        'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006}
    }
    
    def create_llm(self, config: LLMConfig):
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=config.model,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                max_retries=config.max_retries,
                **config.extra_params
            )
        except ImportError:
            raise ImportError("请先安装 langchain-openai: pip install langchain-openai")
    
    def get_available_models(self) -> list:
        return list(self.MODEL_PRICES.keys())
    
    def validate_config(self, config: LLMConfig) -> bool:
        return bool(config.api_key and config.api_key.startswith('sk-'))
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """估算OpenAI模型成本"""
        if model not in self.MODEL_PRICES:
            return 0.0
        
        prices = self.MODEL_PRICES[model]
        input_cost = (input_tokens / 1000) * prices['input']
        output_cost = (output_tokens / 1000) * prices['output']
        return input_cost + output_cost


class QwenProvider(BaseLLMProvider):
    """千问(Qwen)提供商"""
    
    def create_llm(self, config: LLMConfig):
        try:
            from langchain_community.chat_models import ChatTongyi
            return ChatTongyi(
                model=config.model,
                dashscope_api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        except ImportError:
            raise ImportError("请先安装 langchain-community: pip install langchain-community")
    
    def get_available_models(self) -> list:
        return [
            'qwen-max',
            'qwen-max-1201',
            'qwen-plus',
            'qwen-plus-1201',
            'qwen-turbo',
            'qwen-turbo-1201'
        ]
    
    def validate_config(self, config: LLMConfig) -> bool:
        return bool(config.api_key)
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return 0.0  # 暂不计算成本


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek提供商"""
    
    def create_llm(self, config: LLMConfig):
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=config.model,
                api_key=config.api_key,
                base_url=config.base_url or "https://api.deepseek.com/v1",
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                max_retries=config.max_retries
            )
        except ImportError:
            raise ImportError("请先安装 langchain-openai: pip install langchain-openai")
    
    def get_available_models(self) -> list:
        return [
            'deepseek-chat',
            'deepseek-coder'
        ]
    
    def validate_config(self, config: LLMConfig) -> bool:
        return bool(config.api_key)
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return 0.0


class ClaudeProvider(BaseLLMProvider):
    """Claude提供商"""
    
    def create_llm(self, config: LLMConfig):
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=config.model,
                anthropic_api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                max_retries=config.max_retries
            )
        except ImportError:
            raise ImportError("请先安装 langchain-anthropic: pip install langchain-anthropic")
    
    def get_available_models(self) -> list:
        return [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-haiku-20241022',
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307'
        ]
    
    def validate_config(self, config: LLMConfig) -> bool:
        return bool(config.api_key and config.api_key.startswith('sk-ant-'))
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return 0.0


class OllamaProvider(BaseLLMProvider):
    """Ollama提供商"""
    
    def create_llm(self, config: LLMConfig):
        try:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                model=config.model,
                base_url=config.base_url or "http://localhost:11434",
                temperature=config.temperature,
                num_predict=config.max_tokens,
                timeout=config.timeout
            )
        except ImportError:
            # 如果没有ChatOllama，尝试使用旧版本
            try:
                from langchain_community.llms import Ollama
                
                class OllamaAdapter:
                    """Ollama适配器，将LLM包装成Chat格式"""
                    def __init__(self, ollama_llm):
                        self.llm = ollama_llm
                    
                    def invoke(self, messages):
                        # 提取最后一条用户消息
                        if isinstance(messages, list) and len(messages) > 0:
                            last_message = messages[-1]
                            if hasattr(last_message, 'content'):
                                content = last_message.content
                            else:
                                content = str(last_message)
                        else:
                            content = str(messages)
                        
                        # 调用Ollama并包装响应
                        response = self.llm.invoke(content)
                        
                        class OllamaResponse:
                            def __init__(self, content):
                                self.content = content
                        
                        return OllamaResponse(response)
                    
                    async def ainvoke(self, messages):
                        # 提取最后一条用户消息
                        if isinstance(messages, list) and len(messages) > 0:
                            last_message = messages[-1]
                            if hasattr(last_message, 'content'):
                                content = last_message.content
                            else:
                                content = str(last_message)
                        else:
                            content = str(messages)
                        
                        # 调用Ollama并包装响应
                        response = await self.llm.ainvoke(content)
                        
                        class OllamaResponse:
                            def __init__(self, content):
                                self.content = content
                        
                        return OllamaResponse(response)
                
                ollama_llm = Ollama(
                    model=config.model,
                    base_url=config.base_url or "http://localhost:11434",
                    temperature=config.temperature,
                    num_predict=config.max_tokens,
                    timeout=config.timeout
                )
                
                return OllamaAdapter(ollama_llm)
                
            except ImportError:
                raise ImportError("请先安装 langchain-community: pip install langchain-community")
    
    def get_available_models(self) -> list:
        """获取Ollama可用模型列表"""
        try:
            import requests
            base_url = "http://localhost:11434"
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                return [model['name'] for model in models_data.get('models', [])]
            else:
                logger.warning(f"无法连接到Ollama服务: {response.status_code}")
                return self._get_common_ollama_models()
        except Exception as e:
            logger.warning(f"获取Ollama模型列表失败: {e}")
            return self._get_common_ollama_models()
    
    def _get_common_ollama_models(self) -> list:
        """返回常见的Ollama模型列表"""
        return [
            'llama2:7b',
            'llama2:13b',
            'llama2:70b',
            'llama3:8b',
            'llama3:70b',
            'codellama:7b',
            'codellama:13b',
            'mistral:7b',
            'qwen:7b',
            'qwen:14b',
            'deepseek-coder:6.7b',
            'deepseek-coder:33b'
        ]
    
    def validate_config(self, config: LLMConfig) -> bool:
        """验证Ollama配置"""
        try:
            import requests
            base_url = config.base_url or "http://localhost:11434"
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama服务连接失败: {e}")
            return False
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return 0.0  # Ollama本地运行，无成本


class MockProvider(BaseLLMProvider):
    """模拟提供商，用于测试"""
    
    def create_llm(self, config: LLMConfig):
        class MockLLM:
            def __init__(self, model_name: str):
                self.model_name = model_name
            
            def invoke(self, messages):
                class MockResponse:
                    content = f"这是来自{self.model_name}的模拟响应"
                return MockResponse()
            
            async def ainvoke(self, messages):
                class MockResponse:
                    content = f"这是来自{self.model_name}的模拟响应"
                return MockResponse()
        
        return MockLLM(config.model)
    
    def get_available_models(self) -> list:
        return ['mock-model-1', 'mock-model-2']
    
    def validate_config(self, config: LLMConfig) -> bool:
        return True
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return 0.0


class LLMManager:
    """统一的LLM管理器"""
    
    _instance = None
    _providers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化提供商"""
        self._providers = {
            'openai': OpenAIProvider(),
            'qwen': QwenProvider(),
            'deepseek': DeepSeekProvider(),
            'claude': ClaudeProvider(),
            'ollama': OllamaProvider(),
            'mock': MockProvider()
        }
    
    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        """获取指定提供商"""
        if provider_name not in self._providers:
            raise ValueError(f"不支持的提供商: {provider_name}")
        return self._providers[provider_name]
    
    def get_available_providers(self) -> Dict[str, str]:
        """获取所有可用提供商"""
        return LLM_PROVIDERS.copy()
    
    def get_available_models(self, provider: str = None) -> list:
        """获取可用模型列表"""
        if provider:
            return self.get_provider(provider).get_available_models()
        
        models = {}
        for provider_name, provider_instance in self._providers.items():
            if provider_name != 'mock':  # 排除模拟提供商
                models[provider_name] = provider_instance.get_available_models()
        return models
    
    def create_llm_from_env(self, provider_name: str = None) -> Any:
        """从环境变量创建LLM实例"""
        if not provider_name:
            provider_name = os.getenv('LLM_PROVIDER', 'openai')
        
        config = self._load_config_from_env(provider_name)
        
        if not self.validate_config(config):
            logger.warning(f"配置无效，使用模拟模式: {config}")
            provider_name = 'mock'
            config = LLMConfig(provider='mock', model='mock-model')
        
        return self.create_llm(config)
    
    def create_llm(self, config: LLMConfig) -> Any:
        """根据配置创建LLM实例"""
        provider = self.get_provider(config.provider)
        return provider.create_llm(config)
    
    def validate_config(self, config: LLMConfig) -> bool:
        """验证配置"""
        try:
            provider = self.get_provider(config.provider)
            return provider.validate_config(config)
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False
    
    def _load_config_from_env(self, provider_name: str) -> LLMConfig:
        """从环境变量加载配置"""
        config_kwargs = {
            'provider': provider_name,
            'model': os.getenv(f'{provider_name.upper()}_MODEL'),
            'api_key': os.getenv(f'{provider_name.upper()}_API_KEY'),
            'base_url': os.getenv(f'{provider_name.upper()}_BASE_URL'),
            'temperature': float(os.getenv('LLM_TEMPERATURE', '0.7')),
            'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '2000')),
            'timeout': int(os.getenv('LLM_TIMEOUT', '30')),
            'max_retries': int(os.getenv('LLM_MAX_RETRIES', '3'))
        }
        
        # 设置默认值
        if provider_name == 'openai' and not config_kwargs['model']:
            config_kwargs['model'] = 'gpt-3.5-turbo'
        elif provider_name == 'qwen' and not config_kwargs['model']:
            config_kwargs['model'] = 'qwen-max'
        elif provider_name == 'deepseek' and not config_kwargs['model']:
            config_kwargs['model'] = 'deepseek-chat'
        elif provider_name == 'claude' and not config_kwargs['model']:
            config_kwargs['model'] = 'claude-3-5-haiku-20241022'
        elif provider_name == 'ollama' and not config_kwargs['model']:
            config_kwargs['model'] = 'qwen3:8B'  # 使用实际可用的模型
        
        return LLMConfig(**{k: v for k, v in config_kwargs.items() if v is not None})


# 全局管理器实例
llm_manager = LLMManager()


def get_llm(provider: str = None, **kwargs) -> Any:
    """
    快速获取LLM实例的便捷函数
    
    使用示例:
        llm = get_llm()  # 使用环境变量配置
        llm = get_llm('openai', model='gpt-4')
        llm = get_llm('qwen', api_key='your-key')
        llm = get_llm('ollama', model='qwen3:8B')  # 使用本地Ollama
    """
    if kwargs:
        # 使用自定义配置
        config = LLMConfig(provider=provider or os.getenv('LLM_PROVIDER', 'openai'), **kwargs)
        return llm_manager.create_llm(config)
    else:
        # 使用环境变量配置
        return llm_manager.create_llm_from_env(provider)


def configure_ollama(model: str = "qwen3:8B", base_url: str = "http://localhost:11434") -> LLMConfig:
    """
    配置Ollama的便捷函数
    
    参数:
        model: 模型名称，默认 qwen3:8B
        base_url: Ollama服务地址，默认 http://localhost:11434
    
    返回:
        LLMConfig: 配置对象
    
    使用示例:
        # 基本配置
        config = configure_ollama()
        llm = llm_manager.create_llm(config)
        
        # 自定义模型
        config = configure_ollama("deepseek-r1:8B")
        llm = llm_manager.create_llm(config)
        
        # 自定义服务地址
        config = configure_ollama("qwen3:8B", "http://192.168.1.100:11434")
        llm = llm_manager.create_llm(config)
    """
    return LLMConfig(
        provider="ollama",
        model=model,
        base_url=base_url,
        temperature=0.7,
        max_tokens=2000,
        timeout=60  # Ollama可能需要更长时间
    )


def set_ollama_env(model: str = "qwen3:8B", base_url: str = "http://localhost:11434"):
    """
    设置Ollama环境变量的便捷函数
    
    参数:
        model: 模型名称
        base_url: Ollama服务地址
    
    使用示例:
        # 设置环境变量
        set_ollama_env()
        
        # 然后直接使用
        llm = get_llm()  # 自动使用Ollama配置
    """
    os.environ['LLM_PROVIDER'] = 'ollama'
    os.environ['OLLAMA_MODEL'] = model
    os.environ['OLLAMA_BASE_URL'] = base_url
    os.environ['LLM_TEMPERATURE'] = '0.7'
    os.environ['LLM_MAX_TOKENS'] = '2000'
    os.environ['LLM_TIMEOUT'] = '60'


def get_ollama_models() -> List[str]:
    """
    获取本地Ollama可用模型列表
    
    返回:
        List[str]: 模型名称列表
    
    使用示例:
        models = get_ollama_models()
        print(f"可用模型: {models}")
    """
    try:
        provider = llm_manager.get_provider("ollama")
        return provider.get_available_models()
    except Exception as e:
        logger.error(f"获取Ollama模型列表失败: {e}")
        return []


def test_ollama_connection(base_url: str = "http://localhost:11434") -> Dict[str, Any]:
    """
    测试Ollama连接
    
    参数:
        base_url: Ollama服务地址
    
    返回:
        Dict: 测试结果
    
    使用示例:
        result = test_ollama_connection()
        if result['success']:
            print(f"连接成功，可用模型: {result['models']}")
        else:
            print(f"连接失败: {result['error']}")
    """
    try:
        import requests
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            models = [model['name'] for model in models_data.get('models', [])]
            return {
                'success': True,
                'models': models,
                'count': len(models),
                'base_url': base_url
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}",
                'base_url': base_url
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'base_url': base_url
        }