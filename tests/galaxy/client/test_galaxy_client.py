# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Tests for clusterClient with proper interface usage.

This test module verifies that clusterClient works correctly with the updated
clusterSession interface and provides proper functionality for both interactive
and batch modes.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from pathlib import Path
import json

from cluster.cluster_client import clusterClient
from cluster.client.network_client import networkClient
from cluster.session.cluster_session import clusterSession


class TestclusterClient:
    """Test suite for clusterClient functionality."""

    @pytest.fixture
    def mock_network_client(self):
        """Create a mock networkClient."""
        mock_client = MagicMock(spec=networkClient)
        mock_client.device_manager = MagicMock()
        mock_client.initialize = AsyncMock()
        mock_client.shutdown = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_cluster_session(self):
        """Create a mock clusterSession."""
        mock_session = MagicMock(spec=clusterSession)
        mock_session.task = "test_task"
        mock_session._rounds = {}
        mock_session.run = AsyncMock()
        mock_session.force_finish = AsyncMock()
        mock_session._current_network = None
        mock_session.log_path = "test/path"
        return mock_session

    def test_cluster_client_initialization(self):
        """Test clusterClient initialization."""
        # Test default initialization
        client = clusterClient()
        assert client.session_name.startswith("cluster_session_")
        assert client.max_rounds == 10
        assert client.output_dir == Path("./logs")

        # Test custom initialization
        custom_client = clusterClient(
            session_name="custom_session",
            max_rounds=20,
            log_level="DEBUG",
            output_dir="/custom/output",
        )
        assert custom_client.session_name == "custom_session"
        assert custom_client.max_rounds == 20
        assert custom_client.output_dir == Path("/custom/output")

    @pytest.mark.asyncio
    async def test_cluster_client_initialize(
        self, mock_network_client, mock_cluster_session
    ):
        """Test clusterClient initialize method."""
        client = clusterClient(session_name="test_session")

        with patch(
            "Alien.cluster.cluster_client.networkClient",
            return_value=mock_network_client,
        ), patch(
            "Alien.cluster.cluster_client.clusterSession", return_value=mock_cluster_session
        ):
            await client.initialize()

            # Verify initialization
            assert client._client == mock_network_client
            assert client._session == mock_cluster_session
            mock_network_client.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_request(
        self, mock_network_client, mock_cluster_session
    ):
        """Test processing a single request."""
        client = clusterClient(session_name="test_session")
        client._client = mock_network_client
        client._session = mock_cluster_session

        # Mock network for result testing
        mock_network = MagicMock()
        mock_network.network_id = "test_network"
        mock_network.name = "Test network"
        mock_network.tasks = ["task1", "task2"]
        mock_network.dependencies = []
        mock_network.state = MagicMock()
        mock_network.state.value = "completed"
        mock_cluster_session._current_network = mock_network

        result = await client.process_request("Create a test workflow", "test_task")

        # Verify request processing
        assert result["status"] == "completed"
        assert result["request"] == "Create a test workflow"
        assert result["task_name"] == "test_task"
        assert "execution_time" in result
        assert result["network"]["name"] == "Test network"
        mock_cluster_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_request_failure(
        self, mock_network_client, mock_cluster_session
    ):
        """Test processing request with failure."""
        client = clusterClient(session_name="test_session")
        client._client = mock_network_client
        client._session = mock_cluster_session

        # Mock session run to raise an exception
        mock_cluster_session.run.side_effect = Exception("Test error")

        result = await client.process_request("Failing request")

        # Verify error handling
        assert result["status"] == "failed"
        assert result["error"] == "Test error"
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_shutdown(self, mock_network_client, mock_cluster_session):
        """Test cluster client shutdown."""
        client = clusterClient(session_name="test_session")
        client._client = mock_network_client
        client._session = mock_cluster_session

        await client.shutdown()

        # Verify shutdown calls
        mock_network_client.shutdown.assert_called_once()
        mock_cluster_session.force_finish.assert_called_once_with("Client shutdown")

    @pytest.mark.asyncio
    async def test_interactive_mode_commands(
        self, mock_network_client, mock_cluster_session
    ):
        """Test interactive mode command handling."""
        client = clusterClient(session_name="test_session")
        client._client = mock_network_client
        client._session = mock_cluster_session

        # Mock user inputs
        user_inputs = ["help", "status", "quit"]

        with patch.object(client.display, "get_user_input", side_effect=user_inputs):
            await client.interactive_mode()

        # Verify that interactive mode processed commands without errors
        # (This is a basic test - in practice you'd mock more display methods)

    def test_display_integration(self):
        """Test that client properly integrates with ClientDisplay."""
        client = clusterClient(session_name="test_session")

        # Verify display manager is initialized
        assert client.display is not None
        assert hasattr(client.display, "show_cluster_banner")
        assert hasattr(client.display, "display_result")
        assert hasattr(client.display, "show_status")

    @pytest.mark.asyncio
    async def test_cluster_session_interface_compatibility(
        self, mock_network_client
    ):
        """Test that clusterClient uses the correct clusterSession interface."""
        client = clusterClient(session_name="test_session")

        with patch(
            "Alien.cluster.cluster_client.networkClient",
            return_value=mock_network_client,
        ):
            # Mock clusterSession constructor to verify correct parameters
            with patch("Alien.cluster.cluster_client.clusterSession") as mock_session_class:
                mock_session = MagicMock()
                mock_session_class.return_value = mock_session

                await client.initialize()

                # Verify clusterSession is called with correct parameters
                mock_session_class.assert_called_once_with(
                    task="test_session",
                    should_evaluate=False,
                    id="test_session",
                    client=mock_network_client,
                    initial_request="",
                )

    def test_status_display_integration(self):
        """Test status display functionality."""
        client = clusterClient(session_name="test_session")

        # Test status display without session
        client._show_status()

        # Test status display with mock session
        mock_session = MagicMock()
        mock_session._rounds = {"round1": {}}
        client._session = mock_session

        client._show_status()


@pytest.mark.asyncio
class TestclusterClientIntegration:
    """Integration tests for clusterClient."""

    async def test_full_workflow_simulation(self):
        """Test a complete workflow simulation using mocks."""
        # Create client
        client = clusterClient(session_name="integration_test")

        # Mock all external dependencies
        with patch(
            "Alien.cluster.cluster_client.networkClient"
        ) as mock_client_class, patch(
            "Alien.cluster.cluster_client.clusterSession"
        ) as mock_session_class:

            # Setup mocks
            mock_client = MagicMock()
            mock_client.initialize = AsyncMock()
            mock_client.shutdown = AsyncMock()
            mock_client.device_manager = MagicMock()
            mock_client_class.return_value = mock_client

            mock_session = MagicMock()
            mock_session.run = AsyncMock()
            mock_session.force_finish = AsyncMock()
            mock_session._rounds = {}
            mock_session.log_path = "test/path"
            mock_session._current_network = None
            mock_session_class.return_value = mock_session

            # Initialize client
            await client.initialize()

            # Process request
            result = await client.process_request("Test integration request")

            # Shutdown
            await client.shutdown()

            # Verify workflow
            assert result["status"] == "completed"
            mock_client.initialize.assert_called_once()
            mock_session.run.assert_called_once()
            mock_client.shutdown.assert_called_once()


class TestclusterClientMockImplementation:
    """Test mock implementation for testing purposes."""

    def test_mock_creation(self):
        """Test creating a mock clusterClient for testing."""
        # Create mock client for use in other tests
        mock_client = MagicMock(spec=clusterClient)
        mock_client.session_name = "mock_session"
        mock_client.initialize = AsyncMock()
        mock_client.process_request = AsyncMock(return_value={"status": "completed"})
        mock_client.shutdown = AsyncMock()

        # Verify mock behavior
        assert mock_client.session_name == "mock_session"
        assert asyncio.iscoroutinefunction(mock_client.initialize)
        assert asyncio.iscoroutinefunction(mock_client.process_request)
        assert asyncio.iscoroutinefunction(mock_client.shutdown)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
