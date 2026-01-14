"""
Tests for refactored OrionParser integration.
Validates that OrionParser properly uses OrionSerializer and OrionUpdater.
"""

import pytest
import json
from unittest.mock import Mock, patch

from network.orion.parsers.orion_parser import OrionParser
from network.orion.parsers.orion_serializer import (
    OrionSerializer,
)
from network.orion.parsers.orion_updater import OrionUpdater
from network.orion.task_orion import TaskOrion
from network.orion.task_star import TaskStar, TaskPriority


class TestOrionParserRefactored:
    """Test refactored OrionParser functionality."""

    @pytest.fixture
    def parser(self):
        """Create a OrionParser instance."""
        return OrionParser(enable_logging=False)

    @pytest.fixture
    def sample_json_data(self):
        """Create sample JSON data for testing."""
        return {
            "name": "Test Orion",
            "tasks": {
                "task_1": {
                    "task_id": "task_1",
                    "description": "First task",
                    "priority": 2,  # TaskPriority.MEDIUM
                    "status": "pending",
                    "metadata": {},
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                }
            },
            "dependencies": {},
            "metadata": {},
        }

    def test_parser_uses_serializer_for_json_creation(self, parser, sample_json_data):
        """Test that parser uses OrionSerializer for JSON creation."""
        with patch.object(
            OrionSerializer, "normalize_json_data"
        ) as mock_normalize, patch.object(
            OrionSerializer, "from_dict"
        ) as mock_from_dict:

            mock_normalize.return_value = sample_json_data
            mock_orion = TaskOrion(name="Test")
            mock_from_dict.return_value = mock_orion

            result = parser.create_from_json(json.dumps(sample_json_data))

            mock_normalize.assert_called_once()
            mock_from_dict.assert_called_once()
            assert result == mock_orion

    def test_parser_uses_updater_for_llm_updates(self, parser):
        """Test that parser uses OrionUpdater for LLM updates."""
        orion = TaskOrion(name="Test")
        modification_request = "ADD TASK: New task"

        with patch.object(parser._updater, "update_from_llm_output") as mock_update:
            result = parser.update_from_llm(orion, modification_request)

            mock_update.assert_called_once_with(orion, modification_request)
            assert result == orion

    def test_parser_uses_updater_for_task_addition(self, parser):
        """Test that parser uses OrionUpdater for adding tasks."""
        orion = TaskOrion(name="Test")
        orion.add_task(
            TaskStar(task_id="existing_task", description="Existing")
        )

        task = TaskStar(task_id="new_task", description="New task")
        dependencies = ["existing_task"]

        with patch.object(parser._updater, "add_dependencies") as mock_add_deps:
            result = parser.add_task_to_orion(orion, task, dependencies)

            assert result is True
            assert "new_task" in orion.tasks
            mock_add_deps.assert_called_once()

    def test_parser_uses_updater_for_task_removal(self, parser):
        """Test that parser uses OrionUpdater for removing tasks."""
        orion = TaskOrion(name="Test")
        orion.add_task(
            TaskStar(task_id="task_to_remove", description="Remove me")
        )

        with patch.object(parser._updater, "remove_tasks") as mock_remove:
            result = parser.remove_task_from_orion(
                orion, "task_to_remove"
            )

            mock_remove.assert_called_once_with(
                orion, ["task_to_remove"], remove_dependencies=True
            )
            assert result is True

    def test_parser_uses_serializer_for_export(self, parser):
        """Test that parser uses OrionSerializer for export operations."""
        orion = TaskOrion(name="Test")

        with patch.object(OrionSerializer, "to_json") as mock_to_json:
            mock_to_json.return_value = '{"test": "data"}'

            result = parser.export_orion(orion, "json")

            mock_to_json.assert_called_once_with(orion, indent=2)
            assert result == '{"test": "data"}'

    def test_parser_uses_serializer_for_cloning(self, parser):
        """Test that parser uses OrionSerializer for cloning."""
        orion = TaskOrion(name="Original")

        with patch.object(
            OrionSerializer, "to_json"
        ) as mock_to_json, patch.object(
            OrionSerializer, "from_json"
        ) as mock_from_json:

            mock_to_json.return_value = '{"test": "data"}'
            mock_cloned = TaskOrion(name="Cloned")
            mock_from_json.return_value = mock_cloned

            result = parser.clone_orion(orion, "Cloned")

            mock_to_json.assert_called_once()
            mock_from_json.assert_called_once_with('{"test": "data"}')
            assert result.name == "Cloned"

    def test_json_normalization_with_list_dependencies(self, parser):
        """Test that parser properly normalizes JSON with list dependencies."""
        json_data = {
            "name": "Test",
            "tasks": {},
            "dependencies": [{"predecessor_id": "task_1", "successor_id": "task_2"}],
        }

        result = parser.create_from_json(json.dumps(json_data))

        assert result.name == "Test"
        # The normalization should have converted the list to dict format

    def test_orion_name_override(self, parser, sample_json_data):
        """Test that orion name can be overridden during creation."""
        result = parser.create_from_json(
            json.dumps(sample_json_data), orion_name="Override Name"
        )

        assert result.name == "Override Name"

    def test_error_handling_invalid_json(self, parser):
        """Test error handling for invalid JSON input."""
        with pytest.raises(ValueError, match="Invalid JSON data"):
            parser.create_from_json("invalid json")

    def test_create_simple_sequential_delegation(self, parser):
        """Test that simple sequential creation still works after refactoring."""
        descriptions = ["Task 1", "Task 2", "Task 3"]

        result = parser.create_simple_sequential(descriptions, "Sequential Test")

        assert result.name == "Sequential Test"
        assert len(result.tasks) == 3
        assert len(result.dependencies) == 2  # Sequential dependencies

    def test_create_simple_parallel_delegation(self, parser):
        """Test that simple parallel creation still works after refactoring."""
        descriptions = ["Task 1", "Task 2", "Task 3"]

        result = parser.create_simple_parallel(descriptions, "Parallel Test")

        assert result.name == "Parallel Test"
        assert len(result.tasks) == 3
        assert len(result.dependencies) == 0  # No dependencies in parallel

    def test_parser_initialization(self):
        """Test that parser properly initializes its dependencies."""
        parser = OrionParser(enable_logging=True)

        assert parser._updater is not None
        assert isinstance(parser._updater, OrionUpdater)
        assert parser._logger is not None

    def test_parser_initialization_no_logging(self):
        """Test parser initialization without logging."""
        parser = OrionParser(enable_logging=False)

        assert parser._updater is not None
        assert parser._logger is None

    def test_export_format_validation(self, parser):
        """Test that export validates format properly."""
        orion = TaskOrion(name="Test")

        with pytest.raises(ValueError, match="Unsupported export format"):
            parser.export_orion(orion, "invalid_format")

    def test_export_llm_format(self, parser):
        """Test export in LLM format uses orion method."""
        orion = TaskOrion(name="Test")

        result = parser.export_orion(orion, "llm")

        # Should call orion.to_llm_string() directly
        assert isinstance(result, str)
        assert "TaskOrion: Test" in result

    def test_task_addition_error_handling(self, parser):
        """Test error handling in task addition."""
        orion = TaskOrion(name="Test")
        task = TaskStar(task_id="duplicate", description="Task")

        # Add the task first
        orion.add_task(task)

        # Try to add the same task again (should cause error)
        result = parser.add_task_to_orion(orion, task)

        assert result is False

    def test_task_removal_nonexistent_task(self, parser):
        """Test removing a nonexistent task."""
        orion = TaskOrion(name="Test")

        result = parser.remove_task_from_orion(orion, "nonexistent")

        assert result is False

    def test_integration_create_and_update(self, parser):
        """Test integration: create orion and then update it."""
        # Create orion from JSON
        json_data = {
            "name": "Integration Test",
            "tasks": {
                "task_1": {
                    "task_id": "task_1",
                    "description": "Initial task",
                    "priority": 2,  # TaskPriority.MEDIUM
                    "status": "pending",
                    "metadata": {},
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                }
            },
            "dependencies": {},
            "metadata": {},
        }

        orion = parser.create_from_json(json.dumps(json_data))
        assert len(orion.tasks) == 1

        # Update with LLM output
        llm_update = "ADD TASK: Second task from LLM"
        updated = parser.update_from_llm(orion, llm_update)

        # Should be the same orion object, but with updates applied
        assert updated == orion
        assert len(orion.tasks) == 2
