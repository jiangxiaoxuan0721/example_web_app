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
        patches: Array of patch operations. Support op types: set, add, replace, remove, clear.
                 Optional when using field shortcuts.
        new_instance_id: Required when instance_id == "__CREATE__".
        target_instance_id: Required when instance_id == "__DELETE__".
        field_key: Key of field to update/remove (for shortcut operations).
        updates: Dictionary of field properties to update (for update shortcut).
        remove_field: If True, removes the specified field (for remove shortcut).
        block_index: Index of form block (default: 0, first block).

    Returns:
        Dict with status ("success"/"error"), optional message/error, instance_id,
        and operation details like patch, auto_refresh status, or navigate_to target.

    Examples:
        Update state value:
            {
                "instance_id": "counter",
                "patches": [
                    {"op": "set", "path": "state.params.count", "value": 42}
                ]
            }

        Add new field to form:
            {
                "instance_id": "form",
                "patches": [
                    {"op": "set", "path": "state.params.telephone", "value": ""},
                    {"op": "add", "path": "blocks.0.props.fields", "value": {
                        "label": "Telephone", "key": "telephone", "type": "text"
                    }}
                ]
            }

        Update field (shortcut):
            {
                "instance_id": "form",
                "field_key": "email",
                "updates": {"label": "Email Address", "type": "email"}
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

        Delete instance:
            {
                "instance_id": "__DELETE__",
                "target_instance_id": "old_instance"
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
        Dict with status ("success"/"error"), error (if any), instance_id,
        and the complete UISchema object (meta, state, layout, blocks, actions).
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import get_schema_impl
    return await get_schema_impl(instance_id)


@mcp.tool()
async def list_instances() -> Dict[str, Any]:
    """
    List all available UI Schema instances.

    Returns:
        Dict with status ("success"/"error"), error (if any), instances array
        (with instance_id, page_key, status, blocks_count, actions_count), and total count.
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
        Dict with status ("success"/"error"), error (if any), instance_id,
        and the UISchema object (same structure as get_schema).
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
    This tool returns objective evaluation data for Agent to make decisions.

    Args:
        instance_id: Instance ID to validate (e.g., "demo", "counter", "form").
        intent: High-level description of what UI should accomplish.
        completion_criteria: List of criteria to check against. Each criterion should have:
            - type: "field_exists", "field_value", "block_count", "action_exists", "custom"
            - path: Field path (for field-related criteria)
            - value: Expected value (for field_value criteria)
            - count: Expected count (for block_count criteria)
            - condition: Custom validation expression (for custom criteria)
            - description: Human-readable description of criterion

    Returns:
        Dict with status ("success"/"error"), error (if any), and evaluation object
        (passed_criteria, total_criteria, completion_ratio, detailed_results),
        plus summary and recommendations for next steps.

    Important Notes:
        - Tool only returns evaluation data, does NOT provide "is_complete" boolean
        - Agent should autonomously decide based on completion_ratio (e.g., >=1.0 = done)
        - This is a data-driven tool, not a judgment-driven tool

    Examples:
        Check if counter UI has required elements:
            {
                "instance_id": "counter",
                "intent": "Create a counter with display and increment button",
                "completion_criteria": [
                    {"type": "field_exists", "path": "state.params.count",
                     "description": "Counter value field exists"},
                    {"type": "action_exists", "path": "increment",
                     "description": "Increment button exists"}
                ]
            }

        Check if form has specific field values:
            {
                "instance_id": "form",
                "intent": "Form should have email field with validation",
                "completion_criteria": [
                    {"type": "field_exists", "path": "state.params.email",
                     "description": "Email field exists"},
                    {"type": "field_value", "path": "state.params.email",
                     "value": "", "description": "Email field is empty"},
                    {"type": "block_count", "count": 1,
                     "description": "Exactly one form block exists"}
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
    print("  - patch_ui_state: Apply structured patches to modify UI (set/add/replace/remove/clear)")
    print("  - get_schema: Get current UI Schema with meta, state, blocks, and actions")
    print("  - list_instances: List all available instances with metadata")
    print("  - access_instance: Access a specific UI instance and mark it as active")
    print("  - validate_completion: Check if UI meets completion criteria (returns evaluation data)")
    print()
    print("📚 Documentation:")
    print("  - Developer Reference: backend/mcp/MCP_Tool_Reference_Manual.md")
    print("  - Quick Examples: backend/mcp/MCP_Quick_Examples.md")
    print()
    mcp.run(
        transport="streamable-http",
        port=8766,
        host="0.0.0.0",
        path="/mcp",
    )