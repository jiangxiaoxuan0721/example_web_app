# 字段类型参考

本文档详细说明了系统支持的 19 种字段类型。

## 字段类型概览

| 类型 | 分类 | 用途 | 可编辑 |
|------|------|------|--------|
| text | 输入 | 单行文本 | ✓ |
| number | 输入 | 数字输入 | ✓ |
| textarea | 输入 | 多行文本 | ✓ |
| checkbox | 输入 | 复选框 | ✓ |
| json | 输入 | JSON 编辑器 | ✓ |
| select | 选择 | 下拉选择 | ✓ |
| radio | 选择 | 单选按钮 | ✓ |
| multiselect | 选择 | 多选框 | ✓ |
| date | 输入 | 日期选择 | ✓ |
| datetime | 输入 | 日期时间选择 | ✓ |
| file | 输入 | 文件上传 | ✓ |
| html | 显示 | HTML 内容 | ✗ |
| image | 显示 | 图片显示 | ✗ |
| tag | 显示 | 标签显示 | ✗ |
| progress | 显示 | 进度条 | ✗ |
| badge | 显示 | 徽章通知 | ✗ |
| table | 显示 | 数据表格 | ✓ (部分) |
| modal | 显示 | 模态框 | - |
| component | 显示 | 嵌入渲染 | - |

---

## 通用字段属性

所有字段类型都支持以下通用属性：

```json
{
  "key": "field_key",          // 必需，字段唯一标识
  "type": "field_type",        // 必需，字段类型
  "label": "字段标签",         // 必需，显示标签
  "value": "...",              // 可选，字段值
  "description": "描述文字",   // 可选，字段描述
  "editable": true,            // 可选，是否可编辑，默认 true
  "required": false,          // 可选，是否必填，默认 false
  "disabled": false,          // 可选，是否禁用，默认 false
  "placeholder": "占位符",     // 可选，占位符文本
  "hidden": false             // 可选，是否隐藏
}
```

---

## 输入类型

### 1. text

单行文本输入。

**基本示例**：

```json
{
  "key": "username",
  "type": "text",
  "label": "用户名",
  "placeholder": "请输入用户名",
  "required": true
}
```

**使用模板**：

```json
{
  "key": "username",
  "type": "text",
  "label": "用户名",
  "value": "${state.params.username}"
}
```

**常用场景**：
- 用户名
- 邮箱
- 姓名
- 短文本

---

### 2. number

数字输入。

**基本示例**：

```json
{
  "key": "age",
  "type": "number",
  "label": "年龄",
  "value": 0,
  "min": 0,
  "max": 150,
  "step": 1
}
```

**使用模板**：

```json
{
  "key": "count",
  "type": "number",
  "label": "计数",
  "value": "${state.params.count}",
  "disabled": true
}
```

**额外属性**：
- `min`: 最小值
- `max`: 最大值
- `step`: 步长，默认 1

**常用场景**：
- 年龄
- 数量
- 计数
- 评分

---

### 3. textarea

多行文本输入。

**基本示例**：

```json
{
  "key": "description",
  "type": "textarea",
  "label": "描述",
  "placeholder": "请输入详细描述",
  "rows": 4
}
```

**使用模板**：

```json
{
  "key": "bio",
  "type": "textarea",
  "label": "个人简介",
  "value": "${state.params.bio}",
  "disabled": true
}
```

**额外属性**：
- `rows`: 显示行数，默认 4
- `minLength`: 最小字符数
- `maxLength`: 最大字符数

**常用场景**：
- 描述
- 备注
- 简介说明
- 代码片段

---

### 4. checkbox

复选框。

**基本示例**：

```json
{
  "key": "agree",
  "type": "checkbox",
  "label": "我同意服务条款",
  "value": false,
  "required": true
}
```

**使用模板**：

```json
{
  "key": "newsletter",
  "type": "checkbox",
  "label": "订阅新闻邮件",
  "value": "${state.params.newsletter}"
}
```

**常用场景**：
- 同意条款
- 启用功能
- 订阅选项
- 开关状态

---

### 5. json

JSON 编辑器。

**基本示例**：

```json
{
  "key": "config",
  "type": "json",
  "label": "配置",
  "value": "{\"theme\": \"dark\", \"lang\": \"zh\"}"
}
```

**使用模板**：

```json
{
  "key": "user_data",
  "type": "json",
  "label": "用户数据",
  "value": "${state.params.user_data}",
  "disabled": true
}
```

**常用场景**：
- 配置文件
- API 响应
- 数据结构
- 调试信息

---

### 6. date

日期选择。

**基本示例**：

```json
{
  "key": "birthdate",
  "type": "date",
  "label": "出生日期",
  "value": "1990-01-01"
}
```

**使用模板**：

```json
{
  "key": "start_date",
  "type": "date",
  "label": "开始日期",
  "value": "${state.params.start_date}"
}
```

**格式**：`YYYY-MM-DD`

**常用场景**：
- 出生日期
- 日期范围
- 日期选择

---

### 7. datetime

日期时间选择。

**基本示例**：

```json
{
  "key": "deadline",
  "type": "datetime",
  "label": "截止时间",
  "value": "2026-02-09T15:30:00"
}
```

**使用模板**：

```json
{
  "key": "created_at",
  "type": "datetime",
  "label": "创建时间",
  "value": "${state.params.created_at}",
  "disabled": true
}
```

**格式**：ISO 8601 (`YYYY-MM-DDTHH:mm:ss`)

**常用场景**：
- 时间戳
- 截止时间
- 日程安排

---

### 8. file

文件上传。

**基本示例**：

```json
{
  "key": "avatar",
  "type": "file",
  "label": "头像上传",
  "accept": "image/*",
  "multiple": false
}
```

**额外属性**：
- `accept`: 接受的文件类型（MIME 类型）
- `multiple`: 是否多选，默认 false

**常用场景**：
- 头像上传
- 文档上传
- 图片选择
- 数据导入

---

## 选择类型

### 9. select

下拉选择。

**基本示例**：

```json
{
  "key": "status",
  "type": "select",
  "label": "状态",
  "value": "active",
  "options": [
    {"label": "活跃", "value": "active"},
    {"label": "非活跃", "value": "inactive"},
    {"label": "待审核", "value": "pending"}
  ]
}
```

**获取标签**：

```json
{
  "key": "status",
  "type": "html",
  "value": "<p>状态：${state.params.status.label} (${state.params.status})</p>"
}
```

**额外属性**：
- `multiple`: 是否多选，默认 false

**常用场景**：
- 状态选择
- 分类选择
- 单项配置
- 下拉菜单

---

### 10. radio

单选按钮。

**基本示例**：

```json
{
  "key": "priority",
  "type": "radio",
  "label": "优先级",
  "value": "medium",
  "options": [
    {"label": "高", "value": "high"},
    {"label": "中", "value": "medium"},
    {"label": "低", "value": "low"}
  ]
}
```

**获取标签**：

```json
{
  "key": "priority",
  "type": "html",
  "value": "<p>优先级：${state.params.priority.label}</p>"
}
```

**常用场景**：
- 优先级
- 性别
- 单项选择
- 选项较少的场景

---

### 11. multiselect

多选框。

**基本示例**：

```json
{
  "key": "categories",
  "type": "multiselect",
  "label": "分类",
  "value": ["tech", "life"],
  "options": [
    {"label": "科技", "value": "tech"},
    {"label": "生活", "value": "life"},
    {"label": "娱乐", "value": "entertainment"}
  ]
}
```

**获取标签**：

```json
{
  "key": "categories",
  "type": "html",
  "value": "<p>分类：${state.params.categories.label}</p>"
}
```

**常用场景**：
- 标签选择
- 多分类
- 兴趣爱好
- 权限选择

---

## 显示类型

### 12. html

HTML 内容显示。

**基本示例**：

```json
{
  "key": "welcome",
  "type": "html",
  "value": "<h1>欢迎！</h1><p>这是一个示例。</p>"
}
```

**使用模板**：

```json
{
  "key": "message",
  "type": "html",
  "value": "<p>你好，${state.params.username}！</p>"
}
```

**支持的 HTML**：
- 文本标签：h1-h6, p, span, div
- 列表：ul, ol, li
- 格式：strong, em, code, pre
- 其他：a, img, br, hr

**常用场景**：
- 欢迎信息
- 说明文字
- 富文本
- Markdown 渲染结果

---

### 13. image

图片显示。

**基本示例**：

```json
{
  "key": "avatar",
  "type": "image",
  "label": "头像",
  "value": "https://example.com/avatar.jpg"
}
```

**完整配置**：

```json
{
  "key": "cover",
  "type": "image",
  "label": "封面图片",
  "value": "https://example.com/cover.jpg",
  "showFullscreen": true,
  "showDownload": true,
  "imageHeight": "300px",
  "imageFit": "cover",
  "lazy": true,
  "subtitle": "封面图片",
  "fallback": "加载失败"
}
```

**额外属性**：
- `showFullscreen`: 显示全屏按钮，默认 true
- `showDownload`: 显示下载按钮，默认 true
- `imageHeight`: 图片高度，默认 "auto"
- `imageFit`: 适应方式，可选 "contain" | "cover" | "fill"
- `lazy`: 懒加载，默认 false
- `subtitle`: 子标题
- `fallback`: 加载失败时的回退内容

**常用场景**：
- 头像
- 封面图片
- 截图
- 图表

---

### 14. tag

标签显示。

**基本示例**：

```json
{
  "key": "status",
  "type": "tag",
  "label": "状态",
  "value": "active",
  "options": [
    {"label": "活跃", "value": "active"},
    {"label": "非活跃", "value": "inactive"}
  ]
}
```

**颜色设置**：

```json
{
  "key": "priority",
  "type": "tag",
  "label": "优先级",
  "value": "high",
  "options": [
    {"label": "高", "value": "high", "color": "red"},
    {"label": "中", "value": "medium", "color": "orange"},
    {"label": "低", "value": "low", "color": "green"}
  ]
}
```

**常用场景**：
- 状态标签
- 优先级
- 分类标识
- 版本标签

---

### 15. progress

进度条。

**基本示例**：

```json
{
  "key": "progress",
  "type": "progress",
  "label": "进度",
  "value": 50
}
```

**带状态文本**：

```json
{
  "key": "upload_progress",
  "type": "progress",
  "label": "上传进度",
  "value": "${state.params.upload_progress}",
  "showLabel": true
}
```

**额外属性**：
- `showLabel`: 显示百分比文本，默认 false
- `color`: 进度条颜色（CSS 颜色值）

**常用场景**：
- 上传进度
- 任务进度
- 完成度
- 加载状态

---

### 16. badge

徽章通知。

**基本示例**：

```json
{
  "key": "notification_count",
  "type": "badge",
  "label": "通知",
  "value": 5
}
```

**颜色设置**：

```json
{
  "key": "alert_count",
  "type": "badge",
  "label": "告警",
  "value": "${state.params.alert_count}",
  "color": "red"
}
```

**额外属性**：
- `color`: 徽章颜色（CSS 颜色值）

**常用场景**：
- 未读消息
- 告警数量
- 提醒计数
- 通知标记

---

### 17. table

数据表格。

**基本示例**：

```json
{
  "key": "users",
  "type": "table",
  "label": "用户列表",
  "value": [
    {"id": 1, "name": "张三", "email": "zhangsan@example.com", "status": "active"},
    {"id": 2, "name": "李四", "email": "lisi@example.com", "status": "inactive"}
  ],
  "columns": [
    {"key": "id", "title": "ID", "width": "80px"},
    {"key": "name", "title": "姓名", "width": "150px"},
    {"key": "email", "title": "邮箱", "width": "250px"},
    {"key": "status", "title": "状态", "width": "100px"}
  ]
}
```

**可编辑表格**：

```json
{
  "key": "config",
  "type": "table",
  "label": "配置",
  "tableEditable": true,
  "showPagination": false,
  "columns": [
    {"key": "param", "title": "参数名", "width": "200px"},
    {"key": "value", "title": "参数值", "width": "150px", "editable": true},
    {"key": "description", "title": "说明", "width": "300px"}
  ],
  "value": [
    {"param": "iterations", "value": "10", "description": "迭代次数"},
    {"param": "tolerance", "value": "1e-6", "description": "收敛容差"}
  ]
}
```

**额外属性**：
- `tableEditable`: 表格是否可编辑
- `showPagination`: 显示分页，默认 true
- `pageSize`: 每页行数，默认 10

**常用场景**：
- 数据列表
- 配置表格
- 结果展示
- 报告表格

---

### 18. modal

模态框。

**基本示例**：

```json
{
  "key": "modal_trigger",
  "type": "modal",
  "label": "触发按钮",
  "value": "打开模态框",
  "props": {
    "title": "确认操作",
    "content": "确定要执行此操作吗？",
    "confirmText": "确定",
    "cancelText": "取消"
  }
}
```

**常用场景**：
- 确认对话框
- 详细信息
- 表单弹窗
- 操作提示

---

### 19. component

嵌入渲染（跨实例引用）。

**基本示例**：

```json
{
  "key": "embedded_component",
  "type": "component",
  "label": "嵌入组件",
  "value": {
    "instance_name": "other_instance",
    "block_id": "target_block"
  }
}
```

**常用场景**：
- 组件复用
- 跨实例引用
- 模块化设计
- 组合视图

---

## 模板使用

所有字段都可以使用模板语法：

```json
{
  "key": "display_field",
  "type": "text",
  "value": "${state.params.dynamic_value}"
}
```

**支持的路径格式**：

```javascript
${state.params.xxx}        // 参数值
${state.runtime.xxx}       // 运行时值
${params.xxx}              // 参数值（简写）
${runtime.xxx}             // 运行时值（简写）
${state.params.user.name}  // 嵌套对象
```

---

## 选项标签

对于 `select`、`radio`、`multiselect` 类型，可以获取选中值的标签：

```json
{
  "key": "status",
  "type": "html",
  "value": "<p>状态：${state.params.status.label} (${state.params.status})</p>"
}
```

详见 [选项标签功能](./option-label-feature.md)。

---

## 最佳实践

### 1. 字段命名

- 使用小写字母和下划线：`user_name`, `email_address`
- 名称简洁且描述性强
- 避免使用保留字

### 2. 标签设置

- 标签简洁明了
- 使用用户友好的语言
- 必要时添加描述

### 3. 默认值

- 为必填字段设置合理的默认值
- 使用模板引用动态值
- 禁用字段提供明确的占位符

### 4. 验证规则

- 合理使用 `required` 属性
- 数字类型设置 `min` 和 `max`
- 文本类型设置 `minLength` 和 `maxLength`

### 5. 显示优化

- 使用 `disabled` 属性表示只读状态
- 使用 `description` 提供额外说明
- 合理使用 `placeholder` 引导输入

## 相关文档

- [Schema 详解](./schema-guide.md) - Schema 结构详细说明
- [布局系统](./layout-guide.md) - 布局类型使用指南
- [模板语法](./template-syntax.md) - 动态内容渲染
- [选项标签功能](./option-label-feature.md) - 选项标签详细说明
