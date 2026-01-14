"""WebSocket 消息分发器 - 负责向连接发送消息"""

from typing import Dict, Optional, Set
import logging
from fastapi import WebSocket

from ..connection.pool import ConnectionPool

logger = logging.getLogger(__name__)


class MessageDispatcher:
    """消息分发器：处理向 WebSocket 连接发送消息的逻辑"""

    def __init__(self, connection_pool: ConnectionPool):
        self._pool = connection_pool

    async def send_to_instance(
        self,
        instance_id: str,
        message: Dict,
        auto_cleanup: bool = True
    ) -> bool:
        """向指定实例的所有连接发送消息

        Args:
            instance_id: 实例 ID
            message: 要发送的消息字典
            auto_cleanup: 是否自动清理断开的连接

        Returns:
            是否有活跃连接接收到消息
        """
        if not self._pool.has_instance(instance_id):
            logger.warning(f"[MessageDispatcher] 实例 '{instance_id}' 没有活跃连接")
            return False

        connections = self._pool.get_all(instance_id)
        disconnected: Set[WebSocket] = set()

        for websocket in connections:
            try:
                await websocket.send_json(message)
                logger.debug(f"[MessageDispatcher] 发送消息到实例 '{instance_id}': {message}")
            except Exception as e:
                logger.error(f"[MessageDispatcher] 发送失败: {e}")
                disconnected.add(websocket)

        # 清理断开的连接
        if auto_cleanup:
            for ws in disconnected:
                self._pool.remove(ws, instance_id)
            if disconnected:
                logger.info(f"[MessageDispatcher] 清理了 {len(disconnected)} 个断开的连接")

        return self._pool.has_instance(instance_id)

    async def send_patch(
        self,
        instance_id: str,
        patch: Dict,
        patch_id: Optional[int] = None,
        base_version: Optional[int] = None
    ) -> bool:
        """发送 Patch 消息到指定实例

        Args:
            instance_id: 实例 ID
            patch: Patch 数据
            patch_id: Patch ID
            base_version: 基础版本号

        Returns:
            是否有活跃连接接收到消息
        """
        message = {
            "type": "patch",
            "instance_id": instance_id,
            "patch_id": patch_id,
            "baseVersion": base_version,
            "patch": patch
        }

        return await self.send_to_instance(instance_id, message)

    async def broadcast(self, message: Dict) -> int:
        """向所有实例广播消息

        Args:
            message: 要广播的消息

        Returns:
            接收到消息的实例数量
        """
        instances = self._pool.get_all_instances()
        success_count = 0

        for instance_id in instances:
            result = await self.send_to_instance(instance_id, message)
            if result:
                success_count += 1

        return success_count
