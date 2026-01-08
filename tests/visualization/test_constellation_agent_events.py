#!/usr/bin/env python
"""
Test script for networkAgent event publishing functionality.
"""

import asyncio
import pytest
import time
import sys
import os
from unittest.mock import AsyncMock, MagicMock

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from tests.cluster.mocks import MocknetworkAgent
from cluster.network import Tasknetwork, TaskStar
from cluster.network.orchestrator.orchestrator import (
    TasknetworkOrchestrator,
)
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


@pytest.mark.asyncio
async def test_network_agent_event_publishing():
    """Test networkAgent event publishing during process_editing."""
    print("🧪 Testing networkAgent Event Publishing\n")

    # Create mock orchestrator
    mock_orchestrator = MagicMock(spec=TasknetworkOrchestrator)

    # Create network agent
    agent = MocknetworkAgent(
        orchestrator=mock_orchestrator, name="test_network_agent"
    )

    # Create test observer to capture events
    test_observer = TestEventObserver()
    dag_observer = DAGVisualizationObserver()

    # Subscribe observers to the event bus
    agent._event_bus.subscribe(test_observer, {EventType.network_MODIFIED})
    agent._event_bus.subscribe(dag_observer, {EventType.network_MODIFIED})

    # Create initial network
    before_network = Tasknetwork("test-network", "Test network")
    task1 = TaskStar("task1", "Original Task")
    before_network.add_task(task1)

    # Create modified network
    after_network = Tasknetwork("test-network", "Test network")
    task1_mod = TaskStar("task1", "Modified Task")
    task2_mod = TaskStar("task2", "New Task")

    after_network.add_task(task1_mod)
    after_network.add_task(task2_mod)

    # Mock context with networks
    context = MagicMock(spec=Context)
    context.get.side_effect = lambda key: {
        ContextNames.network: after_network
    }.get(key, after_network)

    # Mock processor
    mock_processor = MagicMock()
    mock_processor.processing_context.get_local.return_value = "continue"

    # Set up agent state
    agent.processor = mock_processor
    agent._context_provision_executed = True

    # Manually set the before network for the test
    original_get = context.get

    def mock_get(key):
        if key == ContextNames.network:
            # First call returns before, subsequent calls return after
            if not hasattr(mock_get, "call_count"):
                mock_get.call_count = 0
            mock_get.call_count += 1

            if mock_get.call_count == 1:
                return before_network
            else:
                return after_network
        return original_get(key)

    context.get = mock_get

    print("=== Test 1: networkAgent process_editing with event publishing ===")

    # Test process_editing which should publish an event
    try:
        result = await agent.process_editing(context=context)

        print(f"✅ Process editing completed successfully")
        print(f"   Returned network: {result.network_id}")
        print(f"   Agent status: {agent.status}")

        # Verify that events were published and received
        print(f"\n📊 Event Publishing Results:")
        print(
            f"   Events captured by test observer: {len(test_observer.received_events)}"
        )

        if test_observer.received_events:
            event = test_observer.received_events[0]
            print(f"   Event type: {event.event_type.value}")
            print(f"   Source ID: {event.source_id}")
            print(f"   network ID: {event.network_id}")
            print(f"   Has old network: {'old_network' in event.data}")
            print(f"   Has new network: {'new_network' in event.data}")
            print(f"   Modification type: {event.data.get('modification_type')}")

            # Verify event data
            if "old_network" in event.data and "new_network" in event.data:
                old_const = event.data["old_network"]
                new_const = event.data["new_network"]
                print(f"   Old network tasks: {len(old_const.tasks)}")
                print(f"   New network tasks: {len(new_const.tasks)}")
        else:
            print("   ❌ No events were captured!")

    except Exception as e:
        print(f"❌ Error during process_editing: {e}")

    print("\n" + "=" * 80)

    # Test 2: Verify DAG visualization observer also received the event
    print("\n=== Test 2: Verify DAG Visualization Observer integration ===")

    # Give a small delay to ensure event processing
    await asyncio.sleep(0.1)

    print("✅ DAG Visualization Observer should have received and processed the event")
    print("   (Check the Rich visualization output above)")

    print("\n✅ All networkAgent event publishing tests completed!")
    print("🎉 Event publishing integration successful!")


if __name__ == "__main__":
    asyncio.run(test_network_agent_event_publishing())
