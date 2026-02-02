# MCP 字段类型文档

本文档描述了 MCP 工具支持的所有字段类型及其用法。

## 目录

- [基础字段类型](#基础字段类型)
  - [text](#text-单行文本输入)
  - [number](#number-数字输入)
  - [textarea](#textarea-多行文本框)
  - [checkbox](#checkbox-复选框)
- [选择字段类型](#选择字段类型)
  - [select](#select-下拉选择)
  - [radio](#radio-单选按钮组)
  - [multiselect](#multiselect-多选框组)
- [数据展示类型](#数据展示类型)
  - [html](#html-只读HTML内容)
  - [json](#json-编辑器)
  - [image](#image-图片显示)
  - [tag](#tag-标签显示)
  - [progress](#progress-进度条)
  - [badge](#badge-徽章)
  - [table](#table-数据表格)
  - [modal](#modal-模态框)

---

## 基础字段类型

### text - 单行文本输入

单行文本输入框，用于输入简短文本。支持对象值自动转换和模板渲染。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "text"
- `value` (可选): 初始值
- `description` (可选): 占位符文本
- `editable` (可选): 是否可编辑，默认 true

**特殊处理:**
- 如果值为对象，会自动使用 `JSON.stringify` 格式化显示
- 如果值为字符串且包含模板变量（如 `${state.params.xxx}`），会先进行模板渲染
- 模板渲染会自动更新 `state.runtime.timestamp`（如果引用了该变量）

**示例 1: 基础使用**
```json
{
  "op": "set",
  "path": "state.params.username",
  "value": ""
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "用户名",
    "key": "username",
    "type": "text",
    "description": "请输入用户名"
  }
}
```

**示例 2: 带模板渲染和时间戳**
```json
{
  "op": "set",
  "path": "state.params.message",
  "value": "消息已更新！时间戳: ${state.runtime.timestamp}"
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "消息",
    "key": "message",
    "type": "text"
  }
}
```

每次渲染模板时，`state.runtime.timestamp` 会自动更新为当前时间。

**示例 3: 显示对象值**
```json
{
  "op": "set",
  "path": "state.params.user",
  "value": {"name": "张三", "email": "zhang@example.com"}
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "用户信息",
    "key": "user",
    "type": "text",
    "editable": false
  }
}
```

对象会自动格式化为 JSON 字符串显示。

---

### number - 数字输入

数字输入框，用于输入数值。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "number"
- `value` (可选): 初始数值
- `description` (可选): 占位符文本

**示例:**
```json
{
  "op": "set",
  "path": "state.params.age",
  "value": 0
},
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
```

---

### textarea - 多行文本框

多行文本输入框，用于输入长文本内容。支持对象值自动转换和模板渲染。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "textarea"
- `value` (可选): 初始值
- `description` (可选): 占位符文本
- `rows` (可选): 显示行数，默认 4

**特殊处理:**
- 如果值为对象，会自动使用 `JSON.stringify` 格式化显示
- 如果值为字符串且包含模板变量（如 `${state.params.xxx}`），会先进行模板渲染
- 模板渲染会自动更新 `state.runtime.timestamp`（如果引用了该变量）

**示例 1: 基础使用**
```json
{
  "op": "set",
  "path": "state.params.description",
  "value": ""
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "简介",
    "key": "description",
    "type": "textarea",
    "description": "请输入个人简介",
    "rows": 4
  }
}
```

**示例 2: 带模板渲染**
```json
{
  "op": "set",
  "path": "state.params.log",
  "value": "日志记录:\n操作时间: ${state.runtime.timestamp}\n操作内容: ${state.params.action}"
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "操作日志",
    "key": "log",
    "type": "textarea",
    "editable": false
  }
}
```

---

### checkbox - 复选框

布尔值开关，用于二选一的场景。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "checkbox"
- `value` (可选): 初始布尔值，默认 false
- `description` (可选): 辅助说明文本

**示例:**
```json
{
  "op": "set",
  "path": "state.params.agreed",
  "value": false
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "同意服务条款",
    "key": "agreed",
    "type": "checkbox",
    "description": "阅读并同意服务协议"
  }
}
```

---

## 选择字段类型

### select - 下拉选择

下拉选择框，用于从多个选项中选择一个。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "select"
- `value` (可选): 初始值
- `options` (必填): 选项数组，每个选项包含 `label` 和 `value`

**示例:**
```json
{
  "op": "set",
  "path": "state.params.country",
  "value": ""
},
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
```

---

### radio - 单选按钮组

单选按钮组，用于从多个选项中选择一个。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "radio"
- `value` (可选): 初始值
- `options` (必填): 选项数组，每个选项包含 `label` 和 `value`

**示例:**
```json
{
  "op": "set",
  "path": "state.params.gender",
  "value": ""
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "性别",
    "key": "gender",
    "type": "radio",
    "options": [
      {"label": "男", "value": "male"},
      {"label": "女", "value": "female"},
      {"label": "其他", "value": "other"}
    ]
  }
}
```

---

### multiselect - 多选框组

复选框组，用于从多个选项中选择多个值。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "multiselect"
- `value` (可选): 初始值，字符串数组
- `options` (必填): 选项数组，每个选项包含 `label` 和 `value`
- `description` (可选): 辅助说明文本

**示例:**
```json
{
  "op": "set",
  "path": "state.params.skills",
  "value": ["reading", "coding"]
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "技能选择",
    "key": "skills",
    "type": "multiselect",
    "options": [
      {"label": "阅读", "value": "reading"},
      {"label": "编程", "value": "coding"},
      {"label": "写作", "value": "writing"},
      {"label": "设计", "value": "design"}
    ],
    "description": "请选择您掌握的技能"
  }
}
```

---

## 数据展示类型

### html - 只读 HTML 内容

用于渲染 HTML 内容的只读字段。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "html"
- `value` (必填): HTML 内容字符串
- `description` (可选): 辅助说明文本

**示例:**
```json
{
  "op": "set",
  "path": "state.params.content",
  "value": "<h3>标题</h3><p>这是一段HTML内容</p>"
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "内容",
    "key": "content",
    "type": "html"
  }
}
```

---

### json - JSON 编辑器

带验证功能的 JSON 编辑器，支持对象值的自动转换显示。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "json"
- `value` (可选): 初始 JSON 对象或字符串
- `description` (可选): 占位符文本
- `editable` (可选): 是否可编辑，默认 true

**特殊处理:**
- 如果值为对象，会自动使用 `JSON.stringify` 格式化显示
- 如果值为字符串且包含模板变量（如 `${state.params.xxx}`），会先进行模板渲染
- 支持实时 JSON 语法验证

**示例 1: 基础使用**
```json
{
  "op": "set",
  "path": "state.params.config",
  "value": {"theme": "dark", "language": "zh"}
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "配置",
    "key": "config",
    "type": "json"
  }
}
```

**示例 2: 带模板渲染**
```json
{
  "op": "set",
  "path": "state.params.result",
  "value": "结果: ${state.params.message}"
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "结果",
    "key": "result",
    "type": "json"
  }
}
```

模板会在显示时自动渲染为实际值。

---

### image - 图片显示

带控制器的图片显示组件。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "image"
- `value` (必填): 图片 URL 或对象 `{url, title, alt}`
- `showFullscreen` (可选): 是否显示全屏按钮，默认 true
- `showDownload` (可选): 是否显示下载按钮，默认 true
- `imageHeight` (可选): 图片高度，默认 "auto"
- `imageFit` (可选): 图片适配方式 ("contain"|"cover"|"fill")，默认 "contain"
- `lazy` (可选): 启用懒加载
- `fallback` (可选): 加载失败的回退内容
- `subtitle` (可选): 副标题

**示例:**
```json
{
  "op": "set",
  "path": "state.params.avatar",
  "value": "https://example.com/image.jpg"
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "头像",
    "key": "avatar",
    "type": "image",
    "imageFit": "cover",
    "imageHeight": "200px"
  }
}
```

---

### tag - 标签显示

用于显示标签数组，支持动态类型判断和自定义文本映射。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "tag"
- `value` (可选): 标签数组，每个标签可以是字符串或对象 `{label, type}`
  - `type`: 标签类型 ("default"|"success"|"warning"|"error"|"info")
- `renderText` (可选): 自定义文本映射，格式为 "value1:文本1|value2:文本2" 或函数
- `evaluate` (可选): 条件判断表达式，支持布尔值判断

**动态类型判断:**
标签类型根据值自动判断：
- "success", "active", "completed", "done" → 绿色
- "warning", "pending", "inprogress", "wip" → 黄色
- "error", "failed", "danger", "stopped" → 红色
- "info", "processing", "running", "pending" → 蓝色
- 其他 → 灰色

**示例 1: 基础标签**
```json
{
  "op": "set",
  "path": "state.params.tags",
  "value": [
    {"label": "已完成", "type": "success"},
    {"label": "高优先级", "type": "warning"},
    {"label": "审核中", "type": "info"}
  ]
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "任务标签",
    "key": "tags",
    "type": "tag"
  }
}
```

**示例 2: 带自定义文本映射**
```json
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "状态",
    "key": "status",
    "type": "tag",
    "renderText": "true:已完成|false:未完成"
  }
}
```

当 `state.params.status` 为 `true` 时，显示"已完成"标签；为 `false` 时，显示"未完成"标签。

**示例 3: 带条件判断**
```json
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "状态",
    "key": "status",
    "type": "tag",
    "evaluate": "status === 'completed'",
    "renderText": "true:已完成|false:进行中"
  }
}
```

---

### progress - 进度条

显示进度条。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "progress"
- `value` (可选): 进度对象 `{current, total, showLabel}`
  - `current`: 当前进度数值
  - `total`: 总进度数值
  - `showLabel`: 是否显示标签，默认 true

**示例:**
```json
{
  "op": "set",
  "path": "state.params.progress",
  "value": {
    "current": 3,
    "total": 5,
    "showLabel": true
  }
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "任务进度",
    "key": "progress",
    "type": "progress"
  }
}
```

---

### badge - 徽章

显示带徽章的通知。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "badge"
- `value` (可选): 徽章配置对象
  - `count`: 徽章数字
  - `label`: 锚点文本
  - `dot`: 显示圆点而非数字，默认 false
  - `color`: 徽章颜色，默认 "#f5222d"
  - `showZero`: count 为 0 时是否显示，默认 false
  - `max`: 最大显示值，超过显示 "N+"，默认 99

**示例:**
```json
{
  "op": "set",
  "path": "state.params.notification",
  "value": {
    "count": 5,
    "label": "通知",
    "color": "#f5222d"
  }
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "消息通知",
    "key": "notification",
    "type": "badge"
  }
}
```

---

### table - 数据表格

显示结构化数据表格，支持排序、多种单元格渲染类型。

**基本属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "table"
- `columns` (必填): 列配置数组（详见下方列配置）
- `value` (可选): 数据数组，每个对象代表一行
- `rowKey`: 行唯一键字段名，默认 "id"

**表格样式属性:**
- `bordered`: 是否显示边框，默认 true
- `striped`: 是否斑马纹，默认 true
- `hover`: 是否悬停高亮，默认 true
- `showHeader`: 是否显示表头，默认 true
- `compact`: 是否紧凑模式（减少内边距），默认 false
- `maxHeight`: 最大高度（如 "300px"），超出时滚动
- `emptyText`: 空数据提示文本，默认 "暂无数据"

**分页属性:**
- `showPagination`: 是否显示分页控件，默认 false
- `pageSize`: 每页显示行数，默认 10

#### 列配置 (columns)

每列支持以下属性：

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `key` | string | 是 | 数据对象中对应的字段键名 |
| `label` | string | 是 | 列标题 |
| `width` | string | 否 | 列宽度，如 "150px" |
| `align` | string | 否 | 对齐方式: "left"|"center"|"right"，默认 "left" |
| `sortable` | boolean | 否 | 是否可排序，默认 false |
| `editable` | boolean | 否 | 是否可编辑（待实现），默认 false |
| `renderType` | string | 否 | 内置渲染类型: "text"|"tag"|"badge"|"progress"|"image" |

#### 单元格渲染类型 (renderType)

**1. text (默认)** - 普通文本显示

```json
{
  "key": "name",
  "label": "姓名",
  "renderType": "text"
}
```

**2. tag** - 标签显示

标签类型根据值自动判断：
- "success", "active", "completed" -> 绿色
- "warning", "pending" -> 黄色
- "error", "failed", "danger" -> 红色
- "info", "processing" -> 蓝色
- 其他 -> 灰色

```json
{
  "key": "status",
  "label": "状态",
  "align": "center",
  "renderType": "tag"
}
```

**3. badge** - 徽章显示

使用 `badgeColor` 属性自定义徽章颜色：

```json
{
  "key": "priority",
  "label": "优先级",
  "align": "center",
  "renderType": "badge",
  "badgeColor": "#f5222d"
}
```

**4. progress** - 进度条显示

数据字段值应为对象: `{current, total}`

```json
{
  "key": "progress",
  "label": "进度",
  "renderType": "progress"
}
```

数据示例:
```json
{
  "name": "任务1",
  "progress": {"current": 3, "total": 5}
}
```

**5. image** - 图片显示

数据字段值应为图片 URL

```json
{
  "key": "avatar",
  "label": "头像",
  "align": "center",
  "renderType": "image"
}
```

**6. mixed** - 组合多个元素 ⭐ 新增

`mixed` 类型允许在单个单元格中组合多个元素，包括文本、标签、徽章、进度条、图片、按钮等。

通过 `components` 数组配置每个子元素，支持以下属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | string | 元素类型: "text", "tag", "badge", "progress", "image", "button", "spacer" |
| `field` | string | 从 record 中取值的字段名（可选） |
| `text` | string | 静态文本（用于 text 类型） |
| `tagType` | string | 标签类型（用于 tag 类型） |
| `badgeColor` | string | 徽章颜色（用于 badge 类型） |
| `imageSize` | string | 图片尺寸，如 "32px"（用于 image 类型） |
| `imageFit` | string | 图片适配方式（用于 image 类型） |
| `buttonLabel` | string | 按钮文本（用于 button 类型） |
| `buttonStyle` | string | 按钮样式: "primary", "secondary", "danger" |
| `buttonSize` | string | 按钮尺寸: "small", "medium", "large" |
| `actionType` | string | 操作类型（用于 button 类型） |
| `actionId` | string | 关联的 Action ID（用于 button 类型触发事件） |
| `actionData` | any | 操作数据（用于 button 类型） |
| `width` | string | spacer 宽度（用于 spacer 类型） |
| `margin` | string | 元素左边距 |

#### 表格按钮事件处理 ⭐

**重要**: 表格中的按钮必须通过 `actionId` 关联到一个已定义的 Action 配置，点击后会触发对应的事件。

**按钮触发流程:**
1. 用户点击表格中的按钮
2. 前端发送 `table:button:click` 事件到后端
3. 后端根据 `actionId` 查找对应的 Action 配置
4. 执行 Action 的 `patches` 配置（与普通 Action 处理方式一致）

**Action 配置示例:**

```python
# 在创建实例时添加 Action 配置
await create_ui_instance(
    instance_name="my_instance",
    patches=[
        # ... 其他 patches ...
        {
            "op": "set",
            "path": "actions",
            "value": [
                {
                    "id": "edit_user",
                    "label": "编辑用户",
                    "style": "primary",
                    "action_type": "patch",
                    "patches": [
                        {
                            "op": "set",
                            "path": "state.params.edit_user_id",
                            "value": "${params.rowData.id}"
                        }
                    ]
                },
                {
                    "id": "delete_user",
                    "label": "删除用户",
                    "style": "danger",
                    "action_type": "patch",
                    "patches": [
                        {
                            "op": "remove",
                            "path": "state.params.users",
                            "value": "${params.rowData}"
                        }
                    ]
                }
            ]
        }
    ]
)
```

**表格列配置示例（使用 actionId）:**

```json
{
  "key": "actions",
  "label": "操作",
  "renderType": "mixed",
  "components": [
    {
      "type": "button",
      "buttonLabel": "编辑",
      "buttonStyle": "primary",
      "buttonSize": "small",
      "actionId": "edit_user"
    },
    {
      "type": "spacer",
      "width": "8px"
    },
    {
      "type": "button",
      "buttonLabel": "删除",
      "buttonStyle": "danger",
      "buttonSize": "small",
      "actionId": "delete_user",
      "confirmMessage": "确定要删除此用户吗？"
    }
  ]
}
```

**事件传递的参数:**
当按钮点击时，以下参数会自动传递给 Action：
- `rowData`: 当前行数据对象
- `rowIndex`: 行索引
- `fieldKey`: 表格字段 key（标识是哪个表格）
- `params`: 按钮配置中自定义的参数
- `_actionId`: 关联的 Action ID

**在 Action 的 patches 中使用这些参数:**

```python
{
    "id": "edit_user",
    "label": "编辑用户",
    "patches": [
        # 使用 ${params.rowData.id} 获取当前行的 id
        {
            "op": "set",
            "path": "state.params.selected_user",
            "value": "${params.rowData}"
        },
        {
            "op": "set",
            "path": "state.params.mode",
            "value": "edit"
        }
    ]
}
```

**场景示例 1: 状态标签 + 操作按钮**

```json
{
  "key": "actions",
  "label": "操作",
  "renderType": "mixed",
  "components": [
    {
      "type": "tag",
      "field": "status",
      "tagType": "success"
    },
    {
      "type": "spacer",
      "width": "16px"
    },
    {
      "type": "button",
      "buttonLabel": "编辑",
      "buttonStyle": "primary",
      "buttonSize": "small",
      "actionType": "edit"
    },
    {
      "type": "spacer",
      "width": "8px"
    },
    {
      "type": "button",
      "buttonLabel": "删除",
      "buttonStyle": "danger",
      "buttonSize": "small",
      "actionType": "delete"
    }
  ]
}
```

数据示例:
```json
[
  {"id": 1, "status": "active"},
  {"id": 2, "status": "pending"}
]
```

**场景示例 2: 图片 + 名称 + 状态**

```json
{
  "key": "user_info",
  "label": "用户信息",
  "renderType": "mixed",
  "components": [
    {
      "type": "image",
      "field": "avatar",
      "imageSize": "40px",
      "imageFit": "cover"
    },
    {
      "type": "spacer",
      "width": "12px"
    },
    {
      "type": "text",
      "field": "name"
    },
    {
      "type": "spacer",
      "width": "8px"
    },
    {
      "type": "tag",
      "field": "status",
      "tagType": "info"
    }
  ]
}
```

数据示例:
```json
[
  {
    "id": 1,
    "name": "张三",
    "avatar": "https://example.com/avatar1.jpg",
    "status": "online"
  },
  {
    "id": 2,
    "name": "李四",
    "avatar": "https://example.com/avatar2.jpg",
    "status": "offline"
  }
]
```

**场景示例 3: 徽章 + 文本 + 进度条**

```json
{
  "key": "task_detail",
  "label": "任务详情",
  "renderType": "mixed",
  "components": [
    {
      "type": "badge",
      "field": "priority",
      "badgeColor": "#ff4d4f"
    },
    {
      "type": "spacer",
      "width": "12px"
    },
    {
      "type": "text",
      "field": "title"
    },
    {
      "type": "spacer",
      "width": "16px"
    },
    {
      "type": "progress",
      "field": "progress"
    }
  ]
}
```

数据示例:
```json
[
  {
    "id": 1,
    "priority": "高",
    "title": "完成API开发",
    "progress": {"current": 4, "total": 5}
  }
]
```

#### 排序功能

设置 `sortable: true` 后，点击列标题可排序：
- 首次点击: 升序 (asc)
- 第二次点击: 降序 (desc)
- 第三次点击: 取消排序

#### 完整示例

**基础表格:**
```json
{
  "op": "set",
  "path": "state.params.users",
  "value": [
    {"id": 1, "name": "张三", "age": 25, "status": "active"},
    {"id": 2, "name": "李四", "age": 30, "status": "inactive"}
  ]
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "用户列表",
    "key": "users",
    "type": "table",
    "columns": [
      {"key": "name", "label": "姓名", "width": "150px"},
      {"key": "age", "label": "年龄", "align": "center", "sortable": true},
      {"key": "status", "label": "状态", "align": "center"}
    ],
    "rowKey": "id",
    "bordered": true,
    "striped": true,
    "hover": true
  }
}
```

**带多种渲染类型的表格:**
```json
{
  "op": "set",
  "path": "state.params.tasks",
  "value": [
    {
      "id": 1,
      "name": "任务A",
      "status": "active",
      "priority": 5,
      "progress": {"current": 3, "total": 5},
      "avatar": "https://example.com/avatar1.jpg"
    },
    {
      "id": 2,
      "name": "任务B",
      "status": "pending",
      "priority": 3,
      "progress": {"current": 1, "total": 5},
      "avatar": "https://example.com/avatar2.jpg"
    }
  ]
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "任务列表",
    "key": "tasks",
    "type": "table",
    "columns": [
      {"key": "name", "label": "名称", "width": "200px", "sortable": true},
      {"key": "status", "label": "状态", "align": "center", "renderType": "tag"},
      {"key": "priority", "label": "优先级", "align": "center", "renderType": "badge", "badgeColor": "#1890ff"},
      {"key": "progress", "label": "进度", "renderType": "progress"},
      {"key": "avatar", "label": "头像", "align": "center", "renderType": "image"}
    ],
    "rowKey": "id",
    "bordered": true,
    "striped": true,
    "hover": true,
    "maxHeight": "300px"
  }
}
```

**带分页的表格:**
```json
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "数据列表",
    "key": "data",
    "type": "table",
    "columns": [
      {"key": "id", "label": "ID", "width": "80px"},
      {"key": "name", "label": "名称"}
    ],
    "showPagination": true,
    "pageSize": 10,
    "bordered": true
  }
}
```

---

### modal - 模态框

显示模态对话框。

**属性:**
- `label` (必填): 字段标签
- `key` (必填): 字段唯一标识
- `type` (必填): 必须为 "modal"
- `value` (可选): 模态框配置对象
  - `visible`: 是否显示，布尔值
  - `title`: 标题文本
  - `content`: HTML 内容字符串
  - `width`: 宽度（像素），默认 520
  - `okText`: 确定按钮文本，默认 "确定"
  - `cancelText`: 取消按钮文本，默认 "取消"

**示例:**
```json
{
  "op": "set",
  "path": "state.params.modal",
  "value": {
    "visible": true,
    "title": "确认操作",
    "content": "<p>确定要执行此操作吗？</p>",
    "okText": "确认",
    "cancelText": "取消"
  }
},
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "确认对话框",
    "key": "modal",
    "type": "modal"
  }
}
```

---

## 完整示例

### 创建一个包含多种字段类型的实例

```json
{
  "instance_name": "__CREATE__",
  "new_instance_name": "example_instance",
  "patches": [
    {
      "op": "set",
      "path": "meta",
      "value": {
        "pageKey": "example",
        "step": {"current": 1, "total": 1}
      }
    },
    {
      "op": "set",
      "path": "state",
      "value": {
        "params": {
          "username": "",
          "age": 0,
          "gender": "",
          "hobbies": ["reading", "coding"],
          "tags": [
            {"label": "活跃", "type": "success"},
            {"label": "VIP", "type": "warning"}
          ],
          "progress": {"current": 3, "total": 5},
          "notification": {"count": 5, "label": "消息"},
          "users": [
            {"id": 1, "name": "张三", "age": 25, "status": "active"}
          ],
          "modal": {"visible": false, "title": "提示"}
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
              {
                "label": "用户名",
                "key": "username",
                "type": "text"
              },
              {
                "label": "年龄",
                "key": "age",
                "type": "number"
              },
              {
                "label": "性别",
                "key": "gender",
                "type": "select",
                "options": [
                  {"label": "男", "value": "male"},
                  {"label": "女", "value": "female"}
                ]
              },
              {
                "label": "爱好",
                "key": "hobbies",
                "type": "multiselect",
                "options": [
                  {"label": "阅读", "value": "reading"},
                  {"label": "编程", "value": "coding"},
                  {"label": "运动", "value": "sports"}
                ]
              },
              {
                "label": "标签",
                "key": "tags",
                "type": "tag"
              },
              {
                "label": "进度",
                "key": "progress",
                "type": "progress"
              },
              {
                "label": "通知",
                "key": "notification",
                "type": "badge"
              },
              {
                "label": "用户列表",
                "key": "users",
                "type": "table",
                "columns": [
                  {"key": "name", "label": "姓名"},
                  {"key": "age", "label": "年龄"},
                  {"key": "status", "label": "状态"}
                ]
              }
            ]
          }
        }
      ]
    },
    {
      "op": "set",
      "path": "actions",
      "value": []
    }
  ]
}
```

---

## 模板渲染功能

系统支持在多种字段类型中使用模板渲染，语法为 `${state.xxx}`。

### 支持的字段类型

以下字段类型支持模板渲染：
- `text` - 单行文本
- `textarea` - 多行文本
- `json` - JSON 编辑器
- `html` - HTML 内容

### 模板语法

- `${state.params.xxx}` - 引用 params 中的值
- `${state.runtime.xxx}` - 引用 runtime 中的值
- 支持嵌套路径：`${state.params.user.name}`

### 自动时间戳更新

当模板引用 `state.runtime.timestamp` 时，系统会自动更新时间戳为当前时间，无需手动处理。

### 示例

```json
{
  "op": "set",
  "path": "state.params.message",
  "value": "操作于 ${state.runtime.timestamp} 完成"
}
```

每次渲染模板时，`${state.runtime.timestamp}` 都会自动更新为当前时间。

---

## 对象值处理

以下字段类型支持对象值自动转换为 JSON 字符串：
- `text` - 单行文本
- `textarea` - 多行文本
- `json` - JSON 编辑器

当字段值为对象时，会自动使用 `JSON.stringify` 格式化显示，避免显示 `[object Object]`。

---

## 注意事项

1. **字段唯一性**: 同一个 `bind` 路径下，`key` 必须唯一
2. **类型一致性**: 字段类型一旦设置，不建议随意更改
3. **数组操作**: 使用 `multiselect` 时，值始终是字符串数组
4. **表格数据**: 表格的 `value` 必须是对象数组，每个对象的键应与 `columns.key` 匹配
5. **模态框状态**: 模态框通过 `visible` 字段控制显示/隐藏
6. **HTML 安全**: 使用 `html` 和 `modal` 类型时，注意 XSS 攻击风险
7. **模板渲染**: 引用 `state.runtime.timestamp` 时会自动更新时间戳
8. **对象显示**: 对象值会自动转换为 JSON 字符串，避免显示 `[object Object]`

---

## 总结

MCP 工具现在支持以下 **17 种字段类型**:

### 输入类 (5 种)
- `text` - 单行文本
- `number` - 数字输入
- `textarea` - 多行文本
- `checkbox` - 复选框
- `json` - JSON 编辑器

### 选择类 (3 种)
- `select` - 下拉选择
- `radio` - 单选按钮
- `multiselect` - 多选框

### 展示类 (8 种)
- `html` - HTML 内容
- `image` - 图片显示
- `tag` - 标签显示
- `progress` - 进度条
- `badge` - 徽章
- `table` - 数据表格
- `modal` - 模态框
- `component` - 嵌入渲染（跨实例引用）

---

## 组件嵌入渲染 (component)

`component` 类型用于嵌入其他实例的内容到当前页面中，实现组件复用。

### 属性
| 属性 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `targetInstance` | `string` | 是 | 要嵌入的目标实例 ID |
| `targetBlock` | `string` | 否 | 要嵌入的目标 block ID（不指定则渲染所有 block） |

### 使用示例

```json
{
  "op": "add",
  "path": "blocks.0.props.fields",
  "value": {
    "label": "嵌入图表",
    "key": "embedded_chart",
    "type": "component",
    "targetInstance": "chart_instance"
  }
}
```

### 说明
- 嵌入渲染是静态的，不涉及数据传递和事件处理
- 渲染时不会显示字段的 label
- 如果指定 `targetBlock`，只渲染指定的 block
- 如果不指定 `targetBlock`，渲染目标实例的所有 block

---

## MCP 工具调用示例

### 示例 1: 创建一个带表格的仪表板（包含 mixed 渲染）

```python
from backend.mcp.tool_definitions import patch_ui_state

# 创建仪表板实例，包含一个带 mixed 渲染的表格
await patch_ui_state(
    instance_name="__CREATE__",
    new_instance_name="user_dashboard",
    patches=[
        # 设置元数据
        {"op": "set", "path": "meta", "value": {"pageKey": "dashboard", "step": {"current": 1, "total": 1}}},
        # 设置状态
        {"op": "set", "path": "state", "value": {
            "params": {},
            "runtime": {}
        }},
        # 设置 blocks
        {"op": "set", "path": "blocks", "value": [
            {
                "id": "main_block",
                "type": "form",
                "bind": "state.params",
                "props": {
                    "fields": [
                        # 欢迎文本
                        {
                            "label": "欢迎",
                            "key": "welcome",
                            "type": "static_content",
                            "contentType": "text",
                            "staticContent": {"text": "用户管理仪表板"}
                        },
                        # 统计数据
                        {
                            "label": "统计",
                            "key": "stats",
                            "type": "static_content",
                            "contentType": "stats",
                            "staticContent": {
                                "columns": 3,
                                "items": [
                                    {"label": "总用户", "value": "128"},
                                    {"label": "在线", "value": "45"},
                                    {"label": "VIP", "value": "23"}
                                ]
                            }
                        },
                        # 用户列表（带 mixed 渲染）
                        {
                            "label": "用户列表",
                            "key": "users",
                            "type": "table",
                            "value": [
                                {
                                    "id": 1,
                                    "name": "张三",
                                    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=1",
                                    "status": "online",
                                    "role": "管理员"
                                },
                                {
                                    "id": 2,
                                    "name": "李四",
                                    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=2",
                                    "status": "offline",
                                    "role": "普通用户"
                                },
                                {
                                    "id": 3,
                                    "name": "王五",
                                    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=3",
                                    "status": "busy",
                                    "role": "VIP用户"
                                }
                            ],
                            "columns": [
                                {"key": "id", "label": "ID", "width": "80px", "align": "center"},
                                {
                                    "key": "user_info",
                                    "label": "用户信息",
                                    "width": "250px",
                                    "renderType": "mixed",
                                    "components": [
                                        {"type": "image", "field": "avatar", "imageSize": "40px", "imageFit": "cover"},
                                        {"type": "spacer", "width": "12px"},
                                        {"type": "text", "field": "name"}
                                    ]
                                },
                                {
                                    "key": "status_info",
                                    "label": "状态信息",
                                    "align": "center",
                                    "renderType": "mixed",
                                    "components": [
                                        {"type": "tag", "field": "status"},
                                        {"type": "spacer", "width": "8px"},
                                        {"type": "text", "field": "role"}
                                    ]
                                },
                                {
                                    "key": "actions",
                                    "label": "操作",
                                    "align": "center",
                                    "renderType": "mixed",
                                    "components": [
                                        {
                                            "type": "button",
                                            "buttonLabel": "编辑",
                                            "buttonStyle": "primary",
                                            "buttonSize": "small",
                                            "actionType": "edit"
                                        },
                                        {"type": "spacer", "width": "8px"},
                                        {
                                            "type": "button",
                                            "buttonLabel": "删除",
                                            "buttonStyle": "danger",
                                            "buttonSize": "small",
                                            "actionType": "delete"
                                        }
                                    ]
                                }
                            ],
                            "rowKey": "id",
                            "bordered": True,
                            "striped": True,
                            "hover": True,
                            "maxHeight": "400px"
                        }
                    ]
                }
            }
        ]},
        {"op": "set", "path": "actions", "value": []}
    ]
)
```

### 示例 2: 添加带多种渲染类型的任务表格

```python
# 在现有实例中添加一个任务列表表格
await patch_ui_state(
    instance_name="my_instance",
    patches=[
        {"op": "set", "path": "state.params.tasks", "value": [
            {
                "id": 1,
                "title": "完成API开发",
                "status": "active",
                "priority": "高",
                "progress": {"current": 4, "total": 5}
            },
            {
                "id": 2,
                "title": "编写测试用例",
                "status": "pending",
                "priority": "中",
                "progress": {"current": 0, "total": 5}
            },
            {
                "id": 3,
                "title": "性能优化",
                "status": "completed",
                "priority": "低",
                "progress": {"current": 5, "total": 5}
            }
        ]},
        {"op": "add", "path": "blocks.0.props.fields", "value": {
            "label": "任务列表",
            "key": "tasks",
            "type": "table",
            "columns": [
                {"key": "title", "label": "任务名称", "width": "200px", "sortable": True},
                {"key": "status", "label": "状态", "align": "center", "renderType": "tag"},
                {"key": "priority", "label": "优先级", "align": "center", "renderType": "badge", "badgeColor": "#1890ff"},
                {"key": "progress", "label": "进度", "renderType": "progress"}
            ],
            "rowKey": "id",
            "bordered": True,
            "striped": True,
            "hover": True
        }}
    ]
)
```

### 示例 3: 动态更新表格数据

```python
# 更新现有表格的数据
await patch_ui_state(
    instance_name="user_dashboard",
    patches=[
        {"op": "set", "path": "state.params.users", "value": [
            {
                "id": 1,
                "name": "新用户A",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=100",
                "status": "online",
                "role": "管理员"
            },
            {
                "id": 2,
                "name": "新用户B",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=200",
                "status": "offline",
                "role": "普通用户"
            }
        ]}
    ]
)
```

### 示例 5: 添加带进度和徽章的混合列

```python
# 添加一个任务详情表格，使用 mixed 类型组合多个元素
await patch_ui_state(
    instance_name="task_manager",
    patches=[
        {"op": "set", "path": "state.params.detailed_tasks", "value": [
            {
                "id": 1,
                "priority": "高",
                "title": "紧急修复",
                "progress": {"current": 4, "total": 5}
            },
            {
                "id": 2,
                "priority": "中",
                "title": "常规任务",
                "progress": {"current": 2, "total": 5}
            }
        ]},
        {"op": "add", "path": "blocks.0.props.fields", "value": {
            "label": "任务详情",
            "key": "detailed_tasks",
            "type": "table",
            "columns": [
                {
                    "key": "task_detail",
                    "label": "任务",
                    "width": "300px",
                    "renderType": "mixed",
                    "components": [
                        {"type": "badge", "field": "priority", "badgeColor": "#ff4d4f"},
                        {"type": "spacer", "width": "12px"},
                        {"type": "text", "field": "title"}
                    ]
                },
                {
                    "key": "progress",
                    "label": "完成度",
                    "align": "center",
                    "renderType": "progress"
                }
            ],
            "rowKey": "id",
            "bordered": True
        }}
    ]
)
```

### 快速测试脚本

```python
# test_mcp_tools.py
import asyncio
from backend.mcp.tool_definitions import patch_ui_state, get_schema, list_instances

async def test_mcp_tools():
    # 1. 列出所有实例
    instances = await list_instances()
    print("现有实例:", instances)

    # 2. 创建测试实例
    await patch_ui_state(
        instance_name="__CREATE__",
        new_instance_name="test_mixed_table",
        patches=[
            {"op": "set", "path": "meta", "value": {"pageKey": "test", "step": {"current": 1, "total": 1}}},
            {"op": "set", "path": "state", "value": {"params": {}, "runtime": {}}},
            {"op": "set", "path": "blocks", "value": [{
                "id": "test_block",
                "type": "form",
                "bind": "state.params",
                "props": {"fields": []}
            }]},
            {"op": "set", "path": "actions", "value": []}
        ]
    )

    # 3. 添加 mixed 表格
    await patch_ui_state(
        instance_name="test_mixed_table",
        patches=[
            {"op": "set", "path": "state.params.data", "value": [
                {"id": 1, "name": "张三", "status": "active"},
                {"id": 2, "name": "李四", "status": "pending"}
            ]},
            {"op": "add", "path": "blocks.0.props.fields", "value": {
                "label": "测试表格",
                "key": "data",
                "type": "table",
                "value": [
                    {"id": 1, "name": "张三", "status": "active"},
                    {"id": 2, "name": "李四", "status": "pending"}
                ],
                "columns": [
                    {"key": "name", "label": "姓名"},
                    {"key": "status", "label": "状态", "renderType": "tag"},
                    {
                        "key": "actions",
                        "label": "操作",
                        "renderType": "mixed",
                        "components": [
                            {"type": "tag", "field": "status"},
                            {"type": "spacer", "width": "8px"},
                            {"type": "button", "buttonLabel": "查看", "buttonStyle": "primary", "buttonSize": "small", "actionType": "view"}
                        ]
                    }
                ],
                "rowKey": "id"
            }}
        ]
    )

    # 4. 获取 Schema 验证
    schema = await get_schema("test_mixed_table")
    print("Schema:", schema)

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
```


