
"""
Routers for Network Web UI.

This package contains FastAPI routers that define API endpoints
and WebSocket endpoints for the Web UI.
"""

from network.webui.routers.health import router as health_router
from network.webui.routers.devices import router as devices_router
from network.webui.routers.websocket import router as websocket_router

__all__ = [
    "health_router",
    "devices_router",
    "websocket_router",
]
