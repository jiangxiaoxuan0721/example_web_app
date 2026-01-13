"""Agent 决策逻辑服务"""

from typing import Dict, Any, Optional
from ..models import EventType, UISchema, UIEvent
from ..schemas import generate_mode_selection_schema, generate_step_schema
from ...config import config_manager


class AgentService:
    """Agent 决策服务"""
    
    def __init__(self):
        """初始化 Agent"""
        self.session_state: Dict[str, Any] = {}  # 会话状态（实际应使用 Redis）
    
    def process_event(self, event: UIEvent) -> Dict[str, Any]:
        """
        处理前端事件，返回 Schema 或 Patch
        
        Args:
            event: UI 事件
            
        Returns:
            包含 schema 或 patch 的响应
        """
        event_type = event.type
        payload = event.payload
        
        print(f"[Agent] 处理事件: {event_type}")
        print(f"[Agent] 事件载荷: {payload.model_dump()}")
        
        # 根据事件类型处理
        if event_type == EventType.FIELD_CHANGE:
            return self._handle_field_change(payload)
        
        elif event_type == EventType.ACTION_CLICK:
            return self._handle_action_click(payload, event.pageKey)
        
        elif event_type == EventType.SELECT_MODE:
            return self._handle_select_mode(payload)
        
        elif event_type == EventType.CONFIRM_STEP:
            return self._handle_confirm_step(payload)
        
        else:
            return {
                "error": f"未知事件类型: {event_type}",
                "status": "error"
            }
    
    def _handle_field_change(self, payload) -> Dict[str, Any]:
        """处理字段变化事件"""
        field_key = payload.fieldKey
        value = payload.value
        
        # 可以在这里添加业务逻辑
        # 例如：验证值、检查依赖关系、保存到数据库等
        
        # 示例：验证速度字段
        if field_key == "speed" and isinstance(value, (int, float)):
            if value > 200:
                return {
                    "patch": {},
                    "error": "速度不能超过 200",
                    "status": "error"
                }
        
        # 简单返回 Patch 更新前端状态
        return {
            "patch": {f"state.params.{field_key}": value},
            "status": "success"
        }
    
    def _handle_action_click(self, payload, page_key: Optional[str]) -> Dict[str, Any]:
        """处理操作点击事件"""
        action_id = payload.actionId
        
        if action_id == "confirm":
            # 确认操作
            return {
                "message": "操作已确认",
                "status": "success"
            }
        
        elif action_id == "next":
            # 下一步 - 需要知道当前模式和步骤
            mode = payload.mode
            step_index = payload.stepIndex
            
            if mode is not None and step_index is not None:
                mode_config = config_manager.get_mode(mode)
                if mode_config:
                    total_steps = len(mode_config.get("steps", []))
                    if step_index < total_steps - 1:
                        next_step = step_index + 1
                        params = payload.params or {}
                        schema = generate_step_schema(mode, next_step, params)
                        if schema:
                            return {
                                "schema": schema.model_dump(),
                                "status": "success"
                            }
            
            return {
                "message": "准备进入下一步",
                "status": "success"
            }
        
        elif action_id == "prev":
            # 上一步
            mode = payload.mode
            step_index = payload.stepIndex
            
            if mode is not None and step_index is not None:
                if step_index > 0:
                    prev_step = step_index - 1
                    params = payload.params or {}
                    schema = generate_step_schema(mode, prev_step, params)
                    if schema:
                        return {
                            "schema": schema.model_dump(),
                            "status": "success"
                        }
            
            return {
                "message": "返回上一步",
                "status": "success"
            }
        
        elif action_id == "cancel":
            # 取消 - 返回模式选择页面
            schema = generate_mode_selection_schema()
            return {
                "schema": schema.model_dump(),
                "status": "success"
            }
        
        elif action_id in ["confirm_modify", "confirm_execute", "confirm_config", 
                           "confirm_count", "confirm_submit", "confirm_template"]:
            # 其他确认操作
            mode = payload.mode
            step_index = payload.stepIndex
            params = payload.params or {}
            
            # 示例：执行实际的业务逻辑
            # 在这里可以调用后端服务、执行计算等
            result = self._execute_business_logic(action_id, mode, params)
            
            if not result.get("success", False):
                return {
                    "error": result.get("error", "操作失败"),
                    "status": "error"
                }
            
            # 保存参数到会话状态
            self._save_params(mode, step_index, params)
            
            # 如果是最后一步，可能返回结果页面
            # 这里简化处理，直接返回成功消息
            return {
                "message": result.get("message", "操作成功"),
                "status": "success"
            }
        
        else:
            return {
                "error": f"未知操作: {action_id}",
                "status": "error"
            }
    
    def _handle_select_mode(self, payload) -> Dict[str, Any]:
        """处理选择模式事件"""
        mode = payload.mode
        
        if not mode:
            return {
                "error": "未指定模式",
                "status": "error"
            }
        
        # 返回第一步的 Schema
        schema = generate_step_schema(mode, 0)
        
        if schema:
            return {
                "schema": schema.model_dump(),
                "status": "success"
            }
        else:
            return {
                "error": f"模式不存在: {mode}",
                "status": "error"
            }
    
    def _handle_confirm_step(self, payload) -> Dict[str, Any]:
        """处理确认步骤事件"""
        # 可以在这里执行实际的业务逻辑
        # 例如：调用仿真服务、保存数据等
        return {
            "message": "步骤已确认",
            "status": "success"
        }
    
    def _execute_business_logic(self, action_id: str, mode: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行业务逻辑（示例）
        
        在实际项目中，这里会调用具体的后端服务
        例如：仿真计算、数据处理、数据库操作等
        """
        print(f"[Agent] 执行业务逻辑: action={action_id}, mode={mode}")
        print(f"[Agent] 参数: {params}")
        
        # 示例：根据 action_id 执行不同的逻辑
        if action_id == "confirm_execute":
            # 模拟执行仿真计算
            return {
                "success": True,
                "message": "仿真计算已启动"
            }
        
        elif action_id == "confirm_submit":
            # 模拟提交任务
            return {
                "success": True,
                "message": "任务已提交，任务ID: TASK_001"
            }
        
        elif action_id == "confirm_modify":
            # 模拟修改配置
            return {
                "success": True,
                "message": "配置已更新"
            }
        
        else:
            return {
                "success": True,
                "message": "操作成功"
            }
    
    def _save_params(self, mode: str, step_index: int, params: Dict[str, Any]):
        """保存参数到会话状态"""
        key = f"{mode}_{step_index}"
        self.session_state[key] = params
        print(f"[Agent] 保存参数: {key} = {params}")
    
    def get_session_state(self) -> Dict[str, Any]:
        """获取会话状态"""
        return self.session_state.copy()
    
    def clear_session_state(self):
        """清除会话状态"""
        self.session_state.clear()


# 全局 Agent 实例
agent_service = AgentService()
