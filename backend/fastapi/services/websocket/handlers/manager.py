"""WebSocket 连接管理器 - 整合所有 WebSocket 功能"""

from typing import Optional
import logging
from fastapi import WebSocket
from ..connection.pool import ConnectionPool
from .dispatcher import MessageDispatcher
from ..connection.monitor import ConnectionMonitor

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket 连接管理器：整合连接池、消息分发和监控功能"""

    def __init__(self):
        self._pool = ConnectionPool()
        self._dispatcher = MessageDispatcher(self._pool)
        self._monitor = ConnectionMonitor(self._pool)

    async def connect(self, websocket: WebSocket, instance_id: str) -> None:
        """接受连接并添加到指定实例组

        Args:
            websocket: WebSocket 连接对象
            instance_id: 实例 ID
        """
        await websocket.accept()
        self._pool.add(websocket, instance_id)
        logger.info(
            f"[WSManager] 新连接加入实例 '{instance_id}'，"
            f"当前该实例连接数: {self._pool.count(instance_id)}"
        )

    def disconnect(self, websocket: WebSocket, instance_id: str) -> None:
        """断开连接

        Args:
            websocket: WebSocket 连接对象
            instance_id: 实例 ID
        """
        self._pool.remove(websocket, instance_id)
        logger.info(
            f"[WSManager] 连接断开实例 '{instance_id}'，"
            f"剩余连接数: {self._pool.count(instance_id)}"
        )

    async def send_patch(
        self,
        instance_id: str,
        patch: dict,
        patch_id: Optional[int] = None
    ) -> bool:
        """向指定实例发送 Patch（兼容旧版本）

        Args:
            instance_id: 实例 ID
            patch: Patch 数据
            patch_id: Patch ID

        Returns:
            是否有活跃连接接收到消息
        """
        return await self._dispatcher.send_patch(instance_id, patch, patch_id, None)

    async def send_patch_with_version(
        self,
        instance_id: str,
        patch: dict,
        patch_id: Optional[int] = None,
        base_version: Optional[int] = None
    ) -> bool:
        """向指定实例发送 Patch（带版本号）

        Args:
            instance_id: 实例 ID
            patch: Patch 数据
            patch_id: Patch ID
            base_version: 基础版本号

        Returns:
            是否有活跃连接接收到消息
        """
        return await self._dispatcher.send_patch(instance_id, patch, patch_id, base_version)

    async def send_message(self, instance_id: str, message: dict) -> bool:
        """向指定实例发送自定义消息

        Args:
            instance_id: 实例 ID
            message: 消息内容

        Returns:
            是否有活跃连接接收到消息
        """
        return await self._dispatcher.send_to_instance(instance_id, message)

    async def broadcast(self, message: dict) -> int:
        """向所有实例广播消息

        Args:
            message: 消息内容

        Returns:
            接收到消息的实例数量
        """
        return await self._dispatcher.broadcast(message)

    def get_connection_count(self, instance_id: str) -> int:
        """获取指定实例的连接数

        Args:
            instance_id: 实例 ID

        Returns:
            连接数
        """
        return self._monitor.get_connection_count(instance_id)

    def get_total_connections(self) -> int:
        """获取总连接数

        Returns:
            总连接数
        """
        return self._monitor.get_connection_count()

    def get_stats(self) -> dict:
        """获取连接统计信息

        Returns:
            统计信息字典
        """
        return self._monitor.get_stats()

    def get_instance_stats(self, instance_id: str) -> dict:
        """获取指定实例的统计信息

        Args:
            instance_id: 实例 ID

        Returns:
            实例统计信息
        """
        return self._monitor.get_instance_stats(instance_id)

    def health_check(self) -> dict:
        """健康检查

        Returns:
            健康状态
        """
        return self._monitor.health_check()

    def list_active_instances(self) -> list:
        """列出所有有活跃连接的实例

        Returns:
            实例 ID 列表
        """
        return self._monitor.list_active_instances()


# 全局连接管理器实例
manager = WebSocketManager()
