# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
cluster Web UI Module.

Provides a modern web interface for the cluster Framework with real-time
event streaming via WebSocket.
"""

from .server import app, start_server, set_cluster_session
from .websocket_observer import WebSocketObserver

__all__ = [
    "app",
    "start_server",
    "set_cluster_session",
    "WebSocketObserver",
]
