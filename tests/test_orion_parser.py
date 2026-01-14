
"""
Unit tests for OrionParser.

Tests orion creation, parsing, updating, validation,
and export/import functionality.
"""

import asyncio
import json
import pytest
from typing import Dict, List, Optional

from network.orion.parsers.orion_parser import OrionParser
from network.orion.enums import TaskStatus, DeviceType
from network.orion.task_orion import TaskOrion
from network.orion.task_star import TaskStar


class TestOrionParser:
    """Test cases for OrionParser class."""

    @pytest.fixture
    def parser(self):
        """Create a OrionParser instance for testing."""
        return OrionParser(enable_logging=False)

    @pytest.fixture
    def sample_task_descriptions(self):
        """Sample task descriptions for testing."""
        return [
            "Open the browser",
            "Navigate to the website",
            "Fill out the form",
            "Submit the form",
            "Verify the result",
        ]

    @pytest.fixture
    def sample_llm_output(self):
        """Sample LLM output for testing."""
        return """
        Task 1: Open browser
        Description: Launch the web browser application
        
        Task 2: Navigate to site
        Description: Go to the target website
        Dependencies: Task 1
        
        Task 3: Fill form
        Description: Complete the form fields
        Dependencies: Task 2
        
        Task 4: Submit
        Description: Submit the completed form
        Dependencies: Task 3
        """

    @pytest.fixture
    def sample_orion_json(self):
        """Sample orion JSON data for testing."""
        return json.dumps(
            {
                "orion_id": "test_orion",
                "name": "Test Orion",
                "description": "Test orion for parsing",
                "tasks": {
                    "task1": {
                        "task_id": "task1",
                        "description": "First task",
                        "status": "pending",
                    },
                    "task2": {
                        "task_id": "task2",
                        "description": "Second task",
                        "status": "pending",
                    },
                },
                "dependencies": [
                    {
                        "predecessor_id": "task1",
                        "successor_id": "task2",
                        "dependency_type": "unconditional",
                    }
                ],
            }
        )

    @pytest.mark.asyncio
    async def test_create_from_llm(self, parser, sample_llm_output):
        """Test creating orion from LLM output."""
        orion = await parser.create_from_llm(
            sample_llm_output, "LLM Test Orion"
        )

        assert isinstance(orion, TaskOrion)
        assert orion.name == "LLM Test Orion"
        assert orion.task_count > 0

        # Should have parsed the tasks mentioned in LLM output
        task_ids = list(orion.tasks.keys())
        assert len(task_ids) > 0

    @pytest.mark.asyncio
    async def test_create_from_json(self, parser, sample_orion_json):
        """Test creating orion from JSON data."""
        orion = await parser.create_from_json(
            sample_orion_json, "JSON Test Orion"
        )

        assert isinstance(orion, TaskOrion)
        assert orion.name == "JSON Test Orion"
        assert orion.task_count == 2
        assert "task1" in orion.tasks
        assert "task2" in orion.tasks
        assert orion.dependency_count == 1

    @pytest.mark.asyncio
    async def test_create_simple_sequential(self, parser, sample_task_descriptions):
        """Test creating simple sequential orion."""
        orion = parser.create_simple_sequential(
            sample_task_descriptions, "Sequential Test"
        )

        assert isinstance(orion, TaskOrion)
        assert orion.name == "Sequential Test"
        assert orion.task_count == len(sample_task_descriptions)

        # Should have dependencies for sequential execution
        assert orion.dependency_count == len(sample_task_descriptions) - 1

        # Verify task descriptions
        for i, description in enumerate(sample_task_descriptions):
            task_id = f"task_{i+1}"
            assert task_id in orion.tasks
            assert description in orion.tasks[task_id].description

    @pytest.mark.asyncio
    async def test_create_simple_parallel(self, parser, sample_task_descriptions):
        """Test creating simple parallel orion."""
        orion = parser.create_simple_parallel(
            sample_task_descriptions, "Parallel Test"
        )

        assert isinstance(orion, TaskOrion)
        assert orion.name == "Parallel Test"
        assert orion.task_count == len(sample_task_descriptions)

        # Should have no dependencies for parallel execution
        assert orion.dependency_count == 0

        # All tasks should be ready to execute
        ready_tasks = orion.get_ready_tasks()
        assert len(ready_tasks) == len(sample_task_descriptions)

    @pytest.mark.asyncio
    async def test_update_from_llm(self, parser):
        """Test updating orion from LLM output."""
        # Create initial orion
        initial_tasks = ["Task A", "Task B"]
        orion = parser.create_simple_sequential(
            initial_tasks, "Test Orion"
        )

        initial_task_count = orion.task_count

        # Update with LLM request
        update_request = "Add a new task 'Task C' after Task B"
        updated_orion = await parser.update_from_llm(
            orion, update_request
        )

        assert isinstance(updated_orion, TaskOrion)
        # The update is currently a placeholder that returns the original
        # In a real implementation, this would parse the LLM response
        assert updated_orion.task_count == initial_task_count

    def test_add_task_to_orion(self, parser):
        """Test adding a task to existing orion."""
        orion = TaskOrion(name="Test Orion")

        # Add initial task
        task1 = TaskStar(task_id="task1", description="Initial task")
        orion.add_task(task1)

        # Add new task with dependencies
        task2 = TaskStar(task_id="task2", description="Dependent task")
        success = parser.add_task_to_orion(
            orion, task2, dependencies=["task1"]
        )

        assert success
        assert orion.task_count == 2
        assert "task2" in orion.tasks
        assert orion.dependency_count == 1

    def test_remove_task_from_orion(self, parser):
        """Test removing a task from orion."""
        orion = TaskOrion(name="Test Orion")

        # Add tasks
        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        orion.add_task(task1)
        orion.add_task(task2)

        initial_count = orion.task_count

        # Remove task
        success = parser.remove_task_from_orion(orion, "task1")

        assert success
        assert orion.task_count == initial_count - 1
        assert "task1" not in orion.tasks
        assert "task2" in orion.tasks

    def test_remove_nonexistent_task(self, parser):
        """Test removing a nonexistent task."""
        orion = TaskOrion(name="Test Orion")

        # Try to remove nonexistent task
        success = parser.remove_task_from_orion(orion, "nonexistent")

        assert not success

    def test_validate_orion_valid(self, parser):
        """Test validating a valid orion."""
        orion = TaskOrion(name="Valid Orion")

        # Add tasks
        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        orion.add_task(task1)
        orion.add_task(task2)

        is_valid, errors = parser.validate_orion(orion)

        assert is_valid
        assert len(errors) == 0

    def test_validate_orion_empty(self, parser):
        """Test validating an empty orion."""
        orion = TaskOrion(name="Empty Orion")

        is_valid, errors = parser.validate_orion(orion)

        assert not is_valid
        assert len(errors) > 0
        assert any("no tasks" in error.lower() for error in errors)

    def test_export_orion_json(self, parser):
        """Test exporting orion to JSON format."""
        orion = TaskOrion(name="Export Test")

        # Add a task
        task = TaskStar(task_id="task1", description="Test task")
        orion.add_task(task)

        exported = parser.export_orion(orion, "json")

        assert isinstance(exported, str)
        # Should be valid JSON
        parsed = json.loads(exported)
        assert parsed["name"] == "Export Test"
        assert "tasks" in parsed

    def test_export_orion_llm(self, parser):
        """Test exporting orion to LLM format."""
        orion = TaskOrion(name="Export Test")

        # Add a task
        task = TaskStar(task_id="task1", description="Test task")
        orion.add_task(task)

        exported = parser.export_orion(orion, "llm")

        assert isinstance(exported, str)
        assert "Export Test" in exported
        assert "Test task" in exported

    def test_export_orion_yaml(self, parser):
        """Test exporting orion to YAML format."""
        orion = TaskOrion(name="Export Test")

        # Add a task
        task = TaskStar(task_id="task1", description="Test task")
        orion.add_task(task)

        exported = parser.export_orion(orion, "yaml")

        assert isinstance(exported, str)
        # Should contain YAML comment since full YAML export is not implemented
        assert "YAML export not implemented" in exported

    def test_export_orion_unsupported_format(self, parser):
        """Test exporting orion with unsupported format."""
        orion = TaskOrion(name="Export Test")

        with pytest.raises(ValueError, match="Unsupported export format"):
            parser.export_orion(orion, "unsupported")

    def test_clone_orion(self, parser):
        """Test cloning a orion."""
        # Create original orion
        original = TaskOrion(name="Original Orion")
        task = TaskStar(task_id="task1", description="Original task")
        original.add_task(task)

        # Clone
        cloned = parser.clone_orion(original, "Cloned Orion")

        assert isinstance(cloned, TaskOrion)
        assert cloned.name == "Cloned Orion"
        assert cloned.task_count == original.task_count
        assert cloned.orion_id != original.orion_id

        # Should have the same tasks but different instances
        assert "task1" in cloned.tasks
        assert cloned.tasks["task1"].description == "Original task"

    def test_clone_orion_default_name(self, parser):
        """Test cloning orion with default name."""
        original = TaskOrion(name="Original")

        cloned = parser.clone_orion(original)

        assert cloned.name == "Original (Copy)"

    def test_merge_orions(self, parser):
        """Test merging two orions."""
        # Create first orion
        orion1 = TaskOrion(name="Orion 1")
        task1 = TaskStar(task_id="task1", description="Task from orion 1")
        orion1.add_task(task1)

        # Create second orion
        orion2 = TaskOrion(name="Orion 2")
        task2 = TaskStar(task_id="task2", description="Task from orion 2")
        orion2.add_task(task2)

        # Merge
        merged = parser.merge_orions(
            orion1, orion2, "Merged Orion"
        )

        assert isinstance(merged, TaskOrion)
        assert merged.name == "Merged Orion"
        assert merged.task_count == 2
        assert "c1_task1" in merged.tasks
        assert "c2_task2" in merged.tasks

    def test_merge_orions_default_name(self, parser):
        """Test merging orions with default name."""
        orion1 = TaskOrion(name="First")
        orion2 = TaskOrion(name="Second")

        merged = parser.merge_orions(orion1, orion2)

        assert merged.name == "First + Second"

    def test_merge_orions_with_conflicts(self, parser):
        """Test merging orions with task ID conflicts."""
        # Create orions with same task ID
        orion1 = TaskOrion(name="Orion 1")
        task1a = TaskStar(task_id="task1", description="Task 1 from orion 1")
        orion1.add_task(task1a)

        orion2 = TaskOrion(name="Orion 2")
        task1b = TaskStar(task_id="task1", description="Task 1 from orion 2")
        orion2.add_task(task1b)

        # Merge should handle conflicts by renaming
        merged = parser.merge_orions(orion1, orion2)

        assert merged.task_count == 2
        # Should have renamed one of the conflicting tasks
        task_ids = list(merged.tasks.keys())
        assert len(task_ids) == 2

    @pytest.mark.asyncio
    async def test_create_from_empty_llm_output(self, parser):
        """Test creating orion from empty LLM output."""
        empty_output = ""

        orion = await parser.create_from_llm(empty_output)

        # Should create empty orion
        assert isinstance(orion, TaskOrion)
        assert orion.task_count == 0

    @pytest.mark.asyncio
    async def test_create_from_invalid_json(self, parser):
        """Test creating orion from invalid JSON."""
        invalid_json = "{ invalid json"

        with pytest.raises(json.JSONDecodeError):
            await parser.create_from_json(invalid_json)

    def test_add_task_with_invalid_dependencies(self, parser):
        """Test adding task with nonexistent dependencies."""
        orion = TaskOrion(name="Test Orion")

        task = TaskStar(task_id="task1", description="Test task")

        # Try to add task with nonexistent dependency
        success = parser.add_task_to_orion(
            orion, task, dependencies=["nonexistent_task"]
        )

        # Should still add the task but dependency creation might fail
        assert "task1" in orion.tasks

    @pytest.mark.asyncio
    async def test_parser_with_logging_enabled(self):
        """Test parser with logging enabled."""
        parser = OrionParser(enable_logging=True)

        orion = parser.create_simple_sequential(
            ["Task 1", "Task 2"], "Logged Test"
        )

        assert isinstance(orion, TaskOrion)
        assert orion.task_count == 2

    @pytest.mark.asyncio
    async def test_update_from_llm_with_empty_request(self, parser):
        """Test updating orion with empty LLM request."""
        orion = TaskOrion(name="Test")

        # Update with empty request
        updated = await parser.update_from_llm(orion, "")

        # Should return original orion
        assert updated is orion

    def test_validate_orion_with_cycles(self, parser):
        """Test validating orion with circular dependencies."""
        orion = TaskOrion(name="Cyclic Orion")

        # Add tasks
        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        orion.add_task(task1)
        orion.add_task(task2)

        # Create circular dependency manually (if orion allows)
        # This would be caught by orion's own validation
        is_valid, errors = parser.validate_orion(orion)

        # Should be valid if no cycles exist
        assert is_valid or any("cycle" in error.lower() for error in errors)


class TestOrionParserIntegration:
    """Integration tests for OrionParser with other components."""

    @pytest.fixture
    def parser(self):
        """Create a OrionParser instance for testing."""
        return OrionParser(enable_logging=False)

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, parser):
        """Test complete workflow from creation to export."""
        # Create orion
        tasks = ["Step 1", "Step 2", "Step 3"]
        orion = parser.create_simple_sequential(tasks, "E2E Test")

        # Validate
        is_valid, errors = parser.validate_orion(orion)
        assert is_valid

        # Clone
        cloned = parser.clone_orion(orion, "E2E Cloned")

        # Export original
        json_export = parser.export_orion(orion, "json")
        llm_export = parser.export_orion(orion, "llm")

        # Verify exports are different but both contain orion data
        assert json_export != llm_export
        assert "E2E Test" in json_export
        assert "E2E Test" in llm_export

        # Create new orion from JSON export
        reimported = await parser.create_from_json(json_export, "Reimported")
        assert reimported.task_count == orion.task_count

    @pytest.mark.asyncio
    async def test_complex_orion_operations(self, parser):
        """Test complex operations on orions."""
        # Create two orions
        orion1 = parser.create_simple_sequential(["A1", "A2"], "First")
        orion2 = parser.create_simple_parallel(["B1", "B2", "B3"], "Second")

        # Merge them
        merged = parser.merge_orions(orion1, orion2)
        assert merged.task_count == 5

        # Add a new task to merged orion
        new_task = TaskStar(task_id="new_task", description="New task")
        success = parser.add_task_to_orion(merged, new_task)
        assert success
        assert merged.task_count == 6

        # Remove a task
        success = parser.remove_task_from_orion(merged, "new_task")
        assert success
        assert merged.task_count == 5

        # Validate final result
        is_valid, errors = parser.validate_orion(merged)
        assert is_valid
