"""WebSocket 连接池 - 管理所有 WebSocket 连接"""

from fastapi import WebSocket
from typing import Any


class ConnectionPool:
    """连接池：按 instanceId 分组存储 WebSocket 连接"""

    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = {}

    def add(self, websocket: WebSocket, instance_name: str) -> None:
        """添加连接到指定实例组"""
        if instance_name not in self._connections:
            self._connections[instance_name] = set()
        self._connections[instance_name].add(websocket)

    def remove(self, websocket: WebSocket, instance_name: str) -> None:
        """从指定实例组移除连接"""
        if instance_name in self._connections:
            self._connections[instance_name].discard(websocket)
            # 如果组为空，删除该组
            if not self._connections[instance_name]:
                del self._connections[instance_name]

    def get_all(self, instance_name: str) -> set[WebSocket]:
        """获取指定实例的所有连接"""
        return self._connections.get(instance_name, set()).copy()

    def has_instance(self, instance_name: str) -> bool:
        """检查实例是否有活跃连接"""
        return instance_name in self._connections and len(self._connections[instance_name]) > 0

    def count(self, instance_name: str) -> int:
        """获取指定实例的连接数"""
        return len(self._connections.get(instance_name, set()))

    def count_all(self) -> int:
        """获取总连接数"""
        return sum(len(conns) for conns in self._connections.values())

    def clear(self, instance_name: str = "") -> None:
        """清空连接
        Args:
            instance_name: 如果指定，只清空该实例；否则清空所有
        """
        if instance_name:
            if instance_name in self._connections:
                del self._connections[instance_name]
        else:
            self._connections.clear()

    def get_all_instances(self) -> list[Any]:
        """获取所有有连接的实例 ID 列表"""
        return list(self._connections.keys())
