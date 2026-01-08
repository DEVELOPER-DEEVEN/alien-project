# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Unit tests for the refactored TasknetworkOrchestrator.

Tests orchestration functionality with separated responsibilities
using networkParser and networkManager.
"""

import asyncio
import pytest
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from cluster.network.orchestrator.orchestrator import (
    TasknetworkOrchestrator,
)
from cluster.network.enums import TaskStatus, DeviceType
from cluster.network.task_network import Tasknetwork
from cluster.network.task_star import TaskStar


class MocknetworkDeviceManager:
    """Mock device manager for testing orchestrator."""

    def __init__(self):
        self.device_registry = Mock()
        self._connected_devices = ["device1", "device2"]

    def get_connected_devices(self):
        return self._connected_devices.copy()


class MockAgentProfile:
    """Mock device info for testing."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.device_type = "desktop"
        self.capabilities = ["ui_automation"]
        self.metadata = {"platform": "windows"}


class TestTasknetworkOrchestrator:
    """Test cases for the refactored TasknetworkOrchestrator."""

    @pytest.fixture
    def mock_device_manager(self):
        """Create a mock device manager for testing."""
        device_manager = MocknetworkDeviceManager()

        def get_device_info(device_id):
            if device_id in device_manager._connected_devices:
                return MockAgentProfile(device_id)
            return None

        device_manager.device_registry.get_device_info.side_effect = get_device_info
        return device_manager

    @pytest.fixture
    def mock_event_bus(self):
        """Create a mock event bus for testing."""
        event_bus = Mock()
        event_bus.publish_event = AsyncMock()
        return event_bus

    @pytest.fixture
    def orchestrator(self, mock_device_manager, mock_event_bus):
        """Create a TasknetworkOrchestrator for testing."""
        return TasknetworkOrchestrator(
            device_manager=mock_device_manager,
            enable_logging=False,
            event_bus=mock_event_bus,
        )

    @pytest.fixture
    def orchestrator_no_device(self, mock_event_bus):
        """Create orchestrator without device manager."""
        return TasknetworkOrchestrator(
            enable_logging=False, event_bus=mock_event_bus
        )

    @pytest.fixture
    def sample_tasks(self):
        """Create sample task descriptions for testing."""
        return ["Open browser", "Navigate to website", "Fill form", "Submit form"]

    def test_init_with_device_manager(self, mock_device_manager, mock_event_bus):
        """Test orchestrator initialization with device manager."""
        orchestrator = TasknetworkOrchestrator(
            device_manager=mock_device_manager,
            enable_logging=True,
            event_bus=mock_event_bus,
        )

        assert orchestrator._device_manager is mock_device_manager
        assert orchestrator._event_bus is mock_event_bus
        assert orchestrator._logger is not None

    def test_init_without_device_manager(self, mock_event_bus):
        """Test orchestrator initialization without device manager."""
        orchestrator = TasknetworkOrchestrator(
            enable_logging=False, event_bus=mock_event_bus
        )

        assert orchestrator._device_manager is None
        assert orchestrator._event_bus is mock_event_bus

    def test_set_device_manager(self, orchestrator_no_device, mock_device_manager):
        """Test setting device manager after initialization."""
        orchestrator_no_device.set_device_manager(mock_device_manager)

        assert orchestrator_no_device._device_manager is mock_device_manager
        assert (
            orchestrator_no_device._network_manager._device_manager
            is mock_device_manager
        )

    @pytest.mark.asyncio
    async def test_create_network_from_llm(self, orchestrator):
        """Test creating network from LLM output."""
        llm_output = """
        Task 1: Open browser
        Task 2: Navigate to site
        Dependencies: Task 1 -> Task 2
        """

        network = await orchestrator.create_network_from_llm(
            llm_output, "LLM Test network"
        )

        assert isinstance(network, Tasknetwork)
        assert network.name == "LLM Test network"
        # Should be registered with network manager
        assert (
            network.network_id
            in orchestrator._network_manager._managed_networks
        )

    @pytest.mark.asyncio
    async def test_create_network_from_json(self, orchestrator):
        """Test creating network from JSON data."""
        json_data = """{
            "name": "JSON Test",
            "tasks": {
                "task1": {"task_id": "task1", "description": "Test task"}
            },
            "dependencies": []
        }"""

        network = await orchestrator.create_network_from_json(
            json_data, "JSON network"
        )

        assert isinstance(network, Tasknetwork)
        assert network.name == "JSON network"

    @pytest.mark.asyncio
    async def test_create_simple_network_sequential(
        self, orchestrator, sample_tasks
    ):
        """Test creating simple sequential network."""
        network = await orchestrator.create_simple_network(
            sample_tasks, "Sequential Test", sequential=True
        )

        assert isinstance(network, Tasknetwork)
        assert network.name == "Sequential Test"
        assert network.task_count == len(sample_tasks)
        assert network.dependency_count == len(sample_tasks) - 1

    @pytest.mark.asyncio
    async def test_create_simple_network_parallel(
        self, orchestrator, sample_tasks
    ):
        """Test creating simple parallel network."""
        network = await orchestrator.create_simple_network(
            sample_tasks, "Parallel Test", sequential=False
        )

        assert isinstance(network, Tasknetwork)
        assert network.name == "Parallel Test"
        assert network.task_count == len(sample_tasks)
        assert network.dependency_count == 0

    @pytest.mark.asyncio
    async def test_orchestrate_network_no_device_manager(
        self, orchestrator_no_device
    ):
        """Test orchestration without device manager raises error."""
        network = Tasknetwork(name="Test")

        with pytest.raises(ValueError, match="networkDeviceManager not set"):
            await orchestrator_no_device.orchestrate_network(network)

    @pytest.mark.asyncio
    async def test_orchestrate_network_invalid_dag(self, orchestrator):
        """Test orchestration with invalid DAG structure."""
        network = Tasknetwork(name="Invalid DAG")
        # Create network that will fail validation
        # (empty network is considered invalid)

        with pytest.raises(ValueError, match="Invalid DAG"):
            await orchestrator.orchestrate_network(network)

    @pytest.mark.asyncio
    async def test_orchestrate_network_assignment_validation_failed(
        self, orchestrator
    ):
        """Test orchestration when device assignment validation fails."""
        network = Tasknetwork(name="Test network")

        # Add a task
        task = TaskStar(task_id="task1", description="Test task")
        network.add_task(task)

        # Mock device manager to have no devices
        orchestrator._device_manager._connected_devices = []

        with pytest.raises(ValueError, match="No available devices"):
            await orchestrator.orchestrate_network(network)

    @pytest.mark.asyncio
    async def test_orchestrate_network_with_manual_assignments(
        self, orchestrator
    ):
        """Test orchestration with manual device assignments."""
        network = Tasknetwork(name="Manual Assignment Test")

        # Add tasks
        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        network.add_task(task1)
        network.add_task(task2)

        # Mock task execution to complete immediately
        with patch.object(TaskStar, "execute", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = Mock(result="success")

            device_assignments = {"task1": "device1", "task2": "device2"}
            result = await orchestrator.orchestrate_network(
                network, device_assignments
            )

            assert result["status"] == "completed"
            assert (
                result["total_tasks"] == 0
            )  # No results captured in this simplified version

    @pytest.mark.asyncio
    async def test_execute_single_task(self, orchestrator):
        """Test executing a single task."""
        task = TaskStar(task_id="single_task", description="Single test task")

        # Mock task execution
        with patch.object(TaskStar, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = Mock()
            mock_result.result = "task_completed"
            mock_execute.return_value = mock_result

            result = await orchestrator.execute_single_task(task, "device1")

            assert result == "task_completed"
            assert task.target_device_id == "device1"

    @pytest.mark.asyncio
    async def test_execute_single_task_auto_assign(self, orchestrator):
        """Test executing single task with auto device assignment."""
        task = TaskStar(task_id="auto_task", description="Auto assign task")

        with patch.object(TaskStar, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = Mock()
            mock_result.result = "auto_completed"
            mock_execute.return_value = mock_result

            result = await orchestrator.execute_single_task(task)

            assert result == "auto_completed"
            assert task.target_device_id in ["device1", "device2"]

    @pytest.mark.asyncio
    async def test_execute_single_task_no_devices(self, orchestrator):
        """Test executing single task when no devices available."""
        task = TaskStar(task_id="no_device_task", description="No device task")

        # Mock no available devices
        orchestrator._network_manager._device_manager._connected_devices = []

        with pytest.raises(ValueError, match="No available devices"):
            await orchestrator.execute_single_task(task)

    @pytest.mark.asyncio
    async def test_modify_network_with_llm(self, orchestrator):
        """Test modifying network with LLM request."""
        network = Tasknetwork(name="Original network")
        task = TaskStar(task_id="original_task", description="Original task")
        network.add_task(task)

        modification_request = "Add a new task after the original task"

        modified = await orchestrator.modify_network_with_llm(
            network, modification_request
        )

        assert isinstance(modified, Tasknetwork)
        # In current implementation, this returns the same network
        # as LLM integration is not fully implemented

    @pytest.mark.asyncio
    async def test_get_network_status(self, orchestrator):
        """Test getting network status."""
        network = Tasknetwork(name="Status Test")
        task = TaskStar(task_id="status_task", description="Status task")
        network.add_task(task)

        # Register network
        orchestrator._network_manager.register_network(network)

        status = await orchestrator.get_network_status(network)

        assert status is not None
        assert status["name"] == "Status Test"
        assert "statistics" in status

    @pytest.mark.asyncio
    async def test_get_available_devices(self, orchestrator):
        """Test getting available devices."""
        devices = await orchestrator.get_available_devices()

        assert len(devices) == 2
        assert all("device_id" in device for device in devices)

    @pytest.mark.asyncio
    async def test_assign_devices_automatically(self, orchestrator):
        """Test automatic device assignment."""
        network = Tasknetwork(name="Assignment Test")

        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        network.add_task(task1)
        network.add_task(task2)

        assignments = await orchestrator.assign_devices_automatically(
            network, strategy="round_robin"
        )

        assert len(assignments) == 2
        assert "task1" in assignments
        assert "task2" in assignments

    @pytest.mark.asyncio
    async def test_assign_devices_with_preferences(self, orchestrator):
        """Test device assignment with preferences."""
        network = Tasknetwork(name="Preference Test")

        task1 = TaskStar(task_id="task1", description="Preferred task")
        network.add_task(task1)

        preferences = {"task1": "device2"}
        assignments = await orchestrator.assign_devices_automatically(
            network, device_preferences=preferences
        )

        assert assignments["task1"] == "device2"

    def test_export_network(self, orchestrator):
        """Test exporting network."""
        network = Tasknetwork(name="Export Test")
        task = TaskStar(task_id="export_task", description="Export task")
        network.add_task(task)

        # Test JSON export
        json_export = orchestrator.export_network(network, "json")
        assert isinstance(json_export, str)
        assert "Export Test" in json_export

        # Test LLM export
        llm_export = orchestrator.export_network(network, "llm")
        assert isinstance(llm_export, str)
        assert "Export Test" in llm_export

    @pytest.mark.asyncio
    async def test_import_network_json(self, orchestrator):
        """Test importing network from JSON."""
        json_data = """{
            "name": "Import Test",
            "tasks": {
                "import_task": {
                    "task_id": "import_task",
                    "description": "Imported task"
                }
            },
            "dependencies": []
        }"""

        network = await orchestrator.import_network(json_data, "json")

        assert isinstance(network, Tasknetwork)
        assert "import_task" in network.tasks

    @pytest.mark.asyncio
    async def test_import_network_llm(self, orchestrator):
        """Test importing network from LLM format."""
        llm_data = """
        Task: Import task
        Description: Task created from LLM import
        """

        network = await orchestrator.import_network(llm_data, "llm")

        assert isinstance(network, Tasknetwork)

    @pytest.mark.asyncio
    async def test_import_network_unsupported_format(self, orchestrator):
        """Test importing with unsupported format."""
        with pytest.raises(ValueError, match="Unsupported import format"):
            await orchestrator.import_network("data", "unsupported")

    def test_add_task_to_network(self, orchestrator):
        """Test adding task to network."""
        network = Tasknetwork(name="Add Task Test")
        original_task = TaskStar(task_id="original", description="Original task")
        network.add_task(original_task)

        new_task = TaskStar(task_id="new_task", description="New task")
        success = orchestrator.add_task_to_network(
            network, new_task, dependencies=["original"]
        )

        assert success
        assert "new_task" in network.tasks

    def test_remove_task_from_network(self, orchestrator):
        """Test removing task from network."""
        network = Tasknetwork(name="Remove Task Test")

        task1 = TaskStar(task_id="task1", description="Task 1")
        task2 = TaskStar(task_id="task2", description="Task 2")
        network.add_task(task1)
        network.add_task(task2)

        success = orchestrator.remove_task_from_network(network, "task1")

        assert success
        assert "task1" not in network.tasks
        assert "task2" in network.tasks

    def test_clone_network(self, orchestrator):
        """Test cloning a network."""
        original = Tasknetwork(name="Original")
        task = TaskStar(task_id="task1", description="Original task")
        original.add_task(task)

        cloned = orchestrator.clone_network(original, "Cloned")

        assert isinstance(cloned, Tasknetwork)
        assert cloned.name == "Cloned"
        assert cloned.network_id != original.network_id
        assert cloned.task_count == original.task_count

    def test_merge_networks(self, orchestrator):
        """Test merging two networks."""
        network1 = Tasknetwork(name="First")
        task1 = TaskStar(task_id="task1", description="Task 1")
        network1.add_task(task1)

        network2 = Tasknetwork(name="Second")
        task2 = TaskStar(task_id="task2", description="Task 2")
        network2.add_task(task2)

        merged = orchestrator.merge_networks(
            network1, network2, "Merged"
        )

        assert isinstance(merged, Tasknetwork)
        assert merged.name == "Merged"
        assert merged.task_count == 2
        assert "c1_task1" in merged.tasks
        assert "c2_task2" in merged.tasks


class TestTasknetworkOrchestratorIntegration:
    """Integration tests for TasknetworkOrchestrator."""

    @pytest.fixture
    def mock_device_manager(self):
        """Create mock device manager for integration testing."""
        device_manager = MocknetworkDeviceManager()

        def get_device_info(device_id):
            if device_id in device_manager._connected_devices:
                return MockAgentProfile(device_id)
            return None

        device_manager.device_registry.get_device_info.side_effect = get_device_info
        return device_manager

    @pytest.fixture
    def orchestrator(self, mock_device_manager):
        """Create orchestrator for integration testing."""
        return TasknetworkOrchestrator(
            device_manager=mock_device_manager, enable_logging=False
        )

    @pytest.mark.asyncio
    async def test_end_to_end_network_workflow(self, orchestrator):
        """Test complete network workflow from creation to execution."""
        # Create network from task descriptions
        task_descriptions = ["Open app", "Perform action", "Verify result"]
        network = await orchestrator.create_simple_network(
            task_descriptions, "E2E Test", sequential=True
        )

        # Export and reimport
        exported = orchestrator.export_network(network, "json")
        reimported = await orchestrator.import_network(exported, "json")

        assert reimported.task_count == network.task_count

        # Clone network
        cloned = orchestrator.clone_network(network, "E2E Cloned")
        assert cloned.task_count == network.task_count

        # Assign devices
        assignments = await orchestrator.assign_devices_automatically(cloned)
        assert len(assignments) == 3

        # Get status
        status = await orchestrator.get_network_status(cloned)
        assert status is not None
        assert status["name"] == "E2E Cloned"

    @pytest.mark.asyncio
    async def test_complex_network_operations(self, orchestrator):
        """Test complex network operations and modifications."""
        # Create base network
        network = await orchestrator.create_simple_network(
            ["Base task 1", "Base task 2"], "Complex Test"
        )

        # Add additional task
        new_task = TaskStar(task_id="additional", description="Additional task")
        success = orchestrator.add_task_to_network(network, new_task)
        assert success

        # Create another network to merge
        other_network = await orchestrator.create_simple_network(
            ["Other task"], "Other"
        )

        # Merge networks
        merged = orchestrator.merge_networks(
            network, other_network, "Complex Merged"
        )
        assert merged.task_count == 4  # 2 + 1 + 1

        # Assign devices with different strategies
        await orchestrator.assign_devices_automatically(merged, strategy="load_balance")

        # Verify all tasks have assignments
        for task in merged.tasks.values():
            assert task.target_device_id is not None

        # Remove a task (use the actual task ID from merged network)
        merged_task_ids = list(merged.tasks.keys())
        # Find a task that contains "additional" in its ID
        task_to_remove = next(
            (tid for tid in merged_task_ids if "additional" in tid), None
        )
        if task_to_remove:
            success = orchestrator.remove_task_from_network(
                merged, task_to_remove
            )
        else:
            # If no task with "additional" found, use the first task
            success = orchestrator.remove_task_from_network(
                merged, merged_task_ids[0]
            )
        assert success
        assert merged.task_count == 3

    @pytest.mark.asyncio
    async def test_orchestration_with_task_execution_mock(self, orchestrator):
        """Test orchestration with mocked task execution."""
        network = await orchestrator.create_simple_network(
            ["Mock task 1", "Mock task 2"], "Mock Test", sequential=True
        )

        # Mock task execution to return success
        with patch.object(TaskStar, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = Mock()
            mock_result.result = "mock_success"
            mock_execute.return_value = mock_result

            result = await orchestrator.orchestrate_network(network)

            assert result["status"] == "completed"
            # Verify task execution was called
            assert mock_execute.call_count >= 2  # Should execute both tasks

    @pytest.mark.asyncio
    async def test_error_handling_in_orchestration(self, orchestrator):
        """Test error handling during orchestration."""
        network = await orchestrator.create_simple_network(
            ["Error task"], "Error Test"
        )

        # Mock task execution to raise exception
        with patch.object(TaskStar, "execute", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("Task execution failed")

            # Execute orchestration (it should handle the exception)
            await orchestrator.orchestrate_network(network)

            # Check that the network is in failed state
            assert network.state.value == "failed"
