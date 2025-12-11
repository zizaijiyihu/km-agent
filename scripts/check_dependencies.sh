#!/bin/bash

# ==============================================================================
# 依赖检查脚本
# 用途: 检查所有依赖是否正确安装
# ==============================================================================

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   依赖检查工具${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 检查计数器
total_checks=0
passed_checks=0
failed_checks=0

check_command() {
    local cmd=$1
    local name=$2
    total_checks=$((total_checks + 1))

    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -n1)
        echo -e "${GREEN}✓${NC} $name: $version"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${RED}✗${NC} $name: 未安装"
        failed_checks=$((failed_checks + 1))
    fi
}

check_python_package() {
    local package=$1
    total_checks=$((total_checks + 1))

    if python3 -c "import $package" 2>/dev/null; then
        local version=$(python3 -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✓${NC} $package: $version"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${RED}✗${NC} $package: 未安装"
        failed_checks=$((failed_checks + 1))
    fi
}

# 1. 检查系统命令
echo -e "${BLUE}1. 系统命令检查${NC}"
check_command python3 "Python 3"
check_command pip3 "pip"
check_command node "Node.js"
check_command npm "npm"
check_command git "Git"
echo ""

# 2. 检查 Python 虚拟环境
echo -e "${BLUE}2. Python 虚拟环境${NC}"
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${GREEN}✓${NC} 虚拟环境已激活: $VIRTUAL_ENV"
    passed_checks=$((passed_checks + 1))
else
    echo -e "${YELLOW}⚠${NC} 虚拟环境未激活"
    echo -e "  建议: source ~/projects/venv/bin/activate"
fi
total_checks=$((total_checks + 1))
echo ""

# 3. 检查 Python 第三方包
echo -e "${BLUE}3. Python 第三方包${NC}"
check_python_package flask
check_python_package openai
check_python_package qdrant_client
check_python_package boto3
check_python_package pandas
check_python_package fitz  # PyMuPDF
check_python_package redis
check_python_package mysql.connector
check_python_package requests
echo ""

# 4. 检查本地模块
echo -e "${BLUE}4. 本地 Python 模块${NC}"
cd "$PROJECT_ROOT"

modules=(
    "ks_infrastructure"
    "km_agent"
    "app_api"
    "document_vectorizer"
    "conversation_repository"
    "file_repository"
)

for module in "${modules[@]}"; do
    total_checks=$((total_checks + 1))
    module_name=$(echo "$module" | tr '_' '-')

    if python3 -c "import $module" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $module: 已安装"
        passed_checks=$((passed_checks + 1))
    elif [ -d "$module" ]; then
        echo -e "${YELLOW}⚠${NC} $module: 目录存在但未安装"
        echo -e "  运行: pip install -e ./$module"
    else
        echo -e "${RED}✗${NC} $module: 目录不存在"
        failed_checks=$((failed_checks + 1))
    fi
done
echo ""

# 5. 检查前端依赖
echo -e "${BLUE}5. 前端依赖${NC}"
if [ -d "$PROJECT_ROOT/ui/node_modules" ]; then
    echo -e "${GREEN}✓${NC} node_modules: 已安装"
    passed_checks=$((passed_checks + 1))
else
    echo -e "${RED}✗${NC} node_modules: 未安装"
    echo -e "  运行: cd ui && npm install"
    failed_checks=$((failed_checks + 1))
fi
total_checks=$((total_checks + 1))
echo ""

# 6. 检查配置文件
echo -e "${BLUE}6. 配置文件${NC}"
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} requirements.txt: 存在"
    passed_checks=$((passed_checks + 1))
else
    echo -e "${RED}✗${NC} requirements.txt: 不存在"
    failed_checks=$((failed_checks + 1))
fi
total_checks=$((total_checks + 1))

if [ -f "$PROJECT_ROOT/ui/package.json" ]; then
    echo -e "${GREEN}✓${NC} package.json: 存在"
    passed_checks=$((passed_checks + 1))
else
    echo -e "${RED}✗${NC} package.json: 不存在"
    failed_checks=$((failed_checks + 1))
fi
total_checks=$((total_checks + 1))
echo ""

# 7. 检查外部服务（可选）
echo -e "${BLUE}7. 外部服务连接 (可选)${NC}"

# MySQL
total_checks=$((total_checks + 1))
if command -v mysql &> /dev/null; then
    echo -e "${GREEN}✓${NC} MySQL 客户端: 已安装"
    passed_checks=$((passed_checks + 1))
else
    echo -e "${YELLOW}⚠${NC} MySQL 客户端: 未安装"
fi

# Redis
total_checks=$((total_checks + 1))
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓${NC} Redis: 运行中"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠${NC} Redis: 未运行"
    fi
else
    echo -e "${YELLOW}⚠${NC} Redis: 未安装"
fi

echo ""

# 总结
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   检查结果${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "  总计检查: $total_checks"
echo -e "  ${GREEN}通过: $passed_checks${NC}"
echo -e "  ${RED}失败: $failed_checks${NC}"
echo ""

if [ $failed_checks -eq 0 ]; then
    echo -e "${GREEN}✓ 所有依赖检查通过！${NC}"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠ 发现 $failed_checks 个问题，请修复后重试${NC}"
    echo ""
    echo -e "${BLUE}修复建议:${NC}"
    echo -e "  1. 安装系统依赖: sudo apt install python3 python3-pip nodejs npm"
    echo -e "  2. 创建虚拟环境: python3 -m venv ~/projects/venv"
    echo -e "  3. 激活虚拟环境: source ~/projects/venv/bin/activate"
    echo -e "  4. 安装 Python 依赖: pip install -r requirements.txt"
    echo -e "  5. 安装本地模块: ./scripts/install_local_modules.sh"
    echo -e "  6. 安装前端依赖: cd ui && npm install"
    echo ""
    exit 1
fi
