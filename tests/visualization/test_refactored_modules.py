#!/usr/bin/env python3
"""
Test the refactored visualization modules.
"""

import pytest
from unittest.mock import Mock
from io import StringIO

from cluster.visualization import (
    DAGVisualizer,
    TaskDisplay,
    networkDisplay,
    VisualizationChangeDetector,
)
from cluster.network.enums import TaskStatus, TaskPriority


class MockTaskStar:
    """Mock TaskStar for testing."""

    def __init__(
        self, task_id="test_task", name="Test Task", status=TaskStatus.PENDING
    ):
        self.task_id = task_id
        self.name = name
        self.status = status
        self.priority = TaskPriority.MEDIUM
        self.target_device_id = "test_device"
        self.description = "Test description"


class Mocknetwork:
    """Mock Tasknetwork for testing."""

    def __init__(self):
        self.network_id = "test_network_123"
        self.name = "Test network"
        self.task_count = 3
        self.tasks = {}
        self.dependencies = {}

    def get_statistics(self):
        return {
            "total_tasks": 3,
            "total_dependencies": 2,
            "task_status_counts": {
                "completed": 1,
                "running": 1,
                "pending": 1,
                "failed": 0,
            },
        }

    def get_ready_tasks(self):
        return []


def test_task_display_creation():
    """Test TaskDisplay can be created and has required methods."""
    task_display = TaskDisplay()
    assert task_display is not None
    assert hasattr(task_display, "display_task_started")
    assert hasattr(task_display, "display_task_completed")
    assert hasattr(task_display, "display_task_failed")
    assert hasattr(task_display, "get_task_status_icon")


def test_network_display_creation():
    """Test networkDisplay can be created and has required methods."""
    network_display = networkDisplay()
    assert network_display is not None
    assert hasattr(network_display, "display_network_started")
    assert hasattr(network_display, "display_network_completed")
    assert hasattr(network_display, "display_network_failed")


def test_dag_visualizer_creation():
    """Test DAGVisualizer can be created with new display components."""
    visualizer = DAGVisualizer()
    assert visualizer is not None
    assert hasattr(visualizer, "task_display")
    assert hasattr(visualizer, "network_display")
    assert isinstance(visualizer.task_display, TaskDisplay)
    assert isinstance(visualizer.network_display, networkDisplay)


def test_change_detector_functionality():
    """Test VisualizationChangeDetector basic functionality."""
    # Test with no old network (new network)
    mock_network = Mocknetwork()
    changes = VisualizationChangeDetector.calculate_network_changes(
        None, mock_network
    )

    assert changes is not None
    assert changes["modification_type"] == "network_created"
    assert "added_tasks" in changes
    assert "removed_tasks" in changes


def test_task_status_icons():
    """Test task status icon mapping."""
    task_display = TaskDisplay()

    # Test all status types have icons
    for status in TaskStatus:
        icon = task_display.get_task_status_icon(status)
        assert icon is not None
        assert len(icon) > 0


def test_task_summary_formatting():
    """Test task summary formatting."""
    task_display = TaskDisplay()
    mock_task = MockTaskStar()

    summary = task_display.format_task_summary(mock_task)
    assert mock_task.name in summary
    assert len(summary) > 0

    summary_no_id = task_display.format_task_summary(mock_task, include_id=False)
    assert mock_task.name in summary_no_id
    assert len(summary_no_id) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
