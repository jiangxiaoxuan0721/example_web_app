"""Patch 应用器 - 应用 Patch 到 Schema"""

import re
from typing import Any
from ..models import UISchema


def get_nested_value(schema: UISchema, path: str, default: Any = None) -> Any:
    """获取嵌套值

    Args:
        schema: 当前 schema
        path: 路径，如 "state.params.name"
        default: 默认值

    Returns:
        获取到的值
    """
    keys = path.split('.')
    current: Any = schema

    try:
        for key in keys:
            if key.isdigit():
                # 处理数组索引
                if isinstance(current, (list, tuple)):
                    current = current[int(key)]
                elif hasattr(current, '__getitem__'):
                    current = current[int(key)]  # type: ignore
                else:
                    return default
            elif hasattr(current, key):
                current = getattr(current, key)
            elif isinstance(current, dict):
                current = current.get(key)
            else:
                return default
        return current if current is not None else default
    except (AttributeError, KeyError, IndexError, TypeError):
        return default


def render_template(schema: UISchema, template: str) -> str:
    """渲染模板字符串，支持引用 state 的值

    示例: "表单已提交！姓名: ${state.params.name}"

    Args:
        schema: 当前 schema
        template: 模板字符串

    Returns:
        渲染后的字符串
    """
    result = template
    print(f"[PatchService] render_template 开始: template='{template}'")

    # 匹配 ${path} 格式的占位符
    pattern = r'\$\{([^}]+)\}'

    def replace_match(match):
        path = match.group(1)
        print(f"[PatchService] 替换占位符: path='{path}'")
        value = get_nested_value(schema, path, "")
        print(f"[PatchService] 获取到的值: value='{value}'")
        return str(value)

    result = re.sub(pattern, replace_match, result)
    print(f"[PatchService] render_template 完成: result='{result}'")
    return result


def render_dict_template(schema: UISchema, template_dict: dict[str, Any]) -> dict[str, Any]:
    """渲染字典中的模板值

    Args:
        schema: 当前 schema
        template_dict: 包含模板的字典

    Returns:
        渲染后的字典
    """
    result = {}
    for key, value in template_dict.items():
        if isinstance(value, str):
            result[key] = render_template(schema, value)
        elif isinstance(value, dict):
            result[key] = render_dict_template(schema, value)
        elif isinstance(value, list):
            result[key] = [
                render_template(schema, item) if isinstance(item, str)
                else render_dict_template(schema, item) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def execute_operation(
    schema: UISchema,
    operation: str,
    params: dict[str, Any],
    target_path: str
) -> dict[str, Any]:
    """执行通用操作

    支持的操作：
    - append_to_list: 向列表添加元素
    - prepend_to_list: 向列表开头添加元素
    - remove_from_list: 从列表中删除元素（支持 index: -1 批量删除所有匹配项）
    - remove_last: 删除列表最后一项
    - update_list_item: 更新列表中的某个元素
    - clear_all_params: 清空所有 params
    - append_block: 添加新块到 schema
    - prepend_block: 在开头添加块
    - remove_block: 删除块
    - update_block: 更新块
    - merge: 合并对象

    Args:
        schema: 当前 schema
        operation: 操作名称
        params: 操作参数
        target_path: 目标路径

    Returns:
        Patch 字典
    """
    print(f"[PatchService] execute_operation: operation={operation}, params={params}, target_path={target_path}")

    patch = {}
    from ..models import Block

    if operation == "append_to_list":
        # 向列表添加元素
        current_list = get_nested_value(schema, target_path, [])
        items = params.get("items", [])
        # 渲染 items 中的模板变量
        if isinstance(items, list):
            items_to_add = []
            for single_item in items:
                if isinstance(single_item, dict):
                    items_to_add.append(render_dict_template(schema, single_item))
                else:
                    items_to_add.append(single_item)
            patch[target_path] = current_list + items_to_add
        else:
            # 兼容单个元素的情况（向后兼容）
            if isinstance(items, dict):
                items = render_dict_template(schema, items)
            patch[target_path] = current_list + [items]

    elif operation == "prepend_to_list":
        # 向列表开头添加元素
        current_list = get_nested_value(schema, target_path, [])
        items = params.get("items", [])
        # 渲染 items 中的模板变量
        if isinstance(items, list):
            items_to_add = []
            for single_item in items:
                if isinstance(single_item, dict):
                    items_to_add.append(render_dict_template(schema, single_item))
                else:
                    items_to_add.append(single_item)
            patch[target_path] = items_to_add + current_list
        else:
            # 兼容单个元素的情况（向后兼容）
            if isinstance(items, dict):
                items = render_dict_template(schema, items)
            patch[target_path] = [items] + current_list

    elif operation == "remove_from_list":
        # 从列表中删除元素
        current_list = get_nested_value(schema, target_path, [])
        if isinstance(current_list, list):
            # 渲染 params 中的模板变量
            rendered_params = render_dict_template(schema, params)
            item_key = rendered_params.get("key", "id")
            item_value = rendered_params.get("value")

            print(f"[PatchService] remove_from_list: key={item_key}, value={item_value}")

            # 支持 index: -1 表示删除所有满足条件的项
            if rendered_params.get("index") == -1 and item_value:
                # 删除所有满足条件的项（例如：删除所有 completed=True 的项）
                new_list = [item for item in current_list if not (item.get(item_key) == item_value)]
            elif item_value:
                # 删除单个匹配项
                new_list = [item for item in current_list if str(item.get(item_key)) != str(item_value)]
            else:
                # 没有指定删除条件，不做任何操作
                new_list = current_list

            patch[target_path] = new_list

    elif operation == "remove_last":
        # 删除列表最后一项
        current_list = get_nested_value(schema, target_path, [])
        if isinstance(current_list, list) and len(current_list) > 0:
            patch[target_path] = current_list[:-1]

    elif operation == "update_list_item":
        # 更新列表中的某个元素
        current_list = get_nested_value(schema, target_path, [])
        if isinstance(current_list, list):
            # 渲染 params 中的模板变量
            rendered_params = render_dict_template(schema, params)
            item_key = rendered_params.get("key", "id")
            item_value = rendered_params.get("value")
            updates = rendered_params.get("updates", {})

            print(f"[PatchService] update_list_item: key={item_key}, value={item_value}, updates={updates}")

            new_list = []
            for item in current_list:
                if str(item.get(item_key)) == str(item_value):
                    # 合并更新
                    new_item = {**item, **updates}
                    new_list.append(new_item)
                else:
                    new_list.append(item)
            patch[target_path] = new_list

    elif operation == "clear_all_params":
        # 清空所有 params 字段
        current_params = get_nested_value(schema, "state.params", {})
        for key in current_params.keys():
            patch[f"state.params.{key}"] = ""

    elif operation == "append_block":
        # 添加新块到 schema
        # 渲染 params 中的模板变量
        rendered_params = render_dict_template(schema, params)
        block_data = rendered_params.get("block")
        if block_data:
            new_blocks = list(schema.blocks) + [Block(**block_data)]
            # 转换为字典以便 JSON 序列化
            patch["blocks"] = [block.model_dump(by_alias=True) for block in new_blocks]

    elif operation == "prepend_block":
        # 在开头添加新块
        # 渲染 params 中的模板变量
        rendered_params = render_dict_template(schema, params)
        block_data = rendered_params.get("block")
        if block_data:
            new_blocks = [Block(**block_data)] + list(schema.blocks)
            # 转换为字典以便 JSON 序列化
            patch["blocks"] = [block.model_dump(by_alias=True) for block in new_blocks]

    elif operation == "remove_block":
        # 删除块
        block_id = params.get("id")
        if block_id:
            new_blocks = [block for block in schema.blocks if block.id != block_id]
            patch["blocks"] = [block.model_dump(by_alias=True) for block in new_blocks]

    elif operation == "update_block":
        # 更新块
        block_id = params.get("id")
        updates = params.get("updates", {})
        if block_id and updates:
            new_blocks = []
            for block in schema.blocks:
                if block.id == block_id:
                    # 合并更新
                    block_dict = block.model_dump(by_alias=True)
                    updated_dict = {**block_dict, **updates}
                    new_blocks.append(Block(**updated_dict))
                else:
                    new_blocks.append(block)
            patch["blocks"] = [block.model_dump(by_alias=True) for block in new_blocks]

    elif operation == "merge":
        # 合并对象
        current_obj = get_nested_value(schema, target_path, {})
        if isinstance(current_obj, dict):
            merge_data = params.get("data", {})
            patch[target_path] = {**current_obj, **merge_data}

    return patch


def apply_patch_to_schema(schema: UISchema, patch: dict[str, Any]) -> None:
    """将 Patch 应用到 Schema

    Args:
        schema: 目标 Schema
        patch: Patch 数据字典，格式为 {"path": value} 或 {"path": {"mode": "operation", "operation": "xxx", "params": {...}}}
    """
    print(f"[PatchService] apply_patch_to_schema 被调用，patch keys: {list(patch.keys())}")

    # 首先处理所有操作类型的 patches
    operation_patches = {}
    direct_patches = {}

    for path, value in patch.items():
        if isinstance(value, dict) and value.get("mode") == "operation":
            # 操作类型的 patch
            operation = value.get("operation")
            params = value.get("params", {})
            print(f"[PatchService] 检测到操作 patch: path={path}, operation={operation}")
            if operation:
                operation_result = execute_operation(schema, operation, params, path)
                # 将操作结果合并到 direct_patches 中
                direct_patches.update(operation_result)
        else:
            # 直接赋值类型的 patch
            direct_patches[path] = value

    print(f"[PatchService] 操作 patches: {operation_patches}")
    print(f"[PatchService] 直接 patches: {list(direct_patches.keys())}")

    # 处理直接赋值类型的 patches
    for path, value in direct_patches.items():
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
                        # Pydantic 模型，使用 setattr 更新
                        setattr(action, 'patches', value)

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

        # 路径格式：layout.type, layout.columns, layout.gap 等
        elif len(keys) >= 2 and keys[0] == 'layout':
            layout_attr = keys[1]
            try:
                setattr(schema.layout, layout_attr, value)
                print(f"[PatchService] Updated layout.{layout_attr} = {value}")
            except (ValueError, AttributeError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")

        # 路径格式：blocks.X.id, blocks.X.type, blocks.X.bind 等 - 修改 block 属性
        # 注意：这个分支不处理 blocks.X.props.Y，由下一个分支处理
        elif len(keys) >= 2 and keys[0] == 'blocks' and (len(keys) < 3 or keys[2] != 'props'):
            block_index = int(keys[1])
            block_attr = keys[2] if len(keys) >= 3 else None

            try:
                if block_index < len(schema.blocks):
                    block = schema.blocks[block_index]

                    if block_attr:
                        # 修改 block 的属性（id, type, bind, visible 等）
                        setattr(block, block_attr, value)
                        print(f"[PatchService] Updated block[{block_index}].{block_attr} = {value}")
                    else:
                        # 替换整个 block
                        from ..models import Block
                        if isinstance(value, dict):
                            new_block = Block(**value)
                        else:
                            new_block = value
                        schema.blocks[block_index] = new_block
                        print(f"[PatchService] Replaced block at blocks[{block_index}]")
                else:
                    print(f"[PatchService] Block index {block_index} out of range (total: {len(schema.blocks)})")
            except (ValueError, AttributeError, IndexError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")

        # 路径格式：blocks.X.props.id, blocks.X.props.cols, blocks.X.props.tabs 等 - 修改 block props 属性
        elif len(keys) >= 3 and keys[0] == 'blocks' and keys[2] == 'props':
            try:
                block_index = int(keys[1])
                props_attr = keys[3] if len(keys) >= 4 else None

                print(f"[PatchService] >>> Processing blocks.X.props path: block_index={block_index}, props_attr={props_attr}, total_blocks={len(schema.blocks)}")

                if block_index < len(schema.blocks):
                    block = schema.blocks[block_index]
                    if hasattr(block.props, 'actions'):
                        print(f"[PatchService] >>> Block props.actions value: {getattr(block.props, 'actions', 'NOT_SET')}")

                    if hasattr(block, 'props') and block.props:
                        if props_attr:
                            # 特殊处理 fields 属性（整个字段数组）
                            if props_attr == 'fields':
                                from ..models.field_models import (
                                    BaseFieldConfig,
                                    SelectableFieldConfig,
                                    ImageFieldConfig,
                                    TableFieldConfig,
                                    ComponentFieldConfig
                                )
                                if isinstance(value, list):
                                    # 收集新字段的 key（用于保留 state）
                                    new_field_keys = set()
                                    for field_data in value:
                                        if isinstance(field_data, dict):
                                            new_field_keys.add(field_data.get('key'))
                                        elif hasattr(field_data, 'key'):
                                            new_field_keys.add(getattr(field_data, 'key'))

                                    # 清理旧字段的 state（但保留新 fields 中存在的 key）
                                    old_fields = getattr(block.props, 'fields', None)
                                    if old_fields and isinstance(old_fields, list):
                                        for old_field in old_fields:
                                            old_field_key = getattr(old_field, 'key', None)
                                            if old_field_key and old_field_key not in new_field_keys:
                                                if old_field_key in schema.state.params:
                                                    del schema.state.params[old_field_key]
                                                    print(f"[PatchService] Cleaned up state.params.{old_field_key}")

                                    # 转换为 FieldConfig 列表
                                    fields_list = []
                                    for field_data in value:
                                        if isinstance(field_data, dict):
                                            # 根据字段类型选择正确的模型类
                                            field_type = field_data.get('type', 'text')
                                            
                                            # 根据字段类型处理可能为 None 的数组属性
                                            if field_type == 'table':
                                                # 确保 columns 不是 None
                                                if 'columns' not in field_data or field_data['columns'] is None:
                                                    field_data['columns'] = []
                                                fields_list.append(TableFieldConfig(**field_data))
                                            elif field_type in ['select', 'radio', 'multiselect']:
                                                # 确保 options 不是 None
                                                if 'options' not in field_data or field_data['options'] is None:
                                                    field_data['options'] = []
                                                fields_list.append(SelectableFieldConfig(**field_data))
                                            elif field_type == 'image':
                                                fields_list.append(ImageFieldConfig(**field_data))
                                            elif field_type == 'component':
                                                fields_list.append(ComponentFieldConfig(**field_data))
                                            else:
                                                fields_list.append(BaseFieldConfig(**field_data))
                                        else:
                                            fields_list.append(field_data)
                                    setattr(block.props, 'fields', fields_list)

                                    # 初始化新字段的 state
                                    for new_field in fields_list:
                                        new_field_key = getattr(new_field, 'key', None)
                                        if new_field_key and new_field_key not in schema.state.params:
                                            schema.state.params[new_field_key] = ""
                                            print(f"[PatchService] Initialized state.params.{new_field_key}")
                                else:
                                    print(f"[PatchService] fields value must be a list, got: {type(value)}")
                            # 特殊处理 actions 属性
                            elif props_attr == 'actions':
                                from ..models import ActionConfig
                                if isinstance(value, list):
                                    # 转换为 ActionConfig 列表
                                    actions_list = []
                                    for action_data in value:
                                        if isinstance(action_data, dict):
                                            actions_list.append(ActionConfig(**action_data))
                                        else:
                                            actions_list.append(action_data)
                                    setattr(block.props, 'actions', actions_list)
                                    print(f"[PatchService] Updated block[{block_index}].props.actions (converted {len(actions_list)} actions)")
                                    print(f"[PatchService] Actions after set: {getattr(block.props, 'actions', 'NOT_SET')}")
                                else:
                                    print(f"[PatchService] actions value must be a list, got: {type(value)}")
                            else:
                                # 修改 props 的属性（cols, gap, tabs, panels, title 等）
                                setattr(block.props, props_attr, value)
                                print(f"[PatchService] Updated block[{block_index}].props.{props_attr} = {value}")
                        else:
                            # 替换整个 props
                            from ..models import BlockProps, FieldConfig
                            if isinstance(value, dict):
                                # 确保 fields 中的表格字段有 columns
                                if 'fields' in value and isinstance(value['fields'], list):
                                    for field in value['fields']:
                                        if isinstance(field, dict):
                                            field_type = field.get('type', 'text')
                                            if field_type == 'table' and ('columns' not in field or field['columns'] is None):
                                                field['columns'] = []
                                                print(f"[PatchService] Auto-initialized columns to empty array in table field")
                                            elif field_type in ['select', 'radio', 'multiselect'] and ('options' not in field or field['options'] is None):
                                                field['options'] = []
                                                print(f"[PatchService] Auto-initialized options to empty array in {field_type} field")
                                new_props = BlockProps(**value)
                            else:
                                new_props = value
                            block.props = new_props
                            print(f"[PatchService] Replaced props at blocks[{block_index}].props")
                else:
                    print(f"[PatchService] Block index {block_index} out of range (total: {len(schema.blocks)})")
            except (ValueError, AttributeError, IndexError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")

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
                            # 如果是 dict，转换为 FieldConfig 对象
                            if isinstance(value, dict):
                                # 根据字段类型选择正确的模型类
                                from ..models.field_models import (
                                    BaseFieldConfig,
                                    SelectableFieldConfig,
                                    ImageFieldConfig,
                                    TableFieldConfig,
                                    ComponentFieldConfig
                                )
                                
                                field_type = value.get('type', 'text')
                                
                                # 根据字段类型处理可能为 None 的数组属性
                                if field_type == 'table':
                                    # 确保 columns 不是 None
                                    if 'columns' not in value or value['columns'] is None:
                                        value['columns'] = []
                                        print(f"[PatchService] Auto-initialized columns to empty array for table field")
                                    new_field = TableFieldConfig(**value)
                                elif field_type in ['select', 'radio', 'multiselect']:
                                    # 确保 options 不是 None
                                    if 'options' not in value or value['options'] is None:
                                        value['options'] = []
                                        print(f"[PatchService] Auto-initialized options to empty array for {field_type} field")
                                    new_field = SelectableFieldConfig(**value)
                                elif field_type == 'image':
                                    new_field = ImageFieldConfig(**value)
                                elif field_type == 'component':
                                    new_field = ComponentFieldConfig(**value)
                                else:
                                    new_field = BaseFieldConfig(**value)
                            else:
                                new_field = value

                            # 获取旧字段 key，用于更新 state（如果 key 改变了）
                            old_field = current_fields[field_index]
                            old_field_key = getattr(old_field, 'key', None)
                            new_field_key = getattr(new_field, 'key', None)

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
                                old_key = getattr(field, 'key', None)
                                new_key = value

                                # 更新字段属性
                                setattr(field, field_attr, new_key)

                                # 更新 state
                                if old_key and new_key and old_key != new_key:
                                    if old_key in schema.state.params:
                                        schema.state.params[new_key] = schema.state.params.pop(old_key)
                                    if old_key in schema.state.runtime:
                                        schema.state.runtime[new_key] = schema.state.runtime.pop(old_key)
                            else:
                                # 修改其他属性
                                setattr(field, field_attr, value)

                            print(f"[PatchService] Updated field attribute: blocks[{block_index}].props.fields[{field_index}].{field_attr} = {value}")
            except (ValueError, AttributeError, IndexError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")
     