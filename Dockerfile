# ==============================================================================
# KM Agent Dockerfile - 多阶段构建
# 阶段1: 构建前端静态文件
# 阶段2: 构建 Python 应用 + Nginx
# ==============================================================================

# ================== 阶段 1: 构建前端 ==================
FROM docker.1ms.run/node:18-alpine AS frontend-builder

WORKDIR /app/ui

# 复制 package 文件（利用 Docker 缓存）
COPY ui/package*.json ./

# 安装依赖
RUN npm install

# 复制前端源码
COPY ui/ ./

# 构建生产版本
RUN npm run build

# ================== 阶段 2: Python 应用 + Nginx ==================
FROM docker.1ms.run/python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nginx \
    curl \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 创建应用目录
WORKDIR /app

# 复制并安装 Python 依赖（利用 Docker 缓存）
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 查找并安装所有子模块的依赖（基本包逻辑）
# 遍历当前目录下所有 requirements.txt 并安装
RUN find . -mindepth 2 -name "requirements.txt" -exec pip install -r {} -i https://pypi.tuna.tsinghua.edu.cn/simple \;

# 安装本地 Python 模块（按依赖顺序）
# 安装本地 Python 模块（已被 PYTHONPATH 替代）
# 不需要 pip install -e，因为 start.sh 中已经设置了 export PYTHONPATH=/app:$PYTHONPATH

# 复制前端构建产物
COPY --from=frontend-builder /app/ui/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY docker/nginx.conf /etc/nginx/sites-available/default
RUN rm -f /etc/nginx/sites-enabled/default && \
    ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# 创建 Nginx 配置
RUN echo 'daemon off;' >> /etc/nginx/nginx.conf

# 复制启动脚本
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# 创建日志目录
RUN mkdir -p /var/log/km-agent

# 暴露端口
EXPOSE 80 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 启动服务
CMD ["/start.sh"]
