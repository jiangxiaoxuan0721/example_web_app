"""MCP工具实现文件

此文件包含所有MCP工具的具体实现逻辑。
工具定义在tool_definitions.py文件中。

架构原则：
- patch_ui_state 是万能工具，是唯一的修改工具
- 其他工具（get_schema、list_instances、switch_to_instance、validate_completion）是只读或辅助工具
"""

from httpx._models import Response
from typing import Any
import httpx
from backend.config import settings
# FastAPI 后端地址（从环境变量读取，默认 localhost:8001）
FASTAPI_BASE_URL: str = f"http://localhost:{settings.port}"


async def apply_patch_to_fastapi(
    instance_name: str,
    patches: list[dict[str, Any]],
    new_instance_name: str | None = None,
    target_instance_name: str | None = None
) -> dict[str, Any]:
    """通过 HTTP API 调用 FastAPI 后端应用 patch"""
    try:
        async with httpx.AsyncClient() as client:
            # 调用 FastAPI 的 patch 接口
            url: str = f"{FASTAPI_BASE_URL}/ui/patch"

            payload: dict[str, str | list[dict[str, Any]]] = {
                "instance_name": instance_name,
                "patches": patches
            }

            if new_instance_name:
                payload["new_instance_name"] = new_instance_name
            if target_instance_name:
                payload["target_instance_name"] = target_instance_name

            response: Response = await client.post(url, json=payload, timeout=10.0)

            if response.status_code == 200:
                # 创建成功后，切换到新创建的实例
                actual_instance = new_instance_name if new_instance_name else instance_name
                _ = await switch_to_instance_impl(actual_instance)
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
    instance_name: str,
    patches: list[dict[str, Any]] = [],
    new_instance_name: str | None = None,
    target_instance_name: str | None = None
) -> dict[str, Any]:
    """patch_ui_state 工具的实现"""
    # 验证 patches
    if not patches:
        return {
            "status": "error",
            "error": "Patches array must be provided"
        }

    # 通过 HTTP API 调用 FastAPI 后端
    result: dict[str, Any] = await apply_patch_to_fastapi(instance_name, patches, new_instance_name, target_instance_name)

    print(f"[MCP] 调用 FastAPI patch: instance_name={instance_name}, patches={patches}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


# ==================== 只读查询工具 ====================

async def get_schema_from_fastapi(instance_name: str | None = None) -> dict[str, Any]:
    """从 FastAPI 后端获取 schema"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{FASTAPI_BASE_URL}/ui/schema"
            # 使用驼峰命名 instanceId，与后端 Query(alias="instanceId") 保持一致
            params = {"instanceId": instance_name} if instance_name is not None else None

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


async def get_schema_impl(instance_name: str | None = None) -> dict[str, Any]:
    """get_schema 工具的实现"""
    result = await get_schema_from_fastapi(instance_name)
    print(f"[MCP] 获取 schema: instance_name={instance_name or 'default'}, result={result}")
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


async def switch_to_instance_impl(instance_name: str) -> dict[str, Any]:
    """switch_to_instance 工具的实现（已废弃，使用 switch_ui_impl）"""
    return await switch_ui_impl(instance_name=instance_name, block_id=None)


async def switch_ui_impl(instance_name: str | None, block_id: str | None) -> dict[str, Any]:
    """switch_ui 工具的实现"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{FASTAPI_BASE_URL}/ui/switch"

            payload = {}
            if instance_name:
                payload["instance_name"] = instance_name
            if block_id:
                payload["block_id"] = block_id

            response: Response = await client.post(url, json=payload, timeout=10.0)

            if response.status_code == 200:
                result = response.json()
                print(f"[MCP] 切换UI: instance_name={instance_name}, block_id={block_id}, result={result}")
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

async def validate_completion_impl(instance_name: str) -> dict[str, Any]:
    """validate_completion 工具的实现 - 诊断UI实例状态"""
    # 获取 schema
    schema_result = await get_schema_from_fastapi(instance_name)

    if schema_result.get("status") == "error":
        return {
            "status": "error",
            "error": schema_result.get("error")
        }

    schema = schema_result.get("schema", {})

    # 调试信息
    blocks = schema.get("blocks", [])
    state = schema.get("state", {})
    params = state.get("params", {})
    runtime = state.get("runtime", {})

    field_count: int = 0
    action_count: int = 0

    debug_info = {
        "instance_exists": True,
        "instance_name": instance_name,
        "block_count": len(blocks),
        "field_count": field_count,
        "action_count": action_count,
        "state_params_keys": list(params.keys()),
        "state_runtime_keys": list(runtime.keys()),
        "layout_type": schema.get("layout", {}).get("type", "unknown")
    }

    # 状态摘要
    state_summary = {
        "params": params,
        "runtime": runtime
    }

    # 收集所有字段和动作
    all_fields: list[dict[str, Any]] = []
    all_actions: list[dict[str, Any]] = []
    structure_summary: list[dict[str, Any]] = []

    for idx, block in enumerate(blocks):
        block_id = block.get("id", f"block_{idx}")
        block_layout = block.get("layout", "unknown")
        block_title = block.get("title", "")
        props = block.get("props", {}) or {}

        block_fields = props.get("fields", []) or []
        block_actions = props.get("actions", []) or []

        field_count += len(block_fields) if isinstance(block_fields, list) else 0
        action_count += len(block_actions) if isinstance(block_actions, list) else 0

        # 构建块摘要
        block_summary = {
            "id": block_id,
            "title": block_title,
            "layout": block_layout,
            "fields": [{"key": f.get("key"), "type": f.get("type"), "label": f.get("label", "")} for f in block_fields if isinstance(f, dict)],
            "actions": [{"id": a.get("id"), "type": a.get("action_type"), "label": a.get("label", "")} for a in block_actions if isinstance(a, dict)]
        }
        structure_summary.append(block_summary)

        # 收集字段详细信息
        if isinstance(block_fields, list):
            for field in block_fields:
                field_key = field.get("key", "")
                field_path = f"state.params.{field_key}" if field_key else "unknown"
                has_value = field_key in params or field.get("value") is not None
                all_fields.append({
                    "key": field_key,
                    "type": field.get("type"),
                    "label": field.get("label", ""),
                    "path": field_path,
                    "has_value": has_value
                })
        
        # 收集动作详细信息
        if isinstance(block_actions, list):
            for action in block_actions:
                action_id = action.get("id", "")
                patches = action.get("patches")
                patch_count = len(patches) if isinstance(patches, list) else 0
                all_actions.append({
                    "id": action_id,
                    "label": action.get("label", ""),
                    "type": action.get("action_type"),
                    "patch_count": patch_count
                })
    
    # 全局 actions（顶层）
    global_actions = schema.get("actions", []) or []
    action_count += len(global_actions) if isinstance(global_actions, list) else 0

    # 将全局 actions 添加到 structure_summary 的第一项（作为特殊的顶层块）
    if global_actions and isinstance(global_actions, list):
        structure_summary.insert(0, {
            "id": "__global__",
            "title": "全局操作 (Global Actions)",
            "layout": "global",
            "fields": [],
            "actions": [{"id": a.get("id"), "type": a.get("action_type"), "label": a.get("label", "")} for a in global_actions if isinstance(a, dict)]
        })

    # 收集全局 actions 到 all_actions
    if isinstance(global_actions, list):
        for action in global_actions:
            if not isinstance(action, dict):
                continue
            action_id = action.get("id", "")
            patches = action.get("patches")
            patch_count = len(patches) if isinstance(patches, list) else 0
            all_actions.append({
                "id": action_id,
                "label": action.get("label", ""),
                "type": action.get("action_type"),
                "patch_count": patch_count,
                "scope": "global"
            })

    # 生成提示
    hints = []

    if len(blocks) == 0:
        hints.append("⚠️ 实例没有任何block，需要添加至少一个block")

    if field_count == 0:
        hints.append("⚠️ 没有任何字段，考虑添加text、number等field类型")

    if action_count == 0:
        hints.append("⚠️ 没有任何action，考虑添加按钮触发patch操作")

    if not any("increment" in str(a.get("id", "")).lower() or "decrement" in str(a.get("id", "")).lower() for a in all_actions):
        if field_count > 0 and any(f.get("type") == "number" for f in all_fields if isinstance(f, dict)):
            hints.append("💡 检测到number字段但无增减action，可添加increment/decrement")

    if not any("table" in str(f.get("type", "")) for f in all_fields if isinstance(f, dict)) and len(all_fields) > 3:
        hints.append("💡 字段较多，考虑使用table组件展示数据")

    if not hints:
        hints.append("✅ 实例结构完整，可以尝试添加更多交互功能")

    # 更新 debug_info 中的计数
    debug_info["field_count"] = field_count
    debug_info["action_count"] = action_count

    return {
        "status": "success",
        "debug_info": debug_info,
        "state_summary": state_summary,
        "structure_summary": structure_summary,
        "fields_summary": all_fields,
        "actions_summary": all_actions,
        "hints": hints
    }
