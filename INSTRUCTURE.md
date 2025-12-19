# 电力系统分析平台 - 项目说明

## 项目概述

这是一个基于Flask的电力系统分析Web应用，采用组件化前端架构，提供电力系统相关的分析功能。

## 项目结构

```
workspace\\example_web_app\\
├── app.py                           # Flask应用入口
├── config.py                        # 配置文件
├── INSTRUCTURE.md                   # 项目说明文档
├── backend/                         # 后端模块
│   ├── data_generator/              # 数据生成模块（CloudPSS仿真）
│   └── data_processor/              # 数据处理模块
├── frontend/                        # 前端资源
│   ├── main.css                     # 全局样式和CSS变量定义
│   ├── components/                  # 组件目录
│   │   ├── buttons/                 # 按钮组件
│   │   │   ├── buttons.css
│   │   │   └── buttons.js
│   │   ├── function_cards/          # 功能卡片组件
│   │   │   ├── function_cards.css
│   │   │   └── function_cards.js
│   │   ├── informations/            # 信息展示组件
│   │   │   ├── informations.css
│   │   │   └── informations.js
│   │   ├── kpi_cards/               # KPI卡片组件
│   │   │   ├── kpi_cards.css
│   │   │   └── kpi_cards.js
│   │   ├── tables/                  # 数据表格组件
│   │   │   ├── tables.css
│   │   │   └── tables.js
│   │   └── drawer/                  # 抽屉组件
│   │       ├── drawer.css
│   │       └── drawer.js
│   └── pages/                       # 页面模板
│       ├── index.html               # 主页
│       ├── index.css                # 主页样式
│       ├── batch_n_1/               # 批量N-1分析页面
│       │   ├── batch_n_1.html       # 页面模板
│       │   ├── batch_n_1.css        # 页面特定样式
│       │   └── batch_n_1.js         # 页面逻辑
│       └── not_support.html         # 不支持页面
└── output/                          # 数据输出目录
```

## 技术栈

- **后端**: Flask (Python)
- **前端**: 原生HTML/CSS/JavaScript (组件化架构)
- **样式**: CSS变量 + 组件化样式，深蓝-蓝-白配色方案，响应式设计
- **架构**: 模块化组件设计，支持主题切换

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

#### 核心组件

- **按钮组件 (buttons)**: 支持多种样式和交互效果
- **功能卡片 (function_cards)**: 响应式卡片布局，支持不同状态显示
- **信息组件 (informations)**: 信息面板、统计卡片、进度条等

#### 数据展示组件

- **KPI卡片 (kpi_cards)**: 关键性能指标展示，支持动画和多种布局
- **数据表格 (tables)**: 支持搜索、排序、分页、选择等功能
- **抽屉组件 (drawer)**: 侧边详情面板，支持多种尺寸和方向

### 页面功能

#### 批量N-1分析页面 (batch_n_1)

- **KPI看板**: 显示仿真总工况数、各类异常统计
- **数据表格**: 支持搜索、筛选、分页的数据展示
- **筛选功能**: 支持按异常类型筛选（电压越限、频率失稳、功角失稳）
- **详情抽屉**: 点击行查看详细分析报告，包括：
  - 故障场景定义
  - 关键稳定性指标
  - 仿真波形分析
  - 原始数据文件下载

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
   - 本地访问: <http://127.0.0.1:50890>
   - 网络访问: <http://198.18.0.1:50890>

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

### 组件化开发

#### 创建新组件

1. 在 `frontend/components/` 下创建新目录
2. 创建对应的 `.css` 和 `.js` 文件
3. 遵循组件命名规范和API设计

#### 使用组件

1. 在页面HTML中引入组件CSS和JS文件
2. 按照组件API文档使用组件
3. 通过CSS变量自定义主题

#### 组件示例

**KPI卡片组件使用:**

```javascript
const kpiCards = new KPICards('container-id', {
    layout: 'default',
    animated: true
});

const cards = [
    KPICards.createCard('total', '总数', 100, {
        icon: '⚡',
        type: 'primary'
    })
];
kpiCards.setCards(cards);
```

**数据表格组件使用:**

```javascript
const dataTable = new DataTable('table-container', {
    columns: [
        { key: 'id', title: 'ID', width: '20%' },
        { key: 'name', title: '名称', width: '30%' }
    ],
    data: [],
    searchable: true,
    paginated: true,
    pageSize: 10
});
```

**抽屉组件使用:**

```javascript
const drawer = drawerManager.create('drawer-id', {
    title: '详细信息',
    size: 'large',
    content: '抽屉内容'
});
drawer.open();
```

### 添加新功能卡片

1. 在 `frontend/components/function_cards/function_cards.js` 中的 `cards` 数组添加新卡片
2. 根据需要添加对应的CSS样式
3. 实现相应的后端API路由

### 后端开发

1. 在 `backend/data_generator/` 中编写CloudPSS仿真代码
2. 在 `backend/data_processor/` 中处理数据
3. 在 `app.py` 中添加API路由

## 设计原则

1. **模块化**: 每个组件独立，职责单一
2. **响应式**: 适配不同屏幕尺寸
3. **一致性**: 统一的配色和交互风格
4. **可维护性**: 清晰的代码结构和注释
5. **可复用性**: 组件可在不同页面中重复使用
6. **主题化**: 通过CSS变量支持主题定制

## CSS变量系统

### 全局变量定义 (main.css)

```css
:root {
    /* 主色调 */
    --primary-color: #1890ff;
    --secondary-color: #40a9ff;
    --success-color: #52c41a;
    --warning-color: #faad14;
    --danger-color: #f5222d;
    
    /* 语义化颜色 */
    --text-main: #333;
    --text-secondary: #666;
    --text-disabled: #999;
    --border-color: #e8e8e8;
    --bg-color: #f0f2f5;
    --card-bg: #ffffff;
}
```

## 部署说明

- 开发环境使用Flask内置服务器
- 生产环境建议使用WSGI服务器（如Gunicorn）
- 确保端口50890可被外部访问

## 注意事项

1. 修改配置文件时注意安全性
2. 新增功能时保持组件化架构
3. 遵循现有的命名规范和代码风格
4. 测试时使用外部IP地址确保可访问性
5. 组件开发时注意性能优化和浏览器兼容性
6. 使用CSS变量时注意命名规范和作用域

## 更新日志

### v2.0.0 (最新)

- 完成组件化架构重构
- 新增KPI卡片、数据表格、抽屉组件
- 实现批量N-1分析页面
- 添加CSS变量主题系统
- 优化响应式设计和用户体验

### v1.0.0

- 基础Flask应用框架
- 主页功能卡片展示
- 基础组件系统
