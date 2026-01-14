#!/usr/bin/env python3

"""
Simple test for mock client functionality and visualization for NetworkClient.
"""


def test_simple():
    """Simple test to verify pytest is working."""
    assert True


def test_import_client_display():
    """Test importing ClientDisplay."""
    from network.visualization.client_display import ClientDisplay
    from rich.console import Console

    console = Console()
    display = ClientDisplay(console)
    assert display is not None


def test_import_mock_agent():
    """Test importing MockOrionAgent."""
    from tests.network.mocks import (
        MockOrionAgent,
        MockTaskOrionOrchestrator,
    )

    mock_orchestrator = MockTaskOrionOrchestrator()
    mock_agent = MockOrionAgent(
        orchestrator=mock_orchestrator, name="test_mock"
    )
    assert mock_agent is not None
