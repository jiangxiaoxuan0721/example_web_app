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

|| 工具名 | 功能 | 使用场景 |
||--------|------|----------|
|| `patch_ui_state` | 应用结构化补丁修改 UI | 创建实例、修改结构、更新状态、删除实例 |
|| `get_schema` | 获取实例的完整 Schema | 检查当前状态、分析结构、验证修改 |
|| `list_instances` | 列出所有可用实例 | 浏览实例、发现资源 |
|| `validate_completion` | 验证完成标准 | 评估进度、确定下一步、质量检查 |
|| `access_instance` | 访问并激活实例 | 切换上下文、标记活动实例 |

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

|| 参数名 | 类型 | 必需 | 默认值 | 说明 |
||--------|------|------|--------|------|
|| `instance_id` | string | ✅ | - | 目标实例 ID。<br>• `"__CREATE__"` - 创建新实例<br>• `"__DELETE__"` - 删除实例<br>• 其他 - 修改现有实例 |
|| `patches` | array | ❌ | `[]` | 补丁操作数组（见下方[操作类型](#操作类型）） |
|| `new_instance_id` | string | 条件必需 | `null` | 创建实例时必须提供新实例 ID |
|| `target_instance_id` | string | 条件必需 | `null` | 删除实例时必须提供目标实例 ID |
|| `field_key` | string | ❌ | `null` | 字段操作快捷方式：指定要更新/删除的字段键 |
|| `updates` | object | ❌ | `null` | 字段操作快捷方式：要更新的字段属性 |
|| `remove_field` | boolean | ❌ | `false` | 字段操作快捷方式：如果为 `true` 则删除指定字段 |
|| `block_index` | integer | ❌ | `0` | 指定要操作的 form block 索引（默认第一个） |

#### 操作类型

|| Op 类型 | 行为 | 允许的路径格式 | 必需字段 |
||---------|------|----------------|----------|
|| `set` | 设置路径值（如缺失则创建） | 任意路径（如 `state.params.count`） | `path`, `value` |
|| `add` | 在数组末尾添加元素 | **数组路径**（如 `blocks`, `actions`, `blocks.0.props.fields`） | `path`, `value` |
|| `remove` | 从数组中删除元素（按值匹配） | **数组路径**（如 `blocks`, `actions`, `blocks.0.props.fields`） | `path`, `value` |

#### 支持的路径模式

**状态路径**:
- `state.params.{key}` - 设置/更新参数
- `state.runtime.{key}` - 设置运行时状态

**Blocks 路径**:
- `blocks` - 替换所有 blocks（使用 `set`），或添加/删除 block（使用 `add`/`remove`）
- `blocks.0` - 操作第一个 block
- `blocks.0.props.fields` - 操作第一个 block 的字段数组（`add` 在末尾添加字段，`remove` 删除指定字段）
- `blocks.0.props.fields.0` - 替换第一个字段的所有属性
- `blocks.0.props.fields.0.label` - 修改第一个字段的 label 属性

**Actions 路径**:
- `actions` - 替换所有 actions（使用 `set`），或添加/删除 action（使用 `add`/`remove`）

**重要说明**:
- ❌ **不要使用** `blocks/-` 或 `actions/-` 格式（这是无效的）
- ✅ 使用 `blocks` 或 `actions` 进行 `add` 操作
- ✅ 使用 `blocks` 或 `actions` 配合完整的 `value` 进行 `remove` 操作（工具会按 `id` 或内容匹配）

#### 返回值

```typescript
interface PatchResponse {
  status: "success" | "error";
  message?: string;
  error?: string;
  instance_id?: string;
  patches_applied?: Array<patch>;      // 实际应用的补丁列表
  skipped_patches?: Array<{              // 被跳过的补丁及原因
    patch: patch;
    reason: string;
  }>;
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
  content_type?: string;       // 可选: 内容类型 (如 "json")
  // 图片字段专用属性
  showFullscreen?: boolean;
  showDownload?: boolean;
  imageHeight?: string;
  imageFit?: string;
  lazy?: boolean;
  fallback?: string;
  subtitle?: string;
}
```

**字段类型（type 属性支持的值）**:

| Type | 描述 | 特殊要求 |
|------|------|----------|
| `text` | 单行文本输入 | - |
| `number` | 数字输入 | - |
| `textarea` | 多行文本区域 | - |
| `checkbox` | 布尔切换 | - |
| `select` | 下拉选择 | 需要 `options` 数组 |
| `radio` | 单选按钮组 | 需要 `options` 数组 |
| `json` | JSON 编辑器，带验证 | - |
| `image` | 图片显示，带控制功能 | 支持图片专用属性 |
| `html` | 只读 HTML 内容 | - |

**图片专用属性**（仅当 `type="image"` 时有效）:

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `showFullscreen` | boolean | `true` | 是否显示全屏按钮 |
| `showDownload` | boolean | `true` | 是否显示下载按钮 |
| `imageHeight` | string | `"auto"` | 图片高度（如 "200px"） |
| `imageFit` | string | `"contain"` | 适应方式：`contain`/`cover`/`fill` |
| `lazy` | boolean | - | 是否懒加载 |
| `fallback` | string | - | 加载失败时的回退内容 |
| `subtitle` | string | - | 可选副标题 |

---

## Action Handler 详解

### Handler 类型总览

|| Handler | 说明 | patches 格式 | 使用场景 |
||---------|------|--------------|----------|
|| `set` | 直接设置值 | `{"路径": "值"}` | 清空表单、设置固定状态 |
|| `increment` | 数值增加 | `{"路径": 增量}` | 计数器增加、步进器 |
|| `decrement` | 数值减少 | `{"路径": 减量}` | 计数器减少、步退器 |
|| `toggle` | 布尔值切换 | `{"路径": true}` | 开关、复选框 |
|| `template` | 模板渲染 | `{"路径": "模板字符串"}` | 动态消息、状态提示 |
|| `external` | 调用外部 API | 配置对象 | 获取数据、提交表单、远程操作 |

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

|| 字段 | 类型 | 必需 | 说明 |
||------|------|------|------|
|| `url` | string | ✅ | API 端点 URL（支持模板变量） |
|| `method` | string | ❌ | HTTP 方法，默认 "POST" |
|| `headers` | dict | ❌ | 请求头（支持模板变量） |
|| `body_template` | dict | ❌ | 请求体模板（支持模板变量） |
|| `body_template_type` | string | ❌ | 请求体类型：`json`（默认）或 `form` |
|| `timeout` | number | ❌ | 超时时间（秒），默认 30 |
|| `response_mappings` | dict | ❌ | 成功响应映射 |
|| `error_mapping` | dict | ❌ | 错误响应映射 |

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

|| 错误代码 | HTTP 状态 | 描述 | 解决方案 |
||-----------|-----------|------|----------|
|| `INVALID_INSTANCE` | 404 | 实例不存在 | 检查 `instance_id` |
|| `INVALID_OP` | 400 | 未知的操作类型 | 使用有效的 op: set, add, remove |
|| `INVALID_PATH` | 400 | 路径语法错误 | 使用有效的路径模式 |
|| `PATH_NOT_FOUND` | 404 | 无法解析路径 | 确保路径存在或可创建 |
|| `SCHEMA_MUTATION` | 403 | 不可变字段修改 | 检查允许的字段 |
|| `MISSING_VALUE` | 400 | 缺少必需的值 | 提供 `value` 字段 |
|| `DUPLICATE_ID` | 409 | ID 已存在 | 使用唯一的 ID |
|| `INSTANCE_EXISTS` | 409 | 实例 ID 冲突 | 使用不同的 `instance_id` |
|| `INVALID_STRUCTURE` | 400 | 无效的 block/action 结构 | 验证 UISchema 格式 |

### 验证错误代码

|| 错误类型 | 描述 |
||----------|------|
|| `FIELD_NOT_FOUND` | 指定的字段路径不存在 |
|| `INVALID_CRITERION_TYPE` | 不支持的验证类型 |
|| `INVALID_CONDITION` | 自定义条件语法错误 |
|| `INVALID_JSON_PATH` | JSONPath 解析失败 |

---

## 设计原则

### 单一写入路径

所有修改**必须**通过 `patch_ui_state`：

```
用户输入 → 前端乐观更新 → Action 点击 →
patch_ui_state → 后端应用 → WebSocket 推送 → 前端更新
```

### 最小修改原则

- ✅ 使用精准路径（如 `blocks.0.props.fields.1.label`）
- ❌ 避免覆盖整个结构（如 `blocks`）
- ✅ 使用 `add` 操作添加元素
- ✅ 使用 `set` 操作修改属性

### 验证驱动

- ✅ 修改前使用 `get_schema` 检查状态
- ✅ 修改后使用 `validate_completion` 评估结果
- ✅ Agent 根据评估数据**自主决策**

---

## 相关文档

- [MCP_Quick_Examples.md](./MCP_Quick_Examples.md) - 快速示例文档（初学者）
