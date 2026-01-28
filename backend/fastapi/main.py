"""FastAPI 主应用 - Agent 可编程 UI Runtime 后端"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..core import PatchHistoryManager, SchemaManager
from .services.websocket.handlers.manager import WebSocketManager
from ..config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title="Agent Programmable UI Runtime",
    version="1.0.0",
    description="Schema-driven UI Runtime Backend",
    debug=settings.debug
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
from backend.core.defaults import get_default_instances
from .services.instance_service import InstanceService


# 创建服务实例
schema_manager = SchemaManager()
instance_service = InstanceService(schema_manager)
patch_history = PatchHistoryManager()
ws_manager = WebSocketManager()
default_instance_id = "demo"

# 初始化默认实例
for instance_id, schema in get_default_instances().items():
    schema_manager.set(instance_id, schema)

# 将WebSocket管理器存储到应用状态中，以便在路由中访问
app.state.ws_manager = ws_manager

# 注册路由（使用 routes 模块的注册函数）
from .routes.event_routes import register_event_routes
from .routes.patch_routes import register_patch_routes
from .routes.schema_routes import register_schema_routes
from .routes.websocket_routes import register_websocket_routes

register_event_routes(app, schema_manager, instance_service, patch_history, ws_manager, default_instance_id)
register_patch_routes(app, schema_manager, patch_history, ws_manager)
register_schema_routes(app, schema_manager, default_instance_id, ws_manager)
register_websocket_routes(app, ws_manager, schema_manager)


# 基础端点
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Agent Programmable UI Runtime",
        "version": "1.0.0",
        "status": "running",
        "available_instances": schema_manager.list_all()
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 启动说明
if __name__ == "__main__":
    import uvicorn

    print(f"Starting Agent Programmable UI Runtime")
    print(f"Version: 1.0.0")
    print(f"Frontend: http://localhost:5173")
    print(f"Backend: http://localhost:{settings.port}")
    print()
    print("Architecture:")
    print("- Frontend: Load Schema -> Render -> Emit Event")
    print("- Backend: Save Schema Authority -> Receive Event -> Return Patch")

    uvicorn.run(
        "backend.fastapi.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
