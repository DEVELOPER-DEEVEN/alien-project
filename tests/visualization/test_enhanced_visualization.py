#!/usr/bin/env python3
"""
Test script to verify enhanced DAGVisualizationObserver functionality.
"""

import asyncio
import logging
import pytest
from typing import List

from network.orion.task_orion import TaskOrion
from network.orion.task_star import TaskStar
from network.orion.task_star_line import TaskStarLine
from network.orion.orchestrator.orchestrator import (
    TaskOrionOrchestrator,
)
from network.core.events import (
    get_event_bus,
    Event,
    EventType,
    TaskEvent,
    OrionEvent,
    IEventObserver,
)
from network.client.device_manager import OrionDeviceManager
from network.session.observers import DAGVisualizationObserver

# Configure logging
logging.basicConfig(level=logging.INFO)


class MockDevice:
    """Mock device for testing."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.is_busy = False

    async def execute_command(self, command: str) -> str:
        """Mock command execution."""
        await asyncio.sleep(0.2)  # Simulate work
        return f"Result from {self.device_id}: {command}"


class MockDeviceManager(OrionDeviceManager):
    """Mock device manager for testing."""

    def __init__(self):
        # Don't call super().__init__() to avoid complex initialization
        self.devices = {
            "device_1": MockDevice("device_1"),
            "device_2": MockDevice("device_2"),
        }

        # Create a mock device registry
        self.device_registry = type(
            "MockRegistry",
            (),
            {
                "get_all_devices": lambda: [
                    {
                        "device_id": "device_1",
                        "device_type": "mobile",
                        "status": "available",
                    },
                    {
                        "device_id": "device_2",
                        "device_type": "desktop",
                        "status": "available",
                    },
                ]
            },
        )()

    async def get_available_devices(self) -> List[dict]:
        """Get list of available devices."""
        return [
            {"device_id": "device_1", "device_type": "mobile", "status": "available"},
            {"device_id": "device_2", "device_type": "desktop", "status": "available"},
        ]

    async def execute_task(self, device_id: str, task_data: dict) -> dict:
        """Execute a task on the specified device."""
        device = self.devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        command = task_data.get("command", "default_command")
        result = await device.execute_command(command)

        return {"success": True, "result": result}


@pytest.mark.asyncio
async def test_enhanced_visualization():
    """Test enhanced DAG visualization."""
    print(" Testing Enhanced DAGVisualizationObserver...")

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

    # Create mock device manager
    device_manager = MockDeviceManager()

    # Create orchestrator
    orchestrator = TaskOrionOrchestrator(
        device_manager=device_manager, enable_logging=True, event_bus=event_bus
    )

    # Create a orion
    orion = TaskOrion("enhanced_viz_test")

    # Add some tasks
    task1 = TaskStar(
        task_id="data_prep",
        name="Data Preparation",
        description="Prepare input data for processing",
        target_device_id="device_1",
        task_data={"command": "prepare_data"},
        tips=["Ensure data is clean", "Validate input formats"],
    )

    task2 = TaskStar(
        task_id="model_train",
        name="Model Training",
        description="Train the ML model with prepared data",
        target_device_id="device_2",
        task_data={"command": "train_model"},
        tips=["Monitor training progress", "Use GPU acceleration"],
    )

    task3 = TaskStar(
        task_id="result_eval",
        name="Result Evaluation",
        description="Evaluate model performance",
        target_device_id="device_1",
        task_data={"command": "evaluate_results"},
        tips=["Check accuracy metrics", "Generate reports"],
    )

    orion.add_task(task1)
    orion.add_task(task2)
    orion.add_task(task3)

    # Add dependencies
    dep1 = TaskStarLine(
        from_task_id="data_prep",
        to_task_id="model_train",
        condition_description="Data must be prepared before training",
    )
    dep2 = TaskStarLine(
        from_task_id="model_train",
        to_task_id="result_eval",
        condition_description="Model must be trained before evaluation",
    )

    orion.add_dependency(dep1)
    orion.add_dependency(dep2)

    print(f"[OK] Created orion with {len(orion.tasks)} tasks")

    # Test orion modification event
    print("\n[CONTINUE] Testing ORION_MODIFIED event...")
    modification_event = OrionEvent(
        event_type=EventType.ORION_MODIFIED,
        source_id="test_script",
        timestamp=asyncio.get_event_loop().time(),
        data={
            "orion": orion,
            "modification_type": "tasks_and_dependencies_added",
            "added_tasks": ["data_prep", "model_train", "result_eval"],
            "added_dependencies": [
                "data_prep->model_train",
                "model_train->result_eval",
            ],
            "removed_tasks": [],
            "removed_dependencies": [],
        },
        orion_id=orion.orion_id,
        orion_state="modified",
    )
    await event_bus.publish_event(modification_event)

    # Wait a moment for visualization
    await asyncio.sleep(1)

    # Execute orion to see task events
    print("\n[START] Starting orion execution...")
    try:
        device_assignments = {
            "data_prep": "device_1",
            "model_train": "device_2",
            "result_eval": "device_1",
        }

        result = await orchestrator.orchestrate_orion(
            orion=orion,
            device_assignments=device_assignments,
            assignment_strategy="round_robin",
        )

        print(f"\n[OK] Orion execution completed: {result['status']}")
        print(f"[STATUS] Statistics: {result.get('statistics', {})}")

        return True

    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the enhanced visualization test."""
    print(" Starting Enhanced Visualization Test...")
    success = await test_enhanced_visualization()

    if success:
        print("\n All visualization tests passed!")
    else:
        print("\n Visualization tests failed!")

    return success


if __name__ == "__main__":
    asyncio.run(main())
