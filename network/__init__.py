
"""
ALIEN Network Framework

A comprehensive framework for DAG-based task orchestration and device management.

This package provides:
- Orion: DAG management and execution
- Agents: Task orchestration agents (NetworkWeaverAgent)
- Session: Network session management
- Client: Device management and coordination
"""

# Core orion components
from .orion import (
    TaskOrionOrchestrator,
    TaskOrion,
    TaskStar,
    TaskStarLine,
    TaskStatus,
    DependencyType,
    OrionState,
    DeviceType,
    TaskPriority,
    OrionManager,
)

# Agent components
from .agents import OrionAgent

# Session components
from .session import NetworkSession

# Client entry points
from .network_client import NetworkClient

__all__ = [
    # Orion
    "TaskOrionOrchestrator",
    "TaskOrion",
    "TaskStar",
    "TaskStarLine",
    "TaskStatus",
    "DependencyType",
    "OrionState",
    "DeviceType",
    "TaskPriority",
    "OrionManager",
    # Agents
    "OrionAgent",
    # Session
    "NetworkSession",
    # Client
    "NetworkClient",
]
