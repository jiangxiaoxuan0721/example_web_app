# 前端组件库

## 可用组件

### 基础 UI 组件

#### `Loading`
加载状态显示组件

```tsx
import { Loading } from './components';

<Loading />
```

#### `ErrorState`
错误状态显示组件

```tsx
import { ErrorState } from './components';

<ErrorState error="加载失败" />
```

#### `InstanceSelector`
实例选择器（导航）

```tsx
import { InstanceSelector } from './components';

<InstanceSelector currentInstanceId="demo" />
```

#### `Spinner`
加载动画组件

```tsx
import { Spinner } from './components';

<Spinner size={40} color="#007bff" />
```

#### `Alert`
提示/警告/错误消息组件

```tsx
import { Alert } from './components';

<Alert type="info" message="这是一条提示信息" />
<Alert type="success" message="操作成功" />
<Alert type="warning" message="请注意" dismissible />
<Alert type="error" message="发生错误" onDismiss={() => {}} />
```

#### `Card`
卡片容器组件

```tsx
import { Card } from './components';

<Card title="卡片标题">
  <div>卡片内容</div>
</Card>
```

#### `Modal`
模态框组件

```tsx
import { Modal } from './components';

<Modal
  visible={showModal}
  title="标题"
  onOk={() => console.log('OK')}
  onCancel={() => setShowModal(false)}
>
  模态框内容
</Modal>
```

### 表单组件

#### `FieldDisplay`
只读字段显示组件

```tsx
import { FieldDisplay } from './components';

<FieldDisplay
  field={fieldConfig}
  schema={schema}
  bindPath="state.params"
/>
```

#### `InputField`
文本输入框组件

```tsx
import { InputField } from './components';

<InputField
  field={fieldConfig}
  schema={schema}
  bindPath="state.params"
  onChange={(value) => console.log(value)}
  disabled={false}
/>
```

#### `NumberInput`
数字输入框组件

```tsx
import { NumberInput } from './components';

<NumberInput
  field={fieldConfig}
  schema={schema}
  bindPath="state.params"
  onChange={(value) => console.log(value)}
/>
```

#### `TextArea`
多行文本框组件

```tsx
import { TextArea } from './components';

<TextArea
  field={fieldConfig}
  schema={schema}
  bindPath="state.params"
  onChange={(value) => console.log(value)}
  rows={4}
/>
```

#### `Select`
下拉选择组件

```tsx
import { Select } from './components';

<Select
  field={fieldConfig}
  schema={schema}
  bindPath="state.params"
  onChange={(value) => console.log(value)}
/>
```

#### `CheckBox`
复选框组件

```tsx
import { CheckBox } from './components';

<CheckBox
  field={fieldConfig}
  schema={schema}
  bindPath="state.params"
  onChange={(value) => console.log(value)}
/>
```

#### `RadioGroup`
单选按钮组组件

```tsx
import { RadioGroup } from './components';

<RadioGroup
  field={fieldConfig}
  schema={schema}
  bindPath="state.params"
  onChange={(value) => console.log(value)}
/>
```

### 数据展示组件

#### `CodeBlock`
代码块显示组件

```tsx
import { CodeBlock } from './components';

<CodeBlock
  code="console.log('Hello World');"
  language="javascript"
  showLineNumbers
/>
```

**Props:**
- `code` - 代码内容
- `language` - 代码语言（默认: 'text'）
- `showLineNumbers` - 是否显示行号（默认: false）

#### `Markdown`
Markdown 渲染组件

```tsx
import { Markdown } from './components';

<Markdown content="# 标题\n\n这是**加粗**文本" />
```

**Props:**
- `content` - Markdown 内容
- `className` - 自定义类名

**支持的语法:**
- 标题 (#, ##, ###)
- 粗体 (**text**)
- 斜体 (*text*)
- 行内代码 (`code`)
- 代码块 (```)
- 链接 [text](url)
- 无序列表 (- item)

#### `JSONViewer`
JSON 查看器组件

```tsx
import { JSONViewer } from './components';

const data = {
  name: "John",
  age: 30,
  hobbies: ["reading", "coding"]
};

<JSONViewer
  data={data}
  expandDepth={2}
  showLineNumbers
/>
```

**Props:**
- `data` - JSON 数据
- `expandDepth` - 默认展开深度（默认: 2）
- `showLineNumbers` - 是否显示行号（默认: false）

**特性:**
- 语法高亮（不同类型不同颜色）
- 可展开/折叠树形结构
- 支持深色主题

#### `Table`
表格组件

```tsx
import { Table } from './components';

const columns = [
  {
    key: 'name',
    label: '姓名',
    width: '150px'
  },
  {
    key: 'age',
    label: '年龄',
    align: 'center'
  },
  {
    key: 'action',
    label: '操作',
    render: (value, record, index) => (
      <button onClick={() => console.log(record)}>
        查看
      </button>
    )
  }
];

const data = [
  { id: 1, name: '张三', age: 25 },
  { id: 2, name: '李四', age: 30 }
];

<Table
  columns={columns}
  data={data}
  rowKey="id"
  bordered
  striped
  hover
  emptyText="暂无数据"
/>
```

**Props:**
- `columns` - 列配置
  - `key` - 字段键
  - `label` - 列标题
  - `width` - 列宽度
  - `align` - 对齐方式（'left' | 'center' | 'right'）
  - `render` - 自定义渲染函数 `(value, record, index) => ReactNode`
- `data` - 数据数组
- `rowKey` - 行唯一键（默认: 'id'）
- `bordered` - 是否显示边框（默认: true）
- `striped` - 是否斑马纹（默认: true）
- `hover` - 是否悬停高亮（默认: true）
- `emptyText` - 空数据提示（默认: '暂无数据'）

### 反馈组件

#### `Progress`
进度条组件

```tsx
import { Progress } from './components';

<Progress current={1} total={5} showLabel />
```

#### `Tag`
标签组件

```tsx
import { Tag } from './components';

<Tag type="success" label="已通过" />
<Tag type="warning" label="待审核" closable onClose={() => {}} />
<Tag type="error" label="已拒绝" />
```

**Props:**
- `type` - 标签类型（'default' | 'success' | 'warning' | 'error' | 'info'）
- `label` - 标签文本
- `closable` - 是否可关闭（默认: false）
- `onClose` - 关闭回调
- `style` - 自定义样式

**类型样式:**
- `default` - 灰色
- `success` - 绿色
- `warning` - 黄色
- `error` - 红色
- `info` - 蓝色

#### `Badge`
徽章组件

```tsx
import { Badge } from './components';

<Badge count={5}>
  <button>消息</button>
</Badge>

<Badge count={100} max={99}>
  <span>通知</span>
</Badge>

<Badge dot>
  <div>状态</div>
</Badge>

<Badge count={0} showZero>
  <span>空</span>
</Badge>
```

**Props:**
- `count` - 徽章数字
- `dot` - 是否显示圆点（默认: false）
- `children` - 包裹的子元素
- `color` - 徽章颜色（默认: '#f5222d'）
- `showZero` - count 为 0 时是否显示（默认: false）
- `max` - 最大显示值（超过显示 "N+"，默认: 99）

### 特殊组件

#### `ActionButton`
操作按钮组件

```tsx
import { ActionButton } from './components';

<ActionButton
  action={actionConfig}
  onClick={() => console.log('clicked')}
/>
```

#### `BlockRenderer`
Block 渲染器（根据字段类型自动选择组件）

```tsx
import { BlockRenderer } from './components';

<BlockRenderer
  block={blockConfig}
  schema={schema}
  onFieldChange={(fieldKey, value) => {
    console.log(`字段 ${fieldKey} 变为 ${value}`);
  }}
  disabled={false}
/>
```

## 字段类型

在 `FieldConfig` 中定义的字段类型：

- `text` - 文本输入框
- `number` - 数字输入框
- `textarea` - 多行文本框
- `select` - 下拉选择
- `checkbox` - 复选框
- `radio` - 单选按钮组

## 字段配置示例

```typescript
{
  label: "姓名",
  key: "name",
  type: "text",
  description: "请输入您的姓名"
}
```

```typescript
{
  label: "年龄",
  key: "age",
  type: "number",
  description: "请输入您的年龄"
}
```

```typescript
{
  label: "简介",
  key: "description",
  type: "textarea",
  description: "请输入简介",
  rows: 4
}
```

```typescript
{
  label: "性别",
  key: "gender",
  type: "select",
  options: [
    { label: "男", value: "male" },
    { label: "女", value: "female" }
  ]
}
```

```typescript
{
  label: "同意条款",
  key: "agree",
  type: "checkbox"
}
```

```typescript
{
  label: "类型",
  key: "type",
  type: "radio",
  options: [
    { label: "个人", value: "personal" },
    { label: "企业", value: "company" }
  ]
}
```

## 使用示例

### 完整表单示例

```tsx
import { Card, BlockRenderer, ActionButton } from './components';

function MyForm() {
  return (
    <Card title="用户信息">
      <BlockRenderer
        block={{
          id: "user_form",
          type: "form",
          bind: "state.params",
          props: {
            fields: [
              {
                label: "姓名",
                key: "name",
                type: "text"
              },
              {
                label: "年龄",
                key: "age",
                type: "number"
              },
              {
                label: "性别",
                key: "gender",
                type: "select",
                options: [
                  { label: "男", value: "male" },
                  { label: "女", value: "female" }
                ]
              }
            ]
          }
        }}
        schema={schema}
        onFieldChange={(fieldKey, value) => {
          // 处理字段变化
          console.log(`${fieldKey}: ${value}`);
        }}
      />
      <ActionButton
        action={{
          id: "submit",
          label: "提交",
          style: "primary"
        }}
        onClick={handleSubmit}
      />
    </Card>
  );
}
```

### 表格 + 徽章 + 标签

```tsx
import { Table, Badge, Tag } from './components';

const columns = [
  {
    key: 'name',
    label: '姓名'
  },
  {
    key: 'status',
    label: '状态',
    render: (value) => (
      <Tag
        type={value === 'active' ? 'success' : 'warning'}
        label={value === 'active' ? '激活' : '待激活'}
      />
    )
  }
];

const data = [
  { id: 1, name: '用户1', status: 'active' },
  { id: 2, name: '用户2', status: 'pending' }
];

<Badge count={data.length}>
  <Table columns={columns} data={data} />
</Badge>
```

### 模态框 + 代码块 + JSON 查看器

```tsx
import { Modal, CodeBlock, JSONViewer } from './components';

<Modal
  visible={showModal}
  title="API 响应"
  onCancel={() => setShowModal(false)}
>
  <div style={{ marginBottom: '20px' }}>
    <h3>响应代码</h3>
    <CodeBlock code={responseCode} language="json" />
  </div>

  <div>
    <h3>结构化数据</h3>
    <JSONViewer data={responseData} />
  </div>
</Modal>
```

### Markdown + 表格

```tsx
import { Card, Table } from './components';

<Card title="API 文档">
  <Markdown content="# 用户接口\n\n获取用户信息" />

  <Table
    columns={columns}
    data={apiData}
    rowKey="id"
  />
</Card>
```

### 只读显示模式

当不传递 `onFieldChange` 或 `disabled={true}` 时，所有字段都只读显示：

```tsx
<BlockRenderer
  block={blockConfig}
  schema={schema}
  // 不传 onFieldChange 或 disabled={true}
  // => 只读模式
/>
```

## 样式自定义

所有组件都支持通过 `style` prop 自定义样式：

```tsx
<Card
  title="自定义卡片"
  style={{
    background: '#f0f0f0',
    borderColor: '#007bff'
  }}
>
  ...
</Card>
```
