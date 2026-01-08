#!/usr/bin/env python3
"""
Comprehensive example demonstrating all the updated features of the
network Editor with:

1. Serializable command parameters ( [Text Cleaned] )
2. Command registry with decorators ( [Text Cleaned] )
3. Automatic validation with rollback ( [Text Cleaned] )
"""

import sys
import os

# Add the Alien-Unis directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
Alien_path = os.path.dirname(current_dir)
sys.path.insert(0, Alien_path)

from cluster.network.editor.network_editor import networkEditor
from cluster.network.editor.command_registry import command_registry
from cluster.network.task_network import Tasknetwork


def demo_serializable_parameters():
    """ [Text Cleaned] """
    print("=== 1.  [Text Cleaned]  (Serializable Parameters) ===")

    network = Tasknetwork()
    editor = networkEditor(network)

    print("\n [Text Cleaned] :")

    task1_data = {
        "task_id": "serialize_task1",
        "name": " [Text Cleaned] 1",
        "description": " [Text Cleaned] ",
        "priority": 3,  # HIGH priority
    }

    task2_data = {
        "task_id": "serialize_task2",
        "name": " [Text Cleaned] 2",
        "description": " [Text Cleaned] ",
    }

    task1 = editor.add_task(task1_data)
    task2 = editor.add_task(task2_data)

    print(f"   ✓  [Text Cleaned] 1: {task1.task_id} - {task1.name}")
    print(f"   ✓  [Text Cleaned] 2: {task2.task_id} - {task2.name}")

    print("\n [Text Cleaned] :")

    dependency_data = {
        "from_task_id": "serialize_task1",
        "to_task_id": "serialize_task2",
        "dependency_type": "unconditional",
    }

    dependency = editor.add_dependency(dependency_data)
    print(f"   ✓  [Text Cleaned] : {dependency.from_task_id} -> {dependency.to_task_id}")

    return editor


def demo_command_registry():
    """ [Text Cleaned] """
    print("\n=== 2.  [Text Cleaned]  (Command Registry & Decorators) ===")

    network = Tasknetwork()
    editor = networkEditor(network)

    print("\n [Text Cleaned] :")
    commands = editor.list_available_commands()
    for name, metadata in commands.items():
        print(f"   • {name}: {metadata['description']}")
        print(f"      [Text Cleaned] : {metadata['category']},  [Text Cleaned] : {metadata['is_undoable']}")

    print("\n [Text Cleaned] :")
    for category in editor.get_command_categories():
        category_commands = editor.list_available_commands(category)
        print(f"   {category}:")
        for name in category_commands.keys():
            print(f"     - {name}")

    print("\n [Text Cleaned] :")

    task_data = {
        "task_id": "registry_demo_task",
        "name": " [Text Cleaned] ",
        "description": " [Text Cleaned] ",
    }

    result = editor.execute_command_by_name("add_task", task_data)
    print(f"   ✓  [Text Cleaned] : {result.task_id}")

    metadata = editor.get_command_metadata("add_task")
    print(f"   add_task  [Text Cleaned] : {metadata}")

    return editor


def demo_validation_rollback():
    """ [Text Cleaned] """
    print("\n=== 3.  [Text Cleaned]  (Automatic Validation & Rollback) ===")

    network = Tasknetwork()
    editor = networkEditor(network)

    print("\n [Text Cleaned] :")

    valid_tasks = [
        {
            "task_id": "valid_task_A",
            "name": " [Text Cleaned] A",
            "description": " [Text Cleaned] ",
        },
        {
            "task_id": "valid_task_B",
            "name": " [Text Cleaned] B",
            "description": " [Text Cleaned] ",
        },
    ]

    for task_data in valid_tasks:
        task = editor.add_task(task_data)
        print(f"   ✓  [Text Cleaned] : {task.task_id}")

    print(
        f"\n [Text Cleaned] : {len(network.tasks)}  [Text Cleaned] , {len(network.dependencies)}  [Text Cleaned] "
    )
    is_valid, errors = network.validate_dag()
    print(f"    [Text Cleaned] : {' [Text Cleaned] ' if is_valid else ' [Text Cleaned] '}")

    print("\n [Text Cleaned]  ( [Text Cleaned] ):")
    try:
        invalid_dependency = {
            "from_task_id": "valid_task_A",
            "to_task_id": "nonexistent_task",            "dependency_type": "unconditional",
        }

        editor.add_dependency(invalid_dependency)
        print("   ✗  [Text Cleaned] ")
    except Exception as e:
        print(f"   ✓  [Text Cleaned] : {e}")

    print(
        f"\n [Text Cleaned] : {len(network.tasks)}  [Text Cleaned] , {len(network.dependencies)}  [Text Cleaned] "
    )
    is_valid, errors = network.validate_dag()
    print(f"    [Text Cleaned] : {' [Text Cleaned] ' if is_valid else ' [Text Cleaned] '}")

    print("\n [Text Cleaned] :")
    try:
        valid_dependency = {
            "from_task_id": "valid_task_A",
            "to_task_id": "valid_task_B",
            "dependency_type": "unconditional",
        }

        dependency = editor.add_dependency(valid_dependency)
        print(f"   ✓  [Text Cleaned] : {dependency.from_task_id} -> {dependency.to_task_id}")
    except Exception as e:
        print(f"   ✗  [Text Cleaned] : {e}")

    print(
        f"\n [Text Cleaned] : {len(network.tasks)}  [Text Cleaned] , {len(network.dependencies)}  [Text Cleaned] "
    )
    is_valid, errors = network.validate_dag()
    print(f"    [Text Cleaned] : {' [Text Cleaned] ' if is_valid else ' [Text Cleaned] '}")

    return editor


def demo_advanced_features():
    """ [Text Cleaned] """
    print("\n=== 4.  [Text Cleaned]  (Advanced Features Combination) ===")

    network = Tasknetwork()
    editor = networkEditor(network)

    print("\n [Text Cleaned] :")

    network_config = {
        "tasks": [
            {
                "task_id": "advanced_task1",
                "name": " [Text Cleaned] 1",
                "description": " [Text Cleaned] 1",
                "priority": 2,
            },
            {
                "task_id": "advanced_task2",
                "name": " [Text Cleaned] 2",
                "description": " [Text Cleaned] 2",
                "priority": 3,
            },
            {
                "task_id": "advanced_task3",
                "name": " [Text Cleaned] 3",
                "description": " [Text Cleaned] 3",
                "priority": 1,
            },
        ],
        "dependencies": [
            {
                "from_task_id": "advanced_task1",
                "to_task_id": "advanced_task2",
                "dependency_type": "unconditional",
            },
            {
                "from_task_id": "advanced_task2",
                "to_task_id": "advanced_task3",
                "dependency_type": "success_only",
            },
        ],
    }

    try:
        result = editor.execute_command_by_name(
            "build_network", network_config
        )
        print(
            f"   ✓  [Text Cleaned] : {len(result.tasks)}  [Text Cleaned] , {len(result.dependencies)}  [Text Cleaned] "
        )

        is_valid, errors = network.validate_dag()
        print(f"   ✓  [Text Cleaned] : {' [Text Cleaned] ' if is_valid else ' [Text Cleaned] '}")

    except Exception as e:
        print(f"   ✗  [Text Cleaned] : {e}")

    print("\n [Text Cleaned] / [Text Cleaned] :")
    print(f"    [Text Cleaned] : {len(network.tasks)}  [Text Cleaned] ")
    print(f"    [Text Cleaned] : {editor.can_undo()}")

    if editor.can_undo():
        editor.undo()
        print(f"    [Text Cleaned] : {len(network.tasks)}  [Text Cleaned] ")
        print(f"    [Text Cleaned] : {editor.can_redo()}")

        if editor.can_redo():
            editor.redo()
            print(f"    [Text Cleaned] : {len(network.tasks)}  [Text Cleaned] ")

    return editor


def main():
    """ [Text Cleaned] """
    print("Alien network Editor  [Text Cleaned] ")
    print("=" * 60)

    try:
        editor1 = demo_serializable_parameters()
        editor2 = demo_command_registry()
        editor3 = demo_validation_rollback()
        editor4 = demo_advanced_features()

        print("\n" + "=" * 60)
        print("✓  [Text Cleaned] !  [Text Cleaned] :")
        print("  1. ✓  [Text Cleaned]  (dict  [Text Cleaned] )")
        print("  2. ✓  [Text Cleaned] ")
        print("  3. ✓  [Text Cleaned] ")
        print("  4. ✓  [Text Cleaned] / [Text Cleaned] ")
        print("  5. ✓  [Text Cleaned] ")

        print(f"\n [Text Cleaned] :")
        print(f"  -  [Text Cleaned] : {len(command_registry.list_commands())}")
        print(f"  -  [Text Cleaned] : {len(command_registry.get_categories())}")

        return 0

    except Exception as e:
        print(f"\n✗  [Text Cleaned] : {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
