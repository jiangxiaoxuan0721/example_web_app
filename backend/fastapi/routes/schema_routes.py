"""Schema 相关 API 路由"""

from datetime import datetime
from fastapi import Query
from typing import Any
from ...core.manager import SchemaManager


def register_schema_routes(app, schema_manager: SchemaManager, default_instance_name: str, ws_manager=None):
    """注册 Schema 相关的路由

    Args:
        app: FastAPI 应用实例
        schema_manager: Schema 管理器
        default_instance_name: 默认实例 ID
        ws_manager: WebSocket管理器实例（可选）
    """

    @app.get("/ui/schema")
    async def get_schema(instance_name: str | None = Query(None, alias="instanceId")):
        """
        获取当前 Schema

        支持多实例：
        - /ui/schema              -> 返回默认实例 (demo)
        - /ui/schema?instanceId=counter -> 返回 counter 实例
        - /ui/schema?instanceId=form    -> 返回 form 实例
        """
        print(f"[SchemaRoutes] get_schema 收到 instance_name: '{instance_name}'")

        # 如果没有指定 instanceId，使用默认值
        if not instance_name:
            instance_name = default_instance_name
            print(f"[SchemaRoutes] 使用默认实例: '{instance_name}'")

        # 查找实例
        schema = schema_manager.get(instance_name)

        if not schema:
            print(f"[SchemaRoutes] 实例 '{instance_name}' 不存在")
            return {
                "status": "error",
                "error": f"实例 '{instance_name}' 不存在",
                "available_instances": schema_manager.list_all()
            }

        print(f"[SchemaRoutes] 找到实例 '{instance_name}'")

        # 动态更新 runtime.timestamp 为当前时间
        if schema.state and schema.state.runtime is not None:
            schema.state.runtime["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[SchemaRoutes] 已更新 runtime.timestamp 为当前时间")

        dumped_schema = schema.model_dump(by_alias=True)
        # 调试：检查 columns 的 renderType 字段
        if dumped_schema.get('blocks'):
            first_block = dumped_schema['blocks'][0]
            if 'props' in first_block and 'fields' in first_block['props']:
                first_field = first_block['props']['fields'][0]
                if 'columns' in first_field:
                    print(f"[SchemaRoutes] columns 数据: {first_field['columns'][2]}")  # 打印第3列（avatar）

        return {
            "status": "success",
            "instance_name": instance_name,
            "schema": dumped_schema
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

    @app.post("/ui/switch")
    async def switch_instance(request: dict[Any, Any]):
        """切换到指定实例并设置为活跃状态"""
        instance_name = request.get("instance_name")

        if not instance_name:
            return {
                "status": "error",
                "error": "缺少 instance_name 参数"
            }

        # 检查实例是否存在
        schema = schema_manager.get(instance_name)
        if not schema:
            return {
                "status": "error",
                "error": f"实例 '{instance_name}' 不存在",
                "available_instances": schema_manager.list_all()
            }

        print(f"[SchemaRoutes] 切换实例: '{instance_name}'")

        # 如果WebSocket管理器可用，通知前端切换到指定实例
        if ws_manager:
            await ws_manager.broadcast({
                "type": "switch_instance",
                "instance_name": instance_name
            })
            print(f"[SchemaRoutes] 已通知前端切换到实例: '{instance_name}'")

        return {
            "status": "success",
            "message": f"已成功切换到实例 '{instance_name}'",
            "instance_name": instance_name
        }
