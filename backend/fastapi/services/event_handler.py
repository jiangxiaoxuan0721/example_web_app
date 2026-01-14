"""事件处理器 - 处理前端事件并生成 Patch"""

from typing import Dict, Any
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
        params: Dict[str, Any],
        schema: UISchema
    ) -> Dict[str, Any]:
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
        # 先同步前端传来的 params（如果有）
        if params and isinstance(params, dict):
            params_patch = {f"state.params.{k}": v for k, v in params.items()}
            apply_patch_to_schema(schema, params_patch)
            # 将 params_patch 合并到最终返回的 patch 中
            patch.update(params_patch)

        # 处理具体的 action 逻辑
        if instance_id in self._action_handlers:
            action_patch = self._action_handlers[instance_id](
                action_id, schema
            )
            patch.update(action_patch)

        return patch

    def _handle_demo_actions(self, action_id: str, schema: UISchema) -> Dict[str, Any]:
        """处理 demo 实例的操作"""
        if action_id == "click_me":
            return {"state.params.message": "Button Clicked!"}
        return {}

    def _handle_counter_actions(self, action_id: str, schema: UISchema) -> Dict[str, Any]:
        """处理 counter 实例的操作"""
        current_count = schema.state.params.get("count", 0)

        if action_id == "increment":
            return {"state.params.count": current_count + 1}
        elif action_id == "decrement":
            return {"state.params.count": current_count - 1}
        return {}

    def _handle_form_actions(self, action_id: str, schema: UISchema) -> Dict[str, Any]:
        """处理 form 实例的操作"""
        if action_id == "submit":
            # 提交表单：获取当前值
            current_name = schema.state.params.get("name", "")
            current_email = schema.state.params.get("email", "")

            # 更新 runtime 状态显示成功消息
            return {
                "state.runtime.status": "submitted",
                "state.runtime.message": f"表单已提交！姓名: {current_name}, 邮箱: {current_email}"
            }

        elif action_id == "clear":
            return {
                "state.params.name": "",
                "state.params.email": "",
                "state.runtime.status": "idle",
                "state.runtime.message": ""
            }

        return {}
