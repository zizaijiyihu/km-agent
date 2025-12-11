# KM Agent Docker 部署指南

## 快速开始

### 1. 一键部署（推荐）

```bash
# 赋予执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

部署完成后访问：
- **前端**: http://localhost:80
- **后端API**: http://localhost:5000

---

### 2. 使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 自定义配置

### 自定义端口

```bash
# 使用自定义端口部署
HTTP_PORT=8080 API_PORT=5001 ./deploy.sh
```

### 自定义镜像版本

```bash
# 构建特定版本
IMAGE_TAG=v1.0.0 ./deploy.sh
```

---

## 常用命令

### 查看服务状态

```bash
# 查看运行中的容器
docker ps

# 查看容器详细信息
docker inspect km-agent
```

### 日志管理

```bash
# 实时查看日志
docker logs -f km-agent

# 查看最近 100 行日志
docker logs --tail 100 km-agent

# 查看特定时间段日志
docker logs --since 30m km-agent
```

### 容器管理

```bash
# 停止容器
docker stop km-agent

# 启动容器
docker start km-agent

# 重启容器
docker restart km-agent

# 删除容器
docker rm -f km-agent
```

### 进入容器调试

```bash
# 进入容器 Shell
docker exec -it km-agent bash

# 查看容器内进程
docker exec km-agent ps aux

# 查看容器内文件
docker exec km-agent ls -la /app
```

---

## 更新部署

### 方式 1: 使用部署脚本（推荐）

```bash
# 更新代码后重新部署
git pull
./deploy.sh
```

脚本会自动：
1. 停止并删除旧容器
2. 重新构建镜像
3. 启动新容器
4. 执行健康检查

### 方式 2: 手动更新

```bash
# 1. 停止并删除旧容器
docker stop km-agent
docker rm km-agent

# 2. 重新构建镜像
docker build -t km-agent:latest .

# 3. 启动新容器
docker run -d \
  --name km-agent \
  -p 80:80 \
  -p 5000:5000 \
  --restart unless-stopped \
  km-agent:latest
```

---

## 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker logs km-agent

# 查看最近的错误
docker logs --tail 50 km-agent 2>&1 | grep -i error
```

### 端口被占用

```bash
# 查看端口占用情况
lsof -i :80
lsof -i :5000

# 使用其他端口
HTTP_PORT=8080 API_PORT=5001 ./deploy.sh
```

### 健康检查失败

```bash
# 手动测试 API
curl http://localhost:5000/api/health

# 查看容器状态
docker ps -a

# 查看容器资源使用
docker stats km-agent
```

### 前端无法访问

```bash
# 进入容器检查 Nginx
docker exec km-agent nginx -t

# 检查前端文件是否存在
docker exec km-agent ls -la /usr/share/nginx/html

# 查看 Nginx 日志
docker exec km-agent cat /var/log/nginx/error.log
```

---

## 清理资源

### 清理本项目资源

```bash
# 使用脚本清理
./deploy.sh --clean
```

### 手动清理

```bash
# 删除容器
docker rm -f km-agent

# 删除镜像
docker rmi km-agent:latest

# 清理悬空镜像
docker image prune -f

# 清理所有未使用资源（慎用）
docker system prune -a
```

---

## 配置说明

### 配置文件位置

- **生产环境配置**: `ks_infrastructure/configs/production_config.py`
- **默认配置**: `ks_infrastructure/configs/default.py`

### 切换配置环境

修改配置文件后需要重新构建镜像：

```bash
./deploy.sh
```

---

## 性能优化

### 资源限制

修改 `docker-compose.yml` 添加资源限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### 日志轮转

修改 `docker-compose.yml` 配置日志：

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 生产环境建议

1. **使用 HTTPS**: 配置 SSL 证书（可使用 Let's Encrypt）
2. **配置域名**: 修改 `docker/nginx.conf` 中的 `server_name`
3. **定期备份**: 备份配置文件和数据库
4. **监控告警**: 配置容器监控（如 Prometheus）
5. **日志收集**: 使用 ELK 或云日志服务
6. **自动重启**: 已配置 `--restart unless-stopped`

---

## 镜像仓库（可选）

### 推送到 Docker Hub

```bash
# 登录
docker login

# 标记镜像
docker tag km-agent:latest your-username/km-agent:latest

# 推送
docker push your-username/km-agent:latest
```

### 从仓库部署

```bash
# 拉取镜像
docker pull your-username/km-agent:latest

# 运行
docker run -d \
  --name km-agent \
  -p 80:80 \
  -p 5000:5000 \
  your-username/km-agent:latest
```

---

## 技术支持

如遇问题，请查看：
1. 容器日志: `docker logs -f km-agent`
2. 健康检查: `curl http://localhost:5000/api/health`
3. 容器状态: `docker ps -a`
