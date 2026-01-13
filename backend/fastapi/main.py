"""FastAPI 主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..config import settings
from .api import wizard, events

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Schema-driven UI Backend API",
    debug=settings.debug
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# 注册路由
app.include_router(wizard.router)
app.include_router(events.router)


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy"
    }


# 启动说明
if __name__ == "__main__":
    import uvicorn
    
    print(f"启动 {settings.app_name}")
    print(f"版本: {settings.app_version}")
    print(f"前端: http://localhost:3000")
    print(f"后端: http://localhost:{settings.port}")
    print()
    print("架构说明：")
    print("- 前端: 发射事件，渲染 UISchema")
    print("- 后端: 接收事件，Agent 决策，返回 Schema 或 Patch")
    print("- 配置: 由后端提供，不在前端静态文件")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
