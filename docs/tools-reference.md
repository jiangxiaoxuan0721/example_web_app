# MCP 工具参考手册

本文档详细说明了所有 MCP 工具的使用方法。

## 工具列表

系统提供 **5 个核心 MCP 工具**：

| 工具名 | 类型 | 用途 |
|--------|------|------|
| `patch_ui_state` | 通用 | 修改 UI 状态（创建/删除/修改实例） |
| `get_schema` | 查询 | 获取实例的完整 Schema |
| `list_instances` | 查询 | 列出所有可用实例 |
| `validate_completion` | 查询 | 验证实例是否满足条件 |
| `access_instance` | 操作 | 访问并激活实例 |

---

## 1. patch_ui_state

唯一的 UI 修改方式，支持创建、删除和修改实例。

### 函数签名

```python
async def patch_ui_state(
    instance_name: str,
    patches: list[dict[str, Any]] = [],
    new_instance_name: str | None = None,
    target_instance_name: str | None = None
) -> dict[str, Any]
```

### 参数说明

#### instance_name（必需）

目标实例名称，使用以下值之一：

| 值 | 用途 |
|----|------|
| `"__CREATE__"` | 创建新实例 |
| `"__DELETE__"` | 删除实例 |
| 现有实例名 | 修改现有实例 |

#### patches（必需）

Patch 操作数组，每个 patch 包含：

```json
{
  "op": "set" | "add" | "remove",
  "path": "schema.path",
  "value": any,
  "index": number  // 可选，仅 update_list_item 使用
}
```

**支持的 path 格式**：

- `"meta"` - 元数据
- `"state"` - 状态
- `"state.params.xxx"` - 参数值
- `"state.runtime.xxx"` - 运行时数据
- `"blocks"` - 所有块
- `"blocks.0"` - 第一个块
- `"blocks.0.props.fields"` - 第一个块的字段
- `"blocks.0.props.actions"` - 第一个块的操作
- `"actions"` - 全局操作

#### new_instance_name（可选）

创建新实例时使用，指定新实例名称。

**必需条件**：`instance_name == "__CREATE__"`

#### target_instance_name（可选）

删除实例时使用，指定要删除的实例名称。

**必需条件**：`instance_name == "__DELETE__"`

### 使用示例

#### 示例 1：创建新实例

```json
{
  "instance_name": "__CREATE__",
  "new_instance_name": "my_app",
  "patches": [
    {"op": "set", "path": "page_key", "value": "my_app"},
    {"op": "set", "path": "state", "value": {"params": {}, "runtime": {}}},
    {"op": "set", "path": "layout", "value": {"type": "tabs"}},
    {"op": "set", "path": "blocks", "value": [
      {"id": "welcome", "layout": "form", "title": "欢迎", "props": {"fields": [], "actions": []}}
    ]},
    {"op": "set", "path": "actions", "value": []}
  ]
}
```

#### 示例 2：删除实例

```json
{
  "instance_name": "__DELETE__",
  "target_instance_name": "old_app"
}
```

#### 示例 3：更新状态

```json
{
  "instance_name": "my_app",
  "patches": [
    {"op": "set", "path": "state.params.count", "value": 42},
    {"op": "set", "path": "state.runtime.timestamp", "value": "2026-02-09 15:30:45"}
  ]
}
```

#### 示例 4：添加字段

```json
{
  "instance_name": "my_app",
  "patches": [
    {"op": "set", "path": "blocks.0.props.fields", "value": [
      {"key": "username", "type": "text", "label": "用户名", "value": "${state.params.username}"},
      {"key": "email", "type": "text", "label": "邮箱", "value": "${state.params.email}"}
    ]}
  ]
}
```

#### 示例 5：添加操作

```json
{
  "instance_name": "my_app",
  "patches": [
    {"op": "set", "path": "blocks.0.props.actions", "value": [
      {
        "id": "save",
        "label": "保存",
        "style": "primary",
        "action_type": "apply_patch",
        "handler_type": "set",
        "patches": {"state.params.saved": true}
      }
    ]}
  ]
}
```

#### 示例 6：添加块

```json
{
  "instance_name": "my_app",
  "patches": [
    {"op": "add", "path": "blocks", "value": {
      "id": "settings",
      "layout": "form",
      "title": "设置",
      "props": {"fields": [], "actions": []}
    }}
  ]
}
```

#### 示例 7：删除块

```json
{
  "instance_name": "my_app",
  "patches": [
    {"op": "remove", "path": "blocks", "value": {
      "id": "old_block"
    }}
  ]
}
```

#### 示例 8：批量操作

```json
{
  "instance_name": "my_app",
  "patches": [
    {"op": "set", "path": "state.params.count", "value": 0},
    {"op": "set", "path": "state.params.username", "value": ""},
    {"op": "set", "path": "state.params.email", "value": ""},
    {"op": "set", "path": "blocks.0.props.fields", "value": []},
    {"op": "set", "path": "blocks.0.props.actions", "value": []}
  ]
}
```

### 操作类型（op）

| op | 行为 | 允许的 path | 必需字段 |
|----|------|-------------|----------|
| `set` | 设置值 | 任意 path | `path`, `value` |
| `add` | 添加到数组末尾 | `blocks`, `actions` | `path`, `value` |
| `remove` | 删除特定项 | `blocks`, `actions` | `path`, `value`（通过 id 匹配） |

**注意事项**：
- ❌ 不要使用 `blocks/-` 或 `actions/-` 格式（无效）
- ✅ 使用 `blocks` 或 `actions` 进行 `add` 操作
- ✅ 使用 `blocks` 或 `actions` 配合完整 `value` 进行 `remove` 操作（工具通过 `id` 匹配）

---

## 2. get_schema

获取实例的完整 UI Schema。

### 函数签名

```python
async def get_schema(instance_name: str) -> dict[str, Any]
```

### 参数说明

#### instance_name（必需）

要查询的实例名称。

### 返回值

```json
{
  "status": "success",
  "instance_name": "my_app",
  "schema": {
    "page_key": "my_app",
    "state": {...},
    "layout": {...},
    "blocks": [...],
    "actions": [...]
  }
}
```

### 使用示例

```python
result = await get_schema(instance_name="demo")
schema = result["schema"]

# 访问特定字段
count = schema["state"]["params"]["count"]
blocks = schema["blocks"]
```

### 使用场景

- 检查当前状态
- 分析 UI 结构
- 验证修改结果
- 调试问题

---

## 3. list_instances

列出所有可用的 UI Schema 实例。

### 函数签名

```python
async def list_instances() -> dict[str, Any]
```

### 返回值

```json
{
  "status": "success",
  "instances": [
    {"name": "demo", "page_key": "demo"},
    {"name": "counter", "page_key": "counter"},
    {"name": "user_form", "page_key": "user_form"}
  ],
  "total": 3
}
```

### 使用示例

```python
result = await list_instances()
instances = result["instances"]
total = result["total"]

for instance in instances:
    print(f"Instance: {instance['name']}")
```

### 使用场景

- 浏览可用实例
- 发现实例资源
- 检查实例状态

---

## 4. validate_completion

验证实例是否满足特定的完成条件。

### 函数签名

```python
async def validate_completion(
    instance_name: str,
    intent: str | None = None,
    completion_criteria: list[dict[str, Any]] = []
) -> dict[str, Any]
```

### 参数说明

#### instance_name（必需）

要验证的实例名称。

#### intent（可选）

任务意图描述，帮助理解验证目的。

#### completion_criteria（可选）

完成条件数组，每个条件包含：

```json
{
  "type": "field_exists" | "field_equals" | "field_not_empty" | "custom",
  "path": "state.params.xxx",
  "value": any,  // 可选，field_equals 使用
  "description": "条件描述"
}
```

**支持的条件类型**：

| type | 说明 | 必需字段 |
|------|------|----------|
| `field_exists` | 字段存在 | `path` |
| `field_equals` | 字段等于指定值 | `path`, `value` |
| `field_not_empty` | 字段不为空 | `path` |
| `custom` | 自定义条件 | 自定义 |

### 使用示例

#### 示例 1：检查字段是否存在

```json
{
  "instance_name": "user_form",
  "completion_criteria": [
    {
      "type": "field_exists",
      "path": "state.params.username",
      "description": "用户名字段存在"
    },
    {
      "type": "field_exists",
      "path": "state.params.email",
      "description": "邮箱字段存在"
    }
  ]
}
```

#### 示例 2：检查字段值

```json
{
  "instance_name": "counter",
  "completion_criteria": [
    {
      "type": "field_equals",
      "path": "state.params.count",
      "value": 10,
      "description": "计数等于 10"
    }
  ]
}
```

#### 示例 3：检查字段不为空

```json
{
  "instance_name": "user_form",
  "completion_criteria": [
    {
      "type": "field_not_empty",
      "path": "state.params.username",
      "description": "用户名不为空"
    },
    {
      "type": "field_not_empty",
      "path": "state.params.email",
      "description": "邮箱不为空"
    }
  ]
}
```

#### 示例 4：获取用户输入

```json
{
  "instance_name": "settings",
  "intent": "获取用户配置"
}
```

### 返回值

```json
{
  "status": "success",
  "instance_name": "settings",
  "completed": true,
  "state_summary": {
    "params": {
      "username": "alice",
      "email": "alice@example.com"
    },
    "runtime": {
      "timestamp": "2026-02-09 15:30:45"
    }
  },
  "criteria_results": [...]
}
```

### 使用场景

- 评估任务完成状态
- 确定下一步操作
- 质量检查
- 获取用户输入

---

## 5. access_instance

访问特定实例并标记为活动实例。

### 函数签名

```python
async def access_instance(instance_name: str) -> dict[str, Any]
```

### 参数说明

#### instance_name（必需）

要访问的实例名称。

### 返回值

```json
{
  "status": "success",
  "instance_name": "my_app",
  "schema": {
    "page_key": "my_app",
    "state": {...},
    "layout": {...},
    "blocks": [...],
    "actions": [...]
  }
}
```

### 使用示例

```python
result = await access_instance(instance_name="demo")
schema = result["schema"]
```

### 使用场景

- 切换上下文
- 标记活动实例
- 在多实例之间切换

---

## 工具使用最佳实践

### 1. 创建实例

**完整模板**：

```json
{
  "instance_name": "__CREATE__",
  "new_instance_name": "app_name",
  "patches": [
    {"op": "set", "path": "page_key", "value": "app_name"},
    {"op": "set", "path": "state", "value": {"params": {}, "runtime": {}}},
    {"op": "set", "path": "layout", "value": {"type": "tabs"}},
    {"op": "set", "path": "blocks", "value": []},
    {"op": "set", "path": "actions", "value": []}
  ]
}
```

### 2. 批量修改

使用一次调用完成多个修改：

```json
{
  "instance_name": "app",
  "patches": [
    {"op": "set", "path": "state.params.count", "value": 0},
    {"op": "set", "path": "state.params.name", "value": ""},
    {"op": "set", "path": "blocks.0.props.fields", "value": [...]}
  ]
}
```

### 3. 验证后再操作

先验证，再修改：

```python
# 1. 获取当前状态
result = await validate_completion({
    "instance_name": "app"
})
state = result["state_summary"]["params"]

# 2. 根据状态进行修改
if state.get("step") == "completed":
    await patch_ui_state({
        "instance_name": "app",
        "patches": [{"op": "set", "path": "state.params.next_step", "value": true}]
    })
```

### 4. 错误处理

```python
try:
    result = await patch_ui_state({...})
    if result["status"] != "success":
        print(f"Error: {result.get('error')}")
except Exception as e:
    print(f"Exception: {e}")
```

### 5. 使用模板

避免硬编码，使用模板引用：

```json
{
  "key": "welcome",
  "type": "html",
  "value": "<p>欢迎，${state.params.username}！</p>"
}
```

## 相关文档

- [Schema 详解](./schema-guide.md) - Schema 结构详细说明
- [Patching 机制](./patching-mechanism.md) - Patch 操作深入理解
- [事件处理](./event-handling.md) - Action 和事件系统
- [模板语法](./template-syntax.md) - 模板使用指南
