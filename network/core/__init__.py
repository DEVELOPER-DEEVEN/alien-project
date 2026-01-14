
"""
Network Framework Core Package

This package contains the core types, interfaces, and utilities for the Network framework.
"""

from .types import (
    # Type aliases
    TaskId,
    OrionId,
    DeviceId,
    SessionId,
    AgentId,
    ProgressCallback,
    AsyncProgressCallback,
    ErrorCallback,
    AsyncErrorCallback,
    # Result types
    ExecutionResult,
    OrionResult,
    # Configuration types
    TaskConfiguration,
    OrionConfiguration,
    DeviceConfiguration,
    # Context types
    ProcessingContext,
    # Exception hierarchy
    NetworkFrameworkError,
    TaskExecutionError,
    OrionError,
    DeviceError,
    ConfigurationError,
    ValidationError,
    # Utility types
    Statistics,
)

from .interfaces import (
    # Task interfaces
    ITask,
    ITaskFactory,
    # Dependency interfaces
    IDependency,
    IDependencyResolver,
    # Orion interfaces
    IOrion,
    IOrionBuilder,
    # Execution interfaces
    ITaskExecutor,
    IOrionExecutor,
    # Device interfaces
    IDevice,
    IDeviceRegistry,
    IDeviceSelector,
    # Agent interfaces
    IRequestProcessor,
    IResultProcessor,
    IOrionUpdater,
    # Session interfaces
    ISessionManager,
    ISession,
    # Monitoring interfaces
    IMetricsCollector,
    IEventLogger,
)

__all__ = [
    # Types
    "TaskId",
    "OrionId",
    "DeviceId",
    "SessionId",
    "AgentId",
    "ProgressCallback",
    "AsyncProgressCallback",
    "ErrorCallback",
    "AsyncErrorCallback",
    "ExecutionResult",
    "OrionResult",
    "TaskConfiguration",
    "OrionConfiguration",
    "DeviceConfiguration",
    "ProcessingContext",
    "Statistics",
    # Exceptions
    "NetworkFrameworkError",
    "TaskExecutionError",
    "OrionError",
    "DeviceError",
    "ConfigurationError",
    "ValidationError",
    # Interfaces
    "ITask",
    "ITaskFactory",
    "IDependency",
    "IDependencyResolver",
    "IOrion",
    "IOrionBuilder",
    "ITaskExecutor",
    "IOrionExecutor",
    "IDevice",
    "IDeviceRegistry",
    "IDeviceSelector",
    "IRequestProcessor",
    "IResultProcessor",
    "IOrionUpdater",
    "ISessionManager",
    "ISession",
    "IMetricsCollector",
    "IEventLogger",
]
