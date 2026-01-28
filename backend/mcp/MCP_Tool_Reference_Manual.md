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
    patches: list[dict[str, Any]] = [],
    new_instance_id: str | None = None,
    target_instance_id: str | None = None
) -> dict[str, Any]
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
| `multiselect` | 多选下拉框 | 需要 `options` 数组 |
| `json` | JSON 编辑器，带验证 | - |
| `image` | 图片显示，带控制功能 | 支持图片专用属性 |
| `table` | 表格显示 | 需要 `columns` 数组 |
| `component` | 组件嵌入 | 需要 `target_instance` |
| `date` | 日期选择器 | - |
| `datetime` | 日期时间选择器 | - |
| `file` | 文件上传 | - |
| `html` | 只读 HTML 内容 | - |
| `tag` | 标签显示 | - |
| `progress` | 进度条 | - |
| `badge` | 徽章 | - |
| `modal` | 模态框 | - |

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

直接设置字段值，或执行通用操作对象。

#### 1.1 直接设置值

覆盖现有值。

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

#### 1.2 操作对象

`set` handler 支持 **操作对象**，用于执行复杂的动态操作。

**操作对象格式**:
```json
{
  "operation": "操作名称",
  "params": {
    "参数名": "参数值"
  }
}
```

**支持的操作类型**:

| Operation | 说明 | params 格式 | 使用场景 |
|-----------|------|-------------|----------|
| `append_to_list` | 向列表末尾添加元素 | `{"items": [...]}` | 添加数据项、追加记录 |
| `prepend_to_list` | 向列表开头添加元素 | `{"items": [...]}` | 插入数据到开头 |
| `remove_from_list` | 从列表删除元素 | `{"key": "字段名", "value": "值"}` 或 `{"key": "字段名", "value": "值", "index": -1}` | 删除单个或批量删除 |
| `update_list_item` | 更新列表中的元素 | `{"key": "字段名", "value": "值", "updates": {...}}` | 修改某条记录 |
| `clear_all_params` | 清空所有 params | `{}` | 重置表单 |
| `append_block` | 添加新块 | `{"block": {...}}` | 动态添加 UI 组件 |
| `prepend_block` | 在开头添加块 | `{"block": {...}}` | 动态插入 UI 组件 |
| `remove_block` | 删除块 | `{"block_id": "..."}` | 移除 UI 组件 |
| `update_block` | 更新块 | `{"block_id": "...", "updates": {...}}` | 修改 UI 组件 |
| `merge` | 合并对象 | `{"data": {...}}` | 部分更新对象 |

**示例 1: 向列表添加元素**

```json
{
  "id": "add_user",
  "label": "添加用户",
  "style": "primary",
  "handler_type": "set",
  "patches": {
    "state.params.users": {
      "operation": "append_to_list",
      "params": {
        "items": [
          {
            "id": 6,
            "name": "赵六",
            "email": "zhaoliu@example.com",
            "status": "pending"
          }
        ]
      }
    }
  }
}
```

**示例 2: 从列表删除元素**

```json
{
  "id": "remove_user",
  "label": "删除用户",
  "style": "danger",
  "handler_type": "set",
  "patches": {
    "state.params.users": {
      "operation": "remove_from_list",
      "params": {
        "key": "id",
        "value": "5"
      }
    }
  }
}
```

**示例 3: 从列表删除单个元素**

```json
{
  "id": "remove_user",
  "label": "删除用户",
  "style": "danger",
  "handler_type": "set",
  "patches": {
    "state.params.users": {
      "operation": "remove_from_list",
      "params": {
        "key": "id",
        "value": "5"
      }
    }
  }
}
```

**示例 3.1: 批量删除列表元素（删除所有满足条件的项）**

```json
{
  "id": "clear_completed",
  "label": "清除已完成",
  "style": "danger",
  "handler_type": "set",
  "patches": {
    "state.params.todo_list": {
      "operation": "remove_from_list",
      "params": {
        "key": "completed",
        "value": true,
        "index": -1
      }
    }
  }
}
```

**说明**：当 `index` 为 `-1` 时，会删除所有满足 `key` 和 `value` 条件的项。例如，上述配置会删除所有 `completed=true` 的待办事项。

**示例 4: 更新列表中的元素**

```json
{
  "id": "update_user_status",
  "label": "激活用户",
  "style": "secondary",
  "handler_type": "set",
  "patches": {
    "state.params.users": {
      "operation": "update_list_item",
      "params": {
        "key": "id",
        "value": "5",
        "updates": {
          "status": "active"
        }
      }
    }
  }
}
```

**示例 5: 添加新块（动态 UI 组件）**

```json
{
  "id": "add_notification",
  "label": "添加通知",
  "style": "secondary",
  "handler_type": "set",
  "patches": {
    "blocks": {
      "operation": "append_block",
      "params": {
        "block": {
          "id": "notification_block",
          "type": "form",
          "bind": "state.params",
          "props": {
            "fields": [
              {
                "label": "系统通知",
                "key": "notification",
                "type": "html",
                "description": "这是一条动态添加的通知"
              }
            ]
          }
        }
      }
    }
  }
}
```

**示例 5: 删除块**

```json
{
  "id": "remove_notification",
  "label": "移除通知",
  "style": "danger",
  "handler_type": "set",
  "patches": {
    "blocks": {
      "operation": "remove_block",
      "params": {
        "block_id": "notification_block"
      }
    }
  }
}
```

**示例 6: 清空所有 params**

```json
{
  "id": "clear_form",
  "label": "清空表单",
  "style": "danger",
  "handler_type": "set",
  "patches": {
    "state.params": {
      "operation": "clear_all_params",
      "params": {}
    }
  }
}
```

**注意**:
- 操作对象只在 `handler_type` 为 `set` 时生效
- 所有操作都不需要后端预设，完全通过配置定义
- MCP 工具可以通过这种方式实现任何动态操作需求

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

#### 额外的 Handler 类型

除了 `set`, `increment`, `decrement`, `toggle`, `template`, `external` 外，系统还支持：

- **template:all**：对所有路径执行模板渲染（用于批量更新）
- **template:state**：只对 state 下的路径执行模板渲染

**template:all 示例**：
```json
{
  "handler_type": "template:all",
  "patches": {
    "state.params.message": "消息: ${state.params.value}",
    "blocks.0.props.fields.0.description": "说明: ${state.runtime.info}"
  }
}
```

这将同时渲染 patches 中所有包含模板变量的路径。

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
| `INVALID_OP` | 400 | 未知的操作类型 | 使用有效的 op: set, add, remove |
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

## 设计原则

### 高度自由化但结构化的调用

MCP 工具的设计核心理念是**高度自由化但结构化**，这意味着：

1. **高度自由化**：
   - 支持动态创建任意 UI 结构（通过 blocks、fields、actions 的组合）
   - 支持复杂的逻辑处理（通过 handler 的多样化类型）
   - 无需为特定功能编写硬编码逻辑，所有功能都通过配置实现
   - 支持跨实例引用和组件复用
   - 支持 19 种字段类型和 9 种操作类型，可以组合出无限可能

2. **结构化**：
   - 所有操作都遵循预定义的数据模型
   - 字段类型、handler 类型、操作类型都有明确的定义
   - 路径语法有统一的规范
   - 参数验证保证数据一致性
   - 工具描述提供清晰的指导，确保 AI 智能体能够正确理解和使用

3. **实现方式**：
   - **Schema 驱动**：前端通过解析 schema 动态渲染，无需针对特定功能编写代码
   - **通用处理器**：后端通过统一的 patch 应用机制处理所有操作
   - **配置即功能**：所有功能通过配置定义，而非硬编码
   - **模板渲染**：支持 `${state.xxx}` 语法，实现动态内容更新
   - **自动时间戳**：引用 `state.runtime.timestamp` 时自动更新为当前时间

4. **可扩展性**：
   - 新增字段类型只需在前端添加 renderer，后端无需改动
   - 新增 handler 类型只需在后端扩展处理逻辑
   - 支持通过 set handler 的 operation 对象实现自定义操作

5. **工具描述的重要性**：
   为了让 AI 智能体正确理解和使用 MCP 工具，工具描述应当：
   - 明确功能范围：清晰说明工具能做什么，不能做什么
   - 提供使用场景：给出典型使用场景，帮助 AI 判断何时使用该工具
   - 说明参数约束：详细说明参数的必需性、类型、默认值和取值范围
   - 展示示例用法：提供完整、可运行的示例代码
   - 说明返回值：详细说明返回值的结构和含义
   - 指出注意事项：提醒常见的陷阱和最佳实践

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

### 工具描述的重要性

为了让 AI 智能体正确理解和使用 MCP 工具，工具描述应当：

1. **明确功能范围**：清晰说明工具能做什么，不能做什么
2. **提供使用场景**：给出典型使用场景，帮助 AI 判断何时使用该工具
3. **说明参数约束**：详细说明参数的必需性、类型、默认值和取值范围
4. **展示示例用法**：提供完整、可运行的示例代码
5. **说明返回值**：详细说明返回值的结构和含义
6. **指出注意事项**：提醒常见的陷阱和最佳实践

---

## 相关文档

- [MCP_Quick_Examples.md](./MCP_Quick_Examples.md) - 快速示例文档（初学者）
