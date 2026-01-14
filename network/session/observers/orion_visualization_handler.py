
"""
Orion-specific visualization handler.
"""

import logging
from typing import Optional

from network.visualization.dag_visualizer import DAGVisualizer

from ...orion import TaskOrion
from ...core.events import OrionEvent, EventType
from ...visualization import OrionDisplay, VisualizationChangeDetector


class OrionVisualizationHandler:
    """
    Specialized handler for orion-related visualization events.

    This class routes orion events to appropriate display components,
    delegating actual visualization to specialized display classes.
    """

    def __init__(
        self, visualizer: DAGVisualizer, logger: Optional[logging.Logger] = None
    ):
        """
        Initialize OrionVisualizationHandler.

        :param visualizer: DAGVisualizer instance for complex displays
        :param logger: Optional logger instance
        """
        self._visualizer = visualizer
        self.orion_display = OrionDisplay(visualizer.console)
        self.logger = logger or logging.getLogger(__name__)

    async def handle_orion_started(
        self, event: OrionEvent, orion: Optional[TaskOrion]
    ) -> None:
        """
        Handle orion start visualization.

        :param event: OrionEvent instance
        :param orion: TaskOrion instance if available
        """
        if not orion:
            return

        try:
            # Extract additional info from event
            additional_info = {}
            if event.data:
                additional_info = {k: v for k, v in event.data.items() if v is not None}

            # Use orion display for start notification
            self.orion_display.display_orion_started(
                orion, additional_info
            )

            # Show initial topology using DAGVisualizer
            self._visualizer.display_dag_topology(orion)
        except Exception as e:
            self.logger.debug(f"Error displaying orion start: {e}")

    async def handle_orion_completed(
        self, event: OrionEvent, orion: Optional[TaskOrion]
    ) -> None:
        """
        Handle orion completion visualization.

        :param event: OrionEvent instance
        :param orion: TaskOrion instance if available
        """
        if not orion:
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

            # Use orion display for completion notification
            self.orion_display.display_orion_completed(
                orion, execution_time, additional_info
            )
        except Exception as e:
            self.logger.debug(f"Error displaying orion completion: {e}")

    async def handle_orion_failed(
        self, event: OrionEvent, orion: Optional[TaskOrion]
    ) -> None:
        """
        Handle orion failure visualization.

        :param event: OrionEvent instance
        :param orion: TaskOrion instance if available
        """
        if not orion:
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

            # Use orion display for failure notification
            self.orion_display.display_orion_failed(
                orion, error, additional_info
            )
        except Exception as e:
            self.logger.debug(f"Error displaying orion failure: {e}")

    async def handle_orion_modified(
        self, event: OrionEvent, orion: Optional[TaskOrion]
    ) -> None:
        """
        Handle orion modification visualization with enhanced display.

        :param event: OrionEvent instance
        :param orion: TaskOrion instance if available
        """
        try:
            if not orion:
                return

            # Get old and new orions from event data
            old_orion = None
            new_orion = orion

            if event.data:
                old_orion = event.data.get("old_orion")
                if "new_orion" in event.data:
                    new_orion = event.data["new_orion"]
                elif "updated_orion" in event.data:
                    new_orion = event.data["updated_orion"]

            # Calculate changes using specialized detector
            changes = VisualizationChangeDetector.calculate_orion_changes(
                old_orion, new_orion
            )

            # Extract additional info from event
            additional_info = {}
            if event.data:
                excluded_keys = {
                    "old_orion",
                    "new_orion",
                    "updated_orion",
                    "processing_start_time",
                    "processing_end_time",
                    "processing_duration",
                }
                additional_info = {
                    k: v
                    for k, v in event.data.items()
                    if k not in excluded_keys and v is not None
                }

            # Use orion display for modification notification
            self.orion_display.display_orion_modified(
                new_orion, changes, additional_info
            )

            # Show updated topology using DAGVisualizer
            self._visualizer.display_dag_topology(new_orion)

        except Exception as e:
            self.logger.debug(f"Error displaying orion modification: {e}")

    async def handle_orion_event(
        self, event: OrionEvent, orion: Optional[TaskOrion]
    ) -> None:
        """
        Route orion events to appropriate handlers.

        :param event: OrionEvent instance
        :param orion: TaskOrion instance if available
        """
        if event.event_type == EventType.ORION_STARTED:
            await self.handle_orion_started(event, orion)
        elif event.event_type == EventType.ORION_COMPLETED:
            await self.handle_orion_completed(event, orion)
        elif event.event_type == EventType.ORION_FAILED:
            await self.handle_orion_failed(event, orion)
        elif event.event_type == EventType.ORION_MODIFIED:
            await self.handle_orion_modified(event, orion)
