#!/usr/bin/env python3
# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Simple test for mock client functionality and visualization for clusterClient.
"""


def test_simple():
    """Simple test to verify pytest is working."""
    assert True


def test_import_client_display():
    """Test importing ClientDisplay."""
    from cluster.visualization.client_display import ClientDisplay
    from rich.console import Console

    console = Console()
    display = ClientDisplay(console)
    assert display is not None


def test_import_mock_agent():
    """Test importing MocknetworkAgent."""
    from tests.cluster.mocks import (
        MocknetworkAgent,
        MockTasknetworkOrchestrator,
    )

    mock_orchestrator = MockTasknetworkOrchestrator()
    mock_agent = MocknetworkAgent(
        orchestrator=mock_orchestrator, name="test_mock"
    )
    assert mock_agent is not None
