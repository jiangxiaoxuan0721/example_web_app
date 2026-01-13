@echo off
echo ========================================
echo Schema-Driven UI Backend - 启动脚本
echo ========================================
echo.

echo [1/2] 启动 FastAPI 服务器 (端口 8000)...
start "FastAPI Server" python -m backend.fastapi.main
timeout /t 2 >nul

echo [2/2] 启动 MCP WebSocket 服务器 (端口 8765)...
start "MCP WebSocket Server" python -m backend.mcp.main
timeout /t 2 >nul

echo.
echo ========================================
echo 服务器已启动！
echo ========================================
echo.
echo FastAPI API:   http://localhost:8000
echo MCP WebSocket: ws://localhost:8765
echo MCP HTTP:      http://localhost:4445/mcp
echo API 文档:      http://localhost:8000/docs
echo.
echo 按 Ctrl+C 关闭所有服务器，或关闭各个窗口分别关闭
echo.

pause
