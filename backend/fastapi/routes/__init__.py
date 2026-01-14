"""FastAPI 路由模块"""

from .event_routes import register_event_routes
from .patch_routes import register_patch_routes
from .schema_routes import register_schema_routes
from .websocket_routes import register_websocket_routes
from .events import router as events_router

__all__ = [
    "register_event_routes",
    "register_patch_routes", 
    "register_schema_routes",
    "register_websocket_routes",
    "events_router"
]