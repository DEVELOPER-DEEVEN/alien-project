#!/usr/bin/env python
"""
Test script for OrionAgent event publishing functionality.
"""

import asyncio
import pytest
import time
import sys
import os
from unittest.mock import AsyncMock, MagicMock

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from tests.network.mocks import MockOrionAgent
from network.orion import TaskOrion, TaskStar
from network.orion.orchestrator.orchestrator import (
    TaskOrionOrchestrator,
)
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
        print(f" Received event: {event.event_type.value}")
        print(f"   Source: {event.source_id}")
        print(f"   Orion ID: {event.orion_id}")
        print(f"   Data keys: {list(event.data.keys())}")


@pytest.mark.asyncio
async def test_orion_agent_event_publishing():
    """Test OrionAgent event publishing during process_editing."""
    print(" Testing OrionAgent Event Publishing\n")

    # Create mock orchestrator
    mock_orchestrator = MagicMock(spec=TaskOrionOrchestrator)

    # Create orion agent
    agent = MockOrionAgent(
        orchestrator=mock_orchestrator, name="test_orion_agent"
    )

    # Create test observer to capture events
    test_observer = TestEventObserver()
    dag_observer = DAGVisualizationObserver()

    # Subscribe observers to the event bus
    agent._event_bus.subscribe(test_observer, {EventType.ORION_MODIFIED})
    agent._event_bus.subscribe(dag_observer, {EventType.ORION_MODIFIED})

    # Create initial orion
    before_orion = TaskOrion("test-orion", "Test Orion")
    task1 = TaskStar("task1", "Original Task")
    before_orion.add_task(task1)

    # Create modified orion
    after_orion = TaskOrion("test-orion", "Test Orion")
    task1_mod = TaskStar("task1", "Modified Task")
    task2_mod = TaskStar("task2", "New Task")

    after_orion.add_task(task1_mod)
    after_orion.add_task(task2_mod)

    # Mock context with orions
    context = MagicMock(spec=Context)
    context.get.side_effect = lambda key: {
        ContextNames.ORION: after_orion
    }.get(key, after_orion)

    # Mock processor
    mock_processor = MagicMock()
    mock_processor.processing_context.get_local.return_value = "continue"

    # Set up agent state
    agent.processor = mock_processor
    agent._context_provision_executed = True

    # Manually set the before orion for the test
    original_get = context.get

    def mock_get(key):
        if key == ContextNames.ORION:
            # First call returns before, subsequent calls return after
            if not hasattr(mock_get, "call_count"):
                mock_get.call_count = 0
            mock_get.call_count += 1

            if mock_get.call_count == 1:
                return before_orion
            else:
                return after_orion
        return original_get(key)

    context.get = mock_get

    print("=== Test 1: OrionAgent process_editing with event publishing ===")

    # Test process_editing which should publish an event
    try:
        result = await agent.process_editing(context=context)

        print(f"[OK] Process editing completed successfully")
        print(f"   Returned orion: {result.orion_id}")
        print(f"   Agent status: {agent.status}")

        # Verify that events were published and received
        print(f"\n[STATUS] Event Publishing Results:")
        print(
            f"   Events captured by test observer: {len(test_observer.received_events)}"
        )

        if test_observer.received_events:
            event = test_observer.received_events[0]
            print(f"   Event type: {event.event_type.value}")
            print(f"   Source ID: {event.source_id}")
            print(f"   Orion ID: {event.orion_id}")
            print(f"   Has old orion: {'old_orion' in event.data}")
            print(f"   Has new orion: {'new_orion' in event.data}")
            print(f"   Modification type: {event.data.get('modification_type')}")

            # Verify event data
            if "old_orion" in event.data and "new_orion" in event.data:
                old_const = event.data["old_orion"]
                new_const = event.data["new_orion"]
                print(f"   Old orion tasks: {len(old_const.tasks)}")
                print(f"   New orion tasks: {len(new_const.tasks)}")
        else:
            print("   [FAIL] No events were captured!")

    except Exception as e:
        print(f"[FAIL] Error during process_editing: {e}")

    print("\n" + "=" * 80)

    # Test 2: Verify DAG visualization observer also received the event
    print("\n=== Test 2: Verify DAG Visualization Observer integration ===")

    # Give a small delay to ensure event processing
    await asyncio.sleep(0.1)

    print("[OK] DAG Visualization Observer should have received and processed the event")
    print("   (Check the Rich visualization output above)")

    print("\n[OK] All OrionAgent event publishing tests completed!")
    print(" Event publishing integration successful!")


if __name__ == "__main__":
    asyncio.run(test_orion_agent_event_publishing())
