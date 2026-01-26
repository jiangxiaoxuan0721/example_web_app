"""MCP工具实现文件

此文件包含所有MCP工具的具体实现逻辑。
工具定义在tool_definitions.py文件中。
"""

from typing import Any
import httpx
from backend.config import settings

# FastAPI 后端地址（从环境变量读取，默认 localhost:8001）
FASTAPI_BASE_URL = f"http://localhost:{settings.port}"


async def apply_patch_to_fastapi(
    instance_id: str,
    patches: list[dict[str, Any]],
    new_instance_id: str | None = None,
    target_instance_id: str | None = None
) -> dict[str, Any]:
    """通过 HTTP API 调用 FastAPI 后端应用 patch"""
    try:
        async with httpx.AsyncClient() as client:
            # 调用 FastAPI 的 patch 接口
            url = f"{FASTAPI_BASE_URL}/ui/patch"

            payload = {
                "instance_id": instance_id,
                "patches": patches
            }

            if new_instance_id:
                payload["new_instance_id"] = new_instance_id
            if target_instance_id:
                payload["target_instance_id"] = target_instance_id

            response = await client.post(url, json=payload, timeout=10.0)

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "error": f"FastAPI returned status {response.status_code}",
                    "detail": response.text
                }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to call FastAPI: {str(e)}"
        }


async def patch_ui_state_impl(
    instance_id: str,
    patches: list[dict[str, Any]] = [],
    new_instance_id: str | None = None,
    target_instance_id: str | None = None
) -> dict[str, Any]:
    """patch_ui_state工具的实现"""
    # 验证patches
    if not patches:
        return {
            "status": "error",
            "error": "Patches array must be provided"
        }

    # 通过 HTTP API 调用 FastAPI 后端
    result = await apply_patch_to_fastapi(instance_id, patches, new_instance_id, target_instance_id)

    print(f"[MCP] 调用 FastAPI patch: instance_id={instance_id}, patches={patches}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


async def add_field_impl(
    instance_id: str,
    field: dict[str, Any],
    block_index: int | None = 0,
    state_path: str | None = None,
    initial_value: Any | None = None
) -> dict[str, Any]:
    """add_field工具的实现"""
    patches = []

    # 如果提供了state_path和initial_value，先初始化状态
    if state_path is not None:
        value = initial_value
        # 根据字段类型设置默认值
        if value is None:
            field_type = field.get("type", "text")
            if field_type in ["number"]:
                value = 0
            elif field_type in ["checkbox"]:
                value = False
            elif field_type in ["multiselect", "tag"]:
                value = []
            elif field_type in ["progress"]:
                value = {"current": 0, "total": 100, "showLabel": True}
            elif field_type in ["badge"]:
                value = {"count": 0, "label": "", "dot": False, "color": "#f5222d", "showZero": False, "max": 99}
            elif field_type in ["table"]:
                value = []
            elif field_type in ["modal"]:
                value = {"visible": False, "title": "", "content": "", "width": 520, "okText": "确定", "cancelText": "取消"}
            else:
                value = ""

        patches.append({
            "op": "set",
            "path": state_path,
            "value": value
        })

    # 添加字段
    patches.append({
        "op": "add",
        "path": f"blocks.{block_index}.props.fields",
        "value": field
    })

    # 通过 HTTP API 调用 FastAPI 后端
    result = await apply_patch_to_fastapi(instance_id, patches)

    print(f"[MCP] 添加字段: instance_id={instance_id}, block_index={block_index}, field={field}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


async def update_field_impl(
    instance_id: str,
    field_key: str,
    updates: dict[str, Any],
    block_index: int | None = 0,
    update_all: bool | None = False
) -> dict[str, Any]:
    """update_field工具的实现"""
    # 获取当前schema以查找字段
    schema_result = await get_schema_from_fastapi(instance_id)

    if schema_result.get("status") == "error":
        return {
            "status": "error",
            "error": f"Failed to get schema: {schema_result.get('error')}"
        }

    schema = schema_result.get("schema", {})
    blocks = schema.get("blocks", [])

    patches = []

    if update_all:
        # 更新所有块中的匹配字段
        for i, block in enumerate(blocks):
            if block.get("type") != "form" or not block.get("props", {}).get("fields"):
                continue

            fields = block["props"]["fields"]
            for j, field in enumerate(fields):
                field_obj = field if isinstance(field, dict) else field.__dict__
                if field_obj.get("key") == field_key:
                    updated_field = field_obj.copy()
                    updated_field.update(updates)
                    patches.append({
                        "op": "set",
                        "path": f"blocks.{i}.props.fields.{j}",
                        "value": updated_field
                    })
    else:
        # 验证块索引有效
        if block_index is None or block_index >= len(blocks):
            return {
                "status": "error",
                "error": f"Block index {block_index} out of range. Only {len(blocks)} blocks available."
            }

        # 检查是否是表单块
        block = blocks[block_index]
        if block.get("type") != "form" or not block.get("props", {}).get("fields"):
            return {
                "status": "error",
                "error": f"Block at index {block_index} is not a form block or has no fields."
            }

        # 查找字段
        fields = block["props"]["fields"]
        field_index = -1

        for i, field in enumerate(fields):
            field_obj = field if isinstance(field, dict) else field.__dict__
            if field_obj.get("key") == field_key:
                field_index = i
                break

        if field_index == -1:
            return {
                "status": "error",
                "error": f"Field with key '{field_key}' not found in block {block_index}."
            }

        # 更新字段
        field_obj = fields[field_index]
        updated_field = field_obj if isinstance(field_obj, dict) else field_obj.__dict__.copy()
        updated_field.update(updates)

        patches.append({
            "op": "set",
            "path": f"blocks.{block_index}.props.fields.{field_index}",
            "value": updated_field
        })

    # 通过 HTTP API 调用 FastAPI 后端
    result = await apply_patch_to_fastapi(instance_id, patches)

    print(f"[MCP] 更新字段: instance_id={instance_id}, field_key={field_key}, updates={updates}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


async def remove_field_impl(
    instance_id: str,
    field_key: str,
    block_index: int | None = 0,
    remove_all: bool | None = False
) -> dict[str, Any]:
    """remove_field工具的实现"""
    # 获取当前schema以查找字段
    schema_result = await get_schema_from_fastapi(instance_id)

    if schema_result.get("status") == "error":
        return {
            "status": "error",
            "error": f"Failed to get schema: {schema_result.get('error')}"
        }

    schema = schema_result.get("schema", {})
    blocks = schema.get("blocks", [])

    patches = []

    if remove_all:
        # 删除所有块中的匹配字段
        for i, block in enumerate(blocks):
            if block.get("type") != "form" or not block.get("props", {}).get("fields"):
                continue

            fields = block["props"]["fields"]
            has_field = any(
                (field if isinstance(field, dict) else field.__dict__).get("key") == field_key
                for field in fields
            )

            if has_field:
                patches.append({
                    "op": "remove",
                    "path": f"blocks.{i}.props.fields",
                    "value": {"key": field_key}
                })
    else:
        # 验证块索引有效
        if block_index is None or block_index >= len(blocks):
            return {
                "status": "error",
                "error": f"Block index {block_index} out of range. Only {len(blocks)} blocks available."
            }

        # 检查是否是表单块
        block = blocks[block_index]
        if block.get("type") != "form" or not block.get("props", {}).get("fields"):
            return {
                "status": "error",
                "error": f"Block at index {block_index} is not a form block or has no fields."
            }

        # 查找字段
        fields = block["props"]["fields"]
        has_field = any(
            (field if isinstance(field, dict) else field.__dict__).get("key") == field_key
            for field in fields
        )

        if not has_field:
            return {
                "status": "error",
                "error": f"Field with key '{field_key}' not found in block {block_index}."
            }

        # 删除字段
        patches.append({
            "op": "remove",
            "path": f"blocks.{block_index}.props.fields",
            "value": {"key": field_key}
        })

    # 通过 HTTP API 调用 FastAPI 后端
    result = await apply_patch_to_fastapi(instance_id, patches)

    print(f"[MCP] 删除字段: instance_id={instance_id}, field_key={field_key}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


async def add_block_impl(
    instance_id: str,
    block: dict[str, Any],
    position: str | None = "end"
) -> dict[str, Any]:
    """add_block工具的实现"""
    # 获取当前schema以确定位置
    schema_result = await get_schema_from_fastapi(instance_id)

    if schema_result.get("status") == "error":
        return {
            "status": "error",
            "error": f"Failed to get schema: {schema_result.get('error')}"
        }

    schema = schema_result.get("schema", {})
    blocks = schema.get("blocks", [])

    # 确定插入位置
    if position == "start" or position == "0":
        # 使用insert操作在开始位置插入
        patches = [{
            "op": "insert",
            "path": "blocks",
            "index": 0,
            "value": block
        }]
    elif isinstance(position, int) and 0 <= position < len(blocks):
        # 在指定索引处插入
        patches = [{
            "op": "insert",
            "path": "blocks",
            "index": position,
            "value": block
        }]
    else:
        # 在末尾添加
        patches = [{
            "op": "add",
            "path": "blocks",
            "value": block
        }]

    # 通过 HTTP API 调用 FastAPI 后端
    result = await apply_patch_to_fastapi(instance_id, patches)

    print(f"[MCP] 添加块: instance_id={instance_id}, block={block}, position={position}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


async def remove_block_impl(
    instance_id: str,
    block_id: str,
    remove_all: bool | None = False
) -> dict[str, Any]:
    """remove_block工具的实现"""
    patches = []

    if remove_all:
        # 删除所有匹配的块
        patches.append({
            "op": "remove",
            "path": "blocks",
            "value": {"id": block_id, "remove_all": True}
        })
    else:
        # 删除单个块
        patches.append({
            "op": "remove",
            "path": "blocks",
            "value": {"id": block_id}
        })

    # 通过 HTTP API 调用 FastAPI 后端
    result = await apply_patch_to_fastapi(instance_id, patches)

    print(f"[MCP] 删除块: instance_id={instance_id}, block_id={block_id}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


async def add_action_impl(
    instance_id: str,
    action: dict[str, Any],
    block_index: int | None = None
) -> dict[str, Any]:
    """add_action工具的实现"""
    patches = []

    if block_index is not None:
        # 添加到块级别的actions
        patches.append({
            "op": "add",
            "path": f"blocks.{block_index}.props.actions",
            "value": action
        })
    else:
        # 添加到全局actions
        patches.append({
            "op": "add",
            "path": "actions",
            "value": action
        })

    # 通过 HTTP API 调用 FastAPI 后端
    result = await apply_patch_to_fastapi(instance_id, patches)

    print(f"[MCP] 添加action: instance_id={instance_id}, action={action}, block_index={block_index}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


async def remove_action_impl(
    instance_id: str,
    action_id: str,
    block_index: int | None = None,
    remove_all: bool | None = False
) -> dict[str, Any]:
    """remove_action工具的实现"""
    patches = []

    if remove_all:
        # 删除所有匹配的action（全局和块级别）
        patches.append({
            "op": "remove",
            "path": "actions",
            "value": {"id": action_id, "remove_all": True}
        })
    elif block_index is not None:
        # 从指定块中删除action
        patches.append({
            "op": "remove",
            "path": f"blocks.{block_index}.props.actions",
            "value": {"id": action_id}
        })
    else:
        # 从全局actions中删除
        patches.append({
            "op": "remove",
            "path": "actions",
            "value": {"id": action_id}
        })

    # 通过 HTTP API 调用 FastAPI 后端
    result = await apply_patch_to_fastapi(instance_id, patches)

    print(f"[MCP] 删除action: instance_id={instance_id}, action_id={action_id}, block_index={block_index}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


async def get_schema_from_fastapi(instance_id: str | None = None) -> dict[str, Any]:
    """通过 HTTP API 从 FastAPI 获取 Schema"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{FASTAPI_BASE_URL}/ui/schema"
            if instance_id:
                url += f"?instanceId={instance_id}"

            response = await client.get(url, timeout=10.0)

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "error": f"FastAPI returned status {response.status_code}",
                    "detail": response.text
                }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to call FastAPI: {str(e)}"
        }


async def get_schema_impl(instance_id: str | None = None) -> dict[str, Any]:
    """get_schema工具的实现"""
    # 通过 HTTP API 调用 FastAPI 后端
    return await get_schema_from_fastapi(instance_id)


async def list_instances_from_fastapi() -> dict[str, Any]:
    """通过 HTTP API 从 FastAPI 获取实例列表"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{FASTAPI_BASE_URL}/ui/instances"
            response = await client.get(url, timeout=10.0)

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "error": f"FastAPI returned status {response.status_code}",
                    "detail": response.text
                }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to call FastAPI: {str(e)}"
        }


async def list_instances_impl() -> dict[str, Any]:
    """list_instances工具的实现"""
    # 通过 HTTP API 调用 FastAPI 后端
    return await list_instances_from_fastapi()


async def access_instance_from_fastapi(instance_id: str) -> dict[str, Any]:
    """通过 HTTP API 访问指定实例"""
    try:
        async with httpx.AsyncClient() as client:
            # 设置实例状态为活跃
            url = f"{FASTAPI_BASE_URL}/ui/access"
            payload = {"instance_id": instance_id}
            response = await client.post(url, json=payload, timeout=10.0)

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "error": f"FastAPI returned status {response.status_code}",
                    "detail": response.text
                }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to call FastAPI: {str(e)}"
        }


async def access_instance_impl(instance_id: str) -> dict[str, Any]:
    """access_instance工具的实现"""
    print(f"[MCP] 访问实例: {instance_id}")
    result = await access_instance_from_fastapi(instance_id)
    print(f"[MCP] 访问结果: {result}")
    return result


async def validate_completion_impl(
    instance_id: str,
    intent: str,
    completion_criteria: list[dict[str, Any]]
) -> dict[str, Any]:
    """validate_completion工具的实现"""
    
    try:
        # 首先获取当前实例的Schema
        schema_result = await get_schema_from_fastapi(instance_id)
        
        if schema_result.get("status") == "error":
            return {
                "evaluation": {
                    "passed_criteria": 0,
                    "total_criteria": 0,
                    "completion_ratio": 0,
                    "detailed_results": []
                },
                "summary": f"Failed to retrieve schema for validation: {schema_result.get('error')}",
                "recommendations": ["Ensure instance_id exists and is accessible"]
            }
        
        schema = schema_result.get("schema", {})
        results = []
        
        # 评估每个完成标准
        for criterion in completion_criteria:
            criterion_type = criterion.get("type")
            result = {
                "type": criterion_type,
                "description": criterion.get("description", ""),
                "passed": False,
                "details": ""
            }
            
            # 根据类型执行不同的验证逻辑
            if criterion_type == "field_exists":
                path = criterion.get("path", "")
                field_value = get_nested_value(schema, path)
                result["passed"] = field_value is not None
                result["details"] = f"Field '{path}' exists: {result['passed']}"
                
            elif criterion_type == "field_value":
                path = criterion.get("path", "")
                expected_value = criterion.get("value")
                actual_value = get_nested_value(schema, path)
                result["passed"] = actual_value == expected_value
                result["details"] = f"Field '{path}' value: {actual_value} (expected: {expected_value})"
                
            elif criterion_type == "block_count":
                expected_count = criterion.get("count", 0)
                blocks = schema.get("blocks", [])
                actual_count = len(blocks)
                result["passed"] = actual_count == expected_count
                result["details"] = f"Block count: {actual_count} (expected: {expected_count})"
                
            elif criterion_type == "action_exists":
                action_id = criterion.get("path", "")
                actions = schema.get("actions", [])
                found = any(action.get("id") == action_id for action in actions)
                result["passed"] = found
                result["details"] = f"Action '{action_id}' exists: {found}"
                
            elif criterion_type == "custom":
                # 自定义条件可以基于JSONPath或其他表达式
                # 这里简化实现，实际应该有更复杂的表达式解析
                condition = criterion.get("condition", "")
                result["passed"] = evaluate_custom_condition(schema, condition)
                result["details"] = f"Custom condition '{condition}': {result['passed']}"
            
            results.append(result)
        
        # 计算评估指标
        passed_count = sum(1 for r in results if r["passed"])
        total_count = len(results)
        
        # 生成总结和建议
        if total_count > 0 and passed_count == total_count:
            summary = f"UI instance '{instance_id}' meets all evaluated criteria for intent: '{intent}'"
            recommendations = ["All criteria satisfied - Agent should consider stopping modifications"]
        elif total_count == 0:
            summary = f"UI instance '{instance_id}' has no criteria to evaluate for intent: '{intent}'"
            recommendations = ["Define specific completion criteria to guide further work"]
        else:
            summary = f"UI instance '{instance_id}' meets {passed_count}/{total_count} criteria for intent: '{intent}'"
            recommendations = []
            for result in results:
                if not result["passed"]:
                    recommendations.append(f"Address: {result['details']}")
        
        return {
            "evaluation": {
                "passed_criteria": passed_count,
                "total_criteria": total_count,
                "completion_ratio": passed_count / total_count if total_count > 0 else 0,
                "detailed_results": results
            },
            "summary": summary,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "evaluation": {
                "passed_criteria": 0,
                "total_criteria": 0,
                "completion_ratio": 0,
                "detailed_results": []
            },
            "summary": f"Validation failed with error: {str(e)}",
            "recommendations": ["Check validation criteria and try again"]
        }


def get_nested_value(obj: Any, path: str) -> Any:
    """从嵌套字典中获取值，支持点分隔路径和数组索引"""
    if not path:
        return obj
    
    keys = path.split(".")
    current: Any = obj
    
    for key in keys:
        # Handle array indices
        if key.isdigit():
            index = int(key)
            if isinstance(current, list) and 0 <= index < len(current):
                current = current[index]
            else:
                return None
        # Handle dictionary keys
        elif isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current


def evaluate_custom_condition(schema: dict[str, Any], condition: str) -> bool:
    """评估自定义条件（简化实现）"""
    # 这里应该有更复杂的表达式解析
    # 目前只是简单地检查某些条件
    
    if condition.startswith("has_field:"):
        field_path = condition.split(":", 1)[1]
        return get_nested_value(schema, field_path) is not None
    
    if condition.startswith("field_value:"):
        parts = condition.split(":", 2)
        if len(parts) == 3:
            field_path = parts[1]
            expected_value = parts[2]
            actual_value = get_nested_value(schema, field_path)
            return str(actual_value) == expected_value
    
    if condition.startswith("count_blocks:"):
        expected = int(condition.split(":", 1)[1])
        actual = len(schema.get("blocks", []))
        return actual == expected
    
    if condition.startswith("count_fields:"):
        parts = condition.split(":", 1)
        if len(parts) == 2:
            field_path = parts[1]
            field_container = get_nested_value(schema, field_path)
            return isinstance(field_container, list) and len(field_container) >= 3
    
    if condition.startswith("has_action:"):
        action_id = condition.split(":", 1)[1]
        actions = schema.get("actions", [])
        return any(action.get("id") == action_id for action in actions)
    
    return False