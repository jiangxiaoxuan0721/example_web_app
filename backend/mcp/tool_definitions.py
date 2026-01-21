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
    Modify UI Schema state and structure via patch operations. This is ONLY way to modify UI.

    Args:
        instance_id: Target instance ID (e.g., "demo", "counter", "form").
                    Use "__CREATE__" to create new instance.
                    Use "__DELETE__" to delete instance.
        patches: Array of patch operations. Operations: set, add, remove.
        new_instance_id: Required when instance_id == "__CREATE__".
        target_instance_id: Required when instance_id == "__DELETE__".
        field_key: Field key for update/remove shortcuts.
        updates: Field properties to update (for update shortcut).
        remove_field: If True, removes the specified field.
        block_index: Form block index (default: 0).

    Returns:
        Dict with status ("success"/"error"), message/error, instance_id,
        patches_applied array, and optional skipped_patches with reasons.

    Operation Types:
        - set: Update values (state.params.*, state.runtime.*, blocks.X.props.fields.Y, blocks.X.props.fields.Y.attr)
        - add: Add items to arrays (blocks, actions, blocks.X.props.fields)
        - remove: Remove items by ID/key (blocks, actions, blocks.X.props.fields)

    Path Format Examples:
        state.params.count
        state.runtime.status
        blocks.0.props.fields.0
        blocks.0.props.fields.0.label
        blocks.X.props.fields (add/remove fields)

    Field Types:
        text: Single-line text input
        number: Numeric input
        textarea: Multi-line text area
        checkbox: Boolean toggle
        select: Dropdown selection (requires options)
        radio: Radio button group (requires options)
        json: JSON editor with validation
        image: Image display with controls
        html: Read-only HTML content

    Field Properties:
        label (required): Display label
        key (required): Unique field identifier
        type (required): Field type (see Field Types above)
        value (optional): Initial value
        description (optional): Helper text/placeholder
        options (optional): Array of {label, value} for select/radio
        rid (optional): Resource ID
        content_type (optional): Content type (e.g., "json")
        editable (optional): Boolean, default true

    Image-specific Properties (for type="image"):
        showFullscreen: Boolean, default true
        showDownload: Boolean, default true
        imageHeight: String, default "auto"
        imageFit: String, default "contain" (contain/cover/fill)
        lazy: Boolean, enable lazy loading
        fallback: String, fallback content on load failure
        subtitle: Optional subtitle text

    Examples:
        Update state value:
            {"instance_id": "counter", "patches": [{"op": "set", "path": "state.params.count", "value": 42}]}

        Add text field:
            {"instance_id": "form", "patches": [
                {"op": "set", "path": "state.params.username", "value": ""},
                {"op": "add", "path": "blocks.0.props.fields", "value": {"label": "Username", "key": "username", "type": "text"}}
            ]}

        Add number field:
            {"instance_id": "form", "patches": [
                {"op": "set", "path": "state.params.age", "value": 0},
                {"op": "add", "path": "blocks.0.props.fields", "value": {"label": "Age", "key": "age", "type": "number"}}
            ]}

        Add select field:
            {"instance_id": "form", "patches": [
                {"op": "set", "path": "state.params.country", "value": ""},
                {"op": "add", "path": "blocks.0.props.fields", "value": {
                    "label": "Country", "key": "country", "type": "select",
                    "options": [{"label": "China", "value": "cn"}, {"label": "USA", "value": "us"}]
                }}
            ]}

        Add image field:
            {"instance_id": "form", "patches": [
                {"op": "set", "path": "state.params.avatar", "value": "https://example.com/image.jpg"},
                {"op": "add", "path": "blocks.0.props.fields", "value": {
                    "label": "Avatar", "key": "avatar", "type": "image",
                    "imageFit": "cover", "imageHeight": "200px"
                }}
            ]}

        Replace field (all properties):
            {"instance_id": "form", "patches": [{"op": "set", "path": "blocks.0.props.fields.0", "value": {"label": "New", "key": "field", "type": "text"}}]}

        Update field attribute:
            {"instance_id": "form", "patches": [{"op": "set", "path": "blocks.0.props.fields.0.label", "value": "Updated Label"}]}

        Change field type:
            {"instance_id": "form", "patches": [{"op": "set", "path": "blocks.0.props.fields.0.type", "value": "textarea"}]}

        Remove field:
            {"instance_id": "form", "patches": [{"op": "remove", "path": "blocks.0.props.fields", "value": {"key": "email"}}]}

        Add block:
            {"instance_id": "demo", "patches": [{"op": "add", "path": "blocks", "value": {
                "id": "new_block", "type": "form", "bind": "state.params",
                "props": {"fields": [{"label": "Name", "key": "name", "type": "text"}]}
            }}]}

        Remove block:
            {"instance_id": "form", "patches": [{"op": "remove", "path": "blocks", "value": {"id": "old_block"}}]}

        Add action:
            {"instance_id": "form", "patches": [{"op": "add", "path": "actions", "value": {
                "id": "submit", "label": "Submit", "style": "primary",
                "handler_type": "set", "patches": {"state.runtime.status": "submitted"}
            }}]}

        Action Properties:
            id (required): Unique action identifier
            label (required): Button display label
            style (required): Button style - primary, secondary, danger
            action_type (optional): "api" (default) or "navigate"
            target_instance (optional): Target instance ID (when action_type=navigate)
            handler_type (optional): Handler type - set, increment, decrement, toggle, template, external
            patches (optional): Patch mappings for set/increment/decrement/toggle/template

        Handler Types:
            set: Direct value assignment - {"path": "value"}
            increment: Add to numeric value - {"path": delta}
            decrement: Subtract from numeric value - {"path": delta}
            toggle: Boolean toggle - {"path": true}
            template: Render template string - {"path": "template"}
            external: Call external API with config

        Add action with set handler:
            {"instance_id": "form", "patches": [{"op": "add", "path": "actions", "value": {
                "id": "clear", "label": "Clear", "style": "danger",
                "handler_type": "set", "patches": {"state.params.name": "", "state.runtime.status": "idle"}
            }}]}

        Add action with increment handler:
            {"instance_id": "counter", "patches": [{"op": "add", "path": "actions", "value": {
                "id": "increment", "label": "+", "style": "primary",
                "handler_type": "increment", "patches": {"state.params.count": 1}
            }}]}

        Add action with decrement handler:
            {"instance_id": "counter", "patches": [{"op": "add", "path": "actions", "value": {
                "id": "decrement", "label": "-", "style": "secondary",
                "handler_type": "decrement", "patches": {"state.params.count": 1}
            }}]}

        Add action with toggle handler:
            {"instance_id": "toggle", "patches": [{"op": "add", "path": "actions", "value": {
                "id": "toggle", "label": "Toggle", "style": "primary",
                "handler_type": "toggle", "patches": {"state.params.enabled": true}
            }}]}

        Add action with navigate:
            {"instance_id": "form", "patches": [{"op": "add", "path": "actions", "value": {
                "id": "goto_list", "label": "Go to List", "style": "secondary",
                "action_type": "navigate", "target_instance": "list_page"
            }}]}

        Remove action:
            {"instance_id": "form", "patches": [{"op": "remove", "path": "actions", "value": {"id": "old_action"}}]}

        Create instance:
            {"instance_id": "__CREATE__", "new_instance_id": "my_instance", "patches": [
                {"op": "set", "path": "meta", "value": {"pageKey": "my", "step": {"current": 1, "total": 1}}},
                {"op": "set", "path": "state", "value": {"params": {}, "runtime": {}}},
                {"op": "set", "path": "blocks", "value": []},
                {"op": "set", "path": "actions", "value": []}
            ]}

        Delete instance:
            {"instance_id": "__DELETE__", "target_instance_id": "old_instance"}
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
        and complete UISchema object (meta, state, layout, blocks, actions).
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
    Access a specific UI instance and mark it as active.(bring it to user view)

    Args:
        instance_id: Instance ID to access (e.g., "demo", "counter", "form").

    Returns:
        Dict with status ("success"/"error"), error (if any), instance_id,
        and UISchema object (same structure as get_schema).
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
