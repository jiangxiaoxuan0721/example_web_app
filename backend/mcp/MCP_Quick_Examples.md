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

print(result)  # {"status": "success", "patch": {"state.params.count": 100}}
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

**说明**:
- `state.params` 中必须先有这个字段
- `blocks.0.props.fields` 是第一个表单块的字段列表
- `add` 操作会在数组末尾添加新字段

---

### 删除字段

**场景**: 我想从表单中删除"电话"字段

```python
# 使用字段快捷方式（简单）
result = await patch_ui_state(
    instance_id="form",
    field_key="telephone",
    remove_field=True
)

# 输出：
# {
#   "status": "success",
#   "message": "Field 'telephone' removed successfully",
#   "auto_refreshed": true
# }
```

**使用标准 patch 删除**:

```python
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
# 使用字段快捷方式（简单）
result = await patch_ui_state(
    instance_id="form",
    field_key="email",
    updates={
        "label": "电子邮箱地址",
        "type": "email",  # 把类型改成邮箱输入
        "description": "请输入您的电子邮箱地址",
        "required": True
    }
)
```

**使用标准 patch 更新**:

```python
# 需要知道字段在数组中的位置（这里是第2个字段，索引为1）
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {
            "op": "set",
            "path": "blocks.0.props.fields.1",
            "value": {
                "label": "电子邮箱地址",
                "key": "email",
                "type": "email",
                "description": "请输入您的电子邮箱地址"
            }
        }
    ]
)
```

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
                "style": "secondary",
                "handler_type": "set",
                "patches": {
                    "state.params.name": "",
                    "state.params.email": ""
                }
            }
        }
    ]
)
```

**添加一个"导航到其他页面"按钮**:

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
                "style": "primary",
                "action_type": "navigate",
                "target_instance": "counter"
            }
        }
    ]
)
```

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
        },
        {
            "type": "field_exists",
            "path": "blocks.0.props.fields.2",
            "description": "表单中有第三个字段（电话）"
        }
    ]
)

print(result["evaluation"]["passed_criteria"])    # 通过的条件数量
print(result["evaluation"]["total_criteria"])  # 总条件数量
print(result["evaluation"]["completion_ratio"]) # 完成比例 (0.0 - 1.0)
```

**如何判断是否完成**:

```python
if result["evaluation"]["completion_ratio"] >= 1.0:
    print("✅ 所有条件都满足，操作完成！")
elif result["evaluation"]["completion_ratio"] >= 0.8:
    print("⚠️ 大部分条件满足，可能需要小调整")
else:
    print("❌ 还有很多条件未满足，需要继续操作")
```

---

### 检查字段值

**场景**: 我想确认计数器的值是否是 100

```python
result = await validate_completion(
    instance_id="counter",
    intent="计数器值应该是100",
    completion_criteria=[
        {
            "type": "field_value",
            "path": "state.params.count",
            "value": 100,
            "description": "计数器值为100"
        }
    ]
)

if result["evaluation"]["completion_ratio"] == 1.0:
    print("✅ 计数器值正确")
else:
    print("❌ 计数器值不正确")
```

---

### 检查组件数量

**场景**: 我想确认表单只有 1 个 block 和 3 个按钮

```python
result = await validate_completion(
    instance_id="form",
    intent="表单应该有1个block和3个按钮",
    completion_criteria=[
        {
            "type": "block_count",
            "count": 1,
            "description": "表单有1个block"
        }
    ]
)

# 注意：检查 action 数量需要使用 custom 类型
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

### 示例2：修改现有表单

**目标**: 给 form 实例添加电话字段，并更新邮箱字段

```python
# 1. 先查看当前状态
current = await get_schema(instance_id="form")
print("当前字段:", [f["key"] for f in current["schema"]["blocks"][0]["props"]["fields"]])

# 2. 添加电话字段
await patch_ui_state(
    instance_id="form",
    patches=[
        {"op": "set", "path": "state.params.telephone", "value": ""},
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

# 3. 更新邮箱字段（使用快捷方式）
await patch_ui_state(
    instance_id="form",
    field_key="email",
    updates={
        "label": "电子邮箱",
        "type": "email"
    }
)

# 4. 验证修改结果
validation = await validate_completion(
    instance_id="form",
    intent="表单应该有3个字段：姓名、邮箱、电话",
    completion_criteria=[
        {"type": "field_exists", "path": "state.params.name", "description": "姓名字段存在"},
        {"type": "field_exists", "path": "state.params.email", "description": "邮箱字段存在"},
        {"type": "field_exists", "path": "state.params.telephone", "description": "电话字段存在"},
        {"type": "block_count", "count": 1, "description": "只有1个表单块"}
    ]
)

completion_ratio = validation["evaluation"]["completion_ratio"]
print(f"完成度: {completion_ratio * 100}%")

if completion_ratio == 1.0:
    print("✅ 所有修改完成！")
elif completion_ratio >= 0.8:
    print("⚠️ 基本完成，可能需要微调")
else:
    print("❌ 还有问题需要修复")
```

---

### 示例3：创建一个带外部API调用的表单

**目标**: 创建一个可以获取用户信息的表单

```python
# 1. 创建实例
await patch_ui_state(
    instance_id="__CREATE__",
    new_instance_id="user_info",
    patches=[
        # 元数据
        {
            "op": "set",
            "path": "meta",
            "value": {
                "pageKey": "user_info",
                "step": {"current": 1, "total": 1},
                "status": "idle"
            }
        },
        # 初始状态
        {
            "op": "set",
            "path": "state",
            "value": {
                "params": {"user_id": "1"},
                "runtime": {}
            }
        },
        # 表单字段
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
                            {"label": "用户ID", "key": "user_id", "type": "text"},
                            {"label": "用户信息", "key": "user_data", "type": "textarea", "editable": False}
                        ]
                    }
                }
            ]
        },
        # 按钮（调用外部API）
        {
            "op": "set",
            "path": "actions",
            "value": [
                {
                    "id": "fetch_user",
                    "label": "获取用户信息",
                    "style": "primary",
                    "handler_type": "external",
                    "patches": {
                        "url": "https://jsonplaceholder.typicode.com/users/${state.params.user_id}",
                        "method": "GET",
                        "timeout": 30,
                        "response_mappings": {
                            "state.params.user_data": "",
                            "state.runtime.status": "success"
                        },
                        "error_mapping": {
                            "state.runtime.error": "error.message",
                            "state.runtime.status": "error"
                        }
                    }
                }
            ]
        }
    ]
)
```

---

### 示例4：错误处理

**目标**: 正确处理可能出现的错误

```python
# 删除字段的错误处理
result = await patch_ui_state(
    instance_id="form",
    field_key="nonexistent_field",
    remove_field=True
)

if result.get("status") == "error":
    error_msg = result.get("error", "")
    
    if "not found" in error_msg.lower():
        print("⚠️ 字段不存在，无需删除")
    elif "not a form block" in error_msg.lower():
        print("⚠️ 目标块不是表单类型")
    else:
        print(f"❌ 删除失败: {error_msg}")
else:
    print("✅ 字段删除成功")

# 检查自动刷新状态
if result.get("auto_refreshed"):
    print("✅ 实例已自动刷新")
elif result.get("auto_refresh_error"):
    print(f"⚠️ 刷新失败: {result['auto_refresh_error']}")
```

---

## 常见问题

### Q: 我不知道字段在数组中的索引怎么办？

**A**: 使用字段快捷方式（`field_key`），不需要知道索引：

```python
# ❌ 不推荐：需要知道索引
await patch_ui_state(
    instance_id="form",
    patches=[{"op": "set", "path": "blocks.0.props.fields.2", "value": {...}}]
)

# ✅ 推荐：使用字段键
await patch_ui_state(
    instance_id="form",
    field_key="email",
    updates={"label": "新标签"}
)
```

### Q: 我应该什么时候使用 `add`，什么时候用 `set`？

**A**: 
- `add`: 在数组**末尾**添加新元素
- `set`: 设置整个数组的值，或修改特定路径的值

```python
# 添加新字段（在末尾）
{"op": "add", "path": "blocks.0.props.fields", "value": new_field}

# 替换整个字段数组
{"op": "set", "path": "blocks.0.props.fields", "value": [field1, field2, field3]}

# 修改特定字段
{"op": "set", "path": "blocks.0.props.fields.1", "value": updated_field}
```

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

### Q: 字段快捷方式和标准 patch 有什么区别？

**A**: 
| 特性 | 字段快捷方式 | 标准 patch |
|------|------------|-----------|
| 代码量 | 少 | 多 |
| 需要知道索引 | ❌ 不需要 | ✅ 需要 |
| 自动刷新 | ✅ 自动 | ❌ 手动 |
| 适用场景 | 更新/删除已有字段 | 所有操作 |

---

## 总结

### 核心工具

| 工具 | 主要用途 | 常用参数 |
|------|----------|----------|
| `get_schema` | 查看当前状态 | `instance_id` |
| `patch_ui_state` | 修改 UI | `instance_id`, `patches` 或 `field_key+updates` |
| `validate_completion` | 验证结果 | `instance_id`, `completion_criteria` |
| `list_instances` | 浏览实例 | 无 |
| `access_instance` | 切换实例 | `instance_id` |

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
- 📖 了解 Patch 规范：[../../PATCH_SPEC.md](../../PATCH_SPEC.md)
- 📖 了解系统架构：[../../MINIMAL_PROTOTYPE.md](../../MINIMAL_PROTOTYPE.md)
