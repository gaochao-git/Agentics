# 企业级办公智能体项目

基于LangGraph框架的企业级办公智能体系统，支持多种专业智能体协作的前后端分离架构。

## 项目架构

```
Agentics/
├── backend/                    # Django后端
│   ├── agents/                # 智能体模块
│   │   ├── core/             # 核心框架
│   │   ├── general_qa/       # 通用问答助手
│   │   ├── speech_writer/    # 发言稿智能体
│   │   ├── news_writer/      # 新闻稿智能体
│   │   ├── official_document/# 智能公文智能体
│   │   ├── research_report/  # 智能研报智能体
│   │   ├── code_assistant/   # 智能代码智能体
│   │   └── data_analysis/    # 数据分析智能体
│   ├── settings.py           # Django配置
│   ├── urls.py              # 路由配置
│   ├── requirements.txt     # Python依赖
│   └── manage.py           # Django管理脚本
├── frontend/                  # React前端
│   ├── src/
│   │   ├── agents/          # 前端智能体模块
│   │   ├── components/      # React组件
│   │   ├── pages/          # 页面组件
│   │   ├── store/          # 状态管理
│   │   ├── types/          # TypeScript类型
│   │   └── App.tsx         # 主应用组件
│   ├── package.json        # 前端依赖
│   └── public/            # 静态资源
├── docs/                    # 项目文档
├── tests/                   # 测试文件
├── setup_backend.sh         # 后端安装脚本
└── setup_frontend.sh        # 前端安装脚本
```

## 智能体功能

### 1. 通用问答助手 (General QA)
- 基础知识问答
- 智能路由到专业智能体
- 对话上下文管理

### 2. 发言稿智能体 (Speech Writer)
- 会议致辞撰写
- 庆典讲话创作
- 工作汇报撰写

### 3. 新闻稿智能体 (News Writer)
- 企业新闻稿
- 产品发布新闻
- 活动报道

### 4. 智能公文智能体 (Official Document)
- 通知公告撰写
- 请示报告
- 公文格式规范

### 5. 智能研报智能体 (Research Report)
- 市场调研报告
- 行业分析报告
- 可行性研究

### 6. 智能代码智能体 (Code Assistant)
- 代码生成和优化
- Bug修复建议
- 技术方案设计

### 7. 数据分析智能体 (Data Analysis)
- 数据清洗和处理
- 统计分析建模
- 数据可视化方案

## 技术栈

### 后端
- **Django 4.2**: Web框架
- **Django REST Framework**: API框架
- **LangGraph**: 智能体编排框架
- **LangChain**: LLM集成
- **PostgreSQL**: 数据库
- **Redis**: 缓存和任务队列
- **Celery**: 异步任务处理

### 前端
- **React 18**: 前端框架
- **TypeScript**: 类型安全
- **Ant Design**: UI组件库
- **Zustand**: 状态管理
- **Axios**: HTTP客户端

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### 1. 后端设置

```bash
# 运行后端安装脚本
./setup_backend.sh

# 或手动设置
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件，配置数据库和API密钥
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 2. 前端设置

```bash
# 运行前端安装脚本
./setup_frontend.sh

# 或手动设置
cd frontend
npm install
cp .env.example .env
# 编辑 .env 文件，配置API地址
npm start
```

## 配置说明

### 后端环境变量 (.env)
```
SECRET_KEY=django-secret-key
DEBUG=True
DB_NAME=agentics_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-api-key
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your-langchain-api-key
```

### 前端环境变量 (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
```

## API接口

### 智能体聊天
```
POST /api/agents/chat/
{
  "message": "用户消息",
  "agent_type": "general_qa",
  "conversation_id": 1
}
```

### 获取智能体列表
```
GET /api/agents/list/
```

### 获取对话历史
```
GET /api/agents/conversations/
```

## 扩展智能体

要添加新的智能体，请：

1. 在 `backend/agents/` 下创建新目录
2. 继承 `BaseAgent` 类实现新智能体
3. 在 `AgentType` 枚举中添加新类型
4. 更新初始化脚本注册新智能体
5. 在前端添加对应的UI和路由

## 部署

### 生产环境部署
- 使用 `DEBUG=False`
- 配置正式的数据库
- 使用 `gunicorn` 部署Django
- 使用 `nginx` 作为反向代理
- 前端构建后部署到CDN

## 安全注意事项

- 定期更新依赖包
- 使用环境变量存储敏感信息
- 实施用户认证和授权
- 输入验证和SQL注入防护
- HTTPS部署

## 监控和日志

项目支持：
- 应用日志记录
- 性能监控
- 错误追踪
- 用户行为分析