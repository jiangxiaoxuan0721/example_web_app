"""FastAPI 数据模型包

本包包含所有 Pydantic 模型定义，按功能模块拆分为多个文件：
- enums: 枚举定义
- base: 基础模型和通用配置
- event_models: 事件相关模型
- patch_models: Patch 相关模型
- field_models: 字段配置模型
- schema_models: Schema 相关模型
- response_models: 响应模型
"""

# 导出所有模型，保持向后兼容
from .enums import *
from .base import BaseModelWithConfig
from .event_models import EventPayload, UIEvent
from .patch_models import (
    DirectValuePatch,
    OperationPatch,
    ExternalApiPatch,
    PatchValue
)
from .field_models import (
    OptionItem,
    ColumnConfig,
    BaseFieldConfig,
    SelectableFieldConfig,
    ImageFieldConfig,
    TableFieldConfig,
    ComponentFieldConfig,
    FieldConfig
)
from .schema_models import (
    StepInfo,
    MetaInfo,
    StateInfo,
    LayoutInfo,
    BlockProps,
    Block,
    ActionConfig,
    UISchema
)
from .response_models import (
    BaseResponse,
    ConfigResponse,
    SchemaResponse,
    PatchResponse,
    EventResponse,
    BatchPatchItem,
    BatchPatchRequest,
    BatchPatchResponse
)

__all__ = [
    # 枚举
    "EventType",
    "HandlerType",
    "ActionType",
    "OperationType",
    "HTTPMethod",
    "BodyTemplateType",
    "FieldType",
    "LayoutType",
    "StatusType",
    # 基础模型
    "BaseModelWithConfig",
    # 事件模型
    "EventPayload",
    "UIEvent",
    # Patch 模型
    "DirectValuePatch",
    "OperationPatch",
    "ExternalApiPatch",
    "PatchValue",
    # 字段模型
    "OptionItem",
    "ColumnConfig",
    "BaseFieldConfig",
    "SelectableFieldConfig",
    "ImageFieldConfig",
    "TableFieldConfig",
    "ComponentFieldConfig",
    "FieldConfig",
    # Schema 模型
    "StepInfo",
    "MetaInfo",
    "StateInfo",
    "LayoutInfo",
    "BlockProps",
    "Block",
    "ActionConfig",
    "UISchema",
    # 响应模型
    "BaseResponse",
    "ConfigResponse",
    "SchemaResponse",
    "PatchResponse",
    "EventResponse",
    "BatchPatchItem",
    "BatchPatchRequest",
    "BatchPatchResponse",
]
