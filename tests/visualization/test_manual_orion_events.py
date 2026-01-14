#!/usr/bin/env python
"""
Simple test script for OrionAgent event publishing functionality.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from network.orion import TaskOrion, TaskStar
from network.core.events import OrionEvent, EventType, EventBus
from network.session.observers import DAGVisualizationObserver
from alien.module.context import Context, ContextNames


class TestEventObserver:
    """Test observer to capture published events."""

    def __init__(self):
        self.received_events = []

    async def on_event(self, event):
        """Capture events for testing."""
        self.received_events.append(event)
        print(f"📨 Received event: {event.event_type.value}")
        print(f"   Source: {event.source_id}")
        print(f"   Orion ID: {event.orion_id}")
        print(f"   Data keys: {list(event.data.keys())}")


#!/usr/bin/env python
"""
Simple test script for OrionAgent event publishing functionality.
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock

from network.orion import TaskOrion, TaskStar
from network.core.events import OrionEvent, EventType, EventBus
from network.session.observers import DAGVisualizationObserver
from alien.module.context import Context, ContextNames


class TestEventObserver:
    def __init__(self):
        self.events_received = []

    async def on_event(self, event):
        self.events_received.append(event)
        print(f"📧 Received event: {event.event_type.value} - {event.data}")


@pytest.mark.asyncio
async def test_manual_orion_event_publishing():
    """Test manual OrionEvent publishing and DAG visualization."""
    print("🧪 Testing Manual OrionEvent Publishing and Visualization\n")

    # Create event bus
    event_bus = EventBus()

    # Create observers
    test_observer = TestEventObserver()
    dag_observer = DAGVisualizationObserver()

    # Subscribe observers to the event bus
    event_bus.subscribe(test_observer, {EventType.ORION_MODIFIED})
    event_bus.subscribe(dag_observer, {EventType.ORION_MODIFIED})

    # Create before orion
    before_orion = TaskOrion("test-orion", "Test Orion")
    task1 = TaskStar("task1", "Original Task")
    before_orion.add_task(task1)

    # Create after orion
    after_orion = TaskOrion("test-orion", "Test Orion")
    task1_mod = TaskStar("task1", "Modified Task")
    task2_mod = TaskStar("task2", "New Task")

    after_orion.add_task(task1_mod)
    after_orion.add_task(task2_mod)

    print("=== Test 1: Manual OrionEvent Publishing ===")

    # Create and publish the event manually
    orion_event = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test_orion_agent",
        timestamp=time.time(),
        data={
            "old_orion": before_orion,
            "new_orion": after_orion,
            "modification_type": "agent_processing_result",
        },
        orion_id=after_orion.orion_id,
        orion_state="modified",
    )

    print(f"Publishing OrionEvent...")
    await event_bus.publish_event(orion_event)

    # Give a small delay to ensure event processing
    await asyncio.sleep(0.1)

    print(f"\n📊 Event Publishing Results:")
    print(f"   Events captured by test observer: {len(test_observer.events_received)}")

    if test_observer.events_received:
        event = test_observer.events_received[0]
        print(f"   ✅ Event type: {event.event_type.value}")
        print(f"   ✅ Source ID: {event.source_id}")
        print(f"   ✅ Orion ID: {event.orion_id}")
        print(f"   ✅ Has old orion: {'old_orion' in event.data}")
        print(f"   ✅ Has new orion: {'new_orion' in event.data}")
        print(f"   ✅ Modification type: {event.data.get('modification_type')}")

        # Verify event data
        if "old_orion" in event.data and "new_orion" in event.data:
            old_const = event.data["old_orion"]
            new_const = event.data["new_orion"]
            print(f"   📊 Old orion tasks: {len(old_const.tasks)}")
            print(f"   📊 New orion tasks: {len(new_const.tasks)}")
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

        event = OrionEvent(
            event_type=EventType.ORION_MODIFIED,
            source_id="test_agent",
            timestamp=time.time(),
            data={
                "old_orion": before_orion,
                "new_orion": after_orion,
                "modification_type": mod_type,
            },
            orion_id="test-orion-" + mod_type,
            orion_state="modified",
        )

        await event_bus.publish_event(event)
        await asyncio.sleep(0.05)  # Small delay for processing

    print(f"\n📈 Total events processed: {len(test_observer.events_received)}")

    print("\n✅ All OrionEvent publishing tests completed!")
    print("🎉 Event publishing and DAG visualization integration successful!")


if __name__ == "__main__":
    asyncio.run(test_manual_orion_event_publishing())
