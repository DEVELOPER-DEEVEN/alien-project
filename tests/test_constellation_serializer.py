"""
Tests for networkSerializer class.
Validates serialization and deserialization functionality.
"""

import json
import pytest
from datetime import datetime

from cluster.network.parsers.network_serializer import (
    networkSerializer,
)
from cluster.network.task_network import (
    Tasknetwork,
    networkState,
)
from cluster.network.task_star import TaskStar, TaskPriority, TaskStatus
from cluster.network.task_star_line import TaskStarLine


class TestnetworkSerializer:
    """Test networkSerializer functionality."""

    def test_to_dict_basic(self):
        """Test basic network to dictionary conversion."""
        network = Tasknetwork(name="Test network")

        # Add a task
        task = TaskStar(
            task_id="task_1", description="Test task", priority=TaskPriority.HIGH
        )
        network.add_task(task)

        # Convert to dict
        data = networkSerializer.to_dict(network)

        assert data["name"] == "Test network"
        assert data["state"] == networkState.CREATED.value
        assert "task_1" in data["tasks"]
        assert data["tasks"]["task_1"]["description"] == "Test task"
        assert data["metadata"] == {}

    def test_from_dict_basic(self):
        """Test basic network from dictionary creation."""
        data = {
            "network_id": "test_id",
            "name": "Test network",
            "state": networkState.CREATED.value,
            "tasks": {
                "task_1": {
                    "task_id": "task_1",
                    "description": "Test task",
                    "priority": TaskPriority.HIGH.value,
                    "status": TaskStatus.PENDING.value,
                    "metadata": {},
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            },
            "dependencies": {},
            "metadata": {"test": "value"},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        network = networkSerializer.from_dict(data)

        assert network.name == "Test network"
        assert network.network_id == "test_id"
        assert network.state == networkState.CREATED
        assert len(network.tasks) == 1
        assert "task_1" in network.tasks
        assert network.metadata == {"test": "value"}

    def test_to_json_and_from_json(self):
        """Test JSON serialization round trip."""
        # Create network with task and dependency
        network = Tasknetwork(name="JSON Test")

        task1 = TaskStar(task_id="task_1", description="First task")
        task2 = TaskStar(task_id="task_2", description="Second task")
        network.add_task(task1)
        network.add_task(task2)

        # Add dependency
        dep = TaskStarLine.create_unconditional(
            "task_1", "task_2", "Sequential dependency"
        )
        network.add_dependency(dep)

        # Convert to JSON and back
        json_str = networkSerializer.to_json(network)
        restored = networkSerializer.from_json(json_str)

        assert restored.name == network.name
        assert len(restored.tasks) == len(network.tasks)
        assert len(restored.dependencies) == len(network.dependencies)

        # Verify task details
        for task_id, task in network.tasks.items():
            assert task_id in restored.tasks
            assert restored.tasks[task_id].description == task.description

    def test_normalize_json_data_dependencies_list(self):
        """Test normalization of dependencies in list format."""
        data = {
            "name": "Test",
            "tasks": {},
            "dependencies": [
                {
                    "predecessor_id": "task_1",
                    "successor_id": "task_2",
                    "dependency_type": "unconditional",
                }
            ],
        }

        normalized = networkSerializer.normalize_json_data(data)

        assert isinstance(normalized["dependencies"], dict)
        assert "dep_0" in normalized["dependencies"]
        dep = normalized["dependencies"]["dep_0"]
        assert dep["from_task_id"] == "task_1"
        assert dep["to_task_id"] == "task_2"
        assert dep["dependency_type"] == "unconditional"

    def test_normalize_json_data_dependencies_dict(self):
        """Test normalization preserves dict format dependencies."""
        data = {
            "name": "Test",
            "tasks": {},
            "dependencies": {
                "dep_1": {"from_task_id": "task_1", "to_task_id": "task_2"}
            },
        }

        normalized = networkSerializer.normalize_json_data(data)

        assert normalized["dependencies"] == data["dependencies"]

    def test_serialization_with_timestamps(self):
        """Test serialization preserves timestamps correctly."""
        network = Tasknetwork(name="Timestamp Test")
        network.start_execution()
        network.complete_execution()

        # Serialize and deserialize
        json_str = networkSerializer.to_json(network)
        restored = networkSerializer.from_json(json_str)

        assert restored.execution_start_time is not None
        assert restored.execution_end_time is not None
        assert restored.created_at is not None
        assert restored.updated_at is not None

    def test_serialization_with_metadata(self):
        """Test serialization preserves metadata correctly."""
        network = Tasknetwork(name="Metadata Test")
        network.update_metadata({"custom_field": "custom_value"})
        network.update_metadata({"nested": {"key": "value"}})

        # Serialize and deserialize
        data = networkSerializer.to_dict(network)
        restored = networkSerializer.from_dict(data)

        assert restored.metadata["custom_field"] == "custom_value"
        assert restored.metadata["nested"]["key"] == "value"

    def test_empty_network_serialization(self):
        """Test serialization of empty network."""
        network = Tasknetwork(name="Empty")

        data = networkSerializer.to_dict(network)
        restored = networkSerializer.from_dict(data)

        assert restored.name == "Empty"
        assert len(restored.tasks) == 0
        assert len(restored.dependencies) == 0
        assert restored.state == networkState.CREATED

    def test_json_serialization_invalid_input(self):
        """Test error handling for invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            networkSerializer.from_json("invalid json")

    def test_dict_serialization_missing_fields(self):
        """Test serialization handles missing fields gracefully."""
        minimal_data = {"name": "Minimal Test"}

        network = networkSerializer.from_dict(minimal_data)

        assert network.name == "Minimal Test"
        assert network.state == networkState.CREATED
        assert len(network.tasks) == 0
        assert len(network.dependencies) == 0
