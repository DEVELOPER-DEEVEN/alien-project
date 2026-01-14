#!/usr/bin/env python3
"""
Test script to verify orion events are properly published.
"""

import asyncio
import logging
import pytest
from typing import List, Set

from network.orion.task_orion import TaskOrion
from network.orion.task_star import TaskStar
from network.orion.task_star_line import TaskStarLine
from network.orion.orchestrator.orchestrator import (
    TaskOrionOrchestrator,
)
from network.core.events import get_event_bus, Event, EventType, IEventObserver
from network.client.device_manager import OrionDeviceManager

# Configure logging
logging.basicConfig(level=logging.INFO)


class MockDevice:
    """Mock device for testing."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.is_busy = False

    async def execute_command(self, command: str) -> str:
        """Mock command execution."""
        await asyncio.sleep(0.1)  # Simulate work
        return f"Result from {self.device_id}: {command}"


class MockDeviceManager(OrionDeviceManager):
    """Mock device manager for testing."""

    def __init__(self):
        # Don't call super().__init__() to avoid complex initialization
        self.devices = {
            "device_1": MockDevice("device_1"),
            "device_2": MockDevice("device_2"),
        }

        # Create a mock device registry
        self.device_registry = type(
            "MockRegistry",
            (),
            {
                "get_all_devices": lambda: [
                    {
                        "device_id": "device_1",
                        "device_type": "mobile",
                        "status": "available",
                    },
                    {
                        "device_id": "device_2",
                        "device_type": "desktop",
                        "status": "available",
                    },
                ]
            },
        )()

    async def get_available_devices(self) -> List[dict]:
        """Get list of available devices."""
        return [
            {"device_id": "device_1", "device_type": "mobile", "status": "available"},
            {"device_id": "device_2", "device_type": "desktop", "status": "available"},
        ]

    async def execute_task(self, device_id: str, task_data: dict) -> dict:
        """Execute a task on the specified device."""
        device = self.devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        command = task_data.get("command", "default_command")
        result = await device.execute_command(command)

        return {"success": True, "result": result}


class EventCollector(IEventObserver):
    """Collect events for testing."""

    def __init__(self):
        self.events = []

    async def on_event(self, event: Event):
        """Event handler."""
        self.events.append(event)
        print(f"Event received: {event.event_type} - {event.data}")

    async def handle_event(self, event: Event):
        """Required method from IEventObserver interface."""
        await self.on_event(event)


@pytest.mark.asyncio
async def test_orion_events():
    """Test orion event publishing."""
    print(" Testing Orion Events...")

    # Create event collector
    event_collector = EventCollector()
    event_bus = get_event_bus()
    event_bus.subscribe(
        observer=event_collector,
        event_types={
            EventType.ORION_STARTED,
            EventType.ORION_COMPLETED,
        },
    )

    # Create mock device manager
    device_manager = MockDeviceManager()

    # Create orchestrator
    orchestrator = TaskOrionOrchestrator(
        device_manager=device_manager, enable_logging=True, event_bus=event_bus
    )

    # Create a simple orion
    orion = TaskOrion("test_orion")

    # Add tasks
    task1 = TaskStar(
        task_id="task_1",
        name="First Task",
        description="Execute first task",
        target_device_id="device_1",
        task_data={"command": "echo 'Task 1'"},
    )

    task2 = TaskStar(
        task_id="task_2",
        name="Second Task",
        description="Execute second task",
        target_device_id="device_2",
        task_data={"command": "echo 'Task 2'"},
    )

    orion.add_task(task1)
    orion.add_task(task2)

    # Create dependency: task_2 depends on task_1
    dependency = TaskStarLine(
        from_task_id="task_1",
        to_task_id="task_2",
        condition_description="Task 1 must complete first",
    )
    orion.add_dependency(dependency)

    print(f"[OK] Created orion with {len(orion.tasks)} tasks")

    # Execute orion with manual device assignments
    try:
        device_assignments = {"task_1": "device_1", "task_2": "device_2"}

        result = await orchestrator.orchestrate_orion(
            orion=orion,
            device_assignments=device_assignments,
            assignment_strategy="round_robin",
        )

        print(f"[OK] Orion execution completed: {result['status']}")
        print(f"[STATUS] Statistics: {result.get('statistics', {})}")

        # Check collected events
        print(f"\n[TASK] Collected Events ({len(event_collector.events)}):")
        for i, event in enumerate(event_collector.events, 1):
            print(f"  {i}. {event.event_type}")
            print(f"     Data: {event.data}")
            print(f"     Orion ID: {getattr(event, 'orion_id', 'N/A')}")

        # Verify we got the expected events
        event_types = [event.event_type for event in event_collector.events]
        expected_events = [
            EventType.ORION_STARTED,
            EventType.ORION_COMPLETED,
        ]

        missing_events = [e for e in expected_events if e not in event_types]
        if missing_events:
            print(f"[FAIL] Missing events: {missing_events}")
            return False
        else:
            print("[OK] All expected orion events were published!")
            return True

    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the test."""
    print("[START] Starting Orion Events Test...")
    success = await test_orion_events()

    if success:
        print("\n All tests passed!")
    else:
        print("\n Tests failed!")

    return success


if __name__ == "__main__":
    asyncio.run(main())
