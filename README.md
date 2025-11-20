# KM Agent - 知识管理智能助手

基于 LLM 的智能知识管理系统，支持 PDF 文档上传、向量化存储、语义搜索和智能问答。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)

## 功能特性

### 核心功能
- 📄 **PDF 文档管理** - 上传、存储、删除 PDF 文档
- 🔍 **语义搜索** - 基于向量数据库的智能语义检索
- 💬 **智能问答** - LLM 驱动的知识库问答，支持多轮对话
- 📊 **实时进度** - SSE 流式上传进度展示
- 🔒 **权限控制** - 公开/私有文档管理
- 📖 **PDF 预览** - 内置 PDF 查看器，支持页码跳转

### 技术亮点
- **双路向量化** - 同时对摘要和全文内容进行向量化，提升检索精度
- **流式响应** - SSE 技术实现实时进度更新和流式对话
- **React + Zustand** - 现代化前端架构，状态管理清晰
- **模块化设计** - 清晰的模块划分，易于扩展和维护

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- Qdrant 向量数据库
- Embedding 服务（支持 OpenAI 兼容接口）
- LLM 服务（支持 OpenAI 兼容接口）

### 安装依赖

#### 1. Python 依赖
```bash
pip install -r requirements.txt
```

#### 2. 前端依赖
```bash
cd ui
npm install
```

### 配置

修改 `app_api/config.py` 配置文件：

```python
# LLM 配置
OPENAI_CONFIG = {
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1/",
    "model": "gpt-4"
}

# Embedding 服务配置
EMBEDDING_CONFIG = {
    "url": "http://your-embedding-service/v1/embeddings",
    "api_key": "your-embedding-key"
}

# Qdrant 向量数据库配置
QDRANT_CONFIG = {
    "url": "http://localhost:6333/",
    "api_key": "your-qdrant-key"
}

# PDF 存储目录
PDF_STORAGE_DIR = "/path/to/pdf/storage"
```

### 启动服务

#### 方式一：一键启动（推荐）
```bash
./start.sh
```

启动后访问：
- 前端 UI: http://localhost:8080
- 后端 API: http://localhost:5000

停止服务：
```bash
./stop.sh
```

#### 方式二：手动启动

**启动后端：**
```bash
python -m app_api.api
```

**启动前端：**
```bash
cd ui
npm run dev
```

## 项目结构

```
km-agent/
├── app_api/              # 后端 HTTP API 服务
│   ├── api.py           # Flask API 入口
│   ├── config.py        # 配置文件
│   └── README.md        # API 文档
├── km_agent/            # KM Agent 核心模块
│   ├── agent.py         # 智能对话 Agent
│   └── README.md        # 模块文档
├── pdf_vectorizer/      # PDF 向量化模块
│   ├── vectorizer.py    # 向量化核心逻辑
│   └── README.md        # 模块文档
├── pdf_to_json/         # PDF 解析模块
│   ├── converter.py     # PDF 转 JSON
│   └── README.md        # 模块文档
├── ui/                  # 前端 React 应用
│   ├── src/
│   │   ├── components/  # React 组件
│   │   ├── services/    # API 调用
│   │   └── store/       # Zustand 状态管理
│   └── package.json
├── requirements.txt     # Python 依赖
├── start.sh            # 一键启动脚本
├── stop.sh             # 停止脚本
└── README.md           # 项目文档
```

## 模块说明

### 1. app_api - HTTP API 服务
基于 Flask 的 RESTful API 服务，提供：
- 聊天接口（支持流式响应）
- 文档上传（SSE 实时进度）
- 文档列表查询
- 文档删除
- 权限管理

详见：[app_api/README.md](app_api/README.md)

### 2. km_agent - 智能对话 Agent
LLM 驱动的知识管理 Agent，功能：
- 语义搜索知识库
- 自动获取完整知识切片
- 基于知识库生成准确回答
- 支持多轮对话
- 引用来源标注

详见：[km_agent/README.md](km_agent/README.md)

### 3. pdf_vectorizer - PDF 向量化
将 PDF 文档向量化并存储到 Qdrant，支持：
- 双路向量化（摘要 + 全文）
- 三种召回模式（双路/摘要/全文）
- 实时进度跟踪
- 权限控制（公开/私有）
- 自动去重

详见：[pdf_vectorizer/README.md](pdf_vectorizer/README.md)

### 4. pdf_to_json - PDF 解析
使用 PyMuPDF 将 PDF 按页解析为结构化 JSON。

详见：[pdf_to_json/README.md](pdf_to_json/README.md)

### 5. ui - 前端应用
基于 React + Vite + Tailwind CSS 的现代化 Web 应用：
- 聊天界面（流式响应）
- 文档管理（上传、删除、权限控制）
- PDF 查看器（支持页码跳转）
- 实时上传进度

技术栈：
- React 18
- Zustand (状态管理)
- Tailwind CSS (样式)
- React-PDF (PDF 查看)
- ReactMarkdown (Markdown 渲染)

## API 文档

### 聊天接口
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "居住证如何办理？",
  "owner": "hu",
  "history": []
}
```

### 上传文档
```bash
POST /api/upload
Content-Type: multipart/form-data

file: document.pdf
owner: hu
is_public: 0
```

### 文档列表
```bash
GET /api/documents?owner=hu
```

完整 API 文档：[app_api/README.md](app_api/README.md)

## 使用示例

### 1. 上传 PDF 文档
- 点击「知识文档」按钮打开侧边栏
- 点击上传区域选择 PDF 文件
- 实时查看上传和向量化进度

### 2. 智能问答
- 在聊天框输入问题
- Agent 自动搜索知识库
- 基于检索结果生成回答
- 点击引用链接查看原文

### 3. PDF 查看
- 点击引用链接自动打开 PDF
- 支持页码跳转
- 上下翻页导航

## 开发指南

### 后端开发
```bash
# 运行测试
python test_km_agent.py

# 调试模式
python -m app_api.api
```

### 前端开发
```bash
cd ui
npm run dev     # 开发模式
npm run build   # 生产构建
npm run preview # 预览构建
```

## 配置说明

### 向量数据库
项目使用 Qdrant 作为向量数据库，需要：
1. 启动 Qdrant 服务
2. 配置连接信息到 `config.py`

### Embedding 服务
需要支持 OpenAI 兼容的 Embedding API：
- 输入：文本列表
- 输出：向量列表（4096 维）

### LLM 服务
需要支持 OpenAI 兼容的 Chat API：
- 支持 Function Calling
- 支持流式响应

## 部署建议

### 生产环境配置
1. 修改 `app_api/config.py`:
   - 设置 `DEBUG = False`
   - 配置生产环境的服务地址
2. 使用 Gunicorn 部署后端
3. 使用 Nginx 部署前端静态资源
4. 配置 HTTPS
5. 添加认证和授权

### Docker 部署
```bash
# TODO: 提供 Dockerfile 和 docker-compose.yml
```

## 常见问题

### Q: 上传 PDF 失败？
A: 检查：
1. PDF 存储目录权限
2. Qdrant 服务是否正常
3. Embedding 服务是否可用

### Q: 搜索结果不准确？
A: 尝试：
1. 调整搜索模式（dual/summary/content）
2. 增加检索数量
3. 优化 PDF 内容质量

### Q: 对话响应慢？
A: 检查：
1. LLM 服务响应时间
2. Qdrant 查询性能
3. 网络延迟

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues]

## 更新日志

### v1.0.0 (2025-01-20)
- ✨ 初始版本发布
- ✅ 支持 PDF 上传和向量化
- ✅ 智能问答和多轮对话
- ✅ 文档权限管理
- ✅ PDF 在线预览
- ✅ 流式响应和实时进度
