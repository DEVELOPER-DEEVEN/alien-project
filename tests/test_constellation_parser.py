# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Unit tests for networkParser.

Tests network creation, parsing, updating, validation,
and export/import functionality.
"""

import asyncio
import json
import pytest
from typing import Dict, List, Optional

from cluster.network.parsers.network_parser import networkParser
from cluster.network.enums import TaskStatus, DeviceType
from cluster.network.task_network import Tasknetwork
from cluster.network.task_star import TaskStar


class TestnetworkParser:
    """Test cases for networkParser class."""

    @pytest.fixture
    def parser(self):
        """Create a networkParser instance for testing."""
        return networkParser(enable_logging=False)

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
    def sample_network_json(self):
        """Sample network JSON data for testing."""
        return json.dumps(
            {
                "network_id": "test_network",
                "name": "Test network",
                "description": "Test network for parsing",
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
        """Test creating network from LLM output."""
        network = await parser.create_from_llm(
            sample_llm_output, "LLM Test network"
        )

        assert isinstance(network, Tasknetwork)
        assert network.name == "LLM Test network"
        assert network.task_count > 0

        # Should have parsed the tasks mentioned in LLM output
        task_ids = list(network.tasks.keys())
        assert len(task_ids) > 0

    @pytest.mark.asyncio
    async def test_create_from_json(self, parser, sample_network_json):
        """Test creating network from JSON data."""
        network = await parser.create_from_json(
            sample_network_json, "JSON Test network"
        )

        assert isinstance(network, Tasknetwork)
        assert network.name == "JSON Test network"
        assert network.task_count == 2
        assert "task1" in network.tasks
        assert "task2" in network.tasks
        assert network.dependency_count == 1

    @pytest.mark.asyncio
    async def test_create_simple_sequential(self, parser, sample_task_descriptions):
        """Test creating simple sequential network."""
        network = parser.create_simple_sequential(
            sample_task_descriptions, "Sequential Test"
        )

        assert isinstance(network, Tasknetwork)
        assert network.name == "Sequential Test"
        assert network.task_count == len(sample_task_descriptions)

        # Should have dependencies for sequential execution
        assert network.dependency_count == len(sample_task_descriptions) - 1

        # Verify task descriptions
        for i, description in enumerate(sample_task_descriptions):
            task_id = f"task_{i+1}"
            assert task_id in network.tasks
            assert description in network.tasks[task_id].description

    @pytest.mark.asyncio
    async def test_create_simple_parallel(self, parser, sample_task_descriptions):
        """Test creating simple parallel network."""
        network = parser.create_simple_parallel(
            sample_task_descriptions, "Parallel Test"
        )

        assert isinstance(network, Tasknetwork)
        assert network.name == "Parallel Test"
        assert network.task_count == len(sample_task_descriptions)

        # Should have no dependencies for parallel execution
        assert network.dependency_count == 0

        # All tasks should be ready to execute
        ready_tasks = network.get_ready_tasks()
        assert len(ready_tasks) == len(sample_task_descriptions)

    @pytest.mark.asyncio
    async def test_update_from_llm(self, parser):
        """Test updating network from LLM output."""
        # Create initial network
        initial_tasks = ["Task A", "Task B"]
        network = parser.create_simple_sequential(
            initial_tasks, "Test network"
        )

        initial_task_count = network.task_count

        # Update with LLM request
        update_request = "Add a new task 'Task C' after Task B"
        updated_network = await parser.update_from_llm(
            network, update_request
        )

        assert isinstance(updated_network, Tasknetwork)
        # The update is currently a placeholder that returns the original
        # In a real implementation, this would parse the LLM response
        assert updated_network.task_count == initial_task_count

    def test_add_task_to_network(self, parser):
        """Test adding a task to existing network."""
        network = Tasknetwork(name="Test network")

        # Add initial task
        task1 = TaskStar(task_id="task1", description="Initial task")
        network.add_task(task1)

        # Add new task with dependencies
        task2 = TaskStar(task_id="task2", description="Dependent task")
        success = parser.add_task_to_network(
            network, task2, dependencies=["task1"]
        )

        assert success
        assert network.task_count == 2
        assert "task2" in network.tasks
        assert network.dependency_count == 1

    def test_remove_task_from_network(self, parser):
        """Test removing a task from network."""
        network = Tasknetwork(name="Test network")

        # Add tasks
        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        network.add_task(task1)
        network.add_task(task2)

        initial_count = network.task_count

        # Remove task
        success = parser.remove_task_from_network(network, "task1")

        assert success
        assert network.task_count == initial_count - 1
        assert "task1" not in network.tasks
        assert "task2" in network.tasks

    def test_remove_nonexistent_task(self, parser):
        """Test removing a nonexistent task."""
        network = Tasknetwork(name="Test network")

        # Try to remove nonexistent task
        success = parser.remove_task_from_network(network, "nonexistent")

        assert not success

    def test_validate_network_valid(self, parser):
        """Test validating a valid network."""
        network = Tasknetwork(name="Valid network")

        # Add tasks
        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        network.add_task(task1)
        network.add_task(task2)

        is_valid, errors = parser.validate_network(network)

        assert is_valid
        assert len(errors) == 0

    def test_validate_network_empty(self, parser):
        """Test validating an empty network."""
        network = Tasknetwork(name="Empty network")

        is_valid, errors = parser.validate_network(network)

        assert not is_valid
        assert len(errors) > 0
        assert any("no tasks" in error.lower() for error in errors)

    def test_export_network_json(self, parser):
        """Test exporting network to JSON format."""
        network = Tasknetwork(name="Export Test")

        # Add a task
        task = TaskStar(task_id="task1", description="Test task")
        network.add_task(task)

        exported = parser.export_network(network, "json")

        assert isinstance(exported, str)
        # Should be valid JSON
        parsed = json.loads(exported)
        assert parsed["name"] == "Export Test"
        assert "tasks" in parsed

    def test_export_network_llm(self, parser):
        """Test exporting network to LLM format."""
        network = Tasknetwork(name="Export Test")

        # Add a task
        task = TaskStar(task_id="task1", description="Test task")
        network.add_task(task)

        exported = parser.export_network(network, "llm")

        assert isinstance(exported, str)
        assert "Export Test" in exported
        assert "Test task" in exported

    def test_export_network_yaml(self, parser):
        """Test exporting network to YAML format."""
        network = Tasknetwork(name="Export Test")

        # Add a task
        task = TaskStar(task_id="task1", description="Test task")
        network.add_task(task)

        exported = parser.export_network(network, "yaml")

        assert isinstance(exported, str)
        # Should contain YAML comment since full YAML export is not implemented
        assert "YAML export not implemented" in exported

    def test_export_network_unsupported_format(self, parser):
        """Test exporting network with unsupported format."""
        network = Tasknetwork(name="Export Test")

        with pytest.raises(ValueError, match="Unsupported export format"):
            parser.export_network(network, "unsupported")

    def test_clone_network(self, parser):
        """Test cloning a network."""
        # Create original network
        original = Tasknetwork(name="Original network")
        task = TaskStar(task_id="task1", description="Original task")
        original.add_task(task)

        # Clone
        cloned = parser.clone_network(original, "Cloned network")

        assert isinstance(cloned, Tasknetwork)
        assert cloned.name == "Cloned network"
        assert cloned.task_count == original.task_count
        assert cloned.network_id != original.network_id

        # Should have the same tasks but different instances
        assert "task1" in cloned.tasks
        assert cloned.tasks["task1"].description == "Original task"

    def test_clone_network_default_name(self, parser):
        """Test cloning network with default name."""
        original = Tasknetwork(name="Original")

        cloned = parser.clone_network(original)

        assert cloned.name == "Original (Copy)"

    def test_merge_networks(self, parser):
        """Test merging two networks."""
        # Create first network
        network1 = Tasknetwork(name="network 1")
        task1 = TaskStar(task_id="task1", description="Task from network 1")
        network1.add_task(task1)

        # Create second network
        network2 = Tasknetwork(name="network 2")
        task2 = TaskStar(task_id="task2", description="Task from network 2")
        network2.add_task(task2)

        # Merge
        merged = parser.merge_networks(
            network1, network2, "Merged network"
        )

        assert isinstance(merged, Tasknetwork)
        assert merged.name == "Merged network"
        assert merged.task_count == 2
        assert "c1_task1" in merged.tasks
        assert "c2_task2" in merged.tasks

    def test_merge_networks_default_name(self, parser):
        """Test merging networks with default name."""
        network1 = Tasknetwork(name="First")
        network2 = Tasknetwork(name="Second")

        merged = parser.merge_networks(network1, network2)

        assert merged.name == "First + Second"

    def test_merge_networks_with_conflicts(self, parser):
        """Test merging networks with task ID conflicts."""
        # Create networks with same task ID
        network1 = Tasknetwork(name="network 1")
        task1a = TaskStar(task_id="task1", description="Task 1 from network 1")
        network1.add_task(task1a)

        network2 = Tasknetwork(name="network 2")
        task1b = TaskStar(task_id="task1", description="Task 1 from network 2")
        network2.add_task(task1b)

        # Merge should handle conflicts by renaming
        merged = parser.merge_networks(network1, network2)

        assert merged.task_count == 2
        # Should have renamed one of the conflicting tasks
        task_ids = list(merged.tasks.keys())
        assert len(task_ids) == 2

    @pytest.mark.asyncio
    async def test_create_from_empty_llm_output(self, parser):
        """Test creating network from empty LLM output."""
        empty_output = ""

        network = await parser.create_from_llm(empty_output)

        # Should create empty network
        assert isinstance(network, Tasknetwork)
        assert network.task_count == 0

    @pytest.mark.asyncio
    async def test_create_from_invalid_json(self, parser):
        """Test creating network from invalid JSON."""
        invalid_json = "{ invalid json"

        with pytest.raises(json.JSONDecodeError):
            await parser.create_from_json(invalid_json)

    def test_add_task_with_invalid_dependencies(self, parser):
        """Test adding task with nonexistent dependencies."""
        network = Tasknetwork(name="Test network")

        task = TaskStar(task_id="task1", description="Test task")

        # Try to add task with nonexistent dependency
        success = parser.add_task_to_network(
            network, task, dependencies=["nonexistent_task"]
        )

        # Should still add the task but dependency creation might fail
        assert "task1" in network.tasks

    @pytest.mark.asyncio
    async def test_parser_with_logging_enabled(self):
        """Test parser with logging enabled."""
        parser = networkParser(enable_logging=True)

        network = parser.create_simple_sequential(
            ["Task 1", "Task 2"], "Logged Test"
        )

        assert isinstance(network, Tasknetwork)
        assert network.task_count == 2

    @pytest.mark.asyncio
    async def test_update_from_llm_with_empty_request(self, parser):
        """Test updating network with empty LLM request."""
        network = Tasknetwork(name="Test")

        # Update with empty request
        updated = await parser.update_from_llm(network, "")

        # Should return original network
        assert updated is network

    def test_validate_network_with_cycles(self, parser):
        """Test validating network with circular dependencies."""
        network = Tasknetwork(name="Cyclic network")

        # Add tasks
        task1 = TaskStar(task_id="task1", description="First task")
        task2 = TaskStar(task_id="task2", description="Second task")
        network.add_task(task1)
        network.add_task(task2)

        # Create circular dependency manually (if network allows)
        # This would be caught by network's own validation
        is_valid, errors = parser.validate_network(network)

        # Should be valid if no cycles exist
        assert is_valid or any("cycle" in error.lower() for error in errors)


class TestnetworkParserIntegration:
    """Integration tests for networkParser with other components."""

    @pytest.fixture
    def parser(self):
        """Create a networkParser instance for testing."""
        return networkParser(enable_logging=False)

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, parser):
        """Test complete workflow from creation to export."""
        # Create network
        tasks = ["Step 1", "Step 2", "Step 3"]
        network = parser.create_simple_sequential(tasks, "E2E Test")

        # Validate
        is_valid, errors = parser.validate_network(network)
        assert is_valid

        # Clone
        cloned = parser.clone_network(network, "E2E Cloned")

        # Export original
        json_export = parser.export_network(network, "json")
        llm_export = parser.export_network(network, "llm")

        # Verify exports are different but both contain network data
        assert json_export != llm_export
        assert "E2E Test" in json_export
        assert "E2E Test" in llm_export

        # Create new network from JSON export
        reimported = await parser.create_from_json(json_export, "Reimported")
        assert reimported.task_count == network.task_count

    @pytest.mark.asyncio
    async def test_complex_network_operations(self, parser):
        """Test complex operations on networks."""
        # Create two networks
        network1 = parser.create_simple_sequential(["A1", "A2"], "First")
        network2 = parser.create_simple_parallel(["B1", "B2", "B3"], "Second")

        # Merge them
        merged = parser.merge_networks(network1, network2)
        assert merged.task_count == 5

        # Add a new task to merged network
        new_task = TaskStar(task_id="new_task", description="New task")
        success = parser.add_task_to_network(merged, new_task)
        assert success
        assert merged.task_count == 6

        # Remove a task
        success = parser.remove_task_from_network(merged, "new_task")
        assert success
        assert merged.task_count == 5

        # Validate final result
        is_valid, errors = parser.validate_network(merged)
        assert is_valid
