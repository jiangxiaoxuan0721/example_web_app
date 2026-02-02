"""Schema 相关模型模块
包含步骤信息、元数据、状态、布局、UISchema 等模型定义
"""

from typing import Any
from pydantic import Field

from .base import BaseModelWithConfig
from .enums import LayoutType
from .block_models import Block, ActionConfig


class StateInfo(BaseModelWithConfig):
    """状态信息"""
    params: dict[str, Any] = Field(default_factory=dict, description="参数")
    runtime: dict[str, Any] = Field(default_factory=dict, description="运行时信息")


class LayoutInfo(BaseModelWithConfig):
    """布局信息"""
    type: LayoutType = Field(default=LayoutType.SINGLE, description="布局类型")
    columns: int | None = Field(default=None, ge=1, le=12, description="列数(仅grid布局)")
    gap: str | None = Field(default=None, description="间距")


class UISchema(BaseModelWithConfig):
    """UI Schema"""
    page_key: str = Field(default=..., description="页面键")
    state: StateInfo = Field(default_factory=StateInfo, description="状态")
    layout: LayoutInfo = Field(default_factory=lambda: LayoutInfo(), description="布局")
    blocks: list[Block] = Field(default_factory=list, description="Block列表")
    actions: list[ActionConfig] = Field(default_factory=list, description="操作列表")
