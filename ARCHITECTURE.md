# Schema-Driven UI 架构设计文档

## 1. 概述

本项目实现了一个基于 Schema 驱动的现代化 Web 应用架构，采用 MCP (Model Context Protocol) 实现了 AI、后端和前端之间的无缝交互。

### 核心设计理念

- **前端零业务逻辑**: 前端只负责渲染 UISchema 和发射事件
- **后端唯一决策者**: 后端 Agent 处理所有业务逻辑，返回 Schema 或 Patch
- **AI 驱动**: 外部 AI（如 Claude）通过 MCP 工具控制整个应用流程

## 2. 系统架构

### 2.1 整体架构图

```sh
┌─────────────────────────────────────────────────────────────┐
│                         外部 AI                             │
│                     (Claude, GPT-4 等)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ MCP 协议
                         │ HTTP/WebSocket
                         ▼
┌──────────────────────────────────────────────────────────┐
│                     MCP 服务器层                          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           MCP WebSocket 服务器                      │  │
│  │           (ws://localhost:8765)                     │  │
│  │  - 管理前端 WebSocket 连接                           │  │
│  │  - 转发命令到前端                                    │  │
│  │  - 接收前端事件                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           MCP HTTP 服务器                            │  │
│  │           (http://localhost:4445/mcp)               │  │
│  │  - 暴露 MCP 工具给 AI                                │  │
│  │  - 支持流式 HTTP 传输                                │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────┬──────────────────────────────────┘
                         │
                         │ Python 调用
                         ▼
┌───────────────────────────────────────────────────────────┐
│                   业务逻辑层 (FastAPI)                     │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           Agent 决策服务                             │  │
│  │  - 处理前端事件                                      │  │
│  │  - 执行业务逻辑                                      │  │
│  │  - 生成 Schema 或 Patch                              │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           Schema 生成器                              │  │
│  │  - 生成模式选择 Schema                               │  │
│  │  - 生成步骤 Schema                                   │  │
│  │  - 配置管理                                          │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────┬──────────────────────────────────┘
                         │
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      配置层                                  │
│              wizard_config.json                              │
│  - 模式定义 (modes)                                         │
│  - 组件定义 (components)                                     │
│  - 步骤配置 (steps)                                         │
└─────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│                      前端层 (React)                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           MCP WebSocket 客户端                       │  │
│  │  - 连接到 MCP 服务器                                 │  │
│  │  - 发送 UI 事件                                      │  │
│  │  - 接收 Schema/Patch                                │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           Schema 渲染器                              │  │
│  │  - 根据 UISchema 渲染 UI                             │  │
│  │  - 支持多种 Block 类型                               │  │
│  │  - 应用 Patch 增量更新                               │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           事件系统                                   │  │
│  │  - 发射 UI 事件                                      │  │
│  │  - 监听 Schema/Patch 更新                            │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

### 2.2 通信流程

```sh
1. AI → tool.render_page
   AI 调用 MCP 工具请求渲染页面
   
2. MCP → schema:mount → Frontend
   MCP WebSocket 转发 Schema 到前端
   
3. Frontend → page:ready → MCP
   前端通知 MCP 页面已准备就绪
   
4. MCP → tool.await_event 返回
   MCP 等待前端用户操作事件并返回给 AI
   
5. AI 推理
   AI 根据事件进行推理决策
   
6. AI → tool.patch_ui
   AI 调用 MCP 工具更新 UI
   
7. MCP → schema:patch → Frontend
   MCP WebSocket 转发 Patch 到前端
```

## 3. 核心组件

### 3.1 MCP 工具层

**文件位置**: `backend/mcp/mcp_tools.py`

提供 17 个 MCP 工具，分为以下几类：

#### 3.1.1 页面渲染工具

- `render_page`: 渲染页面，返回 UISchema

#### 3.1.2 UI 更新工具

- `patch_ui`: 打补丁到 UI，增量更新界面

#### 3.1.3 事件等待工具

- `await_event`: 等待前端事件

#### 3.1.4 配置管理工具

- `get_wizard_config`: 获取完整配置
- `get_modes`: 获取所有模式
- `get_mode`: 获取指定模式
- `get_components`: 获取所有组件
- `get_component`: 获取指定组件

#### 3.1.5 会话管理工具

- `get_session_state`: 获取会话状态
- `clear_session_state`: 清除会话状态
- `reload_config`: 重新加载配置

#### 3.1.6 参数验证工具

- `validate_params`: 验证参数有效性

#### 3.1.7 事件处理工具

- `process_event`: 处理前端事件

#### 3.1.8 业务逻辑工具

- `execute_business_logic`: 执行业务逻辑
- `save_session_params`: 保存会话参数

#### 3.1.9 服务器信息工具

- `get_server_info`: 获取服务器信息

### 3.2 MCP 服务器

**文件位置**: `backend/mcp/main.py`

提供两个服务器：

#### 3.2.1 WebSocket 服务器

- 端口: 8765
- 协议: WebSocket
- 功能:
  - 管理前端连接
  - 转发命令到前端
  - 接收前端事件

#### 3.2.2 MCP HTTP 服务器

- 端口: 4445
- 协议: SSE (Server-Sent Events)
- 功能:
  - 暴露 MCP 工具给 AI
  - 支持流式 HTTP 传输

### 3.3 FastAPI 后端

**文件位置**: `backend/fastapi/`

#### 3.3.1 API 路由

- `/api/wizard/*`: Wizard 配置 API
- `/api/events`: 事件处理 API
- `/session/state`: 会话状态 API

#### 3.3.2 Agent 服务

**文件位置**: `backend/fastapi/services/agent.py`

- 处理前端事件
- 执行业务逻辑
- 生成 Schema 或 Patch

#### 3.3.3 Schema 生成器

**文件位置**: `backend/fastapi/schemas.py`

- 生成模式选择 Schema
- 生成步骤 Schema
- 生成 Block 配置

### 3.4 前端层

**文件位置**: `frontend/src/`

#### 3.4.1 MCP 客户端

**文件**: `utils/mcpClient.ts`

- WebSocket 连接管理
- 命令发送和响应处理
- 事件发送

#### 3.4.2 React Hooks

**文件**: `hooks/useMCP.ts`

- `useMCPConnection`: MCP 连接管理
- `useMCPEvent`: MCP 事件监听
- `useMCPCommand`: MCP 命令发送

#### 3.4.3 Schema 渲染器

**文件**: `components/SchemaRenderer.tsx`, `components/BlockRenderer.tsx`

- 根据 UISchema 渲染 UI
- 支持多种 Block 类型
- 应用 Patch 增量更新

## 4. 数据模型

### 4.1 UISchema

```typescript
interface UISchema {
  meta: {
    pageKey: string;        // 页面键
    step: {
      current: number;      // 当前步骤
      total: number;        // 总步骤数
    };
    status: string;         // 状态
    schemaVersion: string;   // Schema 版本
  };
  state: {
    params: Record<string, any>;  // 参数
    runtime: Record<string, any>; // 运行时信息
  };
  layout: {
    type: string;           // 布局类型
  };
  blocks: Block[];          // Block 列表
  actions: Action[];        // 操作列表
}
```

### 4.2 UIPatch

```typescript
type UIPatch = Record<string, any>;
// 键为 dot path，值为新值
// 示例: { "state.params.speed": 150 }
```

### 4.3 UIEvent

```typescript
interface UIEvent {
  type: string;            // 事件类型
  payload: {
    actionId?: string;     // 操作 ID
    fieldKey?: string;     // 字段键
    value?: any;           // 字段值
    mode?: string;         // 模式
    stepIndex?: number;    // 步骤索引
    params?: Record<string, any>; // 参数
  };
  pageKey?: string;        // 页面键
}
```

## 5. 关键设计模式

### 5.1 Schema 驱动模式

前端完全依赖 UISchema 进行渲染，没有任何业务逻辑：

```typescript
// 前端代码示例
<SchemaRenderer schema={schema} />
```

### 5.2 事件驱动模式

前后端通过事件通信，完全解耦：

```typescript
// 前端发射事件
mcpClient.sendEvent('field_change', { fieldKey: 'speed', value: 150 });

// 后端处理事件
await_event() // MCP 工具等待事件
```

### 5.3 Patch 增量更新模式

使用 Patch 进行增量更新，避免完整替换：

```typescript
// AI 调用
patch_ui({ "state.params.speed": 150 });

// 前端应用
applySchemaPatch({ "state.params.speed": 150 });
```

### 5.4 单一决策者模式

后端 Agent 是唯一的决策者，前端不包含任何业务逻辑：

```python
# Agent 决策
class AgentService:
    def process_event(self, event: UIEvent) -> Dict[str, Any]:
        # 处理事件，返回 Schema 或 Patch
        pass
```

## 6. 技术栈

### 6.1 前端

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **路由**: React Router
- **通信**: WebSocket

### 6.2 后端

- **框架**: FastAPI
- **数据验证**: Pydantic
- **MCP 协议**: fastmcp
- **WebSocket**: websockets
- **服务器**: Uvicorn

### 6.3 MCP

- **协议**: Model Context Protocol
- **传输**: SSE + WebSocket
- **工具**: FastMCP

## 7. 部署架构

### 7.1 开发环境

```sh
前端 (localhost:3000)
  ↓ WebSocket
MCP WebSocket Server (localhost:8765)
  ↓
MCP Tools / Agent Service
  ↓ HTTP
FastAPI Server (localhost:8000)
```

### 7.2 生产环境

```sh
负载均衡器
  ├─ 前端服务器集群
  │  ↓ WebSocket
  ├─ MCP WebSocket 服务器集群
  │  ↓
  ├─ FastAPI 服务器集群
  │  ↓
  └─ 数据库 / 缓存
```

## 8. 扩展性设计

### 8.1 添加新的 Block 类型

1. 在前端 `BlockRenderer.tsx` 添加渲染逻辑
2. 更新类型定义 `schema.ts`
3. 在配置文件中定义组件

### 8.2 添加新的 MCP 工具

1. 在 `mcp_tools.py` 添加工具函数
2. 使用 `@mcp.tool()` 装饰器
3. 重启 MCP 服务器

### 8.3 添加新的业务逻辑

1. 在 `agent.py` 添加决策逻辑
2. 添加相应的事件处理
3. 更新配置文件

## 9. 安全性考虑

### 9.1 输入验证

- 使用 Pydantic 验证所有输入
- 前端类型检查

### 9.2 CORS 配置

- 配置允许的前端域名
- 禁止未授权访问

### 9.3 会话管理

- 使用会话状态跟踪
- 支持会话清除

### 9.4 错误处理

- 全局异常捕获
- 详细的错误日志

## 10. 性能优化

### 10.1 前端优化

- 使用 React.memo 避免不必要的重渲染
- Patch 增量更新减少数据传输

### 10.2 后端优化

- 配置缓存
- 异步处理

### 10.3 WebSocket 优化

- 连接池管理
- 消息压缩

## 11. 监控和调试

### 11.1 日志系统

- 结构化日志
- 不同级别日志

### 11.2 性能监控

- 请求耗时统计
- WebSocket 连接状态

### 11.3 调试工具

- 前端调试信息显示
- 后端 API 文档

## 12. 未来规划

### 12.1 功能扩展

- 支持更多 Block 类型
- 支持复杂表单验证
- 支持动态配置加载

### 12.2 性能提升

- 实现配置热更新
- 优化 WebSocket 性能
- 添加缓存层

### 12.3 开发体验

- 完善 TypeScript 类型定义
- 提供开发工具
- 添加单元测试

## 13. 参考资料

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [React 文档](https://react.dev/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [MCP 协议](https://modelcontextprotocol.io/)
