"""Schema 相关 API 路由"""

from backend.fastapi.models.schema_models import UISchema
from datetime import datetime
from fastapi import FastAPI, Query
from typing import Any
from ...core.manager import SchemaManager
from backend.fastapi.services.websocket.handlers.manager import WebSocketManager


def register_schema_routes(app:FastAPI, schema_manager: SchemaManager, default_instance_name: str, ws_manager:WebSocketManager | None = None) -> None:
    """注册 Schema 相关的路由

    Args:
        app: FastAPI 应用实例
        schema_manager: Schema 管理器
        default_instance_name: 默认实例 ID
        ws_manager: WebSocket管理器实例（可选）
    """

    @app.get("/ui/schema")
    async def get_schema(instance_name: str | None = Query(None, alias="instanceId")):
        """
        获取当前 Schema

        支持多实例：
        - /ui/schema              -> 返回默认实例 (demo)
        - /ui/schema?instanceId=counter -> 返回 counter 实例
        - /ui/schema?instanceId=form    -> 返回 form 实例
        """
        print(f"[SchemaRoutes] get_schema 收到 instance_name: '{instance_name}'")

        # 如果没有指定 instanceId，使用默认值
        if not instance_name:
            instance_name = default_instance_name
            print(f"[SchemaRoutes] 使用默认实例: '{instance_name}'")

        # 查找实例
        schema: UISchema | None = schema_manager.get(instance_name)

        if not schema:
            print(f"[SchemaRoutes] 实例 '{instance_name}' 不存在")
            return {
                "status": "error",
                "error": f"实例 '{instance_name}' 不存在",
                "available_instances": schema_manager.list_all()
            }

        print(f"[SchemaRoutes] 找到实例 '{instance_name}'")

        # 动态更新 runtime.timestamp 为当前时间
        if schema.state:
            schema.state.runtime["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[SchemaRoutes] 已更新 runtime.timestamp 为当前时间")

        # 确保字段和 state.params 的一致性
        # 1. 如果字段有 value 但 params 中没有，初始化它
        # 2. 如果 params 中有值但字段没有 value，反向同步
        for block in schema.blocks:
            if block.props and block.props.fields:
                for field in block.props.fields:
                    field_key = getattr(field, 'key', None)
                    if not field_key:
                        continue

                    field_value = getattr(field, 'value', None)

                    # 情况1：字段有 value 但 params 中没有，初始化它
                    if field_key not in schema.state.params and field_value is not None:
                        schema.state.params[field_key] = field_value
                        print(f"[SchemaRoutes] 同步字段值到 params: {field_key} = {field_value}")

                    # 情况2：params 中有值，但字段 value 是 None 或空，可以选择反向同步
                    # 注意：这里我们只记录日志，不修改字段定义
                    # 因为字段定义应该保持原始的默认值，而实际值存储在 state.params 中
                    if field_key in schema.state.params:
                        param_value = schema.state.params[field_key]
                        if param_value != field_value:
                            print(f"[SchemaRoutes] 字段 {field_key}: field.value={field_value}, state.params.{field_key}={param_value}")

        dumped_schema: dict[str, Any] = schema.model_dump(by_alias=True)
        # 调试：检查 columns 的 renderType 字段
        if dumped_schema.get('blocks'):
            first_block = dumped_schema['blocks'][0]
            if 'props' in first_block and 'fields' in first_block['props']:
                first_field = first_block['props']['fields'][0]
                if 'columns' in first_field:
                    print(f"[SchemaRoutes] columns 数据: {first_field['columns'][2]}")  # 打印第3列（avatar）

        return {
            "status": "success",
            "instance_name": instance_name,
            "schema": dumped_schema
        }

    @app.get("/ui/instances")
    async def list_instances():
        """列出所有可用的实例"""
        instances_info = schema_manager.get_all_info()

        return {
            "status": "success",
            "instances": instances_info,
            "total": len(instances_info)
        }

    @app.post("/ui/switch")
    async def switch_ui(request: dict[Any, Any]):
        """切换到指定实例或实例内的指定block"""
        instance_name = request.get("instance_name")
        block_id = request.get("block_id")

        # 至少需要提供一个参数
        if not instance_name and not block_id:
            return {
                "status": "error",
                "error": "缺少参数，需要提供 instance_name 或 block_id"
            }

        # 如果提供了 instance_name，切换实例
        if instance_name:
            # 检查实例是否存在
            schema: UISchema | None = schema_manager.get(instance_name)
            if not schema:
                return {
                    "status": "error",
                    "error": f"实例 '{instance_name}' 不存在",
                    "available_instances": schema_manager.list_all()
                }

            print(f"[SchemaRoutes] 切换实例: '{instance_name}'")

            # 如果WebSocket管理器可用，通知前端切换到指定实例
            if ws_manager:
                _ = await ws_manager.broadcast(message={
                    "type": "switch_instance",
                    "instance_name": instance_name
                })
                print(f"[SchemaRoutes] 已通知前端切换到实例: '{instance_name}'")

        # 如果提供了 block_id，切换到指定block
        if block_id:
            print(f"[SchemaRoutes] 切换到block: '{block_id}'")

            # 验证 block_id 是否存在
            # 如果没有指定 instance_name，使用默认实例或当前实例
            target_instance_name = instance_name or default_instance_name
            target_schema: UISchema | None = schema_manager.get(target_instance_name)

            if not target_schema:
                return {
                    "status": "error",
                    "error": f"无法验证 block_id：实例 '{target_instance_name}' 不存在"
                }

            # 检查 block 是否存在
            block_ids = [block.id for block in target_schema.blocks if hasattr(block, 'id')]
            if block_id not in block_ids:
                return {
                    "status": "error",
                    "error": f"block_id '{block_id}' 在实例 '{target_instance_name}' 中不存在",
                    "available_blocks": block_ids
                }

            # 如果WebSocket管理器可用，通知前端切换到指定block
            if ws_manager:
                _ = await ws_manager.broadcast(message={
                    "type": "highlight_block",
                    "block_id": block_id
                })
                print(f"[SchemaRoutes] 已通知前端切换到block: '{block_id}'")

        return {
            "status": "success",
            "message": f"已切换{'到实例' + f" '{instance_name}'" if instance_name else ''}{'，' if instance_name and block_id else ''}{'切换到block' + f" '{block_id}'" if block_id else ''}",
            "instance_name": instance_name,
            "block_id": block_id
        }
