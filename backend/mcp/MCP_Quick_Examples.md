# MCP 工具快速示例

> **面向初学者**：本文档提供了常见场景的简单示例，帮助你快速上手 MCP 工具。

## 目录

- [快速开始](#快速开始)
- [基础操作](#基础操作)
  - [查看实例](#查看实例)
  - [更新状态](#更新状态)
  - [添加字段](#添加字段)
  - [删除字段](#删除字段)
  - [更新字段](#更新字段)
  - [修改字段类型](#修改字段类型)
  - [添加按钮](#添加按钮)
- [实例管理](#实例管理)
  - [创建新实例](#创建新实例)
  - [删除实例](#删除实例)
- [验证操作](#验证操作)
- [完整示例](#完整示例)

---

## 快速开始

### 第一步：列出所有实例

```python
# 查看当前有哪些可用的实例
result = await list_instances()

# 输出：
# {
#   "status": "success",
#   "instances": [
#     {"instance_id": "demo", "page_key": "demo", ...},
#     {"instance_id": "counter", "page_key": "counter", ...},
#     {"instance_id": "form", "page_key": "form", ...}
#   ],
#   "total": 3
# }
```

### 第二步：查看某个实例的详细信息

```python
# 查看 demo 实例的完整结构
schema_result = await get_schema(instance_id="demo")

# 输出包含：
# - meta: 页面信息
# - state: 当前的状态数据
# - blocks: 页面上的组件
# - actions: 可点击的按钮
```

---

## 基础操作

### 查看实例

**场景**: 我想看看 counter 实例长什么样

```python
# 获取 counter 实例的 schema
result = await get_schema(instance_id="counter")

print(result["schema"]["state"]["params"]["count"])  # 输出: 0
print(result["schema"]["blocks"])                     # 输出 blocks 数组
print(result["schema"]["actions"])                    # 输出 actions 数组
```

---

### 更新状态

**场景**: 我想把计数器的值改成 100

```python
# 直接修改计数器的值
result = await patch_ui_state(
    instance_id="counter",
    patches=[
        {
            "op": "set",
            "path": "state.params.count",
            "value": 100
        }
    ]
)

print(result)  # {"status": "success", "patches_applied": [...]}
```

**一次性修改多个值**:

```python
# 同时修改多个状态值
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {"op": "set", "path": "state.params.name", "value": "张三"},
        {"op": "set", "path": "state.params.email", "value": "zhangsan@example.com"},
        {"op": "set", "path": "state.runtime.status", "value": "editing"}
    ]
)
```

---

### 添加字段

**场景**: 我想给表单添加一个"电话"字段

```python
# 方法1：使用标准 patch（推荐）
result = await patch_ui_state(
    instance_id="form",
    patches=[
        # 先在 state 中添加字段
        {"op": "set", "path": "state.params.telephone", "value": ""},
        # 然后在页面上显示这个字段
        {
            "op": "add",
            "path": "blocks.0.props.fields",
            "value": {
                "label": "电话",
                "key": "telephone",
                "type": "text",
                "description": "请输入手机号码"
            }
        }
    ]
)
```

**添加数字字段**:

```python
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {"op": "set", "path": "state.params.age", "value": 0},
        {
            "op": "add",
            "path": "blocks.0.props.fields",
            "value": {
                "label": "年龄",
                "key": "age",
                "type": "number",
                "description": "请输入年龄"
            }
        }
    ]
)
```

**添加下拉选择字段**:

```python
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {"op": "set", "path": "state.params.country", "value": ""},
        {
            "op": "add",
            "path": "blocks.0.props.fields",
            "value": {
                "label": "国家",
                "key": "country",
                "type": "select",
                "options": [
                    {"label": "中国", "value": "cn"},
                    {"label": "美国", "value": "us"},
                    {"label": "日本", "value": "jp"}
                ]
            }
        }
    ]
)
```

**说明**:
- `state.params` 中必须先有这个字段
- `blocks.0.props.fields` 是第一个表单块的字段列表
- `add` 操作会在数组末尾添加新字段

---

### 删除字段

**场景**: 我想从表单中删除"电话"字段

```python
# 使用标准 patch 删除
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {
            "op": "remove",
            "path": "blocks.0.props.fields",
            "value": {"key": "telephone"}
        }
    ]
)
```

---

### 更新字段

**场景**: 我想把"邮箱"字段的标签改成"电子邮箱地址"

```python
# 方法1：替换整个字段（修改所有属性）
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {
            "op": "set",
            "path": "blocks.0.props.fields.0",
            "value": {
                "label": "电子邮箱地址",
                "key": "email",
                "type": "text",
                "description": "请输入您的电子邮箱"
            }
        }
    ]
)
```

**方法2：只修改某个属性**:

```python
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {
            "op": "set",
            "path": "blocks.0.props.fields.0.label",
            "value": "电子邮箱地址"
        }
    ]
)
```

---

### 修改字段类型

**场景**: 我想把文本输入改成多行文本框

```python
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {
            "op": "set",
            "path": "blocks.0.props.fields.0.type",
            "value": "textarea"
        }
    ]
)
```

**可用字段类型**:
- `text` - 单行文本输入
- `number` - 数字输入
- `textarea` - 多行文本区域
- `checkbox` - 布尔切换
- `select` - 下拉选择（需要 `options`）
- `radio` - 单选按钮组（需要 `options`）
- `json` - JSON 编辑器
- `image` - 图片显示
- `html` - 只读 HTML 内容

---

### 添加按钮

**场景**: 我想给表单添加一个"重置"按钮

```python
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {
            "op": "add",
            "path": "actions",
            "value": {
                "id": "reset",
                "label": "重置",
                "style": "danger",
                "handler_type": "set",
                "patches": {
                    "state.params.name": "",
                    "state.params.email": "",
                    "state.runtime.status": "idle"
                }
            }
        }
    ]
)
```

**添加计数器增加按钮**:

```python
result = await patch_ui_state(
    instance_id="counter",
    patches=[
        {
            "op": "add",
            "path": "actions",
            "value": {
                "id": "increment",
                "label": "+",
                "style": "primary",
                "handler_type": "increment",
                "patches": {
                    "state.params.count": 1
                }
            }
        }
    ]
)
```

**添加导航按钮**:

```python
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {
            "op": "add",
            "path": "actions",
            "value": {
                "id": "go_to_counter",
                "label": "去计数器",
                "style": "secondary",
                "action_type": "navigate",
                "target_instance": "counter"
            }
        }
    ]
)
```

**按钮 Handler 类型**:
- `set` - 直接设置值
- `increment` - 数值增加
- `decrement` - 数值减少
- `toggle` - 布尔切换
- `template` - 模板渲染
- `external` - 外部 API 调用

**按钮样式**:
- `primary` - 主要按钮（蓝色）
- `secondary` - 次要按钮（灰色）
- `danger` - 危险操作（红色）

---

## 实例管理

### 创建新实例

**场景**: 我想创建一个全新的"任务列表"实例

```python
result = await patch_ui_state(
    instance_id="__CREATE__",
    new_instance_id="todo_list",
    patches=[
        # 1. 设置元数据
        {
            "op": "set",
            "path": "meta",
            "value": {
                "pageKey": "todo_list",
                "step": {"current": 1, "total": 1},
                "status": "idle",
                "schemaVersion": "1.0"
            }
        },
        # 2. 设置初始状态
        {
            "op": "set",
            "path": "state",
            "value": {
                "params": {"tasks": [], "new_task": ""},
                "runtime": {}
            }
        },
        # 3. 设置页面结构
        {
            "op": "set",
            "path": "blocks",
            "value": [
                {
                    "id": "todo_block",
                    "type": "form",
                    "bind": "state.params",
                    "props": {
                        "fields": [
                            {
                                "label": "新任务",
                                "key": "new_task",
                                "type": "text",
                                "description": "输入任务内容"
                            },
                            {
                                "label": "任务列表",
                                "key": "tasks",
                                "type": "textarea",
                                "description": "所有任务",
                                "editable": False
                            }
                        ]
                    }
                }
            ]
        },
        # 4. 设置按钮
        {
            "op": "set",
            "path": "actions",
            "value": [
                {
                    "id": "add_task",
                    "label": "添加任务",
                    "style": "primary",
                    "handler_type": "template",
                    "patches": {
                        "state.params.tasks": "${state.params.tasks}\n${state.params.new_task}",
                        "state.params.new_task": ""
                    }
                }
            ]
        }
    ]
)
```

---

### 删除实例

**场景**: 我想删除"todo_list"实例

```python
result = await patch_ui_state(
    instance_id="__DELETE__",
    target_instance_id="todo_list",
    patches=[]
)

print(result)  # {"status": "success", "message": "Instance 'todo_list' deleted successfully"}
```

---

## 验证操作

### 检查字段是否存在

**场景**: 我想确认"电话"字段是否已经添加

```python
result = await validate_completion(
    instance_id="form",
    intent="检查电话字段是否存在",
    completion_criteria=[
        {
            "type": "field_exists",
            "path": "state.params.telephone",
            "description": "电话字段在状态中存在"
        }
    ]
)

print(result["evaluation"]["passed_criteria"])    # 通过的条件数量
print(result["evaluation"]["total_criteria"])  # 总条件数量
print(result["evaluation"]["completion_ratio"]) # 完成比例 (0.0 - 1.0)
```

---

## 完整示例

### 示例1：创建一个计数器页面

**目标**: 创建一个可以增减数字的计数器

```python
# 1. 创建新实例
await patch_ui_state(
    instance_id="__CREATE__",
    new_instance_id="my_counter",
    patches=[
        # 设置元数据
        {
            "op": "set",
            "path": "meta",
            "value": {
                "pageKey": "my_counter",
                "step": {"current": 1, "total": 1},
                "status": "idle"
            }
        },
        # 设置初始状态
        {
            "op": "set",
            "path": "state",
            "value": {
                "params": {"count": 0},
                "runtime": {}
            }
        },
        # 添加显示数字的字段
        {
            "op": "set",
            "path": "blocks",
            "value": [
                {
                    "id": "display_block",
                    "type": "form",
                    "bind": "state.params",
                    "props": {
                        "fields": [
                            {
                                "label": "计数",
                                "key": "count",
                                "type": "text"
                            }
                        ]
                    }
                }
            ]
        },
        # 添加按钮
        {
            "op": "set",
            "path": "actions",
            "value": [
                {
                    "id": "increment",
                    "label": "+1",
                    "style": "primary",
                    "handler_type": "increment",
                    "patches": {"state.params.count": 1}
                },
                {
                    "id": "decrement",
                    "label": "-1",
                    "style": "secondary",
                    "handler_type": "decrement",
                    "patches": {"state.params.count": 1}
                }
            ]
        }
    ]
)

# 2. 验证是否创建成功
validation = await validate_completion(
    instance_id="my_counter",
    intent="创建一个计数器页面",
    completion_criteria=[
        {"type": "field_exists", "path": "state.params.count", "description": "有计数器字段"},
        {"type": "action_exists", "path": "increment", "description": "有+1按钮"},
        {"type": "action_exists", "path": "decrement", "description": "有-1按钮"}
    ]
)

if validation["evaluation"]["completion_ratio"] == 1.0:
    print("✅ 计数器创建成功！")
else:
    print("❌ 计数器创建失败，需要检查")
```

---

### 示例2：创建带多种字段类型的表单

**目标**: 创建一个包含多种字段类型的表单

```python
await patch_ui_state(
    instance_id="__CREATE__",
    new_instance_id="rich_form",
    patches=[
        {
            "op": "set",
            "path": "meta",
            "value": {
                "pageKey": "rich_form",
                "step": {"current": 1, "total": 1},
                "status": "idle"
            }
        },
        {
            "op": "set",
            "path": "state",
            "value": {
                "params": {
                    "name": "",
                    "age": 0,
                    "country": "",
                    "terms": false
                },
                "runtime": {}
            }
        },
        {
            "op": "set",
            "path": "blocks",
            "value": [
                {
                    "id": "form_block",
                    "type": "form",
                    "bind": "state.params",
                    "props": {
                        "fields": [
                            # 文本字段
                            {
                                "label": "姓名",
                                "key": "name",
                                "type": "text",
                                "description": "请输入您的姓名"
                            },
                            # 数字字段
                            {
                                "label": "年龄",
                                "key": "age",
                                "type": "number",
                                "description": "请输入您的年龄"
                            },
                            # 下拉选择
                            {
                                "label": "国家",
                                "key": "country",
                                "type": "select",
                                "options": [
                                    {"label": "中国", "value": "cn"},
                                    {"label": "美国", "value": "us"}
                                ]
                            },
                            # 复选框
                            {
                                "label": "同意条款",
                                "key": "terms",
                                "type": "checkbox"
                            }
                        ]
                    }
                }
            ]
        },
        {
            "op": "set",
            "path": "actions",
            "value": [
                {
                    "id": "submit",
                    "label": "提交",
                    "style": "primary",
                    "handler_type": "set",
                    "patches": {"state.runtime.status": "submitted"}
                }
            ]
        }
    ]
)
```

---

## 常见问题

### Q: 我不知道字段在数组中的索引怎么办？

**A**: 使用精确路径进行修改，无需猜测索引：

```python
# 方法1：替换整个字段
{"op": "set", "path": "blocks.0.props.fields.0", "value": {...}}

# 方法2：只修改特定属性
{"op": "set", "path": "blocks.0.props.fields.0.label", "value": "新标签"}
```

### Q: 我应该什么时候使用 `add`，什么时候用 `set`？

**A**:
- `add`: 在数组**末尾**添加新元素（如添加字段、block、action）
- `set`: 设置整个数组的值，或修改特定路径的值

```python
# 添加新字段（在末尾）
{"op": "add", "path": "blocks.0.props.fields", "value": new_field}

# 添加新 block
{"op": "add", "path": "blocks", "value": {"id": "new_block", "type": "form", ...}}

# 替换整个字段数组
{"op": "set", "path": "blocks.0.props.fields", "value": [field1, field2, field3]}

# 修改特定字段属性
{"op": "set", "path": "blocks.0.props.fields.0.label", "value": "更新标签"}

# 删除 block（通过 id 匹配）
{"op": "remove", "path": "blocks", "value": {"id": "old_block"}}
```

**重要**: 不要使用 `blocks/-` 或 `actions/-` 这种格式，这是无效的！

### Q: 如何删除一个实例？

**A**: 使用 `__DELETE__` 特殊 ID：

```python
await patch_ui_state(
    instance_id="__DELETE__",
    target_instance_id="old_instance",
    patches=[]
)
```

### Q: validate_completion 的完成度是多少时算完成？

**A**: 
- `1.0` = 所有条件都通过 ✅
- `≥ 0.8` = 大部分通过，基本完成 ⚠️
- `< 0.8` = 还有较多问题 ❌

根据你的需求灵活判断，不一定非要等到 1.0。

---

## 总结

### 核心工具

|| 工具 | 主要用途 | 常用参数 |
||------|----------|----------|
|| `get_schema` | 查看当前状态 | `instance_id` |
|| `patch_ui_state` | 修改 UI | `instance_id`, `patches` |
|| `validate_completion` | 验证结果 | `instance_id`, `completion_criteria` |
|| `list_instances` | 浏览实例 | 无 |
|| `access_instance` | 切换实例 | `instance_id` |

### 推荐工作流

```
1. 列出实例
   ↓
2. 选择实例，查看详细信息
   ↓
3. 使用 patch_ui_state 修改
   ↓
4. 使用 validate_completion 验证
   ↓
5. 根据验证结果决定继续或停止
```

---

## 下一步

- 📖 查看完整技术文档：[MCP_Tool_Reference_Manual.md](./MCP_Tool_Reference_Manual.md)
