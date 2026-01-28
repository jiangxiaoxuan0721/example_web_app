"""实例服务 - 处理实例的创建、删除和操作"""

import httpx
from typing import Any
from ..models import UISchema, MetaInfo, StateInfo, LayoutInfo, Block, ActionConfig, StepInfo, FieldConfig, LayoutType
from backend.core.manager import SchemaManager
from .patch import apply_patch_to_schema


class InstanceService:
    """实例服务"""

    def __init__(self, schema_manager: SchemaManager):
        self.schema_manager = schema_manager

    def create_instance(
        self,
        instance_id: str,
        patches: list[dict[str, Any]]
    ) -> tuple[bool, str | None]:
        """
        创建新实例

        返回: (是否成功, 错误消息)
        """
        # 检查实例是否已存在
        if self.schema_manager.exists(instance_id):
            return False, f"Instance '{instance_id}' already exists"

        # 应用 patches 创建实例
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
                    meta=MetaInfo(  # pyright: ignore[reportCallIssue]
                        pageKey=getattr(meta_data, "pageKey", instance_id),
                        step=StepInfo(**getattr(meta_data, "step", {"current": 1, "total": 1})),
                        status=getattr(meta_data, "status", "idle")
                    ),
                    state=StateInfo(params={}, runtime={}),
                    layout=LayoutInfo(type=LayoutType.SINGLE, columns=None, gap=None),
                    blocks=[],
                    actions=[]
                )
            elif path == "state" and new_schema:
                state_data = value
                new_schema.state = StateInfo(
                    params=getattr(state_data, "params", {}),
                    runtime=getattr(state_data, "runtime", {})
                )
            elif path == "blocks" and new_schema:
                blocks_data = value or []
                converted_blocks = []
                for block in blocks_data:
                    block_copy = dict(block)

                    if 'props' in block_copy and block_copy.get('props') is not None:
                        props_copy = dict(block_copy.get('props', {}))
                        if 'fields' in props_copy and props_copy.get('fields') is not None:
                            fields_data = props_copy.get('fields', []) or []
                            # FieldConfig 是 Union 类型，使用 TypeAdapter 进行转换
                            converted_fields = []
                            from pydantic import TypeAdapter
                            field_adapter = TypeAdapter(FieldConfig)
                            for field in fields_data:
                                if isinstance(field, dict):
                                    converted_fields.append(field_adapter.validate_python(field))
                                else:
                                    converted_fields.append(field)
                            props_copy['fields'] = converted_fields
                            block_copy['props'] = props_copy
                        converted_blocks.append(Block(**block_copy))  # type: ignore
                new_schema.blocks = converted_blocks
            elif path == "actions" and new_schema:
                actions_data = value or []
                new_schema.actions = [ActionConfig(**action) for action in actions_data]

        if new_schema:
            self.schema_manager.set(instance_id, new_schema)
            return True, f"Instance '{instance_id}' created successfully"

        return False, "Failed to create instance: Invalid patches"

    def delete_instance(
        self,
        instance_id: str
    ) -> tuple[bool, str | None]:
        """
        删除实例

        返回: (是否成功, 错误消息)
        """
        if not self.schema_manager.exists(instance_id):
            return False, f"Instance '{instance_id}' not found"

        self.schema_manager.delete(instance_id)
        return True, f"Instance '{instance_id}' deleted successfully"

    def handle_action(
        self,
        instance_id: str,
        action_id: str,
        params: dict[str, Any],
        block_id: str | None = None
    ) -> dict[str, Any]:
        """
        处理实例的 action 操作（通用化处理）

        Args:
            instance_id: 实例 ID
            action_id: 操作 ID
            params: 参数
            block_id: Block ID（可选，用于 block 级别的 actions）

        返回: Patch 数据字典
        """
        print(f"[InstanceService] handle_action 被调用: instance_id={instance_id}, action_id={action_id}, params={params}, block_id={block_id}")

        schema = self.schema_manager.get(instance_id)
        if not schema:
            print(f"[InstanceService] 实例 '{instance_id}' 不存在")
            return {
                "status": "error",
                "error": f"Instance '{instance_id}' not found"
            }

        # 先同步前端传来的 params（排除 blockId 参数）
        if params and isinstance(params, dict):
            # 过滤掉非 schema 状态参数（如 blockId）
            filtered_params = {k: v for k, v in params.items() if k != "blockId"}
            params_patch = {f"state.params.{k}": v for k, v in filtered_params.items()}
            print(f"[InstanceService] 同步前端 params: {params_patch}")
            apply_patch_to_schema(schema, params_patch)

        # 查找对应的 action 配置
        action_config = None

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
            available_actions = [a.id for a in schema.actions]
            for block in schema.blocks:
                if block.props and block.props.actions:
                    for action in block.props.actions:
                        available_actions.append(f"{block.id}.{action.id}")
            print(f"[InstanceService] Action '{action_id}' 不存在，可用的 actions: {available_actions}")
            return {
                "status": "success",
                "patch": {}
            }

        print(f"[InstanceService] 找到 action: {action_config.id}, handler_type={getattr(action_config, 'handler_type', None)}")

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
        patch = self._execute_action_handler(schema, action_config)
        print(f"[InstanceService] Action handler 返回的 patch: {patch}")

        # 应用 patch 到 schema
        if patch:
            apply_patch_to_schema(schema, patch)
            print(f"[InstanceService] Patch 已应用到 schema")
        else:
            print(f"[InstanceService] Patch 为空，不应用")

        return {
            "status": "success",
            "patch": patch
        }

    def _execute_action_handler(
        self,
        schema: UISchema,
        action_config: Any
    ) -> dict[str, Any]:
        """
        执行 action 处理器（使用配置驱动的 EventHandler）

        支持 patches 中的值可以是：
        - 直接值：直接设置到对应路径
        - DirectValuePatch: {"mode": "direct"}
        - OperationPatch: {"mode": "operation", "operation": "xxx", "params": {...}}
        - ExternalApiPatch: {"mode": "external", "url": "...", ...}

        Args:
            schema: 当前 schema
            action_config: action 配置

        Returns:
            Patch 字典
        """
        from ..models import HandlerType

        handler_type = getattr(action_config, "handler_type", None)
        patches_config = getattr(action_config, "patches", {})

        print(f"[InstanceService] _execute_action_handler: action_id={getattr(action_config, 'id', None)}, handler_type={handler_type}")
        print(f"[InstanceService] patches_config = {patches_config}")

        if not patches_config:
            return {}

        patch = {}

        # 处理不同的 handler_type
        if handler_type in [HandlerType.SET.value, HandlerType.TEMPLATE.value,
                            HandlerType.TEMPLATE_ALL.value, HandlerType.TEMPLATE_STATE.value]:
            # set、template 相关的处理
            patch = {}
            for path, value in patches_config.items():
                if isinstance(value, dict) and "mode" in value:
                    mode = value.get("mode")

                    if mode == "operation":
                        # OperationPatch
                        operation = value.get("operation")
                        if operation:
                            params = value.get("params", {})
                            operation_patch = self._execute_operation(schema, operation, params, path)
                            patch.update(operation_patch)
                            # 已经处理了这个路径，跳过后续处理
                            continue
                    elif mode == "external":
                        # ExternalApiPatch（预留）
                        pass
                    else:
                        # DirectValuePatch
                        patch[path] = value
                elif isinstance(value, str) and value.startswith("special:"):
                    # 兼容旧的 special: 语法
                    special_op = value[8:]
                    operation_patch = self._execute_operation(schema, special_op, {}, path)
                    patch.update(operation_patch)
                else:
                    # 直接设置值（向后兼容）
                    if isinstance(value, str) and "${" in value and "}" in value:
                        # 检查是否引用了 state.runtime.timestamp
                        if "state.runtime.timestamp" in value:
                            from datetime import datetime
                            patch["state.runtime.timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        patch[path] = self._render_template(schema, value)
                    else:
                        patch[path] = value

        elif handler_type == HandlerType.INCREMENT.value:
            # 使用 increment 处理
            for path, delta in patches_config.items():
                current_value = self._get_nested_value(schema, path, 0)
                try:
                    patch = {path: current_value + int(delta)}
                except (ValueError, TypeError):
                    patch = {path: current_value}
                return patch

        elif handler_type == HandlerType.DECREMENT.value:
            # 使用 decrement 处理
            for path, delta in patches_config.items():
                current_value = self._get_nested_value(schema, path, 0)
                try:
                    patch = {path: current_value - int(delta)}
                except (ValueError, TypeError):
                    patch = {path: current_value}
                return patch

        elif handler_type == HandlerType.TOGGLE.value:
            # 使用 toggle 处理
            for path, _ in patches_config.items():
                current_value = self._get_nested_value(schema, path, False)
                return {path: not current_value}

        elif handler_type == HandlerType.EXTERNAL.value:
            # External API 调用（使用 EventHandler 的实现）
            import asyncio  # type: ignore
            # 注意：这里需要异步调用，但我们现在在同步方法中
            # 返回空 patch，实际的外部 API 调用需要在异步上下文中处理
            # TODO: 考虑将 handle_action 改为异步方法
            print("[InstanceService] External API 调用需要在异步上下文中处理")
            return {}

        else:
            # 未知的 handler_type，尝试直接设置值
            patch = {}
            for path, value in patches_config.items():
                patch[path] = value
            return patch

        return patch

    def _execute_operation(
        self,
        schema: UISchema,
        operation: str,
        params: dict[str, Any],
        target_path: str
    ) -> dict[str, Any]:
        """
        执行通用操作

        支持的操作：
        - append_to_list: 向列表添加元素
        - prepend_to_list: 向列表开头添加元素
        - remove_from_list: 从列表中删除元素（支持 index: -1 批量删除所有匹配项）
        - remove_last: 删除列表最后一项
        - update_list_item: 更新列表中的某个元素
        - clear_all_params: 清空所有 params
        - append_block: 添加新块到 schema
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
        print(f"[InstanceService] _execute_operation: operation={operation}, params={params}, target_path={target_path}")

        patch = {}

        if operation == "append_to_list":
            # 向列表添加元素
            current_list = self._get_nested_value(schema, target_path, [])
            items = params.get("items", [])
            # 渲染 items 中的模板变量
            if isinstance(items, list):
                items_to_add = []
                for single_item in items:
                    if isinstance(single_item, dict):
                        items_to_add.append(self._render_dict_template(schema, single_item))
                    else:
                        items_to_add.append(single_item)
                patch[target_path] = current_list + items_to_add
            else:
                # 兼容单个元素的情况（向后兼容）
                if isinstance(items, dict):
                    items = self._render_dict_template(schema, items)
                patch[target_path] = current_list + [items]

        elif operation == "prepend_to_list":
            # 向列表开头添加元素
            current_list = self._get_nested_value(schema, target_path, [])
            items = params.get("items", [])
            # 渲染 items 中的模板变量
            if isinstance(items, list):
                items_to_add = []
                for single_item in items:
                    if isinstance(single_item, dict):
                        items_to_add.append(self._render_dict_template(schema, single_item))
                    else:
                        items_to_add.append(single_item)
                patch[target_path] = items_to_add + current_list
            else:
                # 兼容单个元素的情况（向后兼容）
                if isinstance(items, dict):
                    items = self._render_dict_template(schema, items)
                patch[target_path] = [items] + current_list

        elif operation == "remove_from_list":
            # 从列表中删除元素
            current_list = self._get_nested_value(schema, target_path, [])
            if isinstance(current_list, list):
                item_key = params.get("key", "id")
                item_value = params.get("value")

                # 支持 index: -1 表示删除所有满足条件的项
                if params.get("index") == -1 and item_value:
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
            current_list = self._get_nested_value(schema, target_path, [])
            if isinstance(current_list, list) and len(current_list) > 0:
                patch[target_path] = current_list[:-1]

        elif operation == "update_list_item":
            # 更新列表中的某个元素
            current_list = self._get_nested_value(schema, target_path, [])
            if isinstance(current_list, list):
                item_key = params.get("key", "id")
                item_value = params.get("value")
                updates = params.get("updates", {})
                # 渲染 updates 中的模板变量
                if isinstance(updates, dict):
                    updates = self._render_dict_template(schema, updates)
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
            current_params = self._get_nested_value(schema, "state.params", {})
            for key in current_params.keys():
                patch[f"state.params.{key}"] = ""

        elif operation == "append_block":
            # 添加新块到 schema
            block_data = params.get("block")
            if block_data:
                new_blocks = list(schema.blocks) + [Block(**block_data)]
                # 转换为字典以便 JSON 序列化
                patch["blocks"] = [block.model_dump(by_alias=True) for block in new_blocks]

        elif operation == "prepend_block":
            # 在开头添加新块
            block_data = params.get("block")
            if block_data:
                new_blocks = [Block(**block_data)] + list(schema.blocks)
                # 转换为字典以便 JSON 序列化
                patch["blocks"] = [block.model_dump(by_alias=True) for block in new_blocks]

        elif operation == "remove_block":
            # 删除块
            block_id = params.get("block_id")
            if block_id:
                new_blocks = [block for block in schema.blocks if block.id != block_id]
                # 转换为字典以便 JSON 序列化
                patch["blocks"] = [block.model_dump(by_alias=True) for block in new_blocks]

        elif operation == "update_block":
            # 更新块
            block_id = params.get("block_id")
            updates = params.get("updates", {})
            if block_id:
                new_blocks = []
                for block in schema.blocks:
                    if block.id == block_id:
                        # 创建更新后的 block
                        block_dict = block.model_dump(by_alias=True)
                        block_dict.update(updates)
                        new_blocks.append(Block(**block_dict))
                    else:
                        new_blocks.append(block)
                # 转换为字典以便 JSON 序列化
                patch["blocks"] = [block.model_dump(by_alias=True) for block in new_blocks]

        elif operation == "merge":
            # 合并对象
            current_value = self._get_nested_value(schema, target_path, {})
            if isinstance(current_value, dict):
                patch[target_path] = {**current_value, **params.get("data", {})}

        return patch

    def _get_nested_value(
        self,
        schema: UISchema,
        path: str,
        default: Any = None
    ) -> Any:
        """
        从 schema 中获取嵌套值

        Args:
            schema: UISchema 对象
            path: 点分隔路径（如 "state.params.count"）
            default: 默认值

        Returns:
            获取的值或默认值
        """
        parts = path.split(".")
        obj = schema

        print(f"[InstanceService] _get_nested_value: path='{path}', parts={parts}")

        try:
            for i, part in enumerate(parts):
                print(f"[InstanceService]  获取第 {i} 层: part='{part}', 当前obj类型={type(obj).__name__}")

                if isinstance(obj, dict):
                    obj = obj.get(part)
                else:
                    obj = getattr(obj, part)

                print(f"[InstanceService]    获取结果: obj='{obj}'")

                if obj is None:
                    print(f"[InstanceService]    obj is None，返回默认值: default='{default}'")
                    return default
            print(f"[InstanceService] 最终返回: obj='{obj}'")
            return obj
        except (AttributeError, KeyError) as e:
            print(f"[InstanceService] 异常: {e}，返回默认值: default='{default}'")
            return default

    def _render_template(
        self,
        schema: UISchema,
        template: str
    ) -> str:
        """
        渲染模板字符串，支持引用 state 的值

        示例: "表单已提交！姓名: ${state.params.name}"

        Args:
            schema: 当前 schema
            template: 模板字符串

        Returns:
            渲染后的字符串
        """
        import re

        result = template
        print(f"[InstanceService] _render_template 开始: template='{template}'")

        # 匹配 ${path} 格式的占位符
        pattern = r'\$\{([^}]+)\}'

        def replace_match(match):
            path = match.group(1)
            print(f"[InstanceService] 替换占位符: path='{path}'")
            value = self._get_nested_value(schema, path, "")
            print(f"[InstanceService] 获取到的值: value='{value}'")
            return str(value)

        result = re.sub(pattern, replace_match, result)
        print(f"[InstanceService] _render_template 完成: result='{result}'")
        return result

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
        渲染字典中的模板值

        Args:
            schema: 当前 schema
            template_dict: 包含模板的字典

        Returns:
            渲染后的字典
        """
        result = {}
        for key, value in template_dict.items():
            if isinstance(value, str):
                result[key] = self._render_template(schema, value)
            elif isinstance(value, dict):
                result[key] = self._render_dict_template(schema, value)
            elif isinstance(value, list):
                result[key] = [
                    self._render_template(schema, item) if isinstance(item, str)
                    else self._render_dict_template(schema, item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

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
