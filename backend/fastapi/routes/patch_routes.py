"""Patch 相关 API 路由"""

from fastapi import Query
from typing import Optional, Any
from ...core.history import PatchHistoryManager
from ...core.manager import SchemaManager
from ..services.patch import apply_patch_to_schema
from ..models import (
    UISchema, MetaInfo, StateInfo, LayoutInfo,
    Block, BlockProps, FieldConfig, ActionConfig, StepInfo
)


def handle_remove_operation(schema: UISchema, path: str, value: Any):
    """
    Handle remove operation for arrays and objects in the schema
    
    Args:
        schema: The UI schema to modify
        path: Dot-separated path to the target property (e.g., "blocks.0.props.fields")
        value: The value to remove (identifies the item to remove)
    """
    print(f"[PatchRoutes] Handling remove operation: path={path}, value={value}")
    # Navigate to the target container
    keys = path.split(".")
    try:
        # Special handling for blocks.X.props.fields path
        if len(keys) == 4 and keys[0] == "blocks" and keys[2] == "props" and keys[3] == "fields":
            # This is removing a field from a form block
            block_index = int(keys[1])
            if block_index < len(schema.blocks):
                block = schema.blocks[block_index]
                if hasattr(block.props, "fields") and isinstance(getattr(block.props, "fields"), list):
                    # Find the field to remove by key
                    field_key = value.get("key") if isinstance(value, dict) else value
                    
                    for i, field in enumerate(getattr(block.props, "fields")):
                        field_key_check = getattr(field, "key") if hasattr(field, "key") else field.get("key")
                        if field_key_check == field_key:
                            # Remove the field
                            getattr(block.props, "fields").pop(i)
                            print(f"[PatchRoutes] Removed field from form block: {field_key}")
                            return
        
        # General navigation for other paths
        current: Any = schema
        for key in keys[:-1]:
            if key.isdigit():
                index = int(key)
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return
            else:
                current = getattr(current, key)
        
        # Get the final container
        final_key = keys[-1]
        container = getattr(current, final_key)
        
        # Remove the value from the container
        if isinstance(container, list):
            # For lists, remove by matching value
            item_to_remove = None
            for item in container:
                if isinstance(item, dict) and "key" in item and item["key"] == value.get("key"):
                    item_to_remove = item
                    break
                elif hasattr(item, "key") and getattr(item, "key") == value.get("key"):
                    item_to_remove = item
                    break
            
            if item_to_remove is not None:
                container.remove(item_to_remove)
        elif hasattr(container, "fields"):
            # For form blocks, remove from fields
            if isinstance(container.fields, list):
                item_to_remove = None
                for item in container.fields:
                    if isinstance(item, dict) and "key" in item and item["key"] == value.get("key"):
                        item_to_remove = item
                        break
                    elif hasattr(item, "key") and getattr(item, "key") == value.get("key"):
                        item_to_remove = item
                        break
                
                if item_to_remove is not None:
                    container.fields.remove(item_to_remove)
        
        print(f"[PatchRoutes] Remove operation applied: path={path}, value={value}")
        
    except (AttributeError, IndexError, ValueError) as e:
        print(f"[PatchRoutes] Error applying remove operation: {e}")
        print(f"[PatchRoutes] Path: {path}, Keys: {keys}")
        # For debugging, let's not raise an error but just log it
        # This way we can continue with other patches


def handle_add_operation(schema: UISchema, path: str, value: Any):
    """
    Handle add operation for arrays and objects in the schema
    
    Args:
        schema: The UI schema to modify
        path: Dot-separated path to the target property (e.g., "blocks.0.props.fields")
        value: The value to add
    """
    print(f"[PatchRoutes] Handling add operation: path={path}, value={value}") 
    # Navigate to the target container
    keys = path.split(".")
    try:
        
        
        # Special handling for blocks.X.props.fields path
        if len(keys) == 4 and keys[0] == "blocks" and keys[2] == "props" and keys[3] == "fields":
            # This is adding a field to a form block
            block_index = int(keys[1])
            if block_index < len(schema.blocks):
                block = schema.blocks[block_index]
                if hasattr(block.props, "fields"):
                    # Convert current fields to a list if it's not already
                    if not isinstance(getattr(block.props, "fields"), list):
                        current_fields = list(getattr(block.props, "fields").values())
                    else:
                        current_fields = getattr(block.props, "fields")
                    
                    # Convert the dict value to a FieldConfig object
                    if isinstance(value, dict):
                        field_config = FieldConfig(**value)
                    else:
                        field_config = value
                    
                    # Add the new field
                    current_fields.append(field_config)
                    
                    # Update the fields property
                    setattr(block.props, "fields", current_fields)
                    
                    print(f"[PatchRoutes] Added field to form block: {value['key']}")
                    return
        
        # General navigation for other paths
        current: Any = schema
        for key in keys[:-1]:
            if key.isdigit():
                index = int(key)
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return
            else:
                current = getattr(current, key)
        
        # Get the final container
        final_key = keys[-1]
        container = getattr(current, final_key)
        
        # Add the value to the container
        if isinstance(container, list):
            if isinstance(value, dict) and "key" in value and "label" in value:
                # Convert dict to FieldConfig if it looks like a field
                field_config = FieldConfig(**value)
                container.append(field_config)
            else:
                container.append(value)
        elif hasattr(container, "fields"):
            # For form blocks, add to fields
            if isinstance(container.fields, list):
                if isinstance(value, dict) and "key" in value and "label" in value:
                    # Convert dict to FieldConfig if it looks like a field
                    field_config = FieldConfig(**value)
                    container.fields.append(field_config)
                else:
                    container.fields.append(value)
            else:
                # Convert dict to list, add, then convert back
                fields_list = list(container.fields.values())
                if isinstance(value, dict) and "key" in value and "label" in value:
                    # Convert dict to FieldConfig if it looks like a field
                    field_config = FieldConfig(**value)
                    fields_list.append(field_config)
                else:
                    fields_list.append(value)
                container.fields = {f["key"]: f for f in fields_list}
        else:
            # If it's not a list, create a list
            setattr(current, final_key, [container, value])
        
        print(f"[PatchRoutes] Add operation applied: path={path}, value={value}")
        
    except (AttributeError, IndexError, ValueError) as e:
        print(f"[PatchRoutes] Error applying add operation: {e}")
        print(f"[PatchRoutes] Path: {path}, Keys: {keys}")
        # For debugging, let's not raise an error but just log it
        # This way we can continue with other patches


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
            # 检查instance_id是否有效
            if not instance_id:
                return {
                    "status": "error",
                    "error": "instance_id is required for normal operations"
                }
                
            schema = schema_manager.get(instance_id)
            if not schema:
                return {
                    "status": "error",
                    "error": f"Instance '{instance_id}' not found",
                    "available_instances": schema_manager.list_all()
                }

            patch_dict = {}

            # Process patches
            add_patches = []  # Track add operations separately
            remove_patches = []  # Track remove operations separately
            
            for patch in patches:
                op = patch.get("op")
                path = patch.get("path")
                value = patch.get("value")

                # Convert structured patch operations to dict format
                if op == "set":
                    patch_dict[path] = value
                elif op == "add":
                    # Handle add operation for arrays and objects
                    handle_add_operation(schema, path, value)
                    # Track add operations for WebSocket notification
                    add_patches.append(patch)
                elif op == "remove":
                    # Handle remove operation for arrays and objects
                    handle_remove_operation(schema, path, value)
                    # Track remove operations for WebSocket notification
                    remove_patches.append(patch)

            # Apply set patches to schema
            if patch_dict:
                apply_patch_to_schema(schema, patch_dict)

            # If we have any patches (set, add, or remove), save to history and notify frontend
            if patch_dict or add_patches or remove_patches:
                # For set operations, use the patch_dict
                # For add/remove operations, we need to create a special representation
                all_patches = patch_dict.copy()
                
                # 生成访问实例消息 - 在使用前定义
                access_instance_message = None
                if add_patches:
                    # 对于添加字段的操作，生成访问实例的消息
                    for patch in add_patches:
                        if patch.get("path") == "blocks.0.props.fields" and isinstance(patch.get("value"), dict):
                            field_key = patch.get("value", {}).get("key")
                            if field_key:
                                # 创建访问实例的消息，带有高亮字段的参数
                                access_instance_message = {
                                    "type": "access_instance",
                                    "instance_id": instance_id,
                                    "highlight": field_key
                                }
                                break
                    
                    # Create a representation of the add operations for history
                    for add_patch in add_patches:
                        # Store the add operation in a format that can be tracked
                        all_patches[f"add:{add_patch['path']}"] = add_patch['value']
                
                # Create a representation of the remove operations for history
                for remove_patch in remove_patches:
                    # Store the remove operation in a format that can be tracked
                    all_patches[f"remove:{remove_patch['path']}"] = remove_patch['value']
                
                # 保存到历史记录
                patch_history.save(instance_id, all_patches)

                # For add operations, we need to send the entire schema since it was modified directly
                # For set operations, we can send just the patches
                if add_patches:
                    # Send the entire updated schema after add operations
                    # This ensures the frontend receives the complete updated state
                    schema_patch = {}
                    for key, value in schema.__dict__.items():
                        if hasattr(value, '__dict__'):
                            # Convert dataclass objects to dict
                            if key == 'meta' and hasattr(value, 'step') and hasattr(value.step, '__dict__'):
                                # Special handling for meta.step to ensure proper serialization
                                meta_dict = value.__dict__.copy()
                                meta_dict['step'] = value.step.__dict__
                                schema_patch[key] = meta_dict
                            else:
                                schema_patch[key] = value.__dict__
                        elif isinstance(value, list):
                            # Convert lists with dataclass objects
                            converted_list = []
                            for item in value:
                                if hasattr(item, '__dict__'):
                                    if hasattr(item, 'props') and hasattr(item.props, '__dict__'):
                                        # Special handling for block.props with fields
                                        props_dict = item.props.__dict__.copy()
                                        if hasattr(item.props, 'fields') and isinstance(item.props.fields, list):
                                            # Convert FieldConfig objects in fields list
                                            fields_list = []
                                            for field in item.props.fields:
                                                if hasattr(field, '__dict__'):
                                                    fields_list.append(field.__dict__)
                                                else:
                                                    fields_list.append(field)
                                            props_dict['fields'] = fields_list
                                        converted_item = item.__dict__.copy()
                                        converted_item['props'] = props_dict
                                        converted_list.append(converted_item)
                                    else:
                                        converted_list.append(item.__dict__)
                                else:
                                    converted_list.append(item)
                            schema_patch[key] = converted_list
                        else:
                            schema_patch[key] = value
                    
                    # Send a custom message directly using the dispatcher
                    message = {
                        "type": "schema_update",
                        "instance_id": instance_id,
                        "schema": schema_patch
                    }
                    await ws_manager._dispatcher.send_to_instance(instance_id, message)

                    # 发送访问实例的消息
                    if access_instance_message:
                        await ws_manager._dispatcher.send_to_instance(instance_id, access_instance_message)
                else:
                    # Send only the patches for set operations
                    await ws_manager.send_patch(instance_id, patch_dict, None)

                print(f"[PatchRoutes] Patch 应用成功: {all_patches}")
                
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
