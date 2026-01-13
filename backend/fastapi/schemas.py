"""Schema 类型定义（与前端类型系统对齐）"""

from typing import Dict, Any, List, Optional
from .models import (
    UISchema, MetaInfo, StepInfo, StateInfo, LayoutInfo,
    Block, BlockProps, ActionConfig, FieldConfig
)
from ..config import config_manager


def generate_step_info(current: int, total: int) -> StepInfo:
    """生成步骤信息"""
    return StepInfo(current=current, total=total)


def generate_state_info(params: Optional[Dict[str, Any]] = None, runtime: Optional[Dict[str, Any]] = None) -> StateInfo:
    """生成状态信息"""
    return StateInfo(
        params=params or {},
        runtime=runtime or {}
    )


def generate_meta_info(page_key: str, step_info: StepInfo, status: str = "idle") -> MetaInfo:
    """生成元数据"""
    return MetaInfo(
        pageKey=page_key,
        step=step_info,
        status=status
    )


def generate_field_config(field_data: Dict[str, Any]) -> FieldConfig:
    """从配置数据生成字段配置"""
    return FieldConfig(**field_data)


def generate_block_props(component_config: Dict[str, Any]) -> Optional[BlockProps]:
    """从组件配置生成 Block 属性"""
    if not component_config:
        return None
    
    # 提取可能的字段
    fields = None
    if "fields" in component_config:
        fields = [generate_field_config(f) for f in component_config["fields"]]
    
    # 提取其他布尔属性
    props_data = {
        k: v for k, v in component_config.items()
        if k != "fields" and isinstance(v, bool)
    }
    
    if fields or props_data:
        return BlockProps(fields=fields, **props_data)
    
    return None


def generate_block(block_id: str, component_config: Dict[str, Any], bind: str = "state.params") -> Block:
    """生成 Block"""
    return Block(
        id=block_id,
        type=component_config.get("type", "form"),
        bind=bind,
        props=generate_block_props(component_config)
    )


def generate_actions(
    execution_strategy: str,
    next_action: str,
    current_step: int,
    total_steps: int
) -> List[ActionConfig]:
    """生成操作列表"""
    actions = []
    
    # Action 标签映射
    action_labels = {
        "confirm_modify": "确认修改",
        "confirm_execute": "执行",
        "confirm_config": "确认配置",
        "confirm_count": "确认",
        "confirm_submit": "提交任务",
        "confirm_template": "确认模板"
    }
    
    # 根据 executionStrategy 决定是否显示执行按钮
    if execution_strategy in ["ask_execute", "auto_wait_confirm"]:
        actions.append(ActionConfig(
            id=next_action,
            label=action_labels.get(next_action, next_action),
            style="primary"
        ))
    
    # 添加上一步按钮（除了第一步）
    if current_step > 0:
        actions.append(ActionConfig(
            id="prev",
            label="上一步",
            style="secondary"
        ))
    
    # 添加下一步按钮（除了最后一步）
    if current_step < total_steps - 1:
        actions.append(ActionConfig(
            id="next",
            label="下一步",
            style="secondary"
        ))
    
    # 添加取消按钮
    actions.append(ActionConfig(
        id="cancel",
        label="取消",
        style="danger"
    ))
    
    return actions


def generate_mode_selection_schema() -> UISchema:
    """生成模式选择 Schema"""
    modes = config_manager.get_modes()

    # 生成模式选项
    mode_options = []
    for mode_id, mode_config in modes.items():
        mode_options.append({
            "value": mode_id,
            "label": mode_config.get("name", mode_id)
        })

    return UISchema(
        meta=generate_meta_info(
            page_key="mode_selection",
            step_info=generate_step_info(0, 1),
            status="idle"
        ),
        state=generate_state_info(),
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="mode_selection",
                type="form",
                bind="state.params",
                props=BlockProps.model_construct(
                    fields=[
                        FieldConfig(
                            label="选择仿真模式",
                            key="selectedMode",
                            type="select",
                            options=mode_options,
                            rid=None,
                            value=None,
                            description=None
                        )
                    ]
                )
            )
        ],
        actions=[
            ActionConfig(id="confirm", label="开始向导", style="primary"),
            ActionConfig(id="cancel", label="取消", style="secondary")
        ]
    )


def generate_step_schema(mode_id: str, step_index: int, params: Optional[Dict[str, Any]] = None) -> Optional[UISchema]:
    """生成步骤 Schema"""
    # 获取模式配置
    mode_config = config_manager.get_mode(mode_id)
    if not mode_config:
        return None
    
    steps = mode_config.get("steps", [])
    if step_index < 0 or step_index >= len(steps):
        return None
    
    step = steps[step_index]
    component_id = step.get("component")
    
    # 获取组件配置
    component_config = config_manager.get_component(component_id)
    if not component_config:
        component_config = {"type": "form", "fields": []}
    
    return UISchema(
        meta=generate_meta_info(
            page_key=f"{mode_id}_{step['id']}",
            step_info=generate_step_info(step_index + 1, len(steps)),
            status="idle"
        ),
        state=generate_state_info(
            params=params or {},
            runtime={
                "mode": mode_id,
                "stepId": step["id"],
                "executionStrategy": step["executionStrategy"],
                "nextAction": step["nextAction"]
            }
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            generate_block(step["id"], component_config, "state.params")
        ],
        actions=generate_actions(
            execution_strategy=step["executionStrategy"],
            next_action=step["nextAction"],
            current_step=step_index,
            total_steps=len(steps)
        )
    )
