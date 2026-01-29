"""Schema 相关模型模块

包含步骤信息、元数据、状态、布局、Block、Action、UISchema 等模型定义
"""

from typing import Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from .base import BaseModelWithConfig
from .enums import ActionType, HandlerType, LayoutType, StatusType
from .field_models import FieldConfig
from .patch_models import PatchValue


class StepInfo(BaseModelWithConfig):
    """步骤信息"""
    current: int = Field(..., ge=1, description="当前步骤（1-based）")
    total: int = Field(..., ge=1, description="总步骤数")
    
    @field_validator("current")
    @classmethod
    def validate_current_step(cls, v, info):
        """验证当前步骤不超过总步骤数"""
        if "total" in info.data and v > info.data["total"]:
            raise ValueError("当前步骤不能超过总步骤数")
        return v


class MetaInfo(BaseModelWithConfig):
    """元数据"""
    page_key: str = Field(..., alias="pageKey", description="页面键")
    step: StepInfo = Field(..., description="步骤信息")
    status: StatusType = Field(default=StatusType.IDLE, description="状态")
    schema_version: str = Field(default="1.0.0", alias="schemaVersion", description="Schema版本")
    title: Optional[str] = Field(None, description="页面标题")
    description: Optional[str] = Field(None, description="页面描述")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class StateInfo(BaseModelWithConfig):
    """状态信息"""
    params: dict[str, Any] = Field(default_factory=dict, description="参数")
    runtime: dict[str, Any] = Field(default_factory=dict, description="运行时信息")
    errors: dict[str, str] = Field(default_factory=dict, description="错误信息")
    warnings: dict[str, str] = Field(default_factory=dict, description="警告信息")


class LayoutInfo(BaseModelWithConfig):
    """布局信息"""
    type: LayoutType = Field(default=LayoutType.SINGLE, description="布局类型")
    columns: int | None = Field(default=None, ge=1, le=12, description="列数(仅grid布局)")
    gap: str | None = Field(default=None, description="间距")
    responsive: bool = Field(default=True, description="是否响应式")


class BlockProps(BaseModelWithConfig):
    """Block属性"""
    fields: Optional[list[FieldConfig]] = Field(None, description="字段列表")
    actions: Optional[list["ActionConfig"]] = Field(None, description="操作按钮列表")
    show_progress: Optional[bool] = Field(None, alias="showProgress", description="显示进度")
    show_status: Optional[bool] = Field(None, alias="showStatus", description="显示状态")
    show_images: Optional[bool] = Field(None, alias="showImages", description="显示图片")
    show_table: Optional[bool] = Field(None, alias="showTable", description="显示表格")
    show_count_input: Optional[bool] = Field(None, alias="showCountInput", description="显示数量输入")
    show_task_id: Optional[bool] = Field(None, alias="showTaskId", description="显示任务ID")
    title: Optional[str] = Field(None, description="区块标题")
    description: Optional[str] = Field(None, description="区块描述")
    collapsible: bool = Field(default=False, description="是否可折叠")
    collapsed: bool = Field(default=False, description="默认折叠")

    # 布局类型相关属性
    tabs: Optional[list[dict[str, Any]]] = Field(None, description="标签页配置(tabs布局)")
    cols: Optional[int] = Field(None, ge=1, le=12, description="网格列数(grid布局)")
    gap: Optional[str] = Field(None, description="网格间距(grid布局)")
    panels: Optional[list[dict[str, Any]]] = Field(None, description="折叠面板配置(accordion布局)")


class Block(BaseModelWithConfig):
    """Block配置"""
    id: str = Field(..., description="Block ID")
    type: str = Field(..., description="Block类型")
    bind: str = Field(default="state.params", description="绑定路径")
    props: Optional[BlockProps] = Field(None, description="Block属性")
    order: int = Field(default=0, description="显示顺序")
    visible: bool = Field(default=True, description="是否可见")


class ActionConfig(BaseModelWithConfig):
    """操作配置"""
    id: str = Field(..., description="操作ID")
    label: str = Field(..., description="操作标签")
    style: Literal["primary", "secondary", "danger", "warning", "success"] = Field(
        default="secondary",
        description="操作样式"
    )
    action_type: ActionType = Field(default=ActionType.API, alias="action_type", description="操作类型")
    target_instance: Optional[str] = Field(None, alias="target_instance", description="目标实例ID")
    handler_type: HandlerType = Field(default=HandlerType.SET, alias="handler_type", description="处理器类型")
    patches: Optional[dict[str, PatchValue]] = Field(None, description="要应用的patch映射")
    icon: Optional[str] = Field(None, description="图标名称")
    disabled: bool = Field(default=False, description="是否禁用")
    loading: bool = Field(default=False, description="加载状态")
    confirm_message: Optional[str] = Field(None, description="确认提示信息")
    tooltip: Optional[str] = Field(None, description="工具提示")


# 解决前向引用问题
BlockProps.model_rebuild()


class UISchema(BaseModelWithConfig):
    """UI Schema"""
    meta: MetaInfo = Field(..., description="元数据")
    state: StateInfo = Field(default_factory=StateInfo, description="状态")
    layout: LayoutInfo = Field(default_factory=lambda: LayoutInfo(), description="布局")
    blocks: list[Block] = Field(default_factory=list, description="Block列表")
    actions: list[ActionConfig] = Field(default_factory=list, description="操作列表")

    @field_validator("blocks")
    @classmethod
    def sort_blocks(cls, v):
        """按order字段排序blocks"""
        return sorted(v, key=lambda x: x.order)
