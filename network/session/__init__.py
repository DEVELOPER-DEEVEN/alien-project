
"""
Network Session Package

This package contains session implementations for the Network framework,
including the NetworkSession for DAG-based task orchestration sessions
and event-driven observers for monitoring and visualization.
"""

from .network_session import NetworkSession

# Import observers from the new modular structure
from .observers import (
    OrionProgressObserver,
    SessionMetricsObserver,
    DAGVisualizationObserver,
)

__all__ = [
    "NetworkSession",
    "OrionProgressObserver",
    "SessionMetricsObserver",
    "DAGVisualizationObserver",
]
