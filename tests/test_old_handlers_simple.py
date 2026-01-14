#!/usr/bin/env python3

"""
简单测试验证旧的handlers都能产生输出
"""

import sys
import os
import asyncio
import time
from io import StringIO
from rich.console import Console

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from network.session.observers.dag_visualization_observer import (
    DAGVisualizationObserver,
)
from network.orion import (
    TaskOrion,
    TaskStar,
    TaskStarLine,
    TaskPriority,
)
from network.orion.enums import (
    TaskStatus,
    OrionState,
    DependencyType,
)
from network.core.events import Event, EventType, TaskEvent, OrionEvent


def create_test_orion():
    """Create a sample orion for testing."""
    orion = TaskOrion(name="Test Pipeline")

    # Add tasks
    data_task = TaskStar(
        task_id="data_001",
        name="Data Collection",
        description="Collect data",
        priority=TaskPriority.HIGH,
    )
    data_task.start_execution()
    data_task.complete_with_success({"records": 1000})
    orion.add_task(data_task)

    process_task = TaskStar(
        task_id="process_001",
        name="Data Processing",
        description="Process data",
        priority=TaskPriority.MEDIUM,
    )
    process_task.start_execution()
    orion.add_task(process_task)

    # Add dependency
    dep1 = TaskStarLine("data_001", "process_001", DependencyType.SUCCESS_ONLY)
    orion.add_dependency(dep1)

    return orion


async def test_all_event_types():
    """测试观察者是否对所有事件类型都产生输出"""
    print("🔍 测试所有事件类型的输出")
    print("=" * 60)

    # Create observer with visible console output
    console = Console()
    observer = DAGVisualizationObserver(console=console)

    orion = create_test_orion()
    observer.register_orion(orion.orion_id, orion)

    event_types_to_test = [
        EventType.ORION_STARTED,
        EventType.ORION_MODIFIED,
        EventType.ORION_COMPLETED,
        EventType.ORION_FAILED,
        EventType.TASK_STARTED,
        EventType.TASK_COMPLETED,
        EventType.TASK_FAILED,
    ]

    for event_type in event_types_to_test:
        print(f"\n📤 测试 {event_type.name}:")
        print("-" * 40)

        try:
            if "ORION" in event_type.name:
                # Orion event
                event = OrionEvent(
                    event_type=event_type,
                    source_id="test",
                    timestamp=time.time(),
                    data={
                        "orion": orion,
                        "orion_id": orion.orion_id,
                        "message": f"Test {event_type.name}",
                    },
                    orion_id=orion.orion_id,
                    orion_state=(
                        "executing"
                        if event_type != EventType.ORION_COMPLETED
                        else "completed"
                    ),
                )

                if event_type == EventType.ORION_MODIFIED:
                    event.data["changes"] = {
                        "modification_type": "tasks_added",
                        "added_tasks": ["new_task"],
                        "added_dependencies": [],
                    }
                    event.new_ready_tasks = ["new_task"]

            else:
                # Task event
                event = TaskEvent(
                    event_type=event_type,
                    source_id="test",
                    timestamp=time.time(),
                    data={"orion_id": orion.orion_id},
                    task_id="process_001",
                    status=(
                        "running"
                        if event_type == EventType.TASK_STARTED
                        else "completed"
                    ),
                )

                if event_type == EventType.TASK_COMPLETED:
                    event.result = {"output": "Success!"}
                    event.data["execution_time"] = 2.5
                elif event_type == EventType.TASK_FAILED:
                    event.data["error"] = "Test error message"

            # Test the event
            await observer.on_event(event)
            print("✅ 输出正常")

        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(test_all_event_types())
