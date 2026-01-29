# 布局组件使用指南

本指南展示了如何在项目中使用不同的布局类型来组织和展示字段。

## 概述

布局类型通过 `BlockRenderer` 实现，在不影响现有字段渲染逻辑的情况下，提供了灵活的布局选项。所有布局类型都使用 `GenericFieldRenderer` 来渲染字段，确保了字段类型的一致性和复用性。

## 可用布局类型

### 1. Card 布局 (card)

卡片式布局，使用 Card 组件包装字段，适合分组显示相关字段。

**使用示例：**

```json
{
  "id": "personal-info",
  "type": "card",
  "title": "个人信息",
  "bind": "user",
  "props": {
    "fields": [
      {
        "key": "name",
        "type": "text",
        "label": "姓名"
      },
      {
        "key": "email",
        "type": "text",
        "label": "邮箱"
      },
      {
        "key": "phone",
        "type": "text",
        "label": "电话"
      }
    ]
  }
}
```

**属性：**
- `title`: 卡片标题（可选）
- `fields`: 字段数组

---

### 2. Columns 布局 (columns)

多列布局，将字段分成指定数量的列，适合并排显示多个字段。

**使用示例：**

```json
{
  "id": "two-column",
  "type": "columns",
  "title": "基本信息",
  "bind": "data",
  "props": {
    "columns": 2,
    "fields": [
      {
        "key": "firstName",
        "type": "text",
        "label": "名"
      },
      {
        "key": "lastName",
        "type": "text",
        "label": "姓"
      },
      {
        "key": "age",
        "type": "number",
        "label": "年龄"
      },
      {
        "key": "gender",
        "type": "select",
        "label": "性别",
        "options": [
          { "value": "male", "label": "男" },
          { "value": "female", "label": "女" }
        ]
      }
    ]
  }
}
```

**属性：**
- `title`: 区块标题（可选）
- `columns`: 列数（默认 2）
- `fields`: 字段数组（按顺序分配到各列）

---

### 3. Tabs 布局 (tabs)

标签页布局，将字段分组到不同的标签页中。

**使用示例：**

```json
{
  "id": "user-settings",
  "type": "tabs",
  "title": "用户设置",
  "bind": "user",
  "props": {
    "tabs": [
      {
        "label": "基本信息",
        "fields": [
          {
            "key": "username",
            "type": "text",
            "label": "用户名"
          },
          {
            "key": "email",
            "type": "text",
            "label": "邮箱"
          }
        ]
      },
      {
        "label": "安全设置",
        "fields": [
          {
            "key": "password",
            "type": "text",
            "label": "密码"
          },
          {
            "key": "twoFactor",
            "type": "checkbox",
            "label": "启用两步验证"
          }
        ]
      },
      {
        "label": "偏好设置",
        "fields": [
          {
            "key": "language",
            "type": "select",
            "label": "语言",
            "options": [
              { "value": "zh", "label": "中文" },
              { "value": "en", "label": "English" }
            ]
          },
          {
            "key": "theme",
            "type": "radio",
            "label": "主题",
            "options": [
              { "value": "light", "label": "浅色" },
              { "value": "dark", "label": "深色" }
            ]
          }
        ]
      }
    ]
  }
}
```

**属性：**
- `title`: 区块标题（可选）
- `tabs`: 标签页数组
  - `label`: 标签页标题
  - `fields`: 该标签页的字段数组

---

### 4. Grid 布局 (grid)

网格布局，使用 CSS Grid 创建响应式网格，适合大量字段的展示。

**使用示例：**

```json
{
  "id": "form-grid",
  "type": "grid",
  "title": "详细表单",
  "bind": "formData",
  "props": {
    "cols": 3,
    "gap": "16px",
    "fields": [
      {
        "key": "field1",
        "type": "text",
        "label": "字段 1"
      },
      {
        "key": "field2",
        "type": "text",
        "label": "字段 2"
      },
      {
        "key": "field3",
        "type": "text",
        "label": "字段 3"
      },
      {
        "key": "field4",
        "type": "text",
        "label": "字段 4"
      },
      {
        "key": "field5",
        "type": "text",
        "label": "字段 5"
      },
      {
        "key": "field6",
        "type": "text",
        "label": "字段 6"
      }
    ]
  }
}
```

**属性：**
- `title`: 区块标题（可选）
- `cols`: 列数（默认 3）
- `gap`: 网格间距（默认 "16px"）
- `fields`: 字段数组

---

### 5. Accordion 布局 (accordion)

折叠面板布局，将内容分组到可折叠的面板中，节省空间。

**使用示例：**

```json
{
  "id": "faq-section",
  "type": "accordion",
  "title": "常见问题",
  "bind": "faq",
  "props": {
    "panels": [
      {
        "title": "账号问题",
        "fields": [
          {
            "key": "question1",
            "type": "text",
            "label": "如何注册账号？"
          },
          {
            "key": "answer1",
            "type": "textarea",
            "label": "答案"
          }
        ]
      },
      {
        "title": "支付问题",
        "fields": [
          {
            "key": "question2",
            "type": "text",
            "label": "支持哪些支付方式？"
          },
          {
            "key": "answer2",
            "type": "textarea",
            "label": "答案"
          }
        ]
      },
      {
        "title": "技术支持",
        "fields": [
          {
            "key": "question3",
            "type": "text",
            "label": "如何联系客服？"
          },
          {
            "key": "answer3",
            "type": "textarea",
            "label": "答案"
          }
        ]
      }
    ]
  }
}
```

**属性：**
- `title`: 区块标题（可选）
- `panels`: 面板数组
  - `title`: 面板标题
  - `fields`: 该面板的字段数组

---

## 完整示例

以下是一个完整的 UISchema 示例，展示了如何组合使用不同的布局类型：

```json
{
  "title": "用户管理系统",
  "blocks": [
    {
      "id": "user-profile",
      "type": "card",
      "title": "用户资料",
      "bind": "user",
      "props": {
        "fields": [
          {
            "key": "avatar",
            "type": "image",
            "label": "头像"
          },
          {
            "key": "name",
            "type": "text",
            "label": "姓名"
          }
        ]
      }
    },
    {
      "id": "user-details",
      "type": "columns",
      "title": "详细信息",
      "bind": "user",
      "props": {
        "columns": 2,
        "fields": [
          {
            "key": "email",
            "type": "text",
            "label": "邮箱"
          },
          {
            "key": "phone",
            "type": "text",
            "label": "电话"
          },
          {
            "key": "age",
            "type": "number",
            "label": "年龄"
          },
          {
            "key": "gender",
            "type": "select",
            "label": "性别",
            "options": [
              { "value": "male", "label": "男" },
              { "value": "female", "label": "女" }
            ]
          }
        ]
      }
    },
    {
      "id": "settings-tabs",
      "type": "tabs",
      "title": "系统设置",
      "bind": "settings",
      "props": {
        "tabs": [
          {
            "label": "通知设置",
            "fields": [
              {
                "key": "emailNotification",
                "type": "checkbox",
                "label": "邮件通知"
              },
              {
                "key": "smsNotification",
                "type": "checkbox",
                "label": "短信通知"
              }
            ]
          },
          {
            "label": "隐私设置",
            "fields": [
              {
                "key": "profileVisible",
                "type": "checkbox",
                "label": "公开个人资料"
              }
            ]
          }
        ]
      }
    }
  ],
  "data": {
    "user": {
      "avatar": "https://example.com/avatar.jpg",
      "name": "张三",
      "email": "zhangsan@example.com",
      "phone": "13800138000",
      "age": 28,
      "gender": "male"
    },
    "settings": {
      "emailNotification": true,
      "smsNotification": false,
      "profileVisible": true
    }
  }
}
```

---

## 自定义布局类型

如果需要添加自定义的布局类型，可以使用 `registerBlockRenderer` 函数：

```typescript
import { registerBlockRenderer } from './components/BlockRenderer';

registerBlockRenderer('myCustomLayout', ({ block, schema, disabled, highlightField, highlightBlockId }) => {
  // 自定义布局逻辑
  return (
    <div style={{ /* 自定义样式 */ }}>
      {block.props?.fields?.map((field) => (
        <GenericFieldRenderer
          key={field.key}
          field={field}
          schema={schema}
          bindPath={block.bind}
          disabled={disabled}
          highlighted={field.key === highlightField}
        />
      ))}
    </div>
  );
});
```

---

## 注意事项

1. **字段渲染一致性**: 所有布局类型都使用 `GenericFieldRenderer` 渲染字段，确保字段类型的行为一致。

2. **数据绑定**: 每个布局都通过 `bind` 属性指定数据路径，字段相对于该路径进行绑定。

3. **响应式设计**: 大多数布局都支持响应式，会自动适应不同屏幕尺寸。

4. **高亮支持**: 所有布局都支持字段高亮功能，通过 `highlightField` 参数实现。

5. **禁用状态**: 所有布局都支持全局禁用，通过 `disabled` 参数控制。

---

## 布局选择建议

| 场景 | 推荐布局 | 原因 |
|------|---------|------|
| 单一组相关字段 | card | 视觉分组清晰 |
| 需要并排显示 | columns | 节省垂直空间 |
| 字段过多 | tabs | 分组管理，避免滚动 |
| 大量表单字段 | grid | 高效利用空间 |
| 内容需要折叠 | accordion | 节省空间，按需展开 |
| 混合需求 | 组合使用 | 不同区块使用不同布局 |
