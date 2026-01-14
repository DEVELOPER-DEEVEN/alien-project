
"""
Data models for Network Web UI.

This package contains Pydantic models and enums used throughout the Web UI.
"""

from network.webui.models.enums import (
    WebSocketMessageType,
    RequestStatus,
)
from network.webui.models.requests import (
    DeviceAddRequest,
    WebSocketMessage,
    RequestMessage,
    ResetMessage,
    NextSessionMessage,
    StopTaskMessage,
    PingMessage,
)
from network.webui.models.responses import (
    StandardResponse,
    HealthResponse,
    DeviceAddResponse,
    WelcomeMessage,
    RequestReceivedMessage,
    RequestCompletedMessage,
    RequestFailedMessage,
    ResetAcknowledgedMessage,
    NextSessionAcknowledgedMessage,
    StopAcknowledgedMessage,
    PongMessage,
    ErrorMessage,
)

__all__ = [
    # Enums
    "WebSocketMessageType",
    "RequestStatus",
    # Requests
    "DeviceAddRequest",
    "WebSocketMessage",
    "RequestMessage",
    "ResetMessage",
    "NextSessionMessage",
    "StopTaskMessage",
    "PingMessage",
    # Responses
    "StandardResponse",
    "HealthResponse",
    "DeviceAddResponse",
    "WelcomeMessage",
    "RequestReceivedMessage",
    "RequestCompletedMessage",
    "RequestFailedMessage",
    "ResetAcknowledgedMessage",
    "NextSessionAcknowledgedMessage",
    "StopAcknowledgedMessage",
    "PongMessage",
    "ErrorMessage",
]
