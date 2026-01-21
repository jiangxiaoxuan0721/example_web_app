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

    Returns:
        dict: Result with 'success' (bool) and 'reason' (str, optional) for failed operations
    """
    print(f"[PatchRoutes] Handling remove operation: path={path}, value={value}")
    # Navigate to the target container
    keys = path.split(".")
    try:
        # Special handling for removing block by id (path: "blocks")
        if len(keys) == 1 and keys[0] == "blocks":
            # This is removing a block by id
            block_id = value.get("id") if isinstance(value, dict) else value

            # Find and remove the block with matching id
            for i, block in enumerate(schema.blocks):
                if hasattr(block, "id") and getattr(block, "id") == block_id:
                    # Get the block's bind path to clean up related state (BEFORE removing)
                    bind_path = getattr(block, "bind", None) if hasattr(block, "bind") else None
                    print(f"[PatchRoutes] Found block to remove: {block.id}")
                    print(f"[PatchRoutes] Block has bind attribute: {hasattr(block, 'bind')}")
                    print(f"[PatchRoutes] Block bind value: {getattr(block, 'bind', 'NOT_SET')}")
                    print(f"[PatchRoutes] Block bind_path: {bind_path}")
                    print(f"[PatchRoutes] Full block object: {block}")

                    # Clean up related state FIRST, then remove the block
                    # Check if block has props with fields (form block)
                    if hasattr(block, "props") and block.props and hasattr(block.props, "fields") and block.props.fields:
                        # For form blocks, delete state keys for each field
                        print(f"[PatchRoutes] Form block detected, will clean up state for all fields")
                        for field in block.props.fields:
                            field_key = getattr(field, "key", None) if hasattr(field, "key") else field.get("key")
                            if field_key:
                                # Try to delete from params and runtime
                                try:
                                    if field_key in schema.state.params:
                                        del schema.state.params[field_key]
                                        print(f"[PatchRoutes] ✓ Deleted state.params.{field_key}")
                                    if field_key in schema.state.runtime:
                                        del schema.state.runtime[field_key]
                                        print(f"[PatchRoutes] ✓ Deleted state.runtime.{field_key}")
                                except (KeyError, AttributeError) as e:
                                    print(f"[PatchRoutes] Warning: Failed to delete state.{field_key}: {e}")
                    elif bind_path and bind_path.startswith("state."):
                        # For non-form blocks, use the bind path to delete specific state
                        # Extract the state key (e.g., "state.params.counter" -> "params.counter")
                        state_keys = bind_path.split(".", 1)[1].split(".")
                        print(f"[PatchRoutes] Cleaning up state - bind_path: {bind_path}, state_keys: {state_keys}")

                        # Check if block binds to top-level state (params or runtime directly)
                        # In this case, don't delete anything
                        if len(state_keys) == 1 and state_keys[0] in ["params", "runtime"]:
                            print(f"[PatchRoutes] Block binds to top-level state ({state_keys[0]}), skipping state cleanup")
                        else:
                            # Navigate to the state dictionary
                            try:
                                # Start from schema.state
                                current = schema.state
                                print(f"[PatchRoutes] Initial current type: {type(current)}")
                                print(f"[PatchRoutes] StateInfo params: {schema.state.params}")
                                print(f"[PatchRoutes] StateInfo runtime: {schema.state.runtime}")

                                # Navigate through the nested dictionaries
                                for j, key in enumerate(state_keys[:-1]):
                                    print(f"[PatchRoutes] Navigating to key: {key}, current type: {type(current)}")
                                    if key == "params":
                                        current = current.params
                                    elif key == "runtime":
                                        current = current.runtime
                                    elif isinstance(current, dict) and key in current:
                                        current = current[key]
                                    else:
                                        current = None
                                        break

                                # Remove the final key
                                if current is not None and isinstance(current, dict):
                                    final_key = state_keys[-1]
                                    print(f"[PatchRoutes] Attempting to delete key '{final_key}' from dict with keys: {list(current.keys())}")
                                    if final_key in current:
                                        del current[final_key]
                                        print(f"[PatchRoutes] ✓ Cleaned up state for removed block: {bind_path} (removed key: {final_key})")
                                        print(f"[PatchRoutes] State after cleanup - params: {schema.state.params}, runtime: {schema.state.runtime}")
                                    else:
                                        print(f"[PatchRoutes] Warning: Final key '{final_key}' not found in state for: {bind_path}")
                            except (KeyError, AttributeError) as e:
                                print(f"[PatchRoutes] Warning: Failed to clean up state for {bind_path}: {e}")
                                import traceback
                                print(f"[PatchRoutes] Traceback:\n{traceback.format_exc()}")

                    # Remove the block AFTER state cleanup
                    removed_block = schema.blocks.pop(i)
                    print(f"[PatchRoutes] Removed block: {removed_block.id}")

                    return {"success": True}

            print(f"[PatchRoutes] Block with id '{block_id}' not found")
            return {"success": False, "reason": f"Block with id '{block_id}' not found"}

        # Special handling for removing action by id (path: "actions")
        if len(keys) == 1 and keys[0] == "actions":
            # This is removing an action by id
            action_id = value.get("id") if isinstance(value, dict) else value

            # Find and remove the action with matching id
            for i, action in enumerate(schema.actions):
                if hasattr(action, "id") and getattr(action, "id") == action_id:
                    removed_action = schema.actions.pop(i)
                    print(f"[PatchRoutes] Removed action: {removed_action.id}")
                    return {"success": True}

            print(f"[PatchRoutes] Action with id '{action_id}' not found")
            return {"success": False, "reason": f"Action with id '{action_id}' not found"}

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
        path: Dot-separated path to the target property (e.g., "blocks", "actions", "blocks.0.props.fields")
        value: The value to add

    Returns:
        dict: Result with 'success' (bool) and 'reason' (str, optional) for skipped operations
    """
    print(f"[PatchRoutes] Handling add operation: path={path}, value={value}")
    # Navigate to the target container
    keys = path.split(".")
    try:

        # Special handling for adding new block to blocks array
        if len(keys) == 1 and keys[0] == "blocks":
            # This is adding a new block to the blocks array
            if isinstance(value, dict):
                # Check if block with same id already exists
                new_block_id = value.get("id")
                if new_block_id:
                    for existing_block in schema.blocks:
                        if hasattr(existing_block, "id") and getattr(existing_block, "id") == new_block_id:
                            print(f"[PatchRoutes] Block with id '{new_block_id}' already exists, skipping add")
                            return {"success": False, "reason": f"Block with id '{new_block_id}' already exists"}

                # Convert dict to Block object
                block = Block(**value)
            else:
                # Check if block with same id already exists
                new_block_id = getattr(value, "id", None)
                if new_block_id:
                    for existing_block in schema.blocks:
                        if hasattr(existing_block, "id") and getattr(existing_block, "id") == new_block_id:
                            print(f"[PatchRoutes] Block with id '{new_block_id}' already exists, skipping add")
                            return {"success": False, "reason": f"Block with id '{new_block_id}' already exists"}
                block = value

            # Add block to schema
            schema.blocks.append(block)
            print(f"[PatchRoutes] Added new block: {block.id}")

            # Initialize state for the block
            # Check if block has props with fields (form block)
            if hasattr(block, "props") and block.props and hasattr(block.props, "fields") and block.props.fields:
                # For form blocks, initialize state keys for each field in params only
                print(f"[PatchRoutes] Form block detected, will initialize state for all fields")
                for field in block.props.fields:
                    field_key = getattr(field, "key", None) if hasattr(field, "key") else field.get("key")
                    if field_key:
                        # Initialize in params if not exists (form data goes to params)
                        if field_key not in schema.state.params:
                            schema.state.params[field_key] = ""
                            print(f"[PatchRoutes] ✓ Initialized state.params.{field_key} = ''")
            else:
                # For non-form blocks, initialize state based on bind path
                bind_path = getattr(block, "bind", None) if hasattr(block, "bind") else None
                if bind_path and bind_path.startswith("state."):
                    # Extract the state key path (e.g., "state.params.counter" -> "params.counter")
                    state_keys = bind_path.split(".", 1)[1].split(".")
                    print(f"[PatchRoutes] Initializing state for new block - bind_path: {bind_path}, state_keys: {state_keys}")

                    # Only initialize if there's a specific key (not just "params" or "runtime")
                    if len(state_keys) == 1 and state_keys[0] in ["params", "runtime"]:
                        # Block binds to state.params or state.runtime directly - don't create anything
                        print(f"[PatchRoutes] Block binds to top-level state ({state_keys[0]}), skipping initialization")
                    else:
                        try:
                            # Navigate to the state dictionary
                            current = schema.state

                            # Navigate through nested dictionaries, creating missing ones
                            for j, key in enumerate(state_keys[:-1]):
                                print(f"[PatchRoutes] Navigating to key: {key}, current type: {type(current)}")
                                if key == "params" and hasattr(current, "params"):
                                    current = current.params
                                elif key == "runtime" and hasattr(current, "runtime"):
                                    current = current.runtime
                                elif isinstance(current, dict):
                                    if key not in current:
                                        # Create missing nested dictionaries
                                        current[key] = {}
                                        print(f"[PatchRoutes] Created missing nested dict for key: {key}")
                                    current = current[key]
                                else:
                                    current = None
                                    break

                            # Initialize the final key if it doesn't exist
                            if current is not None and isinstance(current, dict):
                                final_key = state_keys[-1]
                                if final_key not in current:
                                    current[final_key] = {}
                                    print(f"[PatchRoutes] ✓ Initialized state for new block: {bind_path} (created key: {final_key})")
                                else:
                                    print(f"[PatchRoutes] State key '{final_key}' already exists for: {bind_path}")
                        except (KeyError, AttributeError) as e:
                            print(f"[PatchRoutes] Warning: Failed to initialize state for {bind_path}: {e}")
                            import traceback
                            print(f"[PatchRoutes] Traceback:\n{traceback.format_exc()}")

            return {"success": True}

        # Special handling for adding new action to actions array
        if len(keys) == 1 and keys[0] == "actions":
            # This is adding a new action to the actions array
            if isinstance(value, dict):
                # Convert dict to ActionConfig object
                action = ActionConfig(**value)
            else:
                action = value

            schema.actions.append(action)
            print(f"[PatchRoutes] Added new action: {action.id}")
            return

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

                    print(f"[PatchRoutes] Added field to form block: {value.get('key')}")
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
            applied_patches = []  # Track successfully applied patches
            skipped_patches = []  # Track skipped patches with reasons
            
            for patch in patches:
                op = patch.get("op")
                path = patch.get("path")
                value = patch.get("value")

                # Convert structured patch operations to dict format
                if op == "set":
                    patch_dict[path] = value
                    applied_patches.append(patch)
                elif op == "add":
                    # Handle add operation for arrays and objects
                    original_blocks_count = len(schema.blocks)
                    result = handle_add_operation(schema, path, value)
                    # Track add operations for WebSocket notification
                    add_patches.append(patch)
                    # Check result and add to applied or skipped
                    if result and result.get("success", True):
                        applied_patches.append(patch)
                    else:
                        reason = result.get("reason", "Unknown reason") if result else "Unknown reason"
                        skipped_patches.append({
                            "patch": patch,
                            "reason": reason
                        })
                elif op == "remove":
                    # Handle remove operation for arrays and objects
                    original_blocks_count = len(schema.blocks)
                    result = handle_remove_operation(schema, path, value)
                    # Track remove operations for WebSocket notification
                    remove_patches.append(patch)
                    # Check result and add to applied or skipped
                    if result and result.get("success", True):
                        applied_patches.append(patch)
                    else:
                        reason = result.get("reason", "Unknown reason") if result else "Unknown reason"
                        skipped_patches.append({
                            "patch": patch,
                            "reason": reason
                        })

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

                # 生成访问实例消息
                access_instance_message = {
                    "type": "access_instance",
                    "instance_id": instance_id
                }

                # For add/remove operations, we need to send the entire schema since it was modified directly
                # For set operations, we can send just the patches
                if add_patches or remove_patches:
                    # Send the entire updated schema after add operations
                    # This ensures the frontend receives the complete updated state
                    print(f"[PatchRoutes] Sending schema_update for instance: {instance_id}")
                    print(f"[PatchRoutes] Current schema blocks count: {len(schema.blocks)}")
                    print(f"[PatchRoutes] Current schema actions count: {len(schema.actions)}")

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
                            # Convert lists with dataclass/Pydantic objects
                            converted_list = []
                            for item in value:
                                if hasattr(item, 'model_dump') or hasattr(item, '__dict__'):
                                    # For Pydantic models, use model_dump() method
                                    if hasattr(item, 'model_dump'):
                                        item_dict = item.model_dump()
                                    else:
                                        item_dict = item.__dict__.copy()

                                    # Special handling for block.props with fields
                                    if 'props' in item_dict and item_dict['props'] is not None:
                                        if hasattr(item_dict['props'], 'model_dump'):
                                            props_dict = item_dict['props'].model_dump()
                                        else:
                                            props_dict = item_dict['props'].__dict__.copy() if hasattr(item_dict['props'], '__dict__') else item_dict['props']

                                        if 'fields' in props_dict and isinstance(props_dict['fields'], list):
                                            # Convert FieldConfig objects in fields list
                                            fields_list = []
                                            for field in props_dict['fields']:
                                                if hasattr(field, 'model_dump'):
                                                    fields_list.append(field.model_dump())
                                                elif hasattr(field, '__dict__'):
                                                    fields_list.append(field.__dict__)
                                                else:
                                                    fields_list.append(field)
                                            props_dict['fields'] = fields_list
                                        item_dict['props'] = props_dict

                                    converted_list.append(item_dict)
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
                else:
                    # Send only the patches for set operations
                    await ws_manager.send_patch(instance_id, patch_dict, None)

                print(f"[PatchRoutes] Patch 应用成功: {all_patches}")
                print(f"[PatchRoutes] 实际应用的 patches: {applied_patches}")
                print(f"[PatchRoutes] 跳过的 patches: {skipped_patches}")
                
                if not applied_patches:
                    return {
                        "status": "success",
                        "message": "No patches were applied (all operations were skipped)",
                        "instance_id": instance_id,
                        "patches_applied": [],
                        "skipped_patches": skipped_patches
                    }
                
                result = {
                    "status": "success",
                    "message": "Patch applied successfully",
                    "instance_id": instance_id,
                    "patches_applied": applied_patches
                }
                
                # Add skipped_patches to result if there are any skipped patches
                if skipped_patches:
                    result["skipped_patches"] = skipped_patches
                
                return result

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
