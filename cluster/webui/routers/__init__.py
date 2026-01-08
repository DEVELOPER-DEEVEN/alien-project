# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Routers for cluster Web UI.

This package contains FastAPI routers that define API endpoints
and WebSocket endpoints for the Web UI.
"""

from cluster.webui.routers.health import router as health_router
from cluster.webui.routers.devices import router as devices_router
from cluster.webui.routers.websocket import router as websocket_router

__all__ = [
    "health_router",
    "devices_router",
    "websocket_router",
]
