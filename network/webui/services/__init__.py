
"""
Services for Network Web UI.

This package contains business logic services that encapsulate
operations and interact with the Network framework.
"""

from network.webui.services.device_service import DeviceService
from network.webui.services.network_service import NetworkService
from network.webui.services.config_service import ConfigService

__all__ = [
    "DeviceService",
    "NetworkService",
    "ConfigService",
]
