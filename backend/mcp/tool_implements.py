"""MCP工具实现文件

此文件包含所有MCP工具的具体实现逻辑。
工具定义在tool_definitions.py文件中。

架构原则：
- patch_ui_state 是万能工具，是唯一的修改工具
- 其他工具（get_schema、list_instances、switch_to_instance、validate_completion）是只读或辅助工具
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


# ==================== 万能修改工具 ====================

async def patch_ui_state_impl(
    instance_id: str,
    patches: list[dict[str, Any]] = [],
    new_instance_id: str | None = None,
    target_instance_id: str | None = None
) -> dict[str, Any]:
    """patch_ui_state 工具的实现"""
    # 验证 patches
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


# ==================== 只读查询工具 ====================

async def get_schema_from_fastapi(instance_id: str | None = None) -> dict[str, Any]:
    """从 FastAPI 后端获取 schema"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{FASTAPI_BASE_URL}/ui/schema"
            # 总是传递 params，即使 instance_id 为 None，让后端决定使用默认值
            params = {"instance_id": instance_id} if instance_id is not None else None

            response = await client.get(url, params=params, timeout=10.0)
            
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
    """get_schema 工具的实现"""
    result = await get_schema_from_fastapi(instance_id)
    print(f"[MCP] 获取 schema: instance_id={instance_id or 'default'}, result={result}")
    return result


async def list_instances_impl() -> dict[str, Any]:
    """list_instances 工具的实现"""
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


async def switch_to_instance_impl(instance_id: str) -> dict[str, Any]:
    """switch_to_instance 工具的实现"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{FASTAPI_BASE_URL}/ui/switch"

            payload = {"instance_id": instance_id}

            response = await client.post(url, json=payload, timeout=10.0)

            if response.status_code == 200:
                result = response.json()
                print(f"[MCP] 切换实例: instance_id={instance_id}, result={result}")
                return result
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


# ==================== 验证工具 ====================

async def validate_completion_impl(
    instance_id: str,
    intent: str,
    completion_criteria: list[dict[str, Any]]
) -> dict[str, Any]:
    """validate_completion 工具的实现"""
    # 先获取当前 schema
    schema_result = await get_schema_from_fastapi(instance_id)
    
    if schema_result.get("status") == "error":
        return {
            "status": "error",
            "error": f"Failed to get schema for validation: {schema_result.get('error')}"
        }
    
    schema = schema_result.get("schema", {})
    
    # 评估每个标准
    passed_criteria = 0
    detailed_results = []
    
    for criterion in completion_criteria:
        criterion_type = criterion.get("type")
        description = criterion.get("description", "")
        
        try:
            if criterion_type == "field_exists":
                # 检查字段路径是否存在
                path = criterion.get("path", "")
                if _get_nested_value(schema, path) is not None:
                    passed_criteria += 1
                    detailed_results.append({
                        "criterion": description,
                        "passed": True,
                        "actual": "exists",
                        "expected": "exists"
                    })
                else:
                    detailed_results.append({
                        "criterion": description,
                        "passed": False,
                        "actual": "not found",
                        "expected": "exists"
                    })
            
            elif criterion_type == "field_value":
                # 检查字段值
                path = criterion.get("path", "")
                expected_value = criterion.get("value")
                actual_value = _get_nested_value(schema, path)
                
                if actual_value == expected_value:
                    passed_criteria += 1
                    detailed_results.append({
                        "criterion": description,
                        "passed": True,
                        "actual": actual_value,
                        "expected": expected_value
                    })
                else:
                    detailed_results.append({
                        "criterion": description,
                        "passed": False,
                        "actual": actual_value,
                        "expected": expected_value
                    })
            
            elif criterion_type == "block_count":
                # 检查 block 数量
                expected_count = criterion.get("count", 0)
                actual_count = len(schema.get("blocks", []))
                
                if actual_count == expected_count:
                    passed_criteria += 1
                    detailed_results.append({
                        "criterion": description,
                        "passed": True,
                        "actual": actual_count,
                        "expected": expected_count
                    })
                else:
                    detailed_results.append({
                        "criterion": description,
                        "passed": False,
                        "actual": actual_count,
                        "expected": expected_count
                    })
            
            elif criterion_type == "action_exists":
                # 检查 action 是否存在
                action_id = criterion.get("path", "")
                exists = _action_exists(schema, action_id)
                
                if exists:
                    passed_criteria += 1
                    detailed_results.append({
                        "criterion": description,
                        "passed": True,
                        "actual": "exists",
                        "expected": "exists"
                    })
                else:
                    detailed_results.append({
                        "criterion": description,
                        "passed": False,
                        "actual": "not found",
                        "expected": "exists"
                    })
            
            elif criterion_type == "custom":
                # 自定义验证（这里简化处理，实际应该评估条件表达式）
                condition = criterion.get("condition", "")
                detailed_results.append({
                    "criterion": description,
                    "passed": True,  # 默认通过
                    "actual": "custom",
                    "expected": condition
                })
                passed_criteria += 1
            
            else:
                detailed_results.append({
                    "criterion": description,
                    "passed": False,
                    "actual": "unknown criterion type",
                    "expected": criterion_type
                })
        
        except Exception as e:
            detailed_results.append({
                "criterion": description,
                "passed": False,
                "actual": f"error: {str(e)}",
                "expected": "success"
            })
    
    total_criteria = len(completion_criteria)
    completion_ratio = passed_criteria / total_criteria if total_criteria > 0 else 0
    
    # 生成摘要和建议
    summary = f"通过 {passed_criteria}/{total_criteria} 个标准"
    recommendations = []
    
    if completion_ratio >= 1.0:
        summary += " - 全部通过！✅"
    else:
        summary += f" - 还需 {total_criteria - passed_criteria} 个改进"
        recommendations.append("查看详细结果以了解未通过的标准")
    
    return {
        "status": "success",
        "evaluation": {
            "passed_criteria": passed_criteria,
            "total_criteria": total_criteria,
            "completion_ratio": completion_ratio,
            "detailed_results": detailed_results,
            "summary": summary,
            "recommendations": recommendations
        }
    }


# ==================== 辅助函数 ====================

def _get_nested_value(obj: dict[str, Any], path: str) -> Any:
    """从嵌套对象中获取值（支持点号分隔的路径）"""
    if not path:
        return None
    
    keys = path.split('.')
    current = obj
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current


def _action_exists(schema: dict[str, Any], action_id: str) -> bool:
    """检查 action 是否存在于全局或 block 中"""
    # 检查全局 actions
    global_actions = schema.get("actions", [])
    for action in global_actions:
        if action.get("id") == action_id:
            return True
    
    # 检查 block 级别的 actions
    blocks = schema.get("blocks", [])
    for block in blocks:
        block_actions = block.get("props", {}).get("actions", [])
        for action in block_actions:
            if action.get("id") == action_id:
                return True
    
    return False
