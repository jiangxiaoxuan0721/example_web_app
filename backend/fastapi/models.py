"""FastAPI 数据模型（Pydantic）"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class WizardMode(str, Enum):
    """Wizard 模式"""
    SINGLE = "single"
    BATCH = "batch"


class EventType(str, Enum):
    """事件类型"""
    FIELD_CHANGE = "field_change"
    ACTION_CLICK = "action_click"
    SELECT_MODE = "select_mode"
    CONFIRM_STEP = "confirm_step"


# ==================== 事件模型 ====================

class EventPayload(BaseModel):
    """事件载荷"""
    actionId: Optional[str] = Field(None, description="操作 ID")
    fieldKey: Optional[str] = Field(None, description="字段键")
    value: Optional[Any] = Field(None, description="字段值")
    mode: Optional[str] = Field(None, description="模式")
    stepIndex: Optional[int] = Field(None, description="步骤索引")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="参数")


class UIEvent(BaseModel):
    """UI 事件"""
    type: EventType = Field(..., description="事件类型")
    payload: EventPayload = Field(default_factory=EventPayload, description="事件载荷")
    pageKey: Optional[str] = Field(None, description="页面键")


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
    params: Dict[str, Any] = Field(default_factory=dict, description="参数")
    runtime: Dict[str, Any] = Field(default_factory=dict, description="运行时信息")


class LayoutInfo(BaseModel):
    """布局信息"""
    type: str = Field(default="single", description="布局类型")


class FieldConfig(BaseModel):
    """字段配置"""
    label: str = Field(..., description="标签")
    key: str = Field(..., description="键")
    type: str = Field(..., description="类型")
    rid: Optional[str] = Field(None, description="资源 ID")
    value: Optional[Any] = Field(None, description="值")
    description: Optional[str] = Field(None, description="描述")
    options: Optional[List[Dict[str, str]]] = Field(None, description="选项")


class BlockProps(BaseModel):
    """Block 属性"""
    fields: Optional[List[FieldConfig]] = Field(None, description="字段列表")
    showProgress: Optional[bool] = Field(None, description="是否显示进度")
    showStatus: Optional[bool] = Field(None, description="是否显示状态")
    showImages: Optional[bool] = Field(None, description="是否显示图片")
    showTable: Optional[bool] = Field(None, description="是否显示表格")
    showCountInput: Optional[bool] = Field(None, description="是否显示数量输入")
    showTaskId: Optional[bool] = Field(None, description="是否显示任务 ID")


class Block(BaseModel):
    """Block 配置"""
    id: str = Field(..., description="Block ID")
    type: str = Field(..., description="Block 类型")
    bind: str = Field(default="state.params", description="绑定路径")
    props: Optional[BlockProps] = Field(None, description="Block 属性")


class ActionConfig(BaseModel):
    """操作配置"""
    id: str = Field(..., description="操作 ID")
    label: str = Field(..., description="操作标签")
    style: str = Field(default="secondary", description="操作样式")


class UISchema(BaseModel):
    """UI Schema"""
    meta: MetaInfo = Field(..., description="元数据")
    state: StateInfo = Field(default_factory=StateInfo, description="状态")
    layout: LayoutInfo = Field(default_factory=LayoutInfo, description="布局")
    blocks: List[Block] = Field(default_factory=list, description="Block 列表")
    actions: List[ActionConfig] = Field(default_factory=list, description="操作列表")


# ==================== Patch 模型 ====================

class UIPatch(BaseModel):
    """UI Patch（键为 dot path，值为任意类型）"""
    # 使用 Dict 来表示，键是点路径（如 "state.params.speed"）
    pass


# ==================== 响应模型 ====================

class BaseResponse(BaseModel):
    """基础响应"""
    status: str = Field(..., description="状态")
    message: Optional[str] = Field(None, description="消息")
    error: Optional[str] = Field(None, description="错误信息")


class ConfigResponse(BaseResponse):
    """配置响应"""
    modes: Dict[str, Any] = Field(default_factory=dict, description="模式配置")


class SchemaResponse(BaseResponse):
    """Schema 响应"""
    schema: Optional[UISchema] = Field(None, description="UISchema")


class PatchResponse(BaseResponse):
    """Patch 响应"""
    patch: Dict[str, Any] = Field(default_factory=dict, description="UI Patch")


class EventResponse(BaseResponse):
    """事件处理响应（可能返回 Schema 或 Patch）"""
    schema: Optional[UISchema] = Field(None, description="UISchema")
    patch: Optional[Dict[str, Any]] = Field(None, description="UI Patch")
