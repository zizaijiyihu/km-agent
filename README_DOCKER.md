# Docker 部署方案总结

## 📦 创建的文件

### 核心文件
1. **Dockerfile** - 多阶段构建配置
   - 阶段 1: 构建前端（Node.js）
   - 阶段 2: 构建后端 + Nginx（Python）

2. **docker-compose.yml** - Docker Compose 配置
   - 简化部署流程
   - 配置日志轮转
   - 健康检查

3. **deploy.sh** - 一键部署脚本（已优化）
   - 环境检查
   - 自动构建镜像
   - 容器管理
   - 健康检查
   - 详细日志

### 辅助文件
4. **docker/nginx.conf** - Nginx 配置
   - 前端静态文件服务
   - API 反向代理
   - 缓存策略
   - SSE 流式响应支持

5. **docker/start.sh** - 容器启动脚本
   - 启动 Nginx
   - 启动 Flask API
   - 错误检查

6. **.dockerignore** - 构建优化
   - 排除不必要文件
   - 减小构建上下文

7. **docker-stop.sh** - 快速停止脚本

8. **DOCKER_DEPLOY.md** - 部署文档

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────┐
│  Docker 容器 (km-agent)                  │
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Nginx (端口 80)                │     │
│  │  - 提供前端静态文件              │     │
│  │  - 反向代理 API 到 127.0.0.1:5000│   │
│  └────────────────────────────────┘     │
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Flask API (端口 5000)          │     │
│  │  - 后端业务逻辑                  │     │
│  │  - 连接外部依赖                  │     │
│  └────────────────────────────────┘     │
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Python 依赖 + 应用代码         │     │
│  │  - ks_infrastructure            │     │
│  │  - km_agent                     │     │
│  │  - app_api                      │     │
│  │  - 其他模块                      │     │
│  └────────────────────────────────┘     │
└─────────────────────────────────────────┘
                   │
                   │ 网络连接（配置文件配置）
                   ↓
┌─────────────────────────────────────────┐
│  外部云服务                               │
│  - MySQL (云数据库)                      │
│  - Redis (云缓存)                        │
│  - Qdrant (向量数据库)                   │
│  - MinIO (对象存储)                      │
└─────────────────────────────────────────┘
```

---

## 🚀 使用方式

### 方式 1: 一键部署（最简单）

```bash
./deploy.sh
```

### 方式 2: Docker Compose

```bash
docker-compose up -d
```

### 方式 3: 手动 Docker 命令

```bash
# 构建
docker build -t km-agent:latest .

# 运行
docker run -d --name km-agent -p 80:80 -p 5000:5000 km-agent:latest
```

---

## ✨ 方案优势

### 1. **环境一致性**
- 开发、测试、生产环境完全一致
- 消除"在我机器上能跑"问题

### 2. **部署简单**
- 一条命令完成部署
- 不需要手动安装 Nginx、Node.js 等依赖
- 宿主机只需要 Docker

### 3. **资源隔离**
- 容器之间相互独立
- 不污染宿主机环境
- 易于管理和清理

### 4. **易于扩展**
- 可以轻松启动多个实例（负载均衡）
- 支持 Docker Swarm / Kubernetes

### 5. **版本管理**
- 镜像版本化管理
- 支持快速回滚

### 6. **性能优化**
- 多阶段构建减小镜像体积
- Nginx 提供高性能静态文件服务

### 7. **监控友好**
- 标准化日志输出（stdout/stderr）
- 支持健康检查
- 容易接入监控系统

---

## 📊 镜像大小优化

### 优化措施
1. **多阶段构建**: 前端构建产物不包含 node_modules
2. **使用 slim 镜像**: python:3.11-slim 而非完整版
3. **清理 APT 缓存**: `rm -rf /var/lib/apt/lists/*`
4. **不缓存 pip**: `pip install --no-cache-dir`
5. **.dockerignore**: 排除不必要文件

### 预期镜像大小
- 基础镜像 (python:3.11-slim): ~140MB
- Nginx + 依赖: ~30MB
- Python 依赖: ~100-200MB
- 应用代码: ~20-50MB
- 前端构建产物: ~5-10MB

**总计**: 约 **300-450MB**

---

## 🔧 配置说明

### 配置文件管理
- **开发环境**: `ks_infrastructure/configs/default.py`
- **生产环境**: `ks_infrastructure/configs/production_config.py`

你自己管理配置文件切换，Docker 镜像构建时会包含这些配置。

### 端口配置
- **前端**: 80（可通过 HTTP_PORT 修改）
- **后端API**: 5000（可通过 API_PORT 修改）

### 外部依赖
通过配置文件连接云端服务：
- MySQL
- Redis
- Qdrant
- MinIO

---

## 🛠️ 开发工作流

### 本地开发
```bash
# 使用原有方式开发
npm run dev  # 前端
python -m app_api.api  # 后端
```

### 测试 Docker 部署
```bash
# 构建并运行
./deploy.sh

# 查看日志
docker logs -f km-agent

# 停止
./docker-stop.sh
```

### 更新代码后
```bash
# 重新部署（会自动重建镜像）
./deploy.sh
```

---

## 📝 部署检查清单

部署前确认：
- [ ] 配置文件已更新（production_config.py）
- [ ] Docker 已安装并运行
- [ ] 端口 80 和 5000 未被占用
- [ ] 云端服务（MySQL、Redis等）可访问
- [ ] 防火墙规则已配置

部署后验证：
- [ ] 访问 http://localhost 查看前端
- [ ] 访问 http://localhost:5000/api/health 检查后端
- [ ] 检查容器日志无错误
- [ ] 测试核心功能

---

## 🔄 CI/CD 集成（未来）

可以轻松集成到 CI/CD 流程：

```yaml
# .github/workflows/deploy.yml 示例
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t km-agent:${{ github.sha }} .
      - name: Push to registry
        run: docker push your-registry/km-agent:${{ github.sha }}
```

---

## 🆘 常见问题

### Q: 端口被占用怎么办？
```bash
# 使用自定义端口
HTTP_PORT=8080 API_PORT=5001 ./deploy.sh
```

### Q: 如何查看详细日志？
```bash
docker logs -f km-agent
```

### Q: 容器启动失败？
```bash
# 查看启动日志
docker logs km-agent

# 进入容器调试
docker exec -it km-agent bash
```

### Q: 如何更新代码？
```bash
# 拉取代码后重新部署
git pull
./deploy.sh
```

### Q: 如何清理所有资源？
```bash
./deploy.sh --clean
```

---

## 🎯 下一步

1. **测试部署**
   ```bash
   ./deploy.sh
   ```

2. **验证功能**
   - 访问前端
   - 测试 API
   - 检查日志

3. **生产环境优化**（可选）
   - 配置 HTTPS
   - 配置域名
   - 设置资源限制
   - 配置监控告警

4. **推送到镜像仓库**（可选）
   - Docker Hub
   - 阿里云容器镜像服务
   - 腾讯云容器镜像服务

---

## 📞 技术支持

部署过程中遇到问题，请：
1. 查看 `DOCKER_DEPLOY.md` 文档
2. 检查容器日志: `docker logs -f km-agent`
3. 使用 `./deploy.sh --help` 查看帮助

---

**部署脚本已优化完成！可以直接使用 `./deploy.sh` 一键部署。** 🎉
