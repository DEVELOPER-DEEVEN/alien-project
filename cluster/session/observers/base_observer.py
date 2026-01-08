# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Base observer classes for network progress and session metrics.
"""

import logging
from typing import Any, Dict, Optional

from ...agents.network_agent import networkAgent
from ...core.events import (
    networkEvent,
    Event,
    EventType,
    IEventObserver,
    TaskEvent,
)
from ...visualization.change_detector import VisualizationChangeDetector


class networkProgressObserver(IEventObserver):
    """
    Observer that handles network progress updates.

    This replaces the complex callback logic in clusterRound.
    """

    def __init__(self, agent: networkAgent):
        """
        Initialize networkProgressObserver.

        :param agent: networkAgent instance for task coordination
        """
        self.agent = agent
        self.task_results: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    async def on_event(self, event: Event) -> None:
        """
        Handle network-related events.

        :param event: Event instance to handle (TaskEvent or networkEvent)
        """
        if isinstance(event, TaskEvent):
            await self._handle_task_event(event)
        elif isinstance(event, networkEvent):
            await self._handle_network_event(event)

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

    async def _handle_network_event(self, event: networkEvent) -> None:
        """
        Handle network update events - now handled by agent state machine.

        :param event: networkEvent instance containing network updates
        """
        try:
            if event.event_type == EventType.network_COMPLETED:
                await self.agent.add_network_completion_event(event)

        except AttributeError as e:
            self.logger.error(
                f"Attribute error handling network event: {e}", exc_info=True
            )
        except Exception as e:
            self.logger.error(
                f"Unexpected error handling network event: {e}", exc_info=True
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
            "network_count": 0,
            "completed_networks": 0,
            "failed_networks": 0,
            "total_network_time": 0.0,
            "network_timings": {},
            "network_modifications": {},  # Track modifications per network
        }
        self.logger = logger or logging.getLogger(__name__)

    async def on_event(self, event: Event) -> None:
        """
        Collect metrics from events.

        :param event: Event instance for metrics collection
        """
        if isinstance(event, TaskEvent):
            await self._handle_task_event(event)
        elif isinstance(event, networkEvent):
            await self._handle_network_event(event)

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

    async def _handle_network_event(self, event: networkEvent) -> None:
        """
        Handle network-related events for metrics collection.

        :param event: networkEvent instance
        """
        if event.event_type == EventType.network_STARTED:
            self._handle_network_started(event)
        elif event.event_type == EventType.network_COMPLETED:
            self._handle_network_completed(event)
        elif event.event_type == EventType.network_MODIFIED:
            self._handle_network_modified(event)

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

    def _handle_network_started(self, event: networkEvent) -> None:
        """
        Handle network_STARTED event.

        :param event: networkEvent instance
        """
        self.metrics["network_count"] += 1
        network_id = event.network_id

        # Extract network from event data
        network = event.data.get("network")

        # Store initial network statistics
        self.metrics["network_timings"][network_id] = {
            "start_time": event.timestamp,
            "initial_statistics": (
                network.get_statistics() if network else {}
            ),
            "processing_start_time": event.data.get("processing_start_time"),
            "processing_end_time": event.data.get("processing_end_time"),
            "processing_duration": event.data.get("processing_duration"),
        }

    def _handle_network_completed(self, event: networkEvent) -> None:
        """
        Handle network_COMPLETED event.

        :param event: networkEvent instance
        """
        self.metrics["completed_networks"] += 1
        network_id = event.network_id
        network = event.data.get("network")

        duration = (
            event.timestamp
            - self.metrics["network_timings"][network_id]["start_time"]
            if network_id in self.metrics["network_timings"]
            else None
        )

        # Store final network statistics
        if network_id in self.metrics["network_timings"]:
            self.metrics["network_timings"][network_id].update(
                {
                    "end_time": event.timestamp,
                    "duration": duration,
                    "final_statistics": (
                        network.get_statistics() if network else {}
                    ),
                }
            )

    def _handle_network_modified(self, event: networkEvent) -> None:
        """
        Handle network_MODIFIED event.

        :param event: networkEvent instance
        """
        network_id = event.network_id

        # Initialize modifications list for this network if needed
        if network_id not in self.metrics["network_modifications"]:
            self.metrics["network_modifications"][network_id] = []

        # Extract old and new networks from event data
        if hasattr(event, "data") and event.data:
            old_network = event.data.get("old_network")
            new_network = event.data.get("new_network")

            # Calculate changes using VisualizationChangeDetector
            changes = None
            if old_network and new_network:
                changes = VisualizationChangeDetector.calculate_network_changes(
                    old_network, new_network
                )

            # Get new network statistics
            new_statistics = (
                new_network.get_statistics() if new_network else {}
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

            self.metrics["network_modifications"][network_id].append(
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

        # Compute network statistics
        network_stats = self._compute_network_statistics()
        metrics["network_statistics"] = network_stats

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

    def _compute_network_statistics(self) -> Dict[str, Any]:
        """
        Compute network-related statistics.

        :return: Dictionary containing computed network statistics
        """
        network_timings = self.metrics.get("network_timings", {})

        # Collect all network durations
        durations = [
            timing["duration"]
            for timing in network_timings.values()
            if "duration" in timing and timing["duration"] is not None
        ]

        # Calculate average tasks per network
        total_tasks_in_networks = 0
        network_count = 0

        for timing in network_timings.values():
            initial_stats = timing.get("initial_statistics", {})
            if "total_tasks" in initial_stats:
                total_tasks_in_networks += initial_stats["total_tasks"]
                network_count += 1

        return {
            "total_networks": self.metrics.get("network_count", 0),
            "completed_networks": self.metrics.get("completed_networks", 0),
            "failed_networks": self.metrics.get("failed_networks", 0),
            "success_rate": (
                self.metrics.get("completed_networks", 0)
                / self.metrics.get("network_count", 1)
                if self.metrics.get("network_count", 0) > 0
                else 0.0
            ),
            "average_network_duration": (
                sum(durations) / len(durations) if durations else 0.0
            ),
            "min_network_duration": min(durations) if durations else 0.0,
            "max_network_duration": max(durations) if durations else 0.0,
            "total_network_time": self.metrics.get(
                "total_network_time", 0.0
            ),
            "average_tasks_per_network": (
                total_tasks_in_networks / network_count
                if network_count > 0
                else 0.0
            ),
        }

    def _compute_modification_statistics(self) -> Dict[str, Any]:
        """
        Compute network modification statistics.

        :return: Dictionary containing computed modification statistics
        """
        modifications = self.metrics.get("network_modifications", {})

        # Total modifications across all networks
        total_modifications = sum(len(mods) for mods in modifications.values())

        # Modifications per network
        modifications_per_network = {
            const_id: len(mods) for const_id, mods in modifications.items()
        }

        # Average modifications per network
        avg_modifications = (
            total_modifications / len(modifications) if modifications else 0.0
        )

        # Find most modified network
        most_modified_network = None
        max_modifications = 0
        if modifications_per_network:
            most_modified_network = max(
                modifications_per_network.items(), key=lambda x: x[1]
            )
            max_modifications = most_modified_network[1]
            most_modified_network = most_modified_network[0]

        # Collect modification types
        modification_types = {}
        for const_mods in modifications.values():
            for mod in const_mods:
                mod_type = mod.get("modification_type", "unknown")
                modification_types[mod_type] = modification_types.get(mod_type, 0) + 1

        return {
            "total_modifications": total_modifications,
            "networks_modified": len(modifications),
            "average_modifications_per_network": avg_modifications,
            "max_modifications_for_single_network": max_modifications,
            "most_modified_network": most_modified_network,
            "modifications_per_network": modifications_per_network,
            "modification_types_breakdown": modification_types,
        }
