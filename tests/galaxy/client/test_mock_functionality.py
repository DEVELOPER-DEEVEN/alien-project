#!/usr/bin/env python3
# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Test mock functionality and visualization for clusterClient.

This module tests:
1. Mock network agent integration
2. Visualization display functions
3. Mock network creation
4. TaskStarLine dependency handling
"""

import pytest


def test_create_simple_test_network():
    """Test creating a simple test network with dependencies."""
    from tests.cluster.mocks import create_simple_test_network

    # Test sequential network
    tasks = ["Task 1", "Task 2", "Task 3"]
    network = create_simple_test_network(
        task_descriptions=tasks, network_name="Testnetwork", sequential=True
    )

    assert network is not None
    assert network.task_count == 3
    assert (
        network.dependency_count == 2
    )  # Two dependencies for 3 sequential tasks


@pytest.mark.asyncio
async def test_mock_network_agent_creation():
    """Test MocknetworkAgent network creation."""
    from tests.cluster.mocks import (
        MocknetworkAgent,
        MockTasknetworkOrchestrator,
    )
    from Alien.module.context import Context, ContextNames

    # Create mock orchestrator
    mock_orchestrator = MockTasknetworkOrchestrator(enable_logging=False)

    # Create mock agent
    mock_agent = MocknetworkAgent(
        orchestrator=mock_orchestrator, name="test_mock_network"
    )

    # Create mock context
    context = Context()
    context.set(ContextNames.REQUEST, "Create a simple test workflow")

    # Test network creation
    network = await mock_agent.process_creation(context)

    assert network is not None
    assert network.name is not None
    assert network.task_count > 0
    print(f"Created network with {network.task_count} tasks")


def test_visualization_display():
    """Test basic visualization display functionality."""
    from cluster.visualization.client_display import ClientDisplay
    from rich.console import Console

    console = Console()
    display = ClientDisplay(console)

    # Test basic display functions without errors
    display.show_cluster_banner()
    display.print_success("Test success message")
    display.print_info("Test info message")

    # Test result display
    mock_result = {
        "status": "completed",
        "execution_time": 5.5,
        "network": {
            "name": "Test network",
            "task_count": 3,
            "state": "completed",
        },
    }
    display.display_result(mock_result)

    print("✅ All visualization tests passed")
