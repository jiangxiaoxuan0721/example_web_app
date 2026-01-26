# Agent Programmable UI Runtime

An innovative system that enables AI agents to dynamically build and modify user interfaces through a schema-driven architecture using MCP (Model Context Protocol) tools.

## Overview

This project implements a runtime where AI agents can programmatically control UI elements through structured patches, providing a clean separation between UI definition, state management, and user interaction.

### Core Philosophy

**Highly Flexible Yet Structured**:

1. **Highly Flexible**:
   - Dynamically create arbitrary UI structures (through combinations of blocks, fields, and actions)
   - Support complex logic processing (through diverse handler types)
   - No hardcoded logic required for specific features - all functionality is configuration-driven
   - Support cross-instance referencing and component reuse
   - Support 17 field types and 9 operation types, enabling infinite possibilities

2. **Structured**:
   - All operations follow predefined data models
   - Clear definitions for field types, handler types, and operation types
   - Unified syntax for path specifications
   - Parameter validation ensures data consistency
   - Clear tool descriptions guide AI agents to use tools correctly

### Architecture

```
┌───────────────────────┐
│   External AI (LLM)   │
│  - Reasoning          │
│  - MCP Tool Calls     │
└───────────┬───────────┘
            │
            │ MCP Tool Calls
            ▼
┌───────────────────────┐
│   MCP Tool Server     │  ← FastAPI + FastMCP
│  - Schema Authority   │
│  - Patch Application  │
│  - Event Dispatch     │
│  - Instance Management│
└───────────┬───────────┘
            │
            │ Schema / Patch / Event
            ▼
┌───────────────────────┐
│   Frontend Runtime    │  ← TypeScript SPA
│  - Schema Interpreter │
│  - Renderer           │
│  - Event Emitter      │
└───────────────────────┘
```

## Key Features

- **Schema-Driven UI**: All UI elements are defined and controlled through a structured schema
- **Patch-Based Modifications**: UI changes are applied through structured patches, ensuring predictability
- **MCP Integration**: AI agents can modify UI using well-defined MCP tools
- **Multi-Instance Support**: Manage multiple UI instances with independent states
- **Event-Driven Architecture**: Clean separation between UI events and state changes
- **17 Field Types**: text, number, textarea, checkbox, select, radio, multiselect, json, html, image, tag, progress, badge, table, modal, component, and more
- **9 Handler Types**: set, increment, decrement, toggle, template, external, template:all, template:state, and operation objects
- **Template Rendering**: Support for `${state.xxx}` syntax for dynamic content updates with automatic timestamp updates
- **Object Value Handling**: Automatically converts objects to JSON strings to avoid `[object Object]` display

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jiangxiaoxuan0721/example_web_app.git
cd example_web_app
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn fastapi.main:app --host 0.0.0.0 --port 8001 --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Access the application at `http://localhost:5173`

### Running MCP Tools

#### Quick Start (Recommended)

**Windows (PowerShell):**
```powershell
cd backend/mcp
.\start_http.ps1
```

**Linux/Mac:**
```bash
cd backend/mcp
python start_http.py
```

#### Alternative Methods

**HTTP Mode (Port 8766):**
```bash
cd backend/mcp
export MCP_TRANSPORT=http
export MCP_PORT=8766
python tools.py
```

**STDIO Mode (Default):**
```bash
cd backend/mcp
python tools.py
```

## Available Instances

The system comes with four pre-configured instances:

1. **demo** - User data table example (showcasing tables, tags, images, actions, etc.)
2. **counter** - Counter application (demonstrating increment/decrement functionality)
3. **rich_content** - Rich content display (HTML, images, fullscreen viewing, downloads, etc.)
4. **block_actions_test** - Block Actions testing (showcasing block-level actions and dynamic operations)

Access them at:
- `http://localhost:5173?instanceId=demo`
- `http://localhost:5173?instanceId=counter`
- `http://localhost:5173?instanceId=rich_content`
- `http://localhost:5173?instanceId=block_actions_test`

## MCP Tools

The system provides **12 MCP tools** for comprehensive UI manipulation:

### 1. patch_ui_state (Generic Patch Tool)

Apply structured patches to modify UI Schema state and structure. This is the ONLY way to modify UI - no direct mutations allowed.

**Use Cases**:
- Complex batch operations
- Direct deep path modifications
- Multiple unrelated operations in one call
- Creating new instances or deleting instances

```python
# Update state
await patch_ui_state({
    "instance_id": "counter",
    "patches": [
        {"op": "set", "path": "state.params.count", "value": 42}
    ]
})

# Update field (shortcut)
await patch_ui_state({
    "instance_id": "form",
    "field_key": "email",
    "updates": {
        "label": "Email Address",
        "type": "email"
    }
})

# Create new instance
await patch_ui_state({
    "instance_id": "__CREATE__",
    "new_instance_id": "my_instance",
    "patches": [
        {"op": "set", "path": "meta", "value": {...}},
        {"op": "set", "path": "state", "value": {...}},
        {"op": "set", "path": "blocks", "value": []},
        {"op": "set", "path": "actions", "value": []}
    ]
})
```

### 2. get_schema

Get current UI Schema for an instance.

**Use Cases**:
- Check current state
- Analyze UI structure
- Verify modifications

```python
result = await get_schema(instance_id="demo")
# Returns: {"status": "success", "instance_id": "demo", "schema": {...}}
```

### 3. list_instances

List all available UI Schema instances.

**Use Cases**:
- Browse available instances
- Discover instance resources

```python
result = await list_instances()
# Returns: {"status": "success", "instances": [...], "total": 4}
```

### 4. validate_completion

Validate if UI instance meets specific completion criteria.

**Use Cases**:
- Evaluate task completion
- Determine next steps
- Quality checks

```python
result = await validate_completion({
    "instance_id": "form",
    "intent": "Create a registration form with email and password fields",
    "completion_criteria": [
        {
            "type": "field_exists",
            "path": "state.params.email",
            "description": "Email field exists"
        },
        {
            "type": "field_exists",
            "path": "state.params.password",
            "description": "Password field exists"
        }
    ]
})
```

### 5. access_instance

Access a specific UI instance and mark it as active.

**Use Cases**:
- Switch context
- Mark active instance

```python
result = await access_instance(instance_id="form")
# Returns: {"status": "success", "instance_id": "form", "schema": {...}}
```

### 6. add_field (Specialized Tool)

Add a new field to a form block with optional initial value.

**Use Cases**:
- Add new input fields to forms
- Automatic state initialization

```python
result = await add_field({
    "instance_id": "form",
    "field": {
        "key": "email",
        "label": "Email Address",
        "type": "email",
        "placeholder": "Enter your email"
    },
    "block_index": 0,
    "state_path": "state.params.email",
    "initial_value": ""
})
```

### 7. update_field (Specialized Tool)

Update an existing field in a form block.

**Use Cases**:
- Modify field labels, types, or other properties
- Batch updates

```python
result = await update_field({
    "instance_id": "form",
    "field_key": "email",
    "updates": {
        "label": "Email Address (Updated)",
        "required": true
    }
})
```

### 8. remove_field (Specialized Tool)

Remove a field from a form block and clean up associated state.

**Use Cases**:
- Remove unneeded fields
- Automatic state cleanup

```python
result = await remove_field({
    "instance_id": "form",
    "field_key": "email"
})
```

### 9. add_block (Specialized Tool)

Add a new block to schema with positioning control.

**Use Cases**:
- Create new content blocks
- Flexible position control

```python
result = await add_block({
    "instance_id": "form",
    "block": {
        "id": "info_block",
        "type": "card",
        "props": {
            "title": "Information",
            "content": "Please fill in form below"
        }
    },
    "position": "end"  # or "start" or an index number
})
```

### 10. remove_block (Specialized Tool)

Remove a block and clean up its associated state.

**Use Cases**:
- Remove entire content blocks
- Automatic dependency cleanup

```python
result = await remove_block({
    "instance_id": "form",
    "block_id": "info_block"
})
```

### 11. add_action (Specialized Tool)

Add a new action (button) to a block or globally with handler configuration.

**Use Cases**:
- Add interactive features to UI
- Support global and block-level actions

```python
result = await add_action({
    "instance_id": "form",
    "action": {
        "id": "submit",
        "label": "Submit Form",
        "style": "primary",
        "action_type": "handler",
        "handler_type": "template",
        "patches": {
            "state.runtime.message": "Form submitted at ${state.runtime.timestamp}"
        }
    },
    "block_index": 0  # omit for global action
})
```

### 12. remove_action (Specialized Tool)

Remove an action from a block or globally.

**Use Cases**:
- Remove unneeded action buttons

```python
result = await remove_action({
    "instance_id": "form",
    "action_id": "submit",
    "block_index": 0  # omit for global action
})
```

## Supported Operations

|| Op | Behavior | Allowed Paths | Required Fields |
||----|----------|---------------|-----------------|
|| `set` | Set value at path (creates if missing) | Any path | `path`, `value` |
|| `add` | Add item to end of array | `blocks+`, `actions+` | `path`, `value` |
|| `remove` | Remove specific item | `blocks-{id}`, `actions-{id}` | `path`, `value` |

**Important Notes**:
- ❌ Do NOT use `blocks/-` or `actions/-` format (invalid)
- ✅ Use `blocks` or `actions` for `add` operations
- ✅ Use `blocks` or `actions` with complete `value` for `remove` operations (tool matches by `id` or content)

## API Endpoints

### GET /ui/schema

Get current Schema for an instance.

- `/ui/schema` → Returns default instance (demo)
- `/ui/schema?instanceId=counter` → Returns counter instance

### POST /ui/patch

Apply patches to modify UI Schema.

### POST /ui/access

Access a specific UI instance and mark it as active.

### GET /ui/instances

List all available UI Schema instances.

## Configuration

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ui-patch-server": {
      "command": "python",
      "args": [
        "/path/to/project/backend/mcp/tools.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/project",
        "MCP_TRANSPORT": "http",
        "MCP_PORT": "8766"
      }
    }
  }
}
```

### Cline (VS Code) Configuration

Add to your `.clinerules`:

```yaml
mcpServers:
  ui-patch-server:
    command: python
    args:
      - ./backend/mcp/tools.py
    env:
      PYTHONPATH: ./
      MCP_TRANSPORT: http
      MCP_PORT: '8766'
```

## Architecture Principles

### Single Write Path

All modifications MUST go through `patch_ui_state`:

```
User Input → Frontend Optimistic Update → Action Click →
patch_ui_state Tool → Backend Application → WebSocket Push → Frontend Update
```

### Advantages

- ✅ **No Race Conditions** - Single-writer model
- ✅ **Predictable Behavior** - Sequential application
- ✅ **Debuggable** - Clear operation history
- ✅ **AI Friendly** - Perfect fit for Agent workflows

### High-Level Abstraction vs Low-Level Control

- **Specialized Tools** (add_field, update_field, remove_field, etc.): Provide high-level abstraction with clear parameters for common scenarios
- **patch_ui_state**: Provides low-level control with full flexibility for complex operations and batch updates

**Best Practices**:
- For common operations (add/update/remove fields, blocks, actions), prioritize specialized tools
- For complex batch operations or direct deep path modifications, use `patch_ui_state`

### Template Rendering

The system supports using template variables in field configurations and HTML content with format `${path}`, such as `${state.runtime.timestamp}`.

**Supported Paths**:
- `${state.params.xxx}` - Field parameter values
- `${state.runtime.xxx}` - Runtime data
- `${params.xxx}` - Parameter shortcut access
- `${runtime.xxx}` - Runtime shortcut access
- `${meta.xxx}` - Metadata information

**Automatic Timestamp Updates**:
When a template references `state.runtime.timestamp`, the system automatically updates it to the current time without manual handling.

For details, see [TEMPLATE_USAGE.md](./TEMPLATE_USAGE.md).

### Operation Objects (Set Handler)

The set handler supports executing complex operations through operation objects:

**Supported Operation Types**:
- `append_to_list`: Add element to end of list
- `prepend_to_list`: Add element to beginning of list
- `remove_from_list`: Remove element from list
- `update_list_item`: Update element in list
- `clear_all_params`: Clear all params
- `append_block`: Add new block
- `prepend_block`: Add block at beginning
- `remove_block`: Remove block
- `update_block`: Update block
- `merge`: Merge objects

**Example**:
```json
{
  "handler_type": "set",
  "patches": {
    "state.params.users": {
      "operation": "append_to_list",
      "params": {
        "item": {"id": 6, "name": "Zhao Liu"}
      }
    }
  }
}
```

For details, see "Action Handler Details" in [MCP_Tool_Reference_Manual.md](./backend/mcp/MCP_Tool_Reference_Manual.md).

## Project Structure

```
example_web_app/
├── backend/
│   ├── fastapi/          # FastAPI application
│   │   ├── main.py       # Main application entry point
│   │   ├── models.py     # Pydantic data models (UISchema, Block, FieldConfig, ActionConfig, etc.)
│   │   ├── routes/       # API routes
│   │   │   ├── event_routes.py      # Event handling (action:click, field:change)
│   │   │   ├── patch_routes.py      # Patch application logic (add/remove/set operations)
│   │   │   ├── schema_routes.py     # Schema retrieval and instance management
│   │   │   └── websocket_routes.py  # WebSocket connection handling
│   │   └── services/     # Business logic
│   │       ├── event_handler.py      # Event processing
│   │       ├── instance_service.py   # Instance and action management
│   │       ├── patch.py             # Patch application to schema
│   │       └── websocket/          # WebSocket subsystem
│   │           ├── handlers/        # Message dispatching
│   │           │   ├── dispatcher.py    # Send messages to clients
│   │           │   └── manager.py       # Connection lifecycle
│   │           └── connection/      # Connection pooling
│   │               ├── pool.py          # Active connections pool
│   │               └── monitor.py      # Connection health monitoring
│   ├── mcp/              # MCP tools
│   │   ├── tools.py                # MCP server entry point
│   │   ├── tool_definitions.py     # MCP tool definitions (12 tools)
│   │   ├── tool_implements.py      # Tool implementations
│   │   ├── interfaces.py          # Type definitions and interfaces
│   │   ├── MCP_Field_TYPES.md     # Field type reference (17 types)
│   │   ├── MCP_Tool_Reference_Manual.md  # Complete tool manual
│   │   ├── MCP_Tools_Refactoring_Guide.md # Refactoring guide
│   │   └── start_http.py          # HTTP server starter
│   ├── core/             # Core management
│   │   ├── defaults.py   # Default schema definitions (4 instances)
│   │   ├── history.py    # Patch history management
│   │   └── manager.py    # Schema instance manager
│   ├── config.py         # Configuration
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/              # TypeScript source
│   │   ├── components/   # React components (20+ components)
│   │   │   ├── BlockRenderer.tsx       # Block container renderer
│   │   │   ├── GenericFieldRenderer.tsx # Universal field renderer (50+ field types)
│   │   │   ├── ImageRenderer.tsx       # Image display with modal
│   │   │   ├── RichContentRenderer.tsx  # Markdown/HTML content
│   │   │   ├── ActionButton.tsx        # Button with action handling
│   │   │   ├── DebugInfo.tsx          # Debug information display
│   │   │   ├── PatchHistory.tsx       # Patch history viewer
│   │   │   ├── InstanceSelector.tsx    # Instance switcher
│   │   │   └── ... (20+ more components)
│   │   ├── hooks/        # React hooks
│   │   │   ├── useSchema.ts           # Schema state management
│   │   │   ├── useWebSocket.ts        # WebSocket connection
│   │   │   └── usePatchHistory.ts    # Patch history replay
│   │   ├── store/        # State management (Zustand)
│   │   │   ├── schemaStore.ts        # Schema state & patch application
│   │   │   └── multiInstanceStore.ts # Multi-instance management
│   │   ├── utils/        # Utility functions
│   │   │   ├── api.ts                # HTTP API calls
│   │   │   ├── eventEmitter.ts       # Event emission to backend
│   │   │   ├── patch.ts              # Patch application helpers
│   │   │   └── template.ts          # Template rendering
│   │   ├── types/        # TypeScript types
│   │   │   └── schema.ts             # Schema type definitions
│   │   ├── App.tsx        # Main application component
│   │   ├── main.tsx       # Application entry point
│   │   └── index.css      # Global styles
│   ├── package.json       # NPM dependencies
│   ├── vite.config.ts    # Vite configuration
│   └── COMPONENTS.md    # Frontend components documentation
├── TEMPLATE_USAGE.md      # Template syntax and usage guide
├── TEMPLATE_WORKFLOW.md   # Complete template rendering workflow
├── REPORTS.md            # Project reports and analysis
├── check.py              # Development helper script
└── README.md             # This file
```

## Documentation

### Core Documentation
- [TEMPLATE_USAGE.md](./TEMPLATE_USAGE.md) - Template syntax and usage guide
- [TEMPLATE_WORKFLOW.md](./TEMPLATE_WORKFLOW.md) - Complete template rendering workflow
- [REPORTS.md](./REPORTS.md) - Project reports and analysis

### MCP Tool Documentation
- [MCP_Tool_Reference_Manual.md](./backend/mcp/MCP_Tool_Reference_Manual.md) - Complete tool manual (Required Reading)
- [MCP_FIELD_TYPES.md](./backend/mcp/MCP_Field_TYPES.md) - Field type reference (17 field types detailed)
- [MCP_Tools_Refactoring_Guide.md](./backend/mcp/MCP_Tools_Refactoring_Guide.md) - Tool refactoring guide
- [interfaces.py](./backend/mcp/interfaces.py) - Type definitions and interfaces

### Frontend Documentation
- [COMPONENTS.md](./frontend/COMPONENTS.md) - Frontend components library documentation

### Backend Documentation
- [backend/fastapi/services/websocket/README.md](./backend/fastapi/services/websocket/README.md) - WebSocket subsystem documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue on GitHub.

---

## Quick Reference

### 17 Field Types

#### Input Types (5 types)
- `text` - Single-line text
- `number` - Number input
- `textarea` - Multi-line text
- `checkbox` - Checkbox
- `json` - JSON editor

#### Selection Types (3 types)
- `select` - Dropdown select
- `radio` - Radio buttons
- `multiselect` - Multi-select checkboxes

#### Display Types (9 types)
- `html` - HTML content
- `image` - Image display
- `tag` - Tag display
- `progress` - Progress bar
- `badge` - Badge notification
- `table` - Data table (supports mixed rendering)
- `modal` - Modal dialog
- `component` - Embedded rendering (cross-instance reference)

For details, see [MCP_FIELD_TYPES.md](./backend/mcp/MCP_FIELD_TYPES.md).

### 9 Handler Types

- `set` - Direct value assignment (supports operation objects for complex operations)
- `increment` - Numeric increment
- `decrement` - Numeric decrement
- `toggle` - Boolean toggle
- `template` - Template rendering
- `external` - External API calls
- `template:all` - Template rendering for all paths
- `template:state` - Template rendering for state paths only

For details, see "Action Handler Details" in [MCP_Tool_Reference_Manual.md](./backend/mcp/MCP_Tool_Reference_Manual.md).

### 12 MCP Tools

**Query Tools**:
- `get_schema` - Get instance schema
- `list_instances` - List all instances
- `validate_completion` - Validate completion criteria
- `access_instance` - Access and activate instance

**Specialized Tools**:
- `add_field` - Add field
- `update_field` - Update field
- `remove_field` - Remove field
- `add_block` - Add block
- `remove_block` - Remove block
- `add_action` - Add action
- `remove_action` - Remove action

**Generic Tool**:
- `patch_ui_state` - Apply structured patches (for complex operations, batch updates, instance creation/deletion)
