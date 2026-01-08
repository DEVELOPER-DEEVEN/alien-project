# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
cluster Framework Core Interfaces

This module defines the focused interfaces following the Interface Segregation Principle.
Each interface has a single, well-defined responsibility.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .types import (
    AsyncErrorCallback,
    AsyncProgressCallback,
    networkConfiguration,
    networkId,
    networkResult,
    DeviceId,
    ExecutionResult,
    ProcessingContext,
    SessionId,
    TaskConfiguration,
    TaskId,
)


# Core Task Interfaces
class ITask(ABC):
    """Interface for task objects."""

    @property
    @abstractmethod
    def task_id(self) -> TaskId:
        """Get the task ID."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the task name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Get the task description."""
        pass

    @abstractmethod
    async def execute(
        self, context: Optional[ProcessingContext] = None
    ) -> ExecutionResult:
        """
        Execute the task.

        :param context: Optional processing context
        :return: Execution result
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the task configuration.

        :return: True if valid, False otherwise
        """
        pass


class ITaskFactory(ABC):
    """Interface for creating tasks."""

    @abstractmethod
    def create_task(
        self,
        name: str,
        description: str,
        config: Optional[TaskConfiguration] = None,
        **kwargs
    ) -> ITask:
        """
        Create a new task.

        :param name: Task name
        :param description: Task description
        :param config: Optional task configuration
        :param kwargs: Additional task-specific parameters
        :return: Created task
        """
        pass

    @abstractmethod
    def supports_task_type(self, task_type: str) -> bool:
        """
        Check if this factory supports the given task type.

        :param task_type: Type of task to check
        :return: True if supported
        """
        pass


# Dependency Management Interfaces
class IDependency(ABC):
    """Interface for task dependencies."""

    @property
    @abstractmethod
    def source_task_id(self) -> TaskId:
        """Get the source task ID."""
        pass

    @property
    @abstractmethod
    def target_task_id(self) -> TaskId:
        """Get the target task ID."""
        pass

    @property
    @abstractmethod
    def dependency_type(self) -> str:
        """Get the dependency type."""
        pass

    @abstractmethod
    def is_satisfied(self, completed_tasks: List[TaskId]) -> bool:
        """
        Check if this dependency is satisfied.

        :param completed_tasks: List of completed task IDs
        :return: True if dependency is satisfied
        """
        pass


class IDependencyResolver(ABC):
    """Interface for resolving task dependencies."""

    @abstractmethod
    def get_ready_tasks(
        self,
        all_tasks: List[ITask],
        dependencies: List[IDependency],
        completed_tasks: List[TaskId],
    ) -> List[ITask]:
        """
        Get tasks that are ready to execute.

        :param all_tasks: All tasks in the network
        :param dependencies: All dependencies
        :param completed_tasks: List of completed task IDs
        :return: List of ready tasks
        """
        pass

    @abstractmethod
    def validate_dependencies(
        self, tasks: List[ITask], dependencies: List[IDependency]
    ) -> bool:
        """
        Validate that dependencies form a valid DAG.

        :param tasks: All tasks
        :param dependencies: All dependencies
        :return: True if valid DAG
        """
        pass


# network Interfaces
class Inetwork(ABC):
    """Interface for network objects."""

    @property
    @abstractmethod
    def network_id(self) -> networkId:
        """Get the network ID."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the network name."""
        pass

    @property
    @abstractmethod
    def tasks(self) -> Dict[TaskId, ITask]:
        """Get all tasks in the network."""
        pass

    @property
    @abstractmethod
    def dependencies(self) -> List[IDependency]:
        """Get all dependencies in the network."""
        pass

    @abstractmethod
    def add_task(self, task: ITask) -> None:
        """
        Add a task to the network.

        :param task: Task to add
        """
        pass

    @abstractmethod
    def add_dependency(self, dependency: IDependency) -> None:
        """
        Add a dependency to the network.

        :param dependency: Dependency to add
        """
        pass

    @abstractmethod
    def get_ready_tasks(
        self, completed_tasks: Optional[List[TaskId]] = None
    ) -> List[ITask]:
        """
        Get tasks that are ready to execute.

        :param completed_tasks: Optional list of completed task IDs
        :return: List of ready tasks
        """
        pass


class InetworkBuilder(ABC):
    """Interface for building networks."""

    @abstractmethod
    def create_network(self, name: str) -> Inetwork:
        """
        Create a new network.

        :param name: network name
        :return: Created network
        """
        pass

    @abstractmethod
    def add_task(self, network: Inetwork, task: ITask) -> Inetwork:
        """
        Add a task to the network.

        :param network: Target network
        :param task: Task to add
        :return: Updated network
        """
        pass

    @abstractmethod
    def add_dependency(
        self,
        network: Inetwork,
        source_task_id: TaskId,
        target_task_id: TaskId,
        dependency_type: str = "finish_to_start",
    ) -> Inetwork:
        """
        Add a dependency between tasks.

        :param network: Target network
        :param source_task_id: Source task ID
        :param target_task_id: Target task ID
        :param dependency_type: Type of dependency
        :return: Updated network
        """
        pass


# Execution Interfaces
class ITaskExecutor(ABC):
    """Interface for executing individual tasks."""

    @abstractmethod
    async def execute_task(
        self, task: ITask, context: Optional[ProcessingContext] = None
    ) -> ExecutionResult:
        """
        Execute a single task.

        :param task: Task to execute
        :param context: Optional processing context
        :return: Execution result
        """
        pass

    @abstractmethod
    def can_execute(self, task: ITask) -> bool:
        """
        Check if this executor can handle the given task.

        :param task: Task to check
        :return: True if can execute
        """
        pass


class InetworkExecutor(ABC):
    """Interface for executing networks."""

    @abstractmethod
    async def execute_network(
        self,
        network: Inetwork,
        config: Optional[networkConfiguration] = None,
        progress_callback: Optional[AsyncProgressCallback] = None,
        error_callback: Optional[AsyncErrorCallback] = None,
    ) -> networkResult:
        """
        Execute a network.

        :param network: network to execute
        :param config: Optional execution configuration
        :param progress_callback: Optional progress callback
        :param error_callback: Optional error callback
        :return: Execution result
        """
        pass

    @abstractmethod
    async def pause_execution(self, network_id: networkId) -> bool:
        """
        Pause network execution.

        :param network_id: ID of network to pause
        :return: True if paused successfully
        """
        pass

    @abstractmethod
    async def resume_execution(self, network_id: networkId) -> bool:
        """
        Resume network execution.

        :param network_id: ID of network to resume
        :return: True if resumed successfully
        """
        pass

    @abstractmethod
    async def cancel_execution(self, network_id: networkId) -> bool:
        """
        Cancel network execution.

        :param network_id: ID of network to cancel
        :return: True if cancelled successfully
        """
        pass


# Device Management Interfaces
class IDevice(ABC):
    """Interface for device objects."""

    @property
    @abstractmethod
    def device_id(self) -> DeviceId:
        """Get the device ID."""
        pass

    @property
    @abstractmethod
    def device_type(self) -> str:
        """Get the device type."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Get the device capabilities."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if device is connected."""
        pass

    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the device.

        :return: True if connection successful
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the device.

        :return: True if disconnection successful
        """
        pass

    @abstractmethod
    async def execute_task(self, task: ITask) -> ExecutionResult:
        """
        Execute a task on this device.

        :param task: Task to execute
        :return: Execution result
        """
        pass


class IDeviceRegistry(ABC):
    """Interface for device registry."""

    @abstractmethod
    async def register_device(self, device: IDevice) -> bool:
        """
        Register a device.

        :param device: Device to register
        :return: True if registration successful
        """
        pass

    @abstractmethod
    async def unregister_device(self, device_id: DeviceId) -> bool:
        """
        Unregister a device.

        :param device_id: ID of device to unregister
        :return: True if unregistration successful
        """
        pass

    @abstractmethod
    async def get_device(self, device_id: DeviceId) -> Optional[IDevice]:
        """
        Get a device by ID.

        :param device_id: Device ID
        :return: Device if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_available_devices(
        self, capabilities: Optional[List[str]] = None
    ) -> List[IDevice]:
        """
        Get available devices, optionally filtered by capabilities.

        :param capabilities: Optional capability filter
        :return: List of available devices
        """
        pass


class IDeviceSelector(ABC):
    """Interface for device selection strategies."""

    @abstractmethod
    async def select_device(
        self,
        task: ITask,
        available_devices: List[IDevice],
        context: Optional[ProcessingContext] = None,
    ) -> Optional[IDevice]:
        """
        Select the best device for a task.

        :param task: Task to execute
        :param available_devices: List of available devices
        :param context: Optional processing context
        :return: Selected device or None if no suitable device
        """
        pass


# Agent Interfaces
class IRequestProcessor(ABC):
    """Interface for processing user requests."""

    @abstractmethod
    async def process_creation(
        self, context: Optional[ProcessingContext] = None
    ) -> "Inetwork":
        """
        Process a user request into a network.

        :param context: Optional processing context
        :return: Generated network
        """
        pass


class IResultProcessor(ABC):
    """Interface for processing task results."""

    @abstractmethod
    async def process_editing(
        self,
        context: Optional[ProcessingContext] = None,
    ) -> "Inetwork":
        """
        Process a task result and potentially update the network.

        :param context: Optional processing context
        :return: Updated network
        """
        pass


class InetworkUpdater(ABC):
    """Interface for updating networks based on results."""

    @abstractmethod
    async def should_update(
        self, result: ExecutionResult, network: Inetwork
    ) -> bool:
        """
        Determine if network should be updated based on result.

        :param result: Task execution result
        :param network: Current network
        :return: True if update needed
        """
        pass

    @abstractmethod
    async def update_network(
        self,
        result: ExecutionResult,
        network: Inetwork,
        context: Optional[ProcessingContext] = None,
    ) -> Inetwork:
        """
        Update network based on task result.

        :param result: Task execution result
        :param network: Current network
        :param context: Optional processing context
        :return: Updated network
        """
        pass


# Session Management Interfaces
class ISessionManager(ABC):
    """Interface for session management."""

    @abstractmethod
    async def create_session(
        self,
        session_id: SessionId,
        initial_request: str,
        context: Optional[ProcessingContext] = None,
    ) -> "ISession":
        """
        Create a new session.

        :param session_id: Session ID
        :param initial_request: Initial user request
        :param context: Optional processing context
        :return: Created session
        """
        pass

    @abstractmethod
    async def get_session(self, session_id: SessionId) -> Optional["ISession"]:
        """
        Get an existing session.

        :param session_id: Session ID
        :return: Session if found, None otherwise
        """
        pass

    @abstractmethod
    async def end_session(self, session_id: SessionId) -> bool:
        """
        End a session.

        :param session_id: Session ID
        :return: True if session ended successfully
        """
        pass


class ISession(ABC):
    """Interface for session objects."""

    @property
    @abstractmethod
    def session_id(self) -> SessionId:
        """Get the session ID."""
        pass

    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Check if session is active."""
        pass

    @abstractmethod
    async def process_request(self, request: str) -> networkResult:
        """
        Process a user request in this session.

        :param request: User request
        :return: network execution result
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current session status.

        :return: Status dictionary
        """
        pass


# Monitoring and Observability Interfaces
class IMetricsCollector(ABC):
    """Interface for collecting metrics."""

    @abstractmethod
    def record_task_execution(self, result: ExecutionResult) -> None:
        """
        Record a task execution result.

        :param result: Task execution result
        """
        pass

    @abstractmethod
    def record_network_execution(self, result: networkResult) -> None:
        """
        Record a network execution result.

        :param result: network execution result
        """
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get collected metrics.

        :return: Metrics dictionary
        """
        pass


class IEventLogger(ABC):
    """Interface for event logging."""

    @abstractmethod
    def log_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        context: Optional[ProcessingContext] = None,
    ) -> None:
        """
        Log an event.

        :param event_type: Type of event
        :param event_data: Event data
        :param context: Optional processing context
        """
        pass

    @abstractmethod
    def get_events(
        self, event_type: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get logged events.

        :param event_type: Optional event type filter
        :param limit: Optional limit on number of events
        :return: List of events
        """
        pass
