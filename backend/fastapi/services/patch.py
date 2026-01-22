"""Patch 应用器 - 应用 Patch 到 Schema"""

from typing import Dict, Any
from ..models import UISchema


def apply_patch_to_schema(schema: UISchema, patch: Dict[str, Any]) -> None:
    """将 Patch 应用到 Schema

    Args:
        schema: 目标 Schema
        patch: Patch 数据字典，格式为 {"path": value}
    """
    print(f"[PatchService] apply_patch_to_schema 被调用，patch keys: {list(patch.keys())}")
    
    for path, value in patch.items():
        keys = path.split('.')
        print(f"[PatchService] 处理路径: {path}, keys: {keys}")

        # 路径格式：actions.X.patches - 更新 action 的 patches（必须先匹配，因为比 actions.X 更具体）
        if len(keys) >= 3 and keys[0] == 'actions' and keys[2] == 'patches':
            print(f"[PatchService] 匹配到 actions.X.patches 路径")
            try:
                action_index = int(keys[1])

                if action_index < len(schema.actions):
                    action = schema.actions[action_index]

                    # 更新 patches 属性
                    if hasattr(action, '__dict__'):
                        setattr(action, 'patches', value)
                    else:
                        action['patches'] = value

                    print(f"[PatchService] Updated patches for action at actions[{action_index}]: {getattr(action, 'id', 'unknown')}")
                else:
                    print(f"[PatchService] Action index {action_index} out of range (total: {len(schema.actions)})")
            except (ValueError, AttributeError, IndexError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")

        # 路径格式：actions.X - 替换整个 action
        elif len(keys) >= 2 and keys[0] == 'actions':
            print(f"[PatchService] 匹配到 actions.X 路径")
            try:
                action_index = int(keys[1])

                if action_index < len(schema.actions):
                    from ..models import ActionConfig

                    # 如果是 dict，转换为 ActionConfig 对象
                    if isinstance(value, dict):
                        new_action = ActionConfig(**value)
                    else:
                        new_action = value

                    # 替换 action
                    schema.actions[action_index] = new_action

                    print(f"[PatchService] Replaced action at actions[{action_index}]: {getattr(new_action, 'id', 'unknown')}")
                else:
                    print(f"[PatchService] Action index {action_index} out of range (total: {len(schema.actions)})")
            except (ValueError, AttributeError, IndexError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")

        # 路径格式：state.params.key 或 state.runtime.key
        elif len(keys) >= 3 and keys[0] == 'state':
            target_section = keys[1]  # 'params' 或 'runtime'
            target_key = keys[2]         # 具体键名

            # 确保字典存在
            if target_section == 'params':
                if schema.state.params is None:
                    schema.state.params = {}
                schema.state.params[target_key] = value
            elif target_section == 'runtime':
                if schema.state.runtime is None:
                    schema.state.runtime = {}
                schema.state.runtime[target_key] = value

        # 路径格式：blocks.X.props.fields.Y - 替换指定索引的字段
        elif len(keys) >= 5 and keys[0] == 'blocks' and keys[2] == 'props' and keys[3] == 'fields':
            try:
                block_index = int(keys[1])
                field_index = int(keys[4])

                if block_index < len(schema.blocks):
                    block = schema.blocks[block_index]
                    if hasattr(block, 'props') and block.props and hasattr(block.props, 'fields'):
                        current_fields = getattr(block.props, 'fields')

                        # 确保 fields 是列表
                        if not isinstance(current_fields, list):
                            current_fields = list(current_fields.values())
                            setattr(block.props, 'fields', current_fields)

                        # 检查 field_index 是否有效
                        if 0 <= field_index < len(current_fields):
                            from ..models import FieldConfig
                            # 如果是 dict，转换为 FieldConfig 对象
                            if isinstance(value, dict):
                                new_field = FieldConfig(**value)
                            else:
                                new_field = value

                            # 获取旧字段 key，用于更新 state（如果 key 改变了）
                            old_field = current_fields[field_index]
                            old_field_key = getattr(old_field, 'key', None) if hasattr(old_field, 'key') else old_field.get('key')
                            new_field_key = getattr(new_field, 'key', None) if hasattr(new_field, 'key') else new_field.get('key')

                            # 替换字段
                            current_fields[field_index] = new_field

                            # 如果 key 改变了，更新 state
                            if old_field_key and new_field_key and old_field_key != new_field_key:
                                # 删除旧 key 的 state
                                if old_field_key in schema.state.params:
                                    del schema.state.params[old_field_key]
                                if old_field_key in schema.state.runtime:
                                    del schema.state.runtime[old_field_key]
                                # 添加新 key 的 state（如果不存在）
                                if new_field_key not in schema.state.params:
                                    schema.state.params[new_field_key] = ""

                            print(f"[PatchService] Replaced field at blocks[{block_index}].props.fields[{field_index}]: {new_field_key}")
            except (ValueError, AttributeError, IndexError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")

        # 路径格式：blocks.X.props.fields.Y.key 或 blocks.X.props.fields.Y.label 等 - 修改字段属性
        elif len(keys) >= 6 and keys[0] == 'blocks' and keys[2] == 'props' and keys[3] == 'fields':
            try:
                block_index = int(keys[1])
                field_index = int(keys[4])
                field_attr = keys[5]

                if block_index < len(schema.blocks):
                    block = schema.blocks[block_index]
                    if hasattr(block, 'props') and block.props and hasattr(block.props, 'fields'):
                        current_fields = getattr(block.props, 'fields')

                        # 确保 fields 是列表
                        if not isinstance(current_fields, list):
                            current_fields = list(current_fields.values())
                            setattr(block.props, 'fields', current_fields)

                        # 检查 field_index 是否有效
                        if 0 <= field_index < len(current_fields):
                            field = current_fields[field_index]

                            # 如果修改的是 'key' 属性，需要更新 state
                            if field_attr == 'key':
                                old_key = getattr(field, 'key', None) if hasattr(field, 'key') else field.get('key')
                                new_key = value

                                # 更新字段属性
                                if hasattr(field, '__dict__'):
                                    setattr(field, field_attr, new_key)
                                else:
                                    field[field_attr] = new_key

                                # 更新 state
                                if old_key and new_key and old_key != new_key:
                                    if old_key in schema.state.params:
                                        schema.state.params[new_key] = schema.state.params.pop(old_key)
                                    if old_key in schema.state.runtime:
                                        schema.state.runtime[new_key] = schema.state.runtime.pop(old_key)
                            else:
                                # 修改其他属性
                                if hasattr(field, '__dict__'):
                                    setattr(field, field_attr, value)
                                else:
                                    field[field_attr] = value

                            print(f"[PatchService] Updated field attribute: blocks[{block_index}].props.fields[{field_index}].{field_attr} = {value}")
            except (ValueError, AttributeError, IndexError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")
     