"""Patch 相关模型模块

包含直接赋值、操作、外部 API 调用等 Patch 模型定义
"""

from typing import Any, Union, Literal, Optional
import re
from pydantic import BaseModel, Field, field_validator

from .base import BaseModelWithConfig
from .enums import OperationType, HTTPMethod, BodyTemplateType


class DirectValuePatch(BaseModelWithConfig):
    """直接赋值 Patch"""
    mode: Literal["direct"] = "direct"
    value: Any = Field(..., description="要设置的值")


class OperationPatch(BaseModelWithConfig):
    """操作对象 Patch"""
    mode: Literal["operation"] = "operation"
    operation: OperationType = Field(..., description="操作类型")
    params: dict[str, Any] = Field(default_factory=dict, description="操作参数")


class ExternalApiPatch(BaseModelWithConfig):
    """外部 API 调用 Patch"""
    mode: Literal["external"] = "external"
    url: str = Field(..., description="API端点URL（支持模板变量）")
    method: HTTPMethod = Field(default=HTTPMethod.POST, description="HTTP方法")
    headers: dict[str, str] = Field(default_factory=dict, description="请求头")
    body_template: Optional[dict[str, Any]] = Field(None, description="请求体模板")
    body_template_type: BodyTemplateType = Field(default=BodyTemplateType.JSON, description="请求体类型")
    timeout: int = Field(default=30, ge=1, le=300, description="超时时间（秒）")
    response_mappings: dict[str, str] = Field(
        default_factory=dict,
        description="响应映射（JSONPath表达式）"
    )
    error_mapping: dict[str, str] = Field(
        default_factory=dict,
        description="错误响应映射"
    )
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        """验证URL格式"""
        url_pattern = re.compile(
            r'^(https?://)?'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(v):
            raise ValueError("URL格式不正确")
        return v


# Patch 值的类型联合
PatchValue = Union[DirectValuePatch, OperationPatch, ExternalApiPatch, Any]
