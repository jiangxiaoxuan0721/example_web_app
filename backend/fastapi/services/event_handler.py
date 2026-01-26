"""事件处理器 - 处理前端事件并生成 Patch"""

from typing import Any
from ..models import UISchema
from ..services.patch import apply_patch_to_schema


class EventHandler:
    """前端事件处理器"""

    def __init__(self):
        self._action_handlers = {
            "demo": self._handle_demo_actions,
            "counter": self._handle_counter_actions,
            "form": self._handle_form_actions
        }

    async def handle_event(
        self,
        event_type: str,
        action_id: str,
        instance_id: str,
        params: dict[str, Any],
        schema: UISchema
    ) -> dict[str, Any]:
        """处理前端事件

        Args:
            event_type: 事件类型
            action_id: 操作 ID
            instance_id: 实例 ID
            params: 参数
            schema: 当前 Schema

        Returns:
            Patch 字典
        """
        patch = {}

        # 处理字段变化事件（已废弃，前端不再发送）
        if event_type == "field:change":
            field_key = params.get("fieldKey")
            field_value = params.get("value")
            if field_key:
                patch = {f"state.params.{field_key}": field_value}

        # 处理操作按钮点击事件
        # 注意：不再同步前端传来的 params，让后端直接使用 schema 原始值
        # 前端已过滤掉只读展示字段，不需要在这里更新 schema

        # 处理具体的 action 逻辑
        if instance_id in self._action_handlers:
            action_patch = self._action_handlers[instance_id](
                action_id, schema
            )
            patch.update(action_patch)

        return patch

    def _handle_demo_actions(self, action_id: str, schema: UISchema) -> dict[str, Any]:
        """处理 demo 实例的操作"""
        if action_id == "add_user":
            # 添加新用户
            current_users = schema.state.params.get("users", [])
            new_id = max([user.get("id", 0) for user in current_users] + [0]) + 1
            new_user = {
                "id": new_id,
                "name": f"用户{new_id}",
                "email": f"user{new_id}@example.com",
                "status": "pending" if new_id % 3 == 0 else "active",
                "avatar": f"https://picsum.photos/seed/user{new_id}/100/100.jpg"
            }
            return {"state.params.users": current_users + [new_user]}
        elif action_id == "reset_users":
            # 重置为初始数据
            return {"state.params.users": [
                {"id": 1, "name": "张三", "email": "zhangsan@example.com", "status": "active", "avatar": "https://picsum.photos/seed/zhangsan/100/100.jpg"},
                {"id": 2, "name": "李四", "email": "lisi@example.com", "status": "inactive", "avatar": "https://picsum.photos/seed/lisi/100/100.jpg"},
                {"id": 3, "name": "王五", "email": "wangwu@example.com", "status": "active", "avatar": "https://picsum.photos/seed/wangwu/100/100.jpg"}
            ]}
        return {}

    def _handle_counter_actions(self, action_id: str, schema: UISchema) -> dict[str, Any]:
        """处理 counter 实例的操作"""
        current_count = schema.state.params.get("count", 0)

        if action_id == "increment":
            return {"state.params.count": current_count + 1}
        elif action_id == "decrement":
            return {"state.params.count": current_count - 1}
        return {}

    def _handle_form_actions(self, action_id: str, schema: UISchema) -> dict[str, Any]:
        """处理 form 实例的操作"""
        # 只读展示类型字段（不包含在提交信息中）
        READ_ONLY_FIELD_TYPES = {"html", "image", "tag", "progress", "badge", "table", "modal"}

        # 获取可交互字段类型
        def get_field_type_by_key(field_key: str) -> str:
            """根据字段 key 查找字段类型"""
            for block in schema.blocks:
                if block.props and hasattr(block.props, "fields") and block.props.fields:
                    for field in block.props.fields:
                        if hasattr(field, "key") and field.key == field_key:
                            return getattr(field, "type", "text")
            return "text"  # 默认视为可交互类型

        if action_id == "submit":
            # 提交表单：只获取可交互的字段
            params = schema.state.params or {}
            
            # 构建提交消息，只包含可交互字段
            param_strings = []
            for key, value in sorted(params.items()):
                field_type = get_field_type_by_key(key)
                if field_type not in READ_ONLY_FIELD_TYPES:
                    # 对于数组类型的值，简化显示
                    if isinstance(value, list):
                        if len(value) <= 3:
                            param_strings.append(f"{key}: {value}")
                        else:
                            param_strings.append(f"{key}: [{len(value)} items]")
                    else:
                        param_strings.append(f"{key}: {value}")
            
            message = f"表单已提交！{', '.join(param_strings)}" if param_strings else "表单已提交！"
            
            # 更新 runtime 状态显示成功消息
            return {
                "state.runtime.status": "submitted",
                "state.runtime.message": message
            }

        elif action_id == "clear":
            # 清空表单：只清空可交互的字段
            params_patch = {}
            params = schema.state.params or {}
            
            for key in params.keys():
                field_type = get_field_type_by_key(key)
                # 只清空可交互字段类型，保留只读展示字段
                if field_type not in READ_ONLY_FIELD_TYPES:
                    params_patch[f"state.params.{key}"] = ""
            
            params_patch.update({
                "state.runtime.status": "idle",
                "state.runtime.message": ""
            })
            return params_patch

        return {}
