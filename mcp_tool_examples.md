# MCP 工具使用示例

本文档展示了如何使用新添加的 MCP 工具来最小化 UI 操作。

## 1. 删除字段示例

### 场景：从表单中删除"电话"字段

```python
# 使用 remove_field_from_ui 工具
result = await remove_field_from_ui(
    instance_id="form",
    field_key="telephone",
    block_index=0  # 默认为0，第一个表单块
)

# 结果
# {
#     "status": "success",
#     "message": "Field 'telephone' removed successfully",
#     "instance_id": "form"
# }
```

### 等价的 patch_ui_state 调用（更复杂）

```python
# 使用 patch_ui_state 工具（需要更多代码）
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

## 2. 更新字段示例

### 场景：更新表单中的"邮箱"字段

```python
# 使用 update_field_in_ui 工具
result = await update_field_in_ui(
    instance_id="form",
    field_key="email",
    updates={
        "label": "电子邮箱地址",
        "type": "email",
        "description": "请输入您的电子邮箱地址",
        "required": True
    },
    block_index=0  # 默认为0，第一个表单块
)

# 结果
# {
#     "status": "success",
#     "message": "Field 'email' updated successfully",
#     "instance_id": "form"
# }
```

### 等价的 patch_ui_state 调用（更复杂）

```python
# 使用 patch_ui_state 工具（需要更多代码）
result = await patch_ui_state(
    instance_id="form",
    patches=[
        {
            "op": "set",
            "path": "blocks.0.props.fields.1",
            "value": {
                "key": "email",
                "label": "电子邮箱地址",
                "type": "email",
                "description": "请输入您的电子邮箱地址",
                "required": True
            }
        }
    ]
)
```

## 3. 组合使用示例

### 场景：重构表单 - 删除旧字段并添加新字段

```python
# 1. 首先获取当前表单结构
schema = await get_schema(instance_id="form")

# 2. 删除不需要的字段
await remove_field_from_ui(
    instance_id="form",
    field_key="old_field"
)

# 3. 更新现有字段
await update_field_in_ui(
    instance_id="form",
    field_key="name",
    updates={
        "label": "完整姓名",
        "description": "请输入您的完整姓名，包括姓氏和名字"
    }
)

# 4. 添加新字段（使用现有的 add_field_to_ui 工具或 patch_ui_state）
await patch_ui_state(
    instance_id="form",
    patches=[
        {
            "op": "add",
            "path": "blocks.0.props.fields",
            "value": {
                "key": "phone",
                "label": "手机号码",
                "type": "text",
                "description": "请输入您的手机号码",
                "required": True
            }
        }
    ]
)
```

## 4. 实际工作流示例

### 场景：用户注册表单优化

```python
# 1. 获取当前表单结构
current_schema = await get_schema(instance_id="registration_form")

# 2. 删除冗余字段
redundant_fields = ["fax", "middle_name", "mailing_address"]
for field_key in redundant_fields:
    result = await remove_field_from_ui(
        instance_id="registration_form",
        field_key=field_key
    )
    if result.get("status") == "error":
        print(f"Failed to remove field {field_key}: {result.get('error')}")

# 3. 更新现有字段以提高可访问性
field_updates = {
    "email": {
        "label": "电子邮箱",
        "type": "email",
        "description": "我们将使用此邮箱发送确认信息",
        "required": True
    },
    "password": {
        "label": "密码",
        "type": "password",
        "description": "密码至少包含8个字符，包括字母和数字",
        "required": True
    },
    "terms": {
        "label": "我同意服务条款和隐私政策",
        "type": "checkbox",
        "required": True
    }
}

for field_key, updates in field_updates.items():
    result = await update_field_in_ui(
        instance_id="registration_form",
        field_key=field_key,
        updates=updates
    )
    if result.get("status") == "error":
        print(f"Failed to update field {field_key}: {result.get('error')}")

# 4. 添加新的字段
await patch_ui_state(
    instance_id="registration_form",
    patches=[
        {
            "op": "add",
            "path": "blocks.0.props.fields",
            "value": {
                "key": "newsletter",
                "label": "订阅新闻通讯",
                "type": "checkbox",
                "description": "接收产品更新和优惠信息"
            }
        }
    ]
)

# 5. 验证更新后的表单
validation_result = await validate_completion(
    instance_id="registration_form",
    intent="创建一个优化的用户注册表单，包含必要字段和良好的用户体验",
    completion_criteria=[
        {
            "type": "field_exists",
            "path": "state.params.email",
            "description": "邮箱字段存在"
        },
        {
            "type": "field_exists",
            "path": "state.params.password",
            "description": "密码字段存在"
        },
        {
            "type": "field_exists",
            "path": "state.params.newsletter",
            "description": "新闻订阅字段存在"
        },
        {
            "type": "custom",
            "condition": "has_action:submit",
            "description": "提交按钮存在"
        }
    ]
)

print(f"表单验证结果: {validation_result}")
```

## 5. 错误处理示例

```python
# 删除字段时的错误处理
result = await remove_field_from_ui(
    instance_id="form",
    field_key="nonexistent_field"
)

if result.get("status") == "error":
    error_message = result.get("error")
    if "not found" in error_message:
        print("字段不存在，无需删除")
    elif "not a form block" in error_message:
        print("目标块不是表单块")
    else:
        print(f"删除字段时出错: {error_message}")

# 更新字段时的错误处理
result = await update_field_in_ui(
    instance_id="form",
    field_key="email",
    updates={"invalid_property": "value"}  # 无效属性
)

if result.get("status") == "error":
    print(f"更新字段时出错: {result.get('error')}")
```

## 优势总结

1. **简化操作**：使用 `remove_field_from_ui` 和 `update_field_in_ui` 工具，无需手动构建复杂的补丁结构
2. **减少错误**：工具内部处理了路径构建、索引计算等细节，减少了出错可能性
3. **代码清晰**：意图更加明确，代码更易读和维护
4. **一致性**：所有工具使用相同的错误处理和响应格式
5. **组合使用**：可以与现有的 `patch_ui_state` 和其他工具无缝组合使用
