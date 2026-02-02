"""Block 配置模型模块

包含 Block、BlockProps、ActionConfig 等 Block 相关模型定义
"""

from typing import Any, Literal
from pydantic import Field

from .base import BaseModelWithConfig
from .enums import ActionType
from .patch_models import SchemaPatch


class ActionConfig(BaseModelWithConfig):
    """操作配置"""
    id: str = Field(..., description="操作ID")
    label: str = Field(..., description="操作标签")
    style: Literal["primary", "secondary", "danger", "warning", "success"] = Field(
        default="secondary",
        description="操作样式"
    )
    action_type: ActionType = Field(default=ActionType.PATCH, alias="action_type", description="操作类型")
    patches: list[SchemaPatch] | None = Field(default_factory=list, description="要应用的patch映射")
    target_instance: str | None = Field(default=None, alias="target_instance", description="目标实例ID")
    disabled: bool = Field(default=False, description="是否禁用")


class BlockProps(BaseModelWithConfig):
    """Block属性"""
    # 使用 Any 而非 FieldConfig 以避免循环导入
    # 运行时通过 Pydantic 的验证器或动态类型检查来确保类型正确
    fields: list[Any] | None = Field(None, description="字段列表")
    actions: list[ActionConfig] | None = Field(None, description="操作按钮列表")

    # Tabs 布局属性
    tabs: list[dict[str, Any]] | None = Field(None, description="标签页配置(tabs布局)")

    # Grid 布局属性
    cols: int | None = Field(None, ge=1, le=12, description="网格列数(grid布局)")
    gap: str | None = Field(None, description="网格间距(grid布局)")

    # Accordion 布局属性
    panels: list[dict[str, Any]] | None = Field(None, description="折叠面板配置(accordion布局)")


class Block(BaseModelWithConfig):
    """Block配置"""
    id: str = Field(..., description="Block ID")
    layout: str = Field(..., description="Block布局类型")
    title: str | None = Field(None, description="标题")
    props: BlockProps | None = Field(None, description="Block属性")


# 解决前向引用问题
_ = BlockProps.model_rebuild()
