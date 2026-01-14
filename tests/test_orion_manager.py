
"""
Unit tests for OrionManager.

Tests device assignment, status tracking, and resource management
for TaskOrion objects.
"""

import asyncio
import pytest
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock

from network.orion.orchestrator.orion_manager import (
    OrionManager,
)
from network.orion.enums import TaskStatus, DeviceType
from network.orion.task_orion import TaskOrion
from network.orion.task_star import TaskStar


class MockDeviceManager:
    """Mock device manager for testing."""

    def __init__(self):
        self.device_registry = Mock()
        self._connected_devices = ["device1", "device2", "device3"]

    def get_connected_devices(self):
        return self._connected_devices.copy()


class MockAgentProfile:
    """Mock device info for testing."""

    def __init__(self, device_id: str, device_type: str = "desktop"):
        self.device_id = device_id
        self.device_type = device_type
        self.capabilities = ["ui_automation", "web_browsing"]
        self.metadata = {"platform": "windows", "version": "11"}


class TestOrionManager:
    """Test cases for OrionManager class."""

    @pytest.fixture
    def mock_device_manager(self):
        """Create a mock device manager for testing."""
        device_manager = MockDeviceManager()

        # Set up device registry mock
        def get_device_info(device_id):
            if device_id in device_manager._connected_devices:
                return MockAgentProfile(device_id)
            return None

        device_manager.device_registry.get_device_info.side_effect = get_device_info
        return device_manager

    @pytest.fixture
    def manager(self, mock_device_manager):
        """Create a OrionManager instance for testing."""
        return OrionManager(mock_device_manager, enable_logging=False)

    @pytest.fixture
    def manager_no_device(self):
        """Create a OrionManager without device manager."""
        return OrionManager(enable_logging=False)

    @pytest.fixture
    def sample_orion(self):
        """Create a sample orion for testing."""
        orion = TaskOrion(name="Test Orion")

        # Add tasks
        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        task3 = TaskStar(task_id="task3", description="Third task")

        orion.add_task(task1)
        orion.add_task(task2)
        orion.add_task(task3)

        return orion

    def test_init_with_device_manager(self, mock_device_manager):
        """Test initialization with device manager."""
        manager = OrionManager(mock_device_manager, enable_logging=True)

        assert manager._device_manager is mock_device_manager
        assert manager._logger is not None

    def test_init_without_device_manager(self):
        """Test initialization without device manager."""
        manager = OrionManager(enable_logging=False)

        assert manager._device_manager is None
        assert manager._logger is None

    def test_set_device_manager(self, manager_no_device, mock_device_manager):
        """Test setting device manager after initialization."""
        manager_no_device.set_device_manager(mock_device_manager)

        assert manager_no_device._device_manager is mock_device_manager

    def test_register_orion(self, manager, sample_orion):
        """Test registering a orion for management."""
        metadata = {"priority": "high", "user": "test_user"}

        orion_id = manager.register_orion(
            sample_orion, metadata
        )

        assert orion_id == sample_orion.orion_id
        assert orion_id in manager._managed_orions
        assert manager._managed_orions[orion_id] is sample_orion
        assert manager._orion_metadata[orion_id] == metadata

    def test_register_orion_without_metadata(
        self, manager, sample_orion
    ):
        """Test registering orion without metadata."""
        orion_id = manager.register_orion(sample_orion)

        assert orion_id in manager._managed_orions
        assert manager._orion_metadata[orion_id] == {}

    def test_unregister_orion(self, manager, sample_orion):
        """Test unregistering a orion."""
        # Register first
        orion_id = manager.register_orion(sample_orion)

        # Unregister
        success = manager.unregister_orion(orion_id)

        assert success
        assert orion_id not in manager._managed_orions
        assert orion_id not in manager._orion_metadata

    def test_unregister_nonexistent_orion(self, manager):
        """Test unregistering a nonexistent orion."""
        success = manager.unregister_orion("nonexistent_id")

        assert not success

    def test_get_orion(self, manager, sample_orion):
        """Test getting a managed orion by ID."""
        orion_id = manager.register_orion(sample_orion)

        retrieved = manager.get_orion(orion_id)

        assert retrieved is sample_orion

    def test_get_nonexistent_orion(self, manager):
        """Test getting a nonexistent orion."""
        retrieved = manager.get_orion("nonexistent_id")

        assert retrieved is None

    def test_list_orions(self, manager, sample_orion):
        """Test listing all managed orions."""
        metadata = {"priority": "high"}
        orion_id = manager.register_orion(
            sample_orion, metadata
        )

        orions = manager.list_orions()

        assert len(orions) == 1
        orion_info = orions[0]
        assert orion_info["orion_id"] == orion_id
        assert orion_info["name"] == sample_orion.name
        assert orion_info["task_count"] == sample_orion.task_count
        assert orion_info["metadata"] == metadata

    def test_list_orions_empty(self, manager):
        """Test listing orions when none are registered."""
        orions = manager.list_orions()

        assert len(orions) == 0

    @pytest.mark.asyncio
    async def test_assign_devices_round_robin(self, manager, sample_orion):
        """Test round robin device assignment strategy."""
        assignments = await manager.assign_devices_automatically(
            sample_orion, strategy="round_robin"
        )

        assert len(assignments) == 3  # 3 tasks
        assert all(
            task_id in assignments for task_id in sample_orion.tasks.keys()
        )

        # Verify round robin distribution
        assigned_devices = list(assignments.values())
        assert len(set(assigned_devices)) <= 3  # At most 3 different devices

    @pytest.mark.asyncio
    async def test_assign_devices_capability_match(self, manager, sample_orion):
        """Test capability matching device assignment strategy."""
        # Set device types for tasks
        sample_orion.tasks["task1"].device_type = DeviceType.WINDOWS
        sample_orion.tasks["task2"].device_type = (
            DeviceType.MACOS
        )  # Will fall back

        assignments = await manager.assign_devices_automatically(
            sample_orion, strategy="capability_match"
        )

        assert len(assignments) == 3
        assert all(
            task_id in assignments for task_id in sample_orion.tasks.keys()
        )

    @pytest.mark.asyncio
    async def test_assign_devices_load_balance(self, manager, sample_orion):
        """Test load balanced device assignment strategy."""
        assignments = await manager.assign_devices_automatically(
            sample_orion, strategy="load_balance"
        )

        assert len(assignments) == 3
        assert all(
            task_id in assignments for task_id in sample_orion.tasks.keys()
        )

    @pytest.mark.asyncio
    async def test_assign_devices_with_preferences(self, manager, sample_orion):
        """Test device assignment with preferences."""
        preferences = {"task1": "device2", "task2": "device1"}

        assignments = await manager.assign_devices_automatically(
            sample_orion, strategy="round_robin", device_preferences=preferences
        )

        assert assignments["task1"] == "device2"
        assert assignments["task2"] == "device1"
        assert "task3" in assignments  # Should be assigned automatically

    @pytest.mark.asyncio
    async def test_assign_devices_invalid_strategy(self, manager, sample_orion):
        """Test device assignment with invalid strategy."""
        with pytest.raises(ValueError, match="Unknown assignment strategy"):
            await manager.assign_devices_automatically(
                sample_orion, strategy="invalid_strategy"
            )

    @pytest.mark.asyncio
    async def test_assign_devices_no_device_manager(
        self, manager_no_device, sample_orion
    ):
        """Test device assignment without device manager."""
        with pytest.raises(ValueError, match="Device manager not available"):
            await manager_no_device.assign_devices_automatically(sample_orion)

    @pytest.mark.asyncio
    async def test_assign_devices_no_available_devices(
        self, manager, sample_orion
    ):
        """Test device assignment when no devices are available."""
        # Mock empty device list
        manager._device_manager._connected_devices = []

        with pytest.raises(ValueError, match="No available devices"):
            await manager.assign_devices_automatically(sample_orion)

    @pytest.mark.asyncio
    async def test_get_orion_status(self, manager, sample_orion):
        """Test getting orion status."""
        orion_id = manager.register_orion(
            sample_orion, {"priority": "high"}
        )

        status = await manager.get_orion_status(orion_id)

        assert status is not None
        assert status["orion_id"] == orion_id
        assert status["name"] == sample_orion.name
        assert "statistics" in status
        assert "ready_tasks" in status
        assert "metadata" in status
        assert status["metadata"]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_get_orion_status_nonexistent(self, manager):
        """Test getting status of nonexistent orion."""
        status = await manager.get_orion_status("nonexistent_id")

        assert status is None

    @pytest.mark.asyncio
    async def test_get_available_devices(self, manager):
        """Test getting available devices."""
        devices = await manager.get_available_devices()

        assert len(devices) == 3
        for device in devices:
            assert "device_id" in device
            assert "device_type" in device
            assert "capabilities" in device
            assert "status" in device
            assert device["status"] == "connected"

    @pytest.mark.asyncio
    async def test_get_available_devices_no_manager(self, manager_no_device):
        """Test getting available devices without device manager."""
        devices = await manager_no_device.get_available_devices()

        assert len(devices) == 0

    def test_validate_orion_assignments_valid(
        self, manager, sample_orion
    ):
        """Test validating orion with valid device assignments."""
        # Assign devices to all tasks
        for i, task in enumerate(sample_orion.tasks.values()):
            task.target_device_id = f"device{i+1}"

        is_valid, errors = manager.validate_orion_assignments(
            sample_orion
        )

        assert is_valid
        assert len(errors) == 0

    def test_validate_orion_assignments_invalid(
        self, manager, sample_orion
    ):
        """Test validating orion with missing device assignments."""
        # Leave one task without device assignment
        sample_orion.tasks["task1"].target_device_id = "device1"
        sample_orion.tasks["task2"].target_device_id = "device2"
        # task3 has no assignment

        is_valid, errors = manager.validate_orion_assignments(
            sample_orion
        )

        assert not is_valid
        assert len(errors) == 1
        assert "task3" in errors[0]
        assert "no device assignment" in errors[0]

    def test_get_task_device_info(self, manager, sample_orion):
        """Test getting device info for a specific task."""
        # Assign device to task
        sample_orion.tasks["task1"].target_device_id = "device1"

        device_info = manager.get_task_device_info(sample_orion, "task1")

        assert device_info is not None
        assert device_info["device_id"] == "device1"
        assert "device_type" in device_info
        assert "capabilities" in device_info

    def test_get_task_device_info_no_assignment(self, manager, sample_orion):
        """Test getting device info for task without assignment."""
        device_info = manager.get_task_device_info(sample_orion, "task1")

        assert device_info is None

    def test_get_task_device_info_nonexistent_task(self, manager, sample_orion):
        """Test getting device info for nonexistent task."""
        device_info = manager.get_task_device_info(
            sample_orion, "nonexistent_task"
        )

        assert device_info is None

    def test_reassign_task_device(self, manager, sample_orion):
        """Test reassigning a task to a different device."""
        # Initial assignment
        sample_orion.tasks["task1"].target_device_id = "device1"

        success = manager.reassign_task_device(sample_orion, "task1", "device2")

        assert success
        assert sample_orion.tasks["task1"].target_device_id == "device2"

    def test_reassign_nonexistent_task(self, manager, sample_orion):
        """Test reassigning a nonexistent task."""
        success = manager.reassign_task_device(
            sample_orion, "nonexistent_task", "device1"
        )

        assert not success

    def test_clear_device_assignments(self, manager, sample_orion):
        """Test clearing all device assignments."""
        # Assign devices to all tasks
        for i, task in enumerate(sample_orion.tasks.values()):
            task.target_device_id = f"device{i+1}"

        cleared_count = manager.clear_device_assignments(sample_orion)

        assert cleared_count == 3
        for task in sample_orion.tasks.values():
            assert task.target_device_id is None

    def test_clear_device_assignments_none_assigned(
        self, manager, sample_orion
    ):
        """Test clearing device assignments when none are assigned."""
        cleared_count = manager.clear_device_assignments(sample_orion)

        assert cleared_count == 0

    def test_get_device_utilization(self, manager, sample_orion):
        """Test getting device utilization statistics."""
        # Assign devices (some devices get multiple tasks)
        sample_orion.tasks["task1"].target_device_id = "device1"
        sample_orion.tasks["task2"].target_device_id = "device1"
        sample_orion.tasks["task3"].target_device_id = "device2"

        utilization = manager.get_device_utilization(sample_orion)

        assert utilization["device1"] == 2
        assert utilization["device2"] == 1
        assert "device3" not in utilization  # No tasks assigned

    def test_get_device_utilization_no_assignments(self, manager, sample_orion):
        """Test getting device utilization with no assignments."""
        utilization = manager.get_device_utilization(sample_orion)

        assert len(utilization) == 0

    @pytest.mark.asyncio
    async def test_assign_devices_with_device_manager_error(
        self, manager, sample_orion
    ):
        """Test device assignment when device manager throws error."""
        # Mock device manager to raise exception
        manager._device_manager.get_connected_devices = Mock(
            side_effect=Exception("Device manager error")
        )

        with pytest.raises(ValueError, match="No available devices"):
            await manager.assign_devices_automatically(sample_orion)


class TestOrionManagerIntegration:
    """Integration tests for OrionManager with other components."""

    @pytest.fixture
    def mock_device_manager(self):
        """Create a mock device manager for integration testing."""
        device_manager = MockDeviceManager()

        def get_device_info(device_id):
            if device_id in device_manager._connected_devices:
                return MockAgentProfile(device_id)
            return None

        device_manager.device_registry.get_device_info.side_effect = get_device_info
        return device_manager

    @pytest.fixture
    def manager(self, mock_device_manager):
        """Create a OrionManager for integration testing."""
        return OrionManager(mock_device_manager, enable_logging=False)

    @pytest.mark.asyncio
    async def test_full_orion_lifecycle(self, manager):
        """Test complete orion management lifecycle."""
        # Create orion
        orion = TaskOrion(name="Lifecycle Test")
        for i in range(5):
            task = TaskStar(task_id=f"task_{i+1}", description=f"Task {i+1}")
            orion.add_task(task)

        # Register
        orion_id = manager.register_orion(
            orion, {"test": "lifecycle"}
        )

        # Assign devices
        assignments = await manager.assign_devices_automatically(
            orion, strategy="load_balance"
        )
        assert len(assignments) == 5

        # Validate assignments
        is_valid, errors = manager.validate_orion_assignments(orion)
        assert is_valid

        # Get status
        status = await manager.get_orion_status(orion_id)
        assert status is not None
        assert status["name"] == "Lifecycle Test"

        # Get utilization
        utilization = manager.get_device_utilization(orion)
        assert len(utilization) > 0

        # Reassign one task
        success = manager.reassign_task_device(orion, "task_1", "device1")
        assert success

        # Clear assignments
        cleared = manager.clear_device_assignments(orion)
        assert cleared == 5

        # Unregister
        success = manager.unregister_orion(orion_id)
        assert success

    @pytest.mark.asyncio
    async def test_multiple_orions_management(self, manager):
        """Test managing multiple orions simultaneously."""
        orions = []

        # Create and register multiple orions
        for i in range(3):
            orion = TaskOrion(name=f"Orion {i+1}")
            for j in range(2):
                task = TaskStar(
                    task_id=f"c{i+1}_task_{j+1}",
                    description=f"Task {j+1} in orion {i+1}",
                )
                orion.add_task(task)

            orion_id = manager.register_orion(orion)
            orions.append((orion_id, orion))

        # List all orions
        orion_list = manager.list_orions()
        assert len(orion_list) == 3

        # Assign devices to all orions
        for orion_id, orion in orions:
            assignments = await manager.assign_devices_automatically(orion)
            assert len(assignments) == 2

        # Validate all have assignments
        for orion_id, orion in orions:
            is_valid, errors = manager.validate_orion_assignments(orion)
            assert is_valid

        # Unregister all
        for orion_id, orion in orions:
            success = manager.unregister_orion(orion_id)
            assert success

        # Verify list is empty
        orion_list = manager.list_orions()
        assert len(orion_list) == 0

    @pytest.mark.asyncio
    async def test_device_assignment_strategies_comparison(self, manager):
        """Test and compare different device assignment strategies."""
        orion = TaskOrion(name="Strategy Test")

        # Create tasks with different device type preferences
        task1 = TaskStar(task_id="task1", description="Windows task")
        task1.device_type = DeviceType.WINDOWS

        task2 = TaskStar(task_id="task2", description="MacOS task")
        task2.device_type = DeviceType.MACOS

        task3 = TaskStar(task_id="task3", description="Any device task")

        orion.add_task(task1)
        orion.add_task(task2)
        orion.add_task(task3)

        # Test round robin
        manager.clear_device_assignments(orion)
        assignments_rr = await manager.assign_devices_automatically(
            orion, strategy="round_robin"
        )

        # Test capability match
        manager.clear_device_assignments(orion)
        assignments_cm = await manager.assign_devices_automatically(
            orion, strategy="capability_match"
        )

        # Test load balance
        manager.clear_device_assignments(orion)
        assignments_lb = await manager.assign_devices_automatically(
            orion, strategy="load_balance"
        )

        # All strategies should assign all tasks
        assert len(assignments_rr) == 3
        assert len(assignments_cm) == 3
        assert len(assignments_lb) == 3

        # Assignments may differ between strategies
        # but all should be valid device IDs
        all_device_ids = ["device1", "device2", "device3"]
        for assignments in [assignments_rr, assignments_cm, assignments_lb]:
            assert all(
                device_id in all_device_ids for device_id in assignments.values()
            )
