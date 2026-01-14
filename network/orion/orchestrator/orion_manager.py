
"""
Orion Manager for managing TaskOrion lifecycle and state.

This module handles the management logic for TaskOrion objects,
including device assignment, status tracking, and execution coordination.
"""

import logging
from typing import Any, Dict, List, Optional

from network.client.device_manager import OrionDeviceManager

from ..task_orion import TaskOrion


class OrionManager:
    """
    Manages TaskOrion lifecycle, device assignments, and execution state.

    This class handles:
    - Device assignment strategies
    - Orion status tracking
    - Resource management
    - Execution coordination
    """

    def __init__(
        self,
        device_manager: Optional[OrionDeviceManager] = None,
        enable_logging: bool = True,
    ):
        """
        Initialize the OrionManager.

        :param device_manager: Optional device manager for device operations
        :param enable_logging: Whether to enable logging
        """
        self._device_manager = device_manager
        self._logger = logging.getLogger(__name__) if enable_logging else None

        # Track managed orions
        self._managed_orions: Dict[str, TaskOrion] = {}
        self._orion_metadata: Dict[str, Dict[str, Any]] = {}

    def set_device_manager(self, device_manager: OrionDeviceManager) -> None:
        """
        Set the device manager for device operations.

        :param device_manager: The orion device manager instance
        """
        self._device_manager = device_manager
        if self._logger:
            self._logger.info("Device manager updated")

    def register_orion(
        self,
        orion: TaskOrion,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Register a orion for management.

        :param orion: TaskOrion to manage
        :param metadata: Optional metadata for the orion
        :return: Orion ID
        """
        orion_id = orion.orion_id
        self._managed_orions[orion_id] = orion
        self._orion_metadata[orion_id] = metadata or {}

        if self._logger:
            self._logger.info(
                f"Registered orion '{orion.name}' ({orion_id})"
            )

        return orion_id

    def unregister_orion(self, orion_id: str) -> bool:
        """
        Unregister a orion from management.

        :param orion_id: ID of orion to unregister
        :return: True if unregistered, False if not found
        """
        if orion_id in self._managed_orions:
            orion = self._managed_orions[orion_id]
            del self._managed_orions[orion_id]
            del self._orion_metadata[orion_id]

            if self._logger:
                self._logger.info(
                    f"Unregistered orion '{orion.name}' ({orion_id})"
                )
            return True

        return False

    def get_orion(self, orion_id: str) -> Optional[TaskOrion]:
        """
        Get a managed orion by ID.

        :param orion_id: Orion ID
        :return: TaskOrion if found, None otherwise
        """
        return self._managed_orions.get(orion_id)

    def list_orions(self) -> List[Dict[str, Any]]:
        """
        List all managed orions with their basic information.

        :return: List of orion information dictionaries
        """
        result = []
        for orion_id, orion in self._managed_orions.items():
            metadata = self._orion_metadata.get(orion_id, {})
            result.append(
                {
                    "orion_id": orion_id,
                    "name": orion.name,
                    "state": orion.state.value,
                    "task_count": orion.task_count,
                    "dependency_count": orion.dependency_count,
                    "metadata": metadata,
                }
            )

        return result

    async def assign_devices_automatically(
        self,
        orion: TaskOrion,
        strategy: str = "round_robin",
        device_preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Automatically assign devices to tasks in a orion.

        :param orion: Target orion
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
                f"Assigning devices to orion '{orion.name}' "
                f"using strategy '{strategy}'"
            )

        assignments = {}

        if strategy == "round_robin":
            assignments = await self._assign_round_robin(
                orion, available_devices, device_preferences
            )
        elif strategy == "capability_match":
            assignments = await self._assign_capability_match(
                orion, available_devices, device_preferences
            )
        elif strategy == "load_balance":
            assignments = await self._assign_load_balance(
                orion, available_devices, device_preferences
            )
        else:
            raise ValueError(f"Unknown assignment strategy: {strategy}")

        # Apply assignments to tasks
        for task_id, device_id in assignments.items():
            task = orion.get_task(task_id)
            if task:
                task.target_device_id = device_id

        if self._logger:
            self._logger.info(f"Assigned {len(assignments)} tasks to devices")

        return assignments

    async def _assign_round_robin(
        self,
        orion: TaskOrion,
        available_devices: List[Dict[str, Any]],
        preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Round robin device assignment strategy."""
        assignments = {}
        device_index = 0

        for task_id, task in orion.tasks.items():
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
        orion: TaskOrion,
        available_devices: List[Dict[str, Any]],
        preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Capability-based device assignment strategy."""
        assignments = {}

        for task_id, task in orion.tasks.items():
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
        orion: TaskOrion,
        available_devices: List[Dict[str, Any]],
        preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Load-balanced device assignment strategy."""
        assignments = {}
        device_load = {d["device_id"]: 0 for d in available_devices}

        for task_id, task in orion.tasks.items():
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

    async def get_orion_status(
        self, orion_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed status of a managed orion.

        :param orion_id: Orion ID
        :return: Status information dictionary or None if not found
        """
        orion = self._managed_orions.get(orion_id)
        if not orion:
            return None

        metadata = self._orion_metadata.get(orion_id, {})

        return {
            "orion_id": orion_id,
            "name": orion.name,
            "state": orion.state.value,
            "statistics": orion.get_statistics(),
            "ready_tasks": [task.task_id for task in orion.get_ready_tasks()],
            "running_tasks": [
                task.task_id for task in orion.get_running_tasks()
            ],
            "completed_tasks": [
                task.task_id for task in orion.get_completed_tasks()
            ],
            "failed_tasks": [task.task_id for task in orion.get_failed_tasks()],
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

    def validate_orion_assignments(
        self, orion: TaskOrion
    ) -> tuple[bool, List[str]]:
        """
        Validate that all tasks in a orion have valid device assignments.

        :param orion: Orion to validate
        :return: Tuple of (is_valid, list_of_errors)
        """
        errors = []

        for task_id, task in orion.tasks.items():
            if not task.target_device_id:
                errors.append(f"Task '{task_id}' has no device assignment")

        is_valid = len(errors) == 0

        if self._logger:
            if is_valid:
                self._logger.info(
                    f"All tasks in orion '{orion.name}' have valid assignments"
                )
            else:
                self._logger.warning(
                    f"Orion '{orion.name}' has {len(errors)} assignment errors"
                )

        return is_valid, errors

    def get_task_device_info(
        self, orion: TaskOrion, task_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get device information for a specific task.

        :param orion: Target orion
        :param task_id: Task ID
        :return: Device information or None if not assigned/found
        """
        task = orion.get_task(task_id)
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
        orion: TaskOrion,
        task_id: str,
        new_device_id: str,
    ) -> bool:
        """
        Reassign a task to a different device.

        :param orion: Target orion
        :param task_id: Task ID to reassign
        :param new_device_id: New device ID
        :return: True if reassigned successfully, False otherwise
        """
        task = orion.get_task(task_id)
        if not task:
            return False

        old_device_id = task.target_device_id
        task.target_device_id = new_device_id

        if self._logger:
            self._logger.info(
                f"Reassigned task '{task_id}' from device '{old_device_id}' to '{new_device_id}'"
            )

        return True

    def clear_device_assignments(self, orion: TaskOrion) -> int:
        """
        Clear all device assignments from a orion.

        :param orion: Target orion
        :return: Number of assignments cleared
        """
        cleared_count = 0

        for task in orion.tasks.values():
            if task.target_device_id:
                task.target_device_id = None
                cleared_count += 1

        if self._logger:
            self._logger.info(
                f"Cleared {cleared_count} device assignments from orion '{orion.name}'"
            )

        return cleared_count

    def get_device_utilization(
        self, orion: TaskOrion
    ) -> Dict[str, int]:
        """
        Get device utilization statistics for a orion.

        :param orion: Target orion
        :return: Dictionary mapping device IDs to task counts
        """
        utilization = {}

        for task in orion.tasks.values():
            if task.target_device_id:
                utilization[task.target_device_id] = (
                    utilization.get(task.target_device_id, 0) + 1
                )

        return utilization
