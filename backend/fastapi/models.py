"""FastAPI 数据模型（Pydantic）

本文件提供向后兼容的导入接口，实际模型定义已拆分到 models/ 目录中。
为了兼容性，这里重新导出所有模型。

建议新代码直接使用 from backend.fastapi.models import ... 的形式。
"""

# 从 models 包导入所有模型，保持向后兼容
from .models import * 

# 为了兼容性，直接导出
from .models.enums import (
    EventType,
    ActionType,
    HTTPMethod,
    BodyTemplateType,
    FieldType,
    LayoutType,
)
from .models.base import BaseModelWithConfig
from .models.event_models import EventPayload, UIEvent
from .models.patch_models import (
    SchemaPatch
)
from .models.field_models import (
    OptionItem,
    ColumnConfig,
    BaseFieldConfig,
    SelectableFieldConfig,
    ImageFieldConfig,
    TableFieldConfig,
    ComponentFieldConfig,
    FieldConfig,
)
from .models.schema_models import (
    StateInfo,
    LayoutInfo,
    UISchema,
)

from .models.block_models import(
    Block,
    ActionConfig,
)
from .models.response_models import (  # noqa: F401
    BaseResponse,
    ConfigResponse,
    SchemaResponse,
    PatchResponse,
    EventResponse,
    BatchPatchItem,
    BatchPatchRequest,
    BatchPatchResponse,
)

__all__ = [
    # 枚举
    "EventType",
    "ActionType",
    "HTTPMethod",
    "BodyTemplateType",
    "FieldType",
    "LayoutType",
    # 基础模型
    "BaseModelWithConfig",
    # 事件模型
    "EventPayload",
    "UIEvent",
    # Patch 模型
    "SchemaPatch",
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
