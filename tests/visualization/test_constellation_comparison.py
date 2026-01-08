#!/usr/bin/env python3
"""
Test script for network modification with automatic comparison.
"""

import asyncio
import pytest
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath("."))

from cluster.network import Tasknetwork, TaskStar, TaskStarLine
from cluster.core.events import networkEvent, EventType
from cluster.session.observers import DAGVisualizationObserver
from rich.console import Console


@pytest.mark.asyncio
async def test_network_comparison():
    """Test network modification with automatic comparison."""

    console = Console()
    console.print(
        "[bold blue]🧪 Testing network Modification Comparison[/bold blue]\n"
    )

    # Initialize observer
    observer = DAGVisualizationObserver(enable_visualization=True, console=console)

    # Create original network
    console.print("[cyan]Creating original network...[/cyan]")
    old_network = Tasknetwork("test-network", "Test network")

    # Add some tasks to original
    task1 = TaskStar(
        task_id="task1",
        name="First Task",
        description="Original task 1",
        target_device_id="device1",
    )
    task2 = TaskStar(
        task_id="task2",
        name="Second Task",
        description="Original task 2",
        target_device_id="device1",
    )

    old_network.add_task(task1)
    old_network.add_task(task2)

    # Create dependency object
    from cluster.network import TaskStarLine

    dep1 = TaskStarLine(
        from_task_id=task1.task_id,
        to_task_id=task2.task_id,
        condition_description="task1 must complete before task2",
    )
    old_network.add_dependency(dep1)

    console.print(
        f"Original network: {old_network.task_count} tasks, {len(old_network.dependencies)} dependencies\n"
    )

    # Create modified network
    console.print("[cyan]Creating modified network...[/cyan]")
    new_network = Tasknetwork("test-network", "Test network")

    # Copy existing tasks
    new_network.add_task(task1)
    new_network.add_task(task2)
    new_network.add_dependency(dep1)

    # Add new tasks
    task3 = TaskStar(
        task_id="task3",
        name="Third Task",
        description="Newly added task",
        target_device_id="device2",
    )
    task4 = TaskStar(
        task_id="task4",
        name="Fourth Task",
        description="Another new task",
        target_device_id="device2",
    )

    new_network.add_task(task3)
    new_network.add_task(task4)

    # Add new dependencies
    dep2 = TaskStarLine(
        from_task_id=task2.task_id,
        to_task_id=task3.task_id,
        condition_description="task2 enables task3",
    )
    dep3 = TaskStarLine(
        from_task_id=task3.task_id,
        to_task_id=task4.task_id,
        condition_description="task3 must complete before task4",
    )
    new_network.add_dependency(dep2)
    new_network.add_dependency(dep3)

    # Modify existing task (simulated by changing description)
    task1.description = "Modified task 1 description"

    console.print(
        f"Modified network: {new_network.task_count} tasks, {len(new_network.dependencies)} dependencies\n"
    )

    # Test 1: network modification with automatic comparison
    console.print(
        "[yellow]Test 1: network modification with old/new comparison[/yellow]"
    )

    event = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test_system",
        timestamp=datetime.now().timestamp(),
        data={
            "old_network": old_network,
            "new_network": new_network,
        },
        network_id="test-network",
        network_state="modified",
    )

    await observer.on_event(event)

    console.print("\n" + "=" * 80 + "\n")

    # Test 2: New network (no old network for comparison)
    console.print(
        "[yellow]Test 2: New network creation (no old network)[/yellow]"
    )

    brand_new_network = Tasknetwork("brand-new", "Brand New network")
    brand_new_network.add_task(
        TaskStar("new_task", "New Task", "A completely new task")
    )

    event2 = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test_system",
        timestamp=datetime.now().timestamp(),
        data={"new_network": brand_new_network},
        network_id="brand-new",
        network_state="created",
    )

    await observer.on_event(event2)

    console.print("\n" + "=" * 80 + "\n")

    # Test 3: Task removal scenario
    console.print("[yellow]Test 3: Task removal scenario[/yellow]")

    # Create network with tasks removed
    removed_network = Tasknetwork(
        "test-network", "Test network"
    )
    removed_network.add_task(task1)  # Only keep task1, remove task2

    event3 = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test_system",
        timestamp=datetime.now().timestamp(),
        data={
            "old_network": old_network,
            "new_network": removed_network,
        },
        network_id="test-network",
        network_state="modified",
    )

    await observer.on_event(event3)

    console.print("\n[green]✅ All network comparison tests completed![/green]")


if __name__ == "__main__":
    asyncio.run(test_network_comparison())
