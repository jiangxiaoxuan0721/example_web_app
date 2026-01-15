"""MCP Tools for Agent Programmable UI Runtime"""

import asyncio
from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import httpx
from backend.config import settings

# 创建 FastMCP 服务器
mcp = FastMCP("ui-patch-server")

# FastAPI 后端地址（从环境变量读取，默认 localhost:8001）
FASTAPI_BASE_URL = f"http://192.168.130.12:{settings.port}"


async def apply_patch_to_fastapi(
    instance_id: str,
    patches: List[Dict[str, Any]],
    new_instance_id: Optional[str] = None,
    target_instance_id: Optional[str] = None
) -> Dict[str, Any]:
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


@mcp.tool()
async def patch_ui_state(
    instance_id: str,
    patches: List[Dict[str, Any]],
    new_instance_id: Optional[str] = None,
    target_instance_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Apply structured patches to modify UI Schema state and structure.
    This is the ONLY way to modify UI - no direct mutations allowed.

    Args:
        instance_id: Target instance (e.g., "demo", "counter", "form").
                    Use "__CREATE__" to create new instance.
                    Use "__DELETE__" to delete instance.
        patches: Array of patch operations.
        new_instance_id: Required when instance_id == "__CREATE__".
        target_instance_id: Required when instance_id == "__DELETE__".

    Returns:
        Dict containing operation status and details.

    Examples:
        Update state:
            {
                "instance_id": "counter",
                "patches": [
                    {"op": "set", "path": "state.params.count", "value": 42}
                ]
            }

        Create instance:
            {
                "instance_id": "__CREATE__",
                "new_instance_id": "my_instance",
                "patches": [
                    {"op": "set", "path": "meta", "value": {...}},
                    {"op": "set", "path": "state", "value": {...}},
                    {"op": "set", "path": "blocks", "value": []},
                    {"op": "set", "path": "actions", "value": []}
                ]
            }
    """
    # 通过 HTTP API 调用 FastAPI 后端
    result = await apply_patch_to_fastapi(instance_id, patches, new_instance_id, target_instance_id)

    print(f"[MCP] 调用 FastAPI patch: instance_id={instance_id}, patches={patches}")
    print(f"[MCP] FastAPI 响应: {result}")

    return result


async def get_schema_from_fastapi(instance_id: Optional[str] = None) -> Dict[str, Any]:
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


@mcp.tool()
async def get_schema(instance_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current UI Schema for an instance.

    Args:
        instance_id: Instance ID (e.g., "demo", "counter", "form").
                    If not provided, returns default instance ("demo").

    Returns:
        Dict containing the UI Schema.
    """
    # 通过 HTTP API 调用 FastAPI 后端
    return await get_schema_from_fastapi(instance_id)


async def list_instances_from_fastapi() -> Dict[str, Any]:
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


@mcp.tool()
async def list_instances() -> Dict[str, Any]:
    """
    List all available UI Schema instances.

    Returns:
        Dict containing list of available instances and their metadata.
    """
    # 通过 HTTP API 调用 FastAPI 后端
    return await list_instances_from_fastapi()


async def access_instance_from_fastapi(instance_id: str) -> Dict[str, Any]:
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


@mcp.tool()
async def access_instance(instance_id: str) -> Dict[str, Any]:
    """
    Access a specific UI instance and mark it as active.

    Args:
        instance_id: Instance ID to access (e.g., "demo", "counter", "form").

    Returns:
        Dict containing operation status and the instance schema.
    """
    print(f"[MCP] 访问实例: {instance_id}")
    result = await access_instance_from_fastapi(instance_id)
    print(f"[MCP] 访问结果: {result}")
    return result


# 启动 MCP 服务器（用于本地测试）
if __name__ == "__main__":
    import os

    print("🚀 Starting MCP Server for UI Patch Tool...")
    print("📝 Available tools:")
    print("  - patch_ui_state: Apply structured patches to modify UI")
    print("  - get_schema: Get current UI Schema")
    print("  - list_instances: List all available instances")
    print("  - access_instance: Access a specific UI instance and mark it as active")
    print()
    mcp.run(
        transport="streamable-http",
        port=8766,
        host="0.0.0.0",
        path="/mcp",
    )
