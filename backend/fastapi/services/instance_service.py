"""实例服务 - 处理实例的创建、删除和操作"""

import httpx
from typing import Dict, Any, Optional
from ..models import UISchema, MetaInfo, StateInfo, LayoutInfo, Block, ActionConfig, StepInfo, FieldConfig
from backend.core.manager import SchemaManager
from .patch import apply_patch_to_schema


class InstanceService:
    """实例服务"""

    def __init__(self, schema_manager: SchemaManager):
        self.schema_manager = schema_manager

    def create_instance(
        self,
        instance_id: str,
        patches: list[Dict[str, Any]]
    ) -> tuple[bool, Optional[str]]:
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
                    meta=MetaInfo(
                        pageKey=getattr(meta_data, "pageKey", instance_id),
                        step=StepInfo(**getattr(meta_data, "step", {"current": 1, "total": 1})),
                        status=getattr(meta_data, "status", "idle")
                    ),
                    state=StateInfo(params={}, runtime={}),
                    layout=LayoutInfo(type="single"),
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
                            converted_fields = [FieldConfig(**field) for field in fields_data]
                            props_copy['fields'] = converted_fields
                            block_copy['props'] = props_copy
                        converted_blocks.append(Block(**block_copy))
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
    ) -> tuple[bool, Optional[str]]:
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
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理实例的 action 操作（通用化处理）

        返回: Patch 数据字典
        """
        schema = self.schema_manager.get(instance_id)
        if not schema:
            return {
                "status": "error",
                "error": f"Instance '{instance_id}' not found"
            }

        # 先同步前端传来的 params
        if params and isinstance(params, dict):
            params_patch = {f"state.params.{k}": v for k, v in params.items()}
            apply_patch_to_schema(schema, params_patch)

        # 查找对应的 action 配置
        action_config = None
        for action in schema.actions:
            if action.id == action_id:
                action_config = action
                break

        if not action_config:
            return {
                "status": "success",
                "patch": {}
            }

        # 处理 navigate 类型的 action
        if action_config.action_type == "navigate":
            return {
                "status": "success",
                "patch": {},
                "navigate_to": action_config.target_instance
            }

        # 通用 action 处理
        patch = self._execute_action_handler(schema, action_config)

        # 应用 patch 到 schema
        if patch:
            apply_patch_to_schema(schema, patch)

        return {
            "status": "success",
            "patch": patch
        }

    def _execute_action_handler(
        self,
        schema: UISchema,
        action_config: Any
    ) -> Dict[str, Any]:
        """
        执行 action 处理器（通用逻辑）

        Args:
            schema: 当前 schema
            action_config: action 配置

        Returns:
            Patch 字典
        """
        handler_type = getattr(action_config, "handler_type", None)
        patches_config = getattr(action_config, "patches", {})

        if not patches_config:
            return {}

        patch = {}

        if handler_type == "set":
            # 直接设置值
            for path, value in patches_config.items():
                patch[path] = value

        elif handler_type == "increment":
            # 数值增加
            for path, delta in patches_config.items():
                current_value = self._get_nested_value(schema, path, 0)
                try:
                    patch[path] = current_value + int(delta)
                except (ValueError, TypeError):
                    patch[path] = current_value

        elif handler_type == "decrement":
            # 数值减少
            for path, delta in patches_config.items():
                current_value = self._get_nested_value(schema, path, 0)
                try:
                    patch[path] = current_value - int(delta)
                except (ValueError, TypeError):
                    patch[path] = current_value

        elif handler_type == "toggle":
            # 布尔值切换
            for path, _ in patches_config.items():
                current_value = self._get_nested_value(schema, path, False)
                patch[path] = not current_value

        elif handler_type == "template":
            # 模板替换（支持引用当前 state 的值）
            for path, template in patches_config.items():
                if isinstance(template, str):
                    patch[path] = self._render_template(schema, template)
                else:
                    patch[path] = template

        elif handler_type == "external":
            # 调用外部 API
            external_patch = self._handle_external_api(schema, patches_config)
            patch.update(external_patch)

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

        try:
            for part in parts:
                if isinstance(obj, dict):
                    obj = obj.get(part)
                else:
                    obj = getattr(obj, part)
                if obj is None:
                    return default
            return obj
        except (AttributeError, KeyError):
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

        # 匹配 ${path} 格式的占位符
        pattern = r'\$\{([^}]+)\}'

        def replace_match(match):
            path = match.group(1)
            value = self._get_nested_value(schema, path, "")
            return str(value)

        result = re.sub(pattern, replace_match, result)
        return result

    def _handle_external_api(
        self,
        schema: UISchema,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理外部 API 调用

        Config 格式:
        {
            "url": "https://api.example.com/endpoint",
            "method": "POST",  # GET/POST/PUT/DELETE
            "headers": {"Authorization": "Bearer token"},
            "body_template": {"key": "${state.params.value}"},  # 可选，支持模板
            "body_template_type": "json",  # json/form/none
            "timeout": 30,
            "response_mappings": {
                "state.params.result": "data.items",  # path: JSON path
                "state.runtime.status": "status"
            },
            "error_mapping": {
                "state.runtime.error": "error.message",
                "state.runtime.status": "error"
            }
        }

        Args:
            schema: 当前 schema
            config: API 配置

        Returns:
            Patch 字典
        """
        url = config.get("url")
        if not url:
            return {}

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
        template_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
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
