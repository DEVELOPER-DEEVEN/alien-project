#!/usr/bin/env python3
# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Tasknetwork Editor  [Text Cleaned] 

 [Text Cleaned] 。
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cluster.network.editor import networkEditor
from cluster.network.enums import TaskPriority, DependencyType


def example_basic_operations():
    """ [Text Cleaned] """
    print("🌟  [Text Cleaned] ")
    print("=" * 50)

    editor = networkEditor()

    print("📝  [Text Cleaned] ...")
    task1 = editor.create_and_add_task("login", " [Text Cleaned] ", priority=TaskPriority.HIGH)
    task2 = editor.create_and_add_task(
        "fetch_data", " [Text Cleaned] ", priority=TaskPriority.MEDIUM
    )
    task3 = editor.create_and_add_task(
        "process_data", " [Text Cleaned] ", priority=TaskPriority.MEDIUM
    )
    task4 = editor.create_and_add_task(
        "display_result", " [Text Cleaned] ", priority=TaskPriority.LOW
    )

    print(f"✅  [Text Cleaned]  {len(editor.list_tasks())}  [Text Cleaned] ")

    print("\n🔗  [Text Cleaned] ...")
    dep1 = editor.create_and_add_dependency("login", "fetch_data", "UNCONDITIONAL")
    dep2 = editor.create_and_add_dependency(
        "fetch_data", "process_data", "SUCCESS_ONLY"
    )
    dep3 = editor.create_and_add_dependency(
        "process_data", "display_result", "UNCONDITIONAL"
    )

    print(f"✅  [Text Cleaned]  {len(editor.list_dependencies())}  [Text Cleaned] ")

    print("\n🔍  [Text Cleaned] ...")
    is_valid, errors = editor.validate_network()
    if is_valid:
        print("✅  [Text Cleaned] ")
        topo_order = editor.get_topological_order()
        print(f"📋  [Text Cleaned] : {' -> '.join(topo_order)}")
    else:
        print(f"❌  [Text Cleaned] : {errors}")

    return editor


def example_undo_redo():
    """ [Text Cleaned] / [Text Cleaned] """
    print("\n🔄  [Text Cleaned] / [Text Cleaned] ")
    print("=" * 50)

    editor = networkEditor()

    print("📝  [Text Cleaned] ...")
    editor.create_and_add_task("task1", " [Text Cleaned] 1")
    editor.create_and_add_task("task2", " [Text Cleaned] 2")
    editor.create_and_add_dependency("task1", "task2")

    print(f" [Text Cleaned] : {len(editor.list_tasks())}")
    print(f" [Text Cleaned] : {len(editor.list_dependencies())}")

    print("\n⏪  [Text Cleaned] ...")
    while editor.can_undo():
        undo_desc = editor.get_undo_description()
        print(f" [Text Cleaned] : {undo_desc}")
        editor.undo()
        print(
            f"  ->  [Text Cleaned] : {len(editor.list_tasks())},  [Text Cleaned] : {len(editor.list_dependencies())}"
        )

    print("\n⏩  [Text Cleaned] ...")
    while editor.can_redo():
        redo_desc = editor.get_redo_description()
        print(f" [Text Cleaned] : {redo_desc}")
        editor.redo()
        print(
            f"  ->  [Text Cleaned] : {len(editor.list_tasks())},  [Text Cleaned] : {len(editor.list_dependencies())}"
        )


def example_bulk_operations():
    """ [Text Cleaned] """
    print("\n📦  [Text Cleaned] ")
    print("=" * 50)

    editor = networkEditor()

    tasks = [
        {
            "task_id": "init",
            "description": " [Text Cleaned] ",
            "priority": TaskPriority.CRITICAL.value,
        },
        {
            "task_id": "load_config",
            "description": " [Text Cleaned] ",
            "priority": TaskPriority.HIGH.value,
        },
        {
            "task_id": "start_services",
            "description": " [Text Cleaned] ",
            "priority": TaskPriority.HIGH.value,
        },
        {
            "task_id": "health_check",
            "description": " [Text Cleaned] ",
            "priority": TaskPriority.MEDIUM.value,
        },
        {
            "task_id": "ready",
            "description": " [Text Cleaned] ",
            "priority": TaskPriority.LOW.value,
        },
    ]

    dependencies = [
        {
            "from_task_id": "init",
            "to_task_id": "load_config",
            "dependency_type": DependencyType.UNCONDITIONAL.value,
        },
        {
            "from_task_id": "load_config",
            "to_task_id": "start_services",
            "dependency_type": DependencyType.SUCCESS_ONLY.value,
        },
        {
            "from_task_id": "start_services",
            "to_task_id": "health_check",
            "dependency_type": DependencyType.UNCONDITIONAL.value,
        },
        {
            "from_task_id": "health_check",
            "to_task_id": "ready",
            "dependency_type": DependencyType.SUCCESS_ONLY.value,
        },
    ]

    print("🏗️  [Text Cleaned] ...")
    editor.build_from_tasks_and_dependencies(
        tasks, dependencies, metadata={"purpose": "system_startup", "version": "1.0"}
    )

    print(
        f"✅  [Text Cleaned] : {len(editor.list_tasks())}  [Text Cleaned] , {len(editor.list_dependencies())}  [Text Cleaned] "
    )

    stats = editor.get_statistics()
    print(f"📊  [Text Cleaned] :")
    print(f"  -  [Text Cleaned] : {stats['total_tasks']}")
    print(f"  -  [Text Cleaned] : {stats['total_dependencies']}")
    print(f"  -  [Text Cleaned] : {stats['editor_execution_count']}")

    return editor


def example_file_operations():
    """ [Text Cleaned] """
    print("\n💾  [Text Cleaned] ")
    print("=" * 50)

    editor1 = networkEditor()
    editor1.create_and_add_task("web_request", " [Text Cleaned] ")
    editor1.create_and_add_task("parse_response", " [Text Cleaned] ")
    editor1.create_and_add_dependency("web_request", "parse_response")

    filename = "example_network.json"
    print(f"💾  [Text Cleaned]  {filename}...")
    editor1.save_network(filename)
    print("✅  [Text Cleaned] ")

    print(f"📂  [Text Cleaned]  {filename}  [Text Cleaned] ...")
    editor2 = networkEditor()
    editor2.load_network(filename)
    print(
        f"✅  [Text Cleaned] : {len(editor2.list_tasks())}  [Text Cleaned] , {len(editor2.list_dependencies())}  [Text Cleaned] "
    )

    original_stats = editor1.get_statistics()
    loaded_stats = editor2.get_statistics()

    if (
        original_stats["total_tasks"] == loaded_stats["total_tasks"]
        and original_stats["total_dependencies"] == loaded_stats["total_dependencies"]
    ):
        print("✅  [Text Cleaned] ")
    else:
        print("❌  [Text Cleaned] ")

    import os

    if os.path.exists(filename):
        os.remove(filename)
        print(f"🗑️  [Text Cleaned]  {filename}")


def example_advanced_features():
    """ [Text Cleaned] """
    print("\n🚀  [Text Cleaned] ")
    print("=" * 50)

    editor = networkEditor()

    def operation_observer(editor, command, result):
        print(f"  📢  [Text Cleaned] : {command}")

    print("👁️  [Text Cleaned] ...")
    editor.add_observer(operation_observer)

    print("📝  [Text Cleaned] （ [Text Cleaned] ）...")
    editor.create_and_add_task("observed_task", " [Text Cleaned] ")

    editor.remove_observer(operation_observer)
    print("👁️  [Text Cleaned] ")

    print("\n📊  [Text Cleaned] ...")
    tasks = ["A", "B", "C", "D", "E"]
    for task_id in tasks:
        editor.create_and_add_task(task_id, f" [Text Cleaned]  {task_id}")

    dependencies = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]
    for from_task, to_task in dependencies:
        editor.create_and_add_dependency(from_task, to_task)

    print(f"✅  [Text Cleaned]  {len(editor.list_tasks())}  [Text Cleaned] ")

    print("\n🎯  [Text Cleaned] ...")
    subgraph = editor.create_subgraph(["A", "B", "D"])
    print(
        f"✅  [Text Cleaned]  {len(subgraph.list_tasks())}  [Text Cleaned] , {len(subgraph.list_dependencies())}  [Text Cleaned] "
    )

    ready_tasks = editor.get_ready_tasks()
    print(f"🚦  [Text Cleaned] : {[t.task_id for t in ready_tasks]}")


def main():
    """ [Text Cleaned] """
    print("🌟 Tasknetwork Editor  [Text Cleaned] ")
    print("=" * 80)

    try:
        example_basic_operations()
        example_undo_redo()
        example_bulk_operations()
        example_file_operations()
        example_advanced_features()

        print("\n🎉  [Text Cleaned] ！")
        print("✅ Tasknetwork Editor  [Text Cleaned] ")

    except Exception as e:
        print(f"\n❌  [Text Cleaned] : {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
