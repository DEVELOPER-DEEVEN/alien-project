# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Tasknetwork Editor Module - Command Pattern Implementation

This module provides a command pattern-based editor for Tasknetwork manipulation.
Supports operations for adding/removing nodes/edges, building networks, and
comprehensive CRUD operations with undo/redo capabilities.
"""

from .command_interface import ICommand, IUndoableCommand
from .network_editor import networkEditor
from .commands import (
    AddTaskCommand,
    RemoveTaskCommand,
    UpdateTaskCommand,
    AddDependencyCommand,
    RemoveDependencyCommand,
    UpdateDependencyCommand,
    BuildnetworkCommand,
    ClearnetworkCommand,
    LoadnetworkCommand,
    SavenetworkCommand,
)
from .command_invoker import CommandInvoker
from .command_history import CommandHistory

__all__ = [
    "ICommand",
    "IUndoableCommand",
    "networkEditor",
    "AddTaskCommand",
    "RemoveTaskCommand",
    "UpdateTaskCommand",
    "AddDependencyCommand",
    "RemoveDependencyCommand",
    "UpdateDependencyCommand",
    "BuildnetworkCommand",
    "ClearnetworkCommand",
    "LoadnetworkCommand",
    "SavenetworkCommand",
    "CommandInvoker",
    "CommandHistory",
]
