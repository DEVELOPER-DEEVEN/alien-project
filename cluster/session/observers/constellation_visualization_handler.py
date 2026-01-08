# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
network-specific visualization handler.
"""

import logging
from typing import Optional

from cluster.visualization.dag_visualizer import DAGVisualizer

from ...network import Tasknetwork
from ...core.events import networkEvent, EventType
from ...visualization import networkDisplay, VisualizationChangeDetector


class networkVisualizationHandler:
    """
    Specialized handler for network-related visualization events.

    This class routes network events to appropriate display components,
    delegating actual visualization to specialized display classes.
    """

    def __init__(
        self, visualizer: DAGVisualizer, logger: Optional[logging.Logger] = None
    ):
        """
        Initialize networkVisualizationHandler.

        :param visualizer: DAGVisualizer instance for complex displays
        :param logger: Optional logger instance
        """
        self._visualizer = visualizer
        self.network_display = networkDisplay(visualizer.console)
        self.logger = logger or logging.getLogger(__name__)

    async def handle_network_started(
        self, event: networkEvent, network: Optional[Tasknetwork]
    ) -> None:
        """
        Handle network start visualization.

        :param event: networkEvent instance
        :param network: Tasknetwork instance if available
        """
        if not network:
            return

        try:
            # Extract additional info from event
            additional_info = {}
            if event.data:
                additional_info = {k: v for k, v in event.data.items() if v is not None}

            # Use network display for start notification
            self.network_display.display_network_started(
                network, additional_info
            )

            # Show initial topology using DAGVisualizer
            self._visualizer.display_dag_topology(network)
        except Exception as e:
            self.logger.debug(f"Error displaying network start: {e}")

    async def handle_network_completed(
        self, event: networkEvent, network: Optional[Tasknetwork]
    ) -> None:
        """
        Handle network completion visualization.

        :param event: networkEvent instance
        :param network: Tasknetwork instance if available
        """
        if not network:
            return

        try:
            # Extract execution time from event
            execution_time = event.data.get("execution_time") if event.data else None
            additional_info = {}
            if event.data:
                additional_info = {
                    k: v
                    for k, v in event.data.items()
                    if k != "execution_time" and v is not None
                }

            # Use network display for completion notification
            self.network_display.display_network_completed(
                network, execution_time, additional_info
            )
        except Exception as e:
            self.logger.debug(f"Error displaying network completion: {e}")

    async def handle_network_failed(
        self, event: networkEvent, network: Optional[Tasknetwork]
    ) -> None:
        """
        Handle network failure visualization.

        :param event: networkEvent instance
        :param network: Tasknetwork instance if available
        """
        if not network:
            return

        try:
            # Extract error from event
            error = event.data.get("error") if event.data else None
            additional_info = {}
            if event.data:
                additional_info = {
                    k: v
                    for k, v in event.data.items()
                    if k != "error" and v is not None
                }

            # Use network display for failure notification
            self.network_display.display_network_failed(
                network, error, additional_info
            )
        except Exception as e:
            self.logger.debug(f"Error displaying network failure: {e}")

    async def handle_network_modified(
        self, event: networkEvent, network: Optional[Tasknetwork]
    ) -> None:
        """
        Handle network modification visualization with enhanced display.

        :param event: networkEvent instance
        :param network: Tasknetwork instance if available
        """
        try:
            if not network:
                return

            # Get old and new networks from event data
            old_network = None
            new_network = network

            if event.data:
                old_network = event.data.get("old_network")
                if "new_network" in event.data:
                    new_network = event.data["new_network"]
                elif "updated_network" in event.data:
                    new_network = event.data["updated_network"]

            # Calculate changes using specialized detector
            changes = VisualizationChangeDetector.calculate_network_changes(
                old_network, new_network
            )

            # Extract additional info from event
            additional_info = {}
            if event.data:
                excluded_keys = {
                    "old_network",
                    "new_network",
                    "updated_network",
                    "processing_start_time",
                    "processing_end_time",
                    "processing_duration",
                }
                additional_info = {
                    k: v
                    for k, v in event.data.items()
                    if k not in excluded_keys and v is not None
                }

            # Use network display for modification notification
            self.network_display.display_network_modified(
                new_network, changes, additional_info
            )

            # Show updated topology using DAGVisualizer
            self._visualizer.display_dag_topology(new_network)

        except Exception as e:
            self.logger.debug(f"Error displaying network modification: {e}")

    async def handle_network_event(
        self, event: networkEvent, network: Optional[Tasknetwork]
    ) -> None:
        """
        Route network events to appropriate handlers.

        :param event: networkEvent instance
        :param network: Tasknetwork instance if available
        """
        if event.event_type == EventType.network_STARTED:
            await self.handle_network_started(event, network)
        elif event.event_type == EventType.network_COMPLETED:
            await self.handle_network_completed(event, network)
        elif event.event_type == EventType.network_FAILED:
            await self.handle_network_failed(event, network)
        elif event.event_type == EventType.network_MODIFIED:
            await self.handle_network_modified(event, network)
