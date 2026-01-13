# 快速开始指南

## 前置要求

- Node.js >= 18
- Python >= 3.9
- npm 或 yarn

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd example_web_app
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 安装后端依赖

```bash
cd ../backend
pip install -r requirements.txt
```

### 4. 配置后端

创建 `backend/fastapi/.env` 文件：

```env
APP_NAME="Schema-Driven UI Backend"
APP_VERSION="1.0.0"
DEBUG=true
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CONFIG_PATH=../../frontend/src/data/wizard_config.json
MCP_ENABLED=true
```

## 启动项目

### 方式一：使用启动脚本（推荐）

**Windows:**
```bash
start_servers.bat
```

**Linux/Mac:**
```bash
chmod +x start_servers.sh
./start_servers.sh
```

### 方式二：分别启动

#### 启动后端服务器

**终端 1 - 启动 FastAPI:**
```bash
python -m backend.fastapi.main
```

**终端 2 - 启动 MCP:**
```bash
python -m backend.mcp.main
```

#### 启动前端

**终端 3 - 启动前端开发服务器:**
```bash
cd frontend
npm run dev
```

## 访问应用

- **前端应用**: http://localhost:3000
- **FastAPI API**: http://localhost:8000
- **MCP HTTP**: http://localhost:4445/mcp
- **API 文档**: http://localhost:8000/docs
- **MCP WebSocket**: ws://localhost:8765

## 测试 MCP 工具

运行测试脚本：

```bash
python test_mcp.py
```

## 配置 Claude Desktop

如果要在 Claude Desktop 中使用 MCP 工具，编辑 Claude Desktop 配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "schema-ui-backend": {
      "command": "python",
      "args": [
        "-m",
        "backend.mcp.main"
      ],
      "env": {
        "PYTHONPATH": "<项目绝对路径>/backend"
      }
    }
  }
}
```

## 使用示例

### 1. 基本流程

```python
# 1. 初始化向导
render_page(page_key="mode_selection")

# 2. 等待用户选择模式
event = await_event()
selected_mode = event.payload['value']

# 3. 渲染第一步
render_page(
  page_key=f"{selected_mode}_0",
  mode=selected_mode,
  step_index=0
)

# 4. 等待用户填写参数
event = await_event()
params = event.payload

# 5. 更新 UI
patch_ui({
  "state.runtime.status": "loading"
})

# 6. 执行业务逻辑
result = execute_business_logic(
  action_id="confirm_execute",
  mode=selected_mode,
  params=params
)

# 7. 显示结果
patch_ui({
  "state.runtime.status": "success",
  "state.runtime.result": result
})
```

### 2. 获取配置信息

```python
# 获取所有模式
modes = get_modes()

# 获取指定模式
mode = get_mode('single')

# 获取所有组件
components = get_components()

# 获取指定组件
component = get_component('parameter_table')
```

### 3. 会话管理

```python
# 获取会话状态
state = get_session_state()

# 清除会话状态
clear_session_state()

# 重新加载配置
reload_config()
```

## 常见问题

### 1. 前端无法连接到 MCP

**问题**: 前端显示 "✗ MCP 未连接"

**解决方案**:
- 确认 MCP 服务器已启动
- 检查 WebSocket 地址是否正确
- 查看浏览器控制台是否有错误

### 2. MCP 命令超时

**问题**: `await_event` 或其他命令超时

**解决方案**:
- 增加超时时间
- 检查网络连接
- 查看 MCP 服务器日志

### 3. Schema 渲染失败

**问题**: 前端无法渲染 Schema

**解决方案**:
- 检查返回的 Schema 格式是否正确
- 查看浏览器控制台的错误信息
- 使用 `get_wizard_config` 验证配置

### 4. Claude Desktop 无法连接 MCP

**问题**: Claude Desktop 中 MCP 工具不可用

**解决方案**:
- 确认配置文件路径正确
- 检查 PYTHONPATH 是否正确设置
- 重启 Claude Desktop
- 查看 Claude Desktop 日志

## 开发指南

### 添加新的 Block 类型

1. 在 `frontend/src/components/BlockRenderer.tsx` 中添加渲染逻辑
2. 更新 `frontend/src/types/schema.ts` 中的类型定义
3. 在配置文件中添加组件定义

### 添加新的 MCP 工具

1. 在 `backend/mcp/mcp_tools.py` 中添加工具函数
2. 使用 `@mcp.tool()` 装饰器
3. 重启 MCP 服务器

### 添加新的业务逻辑

1. 在 `backend/fastapi/services/agent.py` 中添加决策逻辑
2. 添加相应的事件处理
3. 更新配置文件

## 项目结构

```
example_web_app/
├── frontend/              # React 前端
│   ├── src/
│   │   ├── components/   # React 组件
│   │   ├── hooks/        # 自定义 Hooks
│   │   ├── types/        # TypeScript 类型
│   │   ├── utils/        # 工具函数
│   │   └── data/         # 配置数据
│   └── package.json
├── backend/              # Python 后端
│   ├── fastapi/          # FastAPI 应用
│   │   ├── api/          # API 路由
│   │   ├── services/     # 业务服务
│   │   ├── models.py     # 数据模型
│   │   ├── schemas.py    # Schema 生成器
│   │   └── main.py       # FastAPI 入口
│   ├── mcp/              # MCP 服务器
│   │   ├── mcp_tools.py  # MCP 工具定义
│   │   └── main.py       # MCP 服务器入口
│   └── requirements.txt
├── start_servers.bat     # Windows 启动脚本
├── start_servers.sh      # Linux/Mac 启动脚本
├── test_mcp.py          # MCP 测试脚本
├── ARCHITECTURE.md      # 架构文档
├── MCP_README.md        # MCP 使用指南
└── README.md            # 项目说明
```

## 下一步

- 阅读 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解架构设计
- 阅读 [MCP_README.md](./MCP_README.md) 了解 MCP 工具使用
- 查看 `frontend/src/data/wizard_config.json` 了解配置格式
- 浏览代码库了解更多实现细节

## 获取帮助

- 提交 Issue
- 查看文档
- 联系维护者
