# Schema 详解

本文档详细说明了 UI Schema 的结构、字段和最佳实践。

## Schema 概览

UI Schema 是定义界面的核心数据结构，包含以下 5 个主要部分：

```typescript
interface UISchema {
  page_key: string;           // 页面标识符
  state: StateInfo;            // 状态信息
  layout: LayoutInfo;          // 布局信息
  blocks: Block[];             // UI 块列表
  actions: ActionConfig[];     // 全局操作列表
}
```

## 1. page_key

页面标识符，用于区分不同的 UI 实例。

```json
{
  "page_key": "user_management"
}
```

### 重要说明
- 创建实例时通过 `page_key` path 设置
- 每个实例的 `page_key` 应该唯一
- 用于路由和缓存

### 设置方式

```json
{
  "instance_name": "__CREATE__",
  "new_instance_name": "my_app",
  "patches": [
    {"op": "set", "path": "page_key", "value": "my_app"}
  ]
}
```

## 2. state

状态管理，包含用户参数和运行时数据。

```typescript
interface StateInfo {
  params: Record<string, any>;    // 用户参数
  runtime: Record<string, any>;   // 运行时数据
}
```

### 2.1 params（用户参数）

存储用户输入的参数，字段通过 `key` 从这里读写数据。

```json
{
  "state": {
    "params": {
      "username": "alice",
      "email": "alice@example.com",
      "age": 30,
      "interests": ["tech", "music"],
      "settings": {
        "theme": "dark",
        "notifications": true
      }
    }
  }
}
```

#### 使用方式

在 field 中引用：

```json
{
  "key": "username",
  "type": "text",
  "label": "用户名",
  "value": "${state.params.username}"
}
```

在 action 中修改：

```json
{
  "handler_type": "set",
  "patches": {
    "state.params.username": "new_value"
  }
}
```

### 2.2 runtime（运行时数据）

存储系统运行时数据，通常包含自动更新的信息。

```json
{
  "state": {
    "runtime": {
      "timestamp": "2026-02-09 15:30:45",
      "temp_rowData": {},
      "last_updated": "2026-02-09T15:30:45Z"
    }
  }
}
```

#### 特殊字段

- `temp_rowData` - 表格行操作的临时数据

### 2.3 模板引用

在模板中使用 state：

```json
{
  "type": "html",
  "value": "<p>欢迎，${state.params.username}！</p><p>当前时间：${state.runtime.timestamp}</p>"
}
```

#### 支持的路径格式

```javascript
${state.params.xxx}        // 参数值
${state.runtime.xxx}       // 运行时值
${params.xxx}              // 参数值（简写）
${runtime.xxx}             // 运行时值（简写）
${state.params.user.name}  // 嵌套对象
```

## 3. layout

布局信息，决定 blocks 如何排列。

```typescript
interface LayoutInfo {
  type: LayoutType;         // 布局类型
  columns?: number;         // 列数（仅 grid）
  gap?: string;            // 间距
}

enum LayoutType {
  SINGLE = "single",       // 单页布局
  FLEX = "flex",           // 弹性布局
  GRID = "grid",           // 网格布局
  TABS = "tabs"            // 标签页布局
}
```

### 3.1 single（单页布局）

简单的单页显示，blocks 垂直排列。

```json
{
  "layout": {
    "type": "single"
  }
}
```

### 3.2 flex（弹性布局）

blocks 水平或垂直弹性排列。

```json
{
  "layout": {
    "type": "flex",
    "gap": "20px"
  }
}
```

### 3.3 grid（网格布局）

blocks 按网格排列，适合复杂布局。

```json
{
  "layout": {
    "type": "grid",
    "columns": 2,
    "gap": "20px"
  }
}
```

### 3.4 tabs（标签页布局）

blocks 显示为标签页，最常用的布局类型。

```json
{
  "layout": {
    "type": "tabs"
  }
}
```

#### tabs 布局的 block 结构

```json
{
  "id": "user_profile",
  "layout": "form",
  "title": "用户资料",  // 标签页标题
  "props": {
    "fields": [...],
    "actions": [...]
  }
}
```

详见 [布局系统](./layout-guide.md)。

## 4. blocks

UI 块列表，每个 block 是一个独立的 UI 容器。

```typescript
interface Block {
  id: string;              // 块 ID
  layout: BlockLayoutType; // 块内布局
  title?: string;          // 块标题（tabs 布局时显示为标签页标题）
  props: BlockProps;       // 块属性
}
```

### 4.1 Block 布局类型

每个 block 内部有自己的布局类型：

```typescript
enum BlockLayoutType {
  FORM = "form",          // 表单布局
  GRID = "grid",          // 网格布局
  TABS = "tabs",          // 标签页布局
  ACCORDION = "accordion" // 折叠面板布局
}
```

### 4.2 form（表单布局）

最常用的 block 布局，fields 垂直排列。

```json
{
  "id": "user_form",
  "layout": "form",
  "title": "用户信息",
  "props": {
    "fields": [
      {"key": "name", "type": "text", "label": "姓名"},
      {"key": "email", "type": "text", "label": "邮箱"}
    ],
    "actions": [
      {"id": "save", "label": "保存", "action_type": "apply_patch"}
    ]
  }
}
```

### 4.3 grid（网格布局）

fields 按网格排列。

```json
{
  "id": "details",
  "layout": "grid",
  "title": "详细信息",
  "props": {
    "cols": 2,
    "gap": "20px",
    "fields": [
      {"key": "firstName", "type": "text", "label": "名"},
      {"key": "lastName", "type": "text", "label": "姓"},
      {"key": "phone", "type": "text", "label": "电话"},
      {"key": "email", "type": "text", "label": "邮箱"}
    ]
  }
}
```

### 4.4 tabs（标签页布局）

fields 分组到标签页中。

```json
{
  "id": "settings",
  "layout": "tabs",
  "title": "设置",
  "props": {
    "tabs": [
      {
        "label": "基本信息",
        "fields": [
          {"key": "username", "type": "text", "label": "用户名"}
        ]
      },
      {
        "label": "安全设置",
        "fields": [
          {"key": "password", "type": "text", "label": "密码"}
        ]
      }
    ]
  }
}
```

### 4.5 accordion（折叠面板布局）

fields 分组到可折叠的面板中。

```json
{
  "id": "faq",
  "layout": "accordion",
  "title": "常见问题",
  "props": {
    "panels": [
      {
        "title": "账号问题",
        "fields": [
          {"key": "q1", "type": "html", "value": "<p>如何注册？</p>"}
        ]
      },
      {
        "title": "支付问题",
        "fields": [
          {"key": "q2", "type": "html", "value": "<p>支持哪些支付方式？</p>"}
        ]
      }
    ]
  }
}
```

## 5. actions

全局操作列表，独立于 block 的 actions。

```typescript
interface ActionConfig {
  id: string;              // 操作 ID
  label: string;           // 按钮标签
  style?: ButtonStyle;     // 按钮样式
  disabled?: boolean;      // 是否禁用
  action_type: string;     // 操作类型
  handler_type?: string;   // 处理器类型
  patches?: any;           // Patch 定义
  confirm?: boolean;       // 是否需要确认
}
```

### 5.1 action_type

操作类型，决定点击后的行为。

```typescript
enum ActionType {
  API = "api",                  // API 调用
  NAVIGATE = "navigate",         // 实例导航
  NAVIGATE_BLOCK = "navigate_block", // 块导航
  MODAL = "modal",              // 模态框
  PATCH = "apply_patch"         // 应用 Patch
}
```

### 5.2 Patch 操作类型

当 `action_type` 为 `"apply_patch"` 时，patches 中可以使用的操作类型：

```typescript
enum PatchOperationType {
  SET = "set",              // 设置值
  INCREMENT = "increment",  // 增加数值
  DECREMENT = "decrement",  // 减少数值
  TOGGLE = "toggle",       // 切换布尔值
  ADD = "add",             // 添加元素
  REMOVE = "remove",       // 移除元素
  MERGE = "merge",         // 合并对象
  // ... 更多操作类型
}
```

### 5.3 操作示例

```json
{
  "actions": [
    {
      "id": "save",
      "label": "保存",
      "style": "primary",
      "action_type": "apply_patch",
      "patches": [
        {"op": "set", "path": "state.params.saved", "value": true}
      ]
    },
    {
      "id": "increment",
      "label": "增加",
      "action_type": "apply_patch",
      "patches": [
        {"op": "increment", "path": "state.params.count", "value": 1}
      ]
    }
  ]
}
```

## 完整示例

```json
{
  "page_key": "user_management",
  "state": {
    "params": {
      "username": "",
      "email": "",
      "count": 0
    },
    "runtime": {
      "timestamp": "2026-02-09 15:30:45"
    }
  },
  "layout": {
    "type": "tabs"
  },
  "blocks": [
    {
      "id": "user_info",
      "layout": "form",
      "title": "用户信息",
      "props": {
        "fields": [
          {
            "key": "username",
            "type": "text",
            "label": "用户名",
            "value": "${state.params.username}",
            "required": true
          },
          {
            "key": "email",
            "type": "text",
            "label": "邮箱",
            "value": "${state.params.email}",
            "required": true
          },
          {
            "key": "count",
            "type": "number",
            "label": "计数",
            "value": "${state.params.count}",
            "disabled": true
          }
        ],
        "actions": [
          {
            "id": "increment",
            "label": "增加",
            "action_type": "apply_patch",
            "handler_type": "increment",
            "patches": {"state.params.count": 1}
          }
        ]
      }
    }
  ],
  "actions": [
    {
      "id": "reset",
      "label": "重置",
      "style": "default",
      "action_type": "apply_patch",
      "handler_type": "set",
      "patches": {
        "state.params.count": 0
      }
    }
  ]
}
```

## 最佳实践

### 1. 命名规范

- `page_key`: 使用小写字母和下划线，如 `user_management`
- `block.id`: 使用描述性名称，如 `user_info`, `settings`
- `field.key`: 使用小写字母和下划线，如 `first_name`, `user_email`
- `action.id`: 使用动词+名词，如 `save_user`, `delete_item`

### 2. 状态管理

- 相关字段组织在同一个对象中：
  ```json
  {
    "params": {
      "user": {"name": "...", "email": "..."},
      "settings": {"theme": "...", "lang": "..."}
    }
  }
  ```

- 使用模板避免硬编码：
  ```json
  {
    "value": "${state.params.user.name}"
  }
  ```

### 3. 布局选择

- 单页简单表单：使用 `layout.type = "single"` + `block.layout = "form"`
- 多步骤流程：使用 `layout.type = "tabs"`
- 复杂配置：使用 `layout.type = "grid"` 或 `block.layout = "tabs"`
- 节省空间：使用 `block.layout = "accordion"`

### 4. 操作设计

- 为每个操作提供清晰的 `id` 和 `label`
- 使用 `style` 区分主次操作：
  - 主要操作：`"primary"`（如保存、提交）
  - 次要操作：`"default"`（如取消、重置）
  - 危险操作：`"danger"`（如删除）
- 使用 `confirm` 标记需要确认的操作

## 相关文档

- [字段类型参考](./field-types.md) - 所有字段类型详解
- [布局系统](./layout-guide.md) - 布局类型详细说明
- [事件处理](./event-handling.md) - Action 和事件系统
- [状态管理](./state-management.md) - 状态管理最佳实践
