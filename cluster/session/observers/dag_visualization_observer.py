# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Main DAG visualization observer with delegated handlers.
"""

import logging
from typing import Dict, Optional

from cluster.visualization.dag_visualizer import DAGVisualizer

from ...network import Tasknetwork
from ...core.events import networkEvent, Event, IEventObserver, TaskEvent
from .network_visualization_handler import networkVisualizationHandler
from .task_visualization_handler import TaskVisualizationHandler


class DAGVisualizationObserver(IEventObserver):
    """
    Main observer that handles DAG visualization for network events.

    This observer coordinates between specialized handlers for different types
    of visualization events. It maintains network references and delegates
    specific visualization tasks to appropriate handlers.
    """

    def __init__(self, enable_visualization: bool = True, console=None):
        """
        Initialize the DAG visualization observer.

        :param enable_visualization: Whether to enable visualization
        :param console: Optional rich console for output
        """
        self.enable_visualization = enable_visualization
        self.logger = logging.getLogger(__name__)
        self._visualizer = None
        self._console = console

        # Track networks for visualization
        self._networks: Dict[str, Tasknetwork] = {}

        # Initialize specialized handlers
        self._task_handler = None
        self._network_handler = None

        # Initialize visualizer if enabled
        if self.enable_visualization:
            self._init_visualizer()

    def _init_visualizer(self) -> None:
        """
        Initialize the DAG visualizer and handlers.

        Attempts to import and create DAGVisualizer instance,
        disables visualization if import fails.
        """
        try:

            self._visualizer = DAGVisualizer(console=self._console)

            # Initialize specialized handlers
            self._task_handler = TaskVisualizationHandler(self._visualizer, self.logger)
            self._network_handler = networkVisualizationHandler(
                self._visualizer, self.logger
            )

        except ImportError as e:
            self.logger.warning(f"Failed to import DAGVisualizer: {e}")
            self.enable_visualization = False

    async def on_event(self, event: Event) -> None:
        """
        Handle visualization events by delegating to appropriate handlers.

        :param event: Event instance for visualization processing
        """
        if not self.enable_visualization or not self._visualizer:
            return

        try:
            if isinstance(event, networkEvent):
                await self._handle_network_event(event)
            elif isinstance(event, TaskEvent):
                await self._handle_task_event(event)
        except Exception as e:
            self.logger.debug(f"Visualization error: {e}")

    async def _handle_network_event(self, event: networkEvent) -> None:
        """
        Handle network-related visualization events.

        :param event: networkEvent instance for visualization updates
        """
        network_id = event.network_id

        # Get network from event data if available
        network = self._extract_network_from_event(event)

        # Store network reference for future use
        if network:
            self._networks[network_id] = network

        # Delegate to network handler
        if self._network_handler:
            await self._network_handler.handle_network_event(
                event, network
            )

    async def _handle_task_event(self, event: TaskEvent) -> None:
        """
        Handle task-related visualization events.

        :param event: TaskEvent instance for task visualization updates
        """
        network_id = event.data.get("network_id") if event.data else None
        if not network_id:
            return

        # Get network for this task
        network = self._networks.get(network_id)
        if not network:
            return

        # Delegate to task handler
        if self._task_handler:
            await self._task_handler.handle_task_event(event, network)

    def _extract_network_from_event(
        self, event: networkEvent
    ) -> Optional[Tasknetwork]:
        """
        Extract network from event data.

        :param event: networkEvent instance
        :return: Tasknetwork instance if found, None otherwise
        """
        network = None
        if isinstance(event.data, dict):
            network = event.data.get("network")
            if not network and "updated_network" in event.data:
                network = event.data["updated_network"]
            if not network and "new_network" in event.data:
                network = event.data["new_network"]

        return network

    def set_visualization_enabled(self, enabled: bool) -> None:
        """
        Enable or disable visualization.

        :param enabled: Whether to enable visualization
        """
        self.enable_visualization = enabled
        if enabled and not self._visualizer:
            self._init_visualizer()

    def get_network(self, network_id: str) -> Optional[Tasknetwork]:
        """
        Get stored network by ID.

        :param network_id: network identifier
        :return: Tasknetwork instance if found, None otherwise
        """
        return self._networks.get(network_id)

    def register_network(
        self, network_id: str, network: Tasknetwork
    ) -> None:
        """
        Manually register a network for visualization.

        :param network_id: network identifier
        :param network: Tasknetwork instance
        """
        self._networks[network_id] = network

    def clear_networks(self) -> None:
        """
        Clear all stored network references.
        """
        self._networks.clear()
