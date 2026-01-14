
"""
Enumerations for the Task System in Orion V2.

This module defines the core enums used throughout the task orchestration system
for task management, dependency handling, and execution coordination.
"""

from enum import Enum


class TaskStatus(Enum):
    """
    Represents the status of a task in the orion.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_DEPENDENCY = "waiting_dependency"


class DependencyType(Enum):
    """
    Types of dependencies between tasks.
    """

    UNCONDITIONAL = "unconditional"  # Unconditional dependency, executes once prerequisite task completes
    CONDITIONAL = (
        "conditional"  # Conditional dependency, requires specific conditions to be met
    )
    SUCCESS_ONLY = "success_only"  # Executes only when prerequisite task succeeds
    COMPLETION_ONLY = "completion_only"  # Executes when prerequisite task completes, regardless of success or failure


class OrionState(Enum):
    """
    State of the entire task orion.
    """

    CREATED = "created"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_FAILED = "partially_failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """
    Priority levels for task execution.
    """

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class DeviceType(Enum):
    """
    Supported device types in the orion.
    """

    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    API = "api"
