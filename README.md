# Agent Programmable UI Runtime

An innovative system that enables AI agents to dynamically build and modify user interfaces through a schema-driven architecture using MCP (Model Context Protocol) tools.

## Overview

This project implements a runtime where AI agents can programmatically control UI elements through structured patches, providing a clean separation between UI definition, state management, and user interaction.

### Architecture

```
┌───────────────────────┐
│   External AI (LLM)   │
│  - Reasoning           │
│  - MCP Tool Calls      │
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

The system comes with three pre-configured instances:

1. **demo** - A simple message display with a button
2. **counter** - A counter application with increment/decrement buttons
3. **form** - A form with text fields and validation

Access them at:
- `http://localhost:5173?instanceId=demo`
- `http://localhost:5173?instanceId=counter`
- `http://localhost:5173?instanceId=form`

## MCP Tools

### 1. patch_ui_state

Apply structured patches to modify UI Schema state and structure. This is the ONLY way to modify UI - no direct mutations allowed.

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

```python
result = await get_schema(instance_id="demo")
# Returns: {"status": "success", "instance_id": "demo", "schema": {...}}
```

### 3. list_instances

List all available UI Schema instances.

```python
result = await list_instances()
# Returns: {"status": "success", "instances": [...], "total": 3}
```

### 4. access_instance

Access a specific UI instance and mark it as active.

```python
result = await access_instance(instance_id="form")
# Returns: {"status": "success", "instance_id": "form", "schema": {...}}
```

### 5. validate_completion

Validate if UI instance meets specific completion criteria.

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

## Supported Operations

| Op | Behavior | Allowed Paths | Required Fields |
|----|----------|---------------|-----------------|
| `set` | Set value at path (creates if missing) | Any path | `path`, `value` |
| `add` | Add item to end of array | `blocks+`, `actions+` | `path`, `value` |
| `replace` | Replace item/array at path | `blocks`, `actions` | `path`, `value` |
| `remove` | Remove specific item | `blocks-{id}`, `actions-{id}` | `path` |
| `clear` | Clear/reset to default | `state.params`, `state.runtime` | `path` |
| `create` | Create new instance | Special | - |
| `delete` | Delete instance | Special | - |

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

## Project Structure

```
example_web_app/
├── backend/
│   ├── fastapi/          # FastAPI application
│   │   ├── main.py       # Main application
│   │   ├── models.py     # Data models
│   │   └── routes/       # API routes
│   ├── mcp/              # MCP tools
│   │   ├── tools.py      # Tool entry point
│   │   ├── tool_definitions.py  # Tool definitions
│   │   ├── tool_implements.py   # Tool implementations
│   │   └── interfaces.py        # Type definitions
│   └── config.py         # Configuration
├── frontend/
│   ├── src/              # TypeScript source
│   └── package.json      # Dependencies
├── README.md             # This file
├── PATCH_SPEC.md         # Patch tool specifications
└── MINIMAL_PROTOTYPE.md  # Architecture documentation
```

## Documentation

- [PATCH_SPEC.md](./PATCH_SPEC.md) - Detailed patch tool specifications
- [MINIMAL_PROTOTYPE.md](./MINIMAL_PROTOTYPE.md) - Architecture overview
- [backend/mcp/README.md](./backend/mcp/README.md) - MCP tools documentation
- [mcp_tool_examples.md](./mcp_tool_examples.md) - MCP tool usage examples

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
