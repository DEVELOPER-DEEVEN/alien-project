
"""
Orion v2 Client Package

This package provides the client-side implementation for the Orion v2 system,
enabling multi-device orchestration and task distribution across ALIEN WebSocket servers.

Main Components:
- OrionClient: Device management and connection support component
- OrionDeviceManager: Low-level device registration and connection management
- OrionConfig: Configuration loading from files, CLI, and environment variables

Note: For task execution, use the main NetworkClient which provides DAG orchestration
and complex task management. OrionClient serves as a device management
support component.

Example Usage:

    # Device management
    await client.connect_device("windows_device")
    devices = client.get_connected_devices()
    status = client.get_orion_info()

    # For task execution, use NetworkClient instead:
    # from network import NetworkClient
    # network = NetworkClient()
    # result = await network.process_request("take a screenshot")
"""

from .orion_client import OrionClient
from .device_manager import OrionDeviceManager
from .components import AgentProfile, DeviceStatus, TaskRequest
from .config_loader import OrionConfig, DeviceConfig
from .support import (
    StatusManager,
    ClientConfigManager,
)

__all__ = [
    "OrionClient",
    "OrionDeviceManager",
    "OrionConfig",
    "DeviceConfig",
    "AgentProfile",
    "DeviceStatus",
    "TaskRequest",
    # Support components
    "StatusManager",
    "ClientConfigManager",
]

__version__ = "2.0.0"
