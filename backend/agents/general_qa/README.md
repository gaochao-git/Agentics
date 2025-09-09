# 通用问答助手 (General QA Agent)

## 概述

通用问答助手是基于LangGraph框架开发的智能对话系统，能够处理各种通用知识问答，并具备智能路由功能，可以根据用户需求将对话路由到相应的专业智能体。

## 功能特性

### 核心功能
- **通用知识问答**: 回答各种通用知识问题
- **智能意图识别**: 使用AI自动识别用户意图
- **专业智能体路由**: 根据需求自动路由到对应的专业智能体
- **上下文管理**: 支持多轮对话和上下文记忆
- **对话历史**: 保存和管理对话记录

### LangGraph特性
- **状态管理**: 使用TypedDict管理对话状态
- **节点化流程**: 将对话流程分解为独立的处理节点
- **条件路由**: 基于用户意图进行智能路由决策
- **可扩展性**: 易于添加新的处理节点和路由规则

## 架构设计

### 对话状态 (ConversationState)
```python
class ConversationState(TypedDict):
    messages: List[Dict[str, Any]]        # 对话消息列表
    current_agent: str                    # 当前处理的智能体
    context: Dict[str, Any]               # 对话上下文
    needs_specialist: bool               # 是否需要专业智能体
    specialist_type: str                  # 专业智能体类型
    user_intent: str                      # 用户意图分类
```

### 处理节点

1. **classify_intent**: 用户意图分类节点
   - 使用LLM分析用户消息
   - 将意图映射到对应的智能体类型

2. **general_response**: 通用回答节点
   - 处理通用问答场景
   - 结合对话历史生成响应

3. **route_to_specialist**: 专业路由节点
   - 将请求路由到对应的专业智能体
   - 提供路由确认信息

4. **update_context**: 上下文更新节点
   - 更新对话上下文信息
   - 维护对话状态

## API接口

### 对话接口
- **POST** `/api/agents/general-qa/chat/`
  - 处理用户消息
  - 参数: `message`, `conversation_id` (可选)
  - 返回: 智能体响应和元数据

### 对话管理
- **GET** `/api/agents/general-qa/conversations/`
  - 获取对话列表
  - 返回: 对话列表和基本信息

- **GET** `/api/agents/general-qa/conversations/{id}/`
  - 获取特定对话详情
  - 返回: 对话消息和元数据

## 使用示例

### 后端使用

```python
from agents.general_qa.agent import GeneralQAAgent
from agents.core.base import AgentMessage, AgentType

# 创建智能体实例
agent = GeneralQAAgent()

# 创建消息
message = AgentMessage(
    id="test-123",
    content="请帮我写一篇关于人工智能的发言稿",
    agent_type=AgentType.GENERAL_QA,
    timestamp=None
)

# 处理消息
response = await agent.process(message)
print(response.content)  # 将路由到发言稿智能体
```

### 前端集成

```typescript
import { GeneralQAChat } from '@/agents/general_qa';

// 在React组件中使用
function App() {
  return (
    <div>
      <GeneralQAChat />
    </div>
  );
}
```

## 智能体路由规则

| 关键词 | 路由到的智能体 |
|--------|----------------|
| 发言稿 | speech_writer |
| 新闻稿 | news_writer |
| 公文   | official_document |
| 研报   | research_report |
| 代码   | code_assistant |
| 数据分析 | data_analysis |

## 扩展开发

### 添加新的处理节点

1. 在 `_build_graph()` 方法中添加新节点
2. 实现对应的处理函数
3. 更新路由逻辑

### 自定义意图分类

修改 `_classify_intent` 方法中的提示词和映射规则：

```python
intent_mapping = {
    "new_intent": AgentType.NEW_AGENT_TYPE,
    # 添加新的意图映射
}
```

## 测试

运行测试用例：

```bash
python manage.py test tests.test_general_qa
```

## 部署配置

### 环境变量
- `OPENAI_API_KEY`: OpenAI API密钥
- `DATABASE_URL`: 数据库连接字符串

### Django设置
确保在 `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ...
    'agents.general_qa',
]
```

## 性能优化

1. **缓存**: 对频繁查询的结果使用Redis缓存
2. **异步处理**: 使用Celery处理耗时任务
3. **数据库优化**: 为消息表添加适当的索引
4. **连接池**: 配置数据库连接池

## 监控和日志

- 记录每次对话的处理时间
- 监控意图分类的准确率
- 跟踪路由决策的合理性
- 记录错误和异常情况