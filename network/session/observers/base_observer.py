
"""
Base observer classes for orion progress and session metrics.
"""

import logging
from typing import Any, Dict, Optional

from ...agents.orion_agent import OrionAgent
from ...core.events import (
    OrionEvent,
    Event,
    EventType,
    IEventObserver,
    TaskEvent,
)
from ...visualization.change_detector import VisualizationChangeDetector


class OrionProgressObserver(IEventObserver):
    """
    Observer that handles orion progress updates.

    This replaces the complex callback logic in NetworkRound.
    """

    def __init__(self, agent: OrionAgent):
        """
        Initialize OrionProgressObserver.

        :param agent: OrionAgent instance for task coordination
        """
        self.agent = agent
        self.task_results: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    async def on_event(self, event: Event) -> None:
        """
        Handle orion-related events.

        :param event: Event instance to handle (TaskEvent or OrionEvent)
        """
        if isinstance(event, TaskEvent):
            await self._handle_task_event(event)
        elif isinstance(event, OrionEvent):
            await self._handle_orion_event(event)

    async def _handle_task_event(self, event: TaskEvent) -> None:
        """
        Handle task progress events and queue them for agent processing.

        :param event: TaskEvent instance containing task status updates
        """
        try:
            self.logger.info(
                f"Task progress: {event.task_id} -> {event.status}. Event Type: {event.event_type}"
            )

            # Store task result
            self.task_results[event.task_id] = {
                "task_id": event.task_id,
                "status": event.status,
                "result": event.result,
                "error": event.error,
                "timestamp": event.timestamp,
            }

            # Put event into agent's queue - this will wake up the Continue state
            if event.event_type in [EventType.TASK_COMPLETED, EventType.TASK_FAILED]:
                await self.agent.add_task_completion_event(event)

        except AttributeError as e:
            self.logger.error(
                f"Attribute error handling task event: {e}", exc_info=True
            )
        except KeyError as e:
            self.logger.error(f"Missing key in task event: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(
                f"Unexpected error handling task event: {e}", exc_info=True
            )

    async def _handle_orion_event(self, event: OrionEvent) -> None:
        """
        Handle orion update events - now handled by agent state machine.

        :param event: OrionEvent instance containing orion updates
        """
        try:
            if event.event_type == EventType.ORION_COMPLETED:
                await self.agent.add_orion_completion_event(event)

        except AttributeError as e:
            self.logger.error(
                f"Attribute error handling orion event: {e}", exc_info=True
            )
        except Exception as e:
            self.logger.error(
                f"Unexpected error handling orion event: {e}", exc_info=True
            )


class SessionMetricsObserver(IEventObserver):
    """
    Observer that collects session metrics and statistics.
    """

    def __init__(self, session_id: str, logger: Optional[logging.Logger] = None):
        """
        Initialize SessionMetricsObserver.

        :param session_id: Unique session identifier for metrics tracking
        :param logger: Optional logger instance (creates default if None)
        """
        self.metrics: Dict[str, Any] = {
            "session_id": session_id,
            "task_count": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_execution_time": 0.0,
            "task_timings": {},
            "orion_count": 0,
            "completed_orions": 0,
            "failed_orions": 0,
            "total_orion_time": 0.0,
            "orion_timings": {},
            "orion_modifications": {},  # Track modifications per orion
        }
        self.logger = logger or logging.getLogger(__name__)

    async def on_event(self, event: Event) -> None:
        """
        Collect metrics from events.

        :param event: Event instance for metrics collection
        """
        if isinstance(event, TaskEvent):
            await self._handle_task_event(event)
        elif isinstance(event, OrionEvent):
            await self._handle_orion_event(event)

    async def _handle_task_event(self, event: TaskEvent) -> None:
        """
        Handle task-related events for metrics collection.

        :param event: TaskEvent instance
        """
        if event.event_type == EventType.TASK_STARTED:
            self._handle_task_started(event)
        elif event.event_type == EventType.TASK_COMPLETED:
            self._handle_task_completed(event)
        elif event.event_type == EventType.TASK_FAILED:
            self._handle_task_failed(event)

    async def _handle_orion_event(self, event: OrionEvent) -> None:
        """
        Handle orion-related events for metrics collection.

        :param event: OrionEvent instance
        """
        if event.event_type == EventType.ORION_STARTED:
            self._handle_orion_started(event)
        elif event.event_type == EventType.ORION_COMPLETED:
            self._handle_orion_completed(event)
        elif event.event_type == EventType.ORION_MODIFIED:
            self._handle_orion_modified(event)

    def _handle_task_started(self, event: TaskEvent) -> None:
        """
        Handle TASK_STARTED event.

        :param event: TaskEvent instance
        """
        self.metrics["task_count"] += 1
        self.metrics["task_timings"][event.task_id] = {"start": event.timestamp}

    def _handle_task_completed(self, event: TaskEvent) -> None:
        """
        Handle TASK_COMPLETED event.

        :param event: TaskEvent instance
        """
        self.metrics["completed_tasks"] += 1

        if event.task_id in self.metrics["task_timings"]:
            duration = (
                event.timestamp - self.metrics["task_timings"][event.task_id]["start"]
            )
            self.metrics["task_timings"][event.task_id]["duration"] = duration
            self.metrics["task_timings"][event.task_id]["end"] = event.timestamp
            self.metrics["total_execution_time"] += duration

    def _handle_task_failed(self, event: TaskEvent) -> None:
        """
        Handle TASK_FAILED event.

        :param event: TaskEvent instance
        """
        self.metrics["failed_tasks"] += 1
        if event.task_id in self.metrics["task_timings"]:
            duration = (
                event.timestamp - self.metrics["task_timings"][event.task_id]["start"]
            )
            self.metrics["task_timings"][event.task_id]["duration"] = duration
            self.metrics["total_execution_time"] += duration
            self.metrics["task_timings"][event.task_id]["end"] = event.timestamp

    def _handle_orion_started(self, event: OrionEvent) -> None:
        """
        Handle ORION_STARTED event.

        :param event: OrionEvent instance
        """
        self.metrics["orion_count"] += 1
        orion_id = event.orion_id

        # Extract orion from event data
        orion = event.data.get("orion")

        # Store initial orion statistics
        self.metrics["orion_timings"][orion_id] = {
            "start_time": event.timestamp,
            "initial_statistics": (
                orion.get_statistics() if orion else {}
            ),
            "processing_start_time": event.data.get("processing_start_time"),
            "processing_end_time": event.data.get("processing_end_time"),
            "processing_duration": event.data.get("processing_duration"),
        }

    def _handle_orion_completed(self, event: OrionEvent) -> None:
        """
        Handle ORION_COMPLETED event.

        :param event: OrionEvent instance
        """
        self.metrics["completed_orions"] += 1
        orion_id = event.orion_id
        orion = event.data.get("orion")

        duration = (
            event.timestamp
            - self.metrics["orion_timings"][orion_id]["start_time"]
            if orion_id in self.metrics["orion_timings"]
            else None
        )

        # Store final orion statistics
        if orion_id in self.metrics["orion_timings"]:
            self.metrics["orion_timings"][orion_id].update(
                {
                    "end_time": event.timestamp,
                    "duration": duration,
                    "final_statistics": (
                        orion.get_statistics() if orion else {}
                    ),
                }
            )

    def _handle_orion_modified(self, event: OrionEvent) -> None:
        """
        Handle ORION_MODIFIED event.

        :param event: OrionEvent instance
        """
        orion_id = event.orion_id

        # Initialize modifications list for this orion if needed
        if orion_id not in self.metrics["orion_modifications"]:
            self.metrics["orion_modifications"][orion_id] = []

        # Extract old and new orions from event data
        if hasattr(event, "data") and event.data:
            old_orion = event.data.get("old_orion")
            new_orion = event.data.get("new_orion")

            # Calculate changes using VisualizationChangeDetector
            changes = None
            if old_orion and new_orion:
                changes = VisualizationChangeDetector.calculate_orion_changes(
                    old_orion, new_orion
                )

            # Get new orion statistics
            new_statistics = (
                new_orion.get_statistics() if new_orion else {}
            )

            # Store modification record
            modification_record = {
                "timestamp": event.timestamp,
                "modification_type": event.data.get("modification_type", "unknown"),
                "on_task_id": event.data.get("on_task_id", []),
                "changes": changes,
                "new_statistics": new_statistics,
                "processing_start_time": event.data.get("processing_start_time"),
                "processing_end_time": event.data.get("processing_end_time"),
                "processing_duration": event.data.get("processing_duration"),
            }

            self.metrics["orion_modifications"][orion_id].append(
                modification_record
            )

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get collected metrics with computed statistics.

        :return: Dictionary containing session metrics and computed statistics
        """
        metrics = self.metrics.copy()

        # Compute task statistics
        task_stats = self._compute_task_statistics()
        metrics["task_statistics"] = task_stats

        # Compute orion statistics
        orion_stats = self._compute_orion_statistics()
        metrics["orion_statistics"] = orion_stats

        # Compute modification statistics
        modification_stats = self._compute_modification_statistics()
        metrics["modification_statistics"] = modification_stats

        return metrics

    def _compute_task_statistics(self) -> Dict[str, Any]:
        """
        Compute task-related statistics.

        :return: Dictionary containing computed task statistics
        """
        task_timings = self.metrics.get("task_timings", {})

        # Collect all task durations
        durations = [
            timing["duration"]
            for timing in task_timings.values()
            if "duration" in timing
        ]

        return {
            "total_tasks": self.metrics.get("task_count", 0),
            "completed_tasks": self.metrics.get("completed_tasks", 0),
            "failed_tasks": self.metrics.get("failed_tasks", 0),
            "success_rate": (
                self.metrics.get("completed_tasks", 0)
                / self.metrics.get("task_count", 1)
                if self.metrics.get("task_count", 0) > 0
                else 0.0
            ),
            "failure_rate": (
                self.metrics.get("failed_tasks", 0) / self.metrics.get("task_count", 1)
                if self.metrics.get("task_count", 0) > 0
                else 0.0
            ),
            "average_task_duration": (
                sum(durations) / len(durations) if durations else 0.0
            ),
            "min_task_duration": min(durations) if durations else 0.0,
            "max_task_duration": max(durations) if durations else 0.0,
            "total_task_execution_time": self.metrics.get("total_execution_time", 0.0),
        }

    def _compute_orion_statistics(self) -> Dict[str, Any]:
        """
        Compute orion-related statistics.

        :return: Dictionary containing computed orion statistics
        """
        orion_timings = self.metrics.get("orion_timings", {})

        # Collect all orion durations
        durations = [
            timing["duration"]
            for timing in orion_timings.values()
            if "duration" in timing and timing["duration"] is not None
        ]

        # Calculate average tasks per orion
        total_tasks_in_orions = 0
        orion_count = 0

        for timing in orion_timings.values():
            initial_stats = timing.get("initial_statistics", {})
            if "total_tasks" in initial_stats:
                total_tasks_in_orions += initial_stats["total_tasks"]
                orion_count += 1

        return {
            "total_orions": self.metrics.get("orion_count", 0),
            "completed_orions": self.metrics.get("completed_orions", 0),
            "failed_orions": self.metrics.get("failed_orions", 0),
            "success_rate": (
                self.metrics.get("completed_orions", 0)
                / self.metrics.get("orion_count", 1)
                if self.metrics.get("orion_count", 0) > 0
                else 0.0
            ),
            "average_orion_duration": (
                sum(durations) / len(durations) if durations else 0.0
            ),
            "min_orion_duration": min(durations) if durations else 0.0,
            "max_orion_duration": max(durations) if durations else 0.0,
            "total_orion_time": self.metrics.get(
                "total_orion_time", 0.0
            ),
            "average_tasks_per_orion": (
                total_tasks_in_orions / orion_count
                if orion_count > 0
                else 0.0
            ),
        }

    def _compute_modification_statistics(self) -> Dict[str, Any]:
        """
        Compute orion modification statistics.

        :return: Dictionary containing computed modification statistics
        """
        modifications = self.metrics.get("orion_modifications", {})

        # Total modifications across all orions
        total_modifications = sum(len(mods) for mods in modifications.values())

        # Modifications per orion
        modifications_per_orion = {
            const_id: len(mods) for const_id, mods in modifications.items()
        }

        # Average modifications per orion
        avg_modifications = (
            total_modifications / len(modifications) if modifications else 0.0
        )

        # Find most modified orion
        most_modified_orion = None
        max_modifications = 0
        if modifications_per_orion:
            most_modified_orion = max(
                modifications_per_orion.items(), key=lambda x: x[1]
            )
            max_modifications = most_modified_orion[1]
            most_modified_orion = most_modified_orion[0]

        # Collect modification types
        modification_types = {}
        for const_mods in modifications.values():
            for mod in const_mods:
                mod_type = mod.get("modification_type", "unknown")
                modification_types[mod_type] = modification_types.get(mod_type, 0) + 1

        return {
            "total_modifications": total_modifications,
            "orions_modified": len(modifications),
            "average_modifications_per_orion": avg_modifications,
            "max_modifications_for_single_orion": max_modifications,
            "most_modified_orion": most_modified_orion,
            "modifications_per_orion": modifications_per_orion,
            "modification_types_breakdown": modification_types,
        }
