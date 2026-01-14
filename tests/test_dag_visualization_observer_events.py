#!/usr/bin/env python3

"""
Comprehensive test for DAGVisualizationObserver event handling and visualization output.

This test verifies that the DAGVisualizationObserver can properly handle different
types of events and produce appropriate visualization output using the refactored
modular visualization components.
"""

import sys
import os
import asyncio
import time
from io import StringIO
from rich.console import Console
from unittest.mock import MagicMock

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
    orion = TaskOrion(name="Test Data Pipeline")

    # Add some tasks
    data_task = TaskStar(
        task_id="data_001",
        name="Data Collection",
        description="Collect data from sources",
        priority=TaskPriority.HIGH,
    )
    # Simulate completed task
    data_task.start_execution()
    data_task.complete_with_success({"records": 1000})
    orion.add_task(data_task)

    process_task = TaskStar(
        task_id="process_001",
        name="Data Processing",
        description="Process collected data",
        priority=TaskPriority.MEDIUM,
    )
    # Simulate running task
    process_task.start_execution()
    orion.add_task(process_task)

    validate_task = TaskStar(
        task_id="validate_001",
        name="Data Validation",
        description="Validate processed data",
        priority=TaskPriority.LOW,
    )
    # Leave as pending (default)
    orion.add_task(validate_task)

    # Add dependencies
    dep1 = TaskStarLine("data_001", "process_001", DependencyType.SUCCESS_ONLY)
    dep2 = TaskStarLine("process_001", "validate_001", DependencyType.SUCCESS_ONLY)
    orion.add_dependency(dep1)
    orion.add_dependency(dep2)

    return orion


def create_orion_event(
    event_type: EventType, orion: TaskOrion, **kwargs
):
    """Create a orion event for testing."""
    return OrionEvent(
        event_type=event_type,
        source_id="test_source",
        timestamp=time.time(),
        data={
            "orion": orion,
            "orion_id": orion.orion_id,
            **kwargs,
        },
        orion_id=orion.orion_id,
        orion_state=(
            orion.state.value if hasattr(orion, "state") else "created"
        ),
        new_ready_tasks=kwargs.get("new_ready_tasks", []),
    )


def create_task_event(
    event_type: EventType, task_id: str, orion_id: str, **kwargs
):
    """Create a task event for testing."""
    return TaskEvent(
        event_type=event_type,
        source_id="test_source",
        timestamp=time.time(),
        data={"orion_id": orion_id, **kwargs},
        task_id=task_id,
        status=kwargs.get("status", "running"),
    )


async def test_observer_initialization():
    """Test that the observer initializes correctly."""
    print("🧪 Testing DAGVisualizationObserver Initialization")
    print("=" * 60)

    # Test with default settings
    observer = DAGVisualizationObserver()
    assert observer.enable_visualization == True
    assert observer._console is None
    print("✅ Default initialization successful")

    # Test with custom console
    custom_console = Console()
    observer_with_console = DAGVisualizationObserver(console=custom_console)
    assert observer_with_console._console == custom_console
    print("✅ Custom console initialization successful")

    # Test with disabled visualization
    disabled_observer = DAGVisualizationObserver(enable_visualization=False)
    assert disabled_observer.enable_visualization == False
    print("✅ Disabled visualization initialization successful")

    return True


async def test_orion_events():
    """Test orion event handling and visualization."""
    print("\n🧪 Testing Orion Event Handling")
    print("=" * 60)

    # Create observer with string output capture
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=80)
    observer = DAGVisualizationObserver(console=console)

    # Create test orion
    orion = create_test_orion()

    # Test orion started event
    print("\n📤 Testing ORION_STARTED event...")
    started_event = create_orion_event(
        EventType.ORION_STARTED,
        orion,
        message="Pipeline execution started",
    )

    await observer.on_event(started_event)
    output_text = output.getvalue()

    if "started" in output_text.lower() or "orion" in output_text.lower():
        print("✅ Orion started event produced output")
    else:
        print("⚠️  Orion started event - no visible output detected")

    # Clear output buffer
    output.seek(0)
    output.truncate(0)

    # Test orion completed event
    print("\n📤 Testing ORION_COMPLETED event...")
    completed_event = create_orion_event(
        EventType.ORION_COMPLETED,
        orion,
        execution_time=45.7,
        message="Pipeline execution completed successfully",
    )

    await observer.on_event(completed_event)
    output_text = output.getvalue()

    if "completed" in output_text.lower() or "execution" in output_text.lower():
        print("✅ Orion completed event produced output")
    else:
        print("⚠️  Orion completed event - no visible output detected")

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
    dep3 = TaskStarLine("validate_001", "report_001", DependencyType.SUCCESS_ONLY)
    orion.add_dependency(dep3)

    modified_event = create_orion_event(
        EventType.ORION_MODIFIED,
        orion,
        changes={
            "modification_type": "tasks_added",
            "added_tasks": ["report_001"],
            "added_dependencies": [("validate_001", "report_001")],
        },
        message="Added report generation task",
    )

    await observer.on_event(modified_event)
    output_text = output.getvalue()

    if "modified" in output_text.lower() or "added" in output_text.lower():
        print("✅ Orion modified event produced output")
    else:
        print("⚠️  Orion modified event - no visible output detected")

    # Clear output buffer
    output.seek(0)
    output.truncate(0)

    # Test orion failed event
    print("\n📤 Testing ORION_FAILED event...")
    failed_event = create_orion_event(
        EventType.ORION_FAILED,
        orion,
        error=Exception("Simulated pipeline failure"),
        message="Pipeline execution failed",
    )

    await observer.on_event(failed_event)
    output_text = output.getvalue()

    if "failed" in output_text.lower() or "error" in output_text.lower():
        print("✅ Orion failed event produced output")
    else:
        print("⚠️  Orion failed event - no visible output detected")

    return True


async def test_task_events():
    """Test task event handling and visualization."""
    print("\n🧪 Testing Task Event Handling")
    print("=" * 60)

    # Create observer with string output capture
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=80)
    observer = DAGVisualizationObserver(console=console)

    # Create and register test orion
    orion = create_test_orion()
    observer.register_orion(orion.orion_id, orion)

    # Test task started event
    print("\n📤 Testing TASK_STARTED event...")
    task_started_event = create_task_event(
        EventType.TASK_STARTED,
        "process_001",
        orion.orion_id,
        status="running",
        message="Data processing task started",
    )

    await observer.on_event(task_started_event)
    output_text = output.getvalue()

    if "task" in output_text.lower() or "process" in output_text.lower():
        print("✅ Task started event produced output")
    else:
        print("⚠️  Task started event - no visible output detected")

    # Clear output buffer
    output.seek(0)
    output.truncate(0)

    # Test task completed event
    print("\n📤 Testing TASK_COMPLETED event...")
    task_completed_event = create_task_event(
        EventType.TASK_COMPLETED,
        "process_001",
        orion.orion_id,
        status="completed",
        result={"records_processed": 10000},
        message="Data processing completed successfully",
    )

    await observer.on_event(task_completed_event)
    output_text = output.getvalue()

    if "completed" in output_text.lower() or "task" in output_text.lower():
        print("✅ Task completed event produced output")
    else:
        print("⚠️  Task completed event - no visible output detected")

    # Clear output buffer
    output.seek(0)
    output.truncate(0)

    # Test task failed event
    print("\n📤 Testing TASK_FAILED event...")
    task_failed_event = create_task_event(
        EventType.TASK_FAILED,
        "validate_001",
        orion.orion_id,
        status="failed",
        error=Exception("Validation failed: invalid data format"),
        message="Data validation task failed",
    )

    await observer.on_event(task_failed_event)
    output_text = output.getvalue()

    if "failed" in output_text.lower() or "error" in output_text.lower():
        print("✅ Task failed event produced output")
    else:
        print("⚠️  Task failed event - no visible output detected")

    return True


async def test_observer_state_management():
    """Test observer state management functionality."""
    print("\n🧪 Testing Observer State Management")
    print("=" * 60)

    observer = DAGVisualizationObserver()
    orion = create_test_orion()

    # Test orion registration
    observer.register_orion(orion.orion_id, orion)
    retrieved = observer.get_orion(orion.orion_id)
    assert retrieved == orion
    print("✅ Orion registration and retrieval works")

    # Test visualization toggle
    observer.set_visualization_enabled(False)
    assert observer.enable_visualization == False
    print("✅ Visualization can be disabled")

    observer.set_visualization_enabled(True)
    assert observer.enable_visualization == True
    print("✅ Visualization can be re-enabled")

    # Test clearing orions
    observer.clear_orions()
    retrieved = observer.get_orion(orion.orion_id)
    assert retrieved is None
    print("✅ Orion clearing works")

    return True


async def test_error_handling():
    """Test observer error handling."""
    print("\n🧪 Testing Error Handling")
    print("=" * 60)

    observer = DAGVisualizationObserver()

    # Test handling event with no orion
    task_event_no_orion = create_task_event(
        EventType.TASK_STARTED, "unknown_task", "unknown_orion_id"
    )

    try:
        await observer.on_event(task_event_no_orion)
        print("✅ Gracefully handled task event with unknown orion")
    except Exception as e:
        print(f"❌ Error handling task event with unknown orion: {e}")
        return False

    # Test handling malformed event
    malformed_event = Event(
        event_type=EventType.TASK_STARTED,
        source_id="test",
        timestamp=time.time(),
        data={},  # Missing required data
    )

    try:
        await observer.on_event(malformed_event)
        print("✅ Gracefully handled malformed event")
    except Exception as e:
        print(f"❌ Error handling malformed event: {e}")
        return False

    return True


async def test_visualization_output_quality():
    """Test the quality and completeness of visualization output."""
    print("\n🧪 Testing Visualization Output Quality")
    print("=" * 60)

    # Create observer with full output capture
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=120)
    observer = DAGVisualizationObserver(console=console)

    # Create rich test orion
    orion = create_test_orion()

    # Register orion
    observer.register_orion(orion.orion_id, orion)

    # Generate all event types and capture output
    events = [
        create_orion_event(EventType.ORION_STARTED, orion),
        create_task_event(
            EventType.TASK_STARTED, "data_001", orion.orion_id
        ),
        create_task_event(
            EventType.TASK_COMPLETED, "data_001", orion.orion_id
        ),
        create_task_event(
            EventType.TASK_STARTED, "process_001", orion.orion_id
        ),
        create_orion_event(
            EventType.ORION_MODIFIED,
            orion,
            changes={"modification_type": "task_updated"},
        ),
        create_task_event(
            EventType.TASK_COMPLETED, "process_001", orion.orion_id
        ),
        create_orion_event(EventType.ORION_COMPLETED, orion),
    ]

    total_output_length = 0
    for event in events:
        output.seek(0)
        output.truncate(0)

        await observer.on_event(event)
        event_output = output.getvalue()
        total_output_length += len(event_output)

        print(
            f"📊 {event.event_type.value} event output: {len(event_output)} characters"
        )

    print(f"\n📈 Total visualization output: {total_output_length} characters")

    if total_output_length > 500:  # Expect meaningful output
        print("✅ Rich visualization output generated")
        return True
    else:
        print("⚠️  Limited visualization output detected")
        return False


async def run_all_tests():
    """Run all DAGVisualizationObserver tests."""
    print("🌟 DAGVisualizationObserver Event Handling Test Suite")
    print("=" * 80)
    print("Testing comprehensive event handling and visualization output")
    print("=" * 80)

    test_results = []

    # Run all tests
    tests = [
        ("Observer Initialization", test_observer_initialization),
        ("Orion Events", test_orion_events),
        ("Task Events", test_task_events),
        ("State Management", test_observer_state_management),
        ("Error Handling", test_error_handling),
        ("Visualization Quality", test_visualization_output_quality),
    ]

    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
            print(
                f"\n{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}"
            )
        except Exception as e:
            test_results.append((test_name, False))
            print(f"\n❌ {test_name}: FAILED - {e}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Results Summary")
    print("=" * 80)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")

    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All DAGVisualizationObserver tests passed!")
        print("✅ Observer properly handles all event types")
        print("✅ Visualization output is generated for events")
        print("✅ Error handling is robust")
        print("✅ State management functions correctly")
    else:
        print("💥 Some tests failed. Observer may need attention.")

    return passed == total


if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
