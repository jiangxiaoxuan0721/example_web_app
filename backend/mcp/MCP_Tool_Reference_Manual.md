# MCP 工具完整参考手册

> **面向开发者**：本手册提供了所有 MCP 工具的完整技术细节，包括参数、返回值、错误处理和内部实现。

## 目录

- [架构概述](#架构概述)
- [工具索引](#工具索引)
- [工具详细文档](#工具详细文档)
  - [1. patch_ui_state](#1-patch_ui_state)
  - [2. get_schema](#2-get_schema)
  - [3. list_instances](#3-list_instances)
  - [4. validate_completion](#4-validate_completion)
  - [5. access_instance](#5-access_instance)
- [数据模型](#数据模型)
- [Action Handler 详解](#action-handler-详解)
- [错误代码参考](#错误代码参考)
- [内部实现细节](#内部实现细节)

---

## 架构概述

### 系统组件

```
┌─────────────────────────────────────────────┐
│              Claude Desktop / Agent         │
│            (MCP Client)                     │
└──────────────────────┬──────────────────────┘
                       │ JSON-RPC
                       ▼
┌─────────────────────────────────────────────┐
│         MCP Tool Server (FastMCP)           │
│  ┌──────────────────────────────────────┐   │
│  │  tool_definitions.py (工具定义)       │   │
│  │  - 装饰器和参数文档                   │   │
│  │  - 类型安全                           │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │  tool_implements.py (工具实现)        │   │
│  │  - 业务逻辑                           │   │
│  │  - 数据验证                           │   │
│  └──────────────────────────────────────┘   │
│         │                                   │
│         │ HTTP / WebSocket                  │
│         ▼                                   │
│  ┌──────────────────────────────────────┐   │
│  │  InstanceService                     │   │
│  │  - Schema 管理                       │   │
│  │  - Action 处理                       │   │
│  │  - Patch 应用                        │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### 数据流

1. **读取流程**: Agent → MCP Tool → SchemaManager → 返回 Schema
2. **修改流程**: Agent → MCP Tool → InstanceService → Patch 应用 → WebSocket 推送
3. **验证流程**: Agent → MCP Tool → Schema 解析 → 返回评估数据

---

## 工具索引

| 工具名 | 功能 | 使用场景 |
|--------|------|----------|
| `patch_ui_state` | 应用结构化补丁修改 UI | 创建实例、修改结构、更新状态、删除实例 |
| `get_schema` | 获取实例的完整 Schema | 检查当前状态、分析结构、验证修改 |
| `list_instances` | 列出所有可用实例 | 浏览实例、发现资源 |
| `validate_completion` | 验证完成标准 | 评估进度、确定下一步、质量检查 |
| `access_instance` | 访问并激活实例 | 切换上下文、标记活动实例 |

---

## 工具详细文档

### 1. patch_ui_state

**功能**: 应用结构化补丁来修改 UI Schema 状态和结构。这是修改 UI 的**唯一方式**。

#### 函数签名

```python
async def patch_ui_state(
    instance_id: str,
    patches: List[Dict[str, Any]] = [],
    new_instance_id: Optional[str] = None,
    target_instance_id: Optional[str] = None,
    field_key: Optional[str] = None,
    updates: Optional[Dict[str, Any]] = None,
    remove_field: Optional[bool] = False,
    block_index: Optional[int] = 0
) -> Dict[str, Any]
```

#### 参数详解

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `instance_id` | string | ✅ | - | 目标实例 ID。<br>• `"__CREATE__"` - 创建新实例<br>• `"__DELETE__"` - 删除实例<br>• 其他 - 修改现有实例 |
| `patches` | array | ❌ | `[]` | 补丁操作数组（见下方[操作类型](#操作类型)） |
| `new_instance_id` | string | 条件必需 | `null` | 创建实例时必须提供新实例 ID |
| `target_instance_id` | string | 条件必需 | `null` | 删除实例时必须提供目标实例 ID |
| `field_key` | string | ❌ | `null` | 字段操作快捷方式：指定要更新/删除的字段键 |
| `updates` | object | ❌ | `null` | 字段操作快捷方式：要更新的字段属性 |
| `remove_field` | boolean | ❌ | `false` | 字段操作快捷方式：如果为 `true` 则删除指定字段 |
| `block_index` | integer | ❌ | `0` | 指定要操作的 form block 索引（默认第一个） |

#### 操作类型

| Op 类型 | 行为 | 允许的路径 | 必需字段 |
|---------|------|------------|----------|
| `set` | 在路径设置值（如缺失则创建） | 任意路径 | `path`, `value` |
| `add` | 在数组末尾添加项 | `blocks+`, `actions+` | `path`, `value` |
| `replace` | 替换路径上的项/数组 | `blocks`, `actions` | `path`, `value` |
| `remove` | 删除特定项 | `blocks-{id}`, `actions-{id}` | `path` |
| `clear` | 清除/重置为默认 | `state.params`, `state.runtime` | `path` |

#### 支持的路径模式

**状态路径**:
- `state.params.{key}` - 设置/更新参数
- `state.runtime.{key}` - 设置运行时状态

**Blocks 路径**:
- `blocks` - 替换所有 blocks
- `blocks+` - 在末尾添加 blocks
- `blocks-{index}` - 替换指定索引的 block
- `blocks[{id}]` - 按 ID 替换 block
- `blocks-{id}` - 按 ID 删除 block

**Actions 路径**:
- `actions` - 替换所有 actions
- `actions+` - 在末尾添加 actions
- `actions-{index}` - 替换指定索引的 action
- `actions[{id}]` - 按 ID 替换 action
- `actions-{id}` - 按 ID 删除 action

#### 返回值

```typescript
interface PatchResponse {
  status: "success" | "error";
  message?: string;
  error?: string;
  instance_id?: string;
  patch?: Record<string, any>;
  auto_refreshed?: boolean;           // 字段操作后的自动刷新状态
  auto_refresh_error?: string;          // 自动刷新失败时的错误信息
  navigate_to?: string;                // navigate 类型的 action 目标实例
}
```

#### 使用场景

| 场景 | 参数配置示例 |
|------|-------------|
| 创建新实例 | `instance_id="__CREATE__"`, `new_instance_id="new"`, `patches=[...]` |
| 删除实例 | `instance_id="__DELETE__"`, `target_instance_id="old"` |
| 更新状态值 | `instance_id="counter"`, `patches=[{"op":"set","path":"state.params.count","value":42}]` |
| 添加 block | `instance_id="demo"`, `patches=[{"op":"add","path":"blocks+","value":{...}}]` |
| 删除 action | `instance_id="form"`, `patches=[{"op":"remove","path":"actions-'old_action'"}]` |
| 快捷更新字段 | `instance_id="form"`, `field_key="email"`, `updates={"label":"新标签"}` |
| 快捷删除字段 | `instance_id="form"`, `field_key="email"`, `remove_field=true` |

#### 自动刷新机制

当使用字段快捷方式（`field_key` + `updates/remove_field`）时：
1. 工具内部会自动刷新实例状态
2. 返回结果包含 `auto_refreshed: true`
3. 如果刷新失败，`auto_refresh_error` 包含错误信息

---

### 2. get_schema

**功能**: 获取指定实例的当前 UI Schema。

#### 函数签名

```python
async def get_schema(instance_id: Optional[str] = None) -> Dict[str, Any]
```

#### 参数详解

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `instance_id` | string | ❌ | `"demo"` | 实例 ID。未提供时返回默认实例 |

#### 返回值

```typescript
interface SchemaResponse {
  status: "success" | "error";
  error?: string;
  instance_id: string;
  schema: UISchema;
}

interface UISchema {
  meta: MetaInfo;
  state: StateInfo;
  layout: LayoutInfo;
  blocks: Block[];
  actions: ActionConfig[];
}
```

---

### 3. list_instances

**功能**: 列出所有可用的 UI Schema 实例。

#### 函数签名

```python
async def list_instances() -> Dict[str, Any]
```

#### 返回值

```typescript
interface InstancesResponse {
  status: "success" | "error";
  error?: string;
  instances: Array<{
    instance_id: string;
    page_key: string;
    status: string;
    blocks_count: number;
    actions_count: number;
  }>;
  total: number;
}
```

---

### 4. validate_completion

**功能**: 验证 UI 实例是否满足特定的完成标准，返回客观评估数据供 Agent 自主决策。

#### 函数签名

```python
async def validate_completion(
    instance_id: str,
    intent: str,
    completion_criteria: List[Dict[str, Any]]
) -> Dict[str, Any]
```

#### 参数详解

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `instance_id` | string | ✅ | 要验证的实例 ID |
| `intent` | string | ✅ | UI 应实现的高级描述（用于上下文） |
| `completion_criteria` | array | ✅ | 验证标准列表（每项结构见下方） |

#### Completion Criteria 结构

```typescript
interface CompletionCriterion {
  type: "field_exists" | "field_value" | "block_count" | "action_exists" | "custom";
  path?: string;        // 字段路径
  value?: any;          // 期望值（用于 field_value）
  count?: number;        // 期望数量（用于 block_count）
  condition?: string;    // 自定义条件（用于 custom）
  description: string;  // 人类可读的描述
}
```

#### 支持的验证类型

| 类型 | 说明 | 必需参数 |
|------|------|----------|
| `field_exists` | 检查字段是否存在 | `path`, `description` |
| `field_value` | 检查字段值 | `path`, `value`, `description` |
| `block_count` | 检查块数量 | `count`, `description` |
| `action_exists` | 检查 action 是否存在 | `path`, `description` |
| `custom` | 自定义验证条件 | `condition`, `description` |

#### 返回值

```typescript
interface ValidationResponse {
  status: "success" | "error";
  error?: string;
  evaluation: {
    passed_criteria: number;           // 通过的条件数量
    total_criteria: number;            // 总条件数量
    completion_ratio: number;           // 完成比例 (0.0 - 1.0)
    detailed_results: Array<{
      type: string;
      description: string;
      passed: boolean;
      error?: string;                 // 验证错误（如果有）
    }>;
  };
  summary: string;                     // 高级评估总结
  recommendations: string[];           // 建议的下一步
}
```

**重要说明**: 
- 工具**只返回评估数据**，不提供 `is_complete` 布尔值
- Agent 根据 `completion_ratio` 等**自主决策**是否完成
- 这是一个**数据驱动**而非判断驱动的工具

---

### 5. access_instance

**功能**: 访问特定的 UI 实例并将其标记为活动状态。

#### 函数签名

```python
async def access_instance(instance_id: str) -> Dict[str, Any]
```

#### 参数详解

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `instance_id` | string | ✅ | 要访问的实例 ID |

#### 返回值

```typescript
interface AccessResponse {
  status: "success" | "error";
  error?: string;
  instance_id: string;
  schema: UISchema;
}
```

---

## 数据模型

### ActionConfig

```typescript
interface ActionConfig {
  id: string;                    // 必需: 唯一 action ID
  label: string;                 // 必需: action 按钮标签
  style: "primary" | "secondary" | "danger";  // 必需: 按钮样式
  action_type?: "api" | "navigate";            // 可选: 默认 "api"
  target_instance?: string;        // 可选: 目标实例 ID (navigate 时使用)
  handler_type?: HandlerType;     // 可选: 处理器类型
  patches?: Record<string, any>; // 可选: patch 映射
}

type HandlerType = "set" | "increment" | "decrement" | "toggle" | "template" | "external";
```

### Block

```typescript
interface Block {
  id: string;                 // 必需: 唯一 block ID
  type: string;                // 必需: block 类型 (form)
  bind: string;                // 必需: 绑定路径 (默认 "state.params")
  props?: BlockProps;          // 可选: block 属性
}

interface BlockProps {
  fields?: FieldConfig[];      // form 类型必需
  showProgress?: boolean;
  showStatus?: boolean;
  showImages?: boolean;
  showTable?: boolean;
  showCountInput?: boolean;
  showTaskId?: boolean;
}
```

### FieldConfig

```typescript
interface FieldConfig {
  label: string;               // 必需: 字段标签
  key: string;                 // 必需: 字段键
  type: string;                // 必需: 字段类型
  rid?: string;                // 可选: 资源 ID
  value?: any;                 // 可选: 默认值
  description?: string;        // 可选: 字段描述
  options?: Array<{ label: string; value: string }>;  // select/radio 必需
  editable?: boolean;           // 可选: 是否可编辑
  // 图片字段属性
  showFullscreen?: boolean;
  showDownload?: boolean;
  imageHeight?: string;
  imageFit?: string;
  lazy?: boolean;
  fallback?: string;
  subtitle?: string;
}
```

---

## Action Handler 详解

### Handler 类型总览

| Handler | 说明 | 配置结构 | 使用场景 |
|---------|------|-----------|----------|
| `set` | 直接设置值 | `{"路径": "值"}` | 清空表单、设置固定状态 |
| `increment` | 数值增加 | `{"路径": 增量}` | 计数器增加、步进器 |
| `decrement` | 数值减少 | `{"路径": 减量}` | 计数器减少、步退器 |
| `toggle` | 布尔值切换 | `{"路径": true}` | 开关、复选框 |
| `template` | 模板渲染 | `{"路径": "模板字符串"}` | 动态消息、状态提示 |
| `external` | 调用外部 API | 见下方 | 获取数据、提交表单、远程操作 |

### 1. set 处理器

直接设置字段值，覆盖现有值。

**配置示例**:
```json
{
  "id": "clear",
  "label": "清空",
  "style": "danger",
  "handler_type": "set",
  "patches": {
    "state.params.name": "",
    "state.params.email": "",
    "state.runtime.status": "idle",
    "state.runtime.message": ""
  }
}
```

### 2. increment / decrement 处理器

对数值字段进行加减操作。

**increment 示例**:
```json
{
  "id": "increment",
  "label": "+1",
  "style": "primary",
  "handler_type": "increment",
  "patches": {
    "state.params.count": 1
  }
}
```

**decrement 示例**:
```json
{
  "id": "decrement",
  "label": "-1",
  "style": "secondary",
  "handler_type": "decrement",
  "patches": {
    "state.params.count": 1
  }
}
```

### 3. toggle 处理器

切换布尔值状态。

**配置示例**:
```json
{
  "id": "toggle_mode",
  "label": "切换模式",
  "style": "secondary",
  "handler_type": "toggle",
  "patches": {
    "state.params.enabled": true
  }
}
```

### 4. template 处理器

支持模板变量渲染。使用 `${path}` 语法引用当前 state 的值。

**支持的路径格式**:
- `${state.params.xxx}` - 引用 params 中的值
- `${state.runtime.xxx}` - 引用 runtime 中的值

**配置示例**:
```json
{
  "id": "submit",
  "label": "提交",
  "style": "primary",
  "handler_type": "template",
  "patches": {
    "state.runtime.status": "submitted",
    "state.runtime.message": "表单已提交！姓名: ${state.params.name}, 邮箱: ${state.params.email}"
  }
}
```

### 5. external 处理器

调用外部 API 并将响应映射到 state。

#### 配置结构

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `url` | string | ✅ | API 端点 URL（支持模板变量） |
| `method` | string | ❌ | HTTP 方法，默认 "POST" |
| `headers` | dict | ❌ | 请求头（支持模板变量） |
| `body_template` | dict | ❌ | 请求体模板（支持模板变量） |
| `body_template_type` | string | ❌ | 请求体类型：`json`（默认）或 `form` |
| `timeout` | number | ❌ | 超时时间（秒），默认 30 |
| `response_mappings` | dict | ❌ | 成功响应映射 |
| `error_mapping` | dict | ❌ | 错误响应映射 |

#### 支持的 HTTP 方法

- `GET`
- `POST`
- `PUT`
- `DELETE`

#### 示例 1: GET 请求

```json
{
  "id": "fetch_user",
  "label": "获取用户信息",
  "style": "primary",
  "handler_type": "external",
  "patches": {
    "url": "https://api.example.com/users/${state.params.user_id}",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer ${state.params.token}"
    },
    "timeout": 30,
    "response_mappings": {
      "state.params.user_data": "",
      "state.runtime.message": "成功获取用户数据"
    },
    "error_mapping": {
      "state.runtime.error": "error.message",
      "state.runtime.status": "error"
    }
  }
}
```

#### 示例 2: POST 请求（带请求体）

```json
{
  "id": "create_user",
  "label": "创建用户",
  "style": "primary",
  "handler_type": "external",
  "patches": {
    "url": "https://api.example.com/users",
    "method": "POST",
    "body_template": {
      "name": "${state.params.name}",
      "email": "${state.params.email}",
      "age": "${state.params.age}"
    },
    "body_template_type": "json",
    "response_mappings": {
      "state.params.user_id": "data.id",
      "state.runtime.status": "success"
    },
    "error_mapping": {
      "state.runtime.error": "error.message",
      "state.runtime.status": "error"
    }
  }
}
```

#### 响应映射说明

- `response_mappings` 的 key 是目标 state 路径
- `response_mappings` 的 value 是 JSONPath（点分隔的路径）
- 空字符串 `""` 表示保存完整响应
- 支持数组索引：`data.users.0.name`

#### 错误处理

- HTTP 状态码非 2xx 时触发 `error_mapping`
- 超时异常触发 `error_mapping`
- 不提供 `error_mapping` 时使用默认错误处理

---

## 错误代码参考

### 通用错误代码

| 错误代码 | HTTP 状态 | 描述 | 解决方案 |
|-----------|-----------|------|----------|
| `INVALID_INSTANCE` | 404 | 实例不存在 | 检查 `instance_id` |
| `INVALID_OP` | 400 | 未知的操作类型 | 使用有效的 op: set, add, remove, clear, replace |
| `INVALID_PATH` | 400 | 路径语法错误 | 使用有效的路径模式 |
| `PATH_NOT_FOUND` | 404 | 无法解析路径 | 确保路径存在或可创建 |
| `SCHEMA_MUTATION` | 403 | 不可变字段修改 | 检查允许的字段 |
| `MISSING_VALUE` | 400 | 缺少必需的值 | 提供 `value` 字段 |
| `DUPLICATE_ID` | 409 | ID 已存在 | 使用唯一的 ID |
| `INSTANCE_EXISTS` | 409 | 实例 ID 冲突 | 使用不同的 `instance_id` |
| `INVALID_STRUCTURE` | 400 | 无效的 block/action 结构 | 验证 UISchema 格式 |

### 验证错误代码

| 错误类型 | 描述 |
|----------|------|
| `FIELD_NOT_FOUND` | 指定的字段路径不存在 |
| `INVALID_CRITERION_TYPE` | 不支持的验证类型 |
| `INVALID_CONDITION` | 自定义条件语法错误 |
| `INVALID_JSON_PATH` | JSONPath 解析失败 |

---

## 内部实现细节

### 代码组织

```
backend/
├── fastapi/
│   ├── services/
│   │   ├── instance_service.py    # 实例管理、Action 处理
│   │   └── patch.py                # Patch 应用逻辑
│   └── models.py                  # Pydantic 数据模型
└── mcp/
    ├── tool_definitions.py        # 工具定义（装饰器）
    ├── tool_implements.py        # 工具实现（业务逻辑）
    └── tools.py                # MCP 服务器入口
```

### 关键实现

#### InstanceService.handle_action

处理用户 action 点击，执行对应的 handler。

```python
def handle_action(
    self,
    instance_id: str,
    action_id: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    # 1. 获取 schema
    schema = self.schema_manager.get(instance_id)
    
    # 2. 同步前端 params
    if params:
        params_patch = {f"state.params.{k}": v for k, v in params.items()}
        apply_patch_to_schema(schema, params_patch)
    
    # 3. 查找 action 配置
    action_config = next((a for a in schema.actions if a.id == action_id), None)
    
    # 4. 执行 handler
    if action_config.handler_type:
        patch = self._execute_action_handler(schema, action_config)
        apply_patch_to_schema(schema, patch)
    
    return {"status": "success", "patch": patch}
```

#### External Handler 实现

```python
def _handle_external_api(self, schema, config) -> Dict[str, Any]:
    # 1. 准备请求（模板渲染）
    url = self._render_template(schema, config["url"])
    headers = {k: self._render_template(schema, v) for k, v in config.get("headers", {}).items()}
    
    # 2. 发起 HTTP 请求
    with httpx.Client(timeout=config.get("timeout", 30)) as client:
        response = client.request(method, url, headers=headers, ...)
    
    # 3. 处理响应
    if 200 <= response.status_code < 300:
        response_data = response.json()
        # 应用 response_mappings
        for target_path, json_path in config.get("response_mappings", {}).items():
            value = self._get_json_path_value(response_data, json_path)
            patch[target_path] = value
    else:
        # 应用 error_mapping
        ...
    
    return patch
```

### WebSocket 推送机制

修改完成后，通过 WebSocket 推送 patch 到前端：

```python
# 在 patch_ui_state 实现中
async def patch_ui_state_impl(...):
    # 应用 patch
    apply_patch_to_schema(schema, patch)
    
    # 推送到前端
    await websocket_manager.broadcast({
        "type": "patch",
        "instance_id": instance_id,
        "patch": patch
    })
```

---

## 设计原则

### 单一写入路径

所有修改**必须**通过 `patch_ui_state`：

```
用户输入 → 前端乐观更新 → Action 点击 →
patch_ui_state → 后端应用 → WebSocket 推送 → 前端更新
```

### 最小修改原则

- ✅ 使用精准路径（如 `blocks.0.fields.1.label`）
- ❌ 避免覆盖整个结构（如 `blocks`）
- ✅ 使用 `add` 操作而非 `replace`

### 验证驱动

- ✅ 修改前使用 `get_schema` 检查状态
- ✅ 修改后使用 `validate_completion` 评估结果
- ✅ Agent 根据评估数据**自主决策**

---

## 相关文档

- [MCP_Quick_Examples.md](./MCP_Quick_Examples.md) - 快速示例文档（初学者）
- [PATCH_SPEC.md](../../PATCH_SPEC.md) - Patch 规范
- [MINIMAL_PROTOTYPE.md](../../MINIMAL_PROTOTYPE.md) - 系统架构
