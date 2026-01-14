
"""
Handlers for Network Web UI.

This package contains handlers for processing various types of messages
and requests, particularly WebSocket message handlers.
"""

from network.webui.handlers.websocket_handlers import WebSocketMessageHandler

__all__ = [
    "WebSocketMessageHandler",
]
