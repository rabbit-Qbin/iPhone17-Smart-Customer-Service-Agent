# iPhone 17 智能客服 Agent

基于 LangGraph 构建的电商智能客服系统，支持 iPhone 17 系列产品的咨询问答。

## 项目架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面层                               │
│                    Gradio Web Chat (7861)                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API 服务层                               │
│                    FastAPI + Uvicorn (8012)                     │
│                  /v1/chat/completions (流式/非流式)              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangGraph Agent 层                         │
│  ┌─────────┐    ┌──────────┐    ┌────────┐    ┌──────────┐     │
│  │  Agent  │───▶│call_tools│───▶│ grade  │───▶│ generate │     │
│  │ (分诊)  │    │ (检索)   │    │(判断)  │    │ (生成)   │     │
│  └─────────┘    └──────────┘    └────────┘    └──────────┘     │
│       │                              │                          │
│       │                              ▼                          │
│       │                        ┌──────────┐                     │
│       │                        │ rewrite  │                     │
│       │                        │(重写查询)│                     │
│       │                        └──────────┘                     │
│       │                              │                          │
│       └──────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌───────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│    ChromaDB       │ │   PostgreSQL    │ │    LLM Provider     │
│   (向量知识库)     │ │   + pgvector    │ │  DeepSeek/OpenAI    │
│ iPhone17产品资料   │ │  (对话持久化)    │ │     /Ollama        │
└───────────────────┘ └─────────────────┘ └─────────────────────┘
```

## 项目结构

```
iPhone17系列产品_RagAgent/
├── main.py                 # FastAPI 服务入口
├── demoRagAgent.py         # LangGraph Agent 核心逻辑
├── webUI.py                # Gradio 前端界面
├── vectorSave_iphone17.py  # 知识库向量化灌库脚本
├── start.py                # 一键启动脚本 (API + Web)
├── docker-compose.yml      # PostgreSQL 容器配置
├── graph.png               # Agent 工作流可视化
│
├── knowledge_base/         # iPhone 17 产品知识库
│   ├── 产品/               # 产品参数、价格、配置
│   └── 销售/               # 售后、配送、选购指南
│
├── prompts/                # 提示词模板
│   ├── prompt_template_agent.txt     # Agent 分诊提示词
│   ├── prompt_template_grade.txt     # 相关性判断提示词
│   ├── prompt_template_rewrite.txt   # 查询重写提示词
│   └── prompt_template_generate.txt  # 回复生成提示词
│
├── utils/
│   ├── config.py           # 统一配置管理
│   ├── llms.py             # LLM 模型初始化
│   └── tools_config.py     # 检索工具配置
│
├── chromaDB/               # ChromaDB 向量数据库存储
└── output/                 # 日志输出目录
```

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **Agent 框架** | LangGraph | 有状态多步骤工作流编排 |
| **LLM 应用** | LangChain | 提示模板、工具、检索器 |
| **大模型** | DeepSeek / OpenAI / Ollama | 可切换的 LLM 后端 |
| **向量数据库** | ChromaDB | 存储 iPhone 17 产品知识库 |
| **Embedding** | nomic-embed-text (Ollama) | 本地向量嵌入模型 |
| **持久化** | PostgreSQL + pgvector | 对话历史 & 跨会话记忆 |
| **后端框架** | FastAPI + Uvicorn | 高性能异步 API 服务 |
| **前端界面** | Gradio | 快速搭建 Chat Web UI |
| **容器化** | Docker Compose | PostgreSQL 一键部署 |

## Agent 工作流 (Self-RAG)

```
用户提问
    │
    ▼
┌─────────┐
│  Agent  │ ──── 判断是否需要检索
└─────────┘
    │ 需要检索
    ▼
┌──────────┐
│call_tools│ ──── 调用 retrieve_iphone17 工具
└──────────┘
    │
    ▼
┌──────────────┐
│grade_documents│ ──── 判断检索结果是否相关 (yes/no)
└──────────────┘
    │
    ├─── yes (相关) ───▶ generate ───▶ 生成回复
    │
    └─── no (不相关) ──▶ rewrite ───▶ 重写查询 ───▶ 返回 Agent
                         (最多重写3次)
```

## 快速开始

### 1. 启动 PostgreSQL
```bash
docker-compose up -d
```

### 2. 启动 Ollama (本地 Embedding)
```bash
ollama serve
ollama pull nomic-embed-text
```

### 3. 灌入知识库
```bash
python vectorSave_iphone17.py
```

### 4. 启动服务
```bash
python start.py
```

访问：
- API 服务：http://localhost:8012
- Web 界面：http://127.0.0.1:7861

## 配置说明

编辑 `utils/config.py` 切换 LLM：

```python
# 可选: "deepseek", "openai", "ollama"
LLM_TYPE = "deepseek"
```

## 开发方式

本项目借助 **Vibe Coding (AI 辅助编程)** 快速完成开发迭代。
