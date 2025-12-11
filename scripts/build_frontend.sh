#!/bin/bash

# ==============================================================================
# 前端构建脚本
# 用途: 构建前端生产版本
# ==============================================================================

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   前端构建脚本${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UI_DIR="$PROJECT_ROOT/ui"

# 检查 UI 目录
if [ ! -d "$UI_DIR" ]; then
    echo -e "${RED}错误: UI 目录不存在: $UI_DIR${NC}"
    exit 1
fi

cd "$UI_DIR"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: Node.js 未安装${NC}"
    echo "请先安装 Node.js 18+ 版本"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}Node.js 版本: $NODE_VERSION${NC}\n"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: npm 未安装${NC}"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}npm 版本: $NPM_VERSION${NC}\n"

# 安装依赖
echo -e "${BLUE}[1/3] 安装依赖...${NC}"
npm install
echo -e "${GREEN}✓ 依赖安装完成${NC}\n"

# 清理旧构建
echo -e "${BLUE}[2/3] 清理旧构建...${NC}"
rm -rf dist
echo -e "${GREEN}✓ 清理完成${NC}\n"

# 执行构建
echo -e "${BLUE}[3/3] 执行生产构建...${NC}"
npm run build

# 检查构建产物
if [ ! -d "dist" ]; then
    echo -e "${RED}错误: 构建失败，dist 目录不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 构建完成${NC}\n"

# 显示构建产物
echo -e "${BLUE}构建产物:${NC}"
ls -lh dist/
echo ""

# 显示构建大小
DIST_SIZE=$(du -sh dist/ | cut -f1)
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   构建成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "  构建目录: $UI_DIR/dist/"
echo -e "  总大小: $DIST_SIZE"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo -e "  1. 预览构建: npm run preview"
echo -e "  2. 部署到服务器: 将 dist/ 目录复制到 Web 服务器"
echo ""
