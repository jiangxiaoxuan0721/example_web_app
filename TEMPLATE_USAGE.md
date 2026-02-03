# 模板语法使用指南

## 概述

系统现在支持在字段配置和 HTML 内容中使用模板变量，格式为 `${path}`，例如 `${state.runtime.timestamp}`。

## 支持的变量路径

### 1. `state.params.*` - 字段参数值
```
${state.params.userId}
${state.params.userName}
${state.params.statusText}
```

### 2. `state.runtime.*` - 运行时数据
```
${state.runtime.timestamp}
${state.runtime.message}
${state.runtime.count}
```

### 3. `params.*` - 参数快捷访问（等同于 state.params.*）
```
${params.userId}
${params.userName}
```

### 4. `runtime.*` - 运行时快捷访问（等同于 state.runtime.*）
```
${runtime.timestamp}
${runtime.message}
```

### 5. `meta.*` - 元数据信息
```
${meta.pageKey}
${meta.status}
```

### 6. 选项框标签获取 - 新功能！

对于 `select`、`radio`、`multiselect` 类型的字段，可以使用 `.label` 后缀获取选中项的标签文本：

```
${state.params.status.label}          # 获取选中状态的标签（如 "活跃"）
${state.params.status}                 # 获取选中状态的值（如 "active"）
${state.params.categories.label}       # 多选框会返回逗号分隔的标签（如 "科技, 生活"）
${state.params.categories}              # 多选框返回值的数组（如 ["tech", "life"]）
```

## 使用场景

### 1. HTML 内容中显示动态值

```json
{
  "type": "html",
  "key": "message",
  "value": "<p>消息已更新！时间戳: ${state.runtime.timestamp}</p>"
}
```

### 2. 字段标签使用模板

```json
{
  "type": "text",
  "key": "userName",
  "label": "用户: ${state.params.userName}",
  "value": "张三"
}
```

### 3. 字段描述使用模板

```json
{
  "type": "number",
  "key": "speed",
  "label": "速度",
  "description": "当前速度: ${state.params.speed} km/h",
  "value": 100
}
```

### 4. 多个模板变量组合

```json
{
  "type": "html",
  "key": "statusMessage",
  "value": "<div>用户 <strong>${state.params.userName}</strong> 于 ${state.runtime.timestamp} 更新了状态: ${state.params.statusText}</div>"
}
```

### 5. 选项框标签显示 - 新功能！

对于 select、radio、multiselect 类型的字段，可以显示选中的标签文本而不是值：

**Select 示例：**

```json
{
  "type": "select",
  "key": "status",
  "label": "状态",
  "options": [
    {"label": "活跃", "value": "active"},
    {"label": "非活跃", "value": "inactive"},
    {"label": "待审核", "value": "pending"}
  ]
}
```

在 HTML 中显示选中的标签：

```json
{
  "type": "html",
  "key": "statusDisplay",
  "value": "<p>当前状态: <strong>${state.params.status.label}</strong></p>"
}
```

用户选择 "active" 时，显示：
```
当前状态: 活跃
```

**MultiSelect 示例：**

```json
{
  "type": "multiselect",
  "key": "categories",
  "label": "分类",
  "options": [
    {"label": "科技", "value": "tech"},
    {"label": "生活", "value": "life"},
    {"label": "娱乐", "value": "entertainment"}
  ]
}
```

在 HTML 中显示选中的多个标签：

```json
{
  "type": "html",
  "key": "categoriesDisplay",
  "value": "<p>已选分类: ${state.params.categories.label}</p>"
}
```

用户选择 ["tech", "life"] 时，显示：
```
已选分类: 科技, 生活
```

**Radio 示例：**

```json
{
  "type": "radio",
  "key": "priority",
  "label": "优先级",
  "options": [
    {"label": "高", "value": "high"},
    {"label": "中", "value": "medium"},
    {"label": "低", "value": "low"}
  ]
}
```

在 HTML 中显示选中的优先级：

```json
{
  "type": "html",
  "key": "priorityDisplay",
  "value": "<p>优先级设置: ${state.params.priority.label} (${state.params.priority})</p>"
}
```

用户选择 "high" 时，显示：
```
优先级设置: 高 (high)
```

## 注意事项

1. **路径区分大小写**：`${state.params.userId}` 和 `${state.params.USERID}` 是不同的

2. **嵌套路径**：支持多层嵌套，如 `${state.params.user.address.city}`

3. **默认值**：如果引用的路径不存在，会保留原始模板字符串

4. **数组类型**：如果值是数组，会自动转换为逗号分隔的字符串

5. **性能优化**：模板解析在组件渲染时进行，使用了 React 的 useMemo 进行优化

6. **选项框标签**：
   - `.label` 后缀仅适用于 select、radio、multiselect 类型的字段
   - 标签存储在客户端内存中，页面刷新后会丢失
   - 对于 multiselect，`.label` 会返回所有选中标签的逗号分隔字符串
   - 如果选项配置中的 label 不存在，会返回原始值

## 示例

### 示例 1：带时间戳的消息

```python
# 后端生成 schema
schema = UISchema(
    meta=MetaInfo(pageKey="demo", step=StepInfo(current=1, total=1)),
    state=StateInfo(
        params={"userName": "张三"},
        runtime={"timestamp": "2026-01-23 14:30:00", "message": "操作成功"}
    ),
    blocks=[
        Block(
            id="block1",
            type="card",
            props=BlockProps(
                fields=[
                    FieldConfig(
                        type="html",
                        key="statusHtml",
                        label="状态信息",
                        value="<p>用户 <strong>${state.params.userName}</strong> 于 ${state.runtime.timestamp} 完成了操作</p><p>${state.runtime.message}</p>"
                    )
                ]
            )
        )
    ]
)
```

### 示例 2：动态字段标签

```python
schema = UISchema(
    state=StateInfo(
        params={"city": "北京"},
        runtime={"temperature": 25, "humidity": 60}
    ),
    blocks=[
        Block(
            id="weather",
            type="card",
            props=BlockProps(
                fields=[
                    FieldConfig(
                        type="number",
                        key="temperature",
                        label=f"当前温度 (${state.runtime.temperature}°C)",
                        value=25
                    ),
                    FieldConfig(
                        type="number",
                        key="humidity",
                        label=f"相对湿度 (${state.runtime.humidity}%)",
                        value=60
                    )
                ]
            )
        )
    ]
)
```

## 高级用法

### 使用额外上下文

某些组件支持传入额外的上下文变量，可以用于模板渲染：

```typescript
import { renderTemplate } from './utils/template';

const result = renderTemplate(
  "Hello ${extra.name}",
  schema,
  { name: "World" } // 额外上下文
);
```

## 错误处理

- 如果模板语法错误（如不匹配的 `${}`），会保留原始字符串
- 如果引用的路径不存在，会保留原始占位符
- 如果值为 `null` 或 `undefined`，会保留原始占位符
