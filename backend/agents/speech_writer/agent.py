from agents.core.base import BaseAgent, AgentType, AgentMessage, AgentResponse
from agents.core.llm_manager import get_llm
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict
import time
import re


class SpeechWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.SPEECH_WRITER,
            name="发言稿智能体",
            description="专业的发言稿撰写助手，支持各类正式场合的发言稿创作"
        )
        # 使用统一的LLM管理器
        self.llm = get_llm()
        
        # 发言稿模板库
        self.templates = {
            "会议致辞": {
                "structure": ["开场致辞", "会议背景", "主要内容", "工作部署", "结束语"],
                "tone": "正式、权威"
            },
            "庆典讲话": {
                "structure": ["致辞开场", "回顾历程", "现状成就", "未来展望", "感谢致辞"],
                "tone": "热烈、感恩"
            },
            "年会发言": {
                "structure": ["新年问候", "年度回顾", "成果展示", "新年规划", "祝福致辞"],
                "tone": "温馨、激励"
            },
            "动员大会": {
                "structure": ["形势分析", "任务目标", "动员号召", "具体要求", "激励结尾"],
                "tone": "鼓舞、激昂"
            },
            "党会发言": {
                "structure": ["政治站位", "思想认识", "工作汇报", "问题反思", "表态决心"],
                "tone": "严肃、庄重"
            },
            "新年致辞": {
                "structure": ["新年祝福", "年度总结", "成就回顾", "新年展望", "美好祝愿"],
                "tone": "温暖、希望"
            },
            "学术演讲": {
                "structure": ["引言", "研究背景", "主要发现", "实践意义", "总结"],
                "tone": "严谨、专业"
            },
            "培训讲话": {
                "structure": ["开场白", "培训目标", "核心内容", "实践指导", "总结勉励"],
                "tone": "亲和、指导"
            },
            "就职演说": {
                "structure": ["感谢致辞", "使命担当", "工作理念", "目标规划", "决心表态"],
                "tone": "庄严、承诺"
            },
            "表彰大会": {
                "structure": ["开场致辞", "成绩回顾", "先进表彰", "经验总结", "再接再厉"],
                "tone": "赞扬、激励"
            },
            "开业致辞": {
                "structure": ["开业祝贺", "发展历程", "业务介绍", "感谢支持", "未来展望"],
                "tone": "喜庆、感恩"
            },
            "毕业典礼": {
                "structure": ["祝贺开场", "求学回顾", "成长感悟", "未来寄语", "祝福结语"],
                "tone": "温馨、祝福"
            },
            "追悼致辞": {
                "structure": ["沉痛开场", "生平回顾", "品格赞颂", "精神传承", "告别致敬"],
                "tone": "沉重、敬意"
            },
            "竞聘演讲": {
                "structure": ["自我介绍", "岗位认知", "能力优势", "工作设想", "决心表态"],
                "tone": "自信、专业"
            },
            "感谢致辞": {
                "structure": ["感谢开场", "获奖感言", "支持回顾", "经验分享", "继续努力"],
                "tone": "谦逊、感激"
            },
            "欢迎致辞": {
                "structure": ["热烈欢迎", "嘉宾介绍", "活动意义", "期待交流", "祝愿成功"],
                "tone": "热情、友好"
            },
            "项目启动": {
                "structure": ["项目背景", "重要意义", "目标任务", "推进计划", "动员结尾"],
                "tone": "振奋、决心"
            },
            "安全教育": {
                "structure": ["安全重要性", "事故案例", "规章制度", "预防措施", "安全承诺"],
                "tone": "严肃、警示"
            },
            "团建活动": {
                "structure": ["活动目的", "团队精神", "协作重要性", "活动安排", "期待成果"],
                "tone": "轻松、团结"
            },
            "产品发布": {
                "structure": ["产品介绍", "创新亮点", "市场价值", "使用体验", "发展前景"],
                "tone": "专业、兴奋"
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
            # 分析用户需求
            speech_info = self._analyze_speech_requirements(message.content)
            
            # 构建专业的系统提示
            system_prompt = self._build_system_prompt(speech_info)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message.content)
            ]

            response = await self.llm.ainvoke(messages)
            
            # 后处理：格式化输出
            formatted_content = self._format_speech_output(response.content)
            
            return AgentResponse(
                success=True,
                content=formatted_content,
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                metadata={
                    "speech_type": speech_info.get("type", "通用发言稿"),
                    "estimated_duration": self._estimate_speech_duration(formatted_content),
                    "structure": speech_info.get("structure", [])
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=f"生成发言稿时发生错误: {str(e)}",
                agent_type=self.agent_type,
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def _analyze_speech_requirements(self, content: str) -> Dict:
        """分析发言稿需求"""
        content_lower = content.lower()
        
        # 识别发言稿类型
        speech_type = "通用发言稿"
        structure = []
        
        for template_name, template_info in self.templates.items():
            if any(keyword in content_lower for keyword in template_name.split()):
                speech_type = template_name
                structure = template_info["structure"]
                break
        
        # 识别关键要素
        occasion = self._extract_occasion(content)
        audience = self._extract_audience(content)
        duration = self._extract_duration(content)
        
        return {
            "type": speech_type,
            "structure": structure,
            "occasion": occasion,
            "audience": audience,
            "duration": duration
        }
    
    def _extract_occasion(self, content: str) -> str:
        """提取场合信息"""
        occasions = {
            "年会": ["年会", "年终", "年度会议", "年终总结", "年度大会"],
            "动员大会": ["动员大会", "动员会", "誓师大会", "启动大会", "冲刺大会"],
            "党会": ["党会", "党员大会", "党委会", "支部会", "党建会", "民主生活会"],
            "新年致辞": ["新年致辞", "新年讲话", "新年祝词", "春节致辞", "元旦致辞"],
            "开业": ["开业", "开幕", "启动", "成立", "揭牌", "开张"],
            "庆典": ["庆典", "庆祝", "纪念", "周年", "庆贺", "典礼"],
            "会议": ["会议", "大会", "座谈", "研讨", "论坛", "峰会"],
            "培训": ["培训", "讲座", "学习", "教学", "研修", "进修"],
            "毕业": ["毕业", "学位", "典礼", "仪式", "毕业典礼", "学位授予"],
            "就职": ["就职", "上任", "履新", "任职", "走马上任", "新官上任"],
            "表彰": ["表彰", "颁奖", "表彰大会", "先进表彰", "优秀表彰"],
            "追悼": ["追悼", "悼念", "告别", "缅怀", "追思", "哀悼"],
            "竞聘": ["竞聘", "竞选", "应聘", "面试", "选拔", "竞争上岗"],
            "感谢": ["感谢", "答谢", "致谢", "谢意", "感激", "感恩"],
            "欢迎": ["欢迎", "迎接", "接待", "欢迎词", "迎新"],
            "项目启动": ["项目启动", "开工", "奠基", "启动仪式", "项目开始"],
            "安全教育": ["安全教育", "安全培训", "安全会议", "安全讲话"],
            "团建活动": ["团建", "团队建设", "拓展", "联谊", "集体活动"],
            "产品发布": ["产品发布", "新品发布", "产品介绍", "产品推广"]
        }
        
        for occasion, keywords in occasions.items():
            if any(keyword in content for keyword in keywords):
                return occasion
        return "正式场合"
    
    def _extract_audience(self, content: str) -> str:
        """提取听众信息"""
        audiences = {
            "员工": ["员工", "同事", "团队", "大家"],
            "领导": ["领导", "各位领导", "上级"],
            "客户": ["客户", "合作伙伴", "朋友"],
            "学生": ["学生", "同学", "学员"],
            "嘉宾": ["嘉宾", "来宾", "朋友们"]
        }
        
        for audience, keywords in audiences.items():
            if any(keyword in content for keyword in keywords):
                return audience
        return "各位"
    
    def _extract_duration(self, content: str) -> int:
        """提取时长要求（分钟）"""
        import re
        duration_match = re.search(r'(\d+)\s*分钟', content)
        if duration_match:
            return int(duration_match.group(1))
        
        # 根据内容长度估算默认时长
        if "简短" in content or "简单" in content:
            return 3
        elif "详细" in content or "完整" in content:
            return 10
        else:
            return 5
    
    def _build_system_prompt(self, speech_info: Dict) -> str:
        """构建系统提示"""
        base_prompt = """你是一个专业的发言稿撰写专家。你需要根据用户需求创作高质量的发言稿。

核心要求：
1. 结构清晰：开头、主体、结尾层次分明
2. 语言得体：正式但不失亲和力
3. 逻辑严谨：论点明确，论证有力
4. 情感适宜：根据场合调整语调

写作规范：
- 开头：合适的称呼和问候语
- 主体：2-4个主要观点，每个观点有具体阐述
- 结尾：总结要点，适当展望或号召
- 语言：避免冗长句式，多使用短句
- 格式：段落清晰，便于朗读

"""
        
        # 根据分析结果定制提示
        if speech_info.get("type") != "通用发言稿":
            template_info = self.templates.get(speech_info["type"], {})
            base_prompt += f"\n当前发言稿类型：{speech_info['type']}\n"
            base_prompt += f"建议结构：{' -> '.join(template_info.get('structure', []))}\n"
            base_prompt += f"语言风格：{template_info.get('tone', '适中')}\n"
        
        if speech_info.get("occasion"):
            base_prompt += f"场合：{speech_info['occasion']}\n"
        
        if speech_info.get("audience"):
            base_prompt += f"听众：{speech_info['audience']}\n"
        
        if speech_info.get("duration"):
            base_prompt += f"预期时长：约{speech_info['duration']}分钟\n"
        
        base_prompt += "\n请根据以上要求，为用户创作一份专业的发言稿。"
        
        return base_prompt
    
    def _format_speech_output(self, content: str) -> str:
        """格式化发言稿输出"""
        # 确保标题突出
        if not content.startswith("#") and not content.startswith("**"):
            # 尝试识别第一行作为标题
            lines = content.split('\n')
            if lines and len(lines[0]) < 50:  # 假设标题不超过50字符
                lines[0] = f"# {lines[0].strip()}"
                content = '\n'.join(lines)
        
        # 添加发言稿标准格式标记
        if "各位" not in content[:100] and "尊敬的" not in content[:100]:
            # 如果开头没有称呼，添加标准开场
            content = "尊敬的各位领导、各位同事：\n\n" + content
        
        # 确保段落分明
        content = re.sub(r'\n{3,}', '\n\n', content)  # 最多两个换行
        
        return content.strip()
    
    def _estimate_speech_duration(self, content: str) -> int:
        """估算发言时长（分钟）"""
        # 去除markdown标记和格式符号
        clean_content = re.sub(r'[#*`\-=]', '', content)
        word_count = len(clean_content.replace(' ', '').replace('\n', ''))
        
        # 按照中文每分钟200-250字的语速估算
        duration = max(1, round(word_count / 225))
        return duration

    def get_capabilities(self) -> List[str]:
        return [
            "会议致辞撰写",
            "庆典讲话创作", 
            "年会发言稿",
            "动员大会讲话",
            "党会发言稿",
            "新年致辞撰写",
            "学术演讲稿",
            "培训讲话",
            "就职演说",
            "表彰大会发言",
            "开业致辞",
            "毕业典礼发言",
            "追悼致辞",
            "竞聘演讲",
            "感谢致辞",
            "欢迎致辞",
            "项目启动讲话",
            "安全教育发言",
            "团建活动致辞",
            "产品发布演讲",
            "工作汇报演讲"
        ]