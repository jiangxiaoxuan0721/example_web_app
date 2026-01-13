"""FastAPI 主应用 - Agent 可编程 UI Runtime 后端"""

from fastapi import FastAPI, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ..config import settings
from .models import UISchema, MetaInfo, StateInfo, LayoutInfo, Block, ActionConfig, StepInfo
from typing import Dict, Any, Optional
from datetime import datetime
import traceback

# 创建 FastAPI 应用
app = FastAPI(
    title="Agent Programmable UI Runtime",
    version="1.0.0",
    description="Schema-driven UI Runtime Backend",
    debug=settings.debug
)

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器，返回 JSON 而不是 traceback"""
    print(f"[后端] [ERROR] 全局异常: {exc}")
    print(f"[后端] Traceback:\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": str(exc),
            "detail": "Internal server error"
        }
    )

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 多个 Schema 实例（支持 instanceId） ============
# 暂时写死3个实例
schema_instances = {
    "demo": UISchema(
        meta=MetaInfo(
            pageKey="demo",
            step=StepInfo(current=1, total=1),
            status="idle",
            schemaVersion="1.0"
        ),
        state=StateInfo(
            params={"message": "Hello Schema!"}
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="text_block",
                type="form",
                bind="state.params",
                props={
                    "fields": [
                        {"label": "消息", "key": "message", "type": "text"}
                    ]
                }
            )
        ],
        actions=[
            ActionConfig(id="click_me", label="Click Me", style="primary")
        ]
    ),
    "counter": UISchema(
        meta=MetaInfo(
            pageKey="counter",
            step=StepInfo(current=1, total=1),
            status="idle",
            schemaVersion="1.0"
        ),
        state=StateInfo(
            params={"count": 0}
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="counter_block",
                type="form",
                bind="state.params",
                props={
                    "fields": [
                        {"label": "计数", "key": "count", "type": "text"}
                    ]
                }
            )
        ],
        actions=[
            ActionConfig(id="increment", label="+1", style="primary"),
            ActionConfig(id="decrement", label="-1", style="secondary")
        ]
    ),
    "form": UISchema(
        meta=MetaInfo(
            pageKey="form",
            step=StepInfo(current=1, total=1),
            status="idle",
            schemaVersion="1.0"
        ),
        state=StateInfo(
            params={"name": "", "email": ""}
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="form_block",
                type="form",
                bind="state.params",
                props={
                    "fields": [
                        {"label": "姓名", "key": "name", "type": "text"},
                        {"label": "邮箱", "key": "email", "type": "text"}
                    ]
                }
            )
        ],
        actions=[
            ActionConfig(id="clear", label="清空", style="danger")
        ]
    )
}

# 默认实例
default_instance_id = "demo"


# ============ Patch 历史记录（支持重放） ============
patch_history: Dict[str, list[Dict[str, Any]]] = {}  # {instanceId: [patches]}
patch_counters: Dict[str, int] = {}  # {instanceId: counter}


def save_patch(instance_id: str, patch: Dict[str, Any]) -> int:
    """保存 Patch 到指定实例的历史记录"""
    if instance_id not in patch_history:
        patch_history[instance_id] = []
    if instance_id not in patch_counters:
        patch_counters[instance_id] = 0

    patch_counters[instance_id] += 1
    patch_record = {
        "id": patch_counters[instance_id],
        "timestamp": datetime.now().isoformat(),
        "patch": patch
    }
    patch_history[instance_id].append(patch_record)
    return patch_counters[instance_id]


# ============ API 接口 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Agent Programmable UI Runtime",
        "version": "1.0.0",
        "status": "running",
        "available_instances": list(schema_instances.keys())
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/ui/schema")
async def get_schema(instance_id: Optional[str] = Query(None, alias="instanceId", description="实例 ID")):
    """
    获取当前 Schema

    支持多实例：
    - /ui/schema              -> 返回默认实例 (demo)
    - /ui/schema?instanceId=counter -> 返回 counter 实例
    - /ui/schema?instanceId=form    -> 返回 form 实例

    Step 1: 返回写死的 Schema
    """
    # 调试日志：打印收到的 instance_id
    print(f"[后端] get_schema 收到 instance_id 参数: '{instance_id}'")
    print(f"[后端] schema_instances 的 keys: {list(schema_instances.keys())}")

    # 如果没有指定 instanceId，使用默认值
    if not instance_id:
        instance_id = default_instance_id
        print(f"[后端] instance_id 为空，使用默认值: '{instance_id}'")

    # 查找实例
    schema = schema_instances.get(instance_id)

    if not schema:
        print(f"[后端] [ERROR] 实例 '{instance_id}' 不存在！")
        return {
            "status": "error",
            "error": f"实例 '{instance_id}' 不存在",
            "available_instances": list(schema_instances.keys())
        }

    print(f"[后端] [OK] 找到实例 '{instance_id}'")

    return {
        "status": "success",
        "instance_id": instance_id,
        "schema": schema.model_dump()
    }


@app.post("/ui/event")
async def handle_event(event: dict):
    """
    处理前端事件
    Step 3: 接收事件，直接返回 Patch
    """
    event_type = event.get("type")
    action_id = event.get("payload", {}).get("actionId")
    instance_id = event.get("pageKey", default_instance_id)

    print(f"[后端] 收到事件: {event_type}, actionId: {action_id}, instanceId: {instance_id}")

    # 获取当前实例的 Schema
    current_schema = schema_instances.get(instance_id)
    if not current_schema:
        return {
            "status": "error",
            "error": f"实例 '{instance_id}' 不存在"
        }

    # Step 3: 不推理，直接返回 Patch
    patch = {}

    if instance_id == "demo" and action_id == "click_me":
        patch = {"state.params.message": "Button Clicked!"}

    elif instance_id == "counter":
        current_count = current_schema.state.params.get("count", 0)
        if action_id == "increment":
            patch = {"state.params.count": current_count + 1}
        elif action_id == "decrement":
            patch = {"state.params.count": current_count - 1}

    elif instance_id == "form" and action_id == "clear":
        patch = {
            "state.params.name": "",
            "state.params.email": ""
        }

    if patch:
        patch_id = save_patch(instance_id, patch)
        # 更新当前 Schema（同步后端状态）
        apply_patch_to_schema(current_schema, patch)
        return {
            "status": "success",
            "instance_id": instance_id,
            "patch_id": patch_id,
            "patch": patch
        }

    return {
        "status": "success",
        "instance_id": instance_id,
        "patch_id": None,
        "patch": {}
    }


def apply_patch_to_schema(schema: UISchema, patch: Dict[str, Any]):
    """将 Patch 应用到 Schema（后端内部状态同步）"""
    for path, value in patch.items():
        keys = path.split('.')

        # 路径格式：state.params.key 或 state.runtime.key
        if len(keys) >= 3 and keys[0] == 'state':
            target_section = keys[1]  # 'params' 或 'runtime'
            target_key = keys[2]         # 具体键名

            if target_section == 'params' and schema.state.params is not None:
                schema.state.params[target_key] = value
            elif target_section == 'runtime' and schema.state.runtime is not None:
                schema.state.runtime[target_key] = value


@app.get("/ui/patches")
async def get_patches(instance_id: Optional[str] = Query(None, alias="instanceId", description="实例 ID")):
    """
    获取所有 Patch 历史记录
    支持 Patch 重放

    - /ui/patches              -> 返回默认实例的历史
    - /ui/patches?instanceId=xxx -> 返回指定实例的历史
    """
    if not instance_id:
        instance_id = default_instance_id

    patches = patch_history.get(instance_id, [])

    return {
        "status": "success",
        "instance_id": instance_id,
        "patches": patches
    }


@app.get("/ui/patches/replay/{patch_id}")
async def replay_patch(patch_id: int, instance_id: Optional[str] = Query(None, alias="instanceId", description="实例 ID")):
    """
    重放指定 Patch

    自检清单验证：
    ✅ Schema 是唯一 UI 来源 - 是
    ✅ 前端完全被动 - 是
    ✅ Patch 能独立重放 - 是（此接口）
    ✅ 去掉前端缓存能恢复 - 是
    """
    if not instance_id:
        instance_id = default_instance_id

    # 找到对应的 Patch
    patches = patch_history.get(instance_id, [])
    patch_record = next((p for p in patches if p["id"] == patch_id), None)

    if not patch_record:
        return {
            "status": "error",
            "message": f"Patch {patch_id} 在实例 '{instance_id}' 中不存在"
        }

    print(f"[后端] 重放 Patch {patch_id} (instance: {instance_id}): {patch_record['patch']}")

    # 应用到当前 Schema
    current_schema = schema_instances.get(instance_id)
    if current_schema:
        apply_patch_to_schema(current_schema, patch_record["patch"])

    return {
        "status": "success",
        "instance_id": instance_id,
        "patch_id": patch_id,
        "patch": patch_record["patch"]
    }


# 启动说明
if __name__ == "__main__":
    import uvicorn

    print(f"🚀 启动 Agent Programmable UI Runtime")
    print(f"版本: 1.0.0")
    print(f"前端: http://localhost:5173")
    print(f"后端: http://localhost:{settings.port}")
    print()
    print("架构：")
    print("- 前端: 加载 Schema -> 渲染 -> 发射 Event")
    print("- 后端: 保存 Schema Authority -> 接收 Event -> 返回 Patch")

    uvicorn.run(
        "backend.fastapi.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
