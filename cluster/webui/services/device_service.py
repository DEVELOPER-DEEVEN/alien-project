# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Device management service for cluster Web UI.

This service handles device-related operations including registration,
configuration management, and device snapshot creation.
"""

import logging
from typing import Any, Dict, Optional

from cluster.webui.dependencies import AppState


class DeviceService:
    """
    Service for managing devices in the cluster framework.

    Provides methods to interact with the device manager, create device snapshots,
    and manage device lifecycle operations.
    """

    def __init__(self, app_state: AppState) -> None:
        """
        Initialize the device service.

        :param app_state: Application state containing cluster client references
        """
        self.app_state = app_state
        self.logger: logging.Logger = logging.getLogger(__name__)

    def build_device_snapshot(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Construct a serializable snapshot of all known devices.

        Retrieves device information from the cluster client's device manager
        and formats it for transmission to the frontend.

        :return: Dictionary mapping device IDs to device information, or None if unavailable
        """
        cluster_client = self.app_state.cluster_client
        if not cluster_client:
            self.logger.warning("cluster client not available for device snapshot")
            return None

        # Get network client from cluster client
        network_client = getattr(cluster_client, "_client", None)
        if not network_client:
            self.logger.warning("network client not available")
            return None

        # Get device manager from network client
        device_manager = getattr(network_client, "device_manager", None)
        if not device_manager:
            self.logger.warning("Device manager not available")
            return None

        try:
            snapshot: Dict[str, Dict[str, Any]] = {}
            for device_id, device in device_manager.get_all_devices().items():
                snapshot[device_id] = {
                    "device_id": device.device_id,
                    "status": getattr(device.status, "value", str(device.status)),
                    "os": device.os,
                    "server_url": device.server_url,
                    "capabilities": (
                        list(device.capabilities) if device.capabilities else []
                    ),
                    "metadata": dict(device.metadata) if device.metadata else {},
                    "last_heartbeat": (
                        device.last_heartbeat.isoformat()
                        if device.last_heartbeat
                        else None
                    ),
                    "connection_attempts": device.connection_attempts,
                    "max_retries": device.max_retries,
                    "current_task_id": device.current_task_id,
                }

            self.logger.debug(f"Built device snapshot with {len(snapshot)} devices")
            return snapshot if snapshot else None

        except Exception as exc:
            self.logger.warning(
                f"Failed to build device snapshot: {exc}", exc_info=True
            )
            return None

    def get_device_manager(self) -> Optional[Any]:
        """
        Get the device manager from the cluster client.

        :return: Device manager instance or None if not available
        """
        cluster_client = self.app_state.cluster_client
        if not cluster_client:
            return None

        network_client = getattr(cluster_client, "_client", None)
        if not network_client:
            return None

        return getattr(network_client, "device_manager", None)

    async def register_and_connect_device(
        self,
        device_id: str,
        server_url: str,
        os: str,
        capabilities: list,
        metadata: Optional[Dict[str, Any]],
        max_retries: int,
        auto_connect: bool,
    ) -> bool:
        """
        Register a device with the device manager and optionally connect to it.

        :param device_id: Unique identifier for the device
        :param server_url: URL of the device's server endpoint
        :param os: Operating system of the device
        :param capabilities: List of capabilities the device supports
        :param metadata: Additional metadata about the device
        :param max_retries: Maximum number of connection retry attempts
        :param auto_connect: Whether to automatically connect to the device
        :return: True if registration and connection succeeded, False otherwise
        """
        device_manager = self.get_device_manager()
        if not device_manager:
            self.logger.warning("Device manager not available for device registration")
            return False

        try:
            # Register the device with device manager
            device_manager.device_registry.register_device(
                device_id=device_id,
                server_url=server_url,
                os=os,
                capabilities=capabilities,
                metadata=metadata or {},
                max_retries=max_retries,
            )
            self.logger.info(f"✅ Device '{device_id}' registered with device manager")

            # If auto_connect is enabled, try to connect
            if auto_connect:
                import asyncio

                asyncio.create_task(device_manager.connect_device(device_id))
                self.logger.info(f"🔄 Initiated connection for device '{device_id}'")

            return True

        except Exception as e:
            self.logger.warning(
                f"⚠️ Failed to register/connect device with manager: {e}"
            )
            return False
