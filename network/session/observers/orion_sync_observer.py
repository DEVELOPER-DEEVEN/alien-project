
"""
Orion Modification Synchronizer Observer

This observer ensures proper synchronization between task completion and
orion modifications. It prevents race conditions where the orchestrator
might execute newly ready tasks before the OrionAgent finishes updating
the orion.

Synchronization Flow:
1. Task completes → TASK_COMPLETED event published
2. This observer registers the task_id as "pending modification"
3. Agent processes modification → ORION_MODIFIED event published
4. This observer marks the modification as complete
5. Orchestrator waits for all pending modifications before proceeding

Example:
    >>> synchronizer = OrionModificationSynchronizer(orchestrator, logger)
    >>> event_bus.subscribe(synchronizer)
    >>> # In orchestrator loop:
    >>> await synchronizer.wait_for_pending_modifications()
    >>> ready_tasks = orion.get_ready_tasks()
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Dict, Optional

from network.orion.task_orion import TaskOrion

from ...core.events import (
    OrionEvent,
    Event,
    EventType,
    IEventObserver,
    TaskEvent,
)

if TYPE_CHECKING:
    from ...orion.orchestrator.orchestrator import TaskOrionOrchestrator


class OrionModificationSynchronizer(IEventObserver):
    """
    Observer that synchronizes orion modifications with orchestrator execution.

    This observer solves the race condition where:
    - Task A completes → triggers orion update
    - Orchestrator immediately gets ready tasks → might execute Task B
    - Agent's process_editing() is still modifying Task B or its dependencies

    The synchronizer ensures orchestrator waits for modifications to complete
    before executing newly ready tasks.
    """

    def __init__(
        self,
        orchestrator: "TaskOrionOrchestrator",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize OrionModificationSynchronizer.

        :param orchestrator: TaskOrionOrchestrator instance to synchronize with
        :param logger: Optional logger instance (creates default if None)
        """
        self.orchestrator = orchestrator
        self.logger = logger or logging.getLogger(__name__)

        # Track pending modifications: task_id -> Future
        self._pending_modifications: Dict[str, asyncio.Future] = {}

        # Track orion being modified
        self._current_orion_id: Optional[str] = None
        self._current_orion: Optional["TaskOrion"] = None

        # Timeout for modifications (safety measure)
        self._modification_timeout = 600.0  # 600 seconds

        # Statistics for monitoring
        self._stats = {
            "total_modifications": 0,
            "completed_modifications": 0,
            "timeout_modifications": 0,
        }

    async def on_event(self, event: Event) -> None:
        """
        Handle orion-related synchronization events.

        :param event: Event instance to handle (TaskEvent or OrionEvent)
        """
        if isinstance(event, TaskEvent):
            await self._handle_task_event(event)
        elif isinstance(event, OrionEvent):
            await self._handle_orion_event(event)

    async def _handle_task_event(self, event: TaskEvent) -> None:
        """
        Handle task completion/failure events by registering pending modifications.

        :param event: TaskEvent instance containing task status updates
        """
        try:
            # Only care about task completion/failure events
            if event.event_type not in [
                EventType.TASK_COMPLETED,
                EventType.TASK_FAILED,
            ]:
                return

            orion_id = event.data.get("orion_id")
            if not orion_id:
                self.logger.debug(
                    f"Task event {event.task_id} missing orion_id, skipping"
                )
                return

            self._current_orion_id = orion_id

            # Register this task as having a pending modification
            if event.task_id not in self._pending_modifications:
                modification_future = asyncio.Future()
                self._pending_modifications[event.task_id] = modification_future
                self._stats["total_modifications"] += 1

                self.logger.info(
                    f" Registered pending modification for task '{event.task_id}' "
                    f"(orion: {orion_id})"
                )

                # Set timeout to auto-complete if modification takes too long
                asyncio.create_task(
                    self._auto_complete_on_timeout(event.task_id, modification_future)
                )

        except AttributeError as e:
            self.logger.error(
                f"Attribute error handling task event in synchronizer: {e}",
                exc_info=True,
            )
        except KeyError as e:
            self.logger.error(f"Missing key in task event: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(
                f"Unexpected error handling task event in synchronizer: {e}",
                exc_info=True,
            )

    async def _handle_orion_event(self, event: OrionEvent) -> None:
        """
        Handle orion modification events by completing pending modifications.

        :param event: OrionEvent instance containing orion updates
        """
        try:
            # Only care about orion modified events
            if event.event_type not in [
                EventType.ORION_MODIFIED,
                EventType.ORION_STARTED,
            ]:
                return

            if event.event_type == EventType.ORION_STARTED:
                self._current_orion_id = event.orion_id
                self._current_orion = event.data.get("orion")
                return

            task_ids = event.data.get("on_task_id")
            if not task_ids:
                self.logger.warning(
                    "ORION_MODIFIED event missing 'on_task_id' field"
                )
                return

            new_orion = event.data.get("new_orion")

            if new_orion:
                self._current_orion = new_orion

                self.logger.info(
                    f"[CONTINUE] Updated orion reference for '{event.orion_id}'"
                )

            # Mark the modification as complete
            for task_id in task_ids:
                if task_id in self._pending_modifications:
                    future = self._pending_modifications[task_id]
                    if not future.done():
                        future.set_result(True)
                        self._stats["completed_modifications"] += 1
                        self.logger.info(
                            f"[OK] Completed modification for task '{task_id}' "
                            f"(orion: {event.orion_id})"
                        )
                    del self._pending_modifications[task_id]
                else:
                    self.logger.debug(
                        f"Received ORION_MODIFIED for task '{task_id}' "
                        f"but no pending modification was registered"
                    )

        except AttributeError as e:
            self.logger.error(
                f"Attribute error handling orion event in synchronizer: {e}",
                exc_info=True,
            )
        except KeyError as e:
            self.logger.error(f"Missing key in orion event: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(
                f"Unexpected error handling orion event in synchronizer: {e}",
                exc_info=True,
            )

    async def _auto_complete_on_timeout(
        self, task_id: str, future: asyncio.Future
    ) -> None:
        """
        Auto-complete a pending modification if it times out.

        :param task_id: ID of the task with pending modification
        :param future: Future to complete on timeout
        """
        try:
            await asyncio.sleep(self._modification_timeout)

            if not future.done():
                self._stats["timeout_modifications"] += 1
                self.logger.warning(
                    f"️ Modification for task '{task_id}' timed out after "
                    f"{self._modification_timeout}s. Auto-completing to prevent deadlock."
                )
                future.set_result(False)
                if task_id in self._pending_modifications:
                    del self._pending_modifications[task_id]
        except asyncio.CancelledError:
            self.logger.debug(f"Auto-complete timeout cancelled for task '{task_id}'")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error in auto-complete timeout handler: {e}", exc_info=True
            )

    async def wait_for_pending_modifications(
        self, timeout: Optional[float] = None
    ) -> bool:
        """
        Wait for all pending modifications to complete.

        This method should be called by the orchestrator before getting ready tasks.
        Handles dynamically added pending modifications during the wait.

        :param timeout: Optional timeout in seconds (uses default if None)
        :return: True if all modifications completed, False if timeout occurred
        """
        if not self._pending_modifications:
            return True

        timeout = timeout or self._modification_timeout
        start_time = asyncio.get_event_loop().time()

        self.logger.info(
            f"⏳ Starting wait for pending modifications (timeout: {timeout}s)"
        )

        try:
            while self._pending_modifications:
                # Get current pending tasks (snapshot)
                pending_tasks = list(self._pending_modifications.keys())
                pending_futures = list(self._pending_modifications.values())

                self.logger.info(
                    f"⏳ Waiting for {len(pending_tasks)} pending modification(s): {pending_tasks}"
                )

                # Calculate remaining timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining_timeout = timeout - elapsed

                if remaining_timeout <= 0:
                    raise asyncio.TimeoutError()

                # Wait for all current pending modifications
                await asyncio.wait_for(
                    asyncio.gather(*pending_futures, return_exceptions=True),
                    timeout=remaining_timeout,
                )

                # Check if new modifications were added during the wait
                # If yes, loop again; if no, we're done
                if not self._pending_modifications:
                    break

                # Small delay to allow new registrations to settle
                await asyncio.sleep(0.01)

            self.logger.info("[OK] All pending modifications completed")
            return True

        except asyncio.TimeoutError:
            pending = list(self._pending_modifications.keys())
            self.logger.warning(
                f"️ Timeout waiting for modifications after {timeout}s. "
                f"Proceeding anyway. Pending: {pending}"
            )
            # Clear all pending modifications to prevent permanent deadlock
            self._pending_modifications.clear()
            return False

    def get_current_orion(self) -> Optional[TaskOrion]:
        """
        Get the ID of the orion currently being modified.

        :return: Orion or None if not set
        """

        return self._current_orion

    def has_pending_modifications(self) -> bool:
        """
        Check if there are any pending modifications.

        :return: True if modifications are pending, False otherwise
        """
        return len(self._pending_modifications) > 0

    def get_pending_count(self) -> int:
        """
        Get the number of pending modifications.

        :return: Number of tasks with pending modifications
        """
        return len(self._pending_modifications)

    def get_pending_task_ids(self) -> list:
        """
        Get the list of task IDs with pending modifications.

        :return: List of task IDs
        """
        return list(self._pending_modifications.keys())

    def get_statistics(self) -> Dict[str, int]:
        """
        Get synchronization statistics.

        :return: Dictionary containing stats like total, completed, timeout counts
        """
        return self._stats.copy()

    def clear_pending_modifications(self) -> None:
        """
        Clear all pending modifications (emergency use only).

        This should only be used in error recovery scenarios.
        """
        count = len(self._pending_modifications)
        if count > 0:
            self.logger.warning(
                f"️ Forcefully clearing {count} pending modification(s)"
            )

            # Complete all pending futures
            for task_id, future in self._pending_modifications.items():
                if not future.done():
                    future.set_result(False)

            self._pending_modifications.clear()

    def set_modification_timeout(self, timeout: float) -> None:
        """
        Set the modification timeout value.

        :param timeout: Timeout in seconds
        """
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        self._modification_timeout = timeout
        self.logger.info(f"Modification timeout set to {timeout}s")

    def merge_and_sync_orion_states(
        self,
        orchestrator_orion: TaskOrion,
    ) -> TaskOrion:
        """
        Merge orion states: structural changes from agent + execution state from orchestrator.

        This prevents race conditions where:
        - Orchestrator marks Task A as COMPLETED
        - Agent modifies orion (Task A still RUNNING in agent's copy)
        - Direct replacement would lose Task A's COMPLETED status

        Uses self._current_orion as the agent's orion with structural changes.

        :param orchestrator_orion: Orchestrator's orion with execution state
        :return: Merged orion
        """
        if not self._current_orion:
            if self.logger:
                self.logger.warning(
                    "️ No agent orion available, returning orchestrator orion"
                )
            return orchestrator_orion

        if self.logger:
            self.logger.info("[CONTINUE] Merging orion states...")

        # Use agent's orion as base (has structural modifications)
        merged = self._current_orion

        # Preserve execution state from orchestrator for existing tasks
        for task_id, orchestrator_task in orchestrator_orion.tasks.items():
            if task_id in merged.tasks:
                agent_task = merged.tasks[task_id]

                # [OK] Key: If orchestrator's task state is more advanced, preserve it
                # State priority: COMPLETED/FAILED > RUNNING > WAITING_DEPENDENCY > PENDING
                if self._is_state_more_advanced(
                    orchestrator_task.status, agent_task.status
                ):
                    if self.logger:
                        self.logger.debug(
                            f"   Preserving advanced state for task '{task_id}': "
                            f"{orchestrator_task.status} (orchestrator) vs "
                            f"{agent_task.status} (agent)"
                        )

                    # Preserve orchestrator's state and results
                    agent_task._status = orchestrator_task.status
                    agent_task._result = orchestrator_task.result
                    agent_task._error = orchestrator_task.error
                    agent_task._execution_start_time = (
                        orchestrator_task.execution_start_time
                    )
                    agent_task._execution_end_time = (
                        orchestrator_task.execution_end_time
                    )

        # Update orion state
        merged.update_state()

        # Sync the current orion reference
        self._current_orion = merged

        if self.logger:
            self.logger.info("[OK] Orion states merged successfully")

        return merged

    def _is_state_more_advanced(self, state1, state2) -> bool:
        """
        Check if state1 is more advanced than state2 in execution progression.

        Progression: PENDING -> WAITING_DEPENDENCY -> RUNNING -> COMPLETED/FAILED

        :param state1: First task status (TaskStatus)
        :param state2: Second task status (TaskStatus)
        :return: True if state1 is more advanced
        """
        from ...orion.enums import TaskStatus

        # Define state advancement levels
        state_levels = {
            TaskStatus.PENDING: 0,
            TaskStatus.WAITING_DEPENDENCY: 1,
            TaskStatus.RUNNING: 2,
            TaskStatus.COMPLETED: 3,
            TaskStatus.FAILED: 3,  # Terminal states are equally advanced
            TaskStatus.CANCELLED: 3,
        }

        level1 = state_levels.get(state1, 0)
        level2 = state_levels.get(state2, 0)

        return level1 > level2
