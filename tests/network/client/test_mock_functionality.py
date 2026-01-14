#!/usr/bin/env python3

"""
Test mock functionality and visualization for NetworkClient.

This module tests:
1. Mock orion agent integration
2. Visualization display functions
3. Mock orion creation
4. TaskStarLine dependency handling
"""

import pytest


def test_create_simple_test_orion():
    """Test creating a simple test orion with dependencies."""
    from tests.network.mocks import create_simple_test_orion

    # Test sequential orion
    tasks = ["Task 1", "Task 2", "Task 3"]
    orion = create_simple_test_orion(
        task_descriptions=tasks, orion_name="TestOrion", sequential=True
    )

    assert orion is not None
    assert orion.task_count == 3
    assert (
        orion.dependency_count == 2
    )  # Two dependencies for 3 sequential tasks


@pytest.mark.asyncio
async def test_mock_orion_agent_creation():
    """Test MockOrionAgent orion creation."""
    from tests.network.mocks import (
        MockOrionAgent,
        MockTaskOrionOrchestrator,
    )
    from alien.module.context import Context, ContextNames

    # Create mock orchestrator
    mock_orchestrator = MockTaskOrionOrchestrator(enable_logging=False)

    # Create mock agent
    mock_agent = MockOrionAgent(
        orchestrator=mock_orchestrator, name="test_mock_orion"
    )

    # Create mock context
    context = Context()
    context.set(ContextNames.REQUEST, "Create a simple test workflow")

    # Test orion creation
    orion = await mock_agent.process_creation(context)

    assert orion is not None
    assert orion.name is not None
    assert orion.task_count > 0
    print(f"Created orion with {orion.task_count} tasks")


def test_visualization_display():
    """Test basic visualization display functionality."""
    from network.visualization.client_display import ClientDisplay
    from rich.console import Console

    console = Console()
    display = ClientDisplay(console)

    # Test basic display functions without errors
    display.show_network_banner()
    display.print_success("Test success message")
    display.print_info("Test info message")

    # Test result display
    mock_result = {
        "status": "completed",
        "execution_time": 5.5,
        "orion": {
            "name": "Test Orion",
            "task_count": 3,
            "state": "completed",
        },
    }
    display.display_result(mock_result)

    print("✅ All visualization tests passed")
