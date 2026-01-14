# MCP Tools - Agent Programmable UI Runtime

## 概述

MCP (Model Context Protocol) 工具集，为 AI Agent 提供 UI Schema 修改能力。

## 工具列表

### 1. `patch_ui_state`

应用结构化补丁来修改 UI Schema 状态和结构。这是修改 UI 的唯一方式，不允许直接修改。

**参数**:
- `instance_id` (str): 目标实例 ID（如 "demo", "counter", "form"）
  - 使用 `"__CREATE__"` 创建新实例
  - 使用 `"__DELETE__"` 删除实例
- `patches` (List[Dict[str, Any]]): 补丁操作数组
- `new_instance_id` (Optional[str]): 创建实例时必需
- `target_instance_id` (Optional[str]): 删除实例时必需

**示例**:

```python
# 更新状态
{
    "instance_id": "counter",
    "patches": [
        {"op": "set", "path": "state.params.count", "value": 42}
    ]
}

# 添加新 Block
{
    "instance_id": "demo",
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

# 创建实例
{
    "instance_id": "__CREATE__",
    "new_instance_id": "my_instance",
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
            "value": {"params": {}, "runtime": {}}
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

# 删除实例
{
    "instance_id": "__DELETE__",
    "target_instance_id": "old_instance",
    "patches": []
}
```

### 2. `get_schema`

获取指定实例的当前 UI Schema。

**参数**:
- `instance_id` (Optional[str]): 实例 ID。如果未提供，返回默认实例 ("demo")

**返回**:
```json
{
    "status": "success",
    "instance_id": "demo",
    "schema": {
        "meta": {...},
        "state": {...},
        "layout": {...},
        "blocks": [...],
        "actions": [...]
    }
}
```

### 3. `list_instances`

列出所有可用的 UI Schema 实例。

**返回**:
```json
{
    "status": "success",
    "instances": [
        {
            "instance_id": "demo",
            "page_key": "demo",
            "status": "idle",
            "blocks_count": 1,
            "actions_count": 1
        },
        ...
    ],
    "total": 3
}
```

## 支持的操作类型

| Op | 行为 | 允许的路径 | 必需字段 |
|-----|------|-----------|---------|
| `set` | 在路径设置值（如果缺失则创建） | 任意路径 | `path`, `value` |
| `add` | 在数组末尾添加项 | `blocks+`, `actions+` | `path`, `value` |
| `replace` | 替换路径上的项/数组 | `blocks`, `actions` | `path`, `value` |
| `remove` | 删除特定项 | `blocks-{id}`, `actions-{id}` | `path` |
| `clear` | 清除/重置为默认 | `state.params`, `state.runtime` | `path` |
| `create` | 创建新实例 | 特殊（见上方） | - |
| `delete` | 删除实例 | 特殊（见上方） | - |

## 支持的路径模式

### 状态路径

| 路径模式 | 描述 | 示例 |
|---------|------|------|
| `state.params.{key}` | 设置/更新参数 | `state.params.count` |
| `state.runtime.{key}` | 设置运行时状态 | `state.runtime.status` |

### Schema 结构路径

#### Blocks 操作

| 路径模式 | 描述 | 示例 |
|---------|------|------|
| `blocks` | 替换所有 blocks | `blocks` |
| `blocks+` | 在末尾添加 blocks | `blocks+` |
| `blocks-{index}` | 替换指定索引的 block | `blocks-0` |
| `blocks[{id}]` | 按 ID 替换 block | `blocks["form_block"]` |
| `blocks-{id}` | 按 ID 删除 block | `blocks-"form_block"` |

**支持的 Block 类型**: `form`

#### Actions 操作

| 路径模式 | 描述 | 示例 |
|---------|------|------|
| `actions` | 替换所有 actions | `actions` |
| `actions+` | 在末尾添加 actions | `actions+` |
| `actions-{index}` | 替换指定索引的 action | `actions-0` |
| `actions[{id}]` | 按 ID 替换 action | `actions["submit"]` |
| `actions-{id}` | 按 ID 删除 action | `actions-"submit"` |

**支持的 Action 样式**: `primary`, `secondary`, `danger`

#### Layout & Meta

| 路径模式 | 描述 | 示例 |
|---------|------|------|
| `layout` | 替换 layout | `layout` |
| `meta.status` | 更新 meta 状态 | `meta.status` |
| `meta.step` | 更新步骤信息 | `meta.step` |

**支持的 Layout 类型**: `single`
**支持的 Meta 状态**: `idle`, `submitted`

## 本地运行

### 快速启动（推荐）

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

### 方式 1：HTTP 模式（端口 8766）

```bash
cd backend/mcp
set MCP_TRANSPORT=http
set MCP_PORT=8766
python tools.py
```

或者使用 PowerShell：

```powershell
cd backend/mcp
$env:MCP_TRANSPORT="http"
$env:MCP_PORT="8766"
python tools.py
```

服务器将在以下地址启动：
- HTTP 端点: `http://localhost:8766`
- SSE 端点: `http://localhost:8766/sse`

### 方式 2：STDIO 模式（默认）

```bash
cd backend/mcp
python tools.py
```

这是默认模式，通过标准输入输出通信。

### 方式 3：测试 MCP 工具（不启动服务器）

```bash
cd backend/mcp
python test_tools.py
```

这将运行单元测试，验证所有工具功能正常工作。

## MCP 配置示例

### Claude Desktop 配置（HTTP 模式，端口 8766）

在 Claude Desktop 的 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "ui-patch-server": {
      "command": "python",
      "args": [
        "z:\\respos\\example_web_app\\backend\\mcp\\tools.py"
      ],
      "env": {
        "PYTHONPATH": "z:\\respos\\example_web_app",
        "MCP_TRANSPORT": "http",
        "MCP_PORT": "8766"
      }
    }
  }
}
```

**Linux/Mac:**
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

### Cline (VS Code) 配置（HTTP 模式，端口 8766）

在 `.clinerules` 中添加 MCP 服务器配置：

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

### STDIO 模式配置

如果使用默认的 STDIO 模式，只需配置 `PYTHONPATH`：

```json
{
  "mcpServers": {
    "ui-patch-server": {
      "command": "python",
      "args": [
        "z:\\respos\\example_web_app\\backend\\mcp\\tools.py"
      ],
      "env": {
        "PYTHONPATH": "z:\\respos\\example_web_app"
      }
    }
  }
}
```

## 错误代码

| 错误代码 | 描述 | 解决方案 |
|---------|------|---------|
| `INVALID_INSTANCE` | 实例不存在 | 检查 instance_id |
| `INVALID_OP` | 未知的操作类型 | 使用有效的 op: set, add, remove, clear, replace, create, delete |
| `INVALID_PATH` | 路径语法错误 | 使用有效的路径模式 |
| `PATH_NOT_FOUND` | 无法解析路径 | 确保路径存在或可创建 |
| `SCHEMA_MUTATION` | 不可变字段修改 | 检查允许的字段 |
| `MISSING_VALUE` | 缺少必需的值 | 提供 `value` 字段 |
| `DUPLICATE_ID` | ID 已存在 | 使用唯一的 ID |
| `INSTANCE_EXISTS` | 实例 ID 冲突 | 使用不同的 instance_id |
| `INVALID_STRUCTURE` | 无效的 block/action 结构 | 验证 UISchema 格式 |

## 设计原则

### 单一写入路径

所有修改**必须**通过 `patch_ui_state`：

```
用户输入 → 前端乐观更新 → 动作点击 →
patch_ui_state 工具 → 后端应用 → WebSocket 推送 → 前端更新
```

### 优势

- ✅ **无竞争条件** - 单写入者模型
- ✅ **可预测行为** - 顺序应用
- ✅ **可调试** - 清晰的操作历史
- ✅ **AI 友好** - 完美适配 Agent 工作流

### 能力

- ✅ 修改状态 (`state.params`, `state.runtime`)
- ✅ 添加/删除/替换 blocks
- ✅ 添加/删除/替换 actions
- ✅ 更新 layout 和 metadata
- ✅ 创建/删除实例
- ✅ 动态构建完整 UI

## 相关文档

- [PATCH_SPEC.md](../../PATCH_SPEC.md) - 详细的 Patch 工具规范
- [MINIMAL_PROTOTYPE.md](../../MINIMAL_PROTOTYPE.md) - 最小原型说明
