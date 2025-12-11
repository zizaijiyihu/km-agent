#!/bin/bash

# ==============================================================================
# 本地模块安装脚本
# 用途: 按正确顺序安装所有本地 Python 模块
# ==============================================================================

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}开始安装本地 Python 模块...${NC}\n"

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检查虚拟环境
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}错误: 请先激活 Python 虚拟环境${NC}"
    echo "例如: source ~/projects/venv/bin/activate"
    exit 1
fi

echo -e "${GREEN}使用虚拟环境: $VIRTUAL_ENV${NC}\n"

# 模块安装顺序（按依赖层次）
modules=(
    # Layer 1: 基础层
    "ks_infrastructure"

    # Layer 2: 存储层
    "conversation_repository"
    "file_repository"
    "instruction_repository"
    "quote_repository"
    "reminder_repository"

    # Layer 3: 文档处理层
    "pdf_to_json"
    "aibase_news"
    "beisen_course"
    "tmp_image_repository"

    # Layer 4: 向量化层
    "document_vectorizer"
    "pdf_vectorizer"

    # Layer 5: 代理层
    "km_agent"

    # Layer 6: API 层
    "app_api"
)

# 安装模块
total=${#modules[@]}
current=0

for module in "${modules[@]}"; do
    current=$((current + 1))
    echo -e "${BLUE}[$current/$total] 安装模块: $module${NC}"

    if [ -d "$module" ]; then
        # 检查是否有 setup.py 或 pyproject.toml
        if [ -f "$module/setup.py" ] || [ -f "$module/pyproject.toml" ]; then
            pip install -e "./$module"
            echo -e "${GREEN}✓ $module 安装成功${NC}\n"
        else
            echo -e "${RED}✗ $module 没有 setup.py 或 pyproject.toml，跳过${NC}\n"
        fi
    else
        echo -e "${RED}✗ 目录 $module 不存在，跳过${NC}\n"
    fi
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}所有模块安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "已安装的模块:"
pip list | grep -E "ks-infrastructure|km-agent|app-api" || true
