#!/usr/bin/env python3
"""
Test script for orion modification with automatic comparison.
"""

import asyncio
import pytest
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath("."))

from network.orion import TaskOrion, TaskStar, TaskStarLine
from network.core.events import OrionEvent, EventType
from network.session.observers import DAGVisualizationObserver
from rich.console import Console


@pytest.mark.asyncio
async def test_orion_comparison():
    """Test orion modification with automatic comparison."""

    console = Console()
    console.print(
        "[bold blue]🧪 Testing Orion Modification Comparison[/bold blue]\n"
    )

    # Initialize observer
    observer = DAGVisualizationObserver(enable_visualization=True, console=console)

    # Create original orion
    console.print("[cyan]Creating original orion...[/cyan]")
    old_orion = TaskOrion("test-orion", "Test Orion")

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

    old_orion.add_task(task1)
    old_orion.add_task(task2)

    # Create dependency object
    from network.orion import TaskStarLine

    dep1 = TaskStarLine(
        from_task_id=task1.task_id,
        to_task_id=task2.task_id,
        condition_description="task1 must complete before task2",
    )
    old_orion.add_dependency(dep1)

    console.print(
        f"Original orion: {old_orion.task_count} tasks, {len(old_orion.dependencies)} dependencies\n"
    )

    # Create modified orion
    console.print("[cyan]Creating modified orion...[/cyan]")
    new_orion = TaskOrion("test-orion", "Test Orion")

    # Copy existing tasks
    new_orion.add_task(task1)
    new_orion.add_task(task2)
    new_orion.add_dependency(dep1)

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

    new_orion.add_task(task3)
    new_orion.add_task(task4)

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
    new_orion.add_dependency(dep2)
    new_orion.add_dependency(dep3)

    # Modify existing task (simulated by changing description)
    task1.description = "Modified task 1 description"

    console.print(
        f"Modified orion: {new_orion.task_count} tasks, {len(new_orion.dependencies)} dependencies\n"
    )

    # Test 1: Orion modification with automatic comparison
    console.print(
        "[yellow]Test 1: Orion modification with old/new comparison[/yellow]"
    )

    event = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test_system",
        timestamp=datetime.now().timestamp(),
        data={
            "old_orion": old_orion,
            "new_orion": new_orion,
        },
        orion_id="test-orion",
        orion_state="modified",
    )

    await observer.on_event(event)

    console.print("\n" + "=" * 80 + "\n")

    # Test 2: New orion (no old orion for comparison)
    console.print(
        "[yellow]Test 2: New orion creation (no old orion)[/yellow]"
    )

    brand_new_orion = TaskOrion("brand-new", "Brand New Orion")
    brand_new_orion.add_task(
        TaskStar("new_task", "New Task", "A completely new task")
    )

    event2 = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test_system",
        timestamp=datetime.now().timestamp(),
        data={"new_orion": brand_new_orion},
        orion_id="brand-new",
        orion_state="created",
    )

    await observer.on_event(event2)

    console.print("\n" + "=" * 80 + "\n")

    # Test 3: Task removal scenario
    console.print("[yellow]Test 3: Task removal scenario[/yellow]")

    # Create orion with tasks removed
    removed_orion = TaskOrion(
        "test-orion", "Test Orion"
    )
    removed_orion.add_task(task1)  # Only keep task1, remove task2

    event3 = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test_system",
        timestamp=datetime.now().timestamp(),
        data={
            "old_orion": old_orion,
            "new_orion": removed_orion,
        },
        orion_id="test-orion",
        orion_state="modified",
    )

    await observer.on_event(event3)

    console.print("\n[green]✅ All orion comparison tests completed![/green]")


if __name__ == "__main__":
    asyncio.run(test_orion_comparison())
