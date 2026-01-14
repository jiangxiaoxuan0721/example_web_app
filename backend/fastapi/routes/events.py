"""事件和 Patch API 路由"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from ...core import SchemaManager, PatchHistoryManager
from ..services import apply_patch_to_schema, InstanceService
from ..services.websocket import manager as websocket_manager
router = APIRouter(prefix="/ui", tags=["Events", "Patches"])


# 初始化服务
schema_manager = SchemaManager()
instance_service = InstanceService(schema_manager)
patch_history = PatchHistoryManager()

default_instance_id = "demo"


@router.post("/event")
async def handle_event(event: dict):
    """
    处理前端事件

    接收事件，调用 InstanceService 处理 action
    """
    event_type = event.get("type")
    action_id = event.get("payload", {}).get("actionId")
    instance_id = event.get("pageKey", default_instance_id)
    params = event.get("payload", {}).get("params", {})

    print(f"[Events API] 收到事件: {event_type}, actionId: {action_id}, instanceId: {instance_id}, params: {params}")

    # 处理字段变化事件
    if event_type == "field:change":
        field_key = event.get("payload", {}).get("fieldKey")
        field_value = event.get("payload", {}).get("value")

        if field_key:
            patch = {f"state.params.{field_key}": field_value}
            print(f"[Events API] 字段更新: {field_key} = {field_value}")

            # 保存到历史记录
            patch_id = patch_history.save(instance_id, patch)

            # 应用到 schema
            schema = schema_manager.get(instance_id)
            if schema:
                apply_patch_to_schema(schema, patch)

                # WebSocket 推送
                await websocket_manager.send_patch(instance_id, patch, patch_id)

            return {
                "status": "success",
                "instance_id": instance_id,
                "patch_id": patch_id,
                "patch": {}  # 不返回 patch，避免与 WebSocket 推送重复
            }

    # 处理操作按钮点击事件
    if event_type == "action:click":
        # 先同步前端传来的 params（如果有）
        if params and isinstance(params, dict):
            schema = schema_manager.get(instance_id)
            if schema:
                params_patch = {f"state.params.{k}": v for k, v in params.items()}
                print(f"[Events API] 同步前端 params: {params_patch}")
                apply_patch_to_schema(schema, params_patch)

                # 保存到历史记录并推送
                patch_id = patch_history.save(instance_id, params_patch)
                await websocket_manager.send_patch(instance_id, params_patch, patch_id)

        # 调用 InstanceService 处理 action
        result = instance_service.handle_action(instance_id, action_id, params)

        if result.get("status") == "success" and result.get("patch"):
            patch = result["patch"]

            # 保存到历史记录
            patch_id = patch_history.save(instance_id, patch)

            # WebSocket 推送
            await websocket_manager.send_patch(instance_id, patch, patch_id)

            return {
                "status": "success",
                "instance_id": instance_id,
                "patch_id": patch_id,
                "patch": {}  # 不返回 patch
            }

        return result


@router.get("/patches")
async def get_patches(
    instance_id: Optional[str] = Query(None, alias="instanceId", description="实例 ID")
):
    """
    获取所有 Patch 历史记录
    """
    if not instance_id:
        instance_id = default_instance_id

    patches = patch_history.get(instance_id)

    return {
        "status": "success",
        "instance_id": instance_id,
        "patches": patches
    }


@router.get("/patches/replay/{patch_id}")
async def replay_patch(
    patch_id: int,
    instance_id: Optional[str] = Query(None, alias="instanceId", description="实例 ID")
):
    """
    重放指定 Patch
    """
    if not instance_id:
        instance_id = default_instance_id

    # 找到对应的 Patch
    patches = patch_history.get(instance_id)
    patch_record = next((p for p in patches if p["id"] == patch_id), None)

    if not patch_record:
        raise HTTPException(
            status_code=404,
            detail=f"Patch {patch_id} not found in instance '{instance_id}'"
        )

    print(f"[Events API] 重放 Patch {patch_id} (instance: {instance_id}): {patch_record['patch']}")

    # 应用到当前 Schema
    current_schema = schema_manager.get(instance_id)
    if current_schema:
        apply_patch_to_schema(current_schema, patch_record["patch"])

        # WebSocket 推送
        await websocket_manager.send_patch(instance_id, patch_record["patch"], None)

    return {
        "status": "success",
        "instance_id": instance_id,
        "patch_id": patch_id,
        "patch": patch_record["patch"]
    }


@router.post("/patch")
async def apply_patch_endpoint(request: dict):
    """
    应用 Patch 到 Schema（供 MCP 工具调用）

    支持操作：
    - 创建实例: {"instance_id": "__CREATE__", "new_instance_id": "my_instance", "patches": [...]}
    - 删除实例: {"instance_id": "__DELETE__", "target_instance_id": "my_instance", "patches": []}
    """
    instance_id = request.get("instance_id")
    patches = request.get("patches", [])
    new_instance_id = request.get("new_instance_id")
    target_instance_id = request.get("target_instance_id")

    print(f"[Events API] /ui/patch 收到请求: instance_id={instance_id}, patches={patches}")

    try:
        # Handle Create Instance
        if instance_id == "__CREATE__":
            if not new_instance_id:
                return {
                    "status": "error",
                    "error": "new_instance_id is required when instanceId is '__CREATE__'"
                }

            success, message = instance_service.create_instance(new_instance_id, patches)
            if not success:
                return {
                    "status": "error",
                    "error": message
                }

            return {
                "status": "success",
                "message": message,
                "instance_id": new_instance_id
            }

        # Handle Delete Instance
        if instance_id == "__DELETE__":
            if not target_instance_id:
                return {
                    "status": "error",
                    "error": "target_instance_id is required when instanceId is '__DELETE__'"
                }

            success, message = instance_service.delete_instance(target_instance_id)
            if not success:
                return {
                    "status": "error",
                    "error": message
                }

            return {
                "status": "success",
                "message": message
            }

        # Handle Normal Instance Operations
        if not schema_manager.exists(instance_id):
            return {
                "status": "error",
                "error": f"Instance '{instance_id}' not found",
                "available_instances": schema_manager.list_all()
            }

        current_schema = schema_manager.get(instance_id)
        patch_dict = {}

        # Process patches
        for patch in patches:
            op = patch.get("op")
            path = patch.get("path")
            value = patch.get("value")

            # Convert structured patch operations to dict format
            if op == "set":
                patch_dict[path] = value

        # Apply patches to schema
        if patch_dict:
            apply_patch_to_schema(current_schema, patch_dict)

            # 保存到历史记录
            patch_id = patch_history.save(instance_id, patch_dict)

            # WebSocket push to frontend
            await websocket_manager.send_patch(instance_id, patch_dict, patch_id)

            print(f"[Events API] Patch 应用成功: {patch_dict}")
            return {
                "status": "success",
                "message": "Patch applied successfully",
                "instance_id": instance_id,
                "patches_applied": patches
            }

        return {
            "status": "success",
            "message": "No patches to apply",
            "instance_id": instance_id
        }

    except Exception as e:
        import traceback
        print(f"[Events API] [ERROR] /ui/patch 错误: {e}")
        print(f"[Events API] Traceback:\n{traceback.format_exc()}")
        return {
            "status": "error",
            "error": str(e),
            "detail": traceback.format_exc()
        }
