
"""
Tests for NetworkClient with proper interface usage.

This test module verifies that NetworkClient works correctly with the updated
NetworkSession interface and provides proper functionality for both interactive
and batch modes.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from pathlib import Path
import json

from network.network_client import NetworkClient
from network.client.orion_client import OrionClient
from network.session.network_session import NetworkSession


class TestNetworkClient:
    """Test suite for NetworkClient functionality."""

    @pytest.fixture
    def mock_orion_client(self):
        """Create a mock OrionClient."""
        mock_client = MagicMock(spec=OrionClient)
        mock_client.device_manager = MagicMock()
        mock_client.initialize = AsyncMock()
        mock_client.shutdown = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_network_session(self):
        """Create a mock NetworkSession."""
        mock_session = MagicMock(spec=NetworkSession)
        mock_session.task = "test_task"
        mock_session._rounds = {}
        mock_session.run = AsyncMock()
        mock_session.force_finish = AsyncMock()
        mock_session._current_orion = None
        mock_session.log_path = "test/path"
        return mock_session

    def test_network_client_initialization(self):
        """Test NetworkClient initialization."""
        # Test default initialization
        client = NetworkClient()
        assert client.session_name.startswith("network_session_")
        assert client.max_rounds == 10
        assert client.output_dir == Path("./logs")

        # Test custom initialization
        custom_client = NetworkClient(
            session_name="custom_session",
            max_rounds=20,
            log_level="DEBUG",
            output_dir="/custom/output",
        )
        assert custom_client.session_name == "custom_session"
        assert custom_client.max_rounds == 20
        assert custom_client.output_dir == Path("/custom/output")

    @pytest.mark.asyncio
    async def test_network_client_initialize(
        self, mock_orion_client, mock_network_session
    ):
        """Test NetworkClient initialize method."""
        client = NetworkClient(session_name="test_session")

        with patch(
            "alien.network.network_client.OrionClient",
            return_value=mock_orion_client,
        ), patch(
            "alien.network.network_client.NetworkSession", return_value=mock_network_session
        ):
            await client.initialize()

            # Verify initialization
            assert client._client == mock_orion_client
            assert client._session == mock_network_session
            mock_orion_client.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_request(
        self, mock_orion_client, mock_network_session
    ):
        """Test processing a single request."""
        client = NetworkClient(session_name="test_session")
        client._client = mock_orion_client
        client._session = mock_network_session

        # Mock orion for result testing
        mock_orion = MagicMock()
        mock_orion.orion_id = "test_orion"
        mock_orion.name = "Test Orion"
        mock_orion.tasks = ["task1", "task2"]
        mock_orion.dependencies = []
        mock_orion.state = MagicMock()
        mock_orion.state.value = "completed"
        mock_network_session._current_orion = mock_orion

        result = await client.process_request("Create a test workflow", "test_task")

        # Verify request processing
        assert result["status"] == "completed"
        assert result["request"] == "Create a test workflow"
        assert result["task_name"] == "test_task"
        assert "execution_time" in result
        assert result["orion"]["name"] == "Test Orion"
        mock_network_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_request_failure(
        self, mock_orion_client, mock_network_session
    ):
        """Test processing request with failure."""
        client = NetworkClient(session_name="test_session")
        client._client = mock_orion_client
        client._session = mock_network_session

        # Mock session run to raise an exception
        mock_network_session.run.side_effect = Exception("Test error")

        result = await client.process_request("Failing request")

        # Verify error handling
        assert result["status"] == "failed"
        assert result["error"] == "Test error"
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_shutdown(self, mock_orion_client, mock_network_session):
        """Test Network client shutdown."""
        client = NetworkClient(session_name="test_session")
        client._client = mock_orion_client
        client._session = mock_network_session

        await client.shutdown()

        # Verify shutdown calls
        mock_orion_client.shutdown.assert_called_once()
        mock_network_session.force_finish.assert_called_once_with("Client shutdown")

    @pytest.mark.asyncio
    async def test_interactive_mode_commands(
        self, mock_orion_client, mock_network_session
    ):
        """Test interactive mode command handling."""
        client = NetworkClient(session_name="test_session")
        client._client = mock_orion_client
        client._session = mock_network_session

        # Mock user inputs
        user_inputs = ["help", "status", "quit"]

        with patch.object(client.display, "get_user_input", side_effect=user_inputs):
            await client.interactive_mode()

        # Verify that interactive mode processed commands without errors
        # (This is a basic test - in practice you'd mock more display methods)

    def test_display_integration(self):
        """Test that client properly integrates with ClientDisplay."""
        client = NetworkClient(session_name="test_session")

        # Verify display manager is initialized
        assert client.display is not None
        assert hasattr(client.display, "show_network_banner")
        assert hasattr(client.display, "display_result")
        assert hasattr(client.display, "show_status")

    @pytest.mark.asyncio
    async def test_network_session_interface_compatibility(
        self, mock_orion_client
    ):
        """Test that NetworkClient uses the correct NetworkSession interface."""
        client = NetworkClient(session_name="test_session")

        with patch(
            "alien.network.network_client.OrionClient",
            return_value=mock_orion_client,
        ):
            # Mock NetworkSession constructor to verify correct parameters
            with patch("alien.network.network_client.NetworkSession") as mock_session_class:
                mock_session = MagicMock()
                mock_session_class.return_value = mock_session

                await client.initialize()

                # Verify NetworkSession is called with correct parameters
                mock_session_class.assert_called_once_with(
                    task="test_session",
                    should_evaluate=False,
                    id="test_session",
                    client=mock_orion_client,
                    initial_request="",
                )

    def test_status_display_integration(self):
        """Test status display functionality."""
        client = NetworkClient(session_name="test_session")

        # Test status display without session
        client._show_status()

        # Test status display with mock session
        mock_session = MagicMock()
        mock_session._rounds = {"round1": {}}
        client._session = mock_session

        client._show_status()


@pytest.mark.asyncio
class TestNetworkClientIntegration:
    """Integration tests for NetworkClient."""

    async def test_full_workflow_simulation(self):
        """Test a complete workflow simulation using mocks."""
        # Create client
        client = NetworkClient(session_name="integration_test")

        # Mock all external dependencies
        with patch(
            "alien.network.network_client.OrionClient"
        ) as mock_client_class, patch(
            "alien.network.network_client.NetworkSession"
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
            mock_session._current_orion = None
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


class TestNetworkClientMockImplementation:
    """Test mock implementation for testing purposes."""

    def test_mock_creation(self):
        """Test creating a mock NetworkClient for testing."""
        # Create mock client for use in other tests
        mock_client = MagicMock(spec=NetworkClient)
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
