#!/usr/bin/env python3

"""
Debug test to check DAGVisualizationObserver output with old handlers.
"""

import sys
import os
import asyncio
import time
from io import StringIO
from rich.console import Console

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from network.session.observers.dag_visualization_observer import DAGVisualizationObserver
from network.orion import TaskOrion, TaskStar, TaskStarLine, TaskPriority
from network.orion.enums import TaskStatus, OrionState, DependencyType
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


async def test_observer_with_old_handlers():
    """Test the observer with old handlers and debug output."""
    print("🔍 Testing DAGVisualizationObserver with Old Handlers")
    print("=" * 60)

    # Create observer with string output capture
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    observer = DAGVisualizationObserver(console=console)

    # Check if handlers are properly initialized
    print(f"Observer initialized: {observer.enable_visualization}")
    print(f"Visualizer present: {observer._visualizer is not None}")
    print(f"Task handler present: {observer._task_handler is not None}")
    print(
        f"Orion handler present: {observer._orion_handler is not None}"
    )

    # Create test orion
    orion = create_test_orion()

    print(
        f"\n🌟 Test orion created with {len(orion.get_all_tasks())} tasks"
    )

    # Register orion first for all tests
    observer.register_orion(orion.orion_id, orion)

    # Test orion started event
    print("\n📤 Testing ORION_STARTED event...")
    started_event = OrionEvent(
        event_type=EventType.ORION_STARTED,
        source_id="test_source",
        timestamp=time.time(),
        data={
            "orion": orion,
            "orion_id": orion.orion_id,
            "message": "Pipeline execution started",
        },
        orion_id=orion.orion_id,
        orion_state="executing",
        new_ready_tasks=[],
    )

    await observer.on_event(started_event)
    output_text = output.getvalue()

    print(f"   Output length: {len(output_text)} characters")
    if output_text:
        print("   Sample output:")
        # Print first few lines
        lines = output_text.split("\n")
        for i, line in enumerate(lines[:5]):
            if line.strip():
                print(f"     {line}")
        if len(lines) > 5:
            print(f"     ... ({len(lines)-5} more lines)")
    else:
        print("   ❌ No output generated!")

    # Clear output buffer
    output.seek(0)
    output.truncate(0)

    # Test task event
    print("\n📤 Testing TASK_STARTED event...")
    task_event = TaskEvent(
        event_type=EventType.TASK_STARTED,
        source_id="test_source",
        timestamp=time.time(),
        data={
            "orion_id": orion.orion_id,
        },
        task_id="process_001",
        status="running",
    )

    await observer.on_event(task_event)
    output_text = output.getvalue()

    print(f"   Output length: {len(output_text)} characters")
    if output_text:
        print("   Sample output:")
        lines = output_text.split("\n")
        for i, line in enumerate(lines[:3]):
            if line.strip():
                print(f"     {line}")
    else:
        print("   ❌ No output generated!")

    # Clear output buffer
    output.seek(0)
    output.truncate(0)

    # Test orion modified event
    print("\n📤 Testing ORION_MODIFIED event...")

    # Add a new task to simulate modification
    new_task = TaskStar(
        task_id="report_001",
        name="Report Generation",
        description="Generate final report",
        priority=TaskPriority.LOW,
    )
    orion.add_task(new_task)

    modified_event = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test_source",
        timestamp=time.time(),
        data={
            "orion": orion,
            "orion_id": orion.orion_id,
            "changes": {
                "modification_type": "tasks_added",
                "added_tasks": ["report_001"],
                "added_dependencies": [],
            },
        },
        orion_id=orion.orion_id,
        orion_state="executing",
        new_ready_tasks=["report_001"],
    )

    await observer.on_event(modified_event)
    output_text = output.getvalue()

    print(f"   Output length: {len(output_text)} characters")
    if output_text:
        print("   Sample output:")
        lines = output_text.split("\n")
        for i, line in enumerate(lines[:5]):
            if line.strip():
                print(f"     {line}")
    else:
        print("   ❌ No output generated!")

    # Debug: Check handler methods
    print("\n🔍 Handler Debug Information:")
    if observer._task_handler:
        print(f"   Task handler type: {type(observer._task_handler)}")
        print(
            f"   Task handler methods: {[m for m in dir(observer._task_handler) if not m.startswith('_')]}"
        )

    if observer._orion_handler:
        print(f"   Orion handler type: {type(observer._orion_handler)}")
        print(
            f"   Orion handler methods: {[m for m in dir(observer._orion_handler) if not m.startswith('_')]}"
        )

    # Test direct handler calls
    print("\n🔧 Testing Direct Handler Calls:")
    if observer._task_handler and hasattr(observer._task_handler, "handle_task_event"):
        print("   Testing task handler directly...")
        output.seek(0)
        output.truncate(0)
        observer._task_handler.handle_task_event(task_event)
        direct_output = output.getvalue()
        print(f"   Direct task handler output: {len(direct_output)} chars")
        if direct_output:
            print(f"     Sample: {direct_output[:100]}...")

    if observer._orion_handler and hasattr(
        observer._orion_handler, "handle_orion_event"
    ):
        print("   Testing orion handler directly...")
        output.seek(0)
        output.truncate(0)
        observer._orion_handler.handle_orion_event(started_event)
        direct_output = output.getvalue()
        print(f"   Direct orion handler output: {len(direct_output)} chars")
        if direct_output:
            print(f"     Sample: {direct_output[:100]}...")


if __name__ == "__main__":
    asyncio.run(test_observer_with_old_handlers())
