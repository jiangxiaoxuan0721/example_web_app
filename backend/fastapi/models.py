"""FastAPI 数据模型（Pydantic）"""

from pydantic import BaseModel, Field
from typing import Any
from enum import Enum


class EventType(str, Enum):
    """事件类型"""
    FIELD_CHANGE = "field_change"
    ACTION_CLICK = "action_click"
    SELECT_MODE = "select_mode"
    CONFIRM_STEP = "confirm_step"


# ==================== 事件模型 ====================

class EventPayload(BaseModel):
    """事件载荷"""
    actionId: str | None = Field(None, description="操作 ID")
    fieldKey: str | None = Field(None, description="字段键")
    value: Any | None = Field(None, description="字段值")
    mode: str | None = Field(None, description="模式")
    stepIndex: int | None = Field(None, description="步骤索引")
    params: dict[str, Any] | None = Field(default_factory=dict, description="参数")


class UIEvent(BaseModel):
    """UI 事件"""
    type: EventType = Field(..., description="事件类型")
    payload: EventPayload = Field(default_factory=lambda: EventPayload(**{}), description="事件载荷")
    pageKey: str | None = Field(None, description="页面键")


# ==================== Schema 模型 ====================

class StepInfo(BaseModel):
    """步骤信息"""
    current: int = Field(..., description="当前步骤（1-based）")
    total: int = Field(..., description="总步骤数")


class MetaInfo(BaseModel):
    """元数据"""
    pageKey: str = Field(..., description="页面键")
    step: StepInfo = Field(..., description="步骤信息")
    status: str = Field(default="idle", description="状态")
    schemaVersion: str = Field(default="1.0", description="Schema 版本")


class StateInfo(BaseModel):
    """状态信息"""
    params: dict[str, Any] = Field(default_factory=dict, description="参数")
    runtime: dict[str, Any] = Field(default_factory=dict, description="运行时信息")


class LayoutInfo(BaseModel):
    """布局信息"""
    type: str = Field(default="single", description="布局类型")


class FieldConfig(BaseModel):
    """字段配置"""
    label: str = Field(..., description="标签")
    key: str = Field(..., description="键")
    type: str = Field(..., description="类型")
    rid: str | None = Field(None, description="资源 ID")
    value: Any | None = Field(None, description="值")
    description: str | None = Field(None, description="描述")
    options: list[dict[str, str]] | None = Field(None, description="选项")
    content_type: str | None = Field(None, description="内容类型（如json）")
    editable: bool | None = Field(True, description="是否可编辑")
    # 图片相关属性
    showFullscreen: bool | None = Field(True, description="是否显示全屏按钮")
    showDownload: bool | None = Field(True, description="是否显示下载按钮")
    imageHeight: str | None = Field("auto", description="图片高度")
    imageFit: str | None = Field("contain", description="图片适应方式")
    lazy: bool | None = Field(None, description="是否懒加载")
    fallback: str | None = Field(None, description="加载失败时的回退内容")
    subtitle: str | None = Field(None, description="子标题")
    # 表格相关属性
    columns: list[dict[str, Any]] | None  = Field(None, description="表格列配置")
    rowKey: str | None = Field("id", description="行唯一标识字段")
    bordered: bool | None = Field(True, description="是否显示边框")
    striped: bool | None = Field(True, description="是否显示斑马纹")
    hover: bool | None = Field(True, description="是否显示悬停效果")
    emptyText: str | None = Field("暂无数据", description="空数据提示文本")
    tableEditable: bool | None = Field(False, description="表格是否可编辑")
    showHeader: bool | None = Field(True, description="是否显示表头")
    showPagination: bool | None = Field(False, description="是否显示分页")
    pageSize: int | None = Field(10, description="每页显示条数")
    maxHeight: str | None = Field(None, description="表格最大高度（如 '400px'）")
    compact: bool | None = Field(False, description="是否紧凑模式")
    # 嵌入渲染相关属性
    targetInstance: str | None = Field(None, description="目标实例ID（用于嵌入渲染）")
    targetBlock: str | None = Field(None, description="目标block ID（用于嵌入渲染）")


class ActionConfig(BaseModel):
    """操作配置"""
    id: str = Field(..., description="操作 ID")
    label: str = Field(..., description="操作标签")
    style: str = Field(default="secondary", description="操作样式")
    action_type: str | None = Field(default="api", description="操作类型：api（默认）/ navigate")
    target_instance: str | None = Field(None, description="目标实例ID（当action_type=navigate时使用）")
    # 通用动作处理器配置
    handler_type: str | None = Field(None, description="处理器类型：set/increment/decrement/toggle/template/custom")
    patches: dict[str, Any] | None = Field(None, description="要应用的 patch 映射（key为路径，value为值或操作对象）")



class BlockProps(BaseModel):
    """Block 属性"""
    fields: list[FieldConfig] | None = Field(None, description="字段列表")
    actions: list[ActionConfig] | None= Field(None, description="Block 级别的操作按钮列表")
    showProgress: bool | None = Field(None, description="是否显示进度")
    showStatus: bool | None = Field(None, description="是否显示状态")
    showImages: bool | None = Field(None, description="是否显示图片")
    showTable: bool | None = Field(None, description="是否显示表格")
    showCountInput: bool | None = Field(None, description="是否显示数量输入")
    showTaskId: bool | None = Field(None, description="是否显示任务 ID")


class Block(BaseModel):
    """Block 配置"""
    id: str = Field(..., description="Block ID")
    type: str = Field(..., description="Block 类型")
    bind: str = Field(default="state.params", description="绑定路径")
    props: BlockProps | None = Field(None, description="Block 属性")
class UISchema(BaseModel):
    """UI Schema"""
    meta: MetaInfo = Field(..., description="元数据")
    state: StateInfo = Field(default_factory=StateInfo, description="状态")
    layout: LayoutInfo = Field(default_factory=LayoutInfo, description="布局")
    blocks: list[Block] = Field(default_factory=list, description="Block 列表")
    actions: list[ActionConfig] = Field(default_factory=list, description="操作列表")


# ==================== Patch 模型 ====================

class UIPatch(BaseModel):
    """UI Patch（键为 dot path，值为任意类型）"""
    # 使用 dict 来表示，键是点路径（如 "state.params.speed"）
    pass


# ==================== 响应模型 ====================

class BaseResponse(BaseModel):
    """基础响应"""
    status: str = Field(..., description="状态")
    message: str | None = Field(None, description="消息")
    error: str | None = Field(None, description="错误信息")


class ConfigResponse(BaseResponse):
    """配置响应"""
    modes: dict[str, Any] = Field(default_factory=dict, description="模式配置")


class SchemaResponse(BaseResponse):
    """Schema 响应"""
    ui_schema: UISchema | None = Field(None, alias="schema", description="UISchema")


class PatchResponse(BaseResponse):
    """Patch 响应"""
    patch: dict[str, Any] = Field(default_factory=dict, description="UI Patch")


class EventResponse(BaseResponse):
    """事件处理响应（可能返回 Schema 或 Patch）"""
    ui_schema: UISchema | None = Field(None, alias="schema", description="UISchema")
    patch: dict[str, Any] | None = Field(None, description="UI Patch")
