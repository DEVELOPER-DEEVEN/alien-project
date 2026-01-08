#!/usr/bin/env python3
# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Unit tests for clusterSession cancellation mechanism.

Tests the request_cancellation method and cancellation flag propagation
through round execution.
"""

import asyncio
import pytest
import pytest_asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add project root to path
Alien_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(Alien_ROOT))

from cluster.session.cluster_session import clusterSession, clusterRound
from cluster.agents.network_agent import networkAgent
from cluster.network.orchestrator.orchestrator import TasknetworkOrchestrator
from cluster.network import Tasknetwork
from Alien.module.context import Context


@pytest_asyncio.fixture
def mock_session():
    """Create a mock clusterSession for testing."""
    with patch("cluster.session.cluster_session.get_cluster_config"), patch(
        "cluster.session.cluster_session.utils"
    ), patch("cluster.session.cluster_session.get_event_bus"):

        mock_client = MagicMock()
        mock_client.device_manager = MagicMock()
        mock_client.device_manager.get_all_devices = MagicMock(return_value={})

        session = clusterSession(
            task="test_task",
            should_evaluate=False,
            id="test_session_id",
            client=mock_client,
            initial_request="test request",
        )

        # Mock orchestrator
        session._orchestrator.cancel_execution = AsyncMock()

        yield session


@pytest.mark.asyncio
async def test_request_cancellation_sets_flags(mock_session):
    """Test that request_cancellation sets cancellation flags."""
    # Arrange
    mock_network = MagicMock(spec=Tasknetwork)
    mock_network.network_id = "test_network_123"
    mock_session._current_network = mock_network

    # Act
    await mock_session.request_cancellation()

    # Assert
    assert mock_session._cancellation_requested is True
    assert mock_session._finish is True
    mock_session._orchestrator.cancel_execution.assert_called_once_with(
        "test_network_123"
    )


@pytest.mark.asyncio
async def test_request_cancellation_without_network(mock_session):
    """Test request_cancellation when no network is active."""
    # Arrange
    mock_session._current_network = None

    # Act
    await mock_session.request_cancellation()

    # Assert
    assert mock_session._cancellation_requested is True
    assert mock_session._finish is True
    mock_session._orchestrator.cancel_execution.assert_not_called()


@pytest.mark.asyncio
async def test_round_checks_cancellation_flag():
    """Test that clusterRound checks cancellation flag during execution."""
    # Arrange
    with patch("cluster.session.cluster_session.get_cluster_config"):
        mock_agent = MagicMock(spec=networkAgent)
        mock_agent.handle = AsyncMock()
        mock_agent.state = MagicMock()
        mock_agent.state.is_round_end = MagicMock(return_value=False)
        mock_agent.state.next_state = MagicMock(return_value=mock_agent.state)
        mock_agent.state.name = MagicMock(return_value="TestState")
        mock_agent.set_state = MagicMock()
        mock_agent._status = "FINISH"

        mock_context = MagicMock(spec=Context)
        mock_context.get = MagicMock(return_value=0)

        # Create a mock session with cancellation flag
        mock_session = MagicMock()
        mock_session._cancellation_requested = False

        round = clusterRound(
            request="test request",
            agent=mock_agent,
            context=mock_context,
            should_evaluate=False,
            id=1,
        )
        round._session = mock_session

        call_count = 0

        async def handle_with_cancellation(ctx):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                mock_session._cancellation_requested = True
                mock_agent.state.is_round_end = MagicMock(return_value=True)
            await asyncio.sleep(0.01)

        mock_agent.handle = handle_with_cancellation

        # Act
        await round.run()

        # Assert
        assert call_count >= 2        assert mock_session._cancellation_requested is True


@pytest.mark.asyncio
async def test_round_stops_immediately_on_cancellation():
    """Test that round stops immediately when cancellation is requested."""
    # Arrange
    with patch("cluster.session.cluster_session.get_cluster_config"):
        mock_agent = MagicMock(spec=networkAgent)
        mock_agent.handle = AsyncMock()
        mock_agent.state = MagicMock()
        mock_agent.state.is_round_end = MagicMock(return_value=False)
        mock_agent._status = "CANCELLED"

        mock_context = MagicMock(spec=Context)
        mock_context.get = MagicMock(return_value=0)

        # Session with cancellation already requested
        mock_session = MagicMock()
        mock_session._cancellation_requested = True

        round = clusterRound(
            request="test request",
            agent=mock_agent,
            context=mock_context,
            should_evaluate=False,
            id=1,
        )
        round._session = mock_session

        # Act
        await round.run()

        # Assert
        mock_agent.handle.assert_not_called()


@pytest.mark.asyncio
async def test_reset_clears_cancellation_flag(mock_session):
    """Test that reset() clears the cancellation flag."""
    # Arrange
    mock_session._cancellation_requested = True
    mock_session._finish = True

    # Act
    mock_session.reset()

    # Assert
    assert mock_session._cancellation_requested is False
    assert mock_session._finish is False


@pytest.mark.asyncio
async def test_force_finish_sets_finish_flag(mock_session):
    """Test that force_finish sets the finish flag."""
    # Arrange
    assert mock_session._finish is False

    # Act
    await mock_session.force_finish("Test reason")

    # Assert
    assert mock_session._finish is True
    assert mock_session._agent.status == "FINISH"
    assert mock_session._session_results["finish_reason"] == "Test reason"


@pytest.mark.asyncio
async def test_create_new_round_passes_session_reference(mock_session):
    """Test that create_new_round properly passes session reference to clusterRound.

    This is a regression test for the bug where clusterRound didn't receive
    the session reference, causing AttributeError when checking cancellation flag.
    """
    # Arrange
    mock_session._initial_request = "test request"

    # Act
    round = mock_session.create_new_round()

    # Assert
    assert round is not None
    assert (
        round._session is mock_session
    ), "clusterRound._session should reference parent session"

    # Verify cancellation check won't fail
    assert (
        mock_session._cancellation_requested is False
    ), "Session should have _cancellation_requested initialized to False"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
