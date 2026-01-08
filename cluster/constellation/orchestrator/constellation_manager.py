# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
network Manager for managing Tasknetwork lifecycle and state.

This module handles the management logic for Tasknetwork objects,
including device assignment, status tracking, and execution coordination.
"""

import logging
from typing import Any, Dict, List, Optional

from cluster.client.device_manager import networkDeviceManager

from ..task_network import Tasknetwork


class networkManager:
    """
    Manages Tasknetwork lifecycle, device assignments, and execution state.

    This class handles:
    - Device assignment strategies
    - network status tracking
    - Resource management
    - Execution coordination
    """

    def __init__(
        self,
        device_manager: Optional[networkDeviceManager] = None,
        enable_logging: bool = True,
    ):
        """
        Initialize the networkManager.

        :param device_manager: Optional device manager for device operations
        :param enable_logging: Whether to enable logging
        """
        self._device_manager = device_manager
        self._logger = logging.getLogger(__name__) if enable_logging else None

        # Track managed networks
        self._managed_networks: Dict[str, Tasknetwork] = {}
        self._network_metadata: Dict[str, Dict[str, Any]] = {}

    def set_device_manager(self, device_manager: networkDeviceManager) -> None:
        """
        Set the device manager for device operations.

        :param device_manager: The network device manager instance
        """
        self._device_manager = device_manager
        if self._logger:
            self._logger.info("Device manager updated")

    def register_network(
        self,
        network: Tasknetwork,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Register a network for management.

        :param network: Tasknetwork to manage
        :param metadata: Optional metadata for the network
        :return: network ID
        """
        network_id = network.network_id
        self._managed_networks[network_id] = network
        self._network_metadata[network_id] = metadata or {}

        if self._logger:
            self._logger.info(
                f"Registered network '{network.name}' ({network_id})"
            )

        return network_id

    def unregister_network(self, network_id: str) -> bool:
        """
        Unregister a network from management.

        :param network_id: ID of network to unregister
        :return: True if unregistered, False if not found
        """
        if network_id in self._managed_networks:
            network = self._managed_networks[network_id]
            del self._managed_networks[network_id]
            del self._network_metadata[network_id]

            if self._logger:
                self._logger.info(
                    f"Unregistered network '{network.name}' ({network_id})"
                )
            return True

        return False

    def get_network(self, network_id: str) -> Optional[Tasknetwork]:
        """
        Get a managed network by ID.

        :param network_id: network ID
        :return: Tasknetwork if found, None otherwise
        """
        return self._managed_networks.get(network_id)

    def list_networks(self) -> List[Dict[str, Any]]:
        """
        List all managed networks with their basic information.

        :return: List of network information dictionaries
        """
        result = []
        for network_id, network in self._managed_networks.items():
            metadata = self._network_metadata.get(network_id, {})
            result.append(
                {
                    "network_id": network_id,
                    "name": network.name,
                    "state": network.state.value,
                    "task_count": network.task_count,
                    "dependency_count": network.dependency_count,
                    "metadata": metadata,
                }
            )

        return result

    async def assign_devices_automatically(
        self,
        network: Tasknetwork,
        strategy: str = "round_robin",
        device_preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Automatically assign devices to tasks in a network.

        :param network: Target network
        :param strategy: Assignment strategy ("round_robin", "capability_match", "load_balance")
        :param device_preferences: Optional device preferences by task ID
        :return: Dictionary mapping task IDs to assigned device IDs
        """
        if not self._device_manager:
            raise ValueError("Device manager not available for device assignment")

        available_devices = await self._get_available_devices()
        if not available_devices:
            raise ValueError("No available devices for assignment")

        if self._logger:
            self._logger.info(
                f"Assigning devices to network '{network.name}' "
                f"using strategy '{strategy}'"
            )

        assignments = {}

        if strategy == "round_robin":
            assignments = await self._assign_round_robin(
                network, available_devices, device_preferences
            )
        elif strategy == "capability_match":
            assignments = await self._assign_capability_match(
                network, available_devices, device_preferences
            )
        elif strategy == "load_balance":
            assignments = await self._assign_load_balance(
                network, available_devices, device_preferences
            )
        else:
            raise ValueError(f"Unknown assignment strategy: {strategy}")

        # Apply assignments to tasks
        for task_id, device_id in assignments.items():
            task = network.get_task(task_id)
            if task:
                task.target_device_id = device_id

        if self._logger:
            self._logger.info(f"Assigned {len(assignments)} tasks to devices")

        return assignments

    async def _assign_round_robin(
        self,
        network: Tasknetwork,
        available_devices: List[Dict[str, Any]],
        preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Round robin device assignment strategy."""
        assignments = {}
        device_index = 0

        for task_id, task in network.tasks.items():
            # Check preferences first
            if preferences and task_id in preferences:
                preferred_device = preferences[task_id]
                if any(d["device_id"] == preferred_device for d in available_devices):
                    assignments[task_id] = preferred_device
                    continue

            # Round robin assignment
            device = available_devices[device_index % len(available_devices)]
            assignments[task_id] = device["device_id"]
            device_index += 1

        return assignments

    async def _assign_capability_match(
        self,
        network: Tasknetwork,
        available_devices: List[Dict[str, Any]],
        preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Capability-based device assignment strategy."""
        assignments = {}

        for task_id, task in network.tasks.items():
            # Check preferences first
            if preferences and task_id in preferences:
                preferred_device = preferences[task_id]
                if any(d["device_id"] == preferred_device for d in available_devices):
                    assignments[task_id] = preferred_device
                    continue

            # Find devices matching task requirements
            matching_devices = []

            if task.device_type:
                matching_devices = [
                    d
                    for d in available_devices
                    if d.get("device_type") == task.device_type.value
                ]

            # Fall back to any available device if no matches
            if not matching_devices:
                matching_devices = available_devices

            # Choose first matching device
            if matching_devices:
                assignments[task_id] = matching_devices[0]["device_id"]

        return assignments

    async def _assign_load_balance(
        self,
        network: Tasknetwork,
        available_devices: List[Dict[str, Any]],
        preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Load-balanced device assignment strategy."""
        assignments = {}
        device_load = {d["device_id"]: 0 for d in available_devices}

        for task_id, task in network.tasks.items():
            # Check preferences first
            if preferences and task_id in preferences:
                preferred_device = preferences[task_id]
                if any(d["device_id"] == preferred_device for d in available_devices):
                    assignments[task_id] = preferred_device
                    device_load[preferred_device] += 1
                    continue

            # Find device with lowest load
            min_load_device = min(device_load.keys(), key=lambda d: device_load[d])
            assignments[task_id] = min_load_device
            device_load[min_load_device] += 1

        return assignments

    async def get_network_status(
        self, network_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed status of a managed network.

        :param network_id: network ID
        :return: Status information dictionary or None if not found
        """
        network = self._managed_networks.get(network_id)
        if not network:
            return None

        metadata = self._network_metadata.get(network_id, {})

        return {
            "network_id": network_id,
            "name": network.name,
            "state": network.state.value,
            "statistics": network.get_statistics(),
            "ready_tasks": [task.task_id for task in network.get_ready_tasks()],
            "running_tasks": [
                task.task_id for task in network.get_running_tasks()
            ],
            "completed_tasks": [
                task.task_id for task in network.get_completed_tasks()
            ],
            "failed_tasks": [task.task_id for task in network.get_failed_tasks()],
            "metadata": metadata,
        }

    async def get_available_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of available devices from device manager.

        :return: List of available device information
        """
        return await self._get_available_devices()

    async def _get_available_devices(self) -> List[Dict[str, Any]]:
        """Internal method to get available devices."""
        if not self._device_manager:
            return []

        try:
            connected_device_ids = self._device_manager.get_connected_devices()
            devices = []

            for device_id in connected_device_ids:
                device_info = self._device_manager.device_registry.get_device_info(
                    device_id
                )
                if device_info:
                    devices.append(
                        {
                            "device_id": device_id,
                            "device_type": getattr(
                                device_info, "device_type", "unknown"
                            ),
                            "capabilities": getattr(device_info, "capabilities", []),
                            "status": "connected",
                            "metadata": getattr(device_info, "metadata", {}),
                        }
                    )

            return devices
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to get available devices: {e}")
            return []

    def validate_network_assignments(
        self, network: Tasknetwork
    ) -> tuple[bool, List[str]]:
        """
        Validate that all tasks in a network have valid device assignments.

        :param network: network to validate
        :return: Tuple of (is_valid, list_of_errors)
        """
        errors = []

        for task_id, task in network.tasks.items():
            if not task.target_device_id:
                errors.append(f"Task '{task_id}' has no device assignment")

        is_valid = len(errors) == 0

        if self._logger:
            if is_valid:
                self._logger.info(
                    f"All tasks in network '{network.name}' have valid assignments"
                )
            else:
                self._logger.warning(
                    f"network '{network.name}' has {len(errors)} assignment errors"
                )

        return is_valid, errors

    def get_task_device_info(
        self, network: Tasknetwork, task_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get device information for a specific task.

        :param network: Target network
        :param task_id: Task ID
        :return: Device information or None if not assigned/found
        """
        task = network.get_task(task_id)
        if not task or not task.target_device_id:
            return None

        # Get device info from device manager
        if self._device_manager:
            try:
                device_info = self._device_manager.device_registry.get_device_info(
                    task.target_device_id
                )
                if device_info:
                    return {
                        "device_id": task.target_device_id,
                        "device_type": getattr(device_info, "device_type", "unknown"),
                        "capabilities": getattr(device_info, "capabilities", []),
                        "metadata": getattr(device_info, "metadata", {}),
                    }
            except Exception as e:
                if self._logger:
                    self._logger.error(
                        f"Failed to get device info for task '{task_id}': {e}"
                    )

        return None

    def reassign_task_device(
        self,
        network: Tasknetwork,
        task_id: str,
        new_device_id: str,
    ) -> bool:
        """
        Reassign a task to a different device.

        :param network: Target network
        :param task_id: Task ID to reassign
        :param new_device_id: New device ID
        :return: True if reassigned successfully, False otherwise
        """
        task = network.get_task(task_id)
        if not task:
            return False

        old_device_id = task.target_device_id
        task.target_device_id = new_device_id

        if self._logger:
            self._logger.info(
                f"Reassigned task '{task_id}' from device '{old_device_id}' to '{new_device_id}'"
            )

        return True

    def clear_device_assignments(self, network: Tasknetwork) -> int:
        """
        Clear all device assignments from a network.

        :param network: Target network
        :return: Number of assignments cleared
        """
        cleared_count = 0

        for task in network.tasks.values():
            if task.target_device_id:
                task.target_device_id = None
                cleared_count += 1

        if self._logger:
            self._logger.info(
                f"Cleared {cleared_count} device assignments from network '{network.name}'"
            )

        return cleared_count

    def get_device_utilization(
        self, network: Tasknetwork
    ) -> Dict[str, int]:
        """
        Get device utilization statistics for a network.

        :param network: Target network
        :return: Dictionary mapping device IDs to task counts
        """
        utilization = {}

        for task in network.tasks.values():
            if task.target_device_id:
                utilization[task.target_device_id] = (
                    utilization.get(task.target_device_id, 0) + 1
                )

        return utilization
