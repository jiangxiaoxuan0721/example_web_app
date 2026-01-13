"""
MCP 工具定义
提供 AI 可调用的工具，用于控制前端 UI
"""

from typing import Dict, Any, Optional
import logging
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# 初始化 MCP Server
mcp = FastMCP(name="schema-ui-backend")


class MCPToolRegistry:
    """MCP 工具注册表，用于存储 WebSocket 连接管理器引用"""

    def __init__(self):
        self.connection_manager = None

    def set_connection_manager(self, manager):
        """设置连接管理器"""
        self.connection_manager = manager


# 全局工具注册表
tool_registry = MCPToolRegistry()


# ===========================
# MCP 工具定义
# ===========================

@mcp.tool()
async def render_page(page_key: str, mode: Optional[str] = None, step_index: Optional[int] = 0) -> Dict[str, Any]:
    """
    渲染页面，返回 UISchema
    
    这是 AI 调用的第一个工具，用于初始化或切换页面
    
    参数说明:
    - page_key (str): 必填，页面键，如 "mode_selection", "single_0", "batch_0" 等
    - mode (str): 可选，模式 ID，如 "single", "batch"
    - step_index (int): 可选，步骤索引，默认为 0
    
    返回:
    - 包含 UISchema 的字典
    
    使用场景:
    1. 初始化向导时：render_page(page_key="mode_selection")
    2. 选择模式后：render_page(page_key=f"{mode}_0", mode="single", step_index=0)
    3. 切换步骤时：render_page(page_key=f"{mode}_{step_index}", mode="single", step_index=1)
    """
    try:
        from ..fastapi.schemas import generate_mode_selection_schema, generate_step_schema
        
        # 如果 page_key 是 "mode_selection"，返回模式选择页面
        if page_key == "mode_selection":
            schema = generate_mode_selection_schema()
            logger.info(f"[MCP] 渲染页面: mode_selection")
            return {
                "success": True,
                "action": "render_page",
                "page_key": page_key,
                "schema": schema.model_dump()
            }
        
        # 否则，根据 mode 和 step_index 返回步骤页面
        if mode and step_index is not None:
            schema = generate_step_schema(mode, step_index)
            if schema:
                logger.info(f"[MCP] 渲染页面: {page_key} (mode={mode}, step={step_index})")
                return {
                    "success": True,
                    "action": "render_page",
                    "page_key": page_key,
                    "schema": schema.model_dump()
                }
            else:
                return {
                    "success": False,
                    "error": f"无法生成 Schema: mode={mode}, step={step_index}"
                }
        
        return {
            "success": False,
            "error": f"未知的页面键: {page_key}"
        }
    except Exception as e:
        logger.error(f"[MCP] render_page 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"渲染页面失败: {str(e)}"
        }


@mcp.tool()
async def patch_ui(patch: Dict[str, Any], page_key: Optional[str] = None) -> Dict[str, Any]:
    """
    打补丁到 UI，增量更新界面
    
    这是 AI 在推理后调用的工具，用于更新 UI 状态
    
    参数说明:
    - patch (Dict[str, Any]): 必填，补丁字典，键为 dot path，值为新值
      例如:
      {
        "state.params.speed": 150,
        "state.runtime.status": "running",
        "blocks.0.props.fields.0.value": "新值"
      }
    - page_key (str): 可选，页面键，用于标识要更新的页面
    
    返回:
    - 包含操作结果的字典
    
    使用场景:
    1. 更新字段值：patch_ui({"state.params.speed": 150})
    2. 更新状态：patch_ui({"state.runtime.status": "running"})
    3. 更新多个值：patch_ui({"state.params.speed": 150, "state.params.distance": 100})
    """
    try:
        logger.info(f"[MCP] 打补丁: {patch}")
        
        # 如果有连接管理器，发送到前端
        if tool_registry.connection_manager:
            response = await tool_registry.connection_manager.send_command(
                action="schema:patch",
                params={
                    "patch": patch,
                    "page_key": page_key
                }
            )
            return response
        else:
            # 没有连接管理器时，返回成功（用于纯 API 模式）
            logger.warning("[MCP] 没有连接管理器，补丁只记录不发送")
            return {
                "success": True,
                "action": "patch_ui",
                "patch": patch,
                "page_key": page_key,
                "message": "补丁已生成（无 WebSocket 连接）"
            }
    except Exception as e:
        logger.error(f"[MCP] patch_ui 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"打补丁失败: {str(e)}"
        }


@mcp.tool()
async def await_event(timeout: int = 30) -> Dict[str, Any]:
    """
    等待前端事件
    
    这是 AI 调用的阻塞工具，等待用户在界面上操作后触发事件
    
    参数说明:
    - timeout (int): 可选，超时时间（秒），默认 30 秒
    
    返回:
    - 包含前端事件的字典，格式为:
      {
        "success": True,
        "event": {
          "type": "field_change",
          "payload": {
            "fieldKey": "speed",
            "value": 150
          },
          "pageKey": "single_0",
          "timestamp": "2024-01-13T10:30:00Z"
        }
      }
    
    使用场景:
    1. 等待用户填写表单：await_event()
    2. 等待用户点击按钮：await_event(timeout=60)
    3. 等待模式选择：await_event()
    
    注意: 此函数会阻塞，直到前端发送事件或超时
    """
    try:
        logger.info(f"[MCP] 等待事件（超时: {timeout}秒）")
        
        # 如果有连接管理器，等待前端事件
        if tool_registry.connection_manager:
            response = await tool_registry.connection_manager.send_command(
                action="tool:await_event",
                params={
                    "timeout": timeout
                }
            )
            return response
        else:
            # 没有连接管理器时，返回错误
            return {
                "success": False,
                "error": "没有连接管理器，无法等待事件"
            }
    except Exception as e:
        logger.error(f"[MCP] await_event 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"等待事件失败: {str(e)}"
        }


@mcp.tool()
async def get_wizard_config() -> Dict[str, Any]:
    """
    获取 Wizard 配置
    
    返回完整的配置信息，包括模式和组件定义
    
    使用场景:
    - AI 需要了解可用的模式和组件
    - 验证配置是否正确加载
    """
    try:
        from ..config import config_manager
        
        config = config_manager.load_config()
        logger.info(f"[MCP] 获取配置: {len(config.get('modes', {}))} 个模式")
        
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        logger.error(f"[MCP] get_wizard_config 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"获取配置失败: {str(e)}"
        }


@mcp.tool()
async def get_modes() -> Dict[str, Any]:
    """
    获取所有模式
    
    返回所有可用的仿真模式及其配置
    
    使用场景:
    - AI 需要显示模式选择列表
    - 验证模式配置
    """
    try:
        from ..config import config_manager
        
        modes = config_manager.get_modes()
        logger.info(f"[MCP] 获取模式: {list(modes.keys())}")
        
        return {
            "success": True,
            "modes": modes
        }
    except Exception as e:
        logger.error(f"[MCP] get_modes 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"获取模式失败: {str(e)}"
        }


@mcp.tool()
async def get_mode(mode_id: str) -> Dict[str, Any]:
    """
    获取指定模式的详细信息
    
    参数说明:
    - mode_id (str): 必填，模式 ID，如 "single", "batch"
    
    使用场景:
    - AI 需要了解特定模式的配置
    - 获取模式的步骤信息
    """
    try:
        from ..config import config_manager
        
        mode = config_manager.get_mode(mode_id)
        if mode:
            logger.info(f"[MCP] 获取模式: {mode_id}")
            return {
                "success": True,
                "mode": mode,
                "mode_id": mode_id
            }
        else:
            return {
                "success": False,
                "error": f"模式不存在: {mode_id}"
            }
    except Exception as e:
        logger.error(f"[MCP] get_mode 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"获取模式失败: {str(e)}"
        }


@mcp.tool()
async def get_components() -> Dict[str, Any]:
    """
    获取所有组件定义
    
    返回所有可用的组件及其配置
    
    使用场景:
    - AI 需要了解可用的组件
    - 生成 Schema 时参考组件定义
    """
    try:
        from ..config import config_manager
        
        components = config_manager.get_components()
        logger.info(f"[MCP] 获取组件: {len(components)} 个")
        
        return {
            "success": True,
            "components": components
        }
    except Exception as e:
        logger.error(f"[MCP] get_components 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"获取组件失败: {str(e)}"
        }


@mcp.tool()
async def get_component(component_id: str) -> Dict[str, Any]:
    """
    获取指定组件的详细信息
    
    参数说明:
    - component_id (str): 必填，组件 ID
    
    使用场景:
    - AI 需要了解特定组件的配置
    - 获取组件的字段定义
    """
    try:
        from ..config import config_manager
        
        component = config_manager.get_component(component_id)
        if component:
            logger.info(f"[MCP] 获取组件: {component_id}")
            return {
                "success": True,
                "component": component,
                "component_id": component_id
            }
        else:
            return {
                "success": False,
                "error": f"组件不存在: {component_id}"
            }
    except Exception as e:
        logger.error(f"[MCP] get_component 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"获取组件失败: {str(e)}"
        }


@mcp.tool()
async def get_session_state() -> Dict[str, Any]:
    """
    获取会话状态
    
    返回当前会话的所有状态信息
    
    使用场景:
    - AI 需要了解当前会话状态
    - 调试和验证状态
    """
    try:
        from ..fastapi.services.agent import agent_service
        
        state = agent_service.get_session_state()
        logger.info(f"[MCP] 获取会话状态: {len(state)} 个键")
        
        return {
            "success": True,
            "state": state
        }
    except Exception as e:
        logger.error(f"[MCP] get_session_state 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"获取会话状态失败: {str(e)}"
        }


@mcp.tool()
async def clear_session_state() -> Dict[str, Any]:
    """
    清除会话状态
    
    清空当前会话的所有状态
    
    使用场景:
    - 重新开始向导
    - 重置会话状态
    """
    try:
        from ..fastapi.services.agent import agent_service
        
        agent_service.clear_session_state()
        logger.info("[MCP] 清除会话状态")
        
        return {
            "success": True,
            "message": "会话状态已清除"
        }
    except Exception as e:
        logger.error(f"[MCP] clear_session_state 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"清除会话状态失败: {str(e)}"
        }


@mcp.tool()
async def reload_config() -> Dict[str, Any]:
    """
    重新加载配置文件
    
    用于配置文件更新后刷新配置
    
    使用场景:
    - 配置文件被修改后
    - 需要应用新的配置
    """
    try:
        from ..config import config_manager
        
        config_manager.reload()
        logger.info("[MCP] 重新加载配置")
        
        return {
            "success": True,
            "message": "配置已重新加载"
        }
    except Exception as e:
        logger.error(f"[MCP] reload_config 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"重新加载配置失败: {str(e)}"
        }


@mcp.tool()
async def get_server_info() -> Dict[str, Any]:
    """
    获取服务器信息
    
    返回 MCP 服务器的状态信息
    
    使用场景:
    - 验证服务器是否正常运行
    - 检查服务器配置
    """
    try:
        from ..config import settings
        import time
        
        info = {
            "name": settings.app_name,
            "version": settings.app_version,
            "mcp_enabled": settings.mcp_enabled,
            "mcp_server_name": settings.mcp_server_name,
            "mcp_server_version": settings.mcp_server_version,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"[MCP] 获取服务器信息: {info['name']}")
        
        return {
            "success": True,
            "info": info
        }
    except Exception as e:
        logger.error(f"[MCP] get_server_info 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"获取服务器信息失败: {str(e)}"
        }


@mcp.tool()
async def validate_params(mode_id: str, step_index: int, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证参数
    
    验证给定模式的步骤参数是否有效
    
    参数说明:
    - mode_id (str): 必填，模式 ID
    - step_index (int): 必填，步骤索引
    - params (Dict[str, Any]): 必填，要验证的参数
    
    使用场景:
    - 用户提交参数前验证
    - AI 推理时验证参数有效性
    """
    try:
        from ..config import config_manager
        
        step_config = config_manager.get_step(mode_id, step_index)
        if not step_config:
            return {
                "success": False,
                "error": f"步骤不存在: {mode_id}, {step_index}"
            }
        
        # 这里可以添加具体的验证逻辑
        # 目前只是简单返回成功，实际验证可以根据params中的值进行
        logger.info(f"[MCP] 验证参数: {mode_id}, step={step_index}, params={params}")
        
        return {
            "success": True,
            "valid": True,
            "message": "参数验证通过"
        }
    except Exception as e:
        logger.error(f"[MCP] validate_params 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"验证参数失败: {str(e)}"
        }


@mcp.tool()
async def process_event(event_type: str, payload: Dict[str, Any], page_key: Optional[str] = None) -> Dict[str, Any]:
    """
    处理前端事件
    
    这是 MCP 版本的事件处理工具，类似于 REST API 的 /api/events
    
    参数说明:
    - event_type (str): 必填，事件类型，如 "field_change", "action_click", "select_mode"
    - payload (Dict[str, Any]): 必填，事件载荷
    - page_key (str): 可选，页面键
    
    使用场景:
    - 处理前端发送的事件
    - 触发 Agent 决策逻辑
    - 返回 Schema 或 Patch
    """
    try:
        from ..fastapi.models import UIEvent, EventType, EventPayload
        from ..fastapi.services.agent import agent_service
        
        # 构建 UIEvent 对象
        event = UIEvent(
            type=EventType(event_type),
            payload=EventPayload(**payload),
            pageKey=page_key
        )
        
        # 调用 Agent 处理事件
        response = agent_service.process_event(event)
        
        logger.info(f"[MCP] 处理事件: {event_type}")
        
        return {
            "success": True,
            "event_type": event_type,
            **response
        }
    except Exception as e:
        logger.error(f"[MCP] process_event 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"处理事件失败: {str(e)}"
        }


@mcp.tool()
async def execute_business_logic(action_id: str, mode: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行业务逻辑
    
    执行指定的业务逻辑操作
    
    参数说明:
    - action_id (str): 必填，操作 ID，如 "confirm_execute", "confirm_submit"
    - mode (str): 必填，模式 ID
    - params (Dict[str, Any]): 必填，操作参数
    
    使用场景:
    - 用户确认执行操作
    - 触发后端服务调用
    - 执行仿真计算等
    """
    try:
        from ..fastapi.services.agent import agent_service
        
        result = agent_service._execute_business_logic(action_id, mode, params)
        
        logger.info(f"[MCP] 执行业务逻辑: {action_id}")
        
        return {
            "success": True,
            "action_id": action_id,
            "mode": mode,
            "result": result
        }
    except Exception as e:
        logger.error(f"[MCP] execute_business_logic 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"执行业务逻辑失败: {str(e)}"
        }


@mcp.tool()
async def save_session_params(mode: str, step_index: int, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    保存会话参数
    
    将参数保存到会话状态中
    
    参数说明:
    - mode (str): 必填，模式 ID
    - step_index (int): 必填，步骤索引
    - params (Dict[str, Any]): 必填，参数字典
    
    使用场景:
    - 用户填写完表单后保存
    - 进入下一步前保存当前步骤参数
    """
    try:
        from ..fastapi.services.agent import agent_service
        
        agent_service._save_params(mode, step_index, params)
        
        logger.info(f"[MCP] 保存会话参数: {mode}, step={step_index}")
        
        return {
            "success": True,
            "message": "参数已保存",
            "mode": mode,
            "step_index": step_index
        }
    except Exception as e:
        logger.error(f"[MCP] save_session_params 错误: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"保存会话参数失败: {str(e)}"
        }
