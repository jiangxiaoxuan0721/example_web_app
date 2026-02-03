"""实例服务 - 处理实例的创建、删除和操作"""

from re import Match
from backend.fastapi.models import ActionConfig, UISchema, PatchOperationType, StateInfo, LayoutInfo, Block, FieldConfig, LayoutType, SchemaPatch
import httpx
from typing import Any, Callable
from backend.core.manager import SchemaManager
from .patch import apply_patch_to_schema


class InstanceService:
    """实例服务"""

    def __init__(self, schema_manager: SchemaManager) -> None:
        self.schema_manager: SchemaManager = schema_manager

    def create_instance(
        self,
        instance_name: str,
        patches: list[SchemaPatch]
    ) -> tuple[bool, str | None]:
        """
        创建新实例

        返回: (是否成功, 错误消息)
        """
        # 检查实例是否已存在
        if self.schema_manager.exists(instance_name):
            return False, f"Instance '{instance_name}' already exists"

        # 应用 patches 创建实例
        new_schema: UISchema | None = None  # pyright: ignore[reportAssignmentType]
        for patch in patches:
            op: PatchOperationType = patch.op
            path: str = patch.path
            value: object = patch.value

            if op != PatchOperationType.SET:
                continue

            if path == "meta":
                meta_data: object = value
                new_schema: UISchema = UISchema(
                    page_key=getattr(meta_data, "page_key", instance_name),
                    state=StateInfo(params={}, runtime={}),
                    layout=LayoutInfo(type=LayoutType.SINGLE, columns=None, gap=None),
                    blocks=[],
                    actions=[]
                )
            elif path == "state" and new_schema:
                state_data: object = value
                new_schema.state = StateInfo(
                    params=getattr(state_data, "params", {}),
                    runtime=getattr(state_data, "runtime", {})
                )
            elif path == "blocks" and new_schema:
                blocks_data: list[Any] = value if isinstance(value, list) else []
                converted_blocks: list[Any] = []
                for block in blocks_data:
                    block_copy: dict[Any, Any] = dict(block)

                    if 'props' in block_copy and block_copy.get('props') is not None:
                        props_copy = dict(block_copy.get('props', {}))
                        if 'fields' in props_copy and props_copy.get('fields') is not None:
                            fields_data: Any | list[Any] = props_copy.get('fields', []) or []
                            # FieldConfig 是 Union 类型，使用 TypeAdapter 进行转换
                            converted_fields: list[Any] = []
                            from pydantic import TypeAdapter
                            field_adapter: TypeAdapter[Any] = TypeAdapter(FieldConfig)
                            for field in fields_data:
                                if isinstance(field, dict):
                                    converted_fields.append(field_adapter.validate_python(field))
                                else:
                                    converted_fields.append(field)
                            props_copy['fields'] = converted_fields
                        # Convert actions in props if present
                        if 'actions' in props_copy and props_copy.get('actions') is not None:
                            actions_data: Any | list[Any] = props_copy.get('actions', []) or []
                            converted_actions: list[ActionConfig] = [ActionConfig(**action) for action in actions_data]
                            props_copy['actions'] = converted_actions
                        block_copy['props'] = props_copy
                    converted_blocks.append(Block(**block_copy))  # type: ignore
                new_schema.blocks = converted_blocks
            elif path == "actions" and new_schema:
                actions_data: Any | list[Any] = value or []
                new_schema.actions = [ActionConfig(**action) for action in actions_data]

        if new_schema:
            self.schema_manager.set(instance_name, new_schema)
            return True, f"Instance '{instance_name}' created successfully"

    def delete_instance(
        self,
        instance_name: str
    ) -> tuple[bool, str | None]:
        """
        删除实例
        返回: (是否成功, 错误消息)
        """
        if not self.schema_manager.exists(instance_name):
            return False, f"Instance '{instance_name}' not found"
        _ = self.schema_manager.delete(instance_name)
        return True, f"Instance '{instance_name}' deleted successfully"

    def handle_action(
        self,
        instance_name: str,
        action_id: str,
        params: dict[str, Any],
        block_id: str | None = None
    ) -> dict[str, Any]:
        """
        处理实例的 action 操作（通用化处理）

        Args:
            instance_name: 实例 ID
            action_id: 操作 ID
            params: 参数
            block_id: Block ID（可选，用于 block 级别的 actions）

        返回: Patch 数据字典
        """
        print(f"[InstanceService] handle_action 被调用: instance_name={instance_name}, action_id={action_id}, params={params}, block_id={block_id}")

        schema: UISchema | None = self.schema_manager.get(instance_name)
        if not schema:
            print(f"[InstanceService] 实例 '{instance_name}' 不存在")
            return {
                "status": "error",
                "error": f"Instance '{instance_name}' not found"
            }

        # 更新 runtime.timestamp 为当前时间（确保模板表达式能获取到最新时间）
        from datetime import datetime
        if schema.state and schema.state.runtime is not None:
            schema.state.runtime["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[InstanceService] 已更新 runtime.timestamp: {schema.state.runtime['timestamp']}")

        # 将前端传来的 params 同步到 schema.state.params
        # 这样模板表达式 ${state.params.xxx} 就能获取到最新的用户输入
        if params and schema.state and schema.state.params is not None:
            for key, value in params.items():
                # 对于 rowData，临时存储到 temp_rowData，供模板使用
                if key == "rowData":
                    schema.state.params["temp_rowData"] = value
                    print(f"[InstanceService] 已同步 temp_rowData: {value}")
                # 只同步在 state.params 中已存在的字段，避免添加未知字段
                elif key in schema.state.params:
                    schema.state.params[key] = value
                    print(f"[InstanceService] 已同步 params: {key} = {value}")

        # 查找对应的 action 配置
        action_config: ActionConfig | None = None

        # 优先在指定的 block 中查找 action
        if block_id:
            for block in schema.blocks:
                if block.id == block_id and block.props and block.props.actions:
                    for action in block.props.actions:
                        if action.id == action_id:
                            action_config = action
                            print(f"[InstanceService] 在 block '{block_id}' 中找到 action: {action_id}")
                            break
                if action_config:
                    break

        # 如果在 block 中没找到，从全局 actions 中查找
        if not action_config:
            for action in schema.actions:
                if action.id == action_id:
                    action_config = action
                    print(f"[InstanceService] 在全局 actions 中找到 action: {action_id}")
                    break

        if not action_config:
            available_actions: list[str] = [a.id for a in schema.actions]
            for block in schema.blocks:
                if block.props and block.props.actions:
                    for action in block.props.actions:
                        available_actions.append(f"{block.id}.{action.id}")
            print(f"[InstanceService] Action '{action_id}' 不存在，可用的 actions: {available_actions}")
            return {
                "status": "success",
                "patch": {}
            }

        # action_config 现在保证不是 None
        assert action_config is not None
        print(f"[InstanceService] 找到 action: {action_config.id}")

        # 处理 navigate 类型的 action
        if action_config.action_type == "navigate":
            print(f"[InstanceService] Action 是 navigate 类型，跳转到 {action_config.target_instance}")
            return {
                "status": "success",
                "patch": {},
                "navigate_to": action_config.target_instance
            }

        # 对于其他类型的 action，不主动同步 params
        # params 应该已经在 action handler 执行前通过 field:change 事件更新过了
        print(f"[InstanceService] 开始执行 action handler")

        # 获取 action patches
        unified_patches = self._get_action_patches(action_config)
        print(f"[InstanceService] 统一格式的 patches: {unified_patches}")

        # 记录已处理的 patch 索引
        skip_indices = set()

        # 预处理特殊的表达式操作
        # 对于包含 JavaScript 表达式的 value，在服务端先计算结果
        for idx, patch_item in enumerate(unified_patches):
            if patch_item.op == PatchOperationType.SET and patch_item.value:
                value = patch_item.value
                if isinstance(value, str) and ".filter(" in value:
                    # 这是一个过滤操作，需要服务端处理
                    print(f"[InstanceService] 检测到过滤表达式: {value}")
                    # 通用解析表达式: "${xxx.filter(y => y.z !== abc)}"
                    import re
                    # 匹配整个过滤表达式
                    full_match = re.match(r'\$\{([^}]+)\}', value)
                    if full_match:
                        expression = full_match.group(1)
                        print(f"[InstanceService] 解析表达式: {expression}")

                        # 尝试提取列表路径: state.params.list_name
                        list_path_match = re.match(r'(state\.params\.[\w_]+)\.filter\(', expression)
                        if list_path_match:
                            list_path = list_path_match.group(1)
                            print(f"[InstanceService] 列表路径: {list_path}")

                            # 获取当前列表
                            current_list = self._get_nested_value(schema, list_path)
                            if not isinstance(current_list, list):
                                print(f"[InstanceService] {list_path} 不是列表，跳过处理")
                                continue

                            # 解析过滤条件，支持多种格式:
                            # 1. item => item.field !== state.params.xxx.yyy (箭头函数格式)
                            # 2. item.field !== params.temp_rowData.id
                            # 其中 item 可以是任意变量名（emp, row, item 等）
                            filter_body: str = re.sub(r'^.*?\.filter\((.+)\)$', r'\1', expression)
                            print(f"[InstanceService] 过滤条件: {filter_body}")

                            # 提取变量名和比较表达式
                            # 匹配箭头函数格式: variable => variable.field !== state.path.value
                            # 或者简单格式: variable.field !== params.temp_rowData.id
                            arrow_match: Match[str] | None = re.match(r'(\w+)\s*=>\s*(\w+)\.(\w+)\s*(===|!==)\s*(.+)', filter_body)
                            simple_match: Match[str] | None = re.match(r'(\w+)\.(\w+)\s*(===|!==)\s*(.+)', filter_body)

                            print(f"[InstanceService] 箭头函数匹配结果: {arrow_match}, 简单匹配结果: {simple_match}")

                            if arrow_match:
                                var_name, var_name2, list_field, operator, right_expr = arrow_match.groups()
                                print(f"[InstanceService] 箭头函数: 变量={var_name}, 字段={list_field}, 操作符={operator}, 右边表达式={right_expr}")

                                # 如果右边是 state 或 params 路径，解析其值
                                target_value = None
                                if right_expr.startswith('state.') or right_expr.startswith('params.') or right_expr.startswith('${'):
                                    # 去掉可能的外层 ${}
                                    right_expr = re.sub(r'^\$\{|\}$', '', right_expr)
                                    target_value = self._get_nested_value(schema, right_expr)
                                    print(f"[InstanceService] 从 {right_expr} 获取到值: {target_value}")
                                else:
                                    # 处理字面量: true, false, 数字, 字符串
                                    right_expr_stripped = right_expr.strip()
                                    if right_expr_stripped == 'true':
                                        target_value = True
                                    elif right_expr_stripped == 'false':
                                        target_value = False
                                    elif right_expr_stripped == 'null' or right_expr_stripped == 'undefined':
                                        target_value = None
                                    elif right_expr_stripped.isdigit():
                                        target_value = int(right_expr_stripped)
                                    elif right_expr_stripped.startswith('"') and right_expr_stripped.endswith('"'):
                                        target_value = right_expr_stripped[1:-1]
                                    elif right_expr_stripped.startswith("'") and right_expr_stripped.endswith("'"):
                                        target_value = right_expr_stripped[1:-1]
                                    else:
                                        # 尝试直接使用
                                        target_value = right_expr_stripped
                                    print(f"[InstanceService] 字面量值: {target_value}")

                                if target_value is not None:
                                    # 执行过滤
                                    if operator == '!==':
                                        filtered_list: list[Any] = [item for item in current_list if item.get(list_field) != target_value]
                                    elif operator == '===':
                                        filtered_list: list[Any] = [item for item in current_list if item.get(list_field) == target_value]
                                    else:
                                        # 不等比较
                                        filtered_list: list[Any] = [item for item in current_list if item.get(list_field) != target_value]

                                    print(f"[InstanceService] 过滤后的列表: {len(filtered_list)} 个元素")

                                    # 生成 patch 并应用到 schema
                                    from .patch import apply_patch_to_schema
                                    operation_patch: dict[str, object] = self._execute_operation(schema, operation=PatchOperationType.SET, params={"value": filtered_list}, target_path=list_path)
                                    print(f"[InstanceService] 已在服务端执行过滤: {len(current_list)} -> {len(filtered_list)}, 操作结果: {operation_patch}")

                                    # 立即应用 patch 到 schema
                                    if operation_patch:
                                        apply_patch_to_schema(schema, operation_patch)
                                        print(f"[InstanceService] 已应用 patch 到 schema")

                                    # 验证更新是否成功
                                    updated_list = self._get_nested_value(schema, list_path)
                                    print(f"[InstanceService] 验证更新后的列表: 长度={len(updated_list) if isinstance(updated_list, list) else 'not a list'}")

                                    # 标记这个 patch 已处理
                                    skip_indices.add(idx)
                                else:
                                    print(f"[InstanceService] 无法获取目标值 (target_value={target_value})，跳过过滤操作")
                            elif simple_match:
                                var_name, list_field, operator, right_expr = simple_match.groups()
                                print(f"[InstanceService] 简单格式: 变量={var_name}, 字段={list_field}, 操作符={operator}, 右边表达式={right_expr}")

                                # 解析右边表达式的值
                                target_value = None
                                if right_expr.startswith('state.') or right_expr.startswith('params.') or right_expr.startswith('${'):
                                    right_expr = re.sub(r'^\$\{|\}$', '', right_expr)
                                    target_value = self._get_nested_value(schema, right_expr)
                                    print(f"[InstanceService] 从 {right_expr} 获取到值: {target_value}")
                                else:
                                    # 处理字面量: true, false, 数字, 字符串
                                    right_expr_stripped = right_expr.strip()
                                    if right_expr_stripped == 'true':
                                        target_value = True
                                    elif right_expr_stripped == 'false':
                                        target_value = False
                                    elif right_expr_stripped == 'null' or right_expr_stripped == 'undefined':
                                        target_value = None
                                    elif right_expr_stripped.isdigit():
                                        target_value = int(right_expr_stripped)
                                    elif right_expr_stripped.startswith('"') and right_expr_stripped.endswith('"'):
                                        target_value = right_expr_stripped[1:-1]
                                    elif right_expr_stripped.startswith("'") and right_expr_stripped.endswith("'"):
                                        target_value = right_expr_stripped[1:-1]
                                    else:
                                        target_value = right_expr_stripped
                                    print(f"[InstanceService] 字面量值: {target_value}")

                                if target_value is not None:
                                    # 执行过滤
                                    if operator == '!==':
                                        filtered_list: list[Any] = [item for item in current_list if item.get(list_field) != target_value]
                                    elif operator == '===':
                                        filtered_list: list[Any] = [item for item in current_list if item.get(list_field) == target_value]
                                    else:
                                        # 不等比较
                                        filtered_list: list[Any] = [item for item in current_list if item.get(list_field) != target_value]

                                    print(f"[InstanceService] 过滤后的列表: {len(filtered_list)} 个元素")

                                    # 生成 patch 并应用到 schema
                                    from .patch import apply_patch_to_schema
                                    operation_result = self._execute_operation(schema, PatchOperationType.SET, {"value": filtered_list}, list_path)
                                    print(f"[InstanceService] 已在服务端执行过滤: {len(current_list)} -> {len(filtered_list)}, 操作结果: {operation_result}")

                                    # 立即应用 patch 到 schema
                                    if operation_result:
                                        apply_patch_to_schema(schema, operation_result)
                                        print(f"[InstanceService] 已应用 patch 到 schema")

                                    # 验证更新是否成功
                                    updated_list = self._get_nested_value(schema, list_path)
                                    print(f"[InstanceService] 验证更新后的列表: 长度={len(updated_list) if isinstance(updated_list, list) else 'not a list'}")

                                    # 标记这个 patch 已处理
                                    skip_indices.add(idx)
                                else:
                                    print(f"[InstanceService] 简单格式无法获取目标值，跳过处理")
                            else:
                                print(f"[InstanceService] 过滤条件格式不匹配，跳过处理")

        # 应用统一格式的 patches
        # 注意：skip_indices 中的 patch 已经通过自定义逻辑处理并应用到 schema
        # 我们不需要再调用 apply_unified_patch，但需要将它们的值加入 patch_dict 用于前端更新
        for idx, patch_item in enumerate(unified_patches):
            if idx in skip_indices:
                print(f"[InstanceService] 跳过已处理的 patch（但值已在schema中）: {patch_item}")
                continue
            result = self.apply_unified_patch(schema, patch_item)
            print(f"[InstanceService] 应用 patch {patch_item}: {result}")

        # 生成用于前端更新的 patch 字典
        # 需要从 schema 中读取更新后的值，而不是使用操作参数
        # 这样无论 patch 是通过自定义逻辑还是统一流程处理的，都能正确获取更新后的值
        from .patch import get_nested_value
        patch_dict = {}
        for idx, patch_item in enumerate(unified_patches):
            path = patch_item.path
            # 从 schema 中获取更新后的值（无论这个 patch 是通过哪种方式处理的）
            updated_value = get_nested_value(schema, path)
            patch_dict[path] = updated_value
            print(f"[InstanceService] 获取 patch 值: path={path}, value={updated_value}, 是否已自定义处理={idx in skip_indices}")

        # 将 Pydantic 对象转换为字典以便 JSON 序列化
        serialized_patch = self._serialize_patch_dict(patch_dict)

        print(f"[InstanceService] Action handler 返回的 patch: {serialized_patch}")

        return {
            "status": "success",
            "patch": serialized_patch
        }

    def _get_action_patches(self, action_config: ActionConfig) -> list[SchemaPatch]:
        """
        获取 action 的 patches 配置

        patches 必须是统一格式数组（Pydantic 已验证）：
        patches: [
            {"op": "append_to_list", "path": "state.params.users", "value": {...}},
            {"op": "merge", "path": "state.params.config", "value": {...}}
        ]

        Args:
            action_config: action 配置

        Returns:
            SchemaPatch 列表
        """
        patches_config = action_config.patches

        print(f"[InstanceService] _get_action_patches: input = {patches_config}")

        if not patches_config:
            print(f"[InstanceService] _get_action_patches: patches 为空")
            return []

        # Pydantic 已经验证过类型，直接返回
        print(f"[InstanceService] _get_action_patches: output = {patches_config}")
        return patches_config

    def apply_unified_patch(self, schema: UISchema, patch: SchemaPatch) -> dict[str, Any]:
        """
        处理统一 Patch 范式的所有操作类型

        支持的操作：
        - set: 直接设置值
        - add/remove: schema 结构变更（原有语义）
        - append_to_list: 追加元素到列表末尾
        - prepend_to_list: 在列表开头插入元素
        - update_list_item: 更新列表指定索引的元素
        - filter_list: 过滤列表元素
        - remove_last: 删除列表最后一项
        - merge: 合并对象到目标路径
        - increment/decrement: 增量/减量更新
        - toggle: 切换布尔值

        Args:
            schema: UISchema 对象
            patch: SchemaPatch 对象（Pydantic 验证过）

        Returns:
            处理结果 {"success": bool, "reason": str}
        """
        from .patch import execute_operation

        op: PatchOperationType = patch.op
        path: str = patch.path
        value: object = patch.value

        print(f"[InstanceService] apply_unified_patch: op={op}, path={path}, value={value}")

        # 原有的 add/remove 操作（用于 schema 结构变更）
        # 这些操作委托给 patch_routes 的函数
        if op in (PatchOperationType.ADD, PatchOperationType.REMOVE):
            # 对于 add/remove，我们需要通过 patch 来实现
            # 因为这些操作需要特殊的状态管理
            operation_patch = self._execute_operation(schema, operation=op, params={"value": value}, target_path=path)
            if operation_patch:
                apply_patch_to_schema(schema, operation_patch)
                return {"success": True}
            return {"success": False, "reason": f"Operation {op} failed"}

        # set 操作：直接赋值（先渲染模板表达式）
        if op == PatchOperationType.SET:
            from .patch import render_template, render_dict_template
            # 如果 value 是字符串，先渲染模板表达式
            if isinstance(value, str):
                rendered_value = render_template(schema, value)
            elif isinstance(value, dict):
                rendered_value = render_dict_template(schema, value)
            elif isinstance(value, list):
                # 如果是列表，对列表中的每个元素进行渲染
                rendered_value = []
                for item in value:
                    if isinstance(item, str):
                        rendered_value.append(render_template(schema, item))
                    elif isinstance(item, dict):
                        rendered_value.append(render_dict_template(schema, item))
                    else:
                        rendered_value.append(item)
            else:
                rendered_value = value
            apply_patch_to_schema(schema, {path: rendered_value})
            return {"success": True}

        # 新的操作类型（委托给 execute_operation）
        operation_map: dict[PatchOperationType, Callable[[], dict[str, Any]]] = {
            PatchOperationType.APPEND_TO_LIST: lambda: execute_operation(schema, operation=PatchOperationType.APPEND_TO_LIST, params={"items": value}, target_path=path),
            PatchOperationType.PREPEND_TO_LIST: lambda: execute_operation(schema, operation=PatchOperationType.PREPEND_TO_LIST, params={"items": value}, target_path=path),
            PatchOperationType.REMOVE_FROM_LIST: lambda: execute_operation(schema, operation=PatchOperationType.REMOVE_FROM_LIST, params=value if isinstance(value, dict) else {"value": value}, target_path=path),
            PatchOperationType.UPDATE_LIST_ITEM: lambda: execute_operation(schema, operation=PatchOperationType.UPDATE_LIST_ITEM, params=value if isinstance(value, dict) else {}, target_path=path),
            PatchOperationType.FILTER_LIST: lambda: execute_operation(schema, operation=PatchOperationType.FILTER_LIST, params=value if isinstance(value, dict) else {}, target_path=path),
            PatchOperationType.REMOVE_LAST: lambda: execute_operation(schema, operation=PatchOperationType.REMOVE_LAST, params={}, target_path=path),
            PatchOperationType.MERGE: lambda: execute_operation(schema, operation=PatchOperationType.MERGE, params={"data": value}, target_path=path),
            PatchOperationType.INCREMENT: lambda: execute_operation(schema, operation=PatchOperationType.INCREMENT, params={"delta": value}, target_path=path),
            PatchOperationType.DECREMENT: lambda: execute_operation(schema, operation=PatchOperationType.DECREMENT, params={"delta": value}, target_path=path),
            PatchOperationType.TOGGLE: lambda: execute_operation(schema, operation=PatchOperationType.TOGGLE, params={}, target_path=path),
            PatchOperationType.CLEAR_ALL_PARAMS: lambda: execute_operation(schema, operation=PatchOperationType.CLEAR_ALL_PARAMS, params={}, target_path=path),
        }

        if op in operation_map:
            try:
                result_patch = operation_map[op]()
                # 将返回的 patch 字典应用到 schema
                if result_patch:
                    apply_patch_to_schema(schema, result_patch)
                    return {"success": True}
                return {"success": False, "reason": "Operation returned empty patch"}
            except Exception as e:
                print(f"[InstanceService] Error executing operation {op}: {e}")
                return {"success": False, "reason": str(e)}

        # 未知的 op 类型
        return {"success": False, "reason": f"Unknown operation type: {op}"}

    def _execute_operation(
        self,
        schema: UISchema,
        operation: PatchOperationType,
        params: dict[str, object],
        target_path: str
    ) -> dict[str, object]:
        """
        执行通用操作（委托给 patch.py 中的实现）

        支持的操作（参考 PTA_Tool_Reference.md）：
        - add: 添加块到 schema
        - remove: 从 schema 移除块
        - append_to_list: 追加元素到列表末尾
        - prepend_to_list: 插入元素到列表开头
        - remove_from_list: 从列表删除元素
        - update_list_item: 更新列表元素
        - filter_list: 按条件过滤列表
        - remove_last: 删除列表最后一项
        - merge: 合并对象
        - increment: 增加数值
        - decrement: 减少数值
        - toggle: 切换布尔值

        注意：set 操作在 apply_unified_patch 中直接处理，不调用此函数。

        Args:
            schema: 当前 schema
            operation: 操作名称
            params: 操作参数
            target_path: 目标路径

        Returns:
            Patch 字典
        """
        from .patch import execute_operation
        return execute_operation(schema, operation, params, target_path)

    def _get_nested_value(
        self,
        schema: UISchema,
        path: str,
        default: Any = None
    ) -> Any:
        """
        从 schema 中获取嵌套值（委托给 patch.py 中的实现）

        Args:
            schema: UISchema 对象
            path: 点分隔路径（如 "state.params.count"）
            default: 默认值

        Returns:
            获取的值或默认值
        """
        from .patch import get_nested_value
        return get_nested_value(schema, path, default)

    def _render_template(
        self,
        schema: UISchema,
        template: str
    ) -> str:
        """
        渲染模板字符串，支持引用 state 的值（委托给 patch.py 中的实现）

        示例: "表单已提交！姓名: ${state.params.name}"

        Args:
            schema: 当前 schema
            template: 模板字符串

        Returns:
            渲染后的字符串
        """
        from .patch import render_template
        return render_template(schema, template)

    def _handle_external_api(
        self,
        schema: UISchema,
        config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        处理外部 API 调用

        支持两种配置格式：
        1. 旧格式（兼容）：
           {
               "url": "https://api.example.com/endpoint",
               "method": "POST",
               "headers": {"Authorization": "Bearer token"},
               "body_template": {"key": "${state.params.value}"},
               "body_template_type": "json",
               "timeout": 30,
               "response_mappings": {...},
               "error_mapping": {...}
           }

        2. 新格式（类型化 ExternalApiPatch）：
           {
               "mode": "external",
               "url": "...",
               "method": "POST",
               ...
           }

        Args:
            schema: 当前 schema
            config: API 配置

        Returns:
            Patch 字典
        """
        # 兼容新旧格式
        if config.get("mode") == "external":
            url = config.get("url")
        else:
            url = config.get("url")

        if not url:
            return {}

        if config.get("mode") == "external":
            method = config.get("method", "POST")
            headers = config.get("headers", {})
            timeout = config.get("timeout", 30)
            body_template = config.get("body_template")
            body_template_type = config.get("body_template_type", "json")
            response_mappings = config.get("response_mappings", {})
            error_mapping = config.get("error_mapping", {})
        else:
            # 旧格式
            method = config.get("method", "POST").upper()
            headers = config.get("headers", {})
            timeout = config.get("timeout", 30)
            body_template = config.get("body_template")
            body_template_type = config.get("body_template_type", "json")
            response_mappings = config.get("response_mappings", {})
            error_mapping = config.get("error_mapping", {})

        patch = {}

        try:
            # 准备请求体
            request_data = None
            if body_template:
                if body_template_type == "json":
                    # 渲染 JSON body 中的模板
                    if isinstance(body_template, dict):
                        request_data = self._render_dict_template(schema, body_template)
                elif body_template_type == "form":
                    request_data = {}
                    for key, value in body_template.items():
                        if isinstance(value, str):
                            request_data[key] = self._render_template(schema, value)
                        else:
                            request_data[key] = value

            # 发起 HTTP 请求
            with httpx.Client(timeout=timeout) as client:
                if method == "GET":
                    response = client.get(url, headers=headers)
                elif method == "POST":
                    if body_template_type == "json":
                        response = client.post(url, headers=headers, json=request_data)
                    else:
                        response = client.post(url, headers=headers, data=request_data)
                elif method == "PUT":
                    if body_template_type == "json":
                        response = client.put(url, headers=headers, json=request_data)
                    else:
                        response = client.put(url, headers=headers, data=request_data)
                elif method == "DELETE":
                    response = client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

            # 处理响应
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    response_data = response.json()

                    # 应用响应映射
                    for target_path, json_path in response_mappings.items():
                        value = self._get_json_path_value(response_data, json_path)
                        if value is not None:
                            patch[target_path] = value

                    # 默认保存完整响应（如果没有指定 mappings）
                    if not response_mappings:
                        patch["state.runtime.response"] = response_data
                except Exception as e:
                    patch["state.runtime.error"] = f"Failed to parse response: {str(e)}"
                    patch["state.runtime.status"] = "error"
            else:
                # 错误响应
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", error_data.get("message", error_msg))
                except:
                    pass

                # 应用错误映射
                if error_mapping:
                    for target_path, json_path in error_mapping.items():
                        if json_path == "error.message":
                            patch[target_path] = error_msg
                        else:
                            patch[target_path] = json_path
                else:
                    patch["state.runtime.error"] = error_msg
                    patch["state.runtime.status"] = "error"

        except httpx.TimeoutException:
            error_msg = "API request timeout"
            if error_mapping:
                for target_path, json_path in error_mapping.items():
                    if json_path == "error.message":
                        patch[target_path] = error_msg
            else:
                patch["state.runtime.error"] = error_msg
                patch["state.runtime.status"] = "error"

        except Exception as e:
            error_msg = f"API request failed: {str(e)}"
            if error_mapping:
                for target_path, json_path in error_mapping.items():
                    if json_path == "error.message":
                        patch[target_path] = error_msg
            else:
                patch["state.runtime.error"] = error_msg
                patch["state.runtime.status"] = "error"

        return patch

    def _render_dict_template(
        self,
        schema: UISchema,
        template_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """
        渲染字典中的模板值（委托给 patch.py 中的实现）

        Args:
            schema: 当前 schema
            template_dict: 包含模板的字典

        Returns:
            渲染后的字典
        """
        from .patch import render_dict_template
        return render_dict_template(schema, template_dict)

    def _get_json_path_value(
        self,
        data: Any,
        json_path: str
    ) -> Any:
        """
        从 JSON 数据中获取指定路径的值

        支持点分隔路径，如 "data.items.0.name"

        Args:
            data: JSON 数据
            json_path: JSON 路径

        Returns:
            获取的值或 None
        """
        if not json_path:
            return data

        parts = json_path.split(".")
        current = data

        for part in parts:
            if current is None:
                return None

            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None

        return current

    def handle_table_button(
        self,
        instance_name: str,
        button_id: str,
        action_id: str | None,
        params: dict[str, Any],
        block_id: str | None = None,
        field_key: str | None = None
    ) -> dict[str, Any]:
        """
        处理表格内按钮点击事件

        处理方式与 action:click 完全一致，通过 action_id 触发对应的 action 配置。

        Args:
            instance_name: 实例 ID
            button_id: 按钮唯一标识
            action_id: 关联的 action ID（可选）
            params: 参数（包含 rowData, rowIndex 等）
            block_id: Block ID（可选）
            field_key: 字段 key（用于标识是哪个表格）

        Returns:
            处理结果字典（包含 status 和 patch）
        """
        print(f"[InstanceService] handle_table_button 被调用: instance_name={instance_name}, button_id={button_id}, action_id={action_id}, block_id={block_id}, field_key={field_key}, params={params}")

        # 如果没有 action_id，返回错误
        if not action_id:
            print(f"[InstanceService] table button 没有关联的 action_id")
            return {
                "status": "error",
                "error": "Table button must have an associated action_id"
            }

        # 复用 handle_action 的逻辑
        # 表格按钮本质上就是一个 action，只是触发源不同
        result: dict[str, Any] = self.handle_action(instance_name, action_id, params, block_id)

        print(f"[InstanceService] handle_table_button 返回: {result}")
        return result

    def _serialize_patch_dict(self, patch_dict: dict[str, Any]) -> dict[str, Any]:
        """
        将 patch 字典中的 Pydantic 对象序列化为字典

        Pydantic 对象（如 Block, ActionConfig, FieldConfig）无法直接 JSON 序列化
        需要调用 model_dump() 方法转换为字典
        """
        serialized = {}

        for key, value in patch_dict.items():
            if isinstance(value, list):
                # 处理列表中的 Pydantic 对象
                serialized[key] = [
                    item.model_dump(by_alias=True) if hasattr(item, 'model_dump') else item
                    for item in value
                ]
            elif hasattr(value, 'model_dump'):
                # 处理 Pydantic 对象
                serialized[key] = value.model_dump(by_alias=True)
            elif isinstance(value, dict):
                # 递归处理嵌套字典
                serialized[key] = self._serialize_patch_dict(value)
            else:
                # 基本类型直接赋值
                serialized[key] = value

        return serialized
