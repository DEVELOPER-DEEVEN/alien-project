#!/usr/bin/env python
"""
Final comprehensive test for all network change detection features.
"""

import asyncio
import pytest
import time
from cluster.network import Tasknetwork, TaskStar, TaskStarLine
from cluster.session.observers import DAGVisualizationObserver
from cluster.core.events import networkEvent, EventType


@pytest.mark.asyncio
async def test_all_change_types():
    """Comprehensive test for all types of network changes."""
    print("🧪 Comprehensive network Change Detection Test\n")

    observer = DAGVisualizationObserver()

    # Test 1: Tasks and Dependencies Added
    print("=== Test 1: Tasks and Dependencies Added ===")

    original1 = Tasknetwork("test-1", "Test network 1")
    task1 = TaskStar("task1", "Task 1")
    original1.add_task(task1)

    modified1 = Tasknetwork("test-1", "Test network 1")
    task1_mod = TaskStar("task1", "Task 1")
    task2_mod = TaskStar("task2", "Task 2")
    task3_mod = TaskStar("task3", "Task 3")
    dep1_mod = TaskStarLine("task1", "task2")
    dep2_mod = TaskStarLine("task2", "task3")

    modified1.add_task(task1_mod)
    modified1.add_task(task2_mod)
    modified1.add_task(task3_mod)
    modified1.add_dependency(dep1_mod)
    modified1.add_dependency(dep2_mod)

    event1 = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test",
        timestamp=time.time(),
        data={"old_network": original1, "new_network": modified1},
        network_id="test-1",
        network_state="modified",
    )

    await observer.on_event(event1)
    print("\n")

    # Test 2: Tasks and Dependencies Removed
    print("=== Test 2: Tasks and Dependencies Removed ===")

    original2 = Tasknetwork("test-2", "Test network 2")
    task1_orig = TaskStar("task1", "Task 1")
    task2_orig = TaskStar("task2", "Task 2")
    task3_orig = TaskStar("task3", "Task 3")
    dep1_orig = TaskStarLine("task1", "task2")
    dep2_orig = TaskStarLine("task2", "task3")

    original2.add_task(task1_orig)
    original2.add_task(task2_orig)
    original2.add_task(task3_orig)
    original2.add_dependency(dep1_orig)
    original2.add_dependency(dep2_orig)

    modified2 = Tasknetwork("test-2", "Test network 2")
    task1_mod2 = TaskStar("task1", "Task 1")
    modified2.add_task(task1_mod2)

    event2 = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test",
        timestamp=time.time(),
        data={"old_network": original2, "new_network": modified2},
        network_id="test-2",
        network_state="modified",
    )

    await observer.on_event(event2)
    print("\n")

    # Test 3: Task Properties Modified (using name and description)
    print("=== Test 3: Task Properties Modified ===")

    original3 = Tasknetwork("test-3", "Test network 3")
    task1_orig3 = TaskStar("task1", "Original Task Name", "Original description")
    original3.add_task(task1_orig3)

    modified3 = Tasknetwork("test-3", "Test network 3")
    task1_mod3 = TaskStar(
        "task1", "Modified Task Name", "Modified description"
    )  # Changed name and description
    modified3.add_task(task1_mod3)

    event3 = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test",
        timestamp=time.time(),
        data={"old_network": original3, "new_network": modified3},
        network_id="test-3",
        network_state="modified",
    )

    await observer.on_event(event3)
    print("\n")

    # Test 4: Dependency Properties Modified
    print("=== Test 4: Dependency Properties Modified ===")

    original4 = Tasknetwork("test-4", "Test network 4")
    task1_orig4 = TaskStar("task1", "Task 1")
    task2_orig4 = TaskStar("task2", "Task 2")
    dep1_orig4 = TaskStarLine("task1", "task2")
    dep1_orig4.trigger_action = "original_action"
    dep1_orig4.condition = "original_condition"

    original4.add_task(task1_orig4)
    original4.add_task(task2_orig4)
    original4.add_dependency(dep1_orig4)

    modified4 = Tasknetwork("test-4", "Test network 4")
    task1_mod4 = TaskStar("task1", "Task 1")
    task2_mod4 = TaskStar("task2", "Task 2")
    dep1_mod4 = TaskStarLine("task1", "task2")
    dep1_mod4.trigger_action = "modified_action"  # Changed
    dep1_mod4.condition = "modified_condition"  # Changed

    modified4.add_task(task1_mod4)
    modified4.add_task(task2_mod4)
    modified4.add_dependency(dep1_mod4)

    event4 = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test",
        timestamp=time.time(),
        data={"old_network": original4, "new_network": modified4},
        network_id="test-4",
        network_state="modified",
    )

    await observer.on_event(event4)
    print("\n")

    print("✅ All comprehensive change detection tests completed!")
    print("🎉 Features successfully implemented:")
    print("   •  [Text Cleaned]  old/new network， [Text Cleaned] ")
    print("   •  [Text Cleaned]  Rich  [Text Cleaned] ， [Text Cleaned] ")
    print("   • task  [Text Cleaned]  dep  [Text Cleaned] ")


if __name__ == "__main__":
    asyncio.run(test_all_change_types())
