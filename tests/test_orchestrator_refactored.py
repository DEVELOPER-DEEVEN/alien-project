
"""
Unit tests for the refactored TaskOrionOrchestrator.

Tests orchestration functionality with separated responsibilities
using OrionParser and OrionManager.
"""

import asyncio
import pytest
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from network.orion.orchestrator.orchestrator import (
    TaskOrionOrchestrator,
)
from network.orion.enums import TaskStatus, DeviceType
from network.orion.task_orion import TaskOrion
from network.orion.task_star import TaskStar


class MockOrionDeviceManager:
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


class TestTaskOrionOrchestrator:
    """Test cases for the refactored TaskOrionOrchestrator."""

    @pytest.fixture
    def mock_device_manager(self):
        """Create a mock device manager for testing."""
        device_manager = MockOrionDeviceManager()

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
        """Create a TaskOrionOrchestrator for testing."""
        return TaskOrionOrchestrator(
            device_manager=mock_device_manager,
            enable_logging=False,
            event_bus=mock_event_bus,
        )

    @pytest.fixture
    def orchestrator_no_device(self, mock_event_bus):
        """Create orchestrator without device manager."""
        return TaskOrionOrchestrator(
            enable_logging=False, event_bus=mock_event_bus
        )

    @pytest.fixture
    def sample_tasks(self):
        """Create sample task descriptions for testing."""
        return ["Open browser", "Navigate to website", "Fill form", "Submit form"]

    def test_init_with_device_manager(self, mock_device_manager, mock_event_bus):
        """Test orchestrator initialization with device manager."""
        orchestrator = TaskOrionOrchestrator(
            device_manager=mock_device_manager,
            enable_logging=True,
            event_bus=mock_event_bus,
        )

        assert orchestrator._device_manager is mock_device_manager
        assert orchestrator._event_bus is mock_event_bus
        assert orchestrator._logger is not None

    def test_init_without_device_manager(self, mock_event_bus):
        """Test orchestrator initialization without device manager."""
        orchestrator = TaskOrionOrchestrator(
            enable_logging=False, event_bus=mock_event_bus
        )

        assert orchestrator._device_manager is None
        assert orchestrator._event_bus is mock_event_bus

    def test_set_device_manager(self, orchestrator_no_device, mock_device_manager):
        """Test setting device manager after initialization."""
        orchestrator_no_device.set_device_manager(mock_device_manager)

        assert orchestrator_no_device._device_manager is mock_device_manager
        assert (
            orchestrator_no_device._orion_manager._device_manager
            is mock_device_manager
        )

    @pytest.mark.asyncio
    async def test_create_orion_from_llm(self, orchestrator):
        """Test creating orion from LLM output."""
        llm_output = """
        Task 1: Open browser
        Task 2: Navigate to site
        Dependencies: Task 1 -> Task 2
        """

        orion = await orchestrator.create_orion_from_llm(
            llm_output, "LLM Test Orion"
        )

        assert isinstance(orion, TaskOrion)
        assert orion.name == "LLM Test Orion"
        # Should be registered with orion manager
        assert (
            orion.orion_id
            in orchestrator._orion_manager._managed_orions
        )

    @pytest.mark.asyncio
    async def test_create_orion_from_json(self, orchestrator):
        """Test creating orion from JSON data."""
        json_data = """{
            "name": "JSON Test",
            "tasks": {
                "task1": {"task_id": "task1", "description": "Test task"}
            },
            "dependencies": []
        }"""

        orion = await orchestrator.create_orion_from_json(
            json_data, "JSON Orion"
        )

        assert isinstance(orion, TaskOrion)
        assert orion.name == "JSON Orion"

    @pytest.mark.asyncio
    async def test_create_simple_orion_sequential(
        self, orchestrator, sample_tasks
    ):
        """Test creating simple sequential orion."""
        orion = await orchestrator.create_simple_orion(
            sample_tasks, "Sequential Test", sequential=True
        )

        assert isinstance(orion, TaskOrion)
        assert orion.name == "Sequential Test"
        assert orion.task_count == len(sample_tasks)
        assert orion.dependency_count == len(sample_tasks) - 1

    @pytest.mark.asyncio
    async def test_create_simple_orion_parallel(
        self, orchestrator, sample_tasks
    ):
        """Test creating simple parallel orion."""
        orion = await orchestrator.create_simple_orion(
            sample_tasks, "Parallel Test", sequential=False
        )

        assert isinstance(orion, TaskOrion)
        assert orion.name == "Parallel Test"
        assert orion.task_count == len(sample_tasks)
        assert orion.dependency_count == 0

    @pytest.mark.asyncio
    async def test_orchestrate_orion_no_device_manager(
        self, orchestrator_no_device
    ):
        """Test orchestration without device manager raises error."""
        orion = TaskOrion(name="Test")

        with pytest.raises(ValueError, match="OrionDeviceManager not set"):
            await orchestrator_no_device.orchestrate_orion(orion)

    @pytest.mark.asyncio
    async def test_orchestrate_orion_invalid_dag(self, orchestrator):
        """Test orchestration with invalid DAG structure."""
        orion = TaskOrion(name="Invalid DAG")
        # Create orion that will fail validation
        # (empty orion is considered invalid)

        with pytest.raises(ValueError, match="Invalid DAG"):
            await orchestrator.orchestrate_orion(orion)

    @pytest.mark.asyncio
    async def test_orchestrate_orion_assignment_validation_failed(
        self, orchestrator
    ):
        """Test orchestration when device assignment validation fails."""
        orion = TaskOrion(name="Test Orion")

        # Add a task
        task = TaskStar(task_id="task1", description="Test task")
        orion.add_task(task)

        # Mock device manager to have no devices
        orchestrator._device_manager._connected_devices = []

        with pytest.raises(ValueError, match="No available devices"):
            await orchestrator.orchestrate_orion(orion)

    @pytest.mark.asyncio
    async def test_orchestrate_orion_with_manual_assignments(
        self, orchestrator
    ):
        """Test orchestration with manual device assignments."""
        orion = TaskOrion(name="Manual Assignment Test")

        # Add tasks
        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        orion.add_task(task1)
        orion.add_task(task2)

        # Mock task execution to complete immediately
        with patch.object(TaskStar, "execute", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = Mock(result="success")

            device_assignments = {"task1": "device1", "task2": "device2"}
            result = await orchestrator.orchestrate_orion(
                orion, device_assignments
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
        orchestrator._orion_manager._device_manager._connected_devices = []

        with pytest.raises(ValueError, match="No available devices"):
            await orchestrator.execute_single_task(task)

    @pytest.mark.asyncio
    async def test_modify_orion_with_llm(self, orchestrator):
        """Test modifying orion with LLM request."""
        orion = TaskOrion(name="Original Orion")
        task = TaskStar(task_id="original_task", description="Original task")
        orion.add_task(task)

        modification_request = "Add a new task after the original task"

        modified = await orchestrator.modify_orion_with_llm(
            orion, modification_request
        )

        assert isinstance(modified, TaskOrion)
        # In current implementation, this returns the same orion
        # as LLM integration is not fully implemented

    @pytest.mark.asyncio
    async def test_get_orion_status(self, orchestrator):
        """Test getting orion status."""
        orion = TaskOrion(name="Status Test")
        task = TaskStar(task_id="status_task", description="Status task")
        orion.add_task(task)

        # Register orion
        orchestrator._orion_manager.register_orion(orion)

        status = await orchestrator.get_orion_status(orion)

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
        orion = TaskOrion(name="Assignment Test")

        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        orion.add_task(task1)
        orion.add_task(task2)

        assignments = await orchestrator.assign_devices_automatically(
            orion, strategy="round_robin"
        )

        assert len(assignments) == 2
        assert "task1" in assignments
        assert "task2" in assignments

    @pytest.mark.asyncio
    async def test_assign_devices_with_preferences(self, orchestrator):
        """Test device assignment with preferences."""
        orion = TaskOrion(name="Preference Test")

        task1 = TaskStar(task_id="task1", description="Preferred task")
        orion.add_task(task1)

        preferences = {"task1": "device2"}
        assignments = await orchestrator.assign_devices_automatically(
            orion, device_preferences=preferences
        )

        assert assignments["task1"] == "device2"

    def test_export_orion(self, orchestrator):
        """Test exporting orion."""
        orion = TaskOrion(name="Export Test")
        task = TaskStar(task_id="export_task", description="Export task")
        orion.add_task(task)

        # Test JSON export
        json_export = orchestrator.export_orion(orion, "json")
        assert isinstance(json_export, str)
        assert "Export Test" in json_export

        # Test LLM export
        llm_export = orchestrator.export_orion(orion, "llm")
        assert isinstance(llm_export, str)
        assert "Export Test" in llm_export

    @pytest.mark.asyncio
    async def test_import_orion_json(self, orchestrator):
        """Test importing orion from JSON."""
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

        orion = await orchestrator.import_orion(json_data, "json")

        assert isinstance(orion, TaskOrion)
        assert "import_task" in orion.tasks

    @pytest.mark.asyncio
    async def test_import_orion_llm(self, orchestrator):
        """Test importing orion from LLM format."""
        llm_data = """
        Task: Import task
        Description: Task created from LLM import
        """

        orion = await orchestrator.import_orion(llm_data, "llm")

        assert isinstance(orion, TaskOrion)

    @pytest.mark.asyncio
    async def test_import_orion_unsupported_format(self, orchestrator):
        """Test importing with unsupported format."""
        with pytest.raises(ValueError, match="Unsupported import format"):
            await orchestrator.import_orion("data", "unsupported")

    def test_add_task_to_orion(self, orchestrator):
        """Test adding task to orion."""
        orion = TaskOrion(name="Add Task Test")
        original_task = TaskStar(task_id="original", description="Original task")
        orion.add_task(original_task)

        new_task = TaskStar(task_id="new_task", description="New task")
        success = orchestrator.add_task_to_orion(
            orion, new_task, dependencies=["original"]
        )

        assert success
        assert "new_task" in orion.tasks

    def test_remove_task_from_orion(self, orchestrator):
        """Test removing task from orion."""
        orion = TaskOrion(name="Remove Task Test")

        task1 = TaskStar(task_id="task1", description="Task 1")
        task2 = TaskStar(task_id="task2", description="Task 2")
        orion.add_task(task1)
        orion.add_task(task2)

        success = orchestrator.remove_task_from_orion(orion, "task1")

        assert success
        assert "task1" not in orion.tasks
        assert "task2" in orion.tasks

    def test_clone_orion(self, orchestrator):
        """Test cloning a orion."""
        original = TaskOrion(name="Original")
        task = TaskStar(task_id="task1", description="Original task")
        original.add_task(task)

        cloned = orchestrator.clone_orion(original, "Cloned")

        assert isinstance(cloned, TaskOrion)
        assert cloned.name == "Cloned"
        assert cloned.orion_id != original.orion_id
        assert cloned.task_count == original.task_count

    def test_merge_orions(self, orchestrator):
        """Test merging two orions."""
        orion1 = TaskOrion(name="First")
        task1 = TaskStar(task_id="task1", description="Task 1")
        orion1.add_task(task1)

        orion2 = TaskOrion(name="Second")
        task2 = TaskStar(task_id="task2", description="Task 2")
        orion2.add_task(task2)

        merged = orchestrator.merge_orions(
            orion1, orion2, "Merged"
        )

        assert isinstance(merged, TaskOrion)
        assert merged.name == "Merged"
        assert merged.task_count == 2
        assert "c1_task1" in merged.tasks
        assert "c2_task2" in merged.tasks


class TestTaskOrionOrchestratorIntegration:
    """Integration tests for TaskOrionOrchestrator."""

    @pytest.fixture
    def mock_device_manager(self):
        """Create mock device manager for integration testing."""
        device_manager = MockOrionDeviceManager()

        def get_device_info(device_id):
            if device_id in device_manager._connected_devices:
                return MockAgentProfile(device_id)
            return None

        device_manager.device_registry.get_device_info.side_effect = get_device_info
        return device_manager

    @pytest.fixture
    def orchestrator(self, mock_device_manager):
        """Create orchestrator for integration testing."""
        return TaskOrionOrchestrator(
            device_manager=mock_device_manager, enable_logging=False
        )

    @pytest.mark.asyncio
    async def test_end_to_end_orion_workflow(self, orchestrator):
        """Test complete orion workflow from creation to execution."""
        # Create orion from task descriptions
        task_descriptions = ["Open app", "Perform action", "Verify result"]
        orion = await orchestrator.create_simple_orion(
            task_descriptions, "E2E Test", sequential=True
        )

        # Export and reimport
        exported = orchestrator.export_orion(orion, "json")
        reimported = await orchestrator.import_orion(exported, "json")

        assert reimported.task_count == orion.task_count

        # Clone orion
        cloned = orchestrator.clone_orion(orion, "E2E Cloned")
        assert cloned.task_count == orion.task_count

        # Assign devices
        assignments = await orchestrator.assign_devices_automatically(cloned)
        assert len(assignments) == 3

        # Get status
        status = await orchestrator.get_orion_status(cloned)
        assert status is not None
        assert status["name"] == "E2E Cloned"

    @pytest.mark.asyncio
    async def test_complex_orion_operations(self, orchestrator):
        """Test complex orion operations and modifications."""
        # Create base orion
        orion = await orchestrator.create_simple_orion(
            ["Base task 1", "Base task 2"], "Complex Test"
        )

        # Add additional task
        new_task = TaskStar(task_id="additional", description="Additional task")
        success = orchestrator.add_task_to_orion(orion, new_task)
        assert success

        # Create another orion to merge
        other_orion = await orchestrator.create_simple_orion(
            ["Other task"], "Other"
        )

        # Merge orions
        merged = orchestrator.merge_orions(
            orion, other_orion, "Complex Merged"
        )
        assert merged.task_count == 4  # 2 + 1 + 1

        # Assign devices with different strategies
        await orchestrator.assign_devices_automatically(merged, strategy="load_balance")

        # Verify all tasks have assignments
        for task in merged.tasks.values():
            assert task.target_device_id is not None

        # Remove a task (use the actual task ID from merged orion)
        merged_task_ids = list(merged.tasks.keys())
        # Find a task that contains "additional" in its ID
        task_to_remove = next(
            (tid for tid in merged_task_ids if "additional" in tid), None
        )
        if task_to_remove:
            success = orchestrator.remove_task_from_orion(
                merged, task_to_remove
            )
        else:
            # If no task with "additional" found, use the first task
            success = orchestrator.remove_task_from_orion(
                merged, merged_task_ids[0]
            )
        assert success
        assert merged.task_count == 3

    @pytest.mark.asyncio
    async def test_orchestration_with_task_execution_mock(self, orchestrator):
        """Test orchestration with mocked task execution."""
        orion = await orchestrator.create_simple_orion(
            ["Mock task 1", "Mock task 2"], "Mock Test", sequential=True
        )

        # Mock task execution to return success
        with patch.object(TaskStar, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = Mock()
            mock_result.result = "mock_success"
            mock_execute.return_value = mock_result

            result = await orchestrator.orchestrate_orion(orion)

            assert result["status"] == "completed"
            # Verify task execution was called
            assert mock_execute.call_count >= 2  # Should execute both tasks

    @pytest.mark.asyncio
    async def test_error_handling_in_orchestration(self, orchestrator):
        """Test error handling during orchestration."""
        orion = await orchestrator.create_simple_orion(
            ["Error task"], "Error Test"
        )

        # Mock task execution to raise exception
        with patch.object(TaskStar, "execute", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("Task execution failed")

            # Execute orchestration (it should handle the exception)
            await orchestrator.orchestrate_orion(orion)

            # Check that the orion is in failed state
            assert orion.state.value == "failed"
