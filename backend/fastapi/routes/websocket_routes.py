"""WebSocket 相关 API 路由"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from ..services.websocket import WebSocketManager


def register_websocket_routes(app, ws_manager: WebSocketManager, schema_manager):
    """注册 WebSocket 相关的路由

    Args:
        app: FastAPI 应用实例
        ws_manager: WebSocket 管理器
        schema_manager: Schema 管理器
    """

    @app.websocket("/ui/ws/{instance_id}")
    async def websocket_endpoint(websocket: WebSocket, instance_id: str):
        """WebSocket 连接端点"""
        await ws_manager.connect(websocket, instance_id)
        try:
            while True:
                # 等待客户端消息
                data = await websocket.receive_json()
                
                # 这里可以添加消息处理逻辑
                # 例如：处理客户端发送的特定指令或状态更新
                
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket, instance_id)

    @app.get("/ui/ws/stats")
    async def get_websocket_stats():
        """获取 WebSocket 连接统计信息"""
        return {
            "status": "success",
            "stats": ws_manager.get_stats()
        }

    @app.get("/ui/ws/health")
    async def websocket_health():
        """WebSocket 健康检查"""
        return {
            "status": "success",
            "health": ws_manager.health_check()
        }