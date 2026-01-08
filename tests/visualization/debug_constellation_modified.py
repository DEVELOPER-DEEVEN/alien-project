#!/usr/bin/env python3
"""
Debug script for network modification event handling.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath("."))

from cluster.network import Tasknetwork, TaskStar, TaskStarLine
from cluster.core.events import networkEvent, EventType
from cluster.session.observers import DAGVisualizationObserver
from rich.console import Console


async def test_network_modified_handling():
    """Test network modified event handling with debug output."""

    console = Console()
    console.print(
        "[bold blue]🔍 Testing network Modified Event Handling[/bold blue]\n"
    )

    # Initialize observer with explicit console
    observer = DAGVisualizationObserver(enable_visualization=True, console=console)

    # Create old network
    old_network = Tasknetwork("test", "Test network")
    task1 = TaskStar("task1", "Task 1", "First task")
    old_network.add_task(task1)

    # Create new network with modifications
    new_network = Tasknetwork("test", "Test network")
    new_network.add_task(task1)
    task2 = TaskStar("task2", "Task 2", "Second task")
    new_network.add_task(task2)

    # Add dependency
    dep = TaskStarLine(
        from_task_id="task1",
        to_task_id="task2",
        condition_description="Task1 must complete before Task2",
    )
    new_network.add_dependency(dep)

    console.print(f"Old network: {old_network.task_count} tasks")
    console.print(f"New network: {new_network.task_count} tasks")

    # Create event
    event = networkEvent(
        event_type=EventType.network_MODIFIED,
        source_id="test_system",
        timestamp=datetime.now().timestamp(),
        data={
            "old_network": old_network,
            "new_network": new_network,
        },
        network_id="test",
        network_state="modified",
    )

    console.print("\n[yellow]Calling observer.on_event() with debug info...[/yellow]")

    # Add some debug prints to the observer temporarily
    original_handle = observer._handle_network_modified

    async def debug_handle_network_modified(event, network):
        console.print(f"[cyan]DEBUG: _handle_network_modified called[/cyan]")
        console.print(
            f"[cyan]DEBUG: event.data = {event.data.keys() if event.data else 'None'}[/cyan]"
        )
        console.print(f"[cyan]DEBUG: network = {network}[/cyan]")
        console.print(
            f"[cyan]DEBUG: observer._visualizer = {observer._visualizer}[/cyan]"
        )

        result = await original_handle(event, network)
        console.print(f"[cyan]DEBUG: _handle_network_modified finished[/cyan]")
        return result

    observer._handle_network_modified = debug_handle_network_modified

    await observer.on_event(event)

    console.print("\n[green]✅ Event handling test completed[/green]")


if __name__ == "__main__":
    asyncio.run(test_network_modified_handling())
