#!/usr/bin/env python3
"""
Test script specifically for individual event visualization.
"""

import asyncio
import time
from network.orion.task_orion import TaskOrion
from network.orion.task_star import TaskStar
from network.core.events import (
    get_event_bus,
    EventType,
    TaskEvent,
    OrionEvent,
)
from network.session.observers import DAGVisualizationObserver
from network.orion.enums import TaskStatus


#!/usr/bin/env python3
"""
Test script specifically for individual event visualization.
"""

import asyncio
import time
import pytest
from network.orion.task_orion import TaskOrion
from network.orion.task_star import TaskStar
from network.core.events import (
    get_event_bus,
    EventType,
    TaskEvent,
    OrionEvent,
)
from network.session.observers import DAGVisualizationObserver


@pytest.mark.asyncio
async def test_individual_events():
    """Test individual event visualizations."""
    print(" Testing Individual Event Visualizations...")

    # Create event bus and visualization observer
    event_bus = get_event_bus()
    viz_observer = DAGVisualizationObserver(enable_visualization=True)

    # Subscribe to all event types
    event_bus.subscribe(
        observer=viz_observer,
        event_types={
            EventType.ORION_STARTED,
            EventType.ORION_COMPLETED,
            EventType.ORION_MODIFIED,
            EventType.TASK_STARTED,
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
        },
    )

    # Create a test orion
    orion = TaskOrion("individual_test")
    task = TaskStar(
        task_id="test_task",
        name="Test Task",
        description="A sample task for testing visualization",
        target_device_id="device_1",
        task_data={"command": "test_command"},
        tips=["This is a test tip", "Another helpful hint"],
    )
    orion.add_task(task)

    # Store orion in viz observer for event handling
    viz_observer._orions[orion.orion_id] = orion

    print("\n[START] Testing TASK_STARTED event...")
    task_started_event = TaskEvent(
        event_type=EventType.TASK_STARTED,
        source_id="test_script",
        timestamp=time.time(),
        data={"orion_id": orion.orion_id},
        task_id="test_task",
        status=TaskStatus.RUNNING.value,
    )
    await event_bus.publish_event(task_started_event)
    await asyncio.sleep(1)

    print("\n[OK] Testing TASK_COMPLETED event...")
    task_completed_event = TaskEvent(
        event_type=EventType.TASK_COMPLETED,
        source_id="test_script",
        timestamp=time.time(),
        data={
            "orion_id": orion.orion_id,
            "newly_ready_tasks": ["next_task_1", "next_task_2"],
        },
        task_id="test_task",
        status=TaskStatus.COMPLETED.value,
        result={"output": "Task completed successfully", "score": 95.5},
    )
    await event_bus.publish_event(task_completed_event)
    await asyncio.sleep(1)

    print("\n[FAIL] Testing TASK_FAILED event...")
    task_failed_event = TaskEvent(
        event_type=EventType.TASK_FAILED,
        source_id="test_script",
        timestamp=time.time(),
        data={
            "orion_id": orion.orion_id,
            "newly_ready_tasks": [],
        },
        task_id="test_task",
        status=TaskStatus.FAILED.value,
        error=Exception("Sample error: Connection timeout occurred"),
    )
    await event_bus.publish_event(task_failed_event)
    await asyncio.sleep(1)

    print("\n[CONTINUE] Testing ORION_MODIFIED event...")
    modification_event = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test_script",
        timestamp=time.time(),
        data={
            "orion": orion,
            "modification_type": "task_properties_updated",
            "added_tasks": [],
            "removed_tasks": [],
            "added_dependencies": [],
            "removed_dependencies": [],
            "modified_tasks": ["test_task"],
        },
        orion_id=orion.orion_id,
        orion_state="modified",
    )
    await event_bus.publish_event(modification_event)
    await asyncio.sleep(1)

    print("\n Individual event visualization tests completed!")


if __name__ == "__main__":
    asyncio.run(test_individual_events())
