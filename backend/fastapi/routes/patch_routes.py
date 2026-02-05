"""Patch 相关 API 路由"""

from backend.fastapi.models.enums import LayoutType
from fastapi import FastAPI, Query
from typing import Any
from ...core.history import PatchHistoryManager
from ...core.manager import SchemaManager
from ..services.patch import apply_patch_to_schema
from ..models import (
    UISchema, StateInfo, LayoutInfo,
    Block, ActionConfig, LayoutType,
    BaseFieldConfig, SelectableFieldConfig, ImageFieldConfig,
    TableFieldConfig, ComponentFieldConfig
)
from backend.fastapi.services.websocket.handlers.manager import WebSocketManager
from backend.fastapi.services.instance_service import InstanceService


def convert_field_config(value: dict[str, Any]) -> Any:
    """根据字段类型将字典转换为正确的 FieldConfig 模型对象"""
    field_type = value.get("type", "text")
    
    # 根据字段类型处理可能为 None 的数组属性
    if field_type == "table":
        # 确保 columns 不是 None
        if 'columns' not in value or value['columns'] is None:
            value['columns'] = []
            print(f"[PatchRoutes] Auto-initialized columns to empty array for table field")
        return TableFieldConfig(**value)
    elif field_type in ["select", "radio", "multiselect"]:
        # 确保 options 不是 None
        if 'options' not in value or value['options'] is None:
            value['options'] = []
            print(f"[PatchRoutes] Auto-initialized options to empty array for {field_type} field")
        return SelectableFieldConfig(**value)
    elif field_type == "image":
        return ImageFieldConfig(**value)
    elif field_type == "component":
        return ComponentFieldConfig(**value)
    else:
        return BaseFieldConfig(**value)


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
                            field_key = getattr(field, "key", None) if hasattr(field, "key") else (field.get("key") if isinstance(field, dict) else None)
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

                            # Clean up state for the removed field
                            if field_key in schema.state.params:
                                del schema.state.params[field_key]
                                print(f"[PatchRoutes] ✓ Deleted state.params.{field_key}")
                            if field_key in schema.state.runtime:
                                del schema.state.runtime[field_key]
                                print(f"[PatchRoutes] ✓ Deleted state.runtime.{field_key}")

                            return {"success": True}

                    print(f"[PatchRoutes] Field with key '{field_key}' not found")
                    return {"success": False, "reason": f"Field with key '{field_key}' not found"}

            print(f"[PatchRoutes] Block index {block_index} out of range or no fields found")
            return {"success": False, "reason": f"Block index {block_index} invalid or has no fields"}

        # Special handling for blocks.X.props.actions path
        if len(keys) == 4 and keys[0] == "blocks" and keys[2] == "props" and keys[3] == "actions":
            # This is removing an action from a block
            block_index = int(keys[1])
            if block_index < len(schema.blocks):
                block = schema.blocks[block_index]
                # Check if block has actions
                if hasattr(block.props, "actions") and isinstance(getattr(block.props, "actions"), list):
                    # Find action to remove by id
                    action_id = value.get("id") if isinstance(value, dict) else value

                    for i, action in enumerate(getattr(block.props, "actions")):
                        action_id_check = getattr(action, "id") if hasattr(action, "id") else action.get("id")
                        if action_id_check == action_id:
                            # Remove action
                            getattr(block.props, "actions").pop(i)
                            print(f"[PatchRoutes] Removed action from block {block_index}: {action_id}")
                            return {"success": True}

                    print(f"[PatchRoutes] Action with id '{action_id}' not found in block {block_index}")
                    return {"success": False, "reason": f"Action with id '{action_id}' not found in block {block_index}"}
                else:
                    # Block has no actions array or it's None
                    print(f"[PatchRoutes] Block {block_index} has no actions array")
                    return {"success": False, "reason": f"Block {block_index} has no actions"}

            print(f"[PatchRoutes] Block index {block_index} out of range")
            return {"success": False, "reason": f"Block index {block_index} out of range"}

        # General navigation for other paths
        current: Any = schema
        for key in keys[:-1]:
            if key.isdigit():
                index = int(key)
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return {"success": False, "reason": f"Index {index} out of range for list"}
            else:
                try:
                    current = getattr(current, key)
                except AttributeError:
                    return {"success": False, "reason": f"Attribute '{key}' not found"}

        # Get the final container
        final_key = keys[-1]
        try:
            container = getattr(current, final_key)
        except AttributeError:
            return {"success": False, "reason": f"Attribute '{final_key}' not found"}

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
                    field_key = getattr(field, "key", None) if hasattr(field, "key") else (field.get("key") if isinstance(field, dict) else None)
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
            # Check if action with same id already exists
            if isinstance(value, dict):
                new_action_id = value.get("id")
                if new_action_id:
                    for existing_action in schema.actions:
                        if hasattr(existing_action, "id") and getattr(existing_action, "id") == new_action_id:
                            print(f"[PatchRoutes] Action with id '{new_action_id}' already exists, skipping add")
                            return {"success": False, "reason": f"Action with id '{new_action_id}' already exists"}
                # Convert dict to ActionConfig object
                action = ActionConfig(**value)
            else:
                new_action_id = getattr(value, "id", None)
                if new_action_id:
                    for existing_action in schema.actions:
                        if hasattr(existing_action, "id") and getattr(existing_action, "id") == new_action_id:
                            print(f"[PatchRoutes] Action with id '{new_action_id}' already exists, skipping add")
                            return {"success": False, "reason": f"Action with id '{new_action_id}' already exists"}
                action = value

            schema.actions.append(action)
            print(f"[PatchRoutes] Added new action: {action.id}")
            return {"success": True}

        # Special handling for blocks.X.props.fields path
        if len(keys) == 4 and keys[0] == "blocks" and keys[2] == "props" and keys[3] == "fields":
            # This is adding a field to a form block
            block_index = int(keys[1])
            if block_index < len(schema.blocks):
                block = schema.blocks[block_index]
                if hasattr(block.props, "fields"):
                    # Ensure fields is initialized to empty list if None
                    current_fields = getattr(block.props, "fields")
                    if current_fields is None:
                        print(f"[PatchRoutes] Block {block_index} has fields=None, initializing to empty list")
                        current_fields = []
                        setattr(block.props, "fields", current_fields)
                    
                    # Check if field with same key already exists
                    new_field_key = value.get("key") if isinstance(value, dict) else getattr(value, "key", None)
                    if new_field_key and isinstance(current_fields, list):
                        for existing_field in current_fields:
                            field_key_check = getattr(existing_field, "key") if hasattr(existing_field, "key") else existing_field.get("key")
                            if field_key_check == new_field_key:
                                print(f"[PatchRoutes] Field with key '{new_field_key}' already exists, skipping add")
                                return {"success": False, "reason": f"Field with key '{new_field_key}' already exists"}

                    # Convert current fields to a list if it's not already
                    if not isinstance(current_fields, list):
                        print(f"[PatchRoutes] Converting fields from {type(current_fields)} to list")
                        current_fields = list(current_fields.values())
                        setattr(block.props, "fields", current_fields)

                    # Convert the dict value to a FieldConfig object
                    if isinstance(value, dict):
                        field_type = value.get("type", "text")
                        
                        # 根据字段类型处理可能为 None 的数组属性
                        if field_type == "table":
                            # 确保 columns 不是 None
                            if 'columns' not in value or value['columns'] is None:
                                value['columns'] = []
                                print(f"[PatchRoutes] Auto-initialized columns to empty array for table field")
                        elif field_type in ['select', 'radio', 'multiselect']:
                            # 确保 options 不是 None
                            if 'options' not in value or value['options'] is None:
                                value['options'] = []
                                print(f"[PatchRoutes] Auto-initialized options to empty array for {field_type} field")
                        
                        # 根据字段类型选择正确的模型类
                        from ..models.field_models import (
                            BaseFieldConfig,
                            SelectableFieldConfig,
                            ImageFieldConfig,
                            TableFieldConfig,
                            ComponentFieldConfig
                        )

                        if field_type == "table":
                            field_config = TableFieldConfig(**value)
                        elif field_type in ["select", "radio", "multiselect"]:
                            field_config = SelectableFieldConfig(**value)
                        elif field_type == "image":
                            field_config = ImageFieldConfig(**value)
                        elif field_type == "component":
                            field_config = ComponentFieldConfig(**value)
                        else:
                            field_config = BaseFieldConfig(**value)
                    else:
                        field_config = value

                    # Add the new field
                    current_fields.append(field_config)

                    # Update the fields property
                    setattr(block.props, "fields", current_fields)

                    print(f"[PatchRoutes] Added field to form block: {value.get('key')}")

                    # Initialize state for the new field in params only
                    if new_field_key and new_field_key not in schema.state.params:
                        schema.state.params[new_field_key] = ""
                        print(f"[PatchRoutes] ✓ Initialized state.params.{new_field_key} = ''")

                    return {"success": True}

            print(f"[PatchRoutes] Block index {block_index} out of range or no props found")
            return {"success": False, "reason": f"Block index {block_index} invalid or has no props"}

        # Special handling for blocks.X.props.actions path
        if len(keys) == 4 and keys[0] == "blocks" and keys[2] == "props" and keys[3] == "actions":
            # This is adding an action to a block
            block_index = int(keys[1])
            if block_index < len(schema.blocks):
                block = schema.blocks[block_index]
                if hasattr(block.props, "actions"):
                    # Ensure actions is initialized to empty list if None
                    current_actions = getattr(block.props, "actions")
                    if current_actions is None:
                        print(f"[PatchRoutes] Block {block_index} has actions=None, initializing to empty list")
                        current_actions = []
                        setattr(block.props, "actions", current_actions)
                    
                    # Check if action with same id already exists
                    new_action_id = value.get("id") if isinstance(value, dict) else getattr(value, "id", None)
                    if new_action_id and isinstance(current_actions, list):
                        for existing_action in current_actions:
                            action_id_check = getattr(existing_action, "id") if hasattr(existing_action, "id") else existing_action.get("id")
                            if action_id_check == new_action_id:
                                print(f"[PatchRoutes] Action with id '{new_action_id}' already exists in block {block_index}, skipping add")
                                return {"success": False, "reason": f"Action with id '{new_action_id}' already exists in block {block_index}"}

                    # Convert current actions to a list if it's not already
                    if not isinstance(current_actions, list):
                        print(f"[PatchRoutes] Converting actions from {type(current_actions)} to list")
                        current_actions = list(current_actions.values())
                        setattr(block.props, "actions", current_actions)

                    # Convert dict value to an ActionConfig object
                    if isinstance(value, dict):
                        action_config = ActionConfig(**value)
                    else:
                        action_config = value

                    # Add new action
                    current_actions.append(action_config)

                    # Update actions property
                    setattr(block.props, "actions", current_actions)

                    print(f"[PatchRoutes] Added action to block {block_index}: {value.get('id')}")

                    return {"success": True}

            print(f"[PatchRoutes] Block index {block_index} out of range or no props found")
            return {"success": False, "reason": f"Block index {block_index} invalid or has no props"}

        # Special handling for state.params.* and state.runtime.* paths
        if len(keys) >= 3 and keys[0] == "state":
            target_section = keys[1]  # 'params' or 'runtime'
            target_key = keys[2]      # the key under params or runtime

            # Get the container (params or runtime dict)
            if target_section == "params":
                container = schema.state.params
            elif target_section == "runtime":
                container = schema.state.runtime
            else:
                return {"success": False, "reason": f"Invalid state section: {target_section}"}

            # Add the value to the container
            if container is None:
                return {"success": False, "reason": f"Container {target_section} is None"}

            if isinstance(container, list):
                container.append(value)
                print(f"[PatchRoutes] Added value to list {target_section}.{target_key}")
            elif isinstance(container, dict):
                if target_key not in container or not isinstance(container[target_key], list):
                    # Create list if it doesn't exist or isn't a list
                    container[target_key] = []
                container[target_key].append(value)
                print(f"[PatchRoutes] Added value to dict {target_section}.{target_key} (now has {len(container[target_key])} items)")
            else:
                return {"success": False, "reason": f"Container {target_section}.{target_key} is not a list or dict"}

            return {"success": True}

        # General navigation for other paths
        current: Any = schema
        for key in keys[:-1]:
            if key.isdigit():
                index = int(key)
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return {"success": False, "reason": f"Index {index} out of range for list"}
            else:
                try:
                    current = getattr(current, key)
                except AttributeError:
                    return {"success": False, "reason": f"Attribute '{key}' not found"}

        # Get the final container
        final_key = keys[-1]
        try:
            container = getattr(current, final_key)
        except AttributeError:
            return {"success": False, "reason": f"Attribute '{final_key}' not found"}

        # Add the value to the container
        if isinstance(container, list):
            if isinstance(value, dict) and "key" in value and "label" in value:
                # Convert dict to FieldConfig if it looks like a field
                field_config = convert_field_config(value)
                container.append(field_config)
            else:
                container.append(value)
        elif hasattr(container, "fields"):
            # For form blocks, add to fields
            if isinstance(container.fields, list):
                if isinstance(value, dict) and "key" in value and "label" in value:
                    # Convert dict to FieldConfig if it looks like a field
                    field_config = convert_field_config(value)
                    container.fields.append(field_config)
                else:
                    container.fields.append(value)
            else:
                # Convert dict to list, add, then convert back
                fields_list = list(container.fields.values())
                if isinstance(value, dict) and "key" in value and "label" in value:
                    # Convert dict to FieldConfig if it looks like a field
                    field_config = convert_field_config(value)
                    fields_list.append(field_config)
                else:
                    fields_list.append(value)
                container.fields = {f["key"]: f for f in fields_list}
        else:
            # If it's not a list, create a list
            setattr(current, final_key, [container, value])

        print(f"[PatchRoutes] Add operation applied: path={path}, value={value}")
        return {"success": True}

    except (AttributeError, IndexError, ValueError) as e:
        print(f"[PatchRoutes] Error applying add operation: {e}")
        print(f"[PatchRoutes] Path: {path}, Keys: {keys}")
        return {"success": False, "reason": str(e)}


def register_patch_routes(
    app:FastAPI,
    schema_manager: SchemaManager,
    patch_history: PatchHistoryManager,
    ws_manager: WebSocketManager,
    instance_service: InstanceService
):
    """注册 Patch 相关的路由

    Args:
        app: FastAPI 应用实例
        schema_manager: Schema 管理器
        patch_history: Patch 历史管理器
        ws_manager: WebSocket 管理器
    """

    @app.post("/ui/patch")
    async def apply_patch_endpoint(request: dict[Any, Any]):
        """
        应用 Patch 到 Schema（供 MCP 工具调用）

        支持操作：
        - 更新状态: {"instance_name": "counter", "patches": [{"op": "set", "path": "state.params.count", "value": 42}]}
        - 创建实例: {"instance_name": "__CREATE__", "new_instance_name": "my_instance", "patches": [...]}
        - 删除实例: {"instance_name": "__DELETE__", "target_instance_name": "my_instance", "patches": []}
        """
        instance_name = request.get("instance_name", "").strip() if request.get("instance_name") else ""
        patches = request.get("patches", [])
        new_instance_name = request.get("new_instance_name", "").strip() if request.get("new_instance_name") else None
        target_instance_name = request.get("target_instance_name", "").strip() if request.get("target_instance_name") else None

        print(f"[PatchRoutes] /ui/patch 收到请求: instance_name={instance_name}")

        try:
            # Handle Create Instance
            if instance_name == "__CREATE__":
                if not new_instance_name:
                    return {
                        "status": "error",
                        "error": "new_instance_name is required when instanceId is '__CREATE__'"
                    }

                if schema_manager.exists(new_instance_name):
                    return {
                        "status": "error",
                        "error": f"Instance '{new_instance_name}' already exists"
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
                            page_key=meta_data.get("page_key", new_instance_name),
                            state=StateInfo(params={}, runtime={}),
                            layout=LayoutInfo(type=LayoutType.SINGLE),
                            blocks=[],
                            actions=[]
                        )
                    elif path == "state" and new_schema:
                        state_data = value
                        new_schema.state = StateInfo(
                            params=state_data.get("params", {}),
                            runtime=state_data.get("runtime", {})
                        )
                    elif path == "layout" and new_schema:
                        # Update layout configuration
                        layout_data = value
                        layout_type_str = layout_data.get("type", "single")
                        # Convert string to LayoutType enum
                        try:
                            layout_type: LayoutType = LayoutType(layout_type_str)
                        except ValueError:
                            layout_type = LayoutType.SINGLE
                        new_schema.layout = LayoutInfo(
                            type=layout_type,
                            columns=layout_data.get("columns"),
                            gap=layout_data.get("gap")
                        )
                    elif path == "blocks" and new_schema:
                        # Convert dict list to Block objects
                        blocks_data: Any | list[Any] = value or []
                        converted_blocks: list[Any] = []
                        for block in blocks_data:
                            # Create a copy to avoid modifying original
                            block_copy: dict[Any, Any] = dict(block)

                            # Convert fields in props if present
                            if 'props' in block_copy and block_copy.get('props') is not None:
                                props_copy: dict[Any, Any] = dict(block_copy.get('props', {}))
                                if 'fields' in props_copy and props_copy.get('fields') is not None:
                                    fields_data: Any | list[Any] = props_copy.get('fields', []) or []
                                    converted_fields: list[BaseFieldConfig] = [BaseFieldConfig(**field) for field in fields_data]
                                    props_copy['fields'] = converted_fields
                                # Convert actions in props if present
                                if 'actions' in props_copy and props_copy.get('actions') is not None:
                                    actions_data = props_copy.get('actions', []) or []
                                    converted_actions = [ActionConfig(**action) for action in actions_data]
                                    props_copy['actions'] = converted_actions
                                block_copy['props'] = props_copy
                            converted_blocks.append(Block(**block_copy))
                        new_schema.blocks = converted_blocks
                    elif path == "actions" and new_schema:
                        # Convert dict list to ActionConfig objects
                        actions_data: Any | list[Any] = value or []
                        new_schema.actions = [ActionConfig(**action) for action in actions_data]

                if new_schema:
                    schema_manager.set(new_instance_name, new_schema)
                    print(f"[PatchRoutes] 实例 '{new_instance_name}' 创建成功")
                    return {
                        "status": "success",
                        "message": f"Instance '{new_instance_name}' created successfully",
                        "instance_name": new_instance_name
                    }

                return {
                    "status": "error",
                    "error": "Failed to create instance: Invalid patches"
                }

            # Handle Delete Instance
            if instance_name == "__DELETE__":
                if not target_instance_name:
                    return {
                        "status": "error",
                        "error": "target_instance_name is required when instanceId is '__DELETE__'"
                    }

                if not schema_manager.exists(target_instance_name):
                    return {
                        "status": "error",
                        "error": f"Instance '{target_instance_name}' not found"
                    }

                schema_manager.delete(target_instance_name)
                print(f"[PatchRoutes] 实例 '{target_instance_name}' 删除成功")
                return {
                    "status": "success",
                    "message": f"Instance '{target_instance_name}' deleted successfully"
                }

            # Handle Normal Instance Operations
            # 检查instance_name是否有效
            if not instance_name:
                return {
                    "status": "error",
                    "error": "instance_name is required for normal operations"
                }
                
            schema = schema_manager.get(instance_name)
            if not schema:
                return {
                    "status": "error",
                    "error": f"Instance '{instance_name}' not found",
                    "available_instances": schema_manager.list_all()
                }

            patch_dict = {}

            # Process patches
            add_patches = []  # Track add operations separately
            remove_patches = []  # Track remove operations separately
            unified_patches = []  # Track unified patch operations (append_to_list, merge, etc.)
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
                else:
                    # Handle unified patch operations (append_to_list, merge, increment, etc.)
                    result = instance_service.apply_unified_patch(schema, patch)
                    unified_patches.append(patch)
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

            # If we have any patches (set, add, remove, or unified ops), save to history and notify frontend
            if patch_dict or add_patches or remove_patches or unified_patches:
                # For set operations, use the patch_dict
                # For add/remove/unified operations, we need to create a special representation
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
                                    "instance_name": instance_name,
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

                # Create a representation of unified patch operations for history
                for unified_patch in unified_patches:
                    # Store the unified operation in a format that can be tracked
                    all_patches[f"{unified_patch['op']}:{unified_patch['path']}"] = unified_patch.get('value')

                # 保存到历史记录
                patch_history.save(instance_name, all_patches)

                # 生成访问实例消息
                access_instance_message = {
                    "type": "access_instance",
                    "instance_name": instance_name
                }

                # For any operation that modifies schema (add/remove/set/unified), always send the entire schema
                # This ensures the frontend receives the complete updated state and can trigger highlights
                # This is more reliable than trying to distinguish between different operation types
                has_any_patches = patch_dict or add_patches or remove_patches or unified_patches

                if has_any_patches:
                    # Send the entire updated schema
                    # This ensures the frontend receives the complete updated state
                    print(f"[PatchRoutes] Sending schema_update for instance: {instance_name}")
                    print(f"[PatchRoutes] Current schema blocks count: {len(schema.blocks)}")
                    print(f"[PatchRoutes] Current schema actions count: {len(schema.actions)}")

                    # Determine what to highlight based on all patches
                    highlight_info = None

                    # Check add patches first (highest priority)
                    for add_patch in add_patches:
                        path = add_patch.get("path")
                        value = add_patch.get("value")

                        # Check if adding a field to a block
                        if "blocks" in path and "props" in path and "fields" in path:
                            if isinstance(value, dict):
                                highlight_info = {
                                    "type": "field",
                                    "key": value.get("key")
                                }
                                break
                        # Check if adding a block
                        elif path == "blocks":
                            if isinstance(value, dict):
                                highlight_info = {
                                    "type": "block",
                                    "id": value.get("id")
                                }
                                break
                        # Check if adding an action
                        elif path == "actions":
                            if isinstance(value, dict):
                                highlight_info = {
                                    "type": "action",
                                    "id": value.get("id")
                                }
                                break

                    # If no highlight from add patches, check set patches for field additions
                    if not highlight_info and patch_dict:
                        for path, value in patch_dict.items():
                            # Check if setting a field array (could be adding/replacing fields)
                            if "blocks" in path and "props" in path and "fields" in path:
                                if isinstance(value, list) or isinstance(value, dict):
                                    # Extract field key from the new field(s)
                                    if isinstance(value, dict):
                                        fields_list = list(value.values()) if not isinstance(value, list) else value
                                    else:
                                        fields_list = value
                                    if fields_list and len(fields_list) > 0:
                                        last_field = fields_list[-1]
                                        if isinstance(last_field, dict) and "key" in last_field:
                                            highlight_info = {
                                                "type": "field",
                                                "key": last_field["key"]
                                            }
                                            break

                    # Use Pydantic's model_dump() method to properly serialize the entire schema
                    # This handles datetime objects and nested Pydantic models automatically
                    schema_patch = schema.model_dump(by_alias=True, mode='json')

                    # Send a custom message directly using the dispatcher
                    message = {
                        "type": "schema_update",
                        "instance_name": instance_name,
                        "schema": schema_patch,
                        "highlight": highlight_info
                    }
                    await ws_manager._dispatcher.send_to_instance(instance_name, message)

                print(f"[PatchRoutes] Patch 应用成功: {all_patches}")
                print(f"[PatchRoutes] 实际应用的 patches: {applied_patches}")
                print(f"[PatchRoutes] 跳过的 patches: {skipped_patches}")
                
                if not applied_patches:
                    return {
                        "status": "success",
                        "message": "No patches were applied (all operations were skipped)",
                        "instance_name": instance_name,
                        "patches_applied": [],
                        "skipped_patches": skipped_patches
                    }

                result = {
                    "status": "success",
                    "message": "Patch applied successfully",
                    "instance_name": instance_name,
                    "patches_applied": applied_patches
                }

                # Add skipped_patches to result if there are any skipped patches
                if skipped_patches:
                    result["skipped_patches"] = skipped_patches

                return result

            return {
                "status": "success",
                "message": "No patches to apply",
                "instance_name": instance_name
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
    async def get_patches(instance_name: str | None = Query(None, alias="instanceId")):
        """
        获取所有 Patch 历史记录
        支持 Patch 重放

        - /ui/patches              -> 返回默认实例的历史
        - /ui/patches?instanceId=xxx -> 返回指定实例的历史
        """
        if not instance_name:
            instance_name = "demo"

        patches = patch_history.get_all(instance_name)

        return {
            "status": "success",
            "instance_name": instance_name,
            "patches": patches
        }

    @app.get("/ui/patches/replay/{patch_id}")
    async def replay_patch(patch_id: int, instance_name: str | None = Query(None, alias="instanceId")):
        """
        重放指定 Patch

        自检清单验证：
        ✅ Schema 是唯一 UI 来源 - 是
        ✅ 前端完全被动 - 是
        ✅ Patch 能独立重放 - 是（此接口）
        ✅ 去掉前端缓存能恢复 - 是
        """
        if not instance_name:
            instance_name = "demo"

        # 找到对应的 Patch
        patch_record = patch_history.get_by_id(instance_name, patch_id)

        if not patch_record:
            return {
                "status": "error",
                "message": f"Patch {patch_id} 在实例 '{instance_name}' 中不存在"
            }

        print(f"[PatchRoutes] 重放 Patch {patch_id} (instance: {instance_name}): {patch_record['patch']}")

        # 应用到当前 Schema
        schema = schema_manager.get(instance_name)
        if schema:
            patch_data = patch_record["patch"]
            if not isinstance(patch_data, dict):
                patch_data = {}
            apply_patch_to_schema(schema, patch_data)

            # WebSocket 推送
            await ws_manager.send_patch(instance_name, patch_data, None)

        return {
            "status": "success",
            "instance_name": instance_name,
            "patch_id": patch_id,
            "patch": patch_record["patch"]
        }


