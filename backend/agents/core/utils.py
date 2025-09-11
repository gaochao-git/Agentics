import re
import html


def markdown_to_plain_text(markdown_content: str) -> str:
    """
    将markdown内容转换为纯文本格式，适合复制粘贴
    """
    if not markdown_content:
        return ""
    
    text = markdown_content
    
    # 移除代码块，保留内容
    text = re.sub(r'```[\w]*\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    
    # 移除行内代码标记
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # 处理标题，转换为层级结构
    text = re.sub(r'^#{1}\s+(.+)$', r'【\1】', text, flags=re.MULTILINE)
    text = re.sub(r'^#{2}\s+(.+)$', r'\n一、\1', text, flags=re.MULTILINE)  
    text = re.sub(r'^#{3}\s+(.+)$', r'\n（一）\1', text, flags=re.MULTILINE)
    text = re.sub(r'^#{4}\s+(.+)$', r'\n1. \1', text, flags=re.MULTILINE)
    text = re.sub(r'^#{5,6}\s+(.+)$', r'\n• \1', text, flags=re.MULTILINE)
    
    # 处理粗体和斜体
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # 处理链接，保留链接文本
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # 处理图片，保留alt文本
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'[图片：\1]', text)
    
    # 处理列表，保持结构
    text = re.sub(r'^[-*+]\s+(.+)$', r'• \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+(.+)$', r'\1', text, flags=re.MULTILINE)
    
    # 处理引用
    text = re.sub(r'^>\s+(.+)$', r'"\1"', text, flags=re.MULTILINE)
    
    # 处理表格（简化处理）
    text = re.sub(r'\|([^|]+)\|', r'\1 ', text)
    text = re.sub(r'^[-\s|]+$', '', text, flags=re.MULTILINE)
    
    # 处理分割线
    text = re.sub(r'^---+$', r'─────────────────────', text, flags=re.MULTILINE)
    
    # 清理HTML实体
    text = html.unescape(text)
    
    # 清理多余的空行
    text = re.sub(r'\n{3,}', r'\n\n', text)
    
    # 清理行首行末空格
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    
    return text.strip()


def extract_title_from_content(content: str) -> str:
    """
    从内容中提取标题
    """
    # 尝试从markdown标题提取
    title_match = re.search(r'^#{1}\s+(.+)$', content, flags=re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    
    # 尝试从内容开头提取
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line and len(line) < 100:
            # 清理markdown语法
            clean_line = re.sub(r'[#*`_\[\]()]', '', line).strip()
            if clean_line:
                return clean_line
    
    return "未命名文档"


def detect_document_type(content: str, agent_type: str) -> str:
    """
    检测文档类型
    """
    content_lower = content.lower()
    
    # 根据智能体类型确定基础类型
    type_mapping = {
        'speech_writer': '发言稿',
        'news_writer': '新闻稿', 
        'code_assistant': '代码文档',
        'data_analysis': '数据分析报告',
        'official_document': '公文',
        'research_report': '研究报告',
        'general_qa': '问答内容'
    }
    
    base_type = type_mapping.get(agent_type, '文档')
    
    # 进一步细化类型
    if '发言稿' in base_type:
        if '动员' in content_lower:
            return '动员大会发言稿'
        elif '年会' in content_lower:
            return '年会发言稿'
        elif '党会' in content_lower:
            return '党会发言稿'
    elif '新闻稿' in base_type:
        if '产品' in content_lower:
            return '产品发布新闻稿'
        elif '合作' in content_lower:
            return '合作协议新闻稿'
    elif '公文' in base_type:
        if '通知' in content_lower:
            return '通知'
        elif '请示' in content_lower:
            return '请示'
        elif '报告' in content_lower:
            return '报告'
    
    return base_type