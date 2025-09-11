from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from agents.core.llm_manager import get_llm
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict
import time
import re
from datetime import datetime


class NewsWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.NEWS_WRITER,
            name="新闻稿智能体",
            description="专业的新闻稿撰写助手，支持各类新闻稿件的创作"
        )
        # 使用统一的LLM管理器
        self.llm = get_llm()
        
        # 新闻稿类型模板
        self.news_types = {
            "企业新闻": {
                "structure": ["标题", "导语", "企业背景", "具体内容", "意义影响", "结尾"],
                "focus": "企业发展、成就、变化"
            },
            "产品发布": {
                "structure": ["标题", "导语", "产品介绍", "功能特点", "市场意义", "上市信息"],
                "focus": "产品特性、创新点、市场价值"
            },
            "人事变动": {
                "structure": ["标题", "导语", "人员背景", "职位变动", "公司声明", "展望"],
                "focus": "人员资历、变动原因、未来规划"
            },
            "合作协议": {
                "structure": ["标题", "导语", "合作双方", "合作内容", "预期效果", "声明"],
                "focus": "合作优势、互补性、共赢前景"
            },
            "活动报道": {
                "structure": ["标题", "导语", "活动背景", "活动过程", "参与反响", "总结"],
                "focus": "活动亮点、参与度、社会影响"
            },
            "业绩公告": {
                "structure": ["标题", "导语", "业绩数据", "增长分析", "市场表现", "展望"],
                "focus": "数据准确、增长原因、未来预期"
            }
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
            # 分析新闻类型和要求
            news_info = self._analyze_news_requirements(message.content)
            
            # 构建专业的系统提示
            system_prompt = self._build_system_prompt(news_info)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message.content)
            ]

            response = await self.llm.ainvoke(messages)
            
            # 后处理：格式化新闻稿输出
            formatted_content = self._format_news_output(response.content, news_info)
            
            return AgentResponse(
                success=True,
                content=formatted_content,
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                metadata={
                    "news_type": news_info.get("type", "通用新闻"),
                    "estimated_words": self._count_words(formatted_content),
                    "urgency": news_info.get("urgency", "普通"),
                    "target_audience": news_info.get("audience", "公众")
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=f"生成新闻稿时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def _analyze_news_requirements(self, content: str) -> Dict:
        """分析新闻稿需求"""
        content_lower = content.lower()
        
        # 识别新闻类型
        news_type = "通用新闻"
        for type_name in self.news_types.keys():
            if any(keyword in content_lower for keyword in type_name.split()):
                news_type = type_name
                break
        
        # 识别其他关键词
        if any(word in content_lower for word in ["发布", "推出", "上市"]):
            news_type = "产品发布"
        elif any(word in content_lower for word in ["任命", "升职", "离职", "加入"]):
            news_type = "人事变动"
        elif any(word in content_lower for word in ["合作", "协议", "签约", "战略"]):
            news_type = "合作协议"
        elif any(word in content_lower for word in ["财报", "业绩", "营收", "利润"]):
            news_type = "业绩公告"
        elif any(word in content_lower for word in ["活动", "会议", "论坛", "发布会"]):
            news_type = "活动报道"
        
        # 分析紧急程度
        urgency = "普通"
        if any(word in content_lower for word in ["紧急", "重要", "重大"]):
            urgency = "重要"
        elif any(word in content_lower for word in ["突发", "即时"]):
            urgency = "紧急"
        
        # 分析目标受众
        audience = "公众"
        if any(word in content_lower for word in ["媒体", "记者"]):
            audience = "媒体"
        elif any(word in content_lower for word in ["投资者", "股东"]):
            audience = "投资者"
        elif any(word in content_lower for word in ["员工", "内部"]):
            audience = "内部"
        
        return {
            "type": news_type,
            "urgency": urgency,
            "audience": audience,
            "structure": self.news_types.get(news_type, {}).get("structure", []),
            "focus": self.news_types.get(news_type, {}).get("focus", "")
        }

    def _build_system_prompt(self, news_info: Dict) -> str:
        """构建系统提示"""
        base_prompt = """你是一个专业的新闻稿撰写专家。你需要根据用户需求创作高质量的新闻稿。

新闻写作基本原则：
1. 真实性：内容必须真实可靠，有事实依据
2. 时效性：突出新闻的时间价值
3. 客观性：保持中立客观的报道立场
4. 准确性：事实、数据、引用必须准确无误

新闻稿结构要求：
- 标题：简洁有力，突出要点（15-25字）
- 导语：回答5W1H（何时、何地、何人、何事、为何、如何）
- 正文：按重要性递减排列，层次分明
- 结尾：适当总结或展望

语言要求：
- 使用第三人称客观描述
- 语言简洁明了，避免冗长句式
- 多用事实和数据支撑观点
- 避免主观性强的形容词

"""
        
        # 根据新闻类型定制
        if news_info.get("type") != "通用新闻":
            template_info = self.news_types.get(news_info["type"], {})
            base_prompt += f"\n当前新闻类型：{news_info['type']}\n"
            base_prompt += f"建议结构：{' -> '.join(template_info.get('structure', []))}\n"
            base_prompt += f"关注重点：{template_info.get('focus', '')}\n"
        
        if news_info.get("urgency") != "普通":
            base_prompt += f"重要程度：{news_info['urgency']}\n"
        
        if news_info.get("audience") != "公众":
            base_prompt += f"目标受众：{news_info['audience']}\n"
        
        base_prompt += f"\n发布时间：{datetime.now().strftime('%Y年%m月%d日')}\n"
        base_prompt += "\n请根据以上要求创作一份专业的新闻稿。"
        
        return base_prompt

    def _format_news_output(self, content: str, news_info: Dict) -> str:
        """格式化新闻稿输出"""
        lines = content.split('\n')
        formatted_lines = []
        
        # 确保有标题
        if lines and not lines[0].startswith('#'):
            if len(lines[0]) < 50:  # 假设第一行是标题
                formatted_lines.append(f"# {lines[0].strip()}")
                lines = lines[1:]
            else:
                # 添加默认标题
                formatted_lines.append(f"# {news_info.get('type', '新闻')}稿")
        
        # 添加新闻头部信息
        formatted_lines.append(f"\n**发布时间：** {datetime.now().strftime('%Y年%m月%d日')}")
        if news_info.get("urgency") != "普通":
            formatted_lines.append(f"**重要程度：** {news_info['urgency']}")
        formatted_lines.append("")
        
        # 处理正文内容
        for line in lines:
            if line.strip():
                formatted_lines.append(line.strip())
            else:
                formatted_lines.append("")
        
        # 确保段落分明
        content = '\n'.join(formatted_lines)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()

    def _count_words(self, content: str) -> int:
        """统计字数"""
        # 去除markdown标记
        clean_content = re.sub(r'[#*`\-=]', '', content)
        # 统计中文字符数
        word_count = len(clean_content.replace(' ', '').replace('\n', ''))
        return word_count

    def get_capabilities(self) -> List[str]:
        return [
            "企业新闻稿撰写",
            "产品发布新闻",
            "人事变动公告",
            "合作协议新闻",
            "活动报道撰写",
            "业绩公告新闻",
            "危机公关稿件",
            "媒体通稿撰写"
        ]