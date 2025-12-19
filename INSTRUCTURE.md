# 电力系统分析平台 - 项目说明

## 项目概述

这是一个基于Flask的电力系统分析Web应用，采用组件化前端架构，提供电力系统相关的分析功能。

## 项目结构

```
workspace\example_web_app\
├── app.py                           # Flask应用入口
├── config.py                        # 配置文件
├── INSTRUCTURE.md                   # 项目说明文档
├── backend/                         # 后端模块
│   ├── data_generator/              # 数据生成模块（CloudPSS仿真）
│   └── data_processor/              # 数据处理模块
├── frontend/                        # 前端资源
│   ├── main.css                     # 全局样式
│   ├── components/                  # 组件目录
│   │   ├── buttons/                 # 按钮组件
│   │   │   ├── buttons.css
│   │   │   └── buttons.js
│   │   ├── function_cards/          # 功能卡片组件
│   │   │   ├── function_cards.css
│   │   │   └── function_cards.js
│   │   └── informations/            # 信息展示组件
│   │       ├── informations.css
│   │       └── informations.js
│   └── pages/                       # 页面模板
│       ├── index.html               # 主页
│       ├── index.css                # 主页样式
│       └── not_support.html         # 不支持页面
└── output/                          # 数据输出目录
```

## 技术栈

- **后端**: Flask (Python)
- **前端**: 原生HTML/CSS/JavaScript (组件化架构)
- **样式**: 深蓝-蓝-白配色方案，响应式设计
- **架构**: 模块化组件设计

## 功能特性

### 主页功能卡片

当前包含6个功能卡片：

1. **N-1分析** - 电力系统N-1安全分析（可用）
2. **潮流计算** - 电力系统潮流计算分析（可用）
3. **短路计算** - 短路电流计算（开发中）
4. **暂态稳定** - 暂态稳定性分析（开发中）
5. **电压稳定** - 电压稳定性分析（即将推出）
6. **优化调度** - 优化调度功能（即将推出）

### 组件系统

- **按钮组件**: 支持多种样式和交互效果
- **功能卡片**: 响应式卡片布局，支持不同状态显示
- **信息组件**: 信息面板、统计卡片、进度条等

## 启动方法

1. **安装依赖**
   ```bash
   pip install flask
   ```

2. **启动应用**
   ```bash
   python app.py
   ```

3. **访问应用**
   - 本地访问: http://127.0.0.1:50890
   - 网络访问: http://198.18.0.1:50890

## 配置说明

### config.py 配置

```python
class Config:
    # 目录配置
    BACKEND_DIR = os.path.join(os.path.dirname(__file__), 'backend')
    FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'frontend', 'pages')
    STATIC_DIR = os.path.join(os.path.dirname(__file__), 'frontend')

    # 服务器配置
    SERVER_HOST = '0.0.0.0'  # 允许外部访问
    SERVER_PORT = 50890
    DEBUG = True

    # CloudPSS配置
    CLOUDPSS = {
        "TOKEN": "<CloudPSS Token>",
        "API_URL": "https://cloudpss.net/"
    }
```

## 开发指南

### 添加新功能卡片

1. 在 `frontend/components/function_cards/function_cards.js` 中的 `cards` 数组添加新卡片
2. 根据需要添加对应的CSS样式
3. 实现相应的后端API路由

### 创建新组件

1. 在 `frontend/components/` 下创建新目录
2. 创建对应的 `.css` 和 `.js` 文件
3. 在页面中引入相关文件

### 后端开发

1. 在 `backend/data_generator/` 中编写CloudPSS仿真代码
2. 在 `backend/data_processor/` 中处理数据
3. 在 `app.py` 中添加API路由

## 设计原则

1. **模块化**: 每个组件独立，职责单一
2. **响应式**: 适配不同屏幕尺寸
3. **一致性**: 统一的配色和交互风格
4. **可维护性**: 清晰的代码结构和注释

## 部署说明

- 开发环境使用Flask内置服务器
- 生产环境建议使用WSGI服务器（如Gunicorn）
- 确保端口50890可被外部访问

## 注意事项

1. 修改配置文件时注意安全性
2. 新增功能时保持组件化架构
3. 遵循现有的命名规范和代码风格
4. 测试时使用外部IP地址确保可访问性