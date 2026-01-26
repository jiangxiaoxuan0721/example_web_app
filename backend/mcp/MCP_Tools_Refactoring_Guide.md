# MCP 工具重构说明

## 概述

为了提高 MCP 工具的可用性和可维护性，我们将原来的大型 `patch_ui_state` 工具拆分为多个更小、更专注的工具。每个工具负责一类特定的操作，使 API 更直观、更易用。

## 设计理念

### 高度自由化但结构化

MCP 工具的设计核心理念是**高度自由化但结构化**：

1. **高度自由化**：
   - 支持动态创建任意 UI 结构（通过 blocks、fields、actions 的组合）
   - 支持复杂的逻辑处理（通过 handler 的多样化类型）
   - 无需为特定功能编写硬编码逻辑，所有功能都通过配置实现
   - 支持跨实例引用和组件复用
   - 支持 17 种字段类型和 9 种操作类型，可以组合出无限可能

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

### 工具描述的重要性

为了让 AI 智能体正确理解和使用 MCP 工具，工具描述应当：
- **明确功能范围**：清晰说明工具能做什么，不能做什么
- **提供使用场景**：给出典型使用场景，帮助 AI 判断何时使用该工具
- **说明参数约束**：详细说明参数的必需性、类型、默认值和取值范围
- **展示示例用法**：提供完整、可运行的示例代码
- **说明返回值**：详细说明返回值的结构和含义
- **指出注意事项**：提醒常见的陷阱和最佳实践

---

## 新工具列表

### 1. add_field

添加新字段到表单块。

**何时使用**: 当需要向表单添加新的输入字段时。

**优点**:
- 自动处理状态初始化
- 支持多种字段类型
- 简洁的参数结构

**示例**:
```python
# 添加文本字段
{
    "instance_id": "form",
    "field": {"label": "Username", "key": "username", "type": "text"},
    "state_path": "state.params.username"
}

# 添加选择字段
{
    "instance_id": "form",
    "field": {
        "label": "Country",
        "key": "country",
        "type": "select",
        "options": [{"label": "China", "value": "cn"}, {"label": "USA", "value": "us"}]
    },
    "state_path": "state.params.country"
}
```

---

### 2. update_field

更新现有字段的属性。

**何时使用**: 当需要修改字段的标签、类型或其他属性时。

**优点**:
- 支持批量更新
- 可选的跨块更新
- 自动验证字段存在

**示例**:
```python
# 更新字段标签
{
    "instance_id": "form",
    "field_key": "username",
    "updates": {"label": "Full Name"}
}

# 更新字段类型
{
    "instance_id": "form",
    "field_key": "description",
    "updates": {"type": "textarea"}
}

# 更新所有块中的同名字段
{
    "instance_id": "form",
    "field_key": "status",
    "updates": {"label": "Current Status"},
    "update_all": true
}
```

---

### 3. remove_field

从表单块中删除字段。

**何时使用**: 当需要移除不再需要的字段时。

**优点**:
- 支持批量删除
- 自动清理关联状态

**示例**:
```python
# 删除指定字段
{
    "instance_id": "form",
    "field_key": "old_field"
}

# 删除所有块中的同名字段
{
    "instance_id": "form",
    "field_key": "temp",
    "remove_all": true
}
```

---

### 4. add_block

添加新块到 UI 实例。

**何时使用**: 当需要创建新的内容区块时。

**优点**:
- 灵活的位置控制
- 支持块级别的 actions
- 自动刷新 UI

**示例**:
```python
# 在末尾添加块
{
    "instance_id": "demo",
    "block": {
        "id": "contact_form",
        "type": "form",
        "bind": "state.params",
        "props": {
            "fields": [
                {"label": "Name", "key": "name", "type": "text"}
            ]
        }
    }
}

# 在开始位置添加块
{
    "instance_id": "demo",
    "position": "start",
    "block": {
        "id": "header",
        "type": "display",
        "bind": "state.params",
        "props": {
            "fields": [{"label": "Title", "key": "title", "type": "html"}]
        }
    }
}

# 添加带 actions 的块
{
    "instance_id": "demo",
    "position": 1,
    "block": {
        "id": "actions_block",
        "type": "form",
        "bind": "state.params",
        "props": {
            "fields": [{"label": "Status", "key": "status", "type": "text"}]
        },
        "actions": [
            {
                "id": "reset",
                "label": "Reset Block",
                "style": "secondary",
                "handler_type": "set",
                "patches": {"state.params.status": ""}
            }
        ]
    }
}
```

---

### 5. remove_block

从 UI 实例中删除块。

**何时使用**: 当需要移除整个内容区块时。

**优点**:
- 支持 ID 批量删除
- 自动清理依赖

**示例**:
```python
# 删除单个块
{
    "instance_id": "form",
    "block_id": "old_block"
}

# 删除所有同名块
{
    "instance_id": "form",
    "block_id": "temp",
    "remove_all": true
}
```

---

### 6. add_action

添加新的操作按钮。

**何时使用**: 当需要为 UI 添加交互功能时。

**优点**:
- 支持全局和块级别 actions
- 丰富的 handler 类型
- 自动刷新 UI

**示例**:
```python
# 添加全局 action
{
    "instance_id": "form",
    "action": {
        "id": "clear",
        "label": "Clear",
        "style": "danger",
        "handler_type": "set",
        "patches": {"state.params.name": "", "state.runtime.status": "idle"}
    }
}

# 添加块级别 action
{
    "instance_id": "form",
    "block_index": 0,
    "action": {
        "id": "reset_block",
        "label": "Reset Block",
        "style": "secondary",
        "handler_type": "set",
        "patches": {"state.params.block_data": ""}
    }
}

# 添加导航 action
{
    "instance_id": "form",
    "action": {
        "id": "goto_list",
        "label": "Go to list",
        "style": "secondary",
        "action_type": "navigate",
        "target_instance": "list_page"
    }
}
```

---

### 7. remove_action

从 UI 实例中删除操作按钮。

**何时使用**: 当需要移除不再需要的操作按钮时。

**优点**:
- 支持批量删除
- 同时支持全局和块级别 actions

**示例**:
```python
# 删除全局 action
{
    "instance_id": "form",
    "action_id": "old_action"
}

# 删除块级别 action
{
    "instance_id": "form",
    "action_id": "reset",
    "block_index": 0
}

# 删除所有同名 action
{
    "instance_id": "form",
    "action_id": "temp",
    "remove_all": true
}
```

---

### 8. patch_ui_state (简化版)

应用原始补丁操作到 UI Schema。

**何时使用**:
- 需要执行复杂的批量操作
- 需要直接修改深层路径
- 需要一次性执行多个不相关的操作

**优点**:
- 完全的灵活性
- 支持所有补丁类型
- 批量操作效率高

**示例**:
```python
# 批量更新多个状态
{
    "instance_id": "counter",
    "patches": [
        {"op": "set", "path": "state.params.count", "value": 42},
        {"op": "set", "path": "state.runtime.status", "value": "updated"}
    ]
}

# 创建新实例
{
    "instance_id": "__CREATE__",
    "new_instance_id": "my_instance",
    "patches": [
        {"op": "set", "path": "meta", "value": {"pageKey": "my", "step": {"current": 1, "total": 1}}},
        {"op": "set", "path": "state", "value": {"params": {}, "runtime": {}}},
        {"op": "set", "path": "blocks", "value": []},
        {"op": "set", "path": "actions", "value": []}
    ]
}

# 删除实例
{
    "instance_id": "__DELETE__",
    "target_instance_id": "old_instance"
}
```

---

## 对比: 旧版 vs 新版

### 旧版 patch_ui_state

```python
# 添加字段 - 需要两个补丁
{
    "instance_id": "form",
    "patches": [
        {"op": "set", "path": "state.params.username", "value": ""},
        {"op": "add", "path": "blocks.0.props.fields", "value": {"label": "Username", "key": "username", "type": "text"}}
    ]
}

# 更新字段 - 需要知道字段索引
{
    "instance_id": "form",
    "field_key": "username",
    "updates": {"label": "Full Name"},
    "block_index": 0
}
```

**缺点**:
- 参数复杂,容易出错
- 需要手动构建补丁数组
- 字段索引不直观
- 文档冗长

---

### 新版专用工具

```python
# 添加字段 - 简洁清晰
{
    "instance_id": "form",
    "field": {"label": "Username", "key": "username", "type": "text"},
    "state_path": "state.params.username"
}

# 更新字段 - 直观明了
{
    "instance_id": "form",
    "field_key": "username",
    "updates": {"label": "Full Name"}
}
```

**优点**:
- 语义清晰,易于理解
- 参数结构合理
- 自动处理常见逻辑
- 文档专注,示例丰富

---

## 迁移指南

### 从旧版迁移到新版

**场景 1: 添加字段**

```python
# 旧版
{
    "instance_id": "form",
    "patches": [
        {"op": "set", "path": "state.params.name", "value": ""},
        {"op": "add", "path": "blocks.0.props.fields", "value": {"label": "Name", "key": "name", "type": "text"}}
    ]
}

# 新版 - 使用 add_field
{
    "instance_id": "form",
    "field": {"label": "Name", "key": "name", "type": "text"},
    "state_path": "state.params.name"
}
```

---

**场景 2: 更新字段**

```python
# 旧版 (快捷方式)
{
    "instance_id": "form",
    "field_key": "name",
    "updates": {"label": "Full Name"},
    "block_index": 0
}

# 新版 - 使用 update_field
{
    "instance_id": "form",
    "field_key": "name",
    "updates": {"label": "Full Name"}
}
```

---

**场景 3: 添加 block**

```python
# 旧版
{
    "instance_id": "demo",
    "patches": [{
        "op": "add",
        "path": "blocks",
        "value": {
            "id": "new_block",
            "type": "form",
            "bind": "state.params",
            "props": {"fields": [{"label": "Name", "key": "name", "type": "text"}]}
        }
    }]
}

# 新版 - 使用 add_block
{
    "instance_id": "demo",
    "block": {
        "id": "new_block",
        "type": "form",
        "bind": "state.params",
        "props": {"fields": [{"label": "Name", "key": "name", "type": "text"}]}
    }
}
```

---

**场景 4: 添加 action**

```python
# 旧版
{
    "instance_id": "form",
    "patches": [{
        "op": "add",
        "path": "actions",
        "value": {
            "id": "submit",
            "label": "Submit",
            "style": "primary",
            "handler_type": "set",
            "patches": {"state.runtime.status": "submitted"}
        }
    }]
}

# 新版 - 使用 add_action
{
    "instance_id": "form",
    "action": {
        "id": "submit",
        "label": "Submit",
        "style": "primary",
        "handler_type": "set",
        "patches": {"state.runtime.status": "submitted"}
    }
}
```

---

**场景 5: 批量操作 - 继续使用 patch_ui_state**

```python
# 复杂的批量操作仍使用 patch_ui_state
{
    "instance_id": "form",
    "patches": [
        {"op": "set", "path": "state.params.field1", "value": "value1"},
        {"op": "set", "path": "state.params.field2", "value": "value2"},
        {"op": "set", "path": "state.runtime.status", "value": "updated"}
    ]
}
```

---

## 最佳实践

### 1. 优先使用专用工具

对于常见的操作(添加/更新/删除字段、块、action),优先使用专用工具。它们更直观、更安全。

### 2. 使用 patch_ui_state 进行批量操作

当需要一次性执行多个操作时,使用 `patch_ui_state` 可以减少网络往返。

### 3. 利用自动刷新

所有新工具都会在操作成功后自动刷新实例,无需手动调用 `access_instance`。

### 4. 验证操作结果

在关键操作后,可以使用 `get_schema` 或 `validate_completion` 验证修改结果。

---

## 字段类型支持

所有 `add_field` 和 `update_field` 操作都支持以下字段类型:

- **text**: 单行文本输入
- **number**: 数字输入
- **textarea**: 多行文本区域
- **checkbox**: 布尔切换
- **select**: 下拉选择(需要 options)
- **radio**: 单选按钮组(需要 options)
- **multiselect**: 多选复选框组(需要 options)
- **json**: JSON 编辑器(带验证)
- **image**: 图片显示(带控件)
- **html**: 只读 HTML 内容
- **tag**: 标签显示
- **progress**: 进度条
- **badge**: 徽章通知
- **table**: 数据表格
- **modal**: 模态对话框

详细属性说明请参考 `MCP_Tool_Reference_Manual.md`。

---

## Handler 类型支持

所有 `add_action` 操作都支持以下 handler 类型:

### 基础 Handler 类型
- **set**: 直接赋值（支持 operation 对象执行复杂操作）
- **increment**: 增加数值
- **decrement**: 减少数值
- **toggle**: 布尔切换
- **template**: 模板渲染（支持模板变量替换）
- **external**: 调用外部 API（支持请求/响应映射）

### 扩展 Handler 类型
- **template:all**: 对所有路径执行模板渲染（用于批量更新）
- **template:state**: 只对 state 下的路径执行模板渲染

### set Handler 的 Operation 对象

set handler 支持通过 operation 对象执行复杂操作：

**支持的操作类型**:
- `append_to_list`: 向列表末尾添加元素
- `prepend_to_list`: 向列表开头添加元素
- `remove_from_list`: 从列表删除元素
- `update_list_item`: 更新列表中的元素
- `clear_all_params`: 清空所有 params
- `append_block`: 添加新块
- `prepend_block`: 在开头添加块
- `remove_block`: 删除块
- `update_block`: 更新块
- `merge`: 合并对象

**示例**:
```json
{
  "handler_type": "set",
  "patches": {
    "state.params.users": {
      "operation": "append_to_list",
      "params": {
        "item": {"id": 6, "name": "赵六"}
      }
    }
  }
}
```

详细说明请参考 `MCP_Tool_Reference_Manual.md` 中的 "Action Handler 详解"。

---

## 后向兼容性

**重要**: 旧的 `patch_ui_state` 工具仍然可用,所有现有代码无需修改即可继续工作。

但是,我们强烈建议新代码使用新的专用工具,以获得更好的开发体验。

---

## 总结

这次重构将一个复杂、多用途的工具拆分为多个专注、易用的工具,主要改进包括:

1. **更好的可用性**: 每个工具专注于一个任务,参数结构清晰
2. **更好的可维护性**: 每个工具的实现更简单,更容易测试
3. **更好的文档**: 每个工具有详细的文档和示例
4. **自动刷新**: 所有工具自动刷新 UI,无需手动调用
5. **后向兼容**: 旧版工具继续工作,平滑迁移
6. **高度自由化**: 通过配置实现任意功能，无需硬编码
7. **结构化**: 所有操作遵循预定义的数据模型和规范
8. **可扩展**: 支持新增字段类型、handler 类型等扩展

---

## 相关文档

- [MCP 工具完整参考手册](./MCP_Tool_Reference_Manual.md) - 所有工具的完整技术文档
- [MCP 快速示例](./MCP_Quick_Examples.md) - 常见使用场景的代码示例
