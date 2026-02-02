# WebSocket 服务模块

## 架构概览

WebSocket 服务采用模块化设计，将连接管理功能拆分为三个核心模块：

```
services/websocket/
├── __init__.py              # 模块导出
├── connection_pool.py        # 连接池管理
├── message_dispatcher.py     # 消息分发
├── connection_monitor.py     # 连接监控
└── manager.py               # 统一管理器
```

## 模块说明

### 1. ConnectionPool (connection_pool.py)

**职责**：管理所有 WebSocket 连接的存储

**核心方法**：
- `add(websocket, instance_name)` - 添加连接
- `remove(websocket, instance_name)` - 移除连接
- `get_all(instance_name)` - 获取实例的所有连接
- `has_instance(instance_name)` - 检查实例是否有连接
- `count(instance_name)` - 获取连接数
- `clear(instance_name)` - 清空连接

**特点**：
- 使用 Set 存储，自动去重
- 按 instance_name 分组管理
- 支持实例级和全局清理

### 2. MessageDispatcher (message_dispatcher.py)

**职责**：处理向 WebSocket 连接发送消息的逻辑

**核心方法**：
- `send_to_instance(instance_name, message)` - 向实例发送消息
- `send_patch(instance_name, patch, patch_id, base_version)` - 发送 Patch
- `broadcast(message)` - 向所有实例广播

**特点**：
- 自动清理断开的连接
- 支持结构化消息发送
- 提供详细的日志记录

### 3. ConnectionMonitor (connection_monitor.py)

**职责**：提供连接统计和健康检查

**核心方法**：
- `get_stats()` - 获取统计信息
- `get_instance_stats(instance_name)` - 获取实例统计
- `health_check()` - 健康检查
- `list_active_instances()` - 列出活跃实例

**特点**：
- 实时统计连接数
- 支持健康检查
- 提供多维度监控

### 4. WebSocketManager (manager.py)

**职责**：整合以上三个模块，提供统一接口

**核心方法**：
```python
# 连接管理
async def connect(websocket, instance_name) - 接受连接
def disconnect(websocket, instance_name) - 断开连接

# 消息发送
async def send_patch(instance_name, patch, patch_id, base_version) - 发送 Patch
async def send_message(instance_name, message) - 发送自定义消息
async def broadcast(message) - 广播消息

# 监控统计
def get_connection_count(instance_name) - 获取连接数
def get_total_connections() - 获取总连接数
def get_stats() - 获取统计信息
def health_check() - 健康检查
```

**特点**：
- 单一接口，简化调用
- 兼容旧的 API
- 提供完整的功能

## 使用示例

### 基本使用（推荐）

```python
from backend.fastapi.services.websocket import manager

# 接受连接
await manager.connect(websocket, instance_name)

# 断开连接
manager.disconnect(websocket, instance_name)

# 发送 Patch
await manager.send_patch("counter", {"state.params.count": 42}, patch_id=1)

# 获取连接数
count = manager.get_connection_count("counter")
```

### 高级使用（直接使用子模块）

```python
from backend.fastapi.services.websocket import (
    ConnectionPool,
    MessageDispatcher,
    ConnectionMonitor
)

# 创建各个模块
pool = ConnectionPool()
dispatcher = MessageDispatcher(pool)
monitor = ConnectionMonitor(pool)

# 使用各模块功能
pool.add(websocket, "demo")
await dispatcher.send_patch("demo", {...})
stats = monitor.get_stats()
```

## 迁移指南

### 从旧版迁移

旧版代码：
```python
from backend.fastapi.websocket_manager import manager

# 旧版 API 完全兼容
await manager.connect(websocket, instance_name)
await manager.send_patch(instance_name, patch, patch_id)
```

新版代码：
```python
from backend.fastapi.services.websocket import manager

# API 完全相同，无需修改
await manager.connect(websocket, instance_name)
await manager.send_patch(instance_name, patch, patch_id)
```

## 设计优势

### 1. 单一职责
- ConnectionPool 只负责连接存储
- MessageDispatcher 只负责消息发送
- ConnectionMonitor 只负责监控统计

### 2. 可测试性
- 每个模块可以独立测试
- 易于 Mock 和单元测试

### 3. 可扩展性
- 可以轻松添加新的功能模块
- 各模块之间低耦合

### 4. 可维护性
- 代码结构清晰
- 易于理解和维护

## 测试

### ConnectionPool 测试

```python
from backend.fastapi.services.websocket import ConnectionPool

pool = ConnectionPool()
pool.add(websocket1, "demo")
pool.add(websocket2, "demo")

assert pool.count("demo") == 2
assert pool.has_instance("demo") == True
```

### MessageDispatcher 测试

```python
from backend.fastapi.services.websocket import MessageDispatcher, ConnectionPool

pool = ConnectionPool()
dispatcher = MessageDispatcher(pool)

result = await dispatcher.send_patch("demo", {"key": "value"})
assert result == True
```

### ConnectionMonitor 测试

```python
from backend.fastapi.services.websocket import ConnectionMonitor, ConnectionPool

pool = ConnectionPool()
monitor = ConnectionMonitor(pool)

stats = monitor.get_stats()
assert "total_connections" in stats
```

## 日志

所有模块都使用 Python logging 模块：

```python
import logging

# ConnectionPool
logger = logging.getLogger("backend.fastapi.services.websocket.connection_pool")

# MessageDispatcher
logger = logging.getLogger("backend.fastapi.services.websocket.message_dispatcher")

# ConnectionMonitor
logger = logging.getLogger("backend.fastapi.services.websocket.connection_monitor")

# WebSocketManager
logger = logging.getLogger("backend.fastapi.services.websocket.manager")
```

## 性能考虑

1. **连接池**：使用 Set 存储，查找和删除 O(1)
2. **消息分发**：异步发送，不阻塞主线程
3. **监控统计**：实时计算，无额外存储开销

## 未来扩展

可能的方向：

1. **连接限流**：限制单实例最大连接数
2. **消息队列**：使用队列缓冲消息
3. **持久化**：保存连接历史
4. **监控面板**：提供可视化监控界面
5. **负载均衡**：支持多进程连接管理
