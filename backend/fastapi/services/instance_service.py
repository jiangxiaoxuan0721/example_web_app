"""实例服务 - 处理实例的创建、删除和操作"""

from typing import Dict, Any, Optional
from ..models import UISchema, MetaInfo, StateInfo, LayoutInfo, Block, ActionConfig, StepInfo, BlockProps, FieldConfig
from backend.core.manager import SchemaManager
from .patch import apply_patch_to_schema


class InstanceService:
    """实例服务"""

    def __init__(self, schema_manager: SchemaManager):
        self.schema_manager = schema_manager

    def create_instance(
        self,
        instance_id: str,
        patches: list[Dict[str, Any]]
    ) -> tuple[bool, Optional[str]]:
        """
        创建新实例

        返回: (是否成功, 错误消息)
        """
        # 检查实例是否已存在
        if self.schema_manager.exists(instance_id):
            return False, f"Instance '{instance_id}' already exists"

        # 应用 patches 创建实例
        new_schema = None
        for patch in patches:
            op = patch.get("op")
            path = patch.get("path")
            value = patch.get("value")

            if op != "set":
                continue

            if path == "meta":
                meta_data = value
                new_schema = UISchema(
                    meta=MetaInfo(
                        pageKey=getattr(meta_data, "pageKey", instance_id),
                        step=StepInfo(**getattr(meta_data, "step", {"current": 1, "total": 1})),
                        status=getattr(meta_data, "status", "idle")
                    ),
                    state=StateInfo(params={}, runtime={}),
                    layout=LayoutInfo(type="single"),
                    blocks=[],
                    actions=[]
                )
            elif path == "state" and new_schema:
                state_data = value
                new_schema.state = StateInfo(
                    params=getattr(state_data, "params", {}),
                    runtime=getattr(state_data, "runtime", {})
                )
            elif path == "blocks" and new_schema:
                blocks_data = value or []
                converted_blocks = []
                for block in blocks_data:
                    block_copy = dict(block)

                    if 'props' in block_copy and block_copy.get('props') is not None:
                        props_copy = dict(block_copy.get('props', {}))
                        if 'fields' in props_copy and props_copy.get('fields') is not None:
                            fields_data = props_copy.get('fields', []) or []
                            converted_fields = [FieldConfig(**field) for field in fields_data]
                            props_copy['fields'] = converted_fields
                            block_copy['props'] = props_copy
                        converted_blocks.append(Block(**block_copy))
                new_schema.blocks = converted_blocks
            elif path == "actions" and new_schema:
                actions_data = value or []
                new_schema.actions = [ActionConfig(**action) for action in actions_data]

        if new_schema:
            self.schema_manager.set(instance_id, new_schema)
            return True, f"Instance '{instance_id}' created successfully"

        return False, "Failed to create instance: Invalid patches"

    def delete_instance(
        self,
        instance_id: str
    ) -> tuple[bool, Optional[str]]:
        """
        删除实例

        返回: (是否成功, 错误消息)
        """
        if not self.schema_manager.exists(instance_id):
            return False, f"Instance '{instance_id}' not found"

        self.schema_manager.delete(instance_id)
        return True, f"Instance '{instance_id}' deleted successfully"

    def handle_action(
        self,
        instance_id: str,
        action_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理实例的 action 操作

        返回: Patch 数据字典
        """
        schema = self.schema_manager.get(instance_id)
        if not schema:
            return {
                "status": "error",
                "error": f"Instance '{instance_id}' not found"
            }

        patch = {}

        # Demo 实例
        if instance_id == "demo" and action_id == "click_me":
            patch.update({"state.params.message": "Button Clicked!"})

        # Counter 实例
        elif instance_id == "counter":
            current_count = schema.state.params.get("count", 0)
            if action_id == "increment":
                patch.update({"state.params.count": current_count + 1})
            elif action_id == "decrement":
                patch.update({"state.params.count": current_count - 1})

        # Form 实例
        elif instance_id == "form":
            if action_id == "submit":
                current_name = schema.state.params.get("name", "")
                current_email = schema.state.params.get("email", "")

                patch.update({
                    "state.runtime.status": "submitted",
                    "state.runtime.message": f"表单已提交！姓名: {current_name}, 邮箱: {current_email}"
                })
            elif action_id == "clear":
                patch.update({
                    "state.params.name": "",
                    "state.params.email": "",
                    "state.runtime.status": "idle",
                    "state.runtime.message": ""
                })

        # 应用 patch 到 schema
        if patch:
            apply_patch_to_schema(schema, patch)

        return {
            "status": "success",
            "patch": patch
        }
