"""
Tests for OrionSerializer class.
Validates serialization and deserialization functionality.
"""

import json
import pytest
from datetime import datetime

from network.orion.parsers.orion_serializer import (
    OrionSerializer,
)
from network.orion.task_orion import (
    TaskOrion,
    OrionState,
)
from network.orion.task_star import TaskStar, TaskPriority, TaskStatus
from network.orion.task_star_line import TaskStarLine


class TestOrionSerializer:
    """Test OrionSerializer functionality."""

    def test_to_dict_basic(self):
        """Test basic orion to dictionary conversion."""
        orion = TaskOrion(name="Test Orion")

        # Add a task
        task = TaskStar(
            task_id="task_1", description="Test task", priority=TaskPriority.HIGH
        )
        orion.add_task(task)

        # Convert to dict
        data = OrionSerializer.to_dict(orion)

        assert data["name"] == "Test Orion"
        assert data["state"] == OrionState.CREATED.value
        assert "task_1" in data["tasks"]
        assert data["tasks"]["task_1"]["description"] == "Test task"
        assert data["metadata"] == {}

    def test_from_dict_basic(self):
        """Test basic orion from dictionary creation."""
        data = {
            "orion_id": "test_id",
            "name": "Test Orion",
            "state": OrionState.CREATED.value,
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

        orion = OrionSerializer.from_dict(data)

        assert orion.name == "Test Orion"
        assert orion.orion_id == "test_id"
        assert orion.state == OrionState.CREATED
        assert len(orion.tasks) == 1
        assert "task_1" in orion.tasks
        assert orion.metadata == {"test": "value"}

    def test_to_json_and_from_json(self):
        """Test JSON serialization round trip."""
        # Create orion with task and dependency
        orion = TaskOrion(name="JSON Test")

        task1 = TaskStar(task_id="task_1", description="First task")
        task2 = TaskStar(task_id="task_2", description="Second task")
        orion.add_task(task1)
        orion.add_task(task2)

        # Add dependency
        dep = TaskStarLine.create_unconditional(
            "task_1", "task_2", "Sequential dependency"
        )
        orion.add_dependency(dep)

        # Convert to JSON and back
        json_str = OrionSerializer.to_json(orion)
        restored = OrionSerializer.from_json(json_str)

        assert restored.name == orion.name
        assert len(restored.tasks) == len(orion.tasks)
        assert len(restored.dependencies) == len(orion.dependencies)

        # Verify task details
        for task_id, task in orion.tasks.items():
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

        normalized = OrionSerializer.normalize_json_data(data)

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

        normalized = OrionSerializer.normalize_json_data(data)

        assert normalized["dependencies"] == data["dependencies"]

    def test_serialization_with_timestamps(self):
        """Test serialization preserves timestamps correctly."""
        orion = TaskOrion(name="Timestamp Test")
        orion.start_execution()
        orion.complete_execution()

        # Serialize and deserialize
        json_str = OrionSerializer.to_json(orion)
        restored = OrionSerializer.from_json(json_str)

        assert restored.execution_start_time is not None
        assert restored.execution_end_time is not None
        assert restored.created_at is not None
        assert restored.updated_at is not None

    def test_serialization_with_metadata(self):
        """Test serialization preserves metadata correctly."""
        orion = TaskOrion(name="Metadata Test")
        orion.update_metadata({"custom_field": "custom_value"})
        orion.update_metadata({"nested": {"key": "value"}})

        # Serialize and deserialize
        data = OrionSerializer.to_dict(orion)
        restored = OrionSerializer.from_dict(data)

        assert restored.metadata["custom_field"] == "custom_value"
        assert restored.metadata["nested"]["key"] == "value"

    def test_empty_orion_serialization(self):
        """Test serialization of empty orion."""
        orion = TaskOrion(name="Empty")

        data = OrionSerializer.to_dict(orion)
        restored = OrionSerializer.from_dict(data)

        assert restored.name == "Empty"
        assert len(restored.tasks) == 0
        assert len(restored.dependencies) == 0
        assert restored.state == OrionState.CREATED

    def test_json_serialization_invalid_input(self):
        """Test error handling for invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            OrionSerializer.from_json("invalid json")

    def test_dict_serialization_missing_fields(self):
        """Test serialization handles missing fields gracefully."""
        minimal_data = {"name": "Minimal Test"}

        orion = OrionSerializer.from_dict(minimal_data)

        assert orion.name == "Minimal Test"
        assert orion.state == OrionState.CREATED
        assert len(orion.tasks) == 0
        assert len(orion.dependencies) == 0
