"""Schema 实例管理器 - 管理所有 UI Schema 实例"""

from typing import Any
from ..fastapi.models import UISchema


class SchemaManager:
    """Schema 实例管理器"""

    def __init__(self):
        self._instances: dict[str, UISchema] = {}

    def get(self, instance_name: str) -> UISchema | None:
        """获取指定实例的 Schema"""
        return self._instances.get(instance_name)

    def set(self, instance_name: str, schema: UISchema) -> None:
        """设置/更新实例的 Schema"""
        self._instances[instance_name] = schema

    def delete(self, instance_name: str) -> bool:
        """删除实例"""
        if instance_name in self._instances:
            del self._instances[instance_name]
            return True
        return False

    def exists(self, instance_name: str) -> bool:
        """检查实例是否存在"""
        return instance_name in self._instances

    def list_all(self) -> list[str]:
        """列出所有实例 ID"""
        return list(self._instances.keys())

    def count(self) -> int:
        """获取实例总数"""
        return len(self._instances)

    def get_info(self, instance_name: str) -> dict[Any, Any] | None:
        """获取实例信息"""
        schema = self.get(instance_name)
        if not schema:
            return None

        return {
            "instance_name": instance_name,
            "page_key": schema.page_key,
            "blocks_count": len(schema.blocks),
            "actions_count": len(schema.actions)
        }

    def get_all_info(self) -> list[dict[Any, Any]]:
        """获取所有实例信息"""
        return [info for info in (self.get_info(instance_name) for instance_name in self.list_all()) if info is not None]
