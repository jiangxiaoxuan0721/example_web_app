"""WebSocket 连接池 - 管理所有 WebSocket 连接"""

from typing import Dict, Set
from fastapi import WebSocket


class ConnectionPool:
    """连接池：按 instanceId 分组存储 WebSocket 连接"""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}

    def add(self, websocket: WebSocket, instance_id: str) -> None:
        """添加连接到指定实例组"""
        if instance_id not in self._connections:
            self._connections[instance_id] = set()
        self._connections[instance_id].add(websocket)

    def remove(self, websocket: WebSocket, instance_id: str) -> None:
        """从指定实例组移除连接"""
        if instance_id in self._connections:
            self._connections[instance_id].discard(websocket)
            # 如果组为空，删除该组
            if not self._connections[instance_id]:
                del self._connections[instance_id]

    def get_all(self, instance_id: str) -> Set[WebSocket]:
        """获取指定实例的所有连接"""
        return self._connections.get(instance_id, set()).copy()

    def has_instance(self, instance_id: str) -> bool:
        """检查实例是否有活跃连接"""
        return instance_id in self._connections and len(self._connections[instance_id]) > 0

    def count(self, instance_id: str) -> int:
        """获取指定实例的连接数"""
        return len(self._connections.get(instance_id, set()))

    def count_all(self) -> int:
        """获取总连接数"""
        return sum(len(conns) for conns in self._connections.values())

    def clear(self, instance_id: str = "") -> None:
        """清空连接
        Args:
            instance_id: 如果指定，只清空该实例；否则清空所有
        """
        if instance_id:
            if instance_id in self._connections:
                del self._connections[instance_id]
        else:
            self._connections.clear()

    def get_all_instances(self) -> list:
        """获取所有有连接的实例 ID 列表"""
        return list(self._connections.keys())
