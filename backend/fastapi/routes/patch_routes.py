"""Patch 相关 API 路由"""

from fastapi import Query
from typing import Optional
from ...core.history import PatchHistoryManager
from ...core.manager import SchemaManager
from ..services.patch import apply_patch_to_schema
from ..models import (
    UISchema, MetaInfo, StateInfo, LayoutInfo,
    Block, BlockProps, FieldConfig, ActionConfig, StepInfo
)


def register_patch_routes(
    app,
    schema_manager: SchemaManager,
    patch_history: PatchHistoryManager,
    ws_manager
):
    """注册 Patch 相关的路由

    Args:
        app: FastAPI 应用实例
        schema_manager: Schema 管理器
        patch_history: Patch 历史管理器
        ws_manager: WebSocket 管理器
    """

    @app.post("/ui/patch")
    async def apply_patch_endpoint(request: dict):
        """
        应用 Patch 到 Schema（供 MCP 工具调用）

        支持操作：
        - 更新状态: {"instance_id": "counter", "patches": [{"op": "set", "path": "state.params.count", "value": 42}]}
        - 创建实例: {"instance_id": "__CREATE__", "new_instance_id": "my_instance", "patches": [...]}
        - 删除实例: {"instance_id": "__DELETE__", "target_instance_id": "my_instance", "patches": []}
        """
        instance_id = request.get("instance_id")
        patches = request.get("patches", [])
        new_instance_id = request.get("new_instance_id")
        target_instance_id = request.get("target_instance_id")

        print(f"[PatchRoutes] /ui/patch 收到请求: instance_id={instance_id}")

        try:
            # Handle Create Instance
            if instance_id == "__CREATE__":
                if not new_instance_id:
                    return {
                        "status": "error",
                        "error": "new_instance_id is required when instanceId is '__CREATE__'"
                    }

                if schema_manager.exists(new_instance_id):
                    return {
                        "status": "error",
                        "error": f"Instance '{new_instance_id}' already exists"
                    }

                # Apply patches to create instance structure
                new_schema = None
                for patch in patches:
                    op = patch.get("op")
                    path = patch.get("path")
                    value = patch.get("value")

                    if op != "set":
                        continue

                    if path == "meta":
                        meta_data = value
                        new_schema = UISchema(
                            meta=MetaInfo(
                                pageKey=meta_data.get("pageKey", new_instance_id),
                                step=StepInfo(**meta_data.get("step", {"current": 1, "total": 1})),
                                status=meta_data.get("status", "idle")
                            ),
                            state=StateInfo(params={}, runtime={}),
                            layout=LayoutInfo(type="single"),
                            blocks=[],
                            actions=[]
                        )
                    elif path == "state" and new_schema:
                        state_data = value
                        new_schema.state = StateInfo(
                            params=state_data.get("params", {}),
                            runtime=state_data.get("runtime", {})
                        )
                    elif path == "blocks" and new_schema:
                        # Convert dict list to Block objects
                        blocks_data = value or []
                        converted_blocks = []
                        for block in blocks_data:
                            # Create a copy to avoid modifying original
                            block_copy = dict(block)

                            # Convert fields in props if present
                            if 'props' in block_copy and block_copy.get('props') is not None:
                                props_copy = dict(block_copy.get('props', {}))
                                if 'fields' in props_copy and props_copy.get('fields') is not None:
                                    fields_data = props_copy.get('fields', []) or []
                                    converted_fields = [FieldConfig(**field) for field in fields_data]
                                    props_copy['fields'] = converted_fields
                                    block_copy['props'] = props_copy
                            converted_blocks.append(Block(**block_copy))
                        new_schema.blocks = converted_blocks
                    elif path == "actions" and new_schema:
                        # Convert dict list to ActionConfig objects
                        actions_data = value or []
                        new_schema.actions = [ActionConfig(**action) for action in actions_data]

                if new_schema:
                    schema_manager.set(new_instance_id, new_schema)
                    print(f"[PatchRoutes] 实例 '{new_instance_id}' 创建成功")
                    return {
                        "status": "success",
                        "message": f"Instance '{new_instance_id}' created successfully",
                        "instance_id": new_instance_id
                    }

                return {
                    "status": "error",
                    "error": "Failed to create instance: Invalid patches"
                }

            # Handle Delete Instance
            if instance_id == "__DELETE__":
                if not target_instance_id:
                    return {
                        "status": "error",
                        "error": "target_instance_id is required when instanceId is '__DELETE__'"
                    }

                if not schema_manager.exists(target_instance_id):
                    return {
                        "status": "error",
                        "error": f"Instance '{target_instance_id}' not found"
                    }

                schema_manager.delete(target_instance_id)
                print(f"[PatchRoutes] 实例 '{target_instance_id}' 删除成功")
                return {
                    "status": "success",
                    "message": f"Instance '{target_instance_id}' deleted successfully"
                }

            # Handle Normal Instance Operations
            schema = schema_manager.get(instance_id)
            if not schema:
                return {
                    "status": "error",
                    "error": f"Instance '{instance_id}' not found",
                    "available_instances": schema_manager.list_all()
                }

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
                apply_patch_to_schema(schema, patch_dict)

                # 保存到历史记录
                patch_history.save(instance_id, patch_dict)

                # WebSocket push to frontend
                await ws_manager.send_patch(instance_id, patch_dict, None)

                print(f"[PatchRoutes] Patch 应用成功: {patch_dict}")
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
            print(f"[PatchRoutes] [ERROR] /ui/patch 错误: {e}")
            print(f"[PatchRoutes] Traceback:\n{traceback.format_exc()}")
            return {
                "status": "error",
                "error": str(e),
                "detail": traceback.format_exc()
            }

    @app.get("/ui/patches")
    async def get_patches(instance_id: Optional[str] = Query(None, alias="instanceId")):
        """
        获取所有 Patch 历史记录
        支持 Patch 重放

        - /ui/patches              -> 返回默认实例的历史
        - /ui/patches?instanceId=xxx -> 返回指定实例的历史
        """
        if not instance_id:
            instance_id = "demo"

        patches = patch_history.get_all(instance_id)

        return {
            "status": "success",
            "instance_id": instance_id,
            "patches": patches
        }

    @app.get("/ui/patches/replay/{patch_id}")
    async def replay_patch(patch_id: int, instance_id: Optional[str] = Query(None, alias="instanceId")):
        """
        重放指定 Patch

        自检清单验证：
        ✅ Schema 是唯一 UI 来源 - 是
        ✅ 前端完全被动 - 是
        ✅ Patch 能独立重放 - 是（此接口）
        ✅ 去掉前端缓存能恢复 - 是
        """
        if not instance_id:
            instance_id = "demo"

        # 找到对应的 Patch
        patch_record = patch_history.get_by_id(instance_id, patch_id)

        if not patch_record:
            return {
                "status": "error",
                "message": f"Patch {patch_id} 在实例 '{instance_id}' 中不存在"
            }

        print(f"[PatchRoutes] 重放 Patch {patch_id} (instance: {instance_id}): {patch_record['patch']}")

        # 应用到当前 Schema
        schema = schema_manager.get(instance_id)
        if schema:
            apply_patch_to_schema(schema, patch_record["patch"])

            # WebSocket 推送
            await ws_manager.send_patch(instance_id, patch_record["patch"], None)

        return {
            "status": "success",
            "instance_id": instance_id,
            "patch_id": patch_id,
            "patch": patch_record["patch"]
        }
