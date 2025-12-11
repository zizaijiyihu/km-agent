# KM Agent 快速部署指南

## 🚀 一键部署（推荐）

如果你只想快速部署到生产环境，执行以下命令：

```bash
# 1. 克隆代码到服务器
git clone <your-repo-url> /tmp/km-agent-source
cd /tmp/km-agent-source

# 2. 执行部署脚本
sudo ./deploy.sh

# 3. 编辑配置文件（填写 API Keys 等）
sudo vim /var/www/km-agent/config/.env

# 4. 重启服务
sudo systemctl restart km-agent-api

# 完成！访问 http://your-server-ip
```

部署脚本会自动完成：
- ✅ 创建部署目录结构
- ✅ 安装所有 Python 依赖
- ✅ 构建前端
- ✅ 配置 Nginx
- ✅ 配置 systemd 服务
- ✅ 启动服务并健康检查

---

## 📦 UI 打包部署详解

### 方式 1: 使用构建脚本（推荐）

```bash
# 执行构建脚本
./scripts/build_frontend.sh

# 构建产物在 ui/dist/ 目录
ls ui/dist/
```

### 方式 2: 手动构建

```bash
cd ui

# 安装依赖（仅首次需要）
npm install

# 生产环境构建
npm run build

# 构建产物
ls dist/
# 输出:
# - index.html          (入口 HTML)
# - assets/             (JS、CSS、图片等)
# - images/            (公共图片资源)
```

### 部署到 Nginx

**方式 A: 让 Nginx 托管静态文件（推荐）**

```nginx
# /etc/nginx/sites-available/km-agent

server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/km-agent/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # API 反向代理到后端
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

部署步骤：
```bash
# 1. 复制构建产物到服务器
scp -r ui/dist/* user@server:/var/www/km-agent/frontend/dist/

# 2. 配置 Nginx（使用 deploy.sh 会自动配置）
sudo vim /etc/nginx/sites-available/km-agent

# 3. 启用站点
sudo ln -s /etc/nginx/sites-available/km-agent /etc/nginx/sites-enabled/

# 4. 测试并重启
sudo nginx -t
sudo systemctl restart nginx
```

**方式 B: 使用 Flask 托管（不推荐生产环境）**

如果你坚持要用 Flask 托管前端，可以这样做：

```python
# app_api/static_server.py
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='../ui/dist')

@app.route('/')
@app.route('/<path:path>')
def serve_static(path='index.html'):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# API 路由
from app_api.api import app as api_app
app.register_blueprint(api_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

但这种方式有明显缺点：
- ❌ 性能差：Flask 托管静态文件比 Nginx 慢 10-100 倍
- ❌ 功能少：缺少缓存、gzip、HTTP/2 等优化
- ❌ 不专业：生产环境不推荐
- ❌ 需要 root：监听 80 端口需要 root 权限

**结论：不需要写 app_ui 模块，用 Nginx！**

---

## 🔍 依赖获取详解

### Python 后端依赖

项目依赖分为两部分：

#### 1. 第三方依赖（已更新）

根目录 [requirements.txt](requirements.txt) 已包含所有第三方依赖：

```bash
# 查看依赖列表
cat requirements.txt

# 安装
pip install -r requirements.txt
```

包含的依赖：
- **AI/LLM**: openai
- **Web**: flask, flask-cors, werkzeug
- **数据库**: mysql-connector-python, qdrant-client, redis
- **对象存储**: boto3
- **数据处理**: pandas, PyMuPDF
- **HTTP**: requests, crawl4ai

#### 2. 本地模块依赖

项目有 14 个本地 Python 模块，需要按顺序安装：

**使用自动化脚本（推荐）：**

```bash
# 激活虚拟环境
source ~/projects/venv/bin/activate

# 执行安装脚本
./scripts/install_local_modules.sh
```

**手动安装：**

```bash
# 按依赖顺序安装
pip install -e ./ks_infrastructure          # Layer 1: 基础设施
pip install -e ./conversation_repository    # Layer 2: 存储层
pip install -e ./file_repository
pip install -e ./instruction_repository
pip install -e ./quote_repository
pip install -e ./reminder_repository
pip install -e ./pdf_to_json               # Layer 3: 文档处理
pip install -e ./aibase_news
pip install -e ./beisen_course
pip install -e ./tmp_image_repository
pip install -e ./document_vectorizer       # Layer 4: 向量化
pip install -e ./km_agent                  # Layer 5: 代理
pip install -e ./app_api                   # Layer 6: API
```

#### 依赖检查

使用依赖检查脚本验证所有依赖：

```bash
./scripts/check_dependencies.sh
```

输出示例：
```
1. 系统命令检查
✓ Python 3: Python 3.10.12
✓ pip: pip 23.0.1
✓ Node.js: v18.16.0
✓ npm: 9.5.1
✓ Git: git version 2.34.1

2. Python 虚拟环境
✓ 虚拟环境已激活: /home/user/venv

3. Python 第三方包
✓ flask: 3.0.0
✓ openai: 1.12.0
✓ qdrant_client: 1.7.0
...

检查结果
  总计检查: 25
  通过: 25
  失败: 0
✓ 所有依赖检查通过！
```

### 前端依赖

前端依赖由 [ui/package.json](ui/package.json) 管理：

```bash
cd ui

# 安装依赖
npm install

# 查看已安装的包
npm list --depth=0
```

主要依赖：
- **框架**: React 18.2.0
- **构建**: Vite 5.0.8
- **状态管理**: Zustand 4.4.7
- **样式**: Tailwind CSS 3.4.0
- **文档**: react-markdown, react-pdf
- **数据**: xlsx (Excel 处理)

---

## 📋 完整部署检查清单

### 部署前

- [ ] 准备服务器（Ubuntu 20.04+）
- [ ] 安装系统依赖（Python, Node.js, Nginx）
- [ ] 准备外部服务（MySQL, Redis, Qdrant, MinIO）
- [ ] 准备 API Keys（OpenAI, MinIO 等）

### 执行部署

- [ ] 克隆代码到服务器
- [ ] 执行 `./deploy.sh` 自动部署
- [ ] 编辑配置文件 `/var/www/km-agent/config/.env`
- [ ] 重启服务 `sudo systemctl restart km-agent-api`

### 部署后验证

- [ ] 检查后端健康：`curl http://localhost:5000/api/health`
- [ ] 检查前端访问：`curl http://localhost/`
- [ ] 查看服务状态：`sudo systemctl status km-agent-api`
- [ ] 查看日志：`tail -f /var/www/km-agent/logs/api.log`
- [ ] 浏览器访问：`http://your-server-ip`

---

## 🔧 常用命令

### 开发环境

```bash
# 启动开发环境（前后端分离）
./start.sh

# 停止开发环境
./stop.sh

# 检查依赖
./scripts/check_dependencies.sh

# 构建前端
./scripts/build_frontend.sh

# 安装本地模块
./scripts/install_local_modules.sh
```

### 生产环境

```bash
# 一键部署
sudo ./deploy.sh

# 服务管理
sudo systemctl start km-agent-api      # 启动
sudo systemctl stop km-agent-api       # 停止
sudo systemctl restart km-agent-api    # 重启
sudo systemctl status km-agent-api     # 状态
sudo systemctl enable km-agent-api     # 开机自启

# 日志查看
tail -f /var/www/km-agent/logs/api.log            # API 日志
tail -f /var/www/km-agent/logs/api.error.log      # 错误日志
tail -f /var/www/km-agent/logs/nginx-access.log   # Nginx 访问日志
sudo journalctl -u km-agent-api -f                # systemd 日志

# Nginx 管理
sudo nginx -t                          # 测试配置
sudo systemctl restart nginx           # 重启 Nginx
```

---

## 🆘 快速故障排查

### 后端无法启动

```bash
# 1. 查看详细日志
sudo journalctl -u km-agent-api -n 100 --no-pager

# 2. 检查端口占用
sudo lsof -i:5000

# 3. 手动启动测试
source /var/www/km-agent/venv/bin/activate
cd /var/www/km-agent/backend
python -m app_api.api
```

### 前端显示空白

```bash
# 1. 检查构建产物
ls -la /var/www/km-agent/frontend/dist/

# 2. 检查 Nginx 配置
sudo nginx -t
cat /etc/nginx/sites-enabled/km-agent

# 3. 查看 Nginx 错误日志
tail -f /var/www/km-agent/logs/nginx-error.log
```

### 502 Bad Gateway

```bash
# 1. 检查后端服务
sudo systemctl status km-agent-api

# 2. 检查端口监听
sudo netstat -tulpn | grep 5000

# 3. 测试后端直接访问
curl http://localhost:5000/api/health
```

---

## 📚 相关文档

- **详细部署指南**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **依赖分析报告**: 见 Agent 生成的完整报告
- **开发启动说明**: [start.sh](start.sh)
- **API 文档**: [app_api/README.md](app_api/README.md)

---

## ❓ 常见问题

### Q: 为什么不用 Flask 托管前端？
A: Nginx 专为静态文件设计，性能是 Flask 的 10-100 倍，且支持缓存、gzip、HTTP/2 等优化。生产环境应该用专业的 Web 服务器。

### Q: 可以不用 Nginx 吗？
A: 可以用其他 Web 服务器（Apache, Caddy），但不推荐用 Flask。如果只是开发测试，可以用 `vite preview` 预览。

### Q: 依赖太多了，能简化吗？
A: 不能。这些都是项目运行必需的依赖。已经按模块拆分，你可以只部署需要的模块。

### Q: 虚拟环境放在哪里？
A: 开发环境：`~/projects/venv`；生产环境：`/var/www/km-agent/venv`（deploy.sh 会自动创建）

### Q: 如何更新部署？
A: 重新执行 `./deploy.sh` 即可，它会自动 git pull 并重新构建。

---

**最后更新**: 2025-12-10
