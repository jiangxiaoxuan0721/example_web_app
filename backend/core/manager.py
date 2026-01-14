"""Schema 实例管理器 - 管理所有 UI Schema 实例"""

from typing import Dict
from ..fastapi.models import UISchema


class SchemaManager:
    """Schema 实例管理器"""

    def __init__(self):
        self._instances: Dict[str, UISchema] = {}

    def get(self, instance_id: str) -> UISchema | None:
        """获取指定实例的 Schema"""
        return self._instances.get(instance_id)

    def set(self, instance_id: str, schema: UISchema) -> None:
        """设置/更新实例的 Schema"""
        self._instances[instance_id] = schema

    def delete(self, instance_id: str) -> bool:
        """删除实例"""
        if instance_id in self._instances:
            del self._instances[instance_id]
            return True
        return False

    def exists(self, instance_id: str) -> bool:
        """检查实例是否存在"""
        return instance_id in self._instances

    def list_all(self) -> list[str]:
        """列出所有实例 ID"""
        return list(self._instances.keys())

    def count(self) -> int:
        """获取实例总数"""
        return len(self._instances)

    def get_info(self, instance_id: str) -> dict | None:
        """获取实例信息"""
        schema = self.get(instance_id)
        if not schema:
            return None

        return {
            "instance_id": instance_id,
            "page_key": schema.meta.pageKey,
            "status": schema.meta.status,
            "blocks_count": len(schema.blocks),
            "actions_count": len(schema.actions)
        }

    def get_all_info(self) -> list[dict]:
        """获取所有实例信息"""
        return [self.get_info(instance_id) for instance_id in self.list_all()] # type: ignore