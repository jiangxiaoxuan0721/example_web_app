"""Schema 相关 API 路由"""

from fastapi import Query
from typing import Optional
from ...core.manager import SchemaManager


def register_schema_routes(app, schema_manager: SchemaManager, default_instance_id: str, ws_manager=None):
    """注册 Schema 相关的路由

    Args:
        app: FastAPI 应用实例
        schema_manager: Schema 管理器
        default_instance_id: 默认实例 ID
        ws_manager: WebSocket管理器实例（可选）
    """

    @app.get("/ui/schema")
    async def get_schema(instance_id: str | None = Query(None, alias="instanceId")):
        """
        获取当前 Schema

        支持多实例：
        - /ui/schema              -> 返回默认实例 (demo)
        - /ui/schema?instanceId=counter -> 返回 counter 实例
        - /ui/schema?instanceId=form    -> 返回 form 实例
        """
        print(f"[SchemaRoutes] get_schema 收到 instance_id: '{instance_id}'")

        # 如果没有指定 instanceId，使用默认值
        if not instance_id:
            instance_id = default_instance_id
            print(f"[SchemaRoutes] 使用默认实例: '{instance_id}'")

        # 查找实例
        schema = schema_manager.get(instance_id)

        if not schema:
            print(f"[SchemaRoutes] 实例 '{instance_id}' 不存在")
            return {
                "status": "error",
                "error": f"实例 '{instance_id}' 不存在",
                "available_instances": schema_manager.list_all()
            }

        print(f"[SchemaRoutes] 找到实例 '{instance_id}'")

        return {
            "status": "success",
            "instance_id": instance_id,
            "schema": schema.model_dump()
        }

    @app.get("/ui/instances")
    async def list_instances():
        """列出所有可用的实例"""
        instances_info = schema_manager.get_all_info()

        return {
            "status": "success",
            "instances": instances_info,
            "total": len(instances_info)
        }

    @app.post("/ui/access")
    async def access_instance(request: dict):
        """访问指定实例并设置为活跃状态"""
        instance_id = request.get("instance_id")
        
        if not instance_id:
            return {
                "status": "error",
                "error": "缺少 instance_id 参数"
            }
        
        # 检查实例是否存在
        schema = schema_manager.get(instance_id)
        if not schema:
            return {
                "status": "error",
                "error": f"实例 '{instance_id}' 不存在",
                "available_instances": schema_manager.list_all()
            }
        
        print(f"[SchemaRoutes] 访问实例: '{instance_id}'")
        
        # 如果WebSocket管理器可用，通知前端切换到指定实例
        if ws_manager:
            await ws_manager.broadcast({
                "type": "switch_instance",
                "instance_id": instance_id,
                "schema": schema.model_dump()
            })
            print(f"[SchemaRoutes] 已通知前端切换到实例: '{instance_id}'")
        
        return {
            "status": "success",
            "message": f"已成功访问实例 '{instance_id}' 并通知前端切换",
            "instance_id": instance_id,
            "schema": schema.model_dump()
        }
