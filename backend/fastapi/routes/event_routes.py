"""事件相关 API 路由"""

from backend.core import SchemaManager, PatchHistoryManager
from ..services import EventHandler


def register_event_routes(
    app,
    schema_manager: SchemaManager,
    event_handler: EventHandler,
    patch_history: PatchHistoryManager,
    ws_manager,
    default_instance_id: str
):
    """注册事件相关的路由

    Args:
        app: FastAPI 应用实例
        schema_manager: Schema 管理器
        event_handler: 事件处理器
        patch_history: Patch 历史管理器
        ws_manager: WebSocket 管理器
        default_instance_id: 默认实例 ID
    """

    @app.post("/ui/event")
    async def handle_event(event: dict):
        """
        处理前端事件
        Step 3: 接收事件，直接返回 Patch
        """
        event_type = event.get("type")
        action_id = event.get("payload", {}).get("actionId")
        instance_id = event.get("pageKey", default_instance_id)
        params = event.get("payload", {}).get("params", {})

        print(f"[EventRoutes] 收到事件: {event_type}, actionId: {action_id}, instanceId: {instance_id}")

        # 获取当前实例的 Schema
        schema = schema_manager.get(instance_id)
        if not schema:
            return {
                "status": "error",
                "error": f"实例 '{instance_id}' 不存在"
            }

        # 处理事件并生成 Patch
        patch = await event_handler.handle_event(
            event_type, action_id, instance_id, params, schema
        )

        if patch:
            patch_id = patch_history.save(instance_id, patch)

            # WebSocket 推送 Patch 到所有连接的客户端
            await ws_manager.send_patch(instance_id, patch, patch_id)

            # HTTP 响应不返回 patch，避免重复更新
            return {
                "status": "success",
                "instance_id": instance_id,
                "patch_id": patch_id,
                "patch": {}
            }

        return {
            "status": "success",
            "instance_id": instance_id,
            "patch_id": None,
            "patch": {}
        }