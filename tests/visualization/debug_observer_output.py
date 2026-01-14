#!/usr/bin/env python3
"""
Debug script to test orion comparison visualization output.
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


async def test_observer_output():
    """Test that the observer actually produces visible output."""

    console = Console()
    console.print("[bold blue]🔍 Testing Observer Visualization Output[/bold blue]\n")

    # Initialize observer with explicit console
    observer = DAGVisualizationObserver(enable_visualization=True, console=console)

    console.print("[cyan]Checking observer initialization...[/cyan]")
    console.print(f"Observer enabled: {observer.enable_visualization}")
    console.print(f"Observer visualizer: {observer._visualizer}")

    if observer._visualizer:
        console.print(f"Visualizer console: {observer._visualizer.console}")

        # Test direct visualizer call
        console.print("\n[yellow]Testing direct visualizer call...[/yellow]")

        # Create simple orion for testing
        test_orion = TaskOrion("test", "Test Orion")
        test_task = TaskStar("test_task", "Test Task", "A simple test task")
        test_orion.add_task(test_task)

        observer._visualizer.display_orion_overview(
            test_orion, "Direct Test"
        )

        console.print("\n[green]✅ Direct visualizer test completed[/green]")

        # Test through observer event
        console.print("\n[yellow]Testing observer event handling...[/yellow]")

        event = OrionEvent(
            event_type=EventType.ORION_MODIFIED,
            source_id="test_system",
            timestamp=datetime.now().timestamp(),
            data={"new_orion": test_orion},
            orion_id="test",
            orion_state="modified",
        )

        console.print("Calling observer.on_event()...")
        await observer.on_event(event)

        console.print("\n[green]✅ Observer event test completed[/green]")
    else:
        console.print("[red]❌ Visualizer not initialized[/red]")


if __name__ == "__main__":
    asyncio.run(test_observer_output())
