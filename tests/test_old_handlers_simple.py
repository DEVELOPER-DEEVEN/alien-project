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

from cluster.session.observers.dag_visualization_observer import (
    DAGVisualizationObserver,
)
from cluster.network import (
    Tasknetwork,
    TaskStar,
    TaskStarLine,
    TaskPriority,
)
from cluster.network.enums import (
    TaskStatus,
    networkState,
    DependencyType,
)
from cluster.core.events import Event, EventType, TaskEvent, networkEvent


def create_test_network():
    """Create a sample network for testing."""
    network = Tasknetwork(name="Test Pipeline")

    # Add tasks
    data_task = TaskStar(
        task_id="data_001",
        name="Data Collection",
        description="Collect data",
        priority=TaskPriority.HIGH,
    )
    data_task.start_execution()
    data_task.complete_with_success({"records": 1000})
    network.add_task(data_task)

    process_task = TaskStar(
        task_id="process_001",
        name="Data Processing",
        description="Process data",
        priority=TaskPriority.MEDIUM,
    )
    process_task.start_execution()
    network.add_task(process_task)

    # Add dependency
    dep1 = TaskStarLine("data_001", "process_001", DependencyType.SUCCESS_ONLY)
    network.add_dependency(dep1)

    return network


async def test_all_event_types():
    """测试观察者是否对所有事件类型都产生输出"""
    print("🔍 测试所有事件类型的输出")
    print("=" * 60)

    # Create observer with visible console output
    console = Console()
    observer = DAGVisualizationObserver(console=console)

    network = create_test_network()
    observer.register_network(network.network_id, network)

    event_types_to_test = [
        EventType.network_STARTED,
        EventType.network_MODIFIED,
        EventType.network_COMPLETED,
        EventType.network_FAILED,
        EventType.TASK_STARTED,
        EventType.TASK_COMPLETED,
        EventType.TASK_FAILED,
    ]

    for event_type in event_types_to_test:
        print(f"\n📤 测试 {event_type.name}:")
        print("-" * 40)

        try:
            if "network" in event_type.name:
                # network event
                event = networkEvent(
                    event_type=event_type,
                    source_id="test",
                    timestamp=time.time(),
                    data={
                        "network": network,
                        "network_id": network.network_id,
                        "message": f"Test {event_type.name}",
                    },
                    network_id=network.network_id,
                    network_state=(
                        "executing"
                        if event_type != EventType.network_COMPLETED
                        else "completed"
                    ),
                )

                if event_type == EventType.network_MODIFIED:
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
                    data={"network_id": network.network_id},
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
