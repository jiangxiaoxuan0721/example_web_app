"""WebSocket 服务模块"""

from .handlers.manager import WebSocketManager

# 导出全局 WebSocket 管理器实例
manager = WebSocketManager()

__all__ = ["manager"]