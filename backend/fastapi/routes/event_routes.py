"""事件相关 API 路由"""

from backend.fastapi.models.schema_models import UISchema
from typing import Any
from fastapi import FastAPI
from backend.fastapi.services.websocket.handlers.manager import WebSocketManager
from backend.core import SchemaManager, PatchHistoryManager
from ..services import InstanceService,apply_patch_to_schema

def register_event_routes(
    app: FastAPI,
    schema_manager: SchemaManager,
    instance_service: InstanceService,
    patch_history: PatchHistoryManager,
    ws_manager: WebSocketManager,
    default_instance_name: str
):
    """注册事件相关的路由

    Args:
        app: FastAPI 应用实例
        schema_manager: Schema 管理器
        instance_service: 实例服务
        patch_history: Patch 历史管理器
        ws_manager: WebSocket 管理器
        default_instance_name: 默认实例 ID
    """

    @app.post("/ui/event")
    async def handle_event(event: dict[Any, Any]) -> dict[str, str] | dict[str, str | Any | int | dict[Any, Any]] | dict[str, Any] | dict[str, str | Any | dict[Any, Any] | None]:
        """
        处理前端事件
        """
        event_type = event.get("type")
        payload = event.get("payload", {})
        action_id = payload.get("actionId")
        instance_name = event.get("pageKey", default_instance_name)
        params = payload.get("params", {})
        block_id = payload.get("blockId")  # 接收 blockId

        print(f"[EventRoutes] 收到事件: {event_type}, actionId: {action_id}, instanceId: {instance_name}, params={params}, blockId={block_id}, payload={payload}")

        # 获取当前实例的 Schema
        schema: UISchema | None = schema_manager.get(instance_name)
        if not schema:
            return {
                "status": "error",
                "error": f"实例 '{instance_name}' 不存在"
            }

        # 处理字段变化事件
        if event_type == "field:change":
            # field:change 事件的 payload 直接包含 fieldKey 和 value
            field_key = payload.get("fieldKey")
            field_value = payload.get("value")

            if field_key:
                patch = {f"state.params.{field_key}": field_value}

                # 保存到历史记录
                patch_id = patch_history.save(instance_name, patch)
                apply_patch_to_schema(schema, patch)

                # WebSocket 推送
                _ = await ws_manager.send_patch(instance_name, patch, patch_id)

                return {
                    "status": "success",
                    "instance_name": instance_name,
                    "patch_id": patch_id,
                    "patch": {}
                }

        # 处理操作按钮点击事件
        if event_type == "action:click":
            # 调用 InstanceService 处理 action
            # 注意：不再在这里同步前端传来的 params，让 InstanceService 来处理
            print(f"[EventRoutes] 调用 instance_service.handle_action")
            result = instance_service.handle_action(instance_name, action_id, params, block_id)
            print(f"[EventRoutes] instance_service.handle_action 返回: {result}")

            if result.get("status") == "success" and result.get("patch"):
                patch = result["patch"]

                # 注意：schema 已在 handle_action 中通过 apply_patch_to_schema 更新
                # 由于 schema 是引用类型，schema_manager._instances[instance_name] 中的对象已被修改
                # 因此不需要再调用 schema_manager.set()

                # 保存到历史记录
                patch_id = patch_history.save(instance_name, patch)

                # WebSocket 推送（此时 schema.state.runtime 已更新）
                _ = await ws_manager.send_patch(instance_name, patch, patch_id)

                return {
                    "status": "success",
                    "instance_name": instance_name,
                    "patch_id": patch_id,
                    "patch": {}
                }

            return result

        # 处理表格内按钮点击事件
        if event_type == "table:button:click":
            button_id = params.get("buttonId")
            button_action_id = params.get("actionId") or params.get("_actionId")
            table_field_key = params.get("fieldKey")

            print(f"[EventRoutes] 处理 table:button:click: button_id={button_id}, actionId={button_action_id}, fieldKey={table_field_key}, params={params}")

            # 调用 InstanceService 处理表格按钮（复用 action 处理逻辑）
            result = instance_service.handle_table_button(
                instance_name,
                button_id,
                button_action_id,
                params,
                block_id,
                table_field_key
            )
            print(f"[EventRoutes] instance_service.handle_table_button 返回: {result}")

            if result.get("status") == "success" and result.get("patch"):
                patch = result["patch"]

                # 注意：schema 已在 handle_table_button 中通过 apply_patch_to_schema 更新
                # 保存到历史记录
                patch_id = patch_history.save(instance_name, patch)

                # WebSocket 推送
                await ws_manager.send_patch(instance_name, patch, patch_id)

                return {
                    "status": "success",
                    "instance_name": instance_name,
                    "patch_id": patch_id,
                    "patch": {},
                    "message": result.get("message"),
                    "navigate_to": result.get("navigate_to")
                }

            # 如果有错误信息，也返回
            if result.get("error"):
                return {
                    "status": "error",
                    "error": result.get("error")
                }

            return result

        return {
            "status": "success",
            "instance_name": instance_name,
            "patch_id": None,
            "patch": {}
        }
