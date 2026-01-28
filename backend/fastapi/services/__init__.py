"""FastAPI 服务模块"""

from .instance_service import InstanceService
from .patch import apply_patch_to_schema
from .websocket import manager as websocket_manager

__all__ = [
    "InstanceService",
    "apply_patch_to_schema",
    "websocket_manager",
]

# 注意：EventHandler 已被废弃
# 所有 action 处理现在都通过 InstanceService 和 MCP Action Handler 配置实现