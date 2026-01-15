"""MCP工具定义文件

此文件定义了所有可用的MCP工具及其参数，但不包含具体实现。
实现逻辑应在tool_implements.py文件中。
"""

from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

# 创建FastMCP服务器实例
mcp = FastMCP("ui-patch-server")

# 工具注册区域 - 所有工具在此处注册但不在本文件中实现

@mcp.tool()
async def patch_ui_state(
    instance_id: str,
    patches: List[Dict[str, Any]] = [],
    new_instance_id: Optional[str] = None,
    target_instance_id: Optional[str] = None,
    field_key: Optional[str] = None,
    updates: Optional[Dict[str, Any]] = None,
    remove_field: Optional[bool] = False,
    block_index: Optional[int] = 0
) -> Dict[str, Any]:
    """
    Apply structured patches to modify UI Schema state and structure.
    This is the ONLY way to modify UI - no direct mutations allowed.
    Enhanced with shortcuts for common field operations.

    Args:
        instance_id: Target instance (e.g., "demo", "counter", "form").
                    Use "__CREATE__" to create new instance.
                    Use "__DELETE__" to delete instance.
        patches: Array of patch operations (optional if using field shortcuts).
        new_instance_id: Required when instance_id == "__CREATE__".
        target_instance_id: Required when instance_id == "__DELETE__".
        field_key: Key of field to update/remove (for shortcut operations).
        updates: Dictionary of field properties to update (for update shortcut).
        remove_field: If True, removes the specified field (for remove shortcut).
        block_index: Index of form block (default: 0, first block).

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

        Update field (shortcut):
            {
                "instance_id": "form",
                "field_key": "email",
                "updates": {
                    "label": "Email Address",
                    "type": "email"
                }
            }

        Remove field (shortcut):
            {
                "instance_id": "form",
                "field_key": "email",
                "remove_field": True
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
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import patch_ui_state_impl
    return await patch_ui_state_impl(
        instance_id, patches, new_instance_id, target_instance_id,
        field_key, updates, remove_field, block_index
    )


@mcp.tool()
async def get_schema(instance_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current UI Schema for an instance.

    Args:
        instance_id: Instance ID (e.g., "demo", "counter", "form").
                    If not provided, returns default instance ("demo").

    Returns:
        Dict containing UI Schema.
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import get_schema_impl
    return await get_schema_impl(instance_id)


@mcp.tool()
async def list_instances() -> Dict[str, Any]:
    """
    List all available UI Schema instances.

    Returns:
        Dict containing list of available instances and their metadata.
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import list_instances_impl
    return await list_instances_impl()


@mcp.tool()
async def access_instance(instance_id: str) -> Dict[str, Any]:
    """
    Access a specific UI instance and mark it as active.

    Args:
        instance_id: Instance ID to access (e.g., "demo", "counter", "form").

    Returns:
        Dict containing operation status and instance schema.
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import access_instance_impl
    return await access_instance_impl(instance_id)


@mcp.tool()
async def validate_completion(
    instance_id: str,
    intent: str,
    completion_criteria: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate if UI instance meets specific completion criteria.
    This tool enables Agent to determine when to stop modifications.

    Args:
        instance_id: Instance ID to validate (e.g., "demo", "counter", "form").
        intent: High-level description of what the UI should accomplish.
        completion_criteria: List of criteria to check against. Each criterion should have:
            - type: "field_exists", "field_value", "block_count", "action_exists", "custom"
            - path: Field path (for field-related criteria)
            - value: Expected value (for field_value criteria)
            - count: Expected count (for block_count criteria)
            - condition: Custom validation expression (for custom criteria)
            - description: Human-readable description of the criterion

    Returns:
        Dict containing:
        - evaluation: Object containing evaluation metrics (NOT a completion decision)
            * passed_criteria: Number of criteria that passed
            * total_criteria: Total number of criteria evaluated
            * completion_ratio: Ratio of passed to total criteria (0.0 to 1.0)
            * detailed_results: Array of individual criterion results
        - summary: High-level assessment of current state
        - recommendations: Suggested next steps (Agent decides whether to follow)

    Examples:
        Check if counter UI has required elements:
            {
                "instance_id": "counter",
                "intent": "Create a counter with display and increment button",
                "completion_criteria": [
                    {
                        "type": "field_exists",
                        "path": "state.params.count",
                        "description": "Counter value field exists"
                    },
                    {
                        "type": "action_exists",
                        "path": "increment",
                        "description": "Increment button exists"
                    }
                ]
            }
        
        Check if form has specific field values:
            {
                "instance_id": "form",
                "intent": "Form should have email field with validation",
                "completion_criteria": [
                    {
                        "type": "field_exists",
                        "path": "state.params.email",
                        "description": "Email field exists"
                    },
                    {
                        "type": "block_count",
                        "count": 1,
                        "description": "Exactly one form block exists"
                    }
                ]
            }
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import validate_completion_impl
    return await validate_completion_impl(instance_id, intent, completion_criteria)


# 启动MCP服务器的代码
if __name__ == "__main__":
    print("🚀 Starting MCP Server for UI Patch Tool...")
    print("📝 Available tools:")
    print("  - patch_ui_state: Apply structured patches to modify UI (with field operation shortcuts)")
    print("  - get_schema: Get current UI Schema")
    print("  - list_instances: List all available instances")
    print("  - access_instance: Access a specific UI instance and mark it as active")
    print("  - validate_completion: Check if UI meets completion criteria (semantic control)")
    print()
    mcp.run(
        transport="streamable-http",
        port=8766,
        host="0.0.0.0",
        path="/mcp",
    )