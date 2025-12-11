# KM Agent 部署指南

## 📋 目录
- [部署架构](#部署架构)
- [系统要求](#系统要求)
- [部署流程](#部署流程)
- [配置说明](#配置说明)
- [服务管理](#服务管理)
- [故障排查](#故障排查)

---

## 🏗️ 部署架构

### 架构图
```
用户 (浏览器)
    ↓
  Nginx (端口 80/443)
    ├─→ 静态文件 (/, /assets/*)  → /var/www/km-agent/frontend/dist/
    └─→ API 请求 (/api/*)        → Flask (端口 5000)
```

### 部署目录结构
```
/var/www/km-agent/
├── backend/                      # 后端 Python 代码
│   ├── aibase_news/
│   ├── app_api/
│   ├── beisen_course/
│   ├── conversation_repository/
│   ├── document_vectorizer/
│   ├── file_repository/
│   ├── instruction_repository/
│   ├── km_agent/
│   ├── ks_infrastructure/
│   ├── pdf_to_json/
│   ├── pdf_vectorizer/
│   ├── quote_repository/
│   ├── reminder_repository/
│   ├── tmp_image_repository/
│   ├── requirements.txt
│   └── ...
│
├── frontend/                     # 前端构建产物
│   └── dist/                    # npm run build 的输出
│       ├── index.html
│       ├── assets/
│       └── ...
│
├── venv/                        # Python 虚拟环境
│   ├── bin/
│   ├── lib/
│   └── ...
│
├── logs/                        # 日志目录
│   ├── api.log
│   ├── api.error.log
│   ├── nginx-access.log
│   └── nginx-error.log
│
└── config/                      # 配置文件
    ├── .env                     # 环境变量
    └── nginx.conf              # Nginx 配置
```

---

## 💻 系统要求

### 操作系统
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- macOS 12+ (开发环境)

### 软件依赖
- **Python**: 3.8+
- **Node.js**: 18+ (仅构建时需要)
- **Nginx**: 1.18+
- **Git**: 2.0+

### 外部服务
- **MySQL**: 8.0+
- **Redis**: 5.0+
- **Qdrant**: 1.7+ (向量数据库)
- **MinIO/S3**: 对象存储服务

### 硬件要求
- **CPU**: 2 核心+
- **内存**: 4GB+ (推荐 8GB+)
- **磁盘**: 20GB+ (取决于数据量)

---

## 🚀 部署流程

### 1. 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git python3 python3-pip python3-venv nginx curl

# 创建部署目录
sudo mkdir -p /var/www/km-agent/{backend,frontend,venv,logs,config}
sudo chown -R $USER:$USER /var/www/km-agent
```

### 2. 克隆代码

```bash
cd /var/www/km-agent
git clone <your-repo-url> backend
cd backend
```

### 3. 安装后端依赖

```bash
cd /var/www/km-agent

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r backend/requirements.txt

# 安装本地模块（按依赖顺序）
cd backend
pip install -e ./ks_infrastructure
pip install -e ./conversation_repository
pip install -e ./file_repository
pip install -e ./instruction_repository
pip install -e ./quote_repository
pip install -e ./reminder_repository
pip install -e ./pdf_to_json
pip install -e ./aibase_news
pip install -e ./beisen_course
pip install -e ./tmp_image_repository
pip install -e ./document_vectorizer
pip install -e ./km_agent
pip install -e ./app_api
cd ..
```

### 4. 构建前端

```bash
cd /var/www/km-agent/backend/ui

# 安装 Node.js 依赖
npm install

# 生产环境构建
npm run build

# 移动构建产物到部署目录
mv dist /var/www/km-agent/frontend/
```

### 5. 配置环境变量

```bash
cd /var/www/km-agent/config

# 创建 .env 文件
cat > .env << 'EOF'
# KM Agent 环境变量配置

# ====== OpenAI 配置 ======
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# ====== MySQL 配置 ======
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=km_agent
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=km_agent

# ====== Redis 配置 ======
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# ====== Qdrant 配置 ======
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=

# ====== MinIO/S3 配置 ======
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-minio-access-key
MINIO_SECRET_KEY=your-minio-secret-key
MINIO_BUCKET=km-agent
MINIO_SECURE=false

# ====== Flask 配置 ======
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# ====== 日志配置 ======
LOG_LEVEL=INFO
LOG_FILE=/var/www/km-agent/logs/api.log
EOF

# 设置权限
chmod 600 .env
```

### 6. 配置 Nginx

```bash
sudo cat > /etc/nginx/sites-available/km-agent << 'EOF'
# KM Agent Nginx 配置

upstream flask_backend {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名

    # 日志文件
    access_log /var/www/km-agent/logs/nginx-access.log;
    error_log /var/www/km-agent/logs/nginx-error.log;

    # 前端静态文件
    location / {
        root /var/www/km-agent/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;

        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API 反向代理
    location /api {
        proxy_pass http://flask_backend;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # 文件上传大小限制
        client_max_body_size 100M;
    }

    # 健康检查端点
    location /api/health {
        proxy_pass http://flask_backend/api/health;
        access_log off;
    }
}
EOF

# 启用站点
sudo ln -sf /etc/nginx/sites-available/km-agent /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 7. 配置 systemd 服务

```bash
sudo cat > /etc/systemd/system/km-agent-api.service << 'EOF'
[Unit]
Description=KM Agent API Service
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/km-agent/backend
Environment="PATH=/var/www/km-agent/venv/bin"
EnvironmentFile=/var/www/km-agent/config/.env
ExecStart=/var/www/km-agent/venv/bin/python -u -m app_api.api
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/var/www/km-agent/logs/api.log
StandardError=append:/var/www/km-agent/logs/api.error.log

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start km-agent-api

# 设置开机自启
sudo systemctl enable km-agent-api

# 查看状态
sudo systemctl status km-agent-api
```

### 8. 验证部署

```bash
# 检查后端健康
curl http://localhost:5000/api/health

# 检查前端 (通过 Nginx)
curl http://localhost/

# 查看日志
tail -f /var/www/km-agent/logs/api.log
```

---

## ⚙️ 配置说明

### 环境变量说明

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | ✅ | - |
| `OPENAI_API_BASE` | OpenAI API 基础 URL | ❌ | https://api.openai.com/v1 |
| `MYSQL_HOST` | MySQL 主机地址 | ✅ | localhost |
| `MYSQL_PORT` | MySQL 端口 | ❌ | 3306 |
| `MYSQL_USER` | MySQL 用户名 | ✅ | - |
| `MYSQL_PASSWORD` | MySQL 密码 | ✅ | - |
| `MYSQL_DATABASE` | MySQL 数据库名 | ✅ | - |
| `REDIS_HOST` | Redis 主机地址 | ✅ | localhost |
| `REDIS_PORT` | Redis 端口 | ❌ | 6379 |
| `QDRANT_HOST` | Qdrant 主机地址 | ✅ | localhost |
| `QDRANT_PORT` | Qdrant 端口 | ❌ | 6333 |
| `MINIO_ENDPOINT` | MinIO 端点 | ✅ | - |
| `MINIO_ACCESS_KEY` | MinIO 访问密钥 | ✅ | - |
| `MINIO_SECRET_KEY` | MinIO 密钥 | ✅ | - |
| `FLASK_PORT` | Flask 监听端口 | ❌ | 5000 |

### 数据库初始化

```bash
# 创建数据库
mysql -u root -p << EOF
CREATE DATABASE km_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'km_agent'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON km_agent.* TO 'km_agent'@'localhost';
FLUSH PRIVILEGES;
EOF

# 运行迁移脚本（如果有）
# source /var/www/km-agent/venv/bin/activate
# cd /var/www/km-agent/backend
# python scripts/init_db.py
```

---

## 🔧 服务管理

### systemd 命令

```bash
# 启动服务
sudo systemctl start km-agent-api

# 停止服务
sudo systemctl stop km-agent-api

# 重启服务
sudo systemctl restart km-agent-api

# 查看状态
sudo systemctl status km-agent-api

# 查看日志
sudo journalctl -u km-agent-api -f

# 启用开机自启
sudo systemctl enable km-agent-api

# 禁用开机自启
sudo systemctl disable km-agent-api
```

### 日志管理

```bash
# 查看 API 日志
tail -f /var/www/km-agent/logs/api.log

# 查看错误日志
tail -f /var/www/km-agent/logs/api.error.log

# 查看 Nginx 访问日志
tail -f /var/www/km-agent/logs/nginx-access.log

# 查看 Nginx 错误日志
tail -f /var/www/km-agent/logs/nginx-error.log

# 清理旧日志
find /var/www/km-agent/logs -name "*.log" -mtime +30 -delete
```

---

## 🔍 故障排查

### 常见问题

#### 1. 后端服务无法启动

**症状**: `systemctl status km-agent-api` 显示失败

**排查步骤**:
```bash
# 查看详细错误日志
sudo journalctl -u km-agent-api -n 50 --no-pager

# 检查环境变量
cat /var/www/km-agent/config/.env

# 手动启动测试
source /var/www/km-agent/venv/bin/activate
cd /var/www/km-agent/backend
python -m app_api.api
```

#### 2. Nginx 502 Bad Gateway

**症状**: 访问网站返回 502 错误

**排查步骤**:
```bash
# 检查后端服务是否运行
sudo systemctl status km-agent-api

# 检查端口监听
sudo netstat -tulpn | grep 5000

# 检查 Nginx 错误日志
sudo tail -f /var/www/km-agent/logs/nginx-error.log
```

#### 3. 前端显示空白页

**症状**: 浏览器加载后显示空白

**排查步骤**:
```bash
# 检查构建产物是否存在
ls -la /var/www/km-agent/frontend/dist/

# 检查 Nginx 配置
sudo nginx -t

# 查看浏览器控制台错误
# (F12 → Console 标签)

# 检查 API 端点是否可达
curl http://localhost/api/health
```

#### 4. 数据库连接失败

**症状**: 日志显示 "Can't connect to MySQL server"

**排查步骤**:
```bash
# 检查 MySQL 服务
sudo systemctl status mysql

# 测试数据库连接
mysql -h localhost -u km_agent -p km_agent

# 检查防火墙
sudo ufw status
```

#### 5. 文件上传失败

**症状**: 上传大文件返回 413 错误

**解决方案**:
```bash
# 修改 Nginx 配置
sudo vim /etc/nginx/sites-available/km-agent

# 在 server 块中添加:
client_max_body_size 100M;

# 重启 Nginx
sudo systemctl restart nginx
```

---

## 🔐 安全建议

### 1. HTTPS 配置 (生产环境必需)

```bash
# 使用 Let's Encrypt 免费证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. 定期更新

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 更新 Python 依赖
source /var/www/km-agent/venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## 📊 监控建议

### 1. 系统监控
- CPU/内存使用率
- 磁盘空间
- 网络流量

### 2. 应用监控
- API 响应时间
- 错误率
- 请求量

### 3. 日志聚合
- ELK Stack (Elasticsearch + Logstash + Kibana)
- Grafana + Loki
- CloudWatch (AWS)

---

## 📚 相关文档

- [开发环境启动说明](README.md)
- [依赖分析报告](DEPENDENCIES.md)
- [API 文档](app_api/README.md)

---

**最后更新**: 2025-12-10
