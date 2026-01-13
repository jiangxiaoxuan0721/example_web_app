# Agent 可编程 UI Runtime - 最小原型

## 架构说明

这是一个「Agent 可编程 UI Runtime 系统」的最小原型，实现Schema驱动的UI架构：

```sh
┌───────────────────────┐
│   External AI (LLM)   │
│  - 推理               │
│  - 调用 MCP 工具      │
└───────────┬───────────┘
            │
            │ MCP Tool Calls
            ▼
┌───────────────────────┐
│   MCP Tool Server     │  ← FastAPI + FastMCP
│  - Schema Authority   │
│  - Patch 应用         │
│  - Event 调度         │
│  - 实例管理           │
└───────────┬───────────┘
            │
            │ Schema / Patch / Event
            ▼
┌───────────────────────┐
│   Frontend Runtime    │  ← TypeScript SPA
│  - Schema Interpreter │
│  - Renderer           │
│  - Event Emitter      │
└───────────────────────┘
```

## 职责划分

### 前端（TypeScript）

**只做三件事：**

1. 加载 Schema（API / WS）
2. 渲染 Schema
3. 把用户行为变成 Event

**🚫 不做：**

- 不存业务状态
- 不做流程判断
- 不生成 Schema

### 后端（FastAPI + FastMCP）

**是系统的大脑 + 内核：**

1. 保存 Schema 实例（Authority）
2. 接收前端 Event
3. 调用 / 等待 AI
4. 校验并下发 Schema / Patch

### AI（外部）

**无状态、工具驱动：**

1. 接收 MCP 提供的上下文
2. 决定下一步
3. 只能通过 Tool 改 UI

## 当前实现（最小闭环）

### Step 1: 后端 - Schema Authority

- 内存中存储 UISchema 实例
- 提供 `GET /ui/schema` 返回写死的 Schema
- 提供 `POST /ui/event` 接收事件并返回 Patch

### Step 2: 前端 - 最小 Schema Renderer

- 支持 `layout: single`
- 支持 `block: form (text)`
- 显示 "Hello Schema + 一个按钮"

### Step 3: 前端 → 后端 Event 通路

- 按钮点击 -> `POST /ui/event`
- 后端接收事件

### Step 4: 前端 applyPatch → rerender

- 接收 Patch -> 应用 Patch -> 重新渲染
- 示例 Patch：`{"state.params.message": "Button Clicked!"}`

## 启动方式

### 启动后端

```bash
cd z:/respos/example_web_app
uvicorn backend.fastapi.main:app --host 0.0.0.0 --port 8001 --reload
```

后端将运行在 `http://localhost:8001`

### 启动前端

```bash
cd z:/respos/example_web_app/frontend
npm run dev
```

前端将运行在 `http://localhost:5173`

## API 接口

### GET /ui/schema

获取当前 Schema

支持多实例：

- `/ui/schema`              -> 返回默认实例 (demo)
- `/ui/schema?instanceId=counter` -> 返回 counter 实例
- `/ui/schema?instanceId=form`    -> 返回 form 实例

**响应示例：**

```json
{
  "status": "success",
  "instance_id": "demo",
  "schema": {
    "meta": {
      "pageKey": "demo",
      "step": {"current": 1, "total": 1},
      "status": "idle",
      "schemaVersion": "1.0"
    },
    "state": {
      "params": {"message": "Hello Schema!"}
    },
    "layout": {"type": "single"},
    "blocks": [
      {
        "id": "text_block",
        "type": "form",
        "bind": "state.params",
        "props": {
          "fields": [
            {"label": "消息", "key": "message", "type": "text"}
          ]
        }
      }
    ],
    "actions": [
      {"id": "click_me", "label": "Click Me", "style": "primary"}
    ]
  }
}
```

**可用实例：**

- `demo` - 消息示例
- `counter` - 计数器示例
- `form` - 表单示例

### POST /ui/event

处理前端事件

**请求示例：**

```json
{
  "type": "action:click",
  "pageKey": "demo",
  "payload": {
    "actionId": "click_me"
  }
}
```

**响应示例：**

```json
{
  "status": "success",
  "instance_id": "demo",
  "patch_id": 1,
  "patch": {
    "state.params.message": "Button Clicked!"
  }
}
```

**注意：** `pageKey` 字段用作 `instance_id`，指定实例。

### GET /ui/patches

获取所有 Patch 历史记录（支持重放）

支持多实例：

- `/ui/patches`              -> 返回默认实例的历史
- `/ui/patches?instanceId=xxx` -> 返回指定实例的历史

**响应示例：**

```json
{
  "status": "success",
  "instance_id": "demo",
  "patches": [
    {
      "id": 1,
      "timestamp": "2026-01-13T08:20:30.123456",
      "patch": {
        "state.params.message": "Button Clicked!"
      }
    },
    {
      "id": 2,
      "timestamp": "2026-01-13T08:21:15.789012",
      "patch": {
        "state.params.message": "Hello Schema!"
      }
    }
  ]
}
```

### GET /ui/patches/replay/{patch_id}

重放指定 Patch（独立重放，不依赖前端状态）

支持多实例：

- `/ui/patches/replay/1`              -> 重放默认实例的 Patch
- `/ui/patches/replay/1?instanceId=xxx` -> 重放指定实例的 Patch

**响应示例：**

```json
{
  "status": "success",
  "instance_id": "demo",
  "patch_id": 1,
  "patch": {
    "state.params.message": "Button Clicked!"
  }
}
```

## 测试流程

### Demo 实例

1. 访问 `http://localhost:5173?instanceId=demo`
2. 看到 "Hello Schema!" 文本和 "Click Me" 按钮
3. 点击 "Click Me" 按钮
4. 文本变为 "Button Clicked!"，下方出现 Patch 记录
5. 点击历史记录中的 Patch，可以重放（恢复到该状态）

### Counter 实例

1. 访问 `http://localhost:5173?instanceId=counter`
2. 看到 "计数: 0" 和 "+1"、"-1" 按钮
3. 点击 "+1" 按钮，计数增加
4. 点击 "-1" 按钮，计数减少
5. 观察 Patch 历史记录

### Form 实例

1. 访问 `http://localhost:5173?instanceId=form`
2. 看到 "姓名" 和 "邮箱" 输入框
3. 点击 "清空" 按钮，清空所有字段
4. 观察 Patch 历史记录

### 切换实例

- 修改 URL 中的 `instanceId` 参数即可切换不同实例
- 每个实例有独立的 Schema 和 Patch 历史

## 自检清单 ✅

进入下一阶段前的自检：

1. **Schema 是不是唯一 UI 来源？**
   - ✅ 是的，前端只从 `GET /ui/schema` 获取 Schema，没有其他 UI 来源

2. **前端是不是完全被动？**
   - ✅ 是的，前端只渲染 Schema、发射事件，不做业务逻辑判断

3. **Patch 能不能独立重放？**
   - ✅ 是的！后端保存所有 Patch 历史记录，前端可随时重放任意 Patch
   - API: `GET /ui/patches` 获取历史，`GET /ui/patches/replay/{id}` 重放指定 Patch

4. **去掉前端缓存还能不能恢复？**
   - ✅ 是的，前端刷新后可重新获取 Schema，并从历史记录重放任意 Patch

5. **是否支持多实例？**
   - ✅ 是的！后端维护多个 Schema 实例（demo, counter, form），前端通过 URL 参数 `instanceId` 切换
   - 每个实例有独立的 Schema 状态和 Patch 历史

**所有检查项通过，可以继续下一阶段！** 🎉

## 下一步

这个最小原型已经实现了完整的 Schema/Patch/Event 闭环：

✅ 前端能通过 API 拿到一个 Schema 并渲染
✅ 用户点击按钮，后端返回 Patch
✅ 前端更新 UI

## 文件结构

### 前端

```
frontend/src/
├── App.tsx           # 主组件：加载Schema、渲染、发射Event
├── main.tsx          # 入口文件
└── index.css         # 样式文件
```

### 后端

```
backend/
├── fastapi/
│   ├── main.py       # 主应用：Schema Authority、API接口
│   └── models.py     # 数据模型：UISchema等
└── config.py         # 配置管理
```

## 职责清晰

### 前端只做3件事

1. 加载 Schema（`GET /ui/schema`）
2. 渲染 Schema（显示文本和按钮）
3. 发射 Event（`POST /ui/event`）

**🚫 不做：**

- 不存业务状态
- 不做流程判断
- 不生成 Schema

### 后端只做2件事

1. 保存 Schema 实例（内存中的 Authority）
2. 接收 Event -> 返回 Patch

**🚫 不做（最小原型阶段）：**

- 不接 MCP
- 不接 AI
- 不存持久化状态

这是最纯粹的前后端分离，Schema 驱动的 UI 架构。
