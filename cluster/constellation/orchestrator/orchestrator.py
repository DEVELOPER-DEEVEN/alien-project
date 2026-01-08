# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Task Execution Orchestrator for Tasknetwork.

This module provides the execution orchestrator for Tasknetwork,
focused purely on execution flow control and coordination.
Delegates device/state management to networkManager.
"""

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from cluster.client.device_manager import networkDeviceManager

if TYPE_CHECKING:
    from ...session.observers.network_sync_observer import (
        networkModificationSynchronizer,
    )

from ...core.events import networkEvent, EventType, TaskEvent, get_event_bus
from ..enums import TaskStatus
from ..task_network import Tasknetwork
from ..task_star import TaskStar
from .network_manager import networkManager


class TasknetworkOrchestrator:
    """
    Task execution orchestrator focused on flow control and coordination.

    This class provides execution orchestration for Tasknetwork using
    event-driven patterns. It delegates device/state management to
    networkManager.
    """

    def __init__(
        self,
        device_manager: Optional[networkDeviceManager] = None,
        enable_logging: bool = True,
        event_bus=None,
    ):
        """
        Initialize the TasknetworkOrchestrator.

        :param device_manager: Instance of networkDeviceManager
        :param enable_logging: Whether to enable logging
        :param event_bus: Event bus for publishing events
        """
        self._device_manager = device_manager
        self._network_manager = networkManager(
            device_manager, enable_logging
        )
        self._logger = logging.getLogger(__name__) if enable_logging else None

        # Initialize event bus for publishing events
        if event_bus is None:

            self._event_bus = get_event_bus()
        else:
            self._event_bus = event_bus

        # Track active execution tasks
        self._execution_tasks: Dict[str, asyncio.Task] = {}

        # Cancellation support
        self._cancellation_requested = False
        self._cancelled_networks: Dict[str, bool] = {}

        # Modification synchronizer (will be set by session)
        self._modification_synchronizer: Optional[
            "networkModificationSynchronizer"
        ] = None

    def set_device_manager(self, device_manager: networkDeviceManager) -> None:
        """
        Set the device manager for device communication.

        :param device_manager: The network device manager instance
        """
        self._device_manager = device_manager
        self._network_manager.set_device_manager(device_manager)

    def set_modification_synchronizer(
        self, synchronizer: "networkModificationSynchronizer"
    ) -> None:
        """
        Set the modification synchronizer for coordination.

        :param synchronizer: networkModificationSynchronizer instance
        """
        self._modification_synchronizer = synchronizer
        if self._logger:
            self._logger.info("Modification synchronizer attached to orchestrator")

    async def cancel_execution(self, network_id: str) -> bool:
        """
        Cancel network execution immediately.

        Cancels all running tasks and marks the network for cancellation.

        :param network_id: ID of the network to cancel
        :return: True if cancellation was successful
        """
        if self._logger:
            self._logger.info(
                f"🛑 Cancelling network execution: {network_id}"
            )

        # Mark this network as cancelled
        self._cancellation_requested = True
        self._cancelled_networks[network_id] = True

        # Cancel all running execution tasks
        if self._execution_tasks:
            cancelled_count = 0
            for task_id, task in list(self._execution_tasks.items()):
                if not task.done():
                    if self._logger:
                        self._logger.debug(f"🛑 Cancelling task {task_id}")
                    task.cancel()
                    cancelled_count += 1

            if self._logger:
                self._logger.info(f"🛑 Cancelled {cancelled_count} running tasks")

            # Wait for all cancellations to complete
            await asyncio.gather(
                *self._execution_tasks.values(), return_exceptions=True
            )
            self._execution_tasks.clear()

        if self._logger:
            self._logger.info(
                f"✅ network {network_id} cancellation completed"
            )

        return True

    async def orchestrate_network(
        self,
        network: Tasknetwork,
        device_assignments: Optional[Dict[str, str]] = None,
        assignment_strategy: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate DAG execution using event-driven pattern.

        This is the main entry point that coordinates the entire orchestration workflow.

        :param network: Tasknetwork to orchestrate
        :param device_assignments: Optional manual device assignments
        :param assignment_strategy: Device assignment strategy for auto-assignment
        :param metadata: Optional metadata for orchestration
        :return: Orchestration results and statistics
        """
        # 1. Pre-execution validation and setup
        await self._validate_and_prepare_network(
            network, device_assignments, assignment_strategy
        )

        # 2. Start execution and publish event
        start_event = await self._start_network_execution(
            network, device_assignments, assignment_strategy, metadata
        )

        try:
            # 3. Main execution loop
            await self._run_execution_loop(network)

            # 4. Finalize and publish completion event
            return await self._finalize_network_execution(
                network, start_event
            )

        except ValueError as e:
            await self._handle_orchestration_failure(network, e)
            raise
        except RuntimeError as e:
            await self._handle_orchestration_failure(network, e)
            raise
        except asyncio.CancelledError:
            if self._logger:
                self._logger.info(
                    f"Orchestration cancelled for network {network.network_id}"
                )
            raise
        except Exception as e:
            await self._handle_orchestration_failure(network, e)
            raise

        finally:
            # Cancel all pending tasks before cleanup
            if self._execution_tasks:
                for task_id, task in list(self._execution_tasks.items()):
                    if not task.done():
                        task.cancel()

                # Wait for all cancellations to complete with proper exception handling
                if self._execution_tasks:
                    results = await asyncio.gather(
                        *self._execution_tasks.values(), return_exceptions=True
                    )
                    # Log any unexpected exceptions (non-CancelledError)
                    for i, result in enumerate(results):
                        if isinstance(result, Exception) and not isinstance(
                            result, asyncio.CancelledError
                        ):
                            if self._logger:
                                self._logger.warning(
                                    f"Task cleanup exception: {result}"
                                )

                self._execution_tasks.clear()

            await self._cleanup_network(network)

    # ========================================
    # Private helper methods (extracted from orchestrate_network)
    # ========================================

    async def _validate_and_prepare_network(
        self,
        network: Tasknetwork,
        device_assignments: Optional[Dict[str, str]],
        assignment_strategy: Optional[str] = None,
    ) -> None:
        """
        Validate DAG structure and prepare device assignments.

        :param network: Tasknetwork to validate
        :param device_assignments: Optional manual device assignments
        :param assignment_strategy: Device assignment strategy
        :raises ValueError: If validation fails
        """
        if not self._device_manager:
            raise ValueError(
                "networkDeviceManager not set. Use set_device_manager() first."
            )

        if self._logger:
            self._logger.info(
                f"Starting orchestration of network {network.network_id}"
            )

        # Validate DAG structure
        is_valid, errors = network.validate_dag()
        if not is_valid:
            raise ValueError(f"Invalid DAG: {errors}")

        # Handle device assignments
        await self._assign_devices_to_tasks(
            network, device_assignments, assignment_strategy
        )

        # Validate assignments
        is_valid, errors = (
            self._network_manager.validate_network_assignments(
                network
            )
        )
        if not is_valid:
            raise ValueError(f"Device assignment validation failed: {errors}")

    async def _assign_devices_to_tasks(
        self,
        network: Tasknetwork,
        device_assignments: Optional[Dict[str, str]],
        assignment_strategy: Optional[str] = None,
    ) -> None:
        """
        Assign devices to tasks either manually or automatically.

        :param network: Tasknetwork to assign devices to
        :param device_assignments: Optional manual device assignments
        :param assignment_strategy: Device assignment strategy for auto-assignment
        :raises ValueError: If assignment_strategy is None and tasks have no target_device_id
        """
        if device_assignments:
            # Apply manual assignments
            for task_id, device_id in device_assignments.items():
                self._network_manager.reassign_task_device(
                    network, task_id, device_id
                )
        elif assignment_strategy:
            # Auto-assign devices
            await self._network_manager.assign_devices_automatically(
                network, assignment_strategy
            )
        else:
            # No assignment strategy provided, validate that all tasks have target_device_id
            self._validate_existing_device_assignments(network)

    def _validate_existing_device_assignments(
        self, network: Tasknetwork
    ) -> None:
        """
        Validate that all tasks in network have target_device_id assigned.

        This is called when no device_assignments or assignment_strategy is provided,
        ensuring that tasks already have device assignments.

        :param network: Tasknetwork to validate
        :raises ValueError: If any task is missing target_device_id or device_id is invalid
        """
        tasks_without_device = []
        tasks_with_invalid_device = []

        # Get all registered devices from device manager
        all_devices = self._device_manager.get_all_devices()
        valid_device_ids = set(all_devices.keys())

        for task_id, task in network.tasks.items():
            # Check if target_device_id is None or empty string
            if not task.target_device_id:
                tasks_without_device.append(task_id)
            else:
                # Check if the device_id exists in device manager
                if task.target_device_id not in valid_device_ids:
                    tasks_with_invalid_device.append(
                        f"{task_id} (assigned to unknown device: {task.target_device_id})"
                    )

        # Build error message if there are issues
        error_parts = []
        if tasks_without_device:
            error_parts.append(
                f"Tasks without device assignment: {tasks_without_device}"
            )
        if tasks_with_invalid_device:
            error_parts.append(
                f"Tasks with invalid device IDs: {tasks_with_invalid_device}"
            )

        if error_parts:
            error_msg = (
                f"Device assignment validation failed:\n"
                + "\n".join(f"  - {part}" for part in error_parts)
                + f"\n  Available devices: {list(valid_device_ids)}"
                + "\n  Please provide either 'device_assignments' or 'assignment_strategy' parameter."
            )
            if self._logger:
                self._logger.error(error_msg)
            raise ValueError(error_msg)

        if self._logger:
            self._logger.debug(
                f"All tasks have valid device assignments. "
                f"Total tasks validated: {len(network.tasks)}, "
                f"Available devices: {list(valid_device_ids)}"
            )

    async def _start_network_execution(
        self,
        network: Tasknetwork,
        device_assignments: Optional[Dict[str, str]],
        assignment_strategy: str,
        metadata: Optional[Dict] = None,
    ) -> networkEvent:
        """
        Start network execution and publish started event.

        :param network: Tasknetwork to start
        :param device_assignments: Device assignments used
        :param assignment_strategy: Assignment strategy used
        :param metadata: Optional metadata for orchestration
        :return: The published network started event
        """
        network.start_execution()

        # Create and publish network started event
        start_event = networkEvent(
            event_type=EventType.network_STARTED,
            source_id=f"orchestrator_{id(self)}",
            timestamp=time.time(),
            data={
                "total_tasks": len(network.tasks),
                "assignment_strategy": assignment_strategy,
                "device_assignments": device_assignments or {},
                "network": network,
                **(metadata or {}),  # Unpack metadata into data
            },
            network_id=network.network_id,
            network_state="executing",
        )
        await self._event_bus.publish_event(start_event)

        return start_event

    async def _run_execution_loop(self, network: Tasknetwork) -> None:
        """
        Main execution loop for processing network tasks.

        Continuously processes ready tasks until network is complete.
        Handles dynamic network modifications via synchronizer.

        :param network: Tasknetwork to execute
        """
        while not network.is_complete():
            # Check for cancellation at the beginning of each iteration
            if self._cancellation_requested or self._cancelled_networks.get(
                network.network_id, False
            ):
                if self._logger:
                    self._logger.info(
                        f"🛑 Execution loop cancelled for network {network.network_id}"
                    )
                # Mark network as cancelled
                from ..enums import networkState

                network.state = networkState.CANCELLED
                break

            # Wait for pending modifications and refresh network
            network = await self._sync_network_modifications(network)

            # Validate existing device assignments
            self._validate_existing_device_assignments(network)

            # Get ready tasks and schedule them
            ready_tasks = network.get_ready_tasks()
            await self._schedule_ready_tasks(ready_tasks, network)

            # Wait for task completion
            await self._wait_for_task_completion()

        # Wait for all remaining tasks
        await self._wait_for_all_tasks()

    async def _sync_network_modifications(
        self, network: Tasknetwork
    ) -> Tasknetwork:
        """
        Synchronize pending network modifications.

        Merges structural changes from agent while preserving orchestrator's
        execution state (task statuses, results) to prevent race conditions.

        :param network: Current orchestrator's network
        :return: Updated network with merged state
        """
        if self._logger:
            old_ready = [t.task_id for t in network.get_ready_tasks()]
            self._logger.debug(f"⚠️ Old Ready tasks: {old_ready}")

        if self._modification_synchronizer:
            await self._modification_synchronizer.wait_for_pending_modifications()

            network = (
                self._modification_synchronizer.merge_and_sync_network_states(
                    orchestrator_network=network,
                )
            )

        if self._logger:
            self._logger.debug(
                f"🆕 Task ID for network after editing: {list(network.tasks.keys())}"
            )
            new_ready = [t.task_id for t in network.get_ready_tasks()]
            self._logger.debug(f"🆕 New Ready tasks: {new_ready}")

        return network

    async def _schedule_ready_tasks(
        self, ready_tasks: List[TaskStar], network: Tasknetwork
    ) -> None:
        """
        Schedule ready tasks for execution.

        :param ready_tasks: List of tasks ready to execute
        :param network: Parent network
        """
        for task in ready_tasks:
            if task.task_id not in self._execution_tasks:
                task_future = asyncio.create_task(
                    self._execute_task_with_events(task, network)
                )
                self._execution_tasks[task.task_id] = task_future

    async def _wait_for_task_completion(self) -> None:
        """
        Wait for at least one task to complete and clean up.
        """
        if self._execution_tasks:
            done, _ = await asyncio.wait(
                self._execution_tasks.values(), return_when=asyncio.FIRST_COMPLETED
            )

            # Clean up completed tasks
            await self._cleanup_completed_tasks(done)
        else:
            # No running tasks, wait briefly
            await asyncio.sleep(0.1)

    async def _cleanup_completed_tasks(self, done_futures: set) -> None:
        """
        Clean up completed task futures from tracking.

        :param done_futures: Set of completed task futures
        """
        completed_task_ids = []
        for task_future in done_futures:
            for task_id, future in self._execution_tasks.items():
                if future == task_future:
                    completed_task_ids.append(task_id)
                    break

        for task_id in completed_task_ids:
            del self._execution_tasks[task_id]

    async def _wait_for_all_tasks(self) -> None:
        """Wait for all remaining tasks to complete."""
        if self._execution_tasks:
            try:
                results = await asyncio.gather(
                    *self._execution_tasks.values(), return_exceptions=True
                )
                # Log any unexpected exceptions (non-CancelledError)
                for result in results:
                    if isinstance(result, Exception) and not isinstance(
                        result, asyncio.CancelledError
                    ):
                        if self._logger:
                            self._logger.warning(f"Task wait exception: {result}")
            except asyncio.CancelledError:
                # Gracefully handle cancellation during shutdown
                if self._logger:
                    self._logger.debug("Task gathering cancelled during shutdown")
                # Re-raise to propagate cancellation
                raise
            finally:
                self._execution_tasks.clear()

    async def _finalize_network_execution(
        self, network: Tasknetwork, start_event: networkEvent
    ) -> Dict[str, Any]:
        """
        Finalize network execution and publish completion event.

        :param network: Completed network
        :param start_event: The original start event for timing
        :return: Orchestration results and statistics
        """
        network.complete_execution()

        # Publish network completed event
        completion_event = networkEvent(
            event_type=EventType.network_COMPLETED,
            source_id=f"orchestrator_{id(self)}",
            timestamp=time.time(),
            data={
                "total_tasks": len(network.tasks),
                "statistics": network.get_statistics(),
                "execution_duration": time.time() - start_event.timestamp,
                "network": network,
            },
            network_id=network.network_id,
            network_state="completed",
        )
        await self._event_bus.publish_event(completion_event)

        if self._logger:
            self._logger.info(
                f"Completed orchestration of network {network.network_id}"
            )

        # Note: results is initialized as {} in original code
        results = {}
        return {
            "results": results,
            "status": "completed",
            "total_tasks": len(results),
            "statistics": network.get_statistics(),
        }

    async def _handle_orchestration_failure(
        self, network: Tasknetwork, error: Exception
    ) -> None:
        """
        Handle orchestration failure.

        :param network: Failed network
        :param error: The exception that caused the failure
        """
        network.complete_execution()
        if self._logger:
            self._logger.error(f"Orchestration failed: {error}")

    async def _cleanup_network(self, network: Tasknetwork) -> None:
        """
        Clean up network resources.

        :param network: network to clean up
        """
        self._network_manager.unregister_network(
            network.network_id
        )

    async def _execute_task_with_events(
        self,
        task: TaskStar,
        network: Tasknetwork,
    ) -> None:
        """
        Execute a single task and publish events.

        :param task: The TaskStar to execute
        :param network: The parent Tasknetwork
        :return: Task execution result
        """
        try:
            # Import event classes

            # Publish task started event
            start_event = TaskEvent(
                event_type=EventType.TASK_STARTED,
                source_id=f"orchestrator_{id(self)}",
                timestamp=time.time(),
                data={"network_id": network.network_id},
                task_id=task.task_id,
                status=TaskStatus.RUNNING.value,
            )
            await self._event_bus.publish_event(start_event)

            task.start_execution()

            # Execute the task
            result = await task.execute(self._device_manager)

            is_success = result.status == TaskStatus.COMPLETED.value

            self._logger.info(
                f"Task {task.task_id} execution result: {result}, is_success: {is_success}"
            )

            # Mark task as completed in network
            newly_ready = network.mark_task_completed(
                task.task_id, success=is_success, result=result
            )

            # Publish task completed event
            completed_event = TaskEvent(
                event_type=(
                    EventType.TASK_COMPLETED if is_success else EventType.TASK_FAILED
                ),
                source_id=f"orchestrator_{id(self)}",
                timestamp=time.time(),
                data={
                    "network_id": network.network_id,
                    "newly_ready_tasks": [t.task_id for t in newly_ready],
                    "network": network,
                },
                task_id=task.task_id,
                status=result.status,
                result=result,
            )
            await self._event_bus.publish_event(completed_event)

            self._logger.debug(
                f"Task {task.task_id} is marked as completed. Completed tasks ids: {[t.task_id for t in network.get_completed_tasks()]}"
            )

            if self._logger:
                self._logger.info(f"Task {task.task_id} completed successfully")

        except Exception as e:
            # Mark task as failed in network
            newly_ready = network.mark_task_completed(
                task.task_id, success=False, error=e
            )

            # Publish task failed event

            failed_event = TaskEvent(
                event_type=EventType.TASK_FAILED,
                source_id=f"orchestrator_{id(self)}",
                timestamp=time.time(),
                data={
                    "network_id": network.network_id,
                    "newly_ready_tasks": [t.task_id for t in newly_ready],
                },
                task_id=task.task_id,
                status=TaskStatus.FAILED.value,
                error=e,
            )
            await self._event_bus.publish_event(failed_event)

            if self._logger:
                self._logger.error(f"Task {task.task_id} failed: {e}")
            raise

        return result

    async def execute_single_task(
        self,
        task: TaskStar,
        target_device_id: Optional[str] = None,
    ) -> Any:
        """
        Execute a single task on a specific device.

        :param task: TaskStar to execute
        :param target_device_id: Optional target device ID
        :return: Task execution result
        """
        if target_device_id:
            task.target_device_id = target_device_id

        if not task.target_device_id:
            # Use network manager to auto-assign device
            available_devices = (
                await self._network_manager.get_available_devices()
            )
            if not available_devices:
                raise ValueError("No available devices for task execution")
            task.target_device_id = available_devices[0]["device_id"]

        # Execute task directly using TaskStar.execute
        result = await task.execute(self._device_manager)
        return result.result

    async def get_network_status(
        self, network: Tasknetwork
    ) -> Dict[str, Any]:
        """
        Get detailed status of a network using networkManager.

        :param network: Tasknetwork to check
        :return: Status information
        """
        return await self._network_manager.get_network_status(
            network.network_id
        )

    async def get_available_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of available devices from networkManager.

        :return: List of available device information
        """
        return await self._network_manager.get_available_devices()

    async def assign_devices_automatically(
        self,
        network: Tasknetwork,
        strategy: str = "round_robin",
        device_preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Automatically assign devices to tasks using networkManager.

        :param network: Tasknetwork to assign devices to
        :param strategy: Assignment strategy
        :param device_preferences: Optional device preferences by task ID
        :return: Dictionary mapping task IDs to assigned device IDs
        """
        return await self._network_manager.assign_devices_automatically(
            network, strategy, device_preferences
        )
