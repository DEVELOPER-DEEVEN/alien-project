
"""
Main DAG visualization observer with delegated handlers.
"""

import logging
from typing import Dict, Optional

from network.visualization.dag_visualizer import DAGVisualizer

from ...orion import TaskOrion
from ...core.events import OrionEvent, Event, IEventObserver, TaskEvent
from .orion_visualization_handler import OrionVisualizationHandler
from .task_visualization_handler import TaskVisualizationHandler


class DAGVisualizationObserver(IEventObserver):
    """
    Main observer that handles DAG visualization for orion events.

    This observer coordinates between specialized handlers for different types
    of visualization events. It maintains orion references and delegates
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

        # Track orions for visualization
        self._orions: Dict[str, TaskOrion] = {}

        # Initialize specialized handlers
        self._task_handler = None
        self._orion_handler = None

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
            self._orion_handler = OrionVisualizationHandler(
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
            if isinstance(event, OrionEvent):
                await self._handle_orion_event(event)
            elif isinstance(event, TaskEvent):
                await self._handle_task_event(event)
        except Exception as e:
            self.logger.debug(f"Visualization error: {e}")

    async def _handle_orion_event(self, event: OrionEvent) -> None:
        """
        Handle orion-related visualization events.

        :param event: OrionEvent instance for visualization updates
        """
        orion_id = event.orion_id

        # Get orion from event data if available
        orion = self._extract_orion_from_event(event)

        # Store orion reference for future use
        if orion:
            self._orions[orion_id] = orion

        # Delegate to orion handler
        if self._orion_handler:
            await self._orion_handler.handle_orion_event(
                event, orion
            )

    async def _handle_task_event(self, event: TaskEvent) -> None:
        """
        Handle task-related visualization events.

        :param event: TaskEvent instance for task visualization updates
        """
        orion_id = event.data.get("orion_id") if event.data else None
        if not orion_id:
            return

        # Get orion for this task
        orion = self._orions.get(orion_id)
        if not orion:
            return

        # Delegate to task handler
        if self._task_handler:
            await self._task_handler.handle_task_event(event, orion)

    def _extract_orion_from_event(
        self, event: OrionEvent
    ) -> Optional[TaskOrion]:
        """
        Extract orion from event data.

        :param event: OrionEvent instance
        :return: TaskOrion instance if found, None otherwise
        """
        orion = None
        if isinstance(event.data, dict):
            orion = event.data.get("orion")
            if not orion and "updated_orion" in event.data:
                orion = event.data["updated_orion"]
            if not orion and "new_orion" in event.data:
                orion = event.data["new_orion"]

        return orion

    def set_visualization_enabled(self, enabled: bool) -> None:
        """
        Enable or disable visualization.

        :param enabled: Whether to enable visualization
        """
        self.enable_visualization = enabled
        if enabled and not self._visualizer:
            self._init_visualizer()

    def get_orion(self, orion_id: str) -> Optional[TaskOrion]:
        """
        Get stored orion by ID.

        :param orion_id: Orion identifier
        :return: TaskOrion instance if found, None otherwise
        """
        return self._orions.get(orion_id)

    def register_orion(
        self, orion_id: str, orion: TaskOrion
    ) -> None:
        """
        Manually register a orion for visualization.

        :param orion_id: Orion identifier
        :param orion: TaskOrion instance
        """
        self._orions[orion_id] = orion

    def clear_orions(self) -> None:
        """
        Clear all stored orion references.
        """
        self._orions.clear()
