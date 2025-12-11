#!/bin/bash

# ==============================================================================
# KM Agent Docker 一键部署脚本
# 用途: 使用 Docker 自动化部署 KM Agent 项目
# 作者: KM Team
# 日期: 2025-12-10
# ==============================================================================

set -e  # 遇到错误立即退出

# ------------------------------------------------------------------------------
# 配置变量
# ------------------------------------------------------------------------------

# Docker 镜像配置
IMAGE_NAME="${IMAGE_NAME:-km-agent}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
CONTAINER_NAME="${CONTAINER_NAME:-km-agent}"

# 端口配置
HTTP_PORT="${HTTP_PORT:-80}"
API_PORT="${API_PORT:-5000}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ------------------------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 未安装，请先安装"
        exit 1
    fi
}

# ------------------------------------------------------------------------------
# 步骤 1: 环境检查
# ------------------------------------------------------------------------------

step1_check_environment() {
    log_info "步骤 1/6: 检查系统环境..."

    # 检查 Docker
    check_command docker

    # 检查 Docker 版本
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    log_info "Docker 版本: $DOCKER_VERSION"

    # 检查 Docker 是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker daemon 未运行，请启动 Docker"
        exit 1
    fi

    # 检查 Docker Compose（可选）
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        log_info "Docker Compose 版本: $COMPOSE_VERSION"
    else
        log_warning "Docker Compose 未安装（可选）"
    fi

    log_success "环境检查通过"
}

# ------------------------------------------------------------------------------
# 步骤 2: 停止并清理旧容器
# ------------------------------------------------------------------------------

step2_cleanup_old_container() {
    log_info "步骤 2/6: 清理旧容器..."

    # 检查容器是否存在
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_info "发现旧容器，正在停止..."
        docker stop "$CONTAINER_NAME" || true
        
        log_info "正在删除旧容器..."
        docker rm "$CONTAINER_NAME" || true
        
        log_success "旧容器已清理"
    else
        log_info "未发现旧容器"
    fi
}

# ------------------------------------------------------------------------------
# 步骤 3: 构建 Docker 镜像
# ------------------------------------------------------------------------------

step3_build_image() {
    log_info "步骤 3/6: 构建 Docker 镜像..."

    # 获取当前目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    log_info "构建镜像: $IMAGE_NAME:$IMAGE_TAG"
    log_info "构建上下文: $SCRIPT_DIR"

    # 构建镜像
    docker build \
        -t "$IMAGE_NAME:$IMAGE_TAG" \
        -f "$SCRIPT_DIR/Dockerfile" \
        "$SCRIPT_DIR"

    # 检查构建结果
    if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE_NAME}:${IMAGE_TAG}$"; then
        log_success "镜像构建成功: $IMAGE_NAME:$IMAGE_TAG"
        
        # 显示镜像信息
        IMAGE_SIZE=$(docker images --format '{{.Size}}' "$IMAGE_NAME:$IMAGE_TAG")
        log_info "镜像大小: $IMAGE_SIZE"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# ------------------------------------------------------------------------------
# 步骤 4: 运行容器
# ------------------------------------------------------------------------------

step4_run_container() {
    log_info "步骤 4/6: 启动容器..."

    # 检查端口是否被占用
    if lsof -Pi :$HTTP_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "端口 $HTTP_PORT 已被占用"
        log_info "请停止占用端口的程序或修改 HTTP_PORT 环境变量"
        exit 1
    fi

    if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "端口 $API_PORT 已被占用"
        log_info "请停止占用端口的程序或修改 API_PORT 环境变量"
        exit 1
    fi

    # 启动容器
    log_info "启动容器: $CONTAINER_NAME"
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$HTTP_PORT:80" \
        -p "$API_PORT:5000" \
        --restart unless-stopped \
        "$IMAGE_NAME:$IMAGE_TAG"

    # 等待容器启动
    sleep 3

    # 检查容器状态
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_success "容器启动成功"
    else
        log_error "容器启动失败，查看日志:"
        docker logs "$CONTAINER_NAME"
        exit 1
    fi
}

# ------------------------------------------------------------------------------
# 步骤 5: 健康检查
# ------------------------------------------------------------------------------

step5_health_check() {
    log_info "步骤 5/6: 执行健康检查..."

    # 等待服务启动
    log_info "等待服务启动（最多 60 秒）..."
    
    for i in {1..60}; do
        if curl -sf "http://localhost:$API_PORT/api/health" > /dev/null 2>&1; then
            log_success "✓ 后端 API 健康检查通过"
            break
        fi
        
        if [ $i -eq 60 ]; then
            log_error "✗ 后端 API 健康检查失败（超时）"
            log_info "查看容器日志:"
            docker logs --tail 50 "$CONTAINER_NAME"
            exit 1
        fi
        
        sleep 1
    done

    # 检查前端
    if curl -sf "http://localhost:$HTTP_PORT/" > /dev/null 2>&1; then
        log_success "✓ 前端服务健康检查通过"
    else
        log_warning "✗ 前端服务健康检查失败（可能 Nginx 还未启动）"
    fi
}

# ------------------------------------------------------------------------------
# 步骤 6: 显示部署信息
# ------------------------------------------------------------------------------

step6_show_info() {
    log_info "步骤 6/6: 收集部署信息..."

    # 获取容器 ID
    CONTAINER_ID=$(docker ps -qf "name=^${CONTAINER_NAME}$")

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   部署成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "  ${BLUE}前端地址:${NC} http://localhost:$HTTP_PORT"
    echo -e "  ${BLUE}后端地址:${NC} http://localhost:$API_PORT"
    echo ""
    echo -e "  ${BLUE}容器名称:${NC} $CONTAINER_NAME"
    echo -e "  ${BLUE}容器 ID:${NC}  $CONTAINER_ID"
    echo -e "  ${BLUE}镜像版本:${NC} $IMAGE_NAME:$IMAGE_TAG"
    echo ""
    echo -e "${YELLOW}常用命令:${NC}"
    echo -e "  查看日志:   ${BLUE}docker logs -f $CONTAINER_NAME${NC}"
    echo -e "  停止容器:   ${BLUE}docker stop $CONTAINER_NAME${NC}"
    echo -e "  启动容器:   ${BLUE}docker start $CONTAINER_NAME${NC}"
    echo -e "  重启容器:   ${BLUE}docker restart $CONTAINER_NAME${NC}"
    echo -e "  删除容器:   ${BLUE}docker rm -f $CONTAINER_NAME${NC}"
    echo -e "  进入容器:   ${BLUE}docker exec -it $CONTAINER_NAME bash${NC}"
    echo -e "  查看状态:   ${BLUE}docker ps -f name=$CONTAINER_NAME${NC}"
    echo ""
    echo -e "${YELLOW}使用 Docker Compose:${NC}"
    echo -e "  启动服务:   ${BLUE}docker-compose up -d${NC}"
    echo -e "  查看日志:   ${BLUE}docker-compose logs -f${NC}"
    echo -e "  停止服务:   ${BLUE}docker-compose down${NC}"
    echo ""
}

# ------------------------------------------------------------------------------
# 清理函数（可选）
# ------------------------------------------------------------------------------

cleanup_images() {
    log_info "清理悬空镜像..."
    docker image prune -f
    log_success "清理完成"
}

# ------------------------------------------------------------------------------
# 主流程
# ------------------------------------------------------------------------------

main() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   KM Agent Docker 自动化部署${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # 执行各个步骤
    step1_check_environment
    step2_cleanup_old_container
    step3_build_image
    step4_run_container
    step5_health_check
    step6_show_info

    # 可选：清理悬空镜像
    # cleanup_images
}

# ------------------------------------------------------------------------------
# 处理命令行参数
# ------------------------------------------------------------------------------

case "${1:-}" in
    --help|-h)
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --help, -h          显示帮助信息"
        echo "  --clean             清理旧镜像和容器"
        echo "  --logs              查看容器日志"
        echo "  --status            查看容器状态"
        echo ""
        echo "环境变量:"
        echo "  IMAGE_NAME          镜像名称（默认: km-agent）"
        echo "  IMAGE_TAG           镜像标签（默认: latest）"
        echo "  CONTAINER_NAME      容器名称（默认: km-agent）"
        echo "  HTTP_PORT           HTTP 端口（默认: 80）"
        echo "  API_PORT            API 端口（默认: 5000）"
        echo ""
        echo "示例:"
        echo "  $0                                 # 标准部署"
        echo "  HTTP_PORT=8080 API_PORT=5001 $0   # 自定义端口"
        echo "  IMAGE_TAG=v1.0.0 $0               # 指定版本"
        exit 0
        ;;
    --clean)
        log_info "清理 Docker 资源..."
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
        docker rmi "$IMAGE_NAME:$IMAGE_TAG" 2>/dev/null || true
        docker image prune -f
        log_success "清理完成"
        exit 0
        ;;
    --logs)
        docker logs -f "$CONTAINER_NAME"
        exit 0
        ;;
    --status)
        docker ps -f "name=$CONTAINER_NAME"
        exit 0
        ;;
    "")
        # 默认执行部署
        main "$@"
        ;;
    *)
        log_error "未知参数: $1"
        echo "使用 --help 查看帮助"
        exit 1
        ;;
esac
