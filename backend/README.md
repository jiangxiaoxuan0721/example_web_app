# Backend 后端模块

后端模块负责数据处理和 CloudPSS 仿真。

## 目录结构

```
├── data_generator/   # 数据生成模块（CloudPSS 仿真）
└── data_processor/  # 数据处理模块
```

## 功能

### data_generator

调用 CloudPSS API 获取仿真数据。

### data_processor

将仿真数据处理成前端需要的格式。

## 开发指南

在 `data_generator` 中编写仿真代码，在 `data_processor` 中处理数据。
