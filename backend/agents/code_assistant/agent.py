from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from agents.core.llm_manager import get_llm
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict
import time
import re


class CodeAssistantAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.CODE_ASSISTANT,
            name="智能代码助手",
            description="专业的代码助手，支持代码生成、分析、优化和调试"
        )
        # 使用统一的LLM管理器
        self.llm = get_llm()
        
        # 编程语言配置
        self.languages = {
            "python": {
                "extensions": [".py"],
                "keywords": ["python", "py", "django", "flask", "pandas", "numpy"],
                "frameworks": ["Django", "Flask", "FastAPI", "Pandas", "NumPy", "TensorFlow", "PyTorch"]
            },
            "javascript": {
                "extensions": [".js", ".jsx"],
                "keywords": ["javascript", "js", "node", "react", "vue", "angular"],
                "frameworks": ["React", "Vue", "Angular", "Node.js", "Express", "Next.js"]
            },
            "typescript": {
                "extensions": [".ts", ".tsx"],
                "keywords": ["typescript", "ts"],
                "frameworks": ["React", "Vue", "Angular", "Node.js", "Nest.js"]
            },
            "java": {
                "extensions": [".java"],
                "keywords": ["java"],
                "frameworks": ["Spring", "Spring Boot", "Hibernate", "Maven", "Gradle"]
            },
            "go": {
                "extensions": [".go"],
                "keywords": ["go", "golang"],
                "frameworks": ["Gin", "Echo", "Fiber", "GORM"]
            },
            "rust": {
                "extensions": [".rs"],
                "keywords": ["rust"],
                "frameworks": ["Actix", "Rocket", "Warp", "Tokio"]
            },
            "cpp": {
                "extensions": [".cpp", ".hpp", ".c", ".h"],
                "keywords": ["c++", "cpp", "c"],
                "frameworks": ["Qt", "Boost", "OpenCV"]
            }
        }
        
        # 任务类型识别
        self.task_types = {
            "代码生成": ["生成", "写", "创建", "实现", "开发"],
            "代码审查": ["审查", "检查", "分析", "评估", "优化"],
            "调试修复": ["调试", "修复", "bug", "错误", "问题"],
            "代码解释": ["解释", "说明", "理解", "分析这段代码"],
            "重构优化": ["重构", "优化", "改进", "简化"],
            "技术咨询": ["如何", "最佳实践", "建议", "方案", "架构"]
        }

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
            # 分析代码请求
            code_info = self._analyze_code_request(message.content)
            
            # 构建专业的系统提示
            system_prompt = self._build_system_prompt(code_info)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message.content)
            ]

            response = await self.llm.ainvoke(messages)
            
            # 后处理：格式化代码输出
            formatted_content = self._format_code_output(response.content, code_info)
            
            return AgentResponse(
                success=True,
                content=formatted_content,
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                metadata={
                    "task_type": code_info.get("task_type", "通用代码助手"),
                    "language": code_info.get("language", "未指定"),
                    "complexity": code_info.get("complexity", "中等"),
                    "has_code": self._contains_code_block(formatted_content)
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=f"处理代码请求时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def _analyze_code_request(self, content: str) -> Dict:
        """分析代码请求"""
        content_lower = content.lower()
        
        # 识别编程语言
        detected_language = "未指定"
        for lang, config in self.languages.items():
            if any(keyword in content_lower for keyword in config["keywords"]):
                detected_language = lang
                break
        
        # 识别任务类型
        detected_task = "通用代码助手"
        for task_type, keywords in self.task_types.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_task = task_type
                break
        
        # 评估复杂度
        complexity = "中等"
        if any(word in content_lower for word in ["简单", "基础", "入门"]):
            complexity = "简单"
        elif any(word in content_lower for word in ["复杂", "高级", "架构", "系统"]):
            complexity = "复杂"
        
        # 检查是否包含代码
        has_existing_code = bool(re.search(r'```|`[^`]+`|\n\s{4,}', content))
        
        return {
            "language": detected_language,
            "task_type": detected_task,
            "complexity": complexity,
            "has_existing_code": has_existing_code
        }

    def _build_system_prompt(self, code_info: Dict) -> str:
        """构建系统提示"""
        base_prompt = """你是一个专业的高级软件工程师和代码专家。你具备以下技能：

技术能力：
1. 精通多种编程语言和框架
2. 深入理解软件架构和设计模式
3. 熟悉最佳编程实践和代码规范
4. 具备丰富的调试和性能优化经验

代码标准：
- 编写清晰、可读、可维护的代码
- 遵循相应语言的最佳实践和编码规范
- 提供详细的注释和文档
- 考虑错误处理和边界情况
- 注重代码性能和安全性

回答格式：
- 直接回答用户问题
- 提供完整可运行的代码示例
- 包含必要的解释和注释
- 给出相关的最佳实践建议

"""
        
        # 根据分析结果定制提示
        if code_info.get("language") != "未指定":
            lang = code_info["language"]
            lang_config = self.languages.get(lang, {})
            base_prompt += f"\n当前编程语言：{lang.title()}\n"
            if lang_config.get("frameworks"):
                base_prompt += f"相关框架：{', '.join(lang_config['frameworks'])}\n"
        
        if code_info.get("task_type") != "通用代码助手":
            base_prompt += f"任务类型：{code_info['task_type']}\n"
        
        if code_info.get("complexity") == "简单":
            base_prompt += "复杂度：简单 - 提供基础实现，重点关注可读性\n"
        elif code_info.get("complexity") == "复杂":
            base_prompt += "复杂度：复杂 - 提供完整的企业级解决方案，考虑扩展性和维护性\n"
        
        base_prompt += "\n请根据用户需求提供专业的代码解决方案。"
        
        return base_prompt

    def _format_code_output(self, content: str, code_info: Dict) -> str:
        """格式化代码输出"""
        # 确保代码块有正确的语言标识
        if code_info.get("language") != "未指定":
            language = code_info["language"]
            # 替换没有语言标识的代码块
            content = re.sub(r'```\n', f'```{language}\n', content)
            content = re.sub(r'```(\s*\n)', f'```{language}\\1', content)
        
        # 确保每个代码块都有说明
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        if code_blocks and not re.search(r'这是|以下是|代码如下', content):
            content = "以下是相应的代码实现：\n\n" + content
        
        return content.strip()

    def _contains_code_block(self, content: str) -> bool:
        """检查内容是否包含代码块"""
        return bool(re.search(r'```[\w]*\n.*?\n```', content, re.DOTALL))

    def get_capabilities(self) -> List[str]:
        return [
            "多语言代码生成",
            "代码审查与优化",
            "Bug调试和修复",
            "代码重构和改进",
            "架构设计咨询",
            "代码解释和文档",
            "最佳实践建议",
            "性能优化指导",
            "单元测试编写",
            "API设计和实现"
        ]