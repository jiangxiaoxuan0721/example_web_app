# 模板语法

本文档详细说明了模板表达式的语法和使用方法。

## 概述

模板表达式允许在字段值、HTML 内容、标题等地方动态引用和显示数据。

## 基本语法

模板表达式使用 `${path}` 格式：

```javascript
${state.params.xxx}        // 参数值
${state.runtime.xxx}       // 运行时值
${params.xxx}              // 参数值（简写）
${runtime.xxx}             // 运行时值（简写）
${page_key}               // 页面标识符
```

## 支持的路径

### 1. state.params

用户参数，存储用户输入的值。

```json
{
  "state": {
    "params": {
      "username": "alice",
      "email": "alice@example.com",
      "count": 10,
      "user": {
        "name": "Alice",
        "age": 30
      }
    }
  }
}
```

**引用方式**：

```html
<!-- 简单值 -->
<p>${state.params.username}</p>

<!-- 嵌套对象 -->
<p>${state.params.user.name}</p>

<!-- 数字 -->
<p>计数：${state.params.count}</p>
```

### 2. state.runtime

运行时数据，自动更新的系统数据。

```json
{
  "state": {
    "runtime": {
      "timestamp": "2026-02-09 15:30:45",
      "temp_rowData": {}
    }
  }
}
```

**引用方式**：

```html
<!-- 时间戳 -->
<p>当前时间：${state.runtime.timestamp}</p>

<!-- 简写 -->
<p>时间：${runtime.timestamp}</p>
```

**注意**：

如果需要在模板中显示当前时间，需要先通过 patch 设置 `state.runtime.timestamp`：

```json
{
  "key": "last_updated",
  "type": "text",
  "label": "最后更新",
  "value": "${state.runtime.timestamp}",
  "disabled": true
}
```

在创建或更新操作时设置时间戳：

```json
[
  {"op": "set", "path": "state.runtime.timestamp", "value": "2026-02-09 15:30:45"}
]
```
```

### 3. page_key

页面标识符，直接位于 Schema 顶层。

```json
{
  "page_key": "my_app"
}
```

**引用方式**：

```html
<p>页面标识：${page_key}</p>
```

**注意**：历史文档中可能看到 `${meta.page_key}`，这已不再推荐使用，请改用 `${page_key}`。

## 使用场景

### 1. 字段值

```json
{
  "key": "welcome_message",
  "type": "text",
  "label": "欢迎消息",
  "value": "${state.params.welcome_message}"
}
```

### 2. HTML 内容

```json
{
  "key": "user_info",
  "type": "html",
  "value": "<h1>欢迎，${state.params.username}！</h1><p>邮箱：${state.params.email}</p>"
}
```

### 3. 标签（Tabs）标题

```json
{
  "id": "user_tab",
  "layout": "form",
  "title": "用户：${state.params.username}",
  "props": {
    "fields": [...]
  }
}
```

### 4. 表格列

```json
{
  "key": "users",
  "type": "table",
  "columns": [
    {"key": "id", "title": "ID"},
    {"key": "name", "title": "姓名"},
    {"key": "email", "title": "邮箱"},
    {"key": "status", "title": "状态：${state.params.filter_status}"}
  ],
  "value": [...]
}
```

### 5. 操作按钮文本

```json
{
  "id": "submit",
  "label": "提交 (${state.params.item_count})",
  "action_type": "apply_patch",
  "patches": [...]
}
```

## 特殊功能

### 1. 时间戳引用

模板可以引用 `state.runtime.timestamp` 来显示时间戳，但需要通过 patch 手动设置：

```json
{
  "key": "updated_time",
  "type": "text",
  "label": "更新时间",
  "value": "${state.runtime.timestamp}"
}
```

### 2. 选项标签获取

对于 `select`、`radio`、`multiselect` 类型，可以获取选中值的标签：

```json
{
  "key": "status",
  "type": "select",
  "label": "状态",
  "value": "active",
  "options": [
    {"label": "活跃", "value": "active"},
    {"label": "非活跃", "value": "inactive"}
  ]
}
```

**显示标签**：

```json
{
  "key": "status_display",
  "type": "html",
  "value": "<p>状态：${state.params.status.label} (${state.params.status})</p>"
}
```

输出：`状态：活跃 (active)`

详见 [选项标签功能](./option-label-feature.md)。

### 3. 对象值自动转换

当值是对象时，系统会自动转换为 JSON 字符串：

```json
{
  "state": {
    "params": {
      "config": {
        "theme": "dark",
        "lang": "zh"
      }
    }
  }
}
```

**引用**：

```json
{
  "key": "config_display",
  "type": "html",
  "value": "<pre>${state.params.config}</pre>"
}
```

输出：`{"theme":"dark","lang":"zh"}`

避免显示 `[object Object]`。

## 高级用法

### 1. 嵌套对象访问

```javascript
${state.params.user.profile.name}     // 三层嵌套
${state.params.settings.theme.mode}  // 深度访问
```

### 2. 动态字段名

使用 `rowData` 访问表格行数据：

```html
<p>${state.params.temp_rowData.name}</p>
<p>${state.params.temp_rowData.email}</p>
```

### 3. 组合多个值

```html
<p>${state.params.first_name} ${state.params.last_name}</p>
<p>(${state.params.username})</p>
```

### 4. 条件渲染

虽然模板本身不支持条件，但可以通过状态控制：

```json
{
  "key": "message",
  "type": "html",
  "value": "${state.params.success_message}"
}
```

在 Action 中切换消息：

```json
{
  "handler_type": "set",
  "patches": {
    "state.params.success_message": "<p class='success'>操作成功！</p>",
    "state.params.error_message": "<p class='error'>操作失败！</p>"
  }
}
```

## 完整示例

### 示例 1：用户信息展示

```json
{
  "blocks": [
    {
      "id": "user_profile",
      "layout": "form",
      "title": "用户资料",
      "props": {
        "fields": [
          {
            "key": "welcome",
            "type": "html",
            "value": "<h1>欢迎，${state.params.user.name}！</h1><p>上次登录：${state.runtime.timestamp}</p>"
          },
          {
            "key": "name",
            "type": "text",
            "label": "姓名",
            "value": "${state.params.user.name}",
            "disabled": true
          },
          {
            "key": "email",
            "type": "text",
            "label": "邮箱",
            "value": "${state.params.user.email}",
            "disabled": true
          },
          {
            "key": "status",
            "type": "tag",
            "label": "状态",
            "value": "${state.params.user.status}",
            "options": [
              {"label": "活跃", "value": "active"},
              {"label": "非活跃", "value": "inactive"}
            ]
          }
        ]
      }
    }
  ]
}
```

### 示例 2：动态表格

```json
{
  "blocks": [
    {
      "id": "data_table",
      "layout": "form",
      "title": "数据列表 (${state.params.data_count})",
      "props": {
        "fields": [
          {
            "key": "filter",
            "type": "select",
            "label": "筛选",
            "value": "all",
            "options": [
              {"label": "全部", "value": "all"},
              {"label": "活跃", "value": "active"},
              {"label": "非活跃", "value": "inactive"}
            ]
          },
          {
            "key": "table",
            "type": "table",
            "label": "数据",
            "value": "${state.params.table_data}",
            "columns": [
              {"key": "id", "title": "ID"},
              {"key": "name", "title": "姓名"},
              {"key": "status", "title": "状态"},
              {"key": "updated", "title": "更新时间"}
            ]
          },
          {
            "key": "summary",
            "type": "html",
            "value": "<p>当前显示：${state.params.data_count} 条记录</p><p>筛选：${state.params.filter.label}</p>"
          }
        ]
      }
    }
  ]
}
```

### 示例 3：动态标题

```json
{
  "layout": {
    "type": "tabs"
  },
  "blocks": [
    {
      "id": "step1",
      "layout": "form",
      "title": "步骤1：${state.params.step1_status}",
      "props": {
        "fields": [...]
      }
    },
    {
      "id": "step2",
      "layout": "form",
      "title": "步骤2：${state.params.step2_status}",
      "props": {
        "fields": [...]
      }
    }
  ]
}
```

## 性能优化

### 1. 避免过度嵌套

**不推荐**：
```javascript
${state.params.a.b.c.d.e.f.value}
```

**推荐**：扁平化状态结构
```javascript
${state.params.value}
```

### 2. 缓存复杂值

对于复杂的计算结果，存储到 state 中：

```json
{
  "handler_type": "set",
  "patches": {
    "state.params.total_price": "${state.params.quantity} * ${state.params.unit_price}"
  }
}
```

然后在模板中使用：
```html
<p>总价：${state.params.total_price}</p>
```

### 3. 按需更新

只更新需要变化的字段，避免全量更新。

## 错误处理

### 1. 路径不存在

当路径不存在时，返回空字符串：

```html
<p>${state.params.nonexistent}</p>
<!-- 输出：(空) -->
```

### 2. 类型不匹配

当值类型不符合预期时，尝试转换：

```javascript
${state.params.count}  // 数字会转换为字符串
${state.params.user}   // 对象会转换为 JSON 字符串
```

### 3. 循环引用

检测循环引用并中断，避免无限递归。

## 最佳实践

### 1. 使用描述性的路径名

```javascript
${state.params.user_email}  // 好
${state.params.x}           // 差
```

### 2. 保持状态扁平

```javascript
${state.params.username}     // 好
${state.params.user.name}   // 可接受
${state.params.data.user.profile.name}  // 差
```

### 3. 合理使用简写

```javascript
${params.username}    // 参数（常用）
${runtime.timestamp} // 运行时数据（常用）
${page_key}         // 页面标识符（常用）
```

### 4. 组合模板和硬编码

```html
<p>当前时间：${state.runtime.timestamp}</p>
<p>版本：v1.0.0</p>
```

### 5. 使用空值检查

```html
<p>${state.params.email || '未填写邮箱'}</p>
```

## 限制

1. **不支持表达式**：模板不支持数学运算、逻辑判断等
2. **不支持函数调用**：不能在模板中调用函数
3. **不支持条件语句**：使用状态控制代替
4. **不支持循环**：使用表格组件代替

## 相关文档

- [Schema 详解](./schema-guide.md) - Schema 结构和 state 管理
- [状态管理](./state-management.md) - 状态管理最佳实践
- [选项标签功能](./option-label-feature.md) - 选项标签详细说明
- [字段类型参考](./field-types.md) - 所有字段类型详解
