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

## 项目架构

```
km-agent/
├── app_api/              # Flask API 服务
├── km_agent/             # 知识管理 Agent
├── pdf_vectorizer/       # PDF 向量化模块
├── pdf_to_json/          # PDF 解析模块
├── file_repository/      # 文件存储模块
├── ks_infrastructure/    # 基础设施服务
├── ui/                   # React 前端界面
├── start.sh              # 一键启动脚本
└── stop.sh               # 停止服务脚本
```

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- Qdrant 向量数据库
- Embedding 服务（支持 OpenAI 兼容接口）
- LLM 服务（支持 OpenAI 兼容接口）
- Python 虚拟环境（用于依赖隔离）

### 安装依赖

#### 1. Python 依赖
```bash
# 创建虚拟环境（推荐）
python3 -m venv $HOME/projects/venv

# 激活虚拟环境
source $HOME/projects/venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 前端依赖
```bash
cd ui
npm install
```

### 配置

修改 `ks_infrastructure/configs/default.py` 配置文件：

```python
# MySQL数据库配置
MYSQL_CONFIG = {
    "host": "120.92.109.164",
    "port": 8306,
    "user": "admin",
    "password": "rsdyxjh",
    "database": "yanzhi"
}

# MinIO对象存储配置
MINIO_CONFIG = {
    "endpoint": "http://120.92.109.164:9000",  # S3 API服务端口
    "access_key": "admin",
    "secret_key": "rsdyxjh110!",
    "region": "us-east-1"
}

# Qdrant向量数据库配置
QDRANT_CONFIG = {
    "url": "http://120.92.109.164:6333",
    "api_key": "rsdyxjh"
}

# OpenAI大语言模型配置
OPENAI_CONFIG = {
    "api_key": "85c923cc-9dcf-467a-89d5-285d3798014d",
    "base_url": "https://kspmas.ksyun.com/v1/",
    "model": "DeepSeek-V3.1-Ksyun"
}

# Embedding服务配置
EMBEDDING_CONFIG = {
    "url": "http://10.69.86.20/v1/embeddings",
    "api_key": "7c64b222-4988-4e6a-bb26-48594ceda8a9"
}

# Vision视觉识别服务配置
VISION_CONFIG = {
    "api_key": "sk-412a5b410f664d60a29327fdfa28ac6e",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-vl-max"
}
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

注意：start.sh 脚本需要 Python 虚拟环境，可以通过 VENV_PATH 环境变量指定虚拟环境路径：
```bash
VENV_PATH=/path/to/your/venv ./start.sh
```

默认虚拟环境路径为 `$HOME/projects/venv`。

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

## API 接口

### 1. 聊天接口
```
POST /api/chat
```
与 KM Agent 对话，支持多轮连续对话

### 2. 获取文档列表
```
GET /api/documents
```
获取用户有权访问的文档列表

### 3. 上传并向量化 PDF
```
POST /api/upload
```
上传 PDF 文件并向量化，支持 SSE 实时进度

### 4. 删除文档
```
DELETE /api/documents/<filename>
```
删除指定文档

### 5. 修改文档可见性
```
PUT /api/documents/<filename>/visibility
```
修改文档为公开/私有

### 6. 获取 PDF 文件内容
```
GET /api/documents/<filename>/content
```
获取 PDF 文件内容用于查看

## 模块介绍

### 1. app_api - API 服务层
基于 Flask 的 HTTP API 服务，提供知识管理功能的 RESTful 接口。

### 2. km_agent - 知识管理 Agent
核心智能代理，负责语义搜索、知识问答和工具调用。

### 3. pdf_vectorizer - PDF 向量化
将 PDF 文档向量化并存储到 Qdrant 向量数据库，支持实时进度跟踪。

### 4. pdf_to_json - PDF 解析
将 PDF 文件转换为结构化的 JSON 格式，保留文本和图片的相对位置。

### 5. file_repository - 文件存储
基于 MinIO 提供文件上传和查询的存储仓库服务，使用 MySQL 管理文件元数据。

### 6. ks_infrastructure - 基础设施
统一的服务工厂方法，用于创建和管理各种基础设施服务实例。

## 许可证

MIT License
