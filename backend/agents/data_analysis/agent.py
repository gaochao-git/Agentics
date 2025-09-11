from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from agents.core.llm_manager import get_llm
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict
import time
import re


class DataAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.DATA_ANALYSIS,
            name="数据分析智能体",
            description="专业的数据分析助手，支持数据处理、分析和可视化"
        )
        # 使用统一的LLM管理器
        self.llm = get_llm()
        
        # 分析类型模板
        self.analysis_types = {
            "描述性分析": ["描述", "统计", "汇总", "概览"],
            "预测分析": ["预测", "预报", "趋势", "未来"],
            "诊断分析": ["原因", "为什么", "影响因素", "相关性"],
            "处方分析": ["建议", "优化", "改进", "策略"]
        }
        
        # 数据类型识别
        self.data_types = {
            "销售数据": ["销售", "收入", "营收", "业绩"],
            "用户数据": ["用户", "客户", "访问", "行为"],
            "财务数据": ["财务", "成本", "利润", "预算"],
            "运营数据": ["运营", "效率", "流程", "KPI"],
            "市场数据": ["市场", "竞争", "份额", "调研"]
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
            # 分析用户需求
            analysis_info = self._analyze_data_request(message.content)
            
            # 构建专业的系统提示
            system_prompt = self._build_system_prompt(analysis_info)

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message.content)
            ]

            response = await self.llm.ainvoke(messages)
            
            # 后处理：格式化数据分析输出
            formatted_content = self._format_analysis_output(response.content, analysis_info)
            
            return AgentResponse(
                success=True,
                content=formatted_content,
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                metadata={
                    "analysis_type": analysis_info.get("type", "通用数据分析"),
                    "data_type": analysis_info.get("data_type", "未指定"),
                    "complexity": analysis_info.get("complexity", "中等"),
                    "tools_suggested": analysis_info.get("tools", [])
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=f"处理数据分析请求时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def _analyze_data_request(self, content: str) -> Dict:
        """分析数据分析请求"""
        content_lower = content.lower()
        
        # 识别分析类型
        analysis_type = "通用数据分析"
        for type_name, keywords in self.analysis_types.items():
            if any(keyword in content_lower for keyword in keywords):
                analysis_type = type_name
                break
        
        # 识别数据类型
        data_type = "未指定"
        for dtype, keywords in self.data_types.items():
            if any(keyword in content_lower for keyword in keywords):
                data_type = dtype
                break
        
        # 评估复杂度
        complexity = "中等"
        if any(word in content_lower for word in ["简单", "基础", "快速"]):
            complexity = "简单"
        elif any(word in content_lower for word in ["深入", "详细", "高级", "复杂"]):
            complexity = "复杂"
        
        # 推荐工具
        tools = ["Python", "Pandas"]
        if any(word in content_lower for word in ["可视化", "图表", "展示"]):
            tools.extend(["Matplotlib", "Seaborn", "Plotly"])
        if any(word in content_lower for word in ["机器学习", "预测", "模型"]):
            tools.extend(["Scikit-learn", "XGBoost"])
        if any(word in content_lower for word in ["统计", "检验", "相关性"]):
            tools.extend(["Scipy", "Statsmodels"])
        
        return {
            "type": analysis_type,
            "data_type": data_type,
            "complexity": complexity,
            "tools": list(set(tools))
        }
    
    def _build_system_prompt(self, analysis_info: Dict) -> str:
        """构建系统提示"""
        base_prompt = """你是一个专业的数据科学家和业务分析专家。你具备以下能力：

核心技能：
1. 数据收集、清洗和预处理
2. 统计分析和假设检验
3. 机器学习和预测建模
4. 数据可视化和报告撰写
5. 业务洞察和决策支持

分析方法：
- 描述性统计：均值、中位数、标准差、分布分析
- 推断统计：假设检验、置信区间、方差分析
- 相关分析：相关系数、回归分析、因果推断
- 时间序列：趋势分析、季节性分解、预测模型
- 分类聚类：用户细分、异常检测、模式识别

输出要求：
- 提供清晰的分析思路和步骤
- 包含可执行的Python代码示例
- 解释分析结果的业务含义
- 给出可行的业务建议

"""
        
        # 根据分析信息定制提示
        if analysis_info.get("type") != "通用数据分析":
            base_prompt += f"\n分析类型：{analysis_info['type']}\n"
        
        if analysis_info.get("data_type") != "未指定":
            base_prompt += f"数据类型：{analysis_info['data_type']}\n"
        
        if analysis_info.get("tools"):
            base_prompt += f"推荐工具：{', '.join(analysis_info['tools'])}\n"
        
        base_prompt += "\n请根据用户需求提供专业的数据分析解决方案。"
        
        return base_prompt
    
    def _format_analysis_output(self, content: str, analysis_info: Dict) -> str:
        """格式化数据分析输出"""
        # 确保有清晰的标题
        if not content.startswith('#'):
            analysis_type = analysis_info.get('type', '数据分析')
            content = f"# {analysis_type}报告\n\n" + content
        
        # 确保代码块有Python标识
        content = re.sub(r'```\n', '```python\n', content)
        
        return content.strip()

    def get_capabilities(self) -> List[str]:
        return [
            "数据清洗与预处理",
            "描述性统计分析",
            "预测建模与预报",
            "数据可视化设计",
            "业务洞察分析",
            "A/B测试设计",
            "用户行为分析",
            "销售数据分析",
            "财务数据分析",
            "市场调研分析"
        ]