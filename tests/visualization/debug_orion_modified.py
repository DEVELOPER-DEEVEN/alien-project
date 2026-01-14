#!/usr/bin/env python3
"""
Debug script for orion modification event handling.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath("."))

from network.orion import TaskOrion, TaskStar, TaskStarLine
from network.core.events import OrionEvent, EventType
from network.session.observers import DAGVisualizationObserver
from rich.console import Console


async def test_orion_modified_handling():
    """Test orion modified event handling with debug output."""

    console = Console()
    console.print(
        "[bold blue] Testing Orion Modified Event Handling[/bold blue]\n"
    )

    # Initialize observer with explicit console
    observer = DAGVisualizationObserver(enable_visualization=True, console=console)

    # Create old orion
    old_orion = TaskOrion("test", "Test Orion")
    task1 = TaskStar("task1", "Task 1", "First task")
    old_orion.add_task(task1)

    # Create new orion with modifications
    new_orion = TaskOrion("test", "Test Orion")
    new_orion.add_task(task1)
    task2 = TaskStar("task2", "Task 2", "Second task")
    new_orion.add_task(task2)

    # Add dependency
    dep = TaskStarLine(
        from_task_id="task1",
        to_task_id="task2",
        condition_description="Task1 must complete before Task2",
    )
    new_orion.add_dependency(dep)

    console.print(f"Old orion: {old_orion.task_count} tasks")
    console.print(f"New orion: {new_orion.task_count} tasks")

    # Create event
    event = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test_system",
        timestamp=datetime.now().timestamp(),
        data={
            "old_orion": old_orion,
            "new_orion": new_orion,
        },
        orion_id="test",
        orion_state="modified",
    )

    console.print("\n[yellow]Calling observer.on_event() with debug info...[/yellow]")

    # Add some debug prints to the observer temporarily
    original_handle = observer._handle_orion_modified

    async def debug_handle_orion_modified(event, orion):
        console.print(f"[cyan]DEBUG: _handle_orion_modified called[/cyan]")
        console.print(
            f"[cyan]DEBUG: event.data = {event.data.keys() if event.data else 'None'}[/cyan]"
        )
        console.print(f"[cyan]DEBUG: orion = {orion}[/cyan]")
        console.print(
            f"[cyan]DEBUG: observer._visualizer = {observer._visualizer}[/cyan]"
        )

        result = await original_handle(event, orion)
        console.print(f"[cyan]DEBUG: _handle_orion_modified finished[/cyan]")
        return result

    observer._handle_orion_modified = debug_handle_orion_modified

    await observer.on_event(event)

    console.print("\n[green][OK] Event handling test completed[/green]")


if __name__ == "__main__":
    asyncio.run(test_orion_modified_handling())
