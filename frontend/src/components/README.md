# 数据展示与反馈组件

## CodeBlock - 代码块显示

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

---

## Markdown - Markdown 渲染

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

---

## JSONViewer - JSON 查看器

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

---

## Table - 表格

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

---

## Tag - 标签

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

---

## Badge - 徽章

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

---

## Modal - 模态框

```tsx
import { Modal } from './components';
import { useState } from 'react';

function App() {
  const [visible, setVisible] = useState(false);

  return (
    <div>
      <button onClick={() => setVisible(true)}>
        打开模态框
      </button>

      <Modal
        visible={visible}
        title="标题"
        onCancel={() => setVisible(false)}
        onOk={() => {
          console.log('确定');
          setVisible(false);
        }}
        okText="确定"
        cancelText="取消"
        width={600}
        maskClosable
      >
        <div>模态框内容</div>
      </Modal>
    </div>
  );
}
```

**Props:**
- `visible` - 是否显示
- `title` - 标题
- `children` - 内容
- `footer` - 自定义底部操作栏（不传则使用默认按钮）
- `onCancel` - 取消回调
- `onOk` - 确定回调
- `okText` - 确定按钮文字（默认: '确定'）
- `cancelText` - 取消按钮文字（默认: '取消'）
- `width` - 宽度（默认: 520）
- `maskClosable` - 点击遮罩是否关闭（默认: true）

**特性:**
- 自动禁止背景滚动
- 点击遮罩关闭（可配置）
- ESC 键关闭
- 支持自定义底部操作栏

---

## 组合使用示例

### 表格 + 徽章 + 标签

```tsx
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
<Card title="API 文档">
  <Markdown content="# 用户接口\n\n获取用户信息" />

  <Table
    columns={columns}
    data={apiData}
    rowKey="id"
  />
</Card>
```
