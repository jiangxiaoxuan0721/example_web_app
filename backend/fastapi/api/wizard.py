"""Wizard API 路由"""

from fastapi import APIRouter
from typing import Dict, Any
from ..models import SchemaResponse, ConfigResponse
from ..schemas import generate_mode_selection_schema, generate_step_schema
from ...config import config_manager

router = APIRouter(prefix="/api/wizard", tags=["Wizard"])


@router.get("/config", response_model=ConfigResponse)
async def get_wizard_config():
    """
    获取 Wizard 配置
    
    返回给前端用于生成模式选择页面
    """
    modes = config_manager.get_modes()
    
    return ConfigResponse(
        modes=modes,
        status="success"
    )


@router.get("/init", response_model=SchemaResponse)
async def init_wizard():
    """
    初始化 Wizard

    返回模式选择页面的 UISchema
    """
    schema = generate_mode_selection_schema()

    return SchemaResponse(
        ui_schema=schema,
        status="success"
    )


@router.get("/step/{mode}/{step_index}", response_model=SchemaResponse)
async def get_step_schema(mode: str, step_index: int):
    """
    获取指定步骤的 UISchema

    Args:
        mode: 模式名称（single/batch）
        step_index: 步骤索引（0-based）

    返回:
        UISchema 响应
    """
    try:
        schema = generate_step_schema(mode, step_index)

        if schema:
            return SchemaResponse(
                ui_schema=schema,
                status="success"
            )
        else:
            return SchemaResponse(
                ui_schema=None,
                status="error",
                error=f"模式 '{mode}' 或步骤 {step_index} 不存在"
            )

    except Exception as e:
        return SchemaResponse(
            ui_schema=None,
            status="error",
            error=str(e)
        )
