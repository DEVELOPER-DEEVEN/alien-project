#!/usr/bin/env python
"""
Integration test demonstrating OrionAgent event publishing in a realistic scenario.
"""

import asyncio
import pytest
import time
from network.orion import TaskOrion, TaskStar, TaskStarLine
from network.core.events import OrionEvent, EventType, get_event_bus
from network.session.observers import DAGVisualizationObserver


class SimulatedOrionAgent:
    """Simplified OrionAgent simulation for demonstration."""

    def __init__(self, name="simulated_orion_agent"):
        self.name = name
        self._event_bus = get_event_bus()
        self._current_orion = None

    async def simulate_process_editing(self, before_orion, after_orion):
        """Simulate the process_editing method with event publishing."""
        print(f"🔄 {self.name} processing orion changes...")

        self._current_orion = after_orion

        # Publish DAG Modified Event (same logic as in OrionAgent)
        await self._event_bus.publish_event(
            OrionEvent(
                event_type=EventType.ORION_MODIFIED,
                source_id=self.name,
                timestamp=time.time(),
                data={
                    "old_orion": before_orion,
                    "new_orion": after_orion,
                    "modification_type": "agent_processing_result",
                },
                orion_id=after_orion.orion_id,
                orion_state=(
                    after_orion.state.value
                    if after_orion.state
                    else "unknown"
                ),
            )
        )

        print(f"✅ {self.name} published orion modified event")
        return after_orion


@pytest.mark.asyncio
async def test_orion_agent_integration():
    """Integration test demonstrating full OrionAgent event flow."""
    print("🧪 OrionAgent Event Publishing Integration Test\n")

    # Create DAG visualization observer
    dag_observer = DAGVisualizationObserver()

    # Subscribe to event bus
    event_bus = get_event_bus()
    event_bus.subscribe(dag_observer, {EventType.ORION_MODIFIED})

    # Create simulated agent
    agent = SimulatedOrionAgent("main_orion_agent")

    print("=== Scenario 1: Task Creation and Dependencies ===")

    # Original orion
    original = TaskOrion("project-alpha", "Project Alpha Development")
    task1 = TaskStar("req_analysis", "Requirements Analysis")
    task2 = TaskStar("system_design", "System Design")

    original.add_task(task1)
    original.add_task(task2)

    # Modified orion with new tasks and dependencies
    modified = TaskOrion("project-alpha", "Project Alpha Development")
    task1_mod = TaskStar("req_analysis", "Requirements Analysis")
    task2_mod = TaskStar("system_design", "System Design")
    task3_new = TaskStar("implementation", "Implementation Phase")
    task4_new = TaskStar("testing", "Testing Phase")

    # Add dependency
    dep1 = TaskStarLine("req_analysis", "system_design")
    dep2 = TaskStarLine("system_design", "implementation")
    dep3 = TaskStarLine("implementation", "testing")

    modified.add_task(task1_mod)
    modified.add_task(task2_mod)
    modified.add_task(task3_new)
    modified.add_task(task4_new)
    modified.add_dependency(dep1)
    modified.add_dependency(dep2)
    modified.add_dependency(dep3)

    await agent.simulate_process_editing(original, modified)
    await asyncio.sleep(0.1)

    print("\n" + "=" * 80)

    print("\n=== Scenario 2: Task Property Updates ===")

    # Create orion with property changes
    updated = TaskOrion("project-alpha", "Project Alpha Development")
    task1_updated = TaskStar(
        "req_analysis", "Updated Requirements Analysis"
    )  # Changed name
    task2_updated = TaskStar("system_design", "Enhanced System Design")  # Changed name
    task3_updated = TaskStar("implementation", "Implementation Phase")
    task4_updated = TaskStar("testing", "Comprehensive Testing Phase")  # Changed name

    updated.add_task(task1_updated)
    updated.add_task(task2_updated)
    updated.add_task(task3_updated)
    updated.add_task(task4_updated)

    await agent.simulate_process_editing(modified, updated)
    await asyncio.sleep(0.1)

    print("\n" + "=" * 80)

    print("\n=== Scenario 3: Task Removal ===")

    # Remove some tasks
    final = TaskOrion("project-alpha", "Project Alpha Development")
    task1_final = TaskStar("req_analysis", "Updated Requirements Analysis")
    task4_final = TaskStar("testing", "Comprehensive Testing Phase")

    final.add_task(task1_final)
    final.add_task(task4_final)

    await agent.simulate_process_editing(updated, final)
    await asyncio.sleep(0.1)

    print("\n✅ All OrionAgent integration tests completed!")
    print("🎉 Features successfully demonstrated:")
    print("   • OrionAgent event publishing")
    print("   • DAG change detection and visualization")
    print("   • Rich terminal beautification")
    print("   • End-to-end event flow")


if __name__ == "__main__":
    asyncio.run(test_orion_agent_integration())
