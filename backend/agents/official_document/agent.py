from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from agents.core.llm_manager import get_llm
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict
import time
import re
from datetime import datetime


class OfficialDocumentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.OFFICIAL_DOCUMENT,
            name="智能公文智能体",
            description="专业的公文撰写助手，支持各类公文格式的标准化创作"
        )
        # 使用统一的LLM管理器
        self.llm = get_llm()
        
        # 公文类型模板库
        self.document_types = {
            "通知": {
                "structure": ["标题", "主送机关", "正文", "结束语", "落款", "日期"],
                "tone": "正式、明确、简洁",
                "format": "行政公文"
            },
            "请示": {
                "structure": ["标题", "主送机关", "事项背景", "请示事项", "理由说明", "结尾", "落款"],
                "tone": "恳请、严谨、详实",
                "format": "上行文"
            },
            "报告": {
                "structure": ["标题", "主送机关", "情况概述", "主要内容", "问题分析", "建议措施", "落款"],
                "tone": "客观、真实、准确",
                "format": "上行文"
            },
            "批复": {
                "structure": ["标题", "主送机关", "批复事项", "批复意见", "要求", "落款"],
                "tone": "权威、明确、指导性",
                "format": "下行文"
            },
            "函": {
                "structure": ["标题", "主送机关", "缘由", "事项", "要求", "联系方式", "落款"],
                "tone": "平等、商洽、协商",
                "format": "平行文"
            },
            "会议纪要": {
                "structure": ["标题", "会议基本情况", "主要议题", "讨论意见", "决定事项", "落款"],
                "tone": "客观、准确、完整",
                "format": "记录文"
            },
            "工作方案": {
                "structure": ["标题", "背景目标", "工作原则", "具体措施", "时间安排", "组织保障"],
                "tone": "可行、具体、操作性强",
                "format": "规划文"
            },
            "规章制度": {
                "structure": ["标题", "总则", "适用范围", "具体条款", "监督执行", "附则"],
                "tone": "严谨、规范、条理清晰",
                "format": "规范文"
            }
        }
        
        # 紧急程度识别
        self.urgency_levels = {
            "特急": ["特急", "十万火急", "紧急", "立即", "马上"],
            "急件": ["急件", "尽快", "加急", "紧急处理"],
            "普通": ["常规", "一般", "按时"]
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
            # 分析公文需求
            doc_info = self._analyze_document_requirements(message.content)
            
            # 构建专业的系统提示
            system_prompt = self._build_system_prompt(doc_info)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message.content)
            ]

            response = await self.llm.ainvoke(messages)
            
            # 后处理：格式化公文输出
            formatted_content = self._format_document_output(response.content, doc_info)
            
            return AgentResponse(
                success=True,
                content=formatted_content,
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                metadata={
                    "document_type": doc_info.get("type", "通用公文"),
                    "urgency_level": doc_info.get("urgency", "普通"),
                    "word_count": self._count_words(formatted_content),
                    "structure_elements": doc_info.get("structure", [])
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=f"生成公文时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def _analyze_document_requirements(self, content: str) -> Dict:
        """分析公文撰写需求"""
        content_lower = content.lower()
        
        # 识别公文类型
        doc_type = "通用公文"
        for type_name in self.document_types.keys():
            if type_name in content or any(keyword in content_lower for keyword in type_name.split()):
                doc_type = type_name
                break
        
        # 识别其他关键词
        if any(word in content_lower for word in ["通知", "告知", "知照", "传达"]):
            doc_type = "通知"
        elif any(word in content_lower for word in ["请示", "申请", "请求", "恳请"]):
            doc_type = "请示"
        elif any(word in content_lower for word in ["汇报", "报告", "总结", "反映"]):
            doc_type = "报告"
        elif any(word in content_lower for word in ["批复", "答复", "批准", "同意"]):
            doc_type = "批复"
        elif any(word in content_lower for word in ["函", "商洽", "协商", "联系"]):
            doc_type = "函"
        elif any(word in content_lower for word in ["会议", "纪要", "记录", "会谈"]):
            doc_type = "会议纪要"
        elif any(word in content_lower for word in ["方案", "计划", "安排"]):
            doc_type = "工作方案"
        elif any(word in content_lower for word in ["制度", "规定", "办法", "条例"]):
            doc_type = "规章制度"
        
        # 分析紧急程度
        urgency = "普通"
        for level, keywords in self.urgency_levels.items():
            if any(keyword in content for keyword in keywords):
                urgency = level
                break
        
        # 获取文档结构
        doc_template = self.document_types.get(doc_type, {})
        
        return {
            "type": doc_type,
            "urgency": urgency,
            "structure": doc_template.get("structure", []),
            "tone": doc_template.get("tone", "正式、规范"),
            "format": doc_template.get("format", "公文")
        }

    def _build_system_prompt(self, doc_info: Dict) -> str:
        """构建系统提示"""
        base_prompt = """你是一个专业的公文撰写专家，精通党政机关公文处理工作条例。

核心能力：
1. 熟练掌握各类公文格式和写作规范
2. 深入理解公文的行文规则和语言特点
3. 具备丰富的政务写作和公文处理经验

写作原则：
- 主题突出：一文一事，主题明确
- 材料真实：以事实为准，数据准确
- 结构合理：层次清晰，逻辑严密
- 语言规范：用词准确，表述简洁
- 格式标准：严格按照国家标准执行

公文要素：
- 标题：机关名称+事由+文种
- 主送机关：明确收文对象
- 正文：开头+主体+结尾
- 附件：相关材料说明
- 发文机关署名：规范完整
- 成文日期：准确标注

语言要求：
- 准确：用词恰当，表意清楚
- 简洁：文字精练，删繁就简
- 庄重：格调严肃，文风端正
- 规范：符合语法，标点正确
"""
        
        # 根据公文类型定制提示
        if doc_info.get("type") != "通用公文":
            doc_template = self.document_types.get(doc_info["type"], {})
            base_prompt += f"\n当前公文类型：{doc_info['type']}\n"
            base_prompt += f"文档结构：{' -> '.join(doc_template.get('structure', []))}\n"
            base_prompt += f"语言风格：{doc_template.get('tone', '正式、规范')}\n"
            base_prompt += f"公文性质：{doc_template.get('format', '公文')}\n"
        
        if doc_info.get("urgency") != "普通":
            base_prompt += f"紧急程度：{doc_info['urgency']} - 请在标题或开头注明\n"
        
        base_prompt += f"\n成文日期：{datetime.now().strftime('%Y年%m月%d日')}\n"
        base_prompt += "\n请根据以上要求撰写规范的公文。"
        
        return base_prompt

    def _format_document_output(self, content: str, doc_info: Dict) -> str:
        """格式化公文输出"""
        lines = content.split('\n')
        formatted_lines = []
        
        # 确保有标题
        if lines and not lines[0].startswith('#'):
            if len(lines[0]) < 80:  # 假设第一行是标题
                formatted_lines.append(f"# {lines[0].strip()}")
                lines = lines[1:]
            else:
                # 添加默认标题
                doc_type = doc_info.get('type', '公文')
                formatted_lines.append(f"# 关于XXX的{doc_type}")
        
        # 添加公文头部信息
        if doc_info.get("urgency") != "普通":
            formatted_lines.append(f"\n**紧急程度：** {doc_info['urgency']}")
        
        formatted_lines.append(f"\n**成文日期：** {datetime.now().strftime('%Y年%m月%d日')}")
        formatted_lines.append("")
        
        # 处理正文内容
        for line in lines:
            if line.strip():
                # 识别主送机关格式
                if line.strip().endswith('：') and len(line.strip()) < 50:
                    formatted_lines.append(f"**{line.strip()}**")
                # 识别落款部分
                elif re.match(r'^\s*(\w+办公室|\w+委员会|\w+政府)', line.strip()):
                    formatted_lines.append(f"\n{' ' * 40}{line.strip()}")
                else:
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
            "通知公告撰写",
            "请示报告起草",
            "批复文件撰写",
            "函件商洽起草",
            "会议纪要整理",
            "工作方案制定",
            "规章制度起草",
            "总结报告撰写",
            "调研报告编制",
            "公文格式规范化"
        ]