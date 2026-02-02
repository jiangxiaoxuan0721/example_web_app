"""Patch 历史管理器 - 管理和查询 Patch 历史记录"""

from datetime import datetime
from typing import cast


class PatchHistoryManager:
    """Patch 历史记录管理器"""

    def __init__(self) -> None:
        self._history: "dict[str, list[dict[str, object]]]" = {}
        self._counters: "dict[str, int]" = {}

    def save(self, instance_name: str, patch: "dict[str, object]") -> int:
        """保存 Patch 到历史记录

        Args:
            instance_name: 实例 ID
            patch: Patch 数据

        Returns:
            Patch ID
        """
        if instance_name not in self._history:
            self._history[instance_name] = []
        if instance_name not in self._counters:
            self._counters[instance_name] = 0

        self._counters[instance_name] += 1
        patch_record = {
            "id": self._counters[instance_name],
            "timestamp": datetime.now().isoformat(),
            "patch": patch
        }

        # 使用 cast 显式转换类型，解决 dict 类型参数的不变性问题
        self._history[instance_name].append(cast("dict[str, object]", patch_record))
        return self._counters[instance_name]

    def get_all(self, instance_name: str) -> "list[dict[str, object]]":
        """获取实例的所有 Patch 历史

        Args:
            instance_name: 实例 ID

        Returns:
            Patch 历史记录列表
        """
        return self._history.get(instance_name, [])

    def get_by_id(self, instance_name: str, patch_id: int) -> "dict[str, object] | None":
        """根据 ID 获取特定 Patch

        Args:
            instance_name: 实例 ID
            patch_id: Patch ID

        Returns:
            Patch 记录，如果不存在返回 None
        """
        patches = self.get_all(instance_name)
        return next((p for p in patches if p["id"] == patch_id), None)

    def clear(self, instance_name: str) -> None:
        """清空实例的 Patch 历史

        Args:
            instance_name: 实例 ID
        """
        if instance_name in self._history:
            self._history[instance_name] = []
        if instance_name in self._counters:
            self._counters[instance_name] = 0

    def count(self, instance_name: str) -> int:
        """获取实例的 Patch 数量

        Args:
            instance_name: 实例 ID

        Returns:
            Patch 数量
        """
        return len(self._history.get(instance_name, []))
