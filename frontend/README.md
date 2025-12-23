# Frontend 前端模块

前端模块包含所有用户界面资源和组件。

## 目录结构

```
├── main.css           # 全局样式和 CSS 变量
├── components/        # 可复用组件
└── pages/            # 页面模板
```

## 组件化架构

每个组件独立，包含 CSS 和 JS 两个文件。

## 样式系统

使用 CSS 变量实现主题系统，定义在 `main.css` 中。

## 常用组件

- kpi_cards: KPI 指标展示
- tables: 数据表格
- drawer: 侧边详情面板
- picture: 图片/HTML 内容展示
- buttons: 按钮组件
- function_cards: 功能卡片
- informations: 信息展示组件

## 开发指南

新增组件时，在 `components/` 下创建新目录，包含对应的 CSS 和 JS 文件。
