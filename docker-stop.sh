#!/bin/bash

# ==============================================================================
# KM Agent 快速停止脚本
# 用途: 快速停止 Docker 容器
# ==============================================================================

set -e

CONTAINER_NAME="${CONTAINER_NAME:-km-agent}"

echo "正在停止容器: $CONTAINER_NAME"
docker stop "$CONTAINER_NAME" 2>/dev/null || echo "容器未运行"

echo "正在删除容器: $CONTAINER_NAME"
docker rm "$CONTAINER_NAME" 2>/dev/null || echo "容器已删除"

echo "✓ 停止完成"
