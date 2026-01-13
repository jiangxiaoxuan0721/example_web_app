#!/bin/bash

echo "========================================"
echo "Schema-Driven UI Backend - 启动脚本"
echo "========================================"
echo ""

echo "[1/2] 启动 FastAPI 服务器 (端口 8000)..."
python -m backend.fastapi.main &
FASTAPI_PID=$!
sleep 2

echo "[2/2] 启动 MCP WebSocket 服务器 (端口 8765)..."
python -m backend.mcp.main &
MCP_PID=$!
sleep 2

echo ""
echo "========================================"
echo "服务器已启动！"
echo "========================================"
echo ""
echo "FastAPI API:   http://localhost:8000"
echo "MCP WebSocket: ws://localhost:8765"
echo "MCP HTTP:      http://localhost:4445/mcp"
echo "API 文档:      http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 关闭所有服务器"
echo ""

# 捕获 Ctrl+C 信号
trap 'kill $FASTAPI_PID $MCP_PID 2>/dev/null; echo ""; echo "服务器已关闭"; exit' INT TERM

# 等待后台进程
wait
