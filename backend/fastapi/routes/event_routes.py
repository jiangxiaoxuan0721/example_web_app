"""事件相关 API 路由"""

from backend.core import SchemaManager, PatchHistoryManager
from ..services import InstanceService


def register_event_routes(
    app,
    schema_manager: SchemaManager,
    instance_service: InstanceService,
    patch_history: PatchHistoryManager,
    ws_manager,
    default_instance_id: str
):
    """注册事件相关的路由

    Args:
        app: FastAPI 应用实例
        schema_manager: Schema 管理器
        instance_service: 实例服务
        patch_history: Patch 历史管理器
        ws_manager: WebSocket 管理器
        default_instance_id: 默认实例 ID
    """

    @app.post("/ui/event")
    async def handle_event(event: dict):
        """
        处理前端事件
        """
        event_type = event.get("type")
        action_id = event.get("payload", {}).get("actionId")
        instance_id = event.get("pageKey", default_instance_id)
        params = event.get("payload", {}).get("params", {})

        print(f"[EventRoutes] 收到事件: {event_type}, actionId: {action_id}, instanceId: {instance_id}, params={params}")

        # 获取当前实例的 Schema
        schema = schema_manager.get(instance_id)
        if not schema:
            return {
                "status": "error",
                "error": f"实例 '{instance_id}' 不存在"
            }

        # 处理字段变化事件
        if event_type == "field:change":
            field_key = params.get("fieldKey")
            field_value = params.get("value")

            if field_key:
                patch = {f"state.params.{field_key}": field_value}

                # 保存到历史记录
                patch_id = patch_history.save(instance_id, patch)

                # 应用到 schema
                from ..services.patch import apply_patch_to_schema
                apply_patch_to_schema(schema, patch)

                # WebSocket 推送
                await ws_manager.send_patch(instance_id, patch, patch_id)

                return {
                    "status": "success",
                    "instance_id": instance_id,
                    "patch_id": patch_id,
                    "patch": {}
                }

        # 处理操作按钮点击事件
        if event_type == "action:click":
            # 先同步前端传来的 params（如果有）
            if params and isinstance(params, dict):
                from ..services.patch import apply_patch_to_schema
                params_patch = {f"state.params.{k}": v for k, v in params.items()}
                print(f"[EventRoutes] 同步前端 params: {params_patch}")
                apply_patch_to_schema(schema, params_patch)

                # 保存到历史记录并推送
                patch_id = patch_history.save(instance_id, params_patch)
                await ws_manager.send_patch(instance_id, params_patch, patch_id)

            # 调用 InstanceService 处理 action
            print(f"[EventRoutes] 调用 instance_service.handle_action")
            result = instance_service.handle_action(instance_id, action_id, params)
            print(f"[EventRoutes] instance_service.handle_action 返回: {result}")

            if result.get("status") == "success" and result.get("patch"):
                patch = result["patch"]

                # 保存到历史记录
                patch_id = patch_history.save(instance_id, patch)

                # WebSocket 推送
                await ws_manager.send_patch(instance_id, patch, patch_id)

                return {
                    "status": "success",
                    "instance_id": instance_id,
                    "patch_id": patch_id,
                    "patch": {}
                }

            return result

        return {
            "status": "success",
            "instance_id": instance_id,
            "patch_id": None,
            "patch": {}
        }