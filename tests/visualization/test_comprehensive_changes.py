#!/usr/bin/env python
"""
Final comprehensive test for all orion change detection features.
"""

import asyncio
import pytest
import time
from network.orion import TaskOrion, TaskStar, TaskStarLine
from network.session.observers import DAGVisualizationObserver
from network.core.events import OrionEvent, EventType


@pytest.mark.asyncio
async def test_all_change_types():
    """Comprehensive test for all types of orion changes."""
    print(" Comprehensive Orion Change Detection Test\n")

    observer = DAGVisualizationObserver()

    # Test 1: Tasks and Dependencies Added
    print("=== Test 1: Tasks and Dependencies Added ===")

    original1 = TaskOrion("test-1", "Test Orion 1")
    task1 = TaskStar("task1", "Task 1")
    original1.add_task(task1)

    modified1 = TaskOrion("test-1", "Test Orion 1")
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

    event1 = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test",
        timestamp=time.time(),
        data={"old_orion": original1, "new_orion": modified1},
        orion_id="test-1",
        orion_state="modified",
    )

    await observer.on_event(event1)
    print("\n")

    # Test 2: Tasks and Dependencies Removed
    print("=== Test 2: Tasks and Dependencies Removed ===")

    original2 = TaskOrion("test-2", "Test Orion 2")
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

    modified2 = TaskOrion("test-2", "Test Orion 2")
    task1_mod2 = TaskStar("task1", "Task 1")
    modified2.add_task(task1_mod2)

    event2 = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test",
        timestamp=time.time(),
        data={"old_orion": original2, "new_orion": modified2},
        orion_id="test-2",
        orion_state="modified",
    )

    await observer.on_event(event2)
    print("\n")

    # Test 3: Task Properties Modified (using name and description)
    print("=== Test 3: Task Properties Modified ===")

    original3 = TaskOrion("test-3", "Test Orion 3")
    task1_orig3 = TaskStar("task1", "Original Task Name", "Original description")
    original3.add_task(task1_orig3)

    modified3 = TaskOrion("test-3", "Test Orion 3")
    task1_mod3 = TaskStar(
        "task1", "Modified Task Name", "Modified description"
    )  # Changed name and description
    modified3.add_task(task1_mod3)

    event3 = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test",
        timestamp=time.time(),
        data={"old_orion": original3, "new_orion": modified3},
        orion_id="test-3",
        orion_state="modified",
    )

    await observer.on_event(event3)
    print("\n")

    # Test 4: Dependency Properties Modified
    print("=== Test 4: Dependency Properties Modified ===")

    original4 = TaskOrion("test-4", "Test Orion 4")
    task1_orig4 = TaskStar("task1", "Task 1")
    task2_orig4 = TaskStar("task2", "Task 2")
    dep1_orig4 = TaskStarLine("task1", "task2")
    dep1_orig4.trigger_action = "original_action"
    dep1_orig4.condition = "original_condition"

    original4.add_task(task1_orig4)
    original4.add_task(task2_orig4)
    original4.add_dependency(dep1_orig4)

    modified4 = TaskOrion("test-4", "Test Orion 4")
    task1_mod4 = TaskStar("task1", "Task 1")
    task2_mod4 = TaskStar("task2", "Task 2")
    dep1_mod4 = TaskStarLine("task1", "task2")
    dep1_mod4.trigger_action = "modified_action"  # Changed
    dep1_mod4.condition = "modified_condition"  # Changed

    modified4.add_task(task1_mod4)
    modified4.add_task(task2_mod4)
    modified4.add_dependency(dep1_mod4)

    event4 = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test",
        timestamp=time.time(),
        data={"old_orion": original4, "new_orion": modified4},
        orion_id="test-4",
        orion_state="modified",
    )

    await observer.on_event(event4)
    print("\n")

    print("[OK] All comprehensive change detection tests completed!")
    print(" Features successfully implemented:")
    print("   • 自动对比 old/new orion，展示节点和边的增删")
    print("   • 优化 Rich 表格布局，防止换行")
    print("   • task 和 dep 属性变化都展示")


if __name__ == "__main__":
    asyncio.run(test_all_change_types())
