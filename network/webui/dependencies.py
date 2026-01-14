
"""
Dependency management for Network Web UI.

This module manages global state and provides dependency injection
for FastAPI endpoints and WebSocket handlers.
"""

import logging
from typing import TYPE_CHECKING, Optional

from network.webui.websocket_observer import WebSocketObserver

if TYPE_CHECKING:
    from network.network_client import NetworkClient
    from network.session.network_session import NetworkSession


class AppState:
    """
    Application state container.

    Manages global state for the Web UI server including:
    - WebSocket observer for event broadcasting
    - Network session and client instances
    - Request counter for tracking user requests

    This class provides a centralized way to manage shared state
    across the application instead of using global variables.
    """

    def __init__(self) -> None:
        """Initialize the application state with default values."""
        self.logger: logging.Logger = logging.getLogger(__name__)

        # WebSocket observer for broadcasting events to clients
        self._websocket_observer: Optional[WebSocketObserver] = None

        # Network session and client instances
        self._network_session: Optional["NetworkSession"] = None
        self._network_client: Optional["NetworkClient"] = None

        # Counter for generating unique task names in Web UI mode
        self._request_counter: int = 0

    @property
    def websocket_observer(self) -> Optional[WebSocketObserver]:
        """
        Get the WebSocket observer instance.

        :return: WebSocket observer or None if not initialized
        """
        return self._websocket_observer

    @websocket_observer.setter
    def websocket_observer(self, observer: WebSocketObserver) -> None:
        """
        Set the WebSocket observer instance.

        :param observer: WebSocket observer to use for event broadcasting
        """
        self._websocket_observer = observer
        self.logger.info(f"WebSocket observer set: {observer}")

    @property
    def network_session(self) -> Optional["NetworkSession"]:
        """
        Get the current Network session.

        :return: Network session or None if not initialized
        """
        return self._network_session

    @network_session.setter
    def network_session(self, session: "NetworkSession") -> None:
        """
        Set the Network session.

        :param session: Network session instance
        """
        self._network_session = session
        self.logger.info("Network session set")

    @property
    def network_client(self) -> Optional["NetworkClient"]:
        """
        Get the current Network client.

        :return: Network client or None if not initialized
        """
        return self._network_client

    @network_client.setter
    def network_client(self, client: "NetworkClient") -> None:
        """
        Set the Network client.

        :param client: Network client instance
        """
        self._network_client = client
        self.logger.info("Network client set")

    @property
    def request_counter(self) -> int:
        """
        Get the current request counter value.

        :return: Current request counter
        """
        return self._request_counter

    def increment_request_counter(self) -> int:
        """
        Increment and return the request counter.

        :return: New counter value after increment
        """
        self._request_counter += 1
        return self._request_counter

    def reset_request_counter(self) -> None:
        """
        Reset the request counter to zero.

        Called when session is reset or task is stopped.
        """
        self._request_counter = 0
        self.logger.info("Request counter reset to 0")


# Global application state instance
# This is initialized once and shared across the application
app_state = AppState()


def get_app_state() -> AppState:
    """
    Get the application state instance.

    This function can be used as a FastAPI dependency to inject
    the application state into route handlers.

    :return: Application state instance
    """
    return app_state
