"""MCP工具定义文件

此文件定义了所有可用的MCP工具及其参数，但不包含具体实现。
实现逻辑应在tool_implements.py文件中。

重要：工具描述会被注入到Agent上下文，所有必要信息都在工具描述中。
"""

from typing import Any
from fastmcp import FastMCP

# 创建FastMCP服务器实例
mcp = FastMCP("ui-patch-server")


# 工具注册区域 - 所有工具在此处注册但不在本文件中实现

@mcp.tool()
async def add_field(
    instance_id: str,
    field: dict[str, Any],
    block_index: int | None = 0,
    state_path: str | None = None,
    initial_value: Any | None = None
) -> dict[str, Any]:
    """
    Add a new field to a form block. Auto-initializes state and updates UI.

    WHEN TO USE: Add input/display fields to forms. Supports 17 field types.

    FIELD TYPES (17 total):
        Input (5): text, number, textarea, checkbox, json
        Selection (3): select, radio, multiselect (needs options array)
        Display (9): html, image, tag, progress, badge, table, modal, component

    REQUIRED FIELD PROPS: label, key, type
    COMMON OPTIONAL: value, description, editable, options (for select/radio/multiselect)

    FIELD TYPE DETAILS:
        text: Single-line text input. Special: Object values auto-convert to JSON, supports template ${state.xxx}.
              Props: label, key, type, value, description, editable. Example: {"label":"Name","key":"name","type":"text"}
        number: Numeric input. Props: label, key, type, value, description. Example: {"label":"Age","key":"age","type":"number","value":0}
        textarea: Multi-line text. Special: Object values auto-convert to JSON, supports template ${state.xxx}.
                 Props: label, key, type, value, description, rows (default:4). Example: {"label":"Bio","key":"bio","type":"textarea","rows":6}
        checkbox: Boolean toggle. Props: label, key, type, value (boolean), description. Example: {"label":"Agreed","key":"agreed","type":"checkbox","value":false}
        json: JSON editor. Special: Object values auto-convert to JSON string, supports template ${state.xxx}.
              Props: label, key, type, value, description, editable. Example: {"label":"Config","key":"config","type":"json"}
        select: Dropdown. Props: label, key, type, value, options (REQUIRED: array of {label,value}).
                Example: {"label":"Country","key":"country","type":"select","options":[{"label":"CN","value":"cn"}]}
        radio: Radio buttons. Props: label, key, type, value, options (REQUIRED: array of {label,value}).
              Example: {"label":"Gender","key":"gender","type":"radio","options":[{"label":"Male","value":"male"}]}
        multiselect: Multi-select. Props: label, key, type, value (array), options (REQUIRED: array of {label,value}).
                    Example: {"label":"Skills","key":"skills","type":"multiselect","value":["coding"],"options":[{"label":"Coding","value":"coding"}]}
        html: Read-only HTML. Props: label, key, type, value (HTML string), description.
              Example: {"label":"Content","key":"content","type":"html","value":"<h3>Title</h3>"}
        image: Image display. Props: label, key, type, value (URL or {url,title,alt}), showFullscreen (default:true),
                showDownload (default:true), imageHeight (default:"auto"), imageFit (default:"contain":contain/cover/fill), lazy, fallback, subtitle.
                Example: {"label":"Avatar","key":"avatar","type":"image","imageFit":"cover","imageHeight":"200px"}
        tag: Tag display with auto-type-detection and custom text mapping. Props: label, key, type, value (array of tags),
              renderText, evaluate. Tag types: success/active/completed->green, warning/pending->yellow,
              error/failed/danger->red, info/processing->blue, other->gray.
              renderText format: "value1:text1|value2:text2" (e.g., "true:已完成|false:未完成").
              evaluate format: Boolean expression (e.g., "status === 'completed'").
              Example: {"label":"Status","key":"status","type":"tag","renderText":"true:已完成|false:未完成"}
        progress: Progress bar. Props: label, key, type, value (object: {current,total,showLabel}).
                  Example: {"label":"Progress","key":"progress","type":"progress","value":{"current":3,"total":5,"showLabel":true}}
        badge: Badge notification. Props: label, key, type, value (object: {count,label,dot,color,showZero,max}).
                Example: {"label":"Notifs","key":"notifs","type":"badge","value":{"count":5,"label":"Msg","color":"#f5222d"}}
        table: Data table with sorting and multiple render types. Required: columns (array of column config).
                Columns props: key, label, width, align (left/center/right), sortable (default:false), editable (default:false),
                renderType (default:text/tag/badge/progress/image/mixed).
                Table props: value (data array), rowKey (default:"id"), bordered (default:true), striped (default:true),
                hover (default:true), showHeader (default:true), showPagination (default:false), pageSize (default:10),
                maxHeight, emptyText (default:"暂无数据"), compact (default:false).
                Example: {"label":"Users","key":"users","type":"table","columns":[{"key":"name","label":"Name"}],"value":[{"id":1,"name":"John"}]}
        modal: Modal dialog. Props: label, key, type, value (object: {visible,title,content,width,okText,cancelText}).
                Example: {"label":"Confirm","key":"confirm","type":"modal","value":{"visible":true,"title":"Confirm?","content":"<p>Are you sure?</p>"}}
        component: Embedded cross-instance rendering. Props: label, key, type, targetInstance (REQUIRED), targetBlock.
                   Example: {"label":"Chart","key":"chart","type":"component","targetInstance":"chart_instance"}

    TEMPLATE RENDERING:
        Syntax: ${state.params.xxx} for params, ${state.runtime.xxx} for runtime
        Auto-timestamp: When ${state.runtime.timestamp} is referenced, auto-updates to current time
        Object handling: For text/textarea/json fields, object values auto-convert to JSON string

    ARGS:
        instance_id: Target instance ID
        field: Field config object
        block_index: Block index to add to (default: 0)
        state_path: State path to init (e.g., "state.params.username")
        initial_value: Initial state value

    RETURNS: {status, instance_id, patches_applied, message/error}

    EXAMPLES:
        Text: {"instance_id":"form","field":{"label":"Name","key":"name","type":"text"},
               "state_path":"state.params.name","initial_value":""}
        Select: {"instance_id":"form","field":{"label":"Country","key":"country","type":"select",
                "options":[{"label":"CN","value":"cn"}]},"state_path":"state.params.country"}
        Table: {"instance_id":"form","field":{"label":"Users","key":"users","type":"table",
                "columns":[{"key":"name","label":"Name"}]},"state_path":"state.params.users",
                "initial_value":[{"id":1,"name":"John"}]}

    NOTE: UI auto-refreshes. No need to call access_instance.
    """
    from backend.mcp.tool_implements import add_field_impl
    return await add_field_impl(instance_id, field, block_index, state_path, initial_value)


@mcp.tool()
async def update_field(
    instance_id: str,
    field_key: str,
    updates: dict[str, Any],
    block_index: int | None = 0,
    update_all: bool | None = False
) -> dict[str, Any]:
    """
    Update an existing field's properties. Modifies field config only.

    WHEN TO USE: Change field label, type, or other properties. NOT for changing field values.

    ARGS:
        instance_id: Target instance ID
        field_key: Key of field to update
        updates: Field properties to update (e.g., {"label": "New Label", "type": "textarea"})
        block_index: Block index containing field (default: 0)
        update_all: Update all fields with matching key across all blocks (default: False)

    RETURNS: {status, instance_id, patches_applied, message/error}

    EXAMPLES:
        Change label: {"instance_id":"form","field_key":"name","updates":{"label":"Full Name"}}
        Change type: {"instance_id":"form","field_key":"desc","updates":{"type":"textarea"}}
        Multi-prop: {"instance_id":"form","field_key":"avatar","updates":{"imageFit":"cover","imageHeight":"150px"}}

    NOTE: To change field values, use patch_ui_state with "state.params.xxx" path.
    """
    from backend.mcp.tool_implements import update_field_impl
    return await update_field_impl(instance_id, field_key, updates, block_index, update_all)


@mcp.tool()
async def remove_field(
    instance_id: str,
    field_key: str,
    block_index: int | None = 0,
    remove_all: bool | None = False
) -> dict[str, Any]:
    """
    Remove a field from a form block.

    WHEN TO USE: Delete unused/incorrect fields from UI.

    ARGS:
        instance_id: Target instance ID
        field_key: Key of field to remove
        block_index: Block index containing field (default: 0)
        remove_all: Remove all fields with matching key across all blocks (default: False)

    RETURNS: {status, instance_id, patches_applied, message/error}

    EXAMPLES:
        Single field: {"instance_id":"form","field_key":"email"}
        Specific block: {"instance_id":"form","field_key":"phone","block_index":1}
        All matching: {"instance_id":"form","field_key":"temp","remove_all":true}
    """
    from backend.mcp.tool_implements import remove_field_impl
    return await remove_field_impl(instance_id, field_key, block_index, remove_all)


@mcp.tool()
async def add_block(
    instance_id: str,
    block: dict[str, Any],
    position: str | None = "end"
) -> dict[str, Any]:
    """
    Add a new block to UI instance. Blocks organize fields and actions.

    WHEN TO USE: Create new content sections (forms, displays, custom layouts).

    BLOCK TYPES:
        form: Block with input fields
        display: Block for read-only content
        other: Custom block types

    REQUIRED BLOCK PROPS: id, type, bind, props (props.fields for form/display)

    ARGS:
        instance_id: Target instance ID
        block: Block config object
        position: Insert location - "start", "end", or integer index (default: "end")

    RETURNS: {status, instance_id, patches_applied, message/error}

    EXAMPLES:
        Form block: {"instance_id":"demo","block":{"id":"contact","type":"form",
                    "bind":"state.params","props":{"fields":[{"label":"Name","key":"name","type":"text"}]}}}
        Display block: {"instance_id":"demo","position":"start","block":{"id":"header","type":"display",
                     "bind":"state.params","props":{"fields":[{"label":"Title","key":"title","type":"html"}]}}}
        With actions: {"instance_id":"demo","block":{"id":"actions_block","type":"form",
                     "bind":"state.params","props":{"fields":[{"label":"Status","key":"status","type":"text"}]},
                     "actions":[{"id":"reset","label":"Reset","style":"secondary","handler_type":"set",
                     "patches":{"state.params.status":""}}]}}

    NOTE: UI auto-refreshes. No need to call access_instance.
    """
    from backend.mcp.tool_implements import add_block_impl
    return await add_block_impl(instance_id, block, position)


@mcp.tool()
async def remove_block(
    instance_id: str,
    block_id: str,
    remove_all: bool | None = False
) -> dict[str, Any]:
    """
    Remove a block from UI instance.

    WHEN TO USE: Delete entire content sections from UI.

    ARGS:
        instance_id: Target instance ID
        block_id: ID of block to remove
        remove_all: Remove all blocks with matching ID (default: False)

    RETURNS: {status, instance_id, patches_applied, message/error}

    EXAMPLES:
        Single block: {"instance_id":"form","block_id":"old_block"}
        All matching: {"instance_id":"form","block_id":"temp","remove_all":true}
    """
    from backend.mcp.tool_implements import remove_block_impl
    return await remove_block_impl(instance_id, block_id, remove_all)


@mcp.tool()
async def add_action(
    instance_id: str,
    action: dict[str, Any],
    block_index: int | None = None
) -> dict[str, Any]:
    """
    Add an action button to UI. Actions trigger handlers when clicked.

    WHEN TO USE: Add interactive buttons that modify state, navigate, or call APIs.

    REQUIRED ACTION PROPS: id, label, style
    STYLE OPTIONS: primary (blue), secondary (gray), danger (red)

    OPTIONAL PROPS:
        action_type: "api" (default) or "navigate"
        target_instance: Target instance ID (when action_type="navigate")
        handler_type: Handler type (see details below)
        patches: Patch mappings (for set/increment/decrement/toggle/template)

    HANDLER TYPES (9 total):
        set: Direct assignment. Patches: {"path": "value"}. Example: {"handler_type":"set","patches":{"state.params.count":42}}
              Supports operation object for complex actions:
              - append_to_list: {"operation":"append_to_list","params":{"item":{...}}}
              - prepend_to_list: {"operation":"prepend_to_list","params":{"item":{...}}}
              - remove_from_list: {"operation":"remove_from_list","params":{"key":"field","value":"val"}}
              - update_list_item: {"operation":"update_list_item","params":{"key":"field","value":"val","updates":{...}}}
              - clear_all_params: {"operation":"clear_all_params","params":{}}
              - append_block: {"operation":"append_block","params":{"block":{...}}}
              - prepend_block: {"operation":"prepend_block","params":{"block":{...}}}
              - remove_block: {"operation":"remove_block","params":{"block_id":"id"}}
              - update_block: {"operation":"update_block","params":{"block_id":"id","updates":{...}}}
              - merge: {"operation":"merge","params":{"data":{...}}}
        increment: Add to number. Patches: {"path": delta}. Example: {"handler_type":"increment","patches":{"state.params.count":1}}
        decrement: Subtract from number. Patches: {"path": delta}. Example: {"handler_type":"decrement","patches":{"state.params.count":1}}
        toggle: Boolean toggle. Patches: {"path": true}. Example: {"handler_type":"toggle","patches":{"state.params.enabled":true}}
        template: Render template string. Patches: {"path": "template"}. Example: {"handler_type":"template",
                 "patches":{"state.runtime.message":"Done at ${state.runtime.timestamp}"}}
        external: Call external API. Config: url, method, headers, body_template, response_mappings, error_mapping.
                 Example: {"handler_type":"external","patches":{"url":"https://api.example.com/data","method":"GET",
                 "response_mappings":{"state.params.user":"data"}}}
        template:all: Render all patches with template variables
        template:state: Render only state patches (state.params.* and state.runtime.*)

    TEMPLATE RENDERING:
        Syntax: ${state.params.xxx} for params, ${state.runtime.xxx} for runtime
        Auto-timestamp: When ${state.runtime.timestamp} is referenced, auto-updates to current time

    ARGS:
        instance_id: Target instance ID
        action: Action config object
        block_index: Optional block index (adds to global actions if None)

    RETURNS: {status, instance_id, patches_applied, message/error}

    EXAMPLES:
        Clear form: {"instance_id":"form","action":{"id":"clear","label":"Clear","style":"danger",
                    "handler_type":"set","patches":{"state.params.name":"","state.runtime.status":"idle"}}}
        Increment: {"instance_id":"counter","action":{"id":"inc","label":"+","style":"primary",
                   "handler_type":"increment","patches":{"state.params.count":1}}}
        Navigate: {"instance_id":"form","action":{"id":"goto","label":"Go to list","style":"secondary",
                   "action_type":"navigate","target_instance":"list_page"}}
        Template: {"instance_id":"form","action":{"id":"submit","label":"Submit","style":"primary",
                   "handler_type":"template","patches":{"state.runtime.message":"Done at ${state.runtime.timestamp}"}}}
        External API: {"instance_id":"form","action":{"id":"fetch","label":"Fetch","style":"primary",
                      "handler_type":"external","patches":{"url":"https://api.example.com/data",
                      "method":"GET","response_mappings":{"state.params.data":""}}}

    NOTE: UI auto-refreshes. No need to call access_instance.
    """
    from backend.mcp.tool_implements import add_action_impl
    return await add_action_impl(instance_id, action, block_index)


@mcp.tool()
async def remove_action(
    instance_id: str,
    action_id: str,
    block_index: int | None = None,
    remove_all: bool | None = False
) -> dict[str, Any]:
    """
    Remove an action button from UI.

    WHEN TO USE: Delete unused action buttons.

    ARGS:
        instance_id: Target instance ID
        action_id: ID of action to remove
        block_index: Optional block index (removes from global actions if None)
        remove_all: Remove all actions with matching ID (default: False)

    RETURNS: {status, instance_id, patches_applied, message/error}

    EXAMPLES:
        Global action: {"instance_id":"form","action_id":"old_action"}
        Block action: {"instance_id":"form","action_id":"reset","block_index":0}
        All matching: {"instance_id":"form","action_id":"temp","remove_all":true}
    """
    from backend.mcp.tool_implements import remove_action_impl
    return await remove_action_impl(instance_id, action_id, block_index, remove_all)


@mcp.tool()
async def patch_ui_state(
    instance_id: str,
    patches: list[dict[str, Any]] = [],
    new_instance_id: str | None = None,
    target_instance_id: str | None = None
) -> dict[str, Any]:
    """
    Apply raw patch operations to UI Schema. Most flexible tool for all modifications.

    WHEN TO USE: Batch operations, complex modifications, or when specialized tools don't fit.
    For simple field/block/action ops, prefer: add_field, update_field, add_block, etc.

    INSTANCE IDs:
        Regular: "demo", "form", "counter" (modify existing)
        "__CREATE__": Create new instance (requires new_instance_id)
        "__DELETE__": Delete instance (requires target_instance_id)

    OPERATIONS (op field):
        set: Set/update value at path. Creates if missing.
        add: Append item to array (blocks, actions, blocks.X.props.fields).
        remove: Remove item from array by ID/key (blocks, actions, blocks.X.props.fields).

    PATH EXAMPLES:
        state.params.count - Set/modify state value
        state.runtime.status - Set runtime status
        blocks.0 - Access first block
        blocks.0.props.fields.0 - Access first field
        blocks.0.props.fields.0.label - Update field property

    FIELD TYPES (17): text, number, textarea, checkbox, json, select, radio, multiselect, html, image, tag, progress, badge, table, modal, component

    HANDLER TYPES (9): set, increment, decrement, toggle, template, external, template:all, template:state
        See add_action tool for complete handler details and examples.

    AUTO-TIMESTAMP: When patches reference state.runtime.timestamp in templates, auto-updates to current time.

    ARGS:
        instance_id: Target instance ID
        patches: Array of patch operations
        new_instance_id: Required when instance_id=="__CREATE__"
        target_instance_id: Required when instance_id=="__DELETE__"

    RETURNS: {status, instance_id, patches_applied, skipped_patches, message/error}

    EXAMPLES:
        Update state: {"instance_id":"counter","patches":[{"op":"set","path":"state.params.count","value":42}]}
        Add field: {"instance_id":"form","patches":[
                    {"op":"set","path":"state.params.name","value":""},
                    {"op":"add","path":"blocks.0.props.fields","value":{"label":"Name","key":"name","type":"text"}}]}
        Update field: {"instance_id":"form","patches":[{"op":"set","path":"blocks.0.props.fields.0.label","value":"New"}]}
        Remove field: {"instance_id":"form","patches":[{"op":"remove","path":"blocks.0.props.fields",
                      "value":{"key":"email"}}]}
        Create instance: {"instance_id":"__CREATE__","new_instance_id":"my","patches":[
                        {"op":"set","path":"meta","value":{"pageKey":"my","step":{"current":1,"total":1}}},
                        {"op":"set","path":"state","value":{"params":{},"runtime":{}}},
                        {"op":"set","path":"blocks","value":[]},{"op":"set","path":"actions","value":[]}]}
        Delete instance: {"instance_id":"__DELETE__","target_instance_id":"old"}
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import patch_ui_state_impl
    return await patch_ui_state_impl(
        instance_id, patches, new_instance_id, target_instance_id
    )


@mcp.tool()
async def get_schema(instance_id: str | None = None) -> dict[str, Any]:
    """
    Get current UI Schema for an instance. Returns complete instance structure.

    WHEN TO USE: Inspect current state, check structure, or prepare modifications.

    ARGS:
        instance_id: Instance ID (e.g., "demo", "form"). If None, returns default "demo" instance.

    RETURNS: {status, error (if any), instance_id, schema}
        Schema structure: {meta, state, layout, blocks, actions}
        - meta: {pageKey, step, ...}
        - state: {params: {...}, runtime: {...}}
        - blocks: [{id, type, bind, props, actions}, ...]
        - actions: [{id, label, style, handler_type, patches}, ...]

    EXAMPLE: {"instance_id":"form"} or get_schema() for default instance.

    NOTE: Use before modifications to understand current structure.
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import get_schema_impl
    return await get_schema_impl(instance_id)


@mcp.tool()
async def list_instances() -> dict[str, Any]:
    """
    List all available UI Schema instances.

    WHEN TO USE: Discover available instances, browse resources, or check instance status.

    RETURNS: {status, error (if any), instances, total}
        instances array: [{instance_id, page_key, status, blocks_count, actions_count}, ...]
        total: Number of instances

    EXAMPLE: No args needed. Call directly.

    NOTE: Use to discover what instances exist before using get_schema or access_instance.
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import list_instances_impl
    return await list_instances_impl()


@mcp.tool()
async def access_instance(instance_id: str) -> dict[str, Any]:
    """
    Access and activate a specific UI instance. Brings instance to user view.

    WHEN TO USE: Switch between instances, mark instance as active for user interaction.

    ARGS:
        instance_id: Instance ID to access (e.g., "demo", "form", "counter")

    RETURNS: {status, error (if any), instance_id, schema}
        Schema structure: Same as get_schema (meta, state, blocks, actions)

    EXAMPLE: {"instance_id":"form"} to switch to form instance.

    NOTE: Automatically triggers WebSocket update to user. UI refreshes immediately.
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import access_instance_impl
    return await access_instance_impl(instance_id)


@mcp.tool()
async def validate_completion(
    instance_id: str,
    intent: str,
    completion_criteria: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Validate UI instance against completion criteria. Returns objective evaluation data.

    WHEN TO USE: Check if UI meets requirements, evaluate progress, or verify modifications.

    IMPORTANT: This is a DATA-DRIVEN tool. Returns evaluation metrics, NOT boolean "is_complete".
                Agent should autonomously decide based on completion_ratio (>=1.0 = done).

    CRITERION TYPES:
        field_exists: Check if field path exists in state
        field_value: Check if field has specific value
        block_count: Check number of blocks
        action_exists: Check if action exists
        custom: Custom validation with condition expression

    CRITERION PROPERTIES:
        type: One of criterion types above
        path: Field path (for field-related criteria)
        value: Expected value (for field_value)
        count: Expected count (for block_count)
        condition: Custom expression (for custom)
        description: Human-readable description

    ARGS:
        instance_id: Instance ID to validate
        intent: High-level description of what UI should accomplish
        completion_criteria: Array of criterion objects

    RETURNS: {status, error (if any), evaluation}
        evaluation object:
        - passed_criteria: Number of criteria met
        - total_criteria: Total number of criteria
        - completion_ratio: passed/total (Agent should use this to decide)
        - detailed_results: [{criterion, passed, actual, expected}, ...]
        - summary: Text summary
        - recommendations: Next step suggestions

    EXAMPLES:
        Check counter exists:
            {"instance_id":"counter","intent":"Create counter with display and button",
             "completion_criteria":[
                {"type":"field_exists","path":"state.params.count","description":"Count field exists"},
                {"type":"action_exists","path":"increment","description":"Increment button exists"}]}

        Check form values:
            {"instance_id":"form","intent":"Form should have email field",
             "completion_criteria":[
                {"type":"field_exists","path":"state.params.email","description":"Email exists"},
                {"type":"field_value","path":"state.params.email","value":"","description":"Email is empty"}]}

        Check structure:
            {"instance_id":"form","intent":"Should have one form block",
             "completion_criteria":[
                {"type":"block_count","count":1,"description":"Exactly one block"}]}

    DECISION RULE: Agent should consider completion_ratio >= 1.0 as fully complete.
                   Use detailed_results to identify what's missing or incorrect.

    NOTE: Use get_schema before validation to understand current state.
    """
    # 实现在tool_implements.py中
    from backend.mcp.tool_implements import validate_completion_impl
    return await validate_completion_impl(instance_id, intent, completion_criteria)


# 启动MCP服务器的代码
if __name__ == "__main__":
    print("🚀 Starting MCP Server for UI Patch Tool...")
    mcp.run(
        transport="streamable-http",
        port=8766,
        host="0.0.0.0",
        path="/mcp",
    )
