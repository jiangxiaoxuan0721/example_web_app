"""Patch 应用器 - 应用 Patch 到 Schema"""

import re
from typing import Any

from backend.fastapi.models.schema_models import LayoutInfo
from ..models import (
    # 枚举定义
    FieldType, PatchOperationType,
    # 基础模型
    UISchema,
    # Block 相关
    Block, BlockProps, ActionConfig,
    # 字段相关
    BaseFieldConfig, SelectableFieldConfig, ImageFieldConfig,
    TableFieldConfig, ComponentFieldConfig, FieldConfig
)


def validate_key_uniqueness(schema: UISchema, error_message: str = "") -> None:
    """验证 schema 中的 key 唯一性

    检查：
    1. Block 的 id 必须在所有 block 中唯一
    2. Field 的 key 必须在所有 block 的所有 fields 中唯一
    3. Action 的 id 必须在所有 block 的 actions 中唯一
    4. Schema actions 的 id 必须唯一

    Args:
        schema: 当前 schema
        error_message: 错误消息前缀

    Raises:
        ValueError: 如果发现重复的 key
    """
    prefix = error_message if error_message else "Key uniqueness validation failed"

    # 检查 Block id 唯一性
    block_ids = []
    for block in schema.blocks:
        block_id = getattr(block, 'id', None)
        if block_id:
            if block_id in block_ids:
                raise ValueError(f"{prefix}: Duplicate block id '{block_id}'")
            block_ids.append(block_id)

    # 检查 Field key 唯一性（跨所有 blocks）
    field_keys = []
    for block in schema.blocks:
        if block.props and block.props.fields:
            for field in block.props.fields:
                field_key = getattr(field, 'key', None)
                if field_key:
                    if field_key in field_keys:
                        raise ValueError(f"{prefix}: Duplicate field key '{field_key}'")
                    field_keys.append(field_key)

    # 检查 Block Action id 唯一性（跨所有 blocks）
    action_ids = []
    for block in schema.blocks:
        if block.props and block.props.actions:
            for action in block.props.actions:
                action_id = getattr(action, 'id', None)
                if action_id:
                    if action_id in action_ids:
                        raise ValueError(f"{prefix}: Duplicate action id '{action_id}'")
                    action_ids.append(action_id)

    # 检查 Schema Action id 唯一性
    schema_action_ids = []
    for action in schema.actions:
        action_id = getattr(action, 'id', None)
        if action_id:
            if action_id in schema_action_ids:
                raise ValueError(f"{prefix}: Duplicate schema action id '{action_id}'")
            schema_action_ids.append(action_id)


def get_nested_value(schema: UISchema, path: str, default: Any = None) -> Any:
    """获取嵌套值

    Args:
        schema: 当前 schema
        path: 路径，如 "state.params.name"
        default: 默认值

    Returns:
        获取到的值
    """
    keys: list[str] = path.split(sep='.')
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
    result: dict[str, Any] = {}
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


def render_block_template(schema: UISchema, block_dict: dict[str, Any]) -> dict[str, Any]:
    """渲染 block 配置中的模板值，但不渲染 field 的 value

    Args:
        schema: 当前 schema
        block_dict: block 配置字典

    Returns:
        渲染后的 block 配置
    """
    result: dict[str, Any] = {}
    for key, value in block_dict.items():
        if key == "value":
            # field 的 value 不渲染，保留模板表达式
            result[key] = value
        elif isinstance(value, str):
            result[key] = render_template(schema, value)
        elif isinstance(value, dict):
            # 如果是 fields，使用特殊的处理
            if key == "fields":
                result[key] = [
                    render_field_template(schema, field) if isinstance(field, dict)
                    else field
                    for field in value
                ]
            else:
                result[key] = render_dict_template(schema, value)
        elif isinstance(value, list):
            result[key] = [
                render_block_template(schema, item) if isinstance(item, dict)
                else render_template(schema, item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def render_field_template(schema: UISchema, field_dict: dict[str, Any]) -> dict[str, Any]:
    """渲染 field 配置中的模板值，但不渲染 value 本身

    Args:
        schema: 当前 schema
        field_dict: field 配置字典

    Returns:
        渲染后的 field 配置
    """
    result: dict[str, Any] = {}
    for key, value in field_dict.items():
        if key == "value":
            # field 的 value 不渲染，保留模板表达式
            result[key] = value
        elif isinstance(value, str):
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


def parse_field_config(field_data: dict[str, Any]) -> (
    BaseFieldConfig |
    SelectableFieldConfig |
    ImageFieldConfig |
    TableFieldConfig |
    ComponentFieldConfig
):
    """根据字段类型解析为对应的 FieldConfig 模型

    Args:
        field_data: 字段数据字典

    Returns:
        对应的 FieldConfig 模型实例

    Raises:
        ValueError: 如果字段类型无效
    """
    field_type = field_data.get('type', 'text')

    # 根据字段类型处理可能为 None 的数组属性
    if field_type == FieldType.TABLE:
        if 'columns' not in field_data or field_data['columns'] is None:
            field_data['columns'] = []
        return TableFieldConfig(**field_data)

    elif field_type in [FieldType.SELECT, FieldType.RADIO, FieldType.MULTISELECT]:
        if 'options' not in field_data or field_data['options'] is None:
            field_data['options'] = []
        return SelectableFieldConfig(**field_data)

    elif field_type == FieldType.IMAGE:
        return ImageFieldConfig(**field_data)

    elif field_type == FieldType.COMPONENT:
        return ComponentFieldConfig(**field_data)

    else:
        return BaseFieldConfig(**field_data)


def init_field_state(
    schema: UISchema,
    field: (BaseFieldConfig | SelectableFieldConfig | ImageFieldConfig | TableFieldConfig | ComponentFieldConfig),
    old_fields: list[BaseFieldConfig] | None = None
) -> None:
    """初始化字段的 state.params

    Args:
        schema: 当前 schema
        field: 要初始化的字段配置
        old_fields: 旧的字段列表（用于清理不存在的字段 state）
    """
    field_key = getattr(field, 'key', None)
    if not field_key:
        return

    # 如果新字段 key 不存在，初始化 state
    if field_key not in schema.state.params:
        schema.state.params[field_key] = field.value if hasattr(field, 'value') else ""
        print(f"[PatchService] Initialized state.params.{field_key}")

    # 清理旧字段的 state（如果提供了旧字段列表）
    if old_fields:
        for old_field in old_fields:
            old_field_key = getattr(old_field, 'key', None)
            if old_field_key and old_field_key not in schema.state.params:
                if old_field_key in schema.state.params:
                    del schema.state.params[old_field_key]
                    print(f"[PatchService] Cleaned up state.params.{old_field_key}")


def execute_operation(
    schema: UISchema,
    operation: PatchOperationType,
    params: dict[str, Any],
    target_path: str
) -> dict[str, Any]:
    """执行通用操作

    支持的操作：
        - add: 添加块到 schema
        - remove: 从 schema 移除块
        - append_to_list: 向列表添加元素
        - prepend_to_list: 向列表开头添加元素
        - remove_from_list: 从列表中删除元素（支持 index: -1 批量删除所有匹配项）
        - remove_last: 删除列表最后一项
        - update_list_item: 更新列表中的某个元素
        - filter_list: 过滤列表元素（根据条件保留元素）
        - clear_all_params: 清空所有 params
        - merge: 合并对象
        - increment: 增量更新
        - decrement: 减量更新
        - toggle: 切换布尔值

    注意：
        set 操作在 apply_unified_patch 中直接处理，不在此函数中。

    Args:
        schema: 当前 schema
        operation: 操作名称
        params: 操作参数（根据操作类型不同而不同）
        target_path: 目标路径

    Returns:
        Patch 字典
    """
    print(f"[PatchService] execute_operation: operation={operation}, params={params}, target_path={target_path}")

    patch: dict[Any, Any] = {}

    if operation == PatchOperationType.APPEND_TO_LIST:
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

    elif operation == PatchOperationType.PREPEND_TO_LIST:
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

    elif operation == PatchOperationType.REMOVE_FROM_LIST:
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

    elif operation == PatchOperationType.REMOVE_LAST:
        # 删除列表最后一项
        current_list = get_nested_value(schema, target_path, [])
        if isinstance(current_list, list) and len(current_list) > 0:
            patch[target_path] = current_list[:-1]

    elif operation == PatchOperationType.UPDATE_LIST_ITEM:
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

    elif operation == PatchOperationType.CLEAR_ALL_PARAMS:
        # 清空所有 params 字段
        current_params = get_nested_value(schema, "state.params", {})
        for key in current_params.keys():
            patch[f"state.params.{key}"] = ""

    elif operation == PatchOperationType.ADD:
        # 添加块到 schema（文档定义的 add 操作）
        current_blocks: list[Block] = get_nested_value(schema, target_path, [])
        value_to_add = params.get("value")

        if value_to_add is not None and isinstance(value_to_add, dict):
            # 渲染模板（但不渲染 field 的 value）
            rendered_value = render_block_template(schema, value_to_add)

            # 使用 Block 模型验证和规范化（自动类型检查和转换）
            new_block = Block(**rendered_value)

            # 验证 key 唯一性（在添加到列表之前）
            temp_blocks = current_blocks + [new_block]
            # 临时修改 schema 以便验证
            original_blocks = schema.blocks
            schema.blocks = temp_blocks  # type: ignore
            try:
                validate_key_uniqueness(schema, error_message="ADD operation validation failed")
            finally:
                # 恢复原始 blocks
                schema.blocks = original_blocks  # type: ignore

            # 初始化新 block 中 fields 的 state.params
            if (new_block.props is not None and
                new_block.props.fields is not None):
                for field_data in new_block.props.fields:
                    init_field_state(schema, field_data)

            # 返回新的 blocks 列表
            patch[target_path] = current_blocks + [new_block]

            # 同时返回 state.params 的更新（让前端同步初始化的值）
            if (new_block.props is not None and
                new_block.props.fields is not None):
                for field_data in new_block.props.fields:
                    field_key = getattr(field_data, 'key', None)
                    if field_key and field_key in schema.state.params:
                        patch[f"state.params.{field_key}"] = schema.state.params[field_key]

        elif isinstance(value_to_add, list):
            # 批量添加 blocks
            new_blocks: list[Block] = []
            for item in value_to_add:
                if isinstance(item, dict):
                    # 渲染模板（但不渲染 field 的 value）
                    rendered_item = render_block_template(schema, item)
                    new_block = Block(**rendered_item)

                    # 初始化 state.params
                    if (new_block.props is not None and
                        new_block.props.fields is not None):
                        for field_data in new_block.props.fields:
                            init_field_state(schema, field_data)

                    new_blocks.append(new_block)
                else:
                    new_blocks.append(item)

            # 验证 key 唯一性（在批量添加之前）
            temp_blocks = current_blocks + new_blocks
            # 临时修改 schema 以便验证
            original_blocks = schema.blocks
            schema.blocks = temp_blocks  # type: ignore
            try:
                validate_key_uniqueness(schema, error_message="ADD operation validation failed")
            finally:
                # 恢复原始 blocks
                schema.blocks = original_blocks  # type: ignore

            patch[target_path] = current_blocks + new_blocks

            # 同时返回 state.params 的更新
            for new_block in new_blocks:
                if (new_block.props is not None and
                    new_block.props.fields is not None):
                    for field_data in new_block.props.fields:
                        field_key = getattr(field_data, 'key', None)
                        if field_key and field_key in schema.state.params:
                            patch[f"state.params.{field_key}"] = schema.state.params[field_key]

    elif operation == PatchOperationType.REMOVE:
        # 从 schema 移除块（文档定义的 remove 操作）
        block_id = params.get("value", {}).get("id") if isinstance(params.get("value"), dict) else None
        current_list = get_nested_value(schema, target_path, [])
        if block_id and isinstance(current_list, list):
            patch[target_path] = [item for item in current_list if getattr(item, 'id', None) != block_id]

    elif operation == PatchOperationType.MERGE:
        # 合并对象
        current_obj = get_nested_value(schema, target_path, {})
        if isinstance(current_obj, dict):
            merge_data = params.get("data", {})
            patch[target_path] = {**current_obj, **merge_data}

    elif operation == PatchOperationType.INCREMENT:
        # 增量更新
        current_value = get_nested_value(schema, target_path, 0)
        delta = params.get("delta", 1)
        try:
            patch[target_path] = current_value + int(delta)
        except (ValueError, TypeError):
            print(f"[PatchService] increment error: current_value={current_value}, delta={delta}")
            patch[target_path] = current_value

    elif operation == PatchOperationType.DECREMENT:
        # 减量更新
        current_value = get_nested_value(schema, target_path, 0)
        delta = params.get("delta", 1)
        try:
            patch[target_path] = current_value - int(delta)
        except (ValueError, TypeError):
            print(f"[PatchService] decrement error: current_value={current_value}, delta={delta}")
            patch[target_path] = current_value

    elif operation == PatchOperationType.TOGGLE:
        # 切换布尔值
        current_value = get_nested_value(schema, target_path, False)
        patch[target_path] = not current_value

    elif operation == PatchOperationType.FILTER_LIST:
        # 过滤列表元素
        current_list = get_nested_value(schema, target_path, [])
        if isinstance(current_list, list):
            # 渲染 params 中的模板变量
            rendered_params = render_dict_template(schema, params)

            # 支持两种过滤方式：
            # 1. filter: {"key": "completed", "value": true} - 保留 key 等于 value 的元素
            # 2. filter: {"key": "completed", "operator": "!=", "value": true} - 使用操作符过滤
            filter_key = rendered_params.get("key")
            filter_value = rendered_params.get("value")
            operator = rendered_params.get("operator", "==")

            print(f"[PatchService] filter_list: key={filter_key}, value={filter_value}, operator={operator}")

            if filter_key is not None:
                filtered_list = []
                for item in current_list:
                    if not isinstance(item, dict):
                        # 非字典元素，保留
                        filtered_list.append(item)
                        continue

                    item_value = item.get(filter_key)

                    # 根据操作符判断
                    if operator == "==":
                        keep = item_value == filter_value
                    elif operator == "!=":
                        keep = item_value != filter_value
                    elif operator == ">":
                        keep = (item_value > filter_value) if isinstance(item_value, (int, float)) and isinstance(filter_value, (int, float)) else False
                    elif operator == "<":
                        keep = (item_value < filter_value) if isinstance(item_value, (int, float)) and isinstance(filter_value, (int, float)) else False
                    elif operator == ">=":
                        keep = (item_value >= filter_value) if isinstance(item_value, (int, float)) and isinstance(filter_value, (int, float)) else False
                    elif operator == "<=":
                        keep = (item_value <= filter_value) if isinstance(item_value, (int, float)) and isinstance(filter_value, (int, float)) else False
                    else:
                        keep = True  # 未知操作符，保留

                    if keep:
                        filtered_list.append(item)

                patch[target_path] = filtered_list
            else:
                # 没有指定过滤条件，返回空列表
                patch[target_path] = []
    return patch


def apply_patch_to_schema(schema: UISchema, patch: dict[str, object]) -> None:
    """将 Patch 应用到 Schema

    注意：此函数接收的 patch 是操作执行后的结果格式 {"path": value}，不是用户的统一格式。
    
    完整流程：
    1. 用户输入：SchemaPatch {"op": "...", "path": "...", "value": ..., "index": ...}
    2. apply_unified_patch 处理，调用 execute_operation
    3. execute_operation 返回：{"path": value} (简化格式)
    4. apply_patch_to_schema 将 {"path": value} 应用到 schema

    Args:
        schema: 目标 Schema
        patch: 操作结果字典，格式为 {"path": value}，例如 {"state.params.name": "value"}
    """
    print(f"[PatchService] apply_patch_to_schema 被调用，patch keys: {list(patch.keys())}")

    # 先收集所有需要验证的路径
    needs_validation = False

    # 处理直接赋值类型的 patches
    for path, value in patch.items():
        keys = path.split('.')
        print(f"[PatchService] 处理路径: {path}, keys: {keys}")

        # 判断是否需要验证唯一性（修改 blocks、fields、actions 相关的路径）
        if keys[0] in ('blocks', 'actions') or (keys[0] == 'state' and keys[1] == 'params'):
            needs_validation = True

        # 路径格式：blocks - 替换整个 blocks 数组（add 操作使用）
        if len(keys) == 1 and keys[0] == 'blocks':
            print(f"[PatchService] 匹配到 blocks 路径（替换整个数组）")
            try:
                if isinstance(value, list):
                    # 确保所有元素都是 Block 对象
                    blocks_list = []
                    for block_data in value:
                        if isinstance(block_data, Block):
                            # 已经是 Block 对象（已在 execute_operation 中验证）
                            blocks_list.append(block_data)
                        elif isinstance(block_data, dict):
                            # 字典转换为 Block（兜底处理）
                            rendered_block_data = render_dict_template(schema, block_data)
                            new_block = Block(**rendered_block_data)
                            blocks_list.append(new_block)

                            # 初始化 state.params（兜底处理）
                            if (new_block.props is not None and
                                new_block.props.fields is not None):
                                for field in new_block.props.fields:
                                    field_key = getattr(field, 'key', None)
                                    if field_key and field_key not in schema.state.params:
                                        schema.state.params[field_key] = field.value if hasattr(field, 'value') else ""
                                        print(f"[PatchService] Initialized state.params.{field_key}")

                    schema.blocks = blocks_list
                    print(f"[PatchService] Replaced blocks array, total: {len(blocks_list)}")
                else:
                    print(f"[PatchService] blocks value must be a list, got: {type(value)}")
            except Exception as e:
                print(f"[PatchService] Error applying blocks operation: {e}")

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
                    # 如果是 dict，转换为 ActionConfig 对象
                    if isinstance(value, dict):
                        new_action = ActionConfig(**value)
                    elif isinstance(value, ActionConfig):
                        new_action = value
                    else:
                        # 忽略不支持的类型
                        print(f"[PatchService] Unsupported value type for action: {type(value)}")
                        return

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

        # 路径格式：layout - 替换整个 layout 对象
        elif len(keys) == 1 and keys[0] == 'layout':
            print(f"[PatchService] 匹配到 layout 路径（替换整个对象）")
            try:
                if isinstance(value, dict):
                    new_layout = LayoutInfo(**value)
                elif isinstance(value, LayoutInfo):
                    new_layout = value
                else:
                    print(f"[PatchService] Unsupported value type for layout: {type(value)}")
                    return

                schema.layout = new_layout
                print(f"[PatchService] Replaced layout: type={new_layout.type}, columns={new_layout.columns}, gap={new_layout.gap}")
            except (ValueError, AttributeError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")

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
                        if isinstance(value, dict):
                            new_block = Block(**value)
                        elif isinstance(value, Block):
                            new_block = value
                        else:
                            # 忽略不支持的类型
                            print(f"[PatchService] Unsupported value type for block: {type(value)}")
                            return
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
                                if isinstance(value, list):
                                    # 转换为 FieldConfig 列表
                                    fields_list: list[FieldConfig] = []

                                    # 获取旧字段列表（用于清理 state）
                                    old_fields = getattr(block.props, 'fields', None)

                                    for field_data in value:
                                        if isinstance(field_data, dict):
                                            new_field = parse_field_config(field_data)
                                            fields_list.append(new_field)
                                        else:
                                            fields_list.append(field_data)

                                    # 清理旧字段 state 并初始化新字段 state
                                    for new_field in fields_list:
                                        init_field_state(schema, new_field, old_fields)

                                    setattr(block.props, 'fields', fields_list)
                                else:
                                    print(f"[PatchService] fields value must be a list, got: {type(value)}")
                            # 特殊处理 actions 属性
                            elif props_attr == 'actions':
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
                            if isinstance(value, dict):
                                # 确保 fields 中的表格字段有 columns
                                if 'fields' in value and isinstance(value['fields'], list):
                                    for field in value['fields']:
                                        if isinstance(field, dict):
                                            field_type = field.get('type', 'text')
                                            if field_type == 'table' and ('columns' not in field or field['columns'] is None):
                                                field['columns'] = []
                                            elif field_type in ['select', 'radio', 'multiselect'] and ('options' not in field or field['options'] is None):
                                                field['options'] = []
                                new_props = BlockProps(**value)
                            elif isinstance(value, BlockProps):
                                new_props = value
                            else:
                                # 忽略不支持的类型
                                print(f"[PatchService] Unsupported value type for props: {type(value)}")
                                return
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
                                new_field = parse_field_config(value)
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

                                # 更新 state（确保键是字符串）
                                if isinstance(old_key, str) and isinstance(new_key, str) and old_key != new_key:
                                    if old_key in (schema.state.params or {}):
                                        (schema.state.params or {})[new_key] = (schema.state.params or {}).pop(old_key)
                                    if old_key in (schema.state.runtime or {}):
                                        (schema.state.runtime or {})[new_key] = (schema.state.runtime or {}).pop(old_key)
                            else:
                                # 修改其他属性
                                setattr(field, field_attr, value)

                            print(f"[PatchService] Updated field attribute: blocks[{block_index}].props.fields[{field_index}].{field_attr} = {value}")
            except (ValueError, AttributeError, IndexError) as e:
                print(f"[PatchService] Error applying set operation for path '{path}': {e}")

    # 如果修改了相关的内容，进行唯一性验证
    if needs_validation:
        try:
            validate_key_uniqueness(schema, error_message="SET operation validation failed")
            print(f"[PatchService] Key uniqueness validation passed")
        except ValueError as e:
            # 验证失败，抛出异常
            print(f"[PatchService] Key uniqueness validation failed: {e}")
            raise ValueError(str(e))
     