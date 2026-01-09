# N-1仿真向导重构文档

## 重构概述

本次重构将N-1仿真向导从静态步骤文件转变为基于配置的动态渲染系统，使其能够根据`.documents/n-1.md`中的定义自动生成界面。

## 架构变更

### 重构前架构
```
n1_wizard/
├── steps/
│   ├── single_mode/
│   │   ├── step_0.html      # 静态HTML文件
│   │   ├── step_0.js        # 静态JavaScript文件
│   │   ├── step_1.html
│   │   ├── step_1.js
│   │   └── ...              # 每个步骤都有独立的HTML和JS文件
│   └── batch_mode/
│       ├── step_0.html
│       ├── step_0.js
│       └── ...              # 批量模式的静态文件
├── wizard_template.html     # 模板文件（未充分利用）
└── wizard_template.js       # 模板脚本（未充分利用）
```

### 重构后架构
```
n1_wizard/
├── config/
│   └── wizard_config.json   # 统一的配置文件（新增）
├── shared/
│   ├── navigation.js        # 导航管理（保持不变）
│   ├── state_manager.js     # 状态管理（保持不变）
│   └── step_content_manager.js  # 步骤内容管理器（新增）
├── steps/
│   ├── single_mode/
│   │   └── .gitkeep         # 保留目录结构
│   └── batch_mode/
│       └── .gitkeep         # 保留目录结构
├── wizard_template.html     # 统一的模板文件（优化）
├── wizard_template.js       # 统一的脚本文件（删除旧的分步骤脚本）
├── wizard_entry.html        # 向导入口页面（保持不变）
├── n1_wizard.css            # 向导样式（保持不变）
└── README.md                # 本文档（新增）
```

## 核心组件

### 1. 配置文件 (`config/wizard_config.json`)

配置文件基于`n-1.md`文档定义了两种仿真模式（单次和批量）的步骤和组件：

```json
{
  "modes": {
    "single": {
      "name": "Model A: 单次 N-1 仿真",
      "steps": [
        {
          "id": "init_model",
          "title": "加载模型并初始化",
          "description": "加载并初始化电力系统模型",
          "executionStrategy": "auto",
          "component": "model_init",
          "nextAction": "auto"
        }
        // ... 更多步骤
      ]
    },
    "batch": {
      // 批量模式配置
    }
  },
  "components": {
    "model_init": {
      "type": "status_panel",
      "fields": [...]
    }
    // ... 更多组件类型
  }
}
```

#### 配置结构

**模式配置 (`modes`)**
- `name`: 模式名称
- `description`: 模式描述
- `steps`: 步骤数组
  - `id`: 步骤唯一标识
  - `title`: 步骤标题
  - `description`: 步骤描述
  - `executionStrategy`: 执行策略（auto/auto_wait_confirm/ask_execute）
  - `component`: 使用的组件类型
  - `nextAction`: 下一步操作类型

**组件配置 (`components`)**
- `type`: 组件类型（status_panel/table/execution/form/result等）
- `fields`: 字段定义（用于表单和表格）
- 其他特定于组件的配置

### 2. 步骤内容管理器 (`shared/step_content_manager.js`)

**核心功能：**
- 加载和解析配置文件
- 根据当前步骤配置动态渲染UI
- 管理不同组件类型的渲染逻辑
- 处理用户交互和导航
- **参数编辑和管理功能**
- **UI组件美化**

**主要方法：**
- `loadConfig()`: 加载配置文件
- `setMode(mode)`: 设置当前模式
- `setStep(stepIndex)`: 设置当前步骤
- `getCurrentStepConfig()`: 获取当前步骤配置
- `renderStepContent()`: 渲染步骤内容
- 各种`renderXxx()`方法：渲染特定类型的组件
- **新增**: `showParameterEditor()`: 显示参数编辑器
- **新增**: `validateParametersInEditor()`: 验证参数格式
- **新增**: `saveParametersFromEditor()`: 保存参数

**UI优化：**
- **参数检查面板**: 使用卡片式布局，图标+标题+描述的格式
- **JSON编辑器**: 添加专业工具栏，包含验证、格式化、清空按钮
- **语法高亮样式**: JSON编辑器使用深色背景，模拟语法高亮效果

**支持的组件类型：**
1. **status_panel**: 状态面板，显示初始化状态
2. **table**: 参数表格，显示和编辑配置
3. **execution**: 执行面板，显示执行进度和日志
4. **form**: 表单，用于参数输入
5. **result**: 结果查看器，显示仿真结果
6. **list**: 列表，显示流程模板
7. **explanation**: 说明组件，解释工具参数
8. **json_editor**: JSON编辑器，用于批量配置
9. **validation**: 验证面板，检查配置
10. **task_submission**: 任务提交面板

### 3. 统一模板 (`wizard_template.html`)

**主要变更：**
- 集成`step_content_manager.js`
- 移除动态加载分步骤脚本的逻辑
- 使用配置驱动的方式渲染内容
- 保持导航和状态管理不变
- **修复**: 优化按钮事件绑定时机，确保返回主页和帮助按钮正常工作

**页面初始化流程：**
1. 从URL参数提取模式和步骤索引
2. 初始化导航管理器
3. 设置内容管理器的模式和步骤
4. 等待配置加载完成
5. 根据配置渲染步骤标题、描述和内容
6. 渲染帮助对话框内容

## 执行策略

配置中定义了三种执行策略，对应`n-1.md`中的规范：

1. **auto (自动执行)**: 立即执行，无需用户确认
2. **auto_wait_confirm (自动执行+等待确认)**: 执行后等待用户确认或提供输入
3. **ask_execute (询问后执行)**: 先询问用户意见，根据回复决定是否执行

## 下一步操作类型

根据步骤的不同，定义了不同的下一步操作：

- `auto`: 自动执行，显示"下一步"按钮
- `confirm_modify`: 确认是否修改配置，显示"修改配置"和"确认无误"按钮
- `confirm_execute`: 确认是否执行操作，显示"取消"和"执行"按钮
- `confirm_config`: 确认配置是否正确，显示"修改配置"和"确认配置"按钮
- `confirm_count`: 确认批量次数，显示"确认次数"按钮
- `confirm_submit`: 确认提交任务，显示"取消"和"确认提交"按钮
- `confirm_template`: 确认流程模板，显示"调整模板"和"确认模板"按钮

## 优势

### 1. 可维护性
- 所有步骤定义集中在一个配置文件中
- 修改流程无需修改多个文件
- 新增步骤只需在配置中添加定义

### 2. 灵活性
- 支持动态添加新的组件类型
- 组件可复用，减少重复代码
- 配置驱动，易于扩展

### 3. 一致性
- 统一的UI风格和交互模式
- 统一的导航和状态管理
- 统一的错误处理和日志记录

### 4. 与文档同步
- 配置文件直接来源于`n-1.md`
- 确保界面实现与文档规范一致
- 便于验证实现是否符合规范

## 迁移指南

### 对于开发者

1. **修改步骤流程**：编辑`config/wizard_config.json`
2. **添加新组件类型**：
   - 在配置文件的`components`中添加新组件定义
   - 在`step_content_manager.js`中实现对应的`renderXxx()`方法
3. **自定义组件样式**：在`n1_wizard.css`中添加样式

### 对于用户

无需任何操作，界面功能和交互保持不变。

## 未来扩展

### 计划中的功能

1. **动态表单验证**：根据配置自动验证用户输入
2. **组件插件系统**：支持第三方组件注册
3. **配置版本管理**：支持多版本配置切换
4. **可视化配置编辑器**：图形化界面编辑配置文件
5. **步骤依赖关系**：支持步骤间的条件依赖
6. **并行步骤执行**：支持多个步骤同时执行

### 技术改进

1. **配置热更新**：无需刷新页面即可更新配置
2. **组件懒加载**：按需加载组件代码
3. **性能优化**：虚拟滚动处理大量数据
4. **响应式设计**：优化移动端体验

## 相关文件

- 配置文件：`frontend/pages/n1_wizard/config/wizard_config.json`
- 内容管理器：`frontend/pages/n1_wizard/shared/step_content_manager.js`
- 统一模板：`frontend/pages/n1_wizard/steps/wizard_template.html`
- 规范文档：`.documents/n-1.md`
- 入口页面：`frontend/pages/n1_wizard/wizard_entry.html`

## 注意事项

1. 修改配置文件后，需要刷新页面才能生效
2. 确保配置文件的JSON格式正确，否则会导致加载失败
3. 新增组件类型时，需要在`step_content_manager.js`中实现对应的渲染方法
4. 保持配置文件与`n-1.md`文档的同步更新
5. 生产环境建议对配置文件进行压缩和缓存优化

## 版本历史

- **v2.0.0** (2026-01-09): 初始重构版本，实现基于配置的动态渲染
