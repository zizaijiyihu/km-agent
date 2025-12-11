#!/bin/bash
# ==============================================================================
# Docker 容器启动脚本
# 用途：在容器内同时启动 Nginx 和 Flask API
# ==============================================================================

set -e  # 遇到错误立即退出

echo "========================================="
echo "  KM Agent - Starting Services"
echo "========================================="

# 检查生产配置文件是否存在
if [ -f "/app/ks_infrastructure/configs/production_config.py" ]; then
    echo "✅ 发现生产配置文件: production_config.py"
    echo "   系统将优先加载此配置"
else
    echo "⚠️ 未找到生产配置文件，系统将使用默认配置 (default.py)"
    echo "   请确认这是否符合预期？"
fi

# 检查必要文件
if [ ! -f "/usr/share/nginx/html/index.html" ]; then
    echo "ERROR: Frontend files not found!"
    exit 1
fi

if [ ! -d "/app/app_api" ]; then
    echo "ERROR: Backend code not found!"
    exit 1
fi

# 启动 Nginx（后台模式）
echo "[1/2] Starting Nginx..."
nginx &
NGINX_PID=$!

# 等待 Nginx 启动
sleep 2

if ! ps -p $NGINX_PID > /dev/null; then
    echo "ERROR: Nginx failed to start!"
    exit 1
fi

echo "✓ Nginx started successfully (PID: $NGINX_PID)"

# 启动 Flask API（前台模式）
echo "[2/2] Starting Flask API..."
cd /app

# 设置 Python 路径
export PYTHONPATH=/app:$PYTHONPATH

# 启动 Flask（前台运行，这样容器不会退出）
exec python -u -m app_api.api

# 注意：上面的 exec 会替换当前 shell 进程
# 如果 Flask 崩溃，容器会退出，Docker 可以自动重启
