"""WebSocket 连接监控器 - 提供连接统计和监控功能"""

import logging
from typing import Dict, List
from .pool import ConnectionPool

logger = logging.getLogger(__name__)


class ConnectionMonitor:
    """连接监控器：提供连接统计和健康检查"""

    def __init__(self, connection_pool: ConnectionPool):
        self._pool = connection_pool

    def get_stats(self) -> Dict:
        """获取连接统计信息

        Returns:
            包含连接统计的字典
        """
        instances = self._pool.get_all_instances()
        instance_stats = []

        for instance_id in instances:
            instance_stats.append({
                "instance_id": instance_id,
                "connections": self._pool.count(instance_id)
            })

        return {
            "total_connections": self._pool.count_all(),
            "total_instances": len(instances),
            "instances": instance_stats
        }

    def get_instance_stats(self, instance_id: str) -> Dict:
        """获取指定实例的连接统计

        Args:
            instance_id: 实例 ID

        Returns:
            实例连接统计
        """
        return {
            "instance_id": instance_id,
            "connections": self._pool.count(instance_id),
            "has_connections": self._pool.has_instance(instance_id)
        }

    def health_check(self) -> Dict:
        """健康检查

        Returns:
            健康状态
        """
        stats = self.get_stats()
        is_healthy = stats["total_connections"] > 0

        return {
            "status": "healthy" if is_healthy else "no_connections",
            "stats": stats
        }

    def list_active_instances(self) -> List[str]:
        """列出所有有活跃连接的实例

        Returns:
            实例 ID 列表
        """
        return self._pool.get_all_instances()

    def get_connection_count(self, instance_id: str = "") -> int:
        """获取连接数

        Args:
            instance_id: 如果指定，返回该实例的连接数；否则返回总数

        Returns:
            连接数
        """
        if instance_id:
            return self._pool.count(instance_id)
        return self._pool.count_all()
