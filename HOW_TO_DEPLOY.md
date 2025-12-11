# KM Agent 上线部署指南

## 📋 概述

- **开发环境**: 使用 `start.sh` 启动（Vite Dev Server + Flask）
- **生产环境**: 使用 `deploy.sh` 启动（Docker 容器：Nginx + 前端构建产物 + Flask）

---

## 🔄 完整上线流程

### 准备阶段

#### 1️⃣ 修改配置文件

在上线前，确保修改生产环境配置：

```bash
# 编辑生产环境配置
vim ks_infrastructure/configs/production_config.py
```

**需要修改的配置项：**
- MySQL 连接信息（云数据库地址）
- Redis 连接信息（云缓存地址）
- Qdrant 连接信息（向量数据库地址）
- MinIO 连接信息（对象存储地址）
- OpenAI API Key 等

**示例：**
```python
# production_config.py
MYSQL_HOST = "your-cloud-mysql.com"  # 修改为云数据库地址
MYSQL_PORT = 3306
MYSQL_USER = "km_agent"
MYSQL_PASSWORD = "your-password"

REDIS_HOST = "your-cloud-redis.com"  # 修改为云 Redis 地址
REDIS_PASSWORD = "your-redis-password"

# ... 其他配置
```

#### 2️⃣ 确保代码已提交

```bash
# 查看修改状态
git status

# 提交修改（如果有）
git add .
git commit -m "Update production config"

# 推送到仓库（可选）
git push origin main
```

---

### 部署阶段

#### 3️⃣ 在生产服务器上执行部署

##### 选项 A: 本地代码部署到服务器

```bash
# 1. 上传代码到服务器
scp -r /Users/xiaohu/projects/km-agent_2 user@your-server:/path/to/

# 2. SSH 登录服务器
ssh user@your-server

# 3. 进入项目目录
cd /path/to/km-agent_2

# 4. 执行部署（一键部署）
./deploy.sh
```

##### 选项 B: 从 Git 仓库部署

```bash
# 1. SSH 登录服务器
ssh user@your-server

# 2. 克隆代码
git clone your-git-repo.git km-agent
cd km-agent

# 3. 执行部署
./deploy.sh
```

##### 选项 C: 使用 Docker Compose

```bash
# 1. SSH 登录服务器
ssh user@your-server

# 2. 进入项目目录
cd km-agent

# 3. 使用 Docker Compose 部署
docker-compose up -d
```

---

### 验证阶段

#### 4️⃣ 检查服务状态

```bash
# 查看容器是否运行
docker ps

# 查看容器日志
docker logs -f km-agent

# 测试后端健康检查
curl http://localhost:5000/api/health

# 测试前端访问
curl http://localhost:80
```

#### 5️⃣ 浏览器访问测试

打开浏览器访问：
- **前端**: `http://your-server-ip`
- **后端API**: `http://your-server-ip:5000/api/health`

测试核心功能：
- [ ] 登录功能
- [ ] 聊天功能
- [ ] 文档上传
- [ ] 知识库查询

---

## 📊 开发 vs 生产环境对比

| 项目 | 开发环境 (`start.sh`) | 生产环境 (`deploy.sh`) |
|------|---------------------|----------------------|
| **启动方式** | `./start.sh` | `./deploy.sh` |
| **前端服务** | Vite Dev Server (8080) | Nginx + 构建产物 (80) |
| **后端服务** | Flask (5000) | Flask (5000) |
| **前端特性** | 热重载、源码调试 | 已压缩、已优化 |
| **Nginx** | ❌ 不使用 | ✅ 使用 |
| **Docker** | ❌ 不使用 | ✅ 使用 |
| **配置文件** | default.py | production_config.py |
| **依赖** | Python、Node.js、npm | 只需 Docker |
| **端口** | 8080（前端）、5000（后端） | 80（前端+API代理）、5000（后端） |
| **性能** | 开发模式（较慢） | 生产优化（快） |
| **隔离性** | 直接运行在宿主机 | Docker 容器隔离 |

---

## 🔧 常见操作

### 查看日志

```bash
# 实时查看日志
docker logs -f km-agent

# 查看最近 100 行日志
docker logs --tail 100 km-agent

# 查看错误日志
docker logs km-agent 2>&1 | grep -i error
```

### 重启服务

```bash
# 方式 1: 使用 Docker 命令
docker restart km-agent

# 方式 2: 重新部署
./deploy.sh
```

### 停止服务

```bash
# 方式 1: 使用停止脚本
./docker-stop.sh

# 方式 2: 使用 Docker 命令
docker stop km-agent
docker rm km-agent

# 方式 3: 使用 Docker Compose
docker-compose down
```

### 更新代码

```bash
# 1. 停止旧服务
./docker-stop.sh

# 2. 拉取最新代码
git pull origin main

# 3. 重新部署
./deploy.sh
```

### 清理资源

```bash
# 清理项目资源
./deploy.sh --clean

# 清理所有 Docker 资源（慎用）
docker system prune -a
```

---

## 🚨 故障排查

### 问题 1: 容器启动失败

```bash
# 查看详细错误日志
docker logs km-agent

# 检查镜像是否构建成功
docker images | grep km-agent

# 重新构建
./deploy.sh
```

### 问题 2: 无法访问前端

```bash
# 检查端口是否开放
curl http://localhost:80

# 检查 Nginx 状态
docker exec km-agent nginx -t

# 检查前端文件是否存在
docker exec km-agent ls -la /usr/share/nginx/html
```

### 问题 3: API 请求失败

```bash
# 测试 API 健康检查
curl http://localhost:5000/api/health

# 查看 Flask 日志
docker logs km-agent | grep -i flask

# 测试云服务连接
docker exec km-agent ping your-mysql-host
```

### 问题 4: 数据库连接失败

**检查配置：**
```bash
# 进入容器
docker exec -it km-agent bash

# 查看配置是否正确
cat ks_infrastructure/configs/production_config.py

# 测试数据库连接
python -c "import pymysql; pymysql.connect(host='your-host', user='user', password='pwd')"
```

### 问题 5: 端口被占用

```bash
# 查看端口占用
lsof -i :80
lsof -i :5000

# 使用自定义端口
HTTP_PORT=8080 API_PORT=5001 ./deploy.sh
```

---

## 🎯 快速参考

### 开发环境（本地）

```bash
# 激活虚拟环境（如果需要）
source ~/projects/venv/bin/activate

# 启动开发服务
./start.sh

# 访问地址
# 前端: http://localhost:8080
# 后端: http://localhost:5000
```

### 生产环境（服务器）

```bash
# 一键部署
./deploy.sh

# 访问地址
# 前端: http://your-server-ip
# 后端: http://your-server-ip:5000

# 查看日志
docker logs -f km-agent

# 重启服务
docker restart km-agent

# 停止服务
./docker-stop.sh
```

---

## 📝 上线检查清单

### 部署前

- [ ] 修改 `production_config.py` 配置云服务地址
- [ ] 确保云服务（MySQL、Redis、Qdrant、MinIO）可访问
- [ ] 代码已提交并测试通过
- [ ] 服务器已安装 Docker
- [ ] 服务器防火墙已开放 80 和 5000 端口

### 部署中

- [ ] 上传代码到服务器（或从 Git 拉取）
- [ ] 执行 `./deploy.sh`
- [ ] 观察构建过程无错误
- [ ] 容器成功启动

### 部署后

- [ ] 访问前端页面正常
- [ ] 访问 `/api/health` 返回正常
- [ ] 测试登录功能
- [ ] 测试聊天功能
- [ ] 测试文档上传
- [ ] 查看日志无错误
- [ ] 设置监控告警（可选）

---

## 🎓 总结

```
开发流程:
    编写代码 → ./start.sh → 测试功能 → 提交代码
                    ↓
                前端: http://localhost:8080
                后端: http://localhost:5000

上线流程:
    修改配置 → 上传代码 → ./deploy.sh → 验证功能
                              ↓
                      前端: http://server-ip:80
                      后端: http://server-ip:5000
                      容器: km-agent (Docker)
```

**核心差异：**
- 开发：`start.sh` = Vite Dev Server（快速开发，热重载）
- 生产：`deploy.sh` = Docker 容器（Nginx + 优化构建，高性能）

---

**需要帮助？**
- 查看详细文档: `DOCKER_DEPLOY.md`
- 查看帮助: `./deploy.sh --help`
- 查看日志: `docker logs -f km-agent`
