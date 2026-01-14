#!/usr/bin/env python
"""
Test script for dependency property change detection and visualization.
"""

import asyncio
import pytest
from network.orion import TaskOrion, TaskStar, TaskStarLine
from network.session.observers import DAGVisualizationObserver
from network.core.events import OrionEvent, EventType


@pytest.mark.asyncio
async def test_dependency_property_changes():
    """Test dependency property change detection."""
    print(" Testing Dependency Property Change Detection\n")

    # Create observer (no context needed for this test)
    observer = DAGVisualizationObserver()

    # Create original orion
    print("Creating original orion...")
    original_orion = TaskOrion(
        "test-orion", "Test Orion"
    )

    task1 = TaskStar("task1", "First Task")
    task2 = TaskStar("task2", "Second Task")

    # Original dependency with specific properties
    dep1 = TaskStarLine("task1", "task2")
    dep1.trigger_action = "original_action"
    dep1.trigger_actor = "original_actor"
    dep1.condition = "original_condition"
    dep1.keyword = "original_keyword"

    original_orion.add_task(task1)
    original_orion.add_task(task2)
    original_orion.add_dependency(dep1)

    print(
        f"Original orion: {len(original_orion.tasks)} tasks, {len(original_orion.dependencies)} dependencies"
    )

    # Create modified orion with changed dependency properties
    print("\nCreating modified orion with changed dependency properties...")
    modified_orion = TaskOrion(
        "test-orion", "Test Orion"
    )

    task1_mod = TaskStar("task1", "First Task")
    task2_mod = TaskStar("task2", "Second Task")

    # Modified dependency with different properties
    dep1_mod = TaskStarLine("task1", "task2")
    dep1_mod.trigger_action = "modified_action"  # Changed
    dep1_mod.trigger_actor = "original_actor"  # Same
    dep1_mod.condition = "modified_condition"  # Changed
    dep1_mod.keyword = "original_keyword"  # Same

    modified_orion.add_task(task1_mod)
    modified_orion.add_task(task2_mod)
    modified_orion.add_dependency(dep1_mod)

    print(
        f"Modified orion: {len(modified_orion.tasks)} tasks, {len(modified_orion.dependencies)} dependencies"
    )

    # Test dependency property change detection
    print("\nTest: Dependency property modification detection")

    import time

    event = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test-source",
        timestamp=time.time(),
        data={
            "old_orion": original_orion,
            "new_orion": modified_orion,
            "modification_type": "dependency_properties_updated",
        },
        orion_id="test-orion",
        orion_state="modified",
    )

    await observer.on_event(event)

    print("=" * 80)

    # Test 2: Multiple property changes
    print("\nTest 2: Multiple dependency property changes")

    # Create another modified orion with more changes
    multi_mod_orion = TaskOrion(
        "test-orion", "Test Orion"
    )

    task1_multi = TaskStar("task1", "First Task")
    task2_multi = TaskStar("task2", "Second Task")

    # More extensively modified dependency
    dep1_multi = TaskStarLine("task1", "task2")
    dep1_multi.trigger_action = "completely_new_action"  # Changed
    dep1_multi.trigger_actor = "completely_new_actor"  # Changed
    dep1_multi.condition = "completely_new_condition"  # Changed
    dep1_multi.keyword = "completely_new_keyword"  # Changed

    multi_mod_orion.add_task(task1_multi)
    multi_mod_orion.add_task(task2_multi)
    multi_mod_orion.add_dependency(dep1_multi)

    event2 = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test-source",
        timestamp=time.time(),
        data={
            "old_orion": original_orion,
            "new_orion": multi_mod_orion,
            "modification_type": "dependency_properties_updated",
        },
        orion_id="test-orion",
        orion_state="modified",
    )

    await observer.on_event(event2)

    print("[OK] All dependency property change tests completed!")


if __name__ == "__main__":
    asyncio.run(test_dependency_property_changes())
