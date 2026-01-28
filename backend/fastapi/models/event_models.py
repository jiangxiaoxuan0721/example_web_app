"""事件相关模型模块

包含事件载荷、UI 事件等模型定义
"""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from .base import BaseModelWithConfig
from .enums import EventType


class EventPayload(BaseModelWithConfig):
    """事件载荷"""
    action_id: Optional[str] = Field(None, alias="actionId", description="操作ID")
    field_key: Optional[str] = Field(None, alias="fieldKey", description="字段键")
    value: Optional[Any] = Field(None, description="字段值")
    step_index: Optional[int] = Field(None, alias="stepIndex", description="步骤索引")
    params: dict[str, Any] = Field(default_factory=dict, description="参数")
    
    @field_validator("step_index")
    @classmethod
    def validate_step_index(cls, v):
        """验证步骤索引"""
        if v is not None and v < 0:
            raise ValueError("step_index 必须大于等于 0")
        return v


class UIEvent(BaseModelWithConfig):
    """UI事件"""
    type: EventType = Field(..., description="事件类型")
    payload: Optional[EventPayload] = Field(None, description="事件载荷")
    page_key: Optional[str] = Field(None, alias="pageKey", description="页面键")
    timestamp: datetime = Field(default_factory=datetime.now, description="事件时间戳")
