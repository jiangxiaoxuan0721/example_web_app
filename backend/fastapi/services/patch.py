"""Patch 应用器 - 应用 Patch 到 Schema"""

from typing import Dict, Any
from ..models import UISchema


def apply_patch_to_schema(schema: UISchema, patch: Dict[str, Any]) -> None:
    """将 Patch 应用到 Schema

    Args:
        schema: 目标 Schema
        patch: Patch 数据字典，格式为 {"path": value}
    """
    for path, value in patch.items():
        keys = path.split('.')

        # 路径格式：state.params.key 或 state.runtime.key
        if len(keys) >= 3 and keys[0] == 'state':
            target_section = keys[1]  # 'params' 或 'runtime'
            target_key = keys[2]         # 具体键名

            # 确保字典存在
            if target_section == 'params':
                if schema.state.params is None:
                    schema.state.params = {}
                schema.state.params[target_key] = value
            elif target_section == 'runtime':
                if schema.state.runtime is None:
                    schema.state.runtime = {}
                schema.state.runtime[target_key] = value