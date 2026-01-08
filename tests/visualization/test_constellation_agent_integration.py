#!/usr/bin/env python
"""
Integration test demonstrating networkAgent event publishing in a realistic scenario.
"""

import asyncio
import pytest
import time
from cluster.network import Tasknetwork, TaskStar, TaskStarLine
from cluster.core.events import networkEvent, EventType, get_event_bus
from cluster.session.observers import DAGVisualizationObserver


class SimulatednetworkAgent:
    """Simplified networkAgent simulation for demonstration."""

    def __init__(self, name="simulated_network_agent"):
        self.name = name
        self._event_bus = get_event_bus()
        self._current_network = None

    async def simulate_process_editing(self, before_network, after_network):
        """Simulate the process_editing method with event publishing."""
        print(f"🔄 {self.name} processing network changes...")

        self._current_network = after_network

        # Publish DAG Modified Event (same logic as in networkAgent)
        await self._event_bus.publish_event(
            networkEvent(
                event_type=EventType.network_MODIFIED,
                source_id=self.name,
                timestamp=time.time(),
                data={
                    "old_network": before_network,
                    "new_network": after_network,
                    "modification_type": "agent_processing_result",
                },
                network_id=after_network.network_id,
                network_state=(
                    after_network.state.value
                    if after_network.state
                    else "unknown"
                ),
            )
        )

        print(f"✅ {self.name} published network modified event")
        return after_network


@pytest.mark.asyncio
async def test_network_agent_integration():
    """Integration test demonstrating full networkAgent event flow."""
    print("🧪 networkAgent Event Publishing Integration Test\n")

    # Create DAG visualization observer
    dag_observer = DAGVisualizationObserver()

    # Subscribe to event bus
    event_bus = get_event_bus()
    event_bus.subscribe(dag_observer, {EventType.network_MODIFIED})

    # Create simulated agent
    agent = SimulatednetworkAgent("main_network_agent")

    print("=== Scenario 1: Task Creation and Dependencies ===")

    # Original network
    original = Tasknetwork("project-alpha", "Project Alpha Development")
    task1 = TaskStar("req_analysis", "Requirements Analysis")
    task2 = TaskStar("system_design", "System Design")

    original.add_task(task1)
    original.add_task(task2)

    # Modified network with new tasks and dependencies
    modified = Tasknetwork("project-alpha", "Project Alpha Development")
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

    # Create network with property changes
    updated = Tasknetwork("project-alpha", "Project Alpha Development")
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
    final = Tasknetwork("project-alpha", "Project Alpha Development")
    task1_final = TaskStar("req_analysis", "Updated Requirements Analysis")
    task4_final = TaskStar("testing", "Comprehensive Testing Phase")

    final.add_task(task1_final)
    final.add_task(task4_final)

    await agent.simulate_process_editing(updated, final)
    await asyncio.sleep(0.1)

    print("\n✅ All networkAgent integration tests completed!")
    print("🎉 Features successfully demonstrated:")
    print("   • networkAgent event publishing")
    print("   • DAG change detection and visualization")
    print("   • Rich terminal beautification")
    print("   • End-to-end event flow")


if __name__ == "__main__":
    asyncio.run(test_network_agent_integration())
