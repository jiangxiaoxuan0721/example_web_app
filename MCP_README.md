# MCP 工具使用指南

## 概述

本项目实现了一个完整的 MCP (Model Context Protocol) 架构，允许外部 AI（如 Claude）通过 WebSocket 和 HTTP 与前端应用交互。

## 架构流程

```
1. AI → tool.render_page         AI调用渲染工具
2. MCP → schema:mount → Frontend  MCP挂载Schema到前端
3. Frontend → page:ready → MCP    前端通知MCP页面就绪
4. MCP → tool.await_event 返回    MCP等待事件并返回
5. AI 推理                         AI进行决策推理
6. AI → tool.patch_ui            AI调用补丁工具更新UI
7. MCP → schema:patch → Frontend  MCP打补丁到前端
```

## 启动服务器

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

**启动 FastAPI 服务器:**
```bash
python -m backend.fastapi.main
```

**启动 MCP WebSocket 服务器:**
```bash
python -m backend.mcp.main
```

## 服务器地址

- FastAPI API: http://localhost:8000
- MCP WebSocket: ws://localhost:8765
- MCP HTTP: http://localhost:4445/mcp
- API 文档: http://localhost:8000/docs

## MCP 工具列表

### 1. 页面渲染

#### `render_page`
渲染页面，返回 UISchema

**参数:**
- `page_key` (str, 必填): 页面键，如 "mode_selection", "single_0", "batch_0"
- `mode` (str, 可选): 模式 ID，如 "single", "batch"
- `step_index` (int, 可选): 步骤索引，默认为 0

**使用示例:**
```python
# 初始化向导
render_page(page_key="mode_selection")

# 选择模式后进入第一步
render_page(page_key="single_0", mode="single", step_index=0)

# 切换到下一步
render_page(page_key="single_1", mode="single", step_index=1)
```

### 2. UI 更新

#### `patch_ui`
打补丁到 UI，增量更新界面

**参数:**
- `patch` (Dict[str, Any], 必填): 补丁字典，键为 dot path，值为新值
- `page_key` (str, 可选): 页面键

**使用示例:**
```python
# 更新字段值
patch_ui({
  "state.params.speed": 150
})

# 更新多个值
patch_ui({
  "state.params.speed": 150,
  "state.params.distance": 100,
  "state.runtime.status": "running"
})
```

### 3. 事件等待

#### `await_event`
等待前端事件

**参数:**
- `timeout` (int, 可选): 超时时间（秒），默认 30 秒

**返回:**
- 前端事件数据

**使用示例:**
```python
# 等待用户操作
result = await_event()

# 带超时
result = await_event(timeout=60)
```

### 4. 配置管理

#### `get_wizard_config`
获取完整的 Wizard 配置

#### `get_modes`
获取所有模式

#### `get_mode`
获取指定模式的详细信息

#### `get_components`
获取所有组件定义

#### `get_component`
获取指定组件的详细信息

### 5. 会话管理

#### `get_session_state`
获取会话状态

#### `clear_session_state`
清除会话状态

#### `reload_config`
重新加载配置文件

### 6. 参数验证

#### `validate_params`
验证参数有效性

**参数:**
- `mode_id` (str): 模式 ID
- `step_index` (int): 步骤索引
- `params` (Dict[str, Any]): 要验证的参数

### 7. 事件处理

#### `process_event`
处理前端事件

**参数:**
- `event_type` (str): 事件类型
- `payload` (Dict[str, Any]): 事件载荷
- `page_key` (str, 可选): 页面键

### 8. 业务逻辑

#### `execute_business_logic`
执行业务逻辑

**参数:**
- `action_id` (str): 操作 ID
- `mode` (str): 模式 ID
- `params` (Dict[str, Any]): 操作参数

#### `save_session_params`
保存会话参数

**参数:**
- `mode` (str): 模式 ID
- `step_index` (int): 步骤索引
- `params` (Dict[str, Any]): 参数字典

### 9. 服务器信息

#### `get_server_info`
获取服务器信息

## 前端集成

### WebSocket 客户端

前端使用 `mcpClient` 与 MCP 服务器通信：

```typescript
import { mcpClient } from './utils/mcpClient';

// 连接到 MCP 服务器
await mcpClient.connect('ws://localhost:8765');

// 发送命令
const response = await mcpClient.sendCommand('render_page', {
  page_key: 'mode_selection'
});

// 发送事件
mcpClient.sendEvent('field_change', { fieldKey: 'speed', value: 150 });
```

### 使用 React Hooks

```typescript
import { useMCPConnection, useMCPCommand } from './hooks/useMCP';

function MyComponent() {
  const { isConnected, sendCommand, sendEvent } = useMCPConnection(true);
  const { sendCommand: mcpSendCommand, isLoading, error } = useMCPCommand();

  const handleButtonClick = async () => {
    const response = await mcpSendCommand('render_page', {
      page_key: 'single_0',
      mode: 'single',
      step_index: 0
    });
  };

  return (
    <div>
      <div>MCP 连接状态: {isConnected ? '已连接' : '未连接'}</div>
      <button onClick={handleButtonClick}>下一步</button>
    </div>
  );
}
```

## 完整使用流程示例

### 场景：N-1 仿真向导

```python
# 1. 初始化向导
render_page(page_key="mode_selection")

# 2. 等待用户选择模式
event = await_event(timeout=60)
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

# 5. 更新 UI（显示加载状态）
patch_ui({
  "state.runtime.status": "loading"
})

# 6. 执行业务逻辑
result = execute_business_logic(
  action_id="confirm_execute",
  mode=selected_mode,
  params=params
)

# 7. 更新 UI（显示结果）
patch_ui({
  "state.runtime.status": "success",
  "state.runtime.result": result
})
```

## 调试

### 查看 MCP 日志

MCP 服务器会输出详细的日志信息：

```
🚀 MCP Server 启动中...
🌐 WebSocket 服务器启动: ws://0.0.0.0:8765
⏳ 等待前端连接...
🔗 浏览器已连接: 127.0.0.1:xxxxx
📤 发送命令: render_page (ID: mcp_000001)
📥 收到响应: mcp_000001
🎉 收到前端事件: field_change
```

### 前端调试信息

前端页面会显示调试信息（生产环境应移除）：

```tsx
<div className="debug-info">
  <strong>调试信息：</strong>
  <pre>{JSON.stringify(schema.meta, null, 2)}</pre>
</div>
```

## 常见问题

### 1. MCP 未连接

**问题:** 前端显示 "✗ MCP 未连接"

**解决方案:**
- 确认 MCP 服务器已启动
- 检查 WebSocket 地址是否正确
- 查看浏览器控制台是否有错误

### 2. 命令超时

**问题:** `await_event` 或其他命令超时

**解决方案:**
- 增加超时时间
- 检查网络连接
- 查看 MCP 服务器日志

### 3. Schema 渲染失败

**问题:** 前端无法渲染 Schema

**解决方案:**
- 检查返回的 Schema 格式是否正确
- 查看浏览器控制台的错误信息
- 使用 `get_wizard_config` 验证配置

## 开发指南

### 添加新的 MCP 工具

1. 在 `backend/mcp/mcp_tools.py` 中添加工具函数：

```python
@mcp.tool()
async def my_tool(param1: str, param2: Optional[int] = 0) -> Dict[str, Any]:
    """
    工具描述
    """
    try:
        # 工具逻辑
        return {"success": True, "result": "..."}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

2. 重启 MCP 服务器

3. AI 就可以调用新工具了

### 添加新的前端事件

1. 在前端使用 `sendEvent` 发送事件：

```typescript
mcpClient.sendEvent('my_event_type', { key: 'value' });
```

2. 在后端 MCP 中使用 `await_event` 等待事件

## 参考资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [项目 README](./README.md)
