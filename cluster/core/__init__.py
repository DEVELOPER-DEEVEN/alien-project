# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
cluster Framework Core Package

This package contains the core types, interfaces, and utilities for the cluster framework.
"""

from .types import (
    # Type aliases
    TaskId,
    networkId,
    DeviceId,
    SessionId,
    AgentId,
    ProgressCallback,
    AsyncProgressCallback,
    ErrorCallback,
    AsyncErrorCallback,
    # Result types
    ExecutionResult,
    networkResult,
    # Configuration types
    TaskConfiguration,
    networkConfiguration,
    DeviceConfiguration,
    # Context types
    ProcessingContext,
    # Exception hierarchy
    clusterFrameworkError,
    TaskExecutionError,
    networkError,
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
    # network interfaces
    Inetwork,
    InetworkBuilder,
    # Execution interfaces
    ITaskExecutor,
    InetworkExecutor,
    # Device interfaces
    IDevice,
    IDeviceRegistry,
    IDeviceSelector,
    # Agent interfaces
    IRequestProcessor,
    IResultProcessor,
    InetworkUpdater,
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
    "networkId",
    "DeviceId",
    "SessionId",
    "AgentId",
    "ProgressCallback",
    "AsyncProgressCallback",
    "ErrorCallback",
    "AsyncErrorCallback",
    "ExecutionResult",
    "networkResult",
    "TaskConfiguration",
    "networkConfiguration",
    "DeviceConfiguration",
    "ProcessingContext",
    "Statistics",
    # Exceptions
    "clusterFrameworkError",
    "TaskExecutionError",
    "networkError",
    "DeviceError",
    "ConfigurationError",
    "ValidationError",
    # Interfaces
    "ITask",
    "ITaskFactory",
    "IDependency",
    "IDependencyResolver",
    "Inetwork",
    "InetworkBuilder",
    "ITaskExecutor",
    "InetworkExecutor",
    "IDevice",
    "IDeviceRegistry",
    "IDeviceSelector",
    "IRequestProcessor",
    "IResultProcessor",
    "InetworkUpdater",
    "ISessionManager",
    "ISession",
    "IMetricsCollector",
    "IEventLogger",
]
