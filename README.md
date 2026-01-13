# Schema-Driven UI 项目

基于 Schema 驱动架构的现代化 Web 应用，采用 React + TypeScript + FastAPI 技术栈，支持 MCP (Model Context Protocol) 集成。

## 🎯 项目概述

本项目实现了一个完整的 Schema 驱动 UI 架构，其中：

- **前端**：零业务逻辑，只负责渲染 UISchema 和发射事件
- **后端**：唯一决策者，通过 Agent 逻辑返回 Schema 或 Patch
- **MCP 工具**：支持外部 AI（如 Claude）直接控制应用，实现 AI 驱动的交互流程

### 核心特性

✨ **AI 驱动**: 通过 MCP 协议，AI 可以直接调用工具控制整个应用流程  
🎨 **Schema 驱动**: 前端完全由 Schema 驱动，零业务逻辑  
🔄 **事件驱动**: 前后端通过事件通信，完全解耦  
⚡ **Patch 增量更新**: 使用 Patch 机制进行高效 UI 更新  
🔌 **MCP 集成**: 完整的 MCP 服务器实现，支持 17 个工具

## 📁 项目结构

```bash
example_web_app/
├── frontend/              # React + TypeScript 前端
│   ├── src/             # 源代码
│   │   ├── App.tsx      # 主应用
│   │   ├── main.tsx     # 入口文件
│   │   ├── components/  # 组件
│   │   ├── hooks/       # 自定义 Hooks (useEvent, useMCP)
│   │   ├── types/       # TypeScript 类型定义
│   │   ├── utils/       # 工具函数 (mcpClient)
│   │   └── data/        # 配置数据
│   ├── package.json     # 依赖配置
│   ├── vite.config.ts   # Vite 配置
│   └── tsconfig.json    # TypeScript 配置
│
├── backend/             # FastAPI 后端
│   ├── fastapi/         # FastAPI 应用
│   │   ├── main.py      # FastAPI 入口
│   │   ├── config.py    # 配置管理
│   │   ├── models.py    # Pydantic 模型
│   │   ├── schemas.py   # Schema 生成器
│   │   ├── api/         # API 路由
│   │   └── services/    # 业务服务 (Agent)
│   ├── mcp/             # MCP 服务器
│   │   ├── mcp_tools.py # MCP 工具定义 (17个工具)
│   │   └── main.py      # MCP 服务器入口
│   └── requirements.txt # Python 依赖
│
├── start_servers.bat     # Windows 启动脚本
├── start_servers.sh     # Linux/Mac 启动脚本
├── test_mcp.py         # MCP 测试脚本
├── ARCHITECTURE.md     # 架构设计文档
├── MCP_README.md       # MCP 使用指南
├── QUICKSTART.md       # 快速开始指南
└── README.md           # 项目说明
```

## 🚀 快速开始

### 前提条件

- Node.js >= 18
- Python >= 3.9
- npm 或 yarn

### 安装依赖

```bash
# 安装前端依赖
cd frontend
npm install

# 安装后端依赖
cd ../backend
pip install -r requirements.txt
```

### 启动项目

#### 启动前端

```bash
cd frontend
npm run dev
```

前端将在 `http://localhost:3000` 启动。

#### 启动后端

**方式一：使用启动脚本（推荐）**

```bash
# Windows
start_servers.bat

# Linux/Mac
chmod +x start_servers.sh
./start_servers.sh
```

这将同时启动：
- FastAPI 服务器 (http://localhost:8000)
- MCP WebSocket 服务器 (ws://localhost:8765)
- MCP HTTP 服务器 (http://localhost:4445/mcp)

**方式二：分别启动**

启动 FastAPI：
```bash
python -m backend.fastapi.main
```

启动 MCP：
```bash
python -m backend.mcp.main
```

### 访问应用

- **前端应用**：<http://localhost:3000>
- **FastAPI API**：<http://localhost:8000>
- **MCP WebSocket**：<ws://localhost:8765>
- **MCP HTTP**：<http://localhost:4445/mcp>
- **API 文档**：<http://localhost:8000/docs>
- **ReDoc**：<http://localhost:8000/redoc>

## 🎯 核心特性

### 1. Schema 驱动架构

- **单一数据源**：UISchema 是 UI 的唯一真相来源
- **声明式 UI**：前端根据 Schema 自动渲染
- **零业务逻辑**：前端不包含任何业务决策

### 2. Patch 机制

- **增量更新**：通过 Patch 更新状态，避免完整替换
- **点路径导航**：使用 dot path 访问嵌套状态
- **高效更新**：只更新变化的部分

### 3. 事件驱动

- **前后端解耦**：通过事件通信
- **Agent 决策**：后端 Agent 处理所有业务逻辑
- **灵活扩展**：易于添加新的事件类型

### 4. MCP 支持

- **17 个工具**：提供完整的 MCP 工具集
  - 页面渲染工具 (render_page, patch_ui)
  - 事件等待工具 (await_event)
  - 配置管理工具 (get_wizard_config, get_modes, get_components)
  - 会话管理工具 (get_session_state, clear_session_state)
  - 业务逻辑工具 (execute_business_logic, process_event)
- **外部 AI 集成**：支持 Claude 等 AI 助手调用
- **双接口**：HTTP API + MCP 工具
- **WebSocket 通信**：前端通过 WebSocket 与 MCP 服务器通信

## 📊 技术栈

### 前端

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **路由**: React Router
- **状态管理**: 自定义 Hooks（useSchemaState, useMCP）
- **通信**: WebSocket, HTTP

### 后端

- **框架**: FastAPI
- **数据验证**: Pydantic
- **MCP 协议**: fastmcp
- **WebSocket**: websockets
- **服务器**: Uvicorn

## 📝 配置

### 前端配置

前端通过 API 从后端获取配置，无需前端配置文件。

### 后端配置

创建 `backend/fastapi/.env` 文件：

```env
APP_NAME="Schema-Driven UI Backend"
APP_VERSION="1.0.0"
DEBUG=true
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CONFIG_PATH=../../src/data/wizard_config.json
MCP_ENABLED=true
```

## 🔌 API 接口

### Wizard 配置 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/wizard/config` | 获取配置 |
| GET | `/api/wizard/init` | 初始化向导 |
| GET | `/api/wizard/step/{mode}/{step_index}` | 获取步骤 Schema |

### 事件处理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/events` | 处理 UI 事件 |
| GET | `/api/session/state` | 获取会话状态 |
| DELETE | `/api/session/state` | 清除会话状态 |

详细 API 文档请查看 [BACKEND_API.md](docs/BACKEND_API.md)。

## 🔧 MCP 工具

### 配置管理（5 个工具）

- `get_wizard_config` - 获取 Wizard 配置
- `get_modes` - 获取所有模式
- `get_mode(mode_id)` - 获取指定模式
- `get_components` - 获取所有组件
- `get_component(component_id)` - 获取指定组件

### Schema 生成（2 个工具）

- `generate_mode_selection_schema` - 生成模式选择 Schema
- `generate_step_schema(mode_id, step_index, params?)` - 生成步骤 Schema

### 事件处理（4 个工具）

- `process_event(event_type, payload, page_key?)` - 处理 UI 事件
- `handle_field_change(field_key, value, page_key?)` - 处理字段变化
- `handle_action_click(action_id, mode?, step_index?, params?, page_key?)` - 处理操作点击
- `handle_select_mode(mode, page_key?)` - 处理模式选择

### 业务逻辑（4 个工具）

- `execute_business_logic(action_id, mode, params)` - 执行业务逻辑
- `save_session_params(mode, step_index, params)` - 保存会话参数
- `get_session_state` - 获取会话状态
- `clear_session_state` - 清除会话状态

### 验证和辅助（3 个工具）

- `validate_params(mode_id, step_index, params)` - 验证参数
- `reload_config` - 重新加载配置
- `get_server_info` - 获取服务器信息

详细 MCP 指南请查看 [MCP_GUIDE.md](docs/MCP_GUIDE.md)。

## 🧪 测试

### MCP 工具测试

运行 MCP 工具测试脚本：

```bash
python test_mcp.py
```

这将测试所有 MCP 工具的基本功能。

## 📚 文档

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 完整的架构设计文档
- **[MCP_README.md](./MCP_README.md)** - MCP 工具使用指南
- **[QUICKSTART.md](./QUICKSTART.md)** - 快速开始指南

## 🎨 开发指南

### 添加新的 Block 类型

1. 在 `frontend/src/components/BlockRenderer.tsx` 中添加渲染逻辑
2. 更新 `frontend/src/types/schema.ts` 中的类型定义
3. 在配置文件中添加组件定义

### 添加新的 MCP 工具

1. 在 `backend/mcp/mcp_tools.py` 中添加工具函数
2. 使用 `@mcp.tool()` 装饰器
3. 重启 MCP 服务器
4. 更新 [MCP_README.md](./MCP_README.md) 文档

### 添加新的业务逻辑

1. 在 `backend/fastapi/services/agent.py` 中添加决策逻辑
2. 添加相应的事件处理
3. 更新配置文件

## 🌟 架构亮点

### 1. 完全解耦

- 前端只负责渲染和发射事件
- 后端唯一决策者，返回 Schema 或 Patch
- 外部 Agent 可直接调用后端工具

### 2. 类型安全

- 前端：TypeScript 完整类型定义
- 后端：Pydantic 数据验证
- API：自动生成文档和类型

### 3. 可扩展性

- 新增 Block 类型无需修改前端逻辑
- 新增决策逻辑只需扩展 Agent
- 新增 MCP 工具通过装饰器即可

### 4. 开发体验

- 热更新（HMR）
- 自动 API 文档
- 完整的测试覆盖

## 🐛 常见问题

### 前端无法连接到 MCP

1. 确保 MCP 服务器已启动：`python -m backend.mcp.main`
2. 检查 WebSocket 地址是否正确
3. 查看浏览器控制台是否有错误

### MCP 命令超时

1. 增加超时时间
2. 检查网络连接
3. 查看 MCP 服务器日志

### Schema 渲染失败

1. 检查返回的 Schema 格式是否正确
2. 查看浏览器控制台的错误信息
3. 使用 `get_wizard_config` 验证配置

### Claude Desktop 无法连接 MCP

1. 确认配置文件路径正确
2. 检查 PYTHONPATH 是否正确设置
3. 重启 Claude Desktop
4. 查看 [QUICKSTART.md](./QUICKSTART.md) 中的配置说明

## 📄 License

MIT

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题，请通过以下方式联系：

- 提交 Issue
- 发送邮件
