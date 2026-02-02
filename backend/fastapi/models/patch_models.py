"""Patch 相关模型模块

统一 Patch 范式 - 所有 patch 使用相同的格式（op/path/value）

支持的操作类型：
- set: 设置值（原有）
- add: 添加元素到数组（原有）
- remove: 删除元素（原有）
- append_to_list: 追加元素到列表末尾
- prepend_to_list: 在列表开头插入元素
- update_list_item: 更新列表中的某个元素
- remove_last: 删除列表最后一项
- merge: 合并对象
- increment: 增量更新
- decrement: 减量更新
- toggle: 切换布尔值
"""

from pydantic import Field
from .enums import PatchOperationType
from .base import BaseModelWithConfig


class SchemaPatch(BaseModelWithConfig):
    """统一 Patch 范式

    所有 patch 使用相同的格式，无论是全局 patch 还是 action patch

    格式：
    {
        "op": "set" | "add" | "remove" | "append_to_list" | "prepend_to_list" | "update_list_item" | "remove_last" | "merge" | "increment" | "decrement" | "toggle",
        "path": "state.params.xxx",
        "value": any  # 根据不同 op，value 的含义不同
    }

    操作说明：
    - set: 直接设置值
    - add: 添加到数组（原有语义，用于 schema 结构变更）
    - remove: 从数组删除（原有语义，用于 schema 结构变更）
    - append_to_list: 追加元素到列表末尾（用于数据操作）
    - prepend_to_list: 在列表开头插入元素（用于数据操作）
    - update_list_item: 更新列表指定索引的元素（用于数据操作）
    - remove_last: 删除列表最后一项（用于数据操作）
    - merge: 合并对象到目标路径（用于数据操作）
    - increment: 数字值增加（value 为增量）
    - decrement: 数字值减少（value 为减量）
    - toggle: 切换布尔值（value 可选，默认切换）
    """
    op: PatchOperationType = Field(..., description="操作类型")
    path: str = Field(..., description="目标路径")
    value: object = Field(default=None, description="操作值（根据 op 类型不同含义不同）")

    # 用于 update_list_item 的可选参数
    index: int | None = Field(default=None, description="目标索引（仅 update_list_item 使用）")
