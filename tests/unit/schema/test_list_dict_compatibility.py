#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test for List/Dict compatibility in TasknetworkSchema.

This test verifies that tasks and dependencies can be provided as either
List or Dict formats and are properly converted and validated.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from cluster.agents.schema import (
    TaskStarSchema,
    TaskStarLineSchema,
    TasknetworkSchema,
)
import json


def test_tasks_and_dependencies_as_lists():
    """ [Text Cleaned]  List  [Text Cleaned]  tasks  [Text Cleaned]  dependencies"""
    print("🧪  [Text Cleaned]  List  [Text Cleaned]  tasks  [Text Cleaned]  dependencies")

    task_list = [
        {
            "task_id": "task_001",
            "name": " [Text Cleaned] ",
            "description": " [Text Cleaned] ",
        },
        {
            "task_id": "task_002",
            "name": " [Text Cleaned] ",
            "description": " [Text Cleaned] ",
        },
        {
            "name": " [Text Cleaned] ",
            "description": " [Text Cleaned]  ID",
        },
    ]

    dependency_list = [
        {
            "line_id": "dep_001",
            "from_task_id": "task_001",
            "to_task_id": "task_002",
            "condition_description": " [Text Cleaned] ",
        },
        {
            "from_task_id": "task_002",
            "to_task_id": "task_003",
            "condition_description": " [Text Cleaned] ， [Text Cleaned]  ID",
        },
    ]

    network_data = {
        "name": "List [Text Cleaned] ",
        "tasks": task_list,
        "dependencies": dependency_list,
    }

    network = TasknetworkSchema(**network_data)

    print(f"✅  [Text Cleaned] : {network.name}")
    print(f"   -  [Text Cleaned]  ID: {network.network_id}")
    print(f"   -  [Text Cleaned] : {len(network.tasks)}")
    print(f"   -  [Text Cleaned] : {len(network.dependencies)}")

    assert isinstance(network.tasks, dict), "Tasks  [Text Cleaned]  Dict  [Text Cleaned] "

    assert isinstance(
        network.dependencies, dict
    ), "Dependencies  [Text Cleaned]  Dict  [Text Cleaned] "

    task_ids = list(network.tasks.keys())
    print(f"   -  [Text Cleaned]  IDs: {task_ids}")

    dep_ids = list(network.dependencies.keys())
    print(f"   -  [Text Cleaned]  IDs: {dep_ids}")

    auto_generated_tasks = [
        task for task in network.tasks.values() if task.name == " [Text Cleaned] "
    ]
    assert len(auto_generated_tasks) == 1, " [Text Cleaned]  ID  [Text Cleaned] "
    print(f"   -  [Text Cleaned]  ID: {auto_generated_tasks[0].task_id}")

    return network


def test_tasks_and_dependencies_as_dicts():
    """ [Text Cleaned]  Dict  [Text Cleaned]  tasks  [Text Cleaned]  dependencies（ [Text Cleaned] ）"""
    print("\n🧪  [Text Cleaned]  Dict  [Text Cleaned]  tasks  [Text Cleaned]  dependencies")

    task_dict = {
        "task_001": TaskStarSchema(
            task_id="task_001",
            name="Dict [Text Cleaned] 1",
            description=" [Text Cleaned] Dict [Text Cleaned] ",
        ),
        "task_002": TaskStarSchema(
            task_id="task_002",
            name="Dict [Text Cleaned] 2",
            description=" [Text Cleaned] Dict [Text Cleaned] ",
        ),
    }

    dependency_dict = {
        "dep_001": TaskStarLineSchema(
            line_id="dep_001",
            from_task_id="task_001",
            to_task_id="task_002",
            condition_description="Dict [Text Cleaned] ",
        )
    }

    network = TasknetworkSchema(
        name="Dict [Text Cleaned] ", tasks=task_dict, dependencies=dependency_dict
    )

    print(f"✅  [Text Cleaned] : {network.name}")
    print(f"   -  [Text Cleaned]  ID: {network.network_id}")
    print(f"   -  [Text Cleaned] : {len(network.tasks)}")
    print(f"   -  [Text Cleaned] : {len(network.dependencies)}")

    assert isinstance(network.tasks, dict), "Tasks  [Text Cleaned]  Dict  [Text Cleaned] "
    assert isinstance(
        network.dependencies, dict
    ), "Dependencies  [Text Cleaned]  Dict  [Text Cleaned] "

    return network


def test_mixed_format_compatibility():
    """ [Text Cleaned] """
    print("\n🧪  [Text Cleaned] ")

    network1 = TasknetworkSchema(
        name=" [Text Cleaned] 1",
        tasks=[
            {"name": "List [Text Cleaned] 1", "description": " [Text Cleaned] List"},
            {"name": "List [Text Cleaned] 2", "description": " [Text Cleaned] List"},
        ],
        dependencies={
            "manual_dep": TaskStarLineSchema(
                line_id="manual_dep", from_task_id="task_001", to_task_id="task_002"
            )
        },
    )

    print(
        f"✅  [Text Cleaned] 1 [Text Cleaned] : tasks={type(network1.tasks).__name__}, dependencies={type(network1.dependencies).__name__}"
    )

    network2 = TasknetworkSchema(
        name=" [Text Cleaned] 2",
        tasks={
            "manual_task": TaskStarSchema(
                task_id="manual_task", name="Dict [Text Cleaned] ", description=" [Text Cleaned] Dict"
            )
        },
        dependencies=[
            {
                "from_task_id": "manual_task",
                "to_task_id": "some_other_task",
                "condition_description": " [Text Cleaned] List [Text Cleaned] ",
            }
        ],
    )

    print(
        f"✅  [Text Cleaned] 2 [Text Cleaned] : tasks={type(network2.tasks).__name__}, dependencies={type(network2.dependencies).__name__}"
    )

    return network1, network2


def test_conversion_methods():
    """ [Text Cleaned] """
    print("\n🧪  [Text Cleaned] ")

    network = TasknetworkSchema(
        name=" [Text Cleaned] ",
        tasks=[
            {"name": " [Text Cleaned] A", "description": " [Text Cleaned] A"},
            {"name": " [Text Cleaned] B", "description": " [Text Cleaned] B"},
            {"name": " [Text Cleaned] C", "description": " [Text Cleaned] C"},
        ],
        dependencies=[
            {"from_task_id": "task_001", "to_task_id": "task_002"},
            {"from_task_id": "task_002", "to_task_id": "task_003"},
        ],
    )

    tasks_list = network.get_tasks_as_list()
    print(f"✅  [Text Cleaned] : {len(tasks_list)}  [Text Cleaned] ")
    assert len(tasks_list) == 3, " [Text Cleaned] 3 [Text Cleaned] "
    assert all(
        isinstance(task, TaskStarSchema) for task in tasks_list
    ), " [Text Cleaned] TaskStarSchema"

    deps_list = network.get_dependencies_as_list()
    print(f"✅  [Text Cleaned] : {len(deps_list)}  [Text Cleaned] ")
    assert len(deps_list) == 2, " [Text Cleaned] 2 [Text Cleaned] "
    assert all(
        isinstance(dep, TaskStarLineSchema) for dep in deps_list
    ), " [Text Cleaned] TaskStarLineSchema"

    data_with_lists = network.to_dict_with_lists()
    print(
        f"✅  [Text Cleaned] : tasks={type(data_with_lists['tasks']).__name__}, dependencies={type(data_with_lists['dependencies']).__name__}"
    )
    assert isinstance(data_with_lists["tasks"], list), " [Text Cleaned] tasks [Text Cleaned] list"
    assert isinstance(
        data_with_lists["dependencies"], list
    ), " [Text Cleaned] dependencies [Text Cleaned] list"

    return network


def test_json_serialization():
    """ [Text Cleaned]  JSON  [Text Cleaned] """
    print("\n🧪  [Text Cleaned]  JSON  [Text Cleaned] ")

    network = TasknetworkSchema(
        name="JSON [Text Cleaned] ",
        tasks=[
            {"name": "JSON [Text Cleaned] 1", "description": "JSON [Text Cleaned] 1"},
            {"name": "JSON [Text Cleaned] 2", "description": "JSON [Text Cleaned] 2"},
        ],
        dependencies=[
            {
                "from_task_id": "task_001",
                "to_task_id": "task_002",
                "condition_description": "JSON [Text Cleaned] ",
            }
        ],
    )

    json_dict_format = network.model_dump_json(indent=2)
    print(f"✅ Dict [Text Cleaned] JSON [Text Cleaned] : {len(json_dict_format)}  [Text Cleaned] ")

    json_list_format = json.dumps(network.to_dict_with_lists(), indent=2)
    print(f"✅ List [Text Cleaned] JSON [Text Cleaned] : {len(json_list_format)}  [Text Cleaned] ")

    restored_from_dict = TasknetworkSchema.model_validate_json(json_dict_format)
    print(f"✅  [Text Cleaned] Dict [Text Cleaned] JSON [Text Cleaned] : {restored_from_dict.name}")

    list_data = json.loads(json_list_format)
    restored_from_list = TasknetworkSchema(**list_data)
    print(f"✅  [Text Cleaned] List [Text Cleaned] JSON [Text Cleaned] : {restored_from_list.name}")

    assert restored_from_dict.name == restored_from_list.name, " [Text Cleaned] "
    assert len(restored_from_dict.tasks) == len(
        restored_from_list.tasks
    ), " [Text Cleaned] "
    assert len(restored_from_dict.dependencies) == len(
        restored_from_list.dependencies
    ), " [Text Cleaned] "

    return network


def main():
    """ [Text Cleaned] """
    print("🎯 TasknetworkSchema List/Dict  [Text Cleaned] ")
    print("=" * 60)

    try:
        network1 = test_tasks_and_dependencies_as_lists()
        network2 = test_tasks_and_dependencies_as_dicts()
        mixed1, mixed2 = test_mixed_format_compatibility()
        network3 = test_conversion_methods()
        network4 = test_json_serialization()

        print("\n" + "=" * 60)
        print("🎉  [Text Cleaned] ！")

        print("\n💡  [Text Cleaned] :")
        print("   ✅ List  [Text Cleaned]  tasks  [Text Cleaned]  dependencies  [Text Cleaned]  Dict")
        print("   ✅ Dict  [Text Cleaned] ")
        print("   ✅  [Text Cleaned] ")
        print("   ✅  [Text Cleaned]  ID  [Text Cleaned]  List  [Text Cleaned] ")
        print("   ✅  [Text Cleaned] ")
        print("   ✅ JSON  [Text Cleaned] / [Text Cleaned] ")

        print("\n📊  [Text Cleaned] :")
        print(
            f"   •  [Text Cleaned]  {len([network1, network2, mixed1, mixed2, network3, network4])}  [Text Cleaned] "
        )
        print("   •  [Text Cleaned]  List ↔ Dict  [Text Cleaned] ")
        print("   •  [Text Cleaned] ")
        print("   •  [Text Cleaned]  JSON  [Text Cleaned] ")

    except Exception as e:
        print(f"\n❌  [Text Cleaned] : {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
