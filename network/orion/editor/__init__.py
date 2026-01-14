
"""
TaskOrion Editor Module - Command Pattern Implementation

This module provides a command pattern-based editor for TaskOrion manipulation.
Supports operations for adding/removing nodes/edges, building orions, and
comprehensive CRUD operations with undo/redo capabilities.
"""

from .command_interface import ICommand, IUndoableCommand
from .orion_editor import OrionEditor
from .commands import (
    AddTaskCommand,
    RemoveTaskCommand,
    UpdateTaskCommand,
    AddDependencyCommand,
    RemoveDependencyCommand,
    UpdateDependencyCommand,
    BuildOrionCommand,
    ClearOrionCommand,
    LoadOrionCommand,
    SaveOrionCommand,
)
from .command_invoker import CommandInvoker
from .command_history import CommandHistory

__all__ = [
    "ICommand",
    "IUndoableCommand",
    "OrionEditor",
    "AddTaskCommand",
    "RemoveTaskCommand",
    "UpdateTaskCommand",
    "AddDependencyCommand",
    "RemoveDependencyCommand",
    "UpdateDependencyCommand",
    "BuildOrionCommand",
    "ClearOrionCommand",
    "LoadOrionCommand",
    "SaveOrionCommand",
    "CommandInvoker",
    "CommandHistory",
]
