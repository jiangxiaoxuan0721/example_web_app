# Agent Programmable UI Runtime

基于 Schema 驱动的 UI 运行时系统，通过 MCP (Model Context Protocol) 工具让 AI Agent 动态构建和修改用户界面。

## 快速开始

### 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 启动服务

```bash
# 后端 (终端 1)
cd backend
uvicorn backend.fastapi.main:app --host 0.0.0.0 --port 8001 --reload

# 前端 (终端 2)
cd frontend
npm run dev

# MCP 服务 (终端 3，可选)
cd backend/mcp
python tools.py
```

访问 `http://localhost:5173`

## 系统架构

```
用户操作 → 前端渲染 → WebSocket → 后端处理 → MCP工具 → Schema更新 → 前端更新
```

### 后端

- **FastAPI** - REST API 和 WebSocket 服务
- **SchemaManager** - 管理所有 UI Schema 实例
- **InstanceService** - 处理实例创建/删除/更新
- **PatchHistoryManager** - 记录 Patch 操作历史

### 前端

- **React 18** + **Vite** - UI 框架
- **Zustand** - 状态管理
- **Immer** - 不可变数据更新

## 默认实例

启动后包含一个 `demo` 实例，展示所有功能：
- 计数器（increment/decrement）
- 动态列表（append_to_list）
- 可编辑表格
- 选项组件
- 图片组件
- Grid/Tabs/Accordion 布局
- 块导航

## MCP 工具

### `patch_ui_state`

应用 Patch 修改 UI，包括创建/删除实例、更新状态等。

**创建实例**:
```json
{
  "instance_name": "__CREATE__",
  "new_instance_name": "my_app",
  "patches": [
    {"op": "set", "path": "page_key", "value": "my_app"},
    {"op": "set", "path": "state", "value": {"params": {}, "runtime": {}}},
    {"op": "set", "path": "blocks", "value": []},
    {"op": "set", "path": "actions", "value": []}
  ]
}
```

### 其他工具

- `get_schema` - 获取 Schema
- `list_instances` - 列出所有实例
- `access_instance` - 激活实例
- `validate_completion` - 验证完成条件

## 核心 Patch 操作

| 操作 | 路径 | 说明 |
|------|------|------|
| `set` | 任意 | 设置值 |
| `add` | 列表 | 添加元素 |
| `remove` | 列表 | 移除元素 |
| `append_to_list` | 列表 | 追加元素 |
| `prepend_to_list` | 列表 | 前置元素 |
| `update_list_item` | 列表索引 | 更新元素 |
| `remove_last` | 列表 | 移除最后一个 |
| `merge` | 对象 | 合并对象 |
| `increment` | 数字 | 自增 |
| `decrement` | 数字 | 自减 |
| `toggle` | 布尔 | 切换 |

## 字段类型

- **基础**: `text`, `number`, `textarea`, `checkbox`, `json`
- **选择**: `select`, `radio`, `multiselect`
- **日期**: `date`, `datetime`
- **富文本**: `html`, `file`
- **高级**: `table`, `image`, `tag`, `progress`, `badge`, `modal`, `component`

## 布局类型

- `single` - 单列布局
- `grid` - 网格布局
- `tabs` - 标签页布局
- `accordion` - 手风琴布局

## 配置

### Claude Desktop

```json
{
  "mcpServers": {
    "ui-patch-server": {
      "command": "python",
      "args": ["/path/to/project/backend/mcp/tools.py"],
      "env": {
        "PYTHONPATH": "/path/to/project"
      }
    }
  }
}
```

### Cline (VS Code)

```yaml
mcpServers:
  ui-patch-server:
    command: python
    args: ["./backend/mcp/tools.py"]
    env:
      PYTHONPATH: ./
```

## 文档

详细文档见 [docs/](docs/)：

- [Schema Guide](docs/schema-guide.md) - UI Schema 结构
- [Tools Reference](docs/tools-reference.md) - MCP 工具文档
- [Field Types](docs/field-types.md) - 字段类型详解
- [Template Syntax](docs/template-syntax.md) - 模板语法
- [Layout Guide](docs/layout-guide.md) - 布局系统

---

Built with FastAPI, React, and FastMCP
