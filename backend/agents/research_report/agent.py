from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from agents.core.llm_manager import get_llm
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict
import time
import re
from datetime import datetime


class ResearchReportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.RESEARCH_REPORT,
            name="智能研报智能体",
            description="专业的研究报告撰写助手，支持各类研究报告的深度分析和撰写"
        )
        # 使用统一的LLM管理器
        self.llm = get_llm()
        
        # 研报类型模板库
        self.report_types = {
            "市场调研报告": {
                "structure": ["执行摘要", "市场概况", "市场规模", "竞争格局", "趋势分析", "机会与风险", "结论建议"],
                "focus": "市场规模、用户需求、竞争态势、发展趋势",
                "methodology": "问卷调查、深度访谈、数据分析、案例研究"
            },
            "行业分析报告": {
                "structure": ["行业概述", "发展现状", "产业链分析", "竞争格局", "发展趋势", "投资机会", "风险评估"],
                "focus": "行业发展阶段、产业链结构、竞争环境、政策影响",
                "methodology": "产业调研、专家访谈、数据挖掘、对比分析"
            },
            "可行性研究报告": {
                "structure": ["项目概述", "市场分析", "技术方案", "投资估算", "财务分析", "风险评估", "可行性结论"],
                "focus": "技术可行性、经济可行性、市场可行性、风险可控性",
                "methodology": "技术评估、财务建模、敏感性分析、风险分析"
            },
            "竞争分析报告": {
                "structure": ["竞争环境", "主要竞争者", "竞争优势", "市场地位", "战略分析", "SWOT分析", "竞争策略"],
                "focus": "竞争对手实力、市场份额、差异化优势、战略定位",
                "methodology": "竞品分析、市场调研、战略分析、SWOT分析"
            },
            "技术调研报告": {
                "structure": ["技术背景", "现状分析", "技术路线", "应用场景", "发展趋势", "技术评估", "应用建议"],
                "focus": "技术成熟度、应用前景、技术壁垒、发展方向",
                "methodology": "文献调研、技术评估、专家咨询、案例分析"
            },
            "投资研究报告": {
                "structure": ["投资要点", "公司概况", "业务分析", "财务分析", "估值分析", "风险提示", "投资建议"],
                "focus": "投资价值、成长性、盈利能力、估值水平",
                "methodology": "基本面分析、财务建模、估值模型、风险评估"
            }
        }
        
        # 研究深度等级
        self.depth_levels = {
            "概览": ["概览", "简要", "初步", "快速"],
            "标准": ["标准", "常规", "一般", "基础"],
            "深度": ["深度", "详细", "全面", "深入", "完整"]
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
            # 分析研报需求
            report_info = self._analyze_research_requirements(message.content)
            
            # 构建专业的系统提示
            system_prompt = self._build_system_prompt(report_info)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message.content)
            ]

            response = await self.llm.ainvoke(messages)
            
            # 后处理：格式化研报输出
            formatted_content = self._format_research_output(response.content, report_info)
            
            return AgentResponse(
                success=True,
                content=formatted_content,
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                metadata={
                    "report_type": report_info.get("type", "通用研究报告"),
                    "research_depth": report_info.get("depth", "标准"),
                    "estimated_pages": self._estimate_pages(formatted_content),
                    "methodology": report_info.get("methodology", "综合分析")
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=f"生成研究报告时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def _analyze_research_requirements(self, content: str) -> Dict:
        """分析研究报告需求"""
        content_lower = content.lower()
        
        # 识别报告类型
        report_type = "通用研究报告"
        for type_name in self.report_types.keys():
            if any(keyword in content_lower for keyword in type_name.split()):
                report_type = type_name
                break
        
        # 识别其他关键词
        if any(word in content_lower for word in ["市场", "调研", "用户", "需求"]):
            report_type = "市场调研报告"
        elif any(word in content_lower for word in ["行业", "产业", "发展", "现状"]):
            report_type = "行业分析报告"
        elif any(word in content_lower for word in ["可行性", "项目", "投资", "建设"]):
            report_type = "可行性研究报告"
        elif any(word in content_lower for word in ["竞争", "对手", "竞品", "比较"]):
            report_type = "竞争分析报告"
        elif any(word in content_lower for word in ["技术", "工艺", "方案", "解决方案"]):
            report_type = "技术调研报告"
        elif any(word in content_lower for word in ["投资", "股票", "估值", "财务"]):
            report_type = "投资研究报告"
        
        # 分析研究深度
        depth = "标准"
        for level, keywords in self.depth_levels.items():
            if any(keyword in content_lower for keyword in keywords):
                depth = level
                break
        
        # 获取报告模板信息
        report_template = self.report_types.get(report_type, {})
        
        # 识别目标行业或领域
        industry = self._extract_industry(content)
        
        return {
            "type": report_type,
            "depth": depth,
            "industry": industry,
            "structure": report_template.get("structure", []),
            "focus": report_template.get("focus", "综合分析"),
            "methodology": report_template.get("methodology", "数据分析")
        }

    def _extract_industry(self, content: str) -> str:
        """提取行业领域"""
        industries = {
            "互联网": ["互联网", "网络", "在线", "电商", "平台"],
            "金融": ["金融", "银行", "保险", "证券", "投资"],
            "制造业": ["制造", "生产", "工厂", "加工", "工业"],
            "房地产": ["房地产", "地产", "房屋", "物业", "建筑"],
            "医疗健康": ["医疗", "健康", "医院", "药品", "医药"],
            "教育": ["教育", "培训", "学校", "学习", "教学"],
            "零售": ["零售", "商店", "超市", "购物", "消费"],
            "汽车": ["汽车", "车辆", "交通", "出行", "驾驶"]
        }
        
        for industry, keywords in industries.items():
            if any(keyword in content for keyword in keywords):
                return industry
        return "通用行业"

    def _build_system_prompt(self, report_info: Dict) -> str:
        """构建系统提示"""
        base_prompt = """你是一个资深的研究分析师和商业顾问，具备以下专业能力：

核心专长：
1. 深度的行业洞察和市场分析能力
2. 严谨的数据收集和分析方法论
3. 清晰的逻辑推理和论证能力
4. 丰富的商业实战和咨询经验

研究方法论：
- 定量分析：数据挖掘、统计分析、建模预测
- 定性分析：专家访谈、案例研究、趋势分析
- 综合分析：SWOT分析、波特五力、价值链分析
- 验证机制：交叉验证、敏感性分析、情景分析

报告标准：
- 结构完整：逻辑清晰，层次分明
- 数据支撑：事实为基础，论证有力
- 分析深入：多维度分析，洞察深刻
- 结论明确：观点清晰，建议可行
- 专业严谨：用词准确，表述客观

质量要求：
- 信息准确性：确保数据和事实的真实性
- 分析客观性：避免主观臆断，保持中立立场
- 逻辑严密性：论证过程清晰，结论有说服力
- 实用价值：提供可操作的洞察和建议
"""
        
        # 根据报告类型定制提示
        if report_info.get("type") != "通用研究报告":
            report_template = self.report_types.get(report_info["type"], {})
            base_prompt += f"\n当前报告类型：{report_info['type']}\n"
            base_prompt += f"报告结构：{' -> '.join(report_template.get('structure', []))}\n"
            base_prompt += f"分析重点：{report_template.get('focus', '')}\n"
            base_prompt += f"研究方法：{report_template.get('methodology', '')}\n"
        
        if report_info.get("industry") != "通用行业":
            base_prompt += f"\n目标行业：{report_info['industry']}\n"
        
        if report_info.get("depth") == "概览":
            base_prompt += "研究深度：概览级别 - 重点突出核心观点，篇幅适中\n"
        elif report_info.get("depth") == "深度":
            base_prompt += "研究深度：深度分析 - 提供全面详细的分析，支撑数据充分\n"
        
        base_prompt += f"\n报告日期：{datetime.now().strftime('%Y年%m月%d日')}\n"
        base_prompt += "\n请根据以上要求撰写专业的研究报告。"
        
        return base_prompt

    def _format_research_output(self, content: str, report_info: Dict) -> str:
        """格式化研究报告输出"""
        lines = content.split('\n')
        formatted_lines = []
        
        # 确保有标题
        if lines and not lines[0].startswith('#'):
            if len(lines[0]) < 60:  # 假设第一行是标题
                formatted_lines.append(f"# {lines[0].strip()}")
                lines = lines[1:]
            else:
                # 添加默认标题
                report_type = report_info.get('type', '研究报告')
                industry = report_info.get('industry', '')
                if industry != "通用行业":
                    formatted_lines.append(f"# {industry}{report_type}")
                else:
                    formatted_lines.append(f"# {report_type}")
        
        # 添加报告头部信息
        formatted_lines.append(f"\n**报告日期：** {datetime.now().strftime('%Y年%m月%d日')}")
        formatted_lines.append(f"**研究深度：** {report_info.get('depth', '标准')}")
        if report_info.get("industry") != "通用行业":
            formatted_lines.append(f"**目标行业：** {report_info['industry']}")
        formatted_lines.append(f"**研究方法：** {report_info.get('methodology', '综合分析')}")
        formatted_lines.append("")
        formatted_lines.append("---")
        formatted_lines.append("")
        
        # 处理正文内容
        for line in lines:
            if line.strip():
                # 增强章节标题格式
                if any(keyword in line for keyword in ["摘要", "概述", "分析", "结论", "建议"]):
                    if not line.startswith('#') and len(line) < 50:
                        formatted_lines.append(f"## {line.strip()}")
                    else:
                        formatted_lines.append(line.strip())
                else:
                    formatted_lines.append(line.strip())
            else:
                formatted_lines.append("")
        
        # 确保段落分明
        content = '\n'.join(formatted_lines)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()

    def _estimate_pages(self, content: str) -> int:
        """估算报告页数"""
        # 去除markdown标记
        clean_content = re.sub(r'[#*`\-=]', '', content)
        word_count = len(clean_content.replace(' ', '').replace('\n', ''))
        
        # 按照每页500字估算
        pages = max(1, round(word_count / 500))
        return pages

    def get_capabilities(self) -> List[str]:
        return [
            "市场调研报告撰写",
            "行业分析报告",
            "可行性研究报告",
            "竞争分析报告",
            "技术调研报告",
            "投资研究报告",
            "商业计划书",
            "尽职调查报告",
            "战略咨询报告",
            "专题研究报告"
        ]