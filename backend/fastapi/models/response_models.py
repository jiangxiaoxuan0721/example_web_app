"""响应模型模块

包含基础响应、配置响应、Schema 响应、Patch 响应、事件响应等模型定义
"""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseModelWithConfig
from .schema_models import UISchema
from .patch_models import SchemaPatch

class BaseResponse(BaseModelWithConfig):
    """基础响应"""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    message: Optional[str] = Field(None, description="消息")
    error: Optional[str] = Field(None, description="错误信息")
    code: Optional[int] = Field(None, description="状态码")
    request_id: Optional[str] = Field(None, description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ConfigResponse(BaseResponse):
    """配置响应"""
    modes: dict[str, Any] = Field(default_factory=dict, description="模式配置")
    features: list[str] = Field(default_factory=list, description="支持的特性")


class SchemaResponse(BaseResponse):
    """Schema响应"""
    ui_schema: Optional[UISchema] = Field(None, alias="schema", description="UI Schema")
    partial: bool = Field(default=False, description="是否为部分更新")


class PatchResponse(BaseResponse):
    """Patch响应"""
    patch: dict[str, Any] = Field(default_factory=dict, description="UI Patch")
    affected_paths: list[str] = Field(default_factory=list, description="影响的路径")


class EventResponse(BaseResponse):
    """事件处理响应"""
    ui_schema: Optional[UISchema] = Field(None, alias="schema", description="UI Schema")
    patch: Optional[dict[str, Any]] = Field(None, description="UI Patch")
    redirect: Optional[str] = Field(None, description="重定向URL")
    reload: bool = Field(default=False, description="是否重新加载")


# ==================== 批量操作模型 ====================

class BatchPatchItem(BaseModelWithConfig):
    """批量Patch项"""
    path: str = Field(..., description="路径")
    value: SchemaPatch = Field(..., description="Patch值")


class BatchPatchRequest(BaseModelWithConfig):
    """批量Patch请求"""
    patches: list[BatchPatchItem] = Field(..., min_length=1, description="Patch列表")
    atomic: bool = Field(default=True, description="是否原子操作")


class BatchPatchResponse(BaseResponse):
    """批量Patch响应"""
    results: list[dict[str, Any]] = Field(default_factory=list, description="操作结果")
    succeeded: int = Field(default=0, description="成功数量")
    failed: int = Field(default=0, description="失败数量")
