#!/usr/bin/env python
"""
Test script for dependency property change detection and visualization.
"""

import asyncio
import pytest
from cluster.network import Tasknetwork, TaskStar, TaskStarLine
from cluster.session.observers import DAGVisualizationObserver
from cluster.core.events import networkEvent, EventType


@pytest.mark.asyncio
async def test_dependency_property_changes():
    """Test dependency property change detection."""
    print("🧪 Testing Dependency Property Change Detection\n")

    # Create observer (no context needed for this test)
    observer = DAGVisualizationObserver()

    # Create original network
    print("Creating original network...")
    original_network = Tasknetwork(
        "test-network", "Test network"
    )

    task1 = TaskStar("task1", "First Task")
    task2 = TaskStar("task2", "Second Task")

    # Original dependency with specific properties
    dep1 = TaskStarLine("task1", "task2")
    dep1.trigger_action = "original_action"
    dep1.trigger_actor = "original_actor"
    dep1.condition = "original_condition"
    dep1.keyword = "original_keyword"

    original_network.add_task(task1)
    original_network.add_task(task2)
    original_network.add_dependency(dep1)

    print(
        f"Original network: {len(original_network.tasks)} tasks, {len(original_network.dependencies)} dependencies"
    )

    # Create modified network with changed dependency properties
    print("\nCreating modified network with changed dependency properties...")
    modified_network = Tasknetwork(
        "test-network", "Test network"
    )

    task1_mod = TaskStar("task1", "First Task")
    task2_mod = TaskStar("task2", "Second Task")

    # Modified dependency with different properties
    dep1_mod = TaskStarLine("task1", "task2")
    dep1_mod.trigger_action = "modified_action"  # Changed
    dep1_mod.trigger_actor = "original_actor"  # Same
    dep1_mod.condition = "modified_condition"  # Changed
    dep1_mod.keyword = "original_keyword"  # Same

    modified_network.add_task(task1_mod)
    modified_network.add_task(task2_mod)
    modified_network.add_dependency(dep1_mod)

    print(
        f"Modified network: {len(modified_network.tasks)} tasks, {len(modified_network.dependencies)} dependencies"
    )

    # Test dependency property change detection
    print("\nTest: Dependency property modification detection")

    import time

    event = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test-source",
        timestamp=time.time(),
        data={
            "old_network": original_network,
            "new_network": modified_network,
            "modification_type": "dependency_properties_updated",
        },
        network_id="test-network",
        network_state="modified",
    )

    await observer.on_event(event)

    print("=" * 80)

    # Test 2: Multiple property changes
    print("\nTest 2: Multiple dependency property changes")

    # Create another modified network with more changes
    multi_mod_network = Tasknetwork(
        "test-network", "Test network"
    )

    task1_multi = TaskStar("task1", "First Task")
    task2_multi = TaskStar("task2", "Second Task")

    # More extensively modified dependency
    dep1_multi = TaskStarLine("task1", "task2")
    dep1_multi.trigger_action = "completely_new_action"  # Changed
    dep1_multi.trigger_actor = "completely_new_actor"  # Changed
    dep1_multi.condition = "completely_new_condition"  # Changed
    dep1_multi.keyword = "completely_new_keyword"  # Changed

    multi_mod_network.add_task(task1_multi)
    multi_mod_network.add_task(task2_multi)
    multi_mod_network.add_dependency(dep1_multi)

    event2 = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test-source",
        timestamp=time.time(),
        data={
            "old_network": original_network,
            "new_network": multi_mod_network,
            "modification_type": "dependency_properties_updated",
        },
        network_id="test-network",
        network_state="modified",
    )

    await observer.on_event(event2)

    print("✅ All dependency property change tests completed!")


if __name__ == "__main__":
    asyncio.run(test_dependency_property_changes())
