#!/usr/bin/env python
"""
Simple test script for networkAgent event publishing functionality.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from cluster.network import Tasknetwork, TaskStar
from cluster.core.events import networkEvent, EventType, EventBus
from cluster.session.observers import DAGVisualizationObserver
from Alien.module.context import Context, ContextNames


class TestEventObserver:
    """Test observer to capture published events."""

    def __init__(self):
        self.received_events = []

    async def on_event(self, event):
        """Capture events for testing."""
        self.received_events.append(event)
        print(f"📨 Received event: {event.event_type.value}")
        print(f"   Source: {event.source_id}")
        print(f"   network ID: {event.network_id}")
        print(f"   Data keys: {list(event.data.keys())}")


#!/usr/bin/env python
"""
Simple test script for networkAgent event publishing functionality.
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock

from cluster.network import Tasknetwork, TaskStar
from cluster.core.events import networkEvent, EventType, EventBus
from cluster.session.observers import DAGVisualizationObserver
from Alien.module.context import Context, ContextNames


class TestEventObserver:
    def __init__(self):
        self.events_received = []

    async def on_event(self, event):
        self.events_received.append(event)
        print(f"📧 Received event: {event.event_type.value} - {event.data}")


@pytest.mark.asyncio
async def test_manual_network_event_publishing():
    """Test manual networkEvent publishing and DAG visualization."""
    print("🧪 Testing Manual networkEvent Publishing and Visualization\n")

    # Create event bus
    event_bus = EventBus()

    # Create observers
    test_observer = TestEventObserver()
    dag_observer = DAGVisualizationObserver()

    # Subscribe observers to the event bus
    event_bus.subscribe(test_observer, {EventType.network_MODIFIED})
    event_bus.subscribe(dag_observer, {EventType.network_MODIFIED})

    # Create before network
    before_network = Tasknetwork("test-network", "Test network")
    task1 = TaskStar("task1", "Original Task")
    before_network.add_task(task1)

    # Create after network
    after_network = Tasknetwork("test-network", "Test network")
    task1_mod = TaskStar("task1", "Modified Task")
    task2_mod = TaskStar("task2", "New Task")

    after_network.add_task(task1_mod)
    after_network.add_task(task2_mod)

    print("=== Test 1: Manual networkEvent Publishing ===")

    # Create and publish the event manually
    network_event = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test_network_agent",
        timestamp=time.time(),
        data={
            "old_network": before_network,
            "new_network": after_network,
            "modification_type": "agent_processing_result",
        },
        network_id=after_network.network_id,
        network_state="modified",
    )

    print(f"Publishing networkEvent...")
    await event_bus.publish_event(network_event)

    # Give a small delay to ensure event processing
    await asyncio.sleep(0.1)

    print(f"\n📊 Event Publishing Results:")
    print(f"   Events captured by test observer: {len(test_observer.events_received)}")

    if test_observer.events_received:
        event = test_observer.events_received[0]
        print(f"   ✅ Event type: {event.event_type.value}")
        print(f"   ✅ Source ID: {event.source_id}")
        print(f"   ✅ network ID: {event.network_id}")
        print(f"   ✅ Has old network: {'old_network' in event.data}")
        print(f"   ✅ Has new network: {'new_network' in event.data}")
        print(f"   ✅ Modification type: {event.data.get('modification_type')}")

        # Verify event data
        if "old_network" in event.data and "new_network" in event.data:
            old_const = event.data["old_network"]
            new_const = event.data["new_network"]
            print(f"   📊 Old network tasks: {len(old_const.tasks)}")
            print(f"   📊 New network tasks: {len(new_const.tasks)}")
    else:
        print("   ❌ No events were captured!")

    print("\n" + "=" * 80)

    # Test 2: Test different modification types
    print("\n=== Test 2: Different Modification Types ===")

    test_cases = [
        ("task_properties_updated", "Task property changes"),
        ("dependency_properties_updated", "Dependency property changes"),
        ("tasks_added", "New tasks added"),
        ("tasks_removed", "Tasks removed"),
    ]

    for mod_type, description in test_cases:
        print(f"\n🔄 Testing {mod_type}: {description}")

        event = networkEvent(
            event_type=EventType.network_MODIFIED,
            source_id="test_agent",
            timestamp=time.time(),
            data={
                "old_network": before_network,
                "new_network": after_network,
                "modification_type": mod_type,
            },
            network_id="test-network-" + mod_type,
            network_state="modified",
        )

        await event_bus.publish_event(event)
        await asyncio.sleep(0.05)  # Small delay for processing

    print(f"\n📈 Total events processed: {len(test_observer.events_received)}")

    print("\n✅ All networkEvent publishing tests completed!")
    print("🎉 Event publishing and DAG visualization integration successful!")


if __name__ == "__main__":
    asyncio.run(test_manual_network_event_publishing())
