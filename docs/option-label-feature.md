# 选项框标签模板功能说明

## 功能概述

现在支持在模板表达式中从选项框（select、radio、multiselect）中获取选中值的标签文本。

## 语法格式

```typescript
${state.params.fieldKey}      // 获取选中的值（如 "active"）
${state.params.fieldKey.label} // 获取选中的标签（如 "活跃"）
```

## 使用示例

### 1. Select 下拉框

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

用户选择 "active" 后：

```html
<!-- 显示值 -->
<div>${state.params.status}</div>
<!-- 输出: active -->

<!-- 显示标签 -->
<div>${state.params.status.label}</div>
<!-- 输出: 活跃 -->
```

### 2. Radio 单选框

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

用户选择 "high" 后：

```html
<div>优先级: ${state.params.priority.label} (${state.params.priority})</div>
<!-- 输出: 优先级: 高 (high) -->
```

### 3. MultiSelect 多选框

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

用户选择 ["tech", "life"] 后：

```html
<!-- 显示值数组 -->
<div>${state.params.categories}</div>
<!-- 输出: tech,life -->

<!-- 显示标签字符串 -->
<div>${state.params.categories.label}</div>
<!-- 输出: 科技, 生活 -->
```

## 演示实例

访问 `http://localhost:5173?instanceId=option_label_demo` 查看完整的演示示例。

这个演示包含：
- 三种选项框类型（select、radio、multiselect）
- 实时显示选中的值和标签
- 综合信息展示
- 功能说明

## 实现细节

### 1. 标签存储

当用户选择选项时，标签会自动存储到 `window.__optionLabels__` 全局对象中：

```typescript
window.__optionLabels__ = {
  status: "活跃",
  priority: "高",
  categories: "科技, 生活"
}
```

### 2. 模板解析

模板引擎会检测 `.label` 后缀，并从全局存储中查找对应的标签：

```typescript
// 检测 .label 后缀
if (trimmed.endsWith('.label')) {
  const baseExpression = trimmed.slice(0, -6);
  const baseValue = getNestedValue(context, baseExpression, match);
  
  // 从全局存储中查找标签
  const parts = baseExpression.split('.');
  const fieldKey = parts[parts.length - 1];
  const label = window.__optionLabels__[fieldKey];
  
  return label || baseValue;
}
```

### 3. 工具函数

提供了两个工具函数用于处理标签：

```typescript
// 获取单个标签
getOptionLabel(value: any, options?: Array<{ label: string; value: string }>): string

// 获取多个标签
getOptionLabels(values: any[], options?: Array<{ label: string; value: string }>): string[]
```

## 限制

1. **客户端存储**：标签存储在客户端内存中，页面刷新后会丢失
2. **仅限选项框**：`.label` 后缀仅适用于 select、radio、multiselect 类型
3. **动态更新**：只有通过 UI 选择才会更新标签，直接设置值不会更新

## 最佳实践

1. **同时显示值和标签**：

```html
<div>
  ${state.params.status.label} (${state.params.status})
</div>
<!-- 输出: 活跃 (active) -->
```

2. **使用条件判断**：

```html
<div class="${state.params.status === 'active' ? 'success' : 'warning'}">
  ${state.params.status.label}
</div>
```

3. **组合多个字段**：

```html
<div>
  <p>用户: ${state.params.userName}</p>
  <p>状态: ${state.params.status.label}</p>
  <p>优先级: ${state.params.priority.label}</p>
</div>
```

## 故障排除

**问题：`.label` 返回 undefined 或原值**

可能原因：
1. 字段不是 select/radio/multiselect 类型
2. 用户尚未选择任何选项
3. 页面刷新导致标签丢失

**解决方案**：
- 确保字段类型正确
- 使用条件判断处理未选择状态
- 在组件加载时设置默认值

```html
<div>
  ${state.params.status.label || '请选择状态'}
</div>
```

## 相关文档

- [TEMPLATE_USAGE.md](./TEMPLATE_USAGE.md) - 完整的模板语法指南
- [README.md](./README.md) - 项目概览
