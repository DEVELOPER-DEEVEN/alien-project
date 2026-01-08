# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
network v2 Client Package

This package provides the client-side implementation for the network v2 system,
enabling multi-device orchestration and task distribution across Alien WebSocket servers.

Main Components:
- networkClient: Device management and connection support component
- networkDeviceManager: Low-level device registration and connection management
- networkConfig: Configuration loading from files, CLI, and environment variables

Note: For task execution, use the main clusterClient which provides DAG orchestration
and complex task management. networkClient serves as a device management
support component.

Example Usage:

    # Device management
    await client.connect_device("windows_device")
    devices = client.get_connected_devices()
    status = client.get_network_info()

    # For task execution, use clusterClient instead:
    # from cluster import clusterClient
    # cluster = clusterClient()
    # result = await cluster.process_request("take a screenshot")
"""

from .network_client import networkClient
from .device_manager import networkDeviceManager
from .components import AgentProfile, DeviceStatus, TaskRequest
from .config_loader import networkConfig, DeviceConfig
from .support import (
    StatusManager,
    ClientConfigManager,
)

__all__ = [
    "networkClient",
    "networkDeviceManager",
    "networkConfig",
    "DeviceConfig",
    "AgentProfile",
    "DeviceStatus",
    "TaskRequest",
    # Support components
    "StatusManager",
    "ClientConfigManager",
]

__version__ = "2.0.0"
