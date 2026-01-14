
"""
Network Web UI Module.

Provides a modern web interface for the Network Framework with real-time
event streaming via WebSocket.
"""

from .server import app, start_server, set_network_session
from .websocket_observer import WebSocketObserver

__all__ = [
    "app",
    "start_server",
    "set_network_session",
    "WebSocketObserver",
]
