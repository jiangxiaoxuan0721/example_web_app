"""事件处理 API 路由"""

from fastapi import APIRouter
from ..models import UIEvent, EventResponse
from ..services.agent import agent_service

router = APIRouter(prefix="/api", tags=["Events"])


@router.post("/events", response_model=EventResponse)
async def handle_events(event: UIEvent):
    """
    处理前端发送的事件

    这是架构的核心：前端只发射事件，后端 Agent 决策

    Args:
        event: UI 事件

    Returns:
        包含 Schema 或 Patch 的响应
    """
    try:
        # 调用 Agent 处理事件
        response = agent_service.process_event(event)

        # 过滤只包含 EventResponse 定义的字段，避免多余参数错误
        valid_fields = {"status", "message", "error", "schema", "patch"}
        filtered_response = {
            k: v for k, v in response.items()
            if k in valid_fields
        }

        return EventResponse(**filtered_response)

    except Exception as e:
        return EventResponse(
            status="error",
            error=str(e),
            message=None,
            schema=None,
            patch=None
        )


@router.get("/session/state")
async def get_session_state():
    """
    获取会话状态（调试用）
    """
    state = agent_service.get_session_state()
    return {
        "status": "success",
        "state": state
    }


@router.delete("/session/state")
async def clear_session_state():
    """
    清除会话状态（调试用）
    """
    agent_service.clear_session_state()
    return {
        "status": "success",
        "message": "会话状态已清除"
    }
