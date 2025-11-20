#!/bin/bash

# KM Agent 停止脚本

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}正在停止 KM Agent 服务...${NC}\n"

# 停止通过 start.sh 启动的服务
if [ -f /tmp/km_agent_api.pid ]; then
    API_PID=$(cat /tmp/km_agent_api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        kill $API_PID
        echo -e "${GREEN}✓ 后端服务已停止 (PID: $API_PID)${NC}"
    fi
    rm -f /tmp/km_agent_api.pid
fi

if [ -f /tmp/km_agent_ui.pid ]; then
    UI_PID=$(cat /tmp/km_agent_ui.pid)
    if kill -0 $UI_PID 2>/dev/null; then
        kill $UI_PID
        echo -e "${GREEN}✓ 前端服务已停止 (PID: $UI_PID)${NC}"
    fi
    rm -f /tmp/km_agent_ui.pid
fi

# 强制清理端口占用
if lsof -ti:5000 > /dev/null 2>&1; then
    echo -e "${BLUE}清理端口 5000...${NC}"
    lsof -ti:5000 | xargs kill -9 2>/dev/null || true
fi

if lsof -ti:8080 > /dev/null 2>&1; then
    echo -e "${BLUE}清理端口 8080...${NC}"
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
fi

echo -e "\n${GREEN}所有服务已停止${NC}"
