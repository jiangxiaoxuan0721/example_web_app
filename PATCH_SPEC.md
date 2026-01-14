# Patch Tool Specification - Final Design

## Tool Identity

**Name**: `patch_ui_state`

**Description**: Apply structured patches to modify UI Schema state and structure. This is the **ONLY** way to modify UI - no direct mutations allowed.

---

## Tool Input

```typescript
interface PatchInput {
  instanceId: string;          // Target instance (e.g., "demo", "counter", "form")
                               // Use "__CREATE__" to create new instance
                               // Use "__DELETE__" to delete instance
  newInstanceId?: string;      // Required when instanceId === "__CREATE__"
  targetInstanceId?: string;   // Required when instanceId === "__DELETE__"
  patches: PatchOperation[];   // Array of patch operations
}

interface PatchOperation {
  op: PatchOp;                 // Operation type
  path: string;                // Dot-notation path to the target
  value?: any;                 // New value (for 'set', 'add', 'replace')
  items?: any[];               // Items to add (for 'add')
  condition?: string;          // Optional condition
}

type PatchOp = "set" | "add" | "remove" | "clear" | "delete" | "create" | "replace";
```

---

## Supported Path Patterns

### State Paths

| Path Pattern | Description | Example |
|-------------|-------------|----------|
| `state.params.{key}` | Set/update a parameter | `state.params.count` |
| `state.runtime.{key}` | Set runtime state | `state.runtime.status` |

### Schema Structure Paths

#### Blocks Manipulation

| Path Pattern | Description | Example |
|-------------|-------------|----------|
| `blocks` | Replace all blocks | `blocks` |
| `blocks+` | Add blocks to end | `blocks+` |
| `blocks-{index}` | Replace block at index | `blocks-0` |
| `blocks[{id}]` | Replace block by id | `blocks["form_block"]` |
| `blocks-{id}` | Delete block by id | `blocks-"form_block"` |

**Supported Block Types**: `form`

#### Actions Manipulation

| Path Pattern | Description | Example |
|-------------|-------------|----------|
| `actions` | Replace all actions | `actions` |
| `actions+` | Add actions to end | `actions+` |
| `actions-{index}` | Replace action at index | `actions-0` |
| `actions[{id}]` | Replace action by id | `actions["submit"]` |
| `actions-{id}` | Delete action by id | `actions-"submit"` |

**Supported Action Styles**: `primary`, `secondary`, `danger`

#### Layout & Meta

| Path Pattern | Description | Example |
|-------------|-------------|----------|
| `layout` | Replace layout | `layout` |
| `meta.status` | Update meta status | `meta.status` |
| `meta.step` | Update step info | `meta.step` |

**Supported Layout Types**: `single`
**Supported Meta Statuses**: `idle`, `submitted`

---

## Operation Semantics

| Op | Behavior | Allowed Paths | Required Fields |
|-----|-----------|---------------|-----------------|
| `set` | Set value at path (create if missing) | Any path | `path`, `value` |
| `add` | Add item(s) to end of array | `blocks+`, `actions+` | `path`, `value` |
| `replace` | Replace item/array at path | `blocks`, `actions` | `path`, `value` |
| `remove` | Remove specific item | `blocks-{id}`, `actions-{id}` | `path` |
| `clear` | Clear/reset to default | `state.params`, `state.runtime` | `path` |
| `create` | Create new instance | Special (see below) | - |
| `delete` | Delete instance | Special (see below) | - |

---

## Instance Operations

### Create Instance

```json
{
  "instanceId": "__CREATE__",
  "newInstanceId": "my_instance",
  "patches": [
    {
      "op": "set",
      "path": "meta",
      "value": {
        "pageKey": "my_instance",
        "step": {"current": 1, "total": 1},
        "status": "idle"
      }
    },
    {
      "op": "set",
      "path": "state",
      "value": {
        "params": {},
        "runtime": {}
      }
    },
    {
      "op": "set",
      "path": "blocks",
      "value": []
    },
    {
      "op": "set",
      "path": "actions",
      "value": []
    }
  ]
}
```

### Delete Instance

```json
{
  "instanceId": "__DELETE__",
  "targetInstanceId": "my_instance",
  "patches": []
}
```

---

## Examples

### Example 1: Update State

```json
{
  "instanceId": "counter",
  "patches": [
    {
      "op": "set",
      "path": "state.params.count",
      "value": 42
    }
  ]
}
```

### Example 2: Add New Block

```json
{
  "instanceId": "demo",
  "patches": [
    {
      "op": "add",
      "path": "blocks+",
      "value": {
        "id": "new_block",
        "type": "form",
        "bind": "state.params",
        "props": {
          "fields": [
            {"label": "Field", "key": "field1", "type": "text"}
          ]
        }
      }
    }
  ]
}
```

### Example 3: Replace Block by ID

```json
{
  "instanceId": "demo",
  "patches": [
    {
      "op": "set",
      "path": "blocks[\"text_block\"]",
      "value": {
        "id": "text_block",
        "type": "form",
        "bind": "state.params",
        "props": {
          "fields": [
            {"label": "Updated Field", "key": "updatedField", "type": "text"}
          ]
        }
      }
    }
  ]
}
```

### Example 4: Remove Block

```json
{
  "instanceId": "demo",
  "patches": [
    {
      "op": "remove",
      "path": "blocks-\"old_block\""
    }
  ]
}
```

### Example 5: Replace All Blocks

```json
{
  "instanceId": "demo",
  "patches": [
    {
      "op": "replace",
      "path": "blocks",
      "value": [
        {"id": "block1", "type": "form", "bind": "state.params", "props": {"fields": []}},
        {"id": "block2", "type": "form", "bind": "state.params", "props": {"fields": []}}
      ]
    }
  ]
}
```

### Example 6: Multi-Step Update

```json
{
  "instanceId": "wizard",
  "patches": [
    {
      "op": "set",
      "path": "meta.step",
      "value": {"current": 2, "total": 3}
    },
    {
      "op": "set",
      "path": "state.runtime.stepStatus",
      "value": "in_progress"
    }
  ]
}
```

---

## Component Schema Reference

### Block Structure

```typescript
interface Block {
  id: string;                 // Required: Unique block ID
  type: string;                // Required: Block type (currently supports: "form")
  bind: string;                // Required: Binding path (default: "state.params")
  props?: BlockProps;          // Optional: Block properties
}

interface BlockProps {
  fields?: FieldConfig[];      // Required for form type: List of fields
  showProgress?: boolean;      // Optional: Show progress indicator
  showStatus?: boolean;        // Optional: Show status message
  showImages?: boolean;        // Optional: Show images section
  showTable?: boolean;         // Optional: Show table section
  showCountInput?: boolean;    // Optional: Show count input field
  showTaskId?: boolean;        // Optional: Show task ID field
}
```

### Field Types

**Supported Field Types**: `text`, `number`, `textarea`, `select`, `checkbox`, `radio`

```typescript
interface FieldConfig {
  label: string;               // Required: Field label
  key: string;                 // Required: Field key (binds to state.params)
  type: string;                // Required: Field type
  rid?: string;                // Optional: Resource ID
  value?: any;                 // Optional: Default value
  description?: string;        // Optional: Field description
  options?: Array<{ label: string; value: string }>;  // Required for select/radio: Options list
}
```

### Action Structure

```typescript
interface ActionConfig {
  id: string;                  // Required: Unique action ID
  label: string;               // Required: Action button label
  style: string;               // Required: Button style (primary, secondary, danger)
}
```

---

## Design Rules

### ✅ Always Do This

1. **Use structured operations** - Always use `op` + `path` + `value`
2. **Apply in order** - Patches are applied sequentially
3. **Validate paths** - Ensure paths exist or are creatable
4. **Atomic operations** - Each patch is atomic
5. **Use ID-based lookups** - `blocks[{id}]` for safety
6. **Unique IDs** - Ensure block/action IDs are unique

### ❌ Never Do This

1. **No version tracking** - No `baseVersion` or `version` fields in patches
2. **No merging** - Patches are not merged
3. **No rollback** - No undo/revert support
4. **No collaboration** - Single-writer model only
5. **No direct mutation** - All changes via `patch_ui_state`
6. **No duplicate IDs** - Cannot add duplicate block/action IDs
7. **No pageKey changes** - `meta.pageKey` is immutable after creation
8. **No schemaVersion in patches** - Use only in initial schema creation

---

## Error Responses

| Error Code | Description | Solution |
|------------|-------------|----------|
| `INVALID_INSTANCE` | Instance not found | Check instanceId |
| `INVALID_OP` | Unknown operation type | Use valid op: set, add, remove, clear, replace, create, delete |
| `INVALID_PATH` | Path syntax error | Use valid path patterns |
| `PATH_NOT_FOUND` | Cannot resolve path | Ensure path exists or is creatable |
| `SCHEMA_MUTATION` | Immutable field modification | Check allowed fields |
| `MISSING_VALUE` | Required value missing | Provide `value` field |
| `DUPLICATE_ID` | ID already exists | Use unique IDs |
| `INSTANCE_EXISTS` | Instance ID conflict | Use different instanceId |
| `INVALID_STRUCTURE` | Invalid block/action structure | Validate UISchema format |

---

## Design Principles

### Single Write Path

All modifications **MUST** go through `patch_ui_state`:

```
User Input → Frontend Optimistic Update → Action Click →
patch_ui_state Tool → Backend Apply → WebSocket Push → Frontend Update
```

### Benefits

- ✅ **No race conditions** - Single-writer model
- ✅ **Predictable behavior** - Sequential application
- ✅ **Debuggable** - Clear operation history
- ✅ **AI-friendly** - Perfect for agent workflows

### Capabilities

- ✅ Modify state (`state.params`, `state.runtime`)
- ✅ Add/remove/replace blocks
- ✅ Add/remove/replace actions
- ✅ Update layout and metadata
- ✅ Create/delete instances
- ✅ Build complete UIs dynamically

---

## Summary

**Patch Tool** is the **contract** between AI agents, backend, and frontend.

**Core Rules**:

1. Single write entry point (`patch_ui_state`)
2. Structured operations (`op` + `path` + `value`)
3. No version tracking in patches, no merging, no rollback
4. Atomic, ordered application
5. Supports both state and schema modifications
6. Instance lifecycle management (create/delete)

**Result**: A **simple**, **fast**, and **powerful** system for AI-driven UI building.
