#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BaseModel Integration Example for TaskStar, TaskStarLine, and Tasknetwork.

This example demonstrates how to use the Pydantic BaseModel schemas for
serialization, deserialization, and data validation with the network classes.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
from datetime import datetime

from cluster.network.task_star import TaskStar
from cluster.network.task_star_line import TaskStarLine
from cluster.network.task_network import Tasknetwork
from cluster.network.enums import (
    TaskStatus,
    TaskPriority,
    DeviceType,
    DependencyType,
)
from cluster.agents.schema import (
    TaskStarSchema,
    TaskStarLineSchema,
    TasknetworkSchema,
)


def example_basic_usage():
    """ [Text Cleaned] ： [Text Cleaned] """
    print("📚  [Text Cleaned] ")
    print("=" * 50)

    task = TaskStar(
        task_id="example_task",
        name=" [Text Cleaned] ",
        description=" [Text Cleaned] ， [Text Cleaned]  BaseModel  [Text Cleaned] ",
        priority=TaskPriority.HIGH,
        device_type=DeviceType.WINDOWS,
    )

    schema = task.to_basemodel()
    print(f"✅ TaskStar -> BaseModel: {schema.name}")

    task_restored = TaskStar.from_basemodel(schema)
    print(f"✅ BaseModel -> TaskStar: {task_restored.name}")

    json_str = schema.model_dump_json(indent=2)
    print(f"✅ JSON  [Text Cleaned] : {len(json_str)}  [Text Cleaned] ")


def example_json_persistence():
    """ [Text Cleaned] ：JSON  [Text Cleaned] """
    print("\n💾 JSON  [Text Cleaned] ")
    print("=" * 50)

    network = Tasknetwork(
        network_id="example_network", name=" [Text Cleaned] "
    )

    tasks_data = [
        (" [Text Cleaned] ", " [Text Cleaned] ", TaskPriority.HIGH),
        (" [Text Cleaned] ", " [Text Cleaned] ", TaskPriority.MEDIUM),
        (" [Text Cleaned] ", " [Text Cleaned] ", TaskPriority.LOW),
    ]

    task_ids = []
    for i, (name, desc, priority) in enumerate(tasks_data, 1):
        task_id = f"task_{i:03d}"
        task = TaskStar(
            task_id=task_id,
            name=name,
            description=desc,
            priority=priority,
            device_type=DeviceType.LINUX,
        )
        network.add_task(task)
        task_ids.append(task_id)

    deps = [
        (task_ids[0], task_ids[1], DependencyType.SUCCESS_ONLY),
        (task_ids[1], task_ids[2], DependencyType.UNCONDITIONAL),
    ]

    for from_id, to_id, dep_type in deps:
        dep = TaskStarLine(from_id, to_id, dep_type)
        network.add_dependency(dep)

    schema = network.to_basemodel()
    json_data = schema.model_dump_json(indent=2)

    filename = "example_network.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json_data)
    print(f"✅  [Text Cleaned] : {filename}")

    with open(filename, "r", encoding="utf-8") as f:
        loaded_json = f.read()

    loaded_schema = TasknetworkSchema.model_validate_json(loaded_json)
    loaded_network = Tasknetwork.from_basemodel(loaded_schema)

    print(f"✅  [Text Cleaned] : {loaded_network.name}")
    print(f"   -  [Text Cleaned] : {len(loaded_network.tasks)}")
    print(f"   -  [Text Cleaned] : {len(loaded_network.dependencies)}")


def example_data_validation():
    """ [Text Cleaned] ： [Text Cleaned] """
    print("\n🔍  [Text Cleaned] ")
    print("=" * 50)

    valid_data = {
        "task_id": "validation_task",
        "name": " [Text Cleaned] ",
        "description": " [Text Cleaned] ",
        "priority": "HIGH",
        "status": "PENDING",
        "device_type": "WINDOWS",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "task_data": {"param1": "value1"},
        "dependencies": [],
        "dependents": [],
    }

    try:
        schema = TaskStarSchema(**valid_data)
        print("✅  [Text Cleaned] ")

        task = TaskStar.from_basemodel(schema)
        print(f"✅  [Text Cleaned] : {task.name}")

    except Exception as e:
        print(f"❌  [Text Cleaned] : {e}")

    invalid_data = valid_data.copy()
    invalid_data["task_id"] = ""
    try:
        schema = TaskStarSchema(**invalid_data)
        task = TaskStar.from_basemodel(schema)
        print("⚠️  [Text Cleaned]  task_id  [Text Cleaned] ")
    except Exception as e:
        print(f"✅  [Text Cleaned] : {type(e).__name__}")


def example_api_integration():
    """ [Text Cleaned] ：API  [Text Cleaned] """
    print("\n🌐 API  [Text Cleaned] ")
    print("=" * 50)

    api_response = {
        "network_id": "api_network",
        "name": " [Text Cleaned] API [Text Cleaned] ",
        "state": "READY",
        "tasks": {
            "api_task_1": {
                "task_id": "api_task_1",
                "name": "API [Text Cleaned] 1",
                "description": " [Text Cleaned] API [Text Cleaned] ",
                "priority": 3,                "status": "pending",                "device_type": "windows",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "task_data": {},
                "dependencies": [],
                "dependents": [],
            }
        },
        "dependencies": {},
        "metadata": {"source": "api", "version": "1.0"},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "enable_visualization": True,
    }

    try:
        schema = TasknetworkSchema(**api_response)
        print("✅ API  [Text Cleaned] ")

        network = Tasknetwork.from_basemodel(schema)
        print(f"✅  [Text Cleaned] : {network.name}")
        print(f"   -  [Text Cleaned] : {network.state.value}")
        print(f"   -  [Text Cleaned] : {len(network.tasks)}")

        task = list(network.tasks.values())[0]
        print(f"   -  [Text Cleaned] : {task.priority.value} ({task.priority.name})")
        print(f"   -  [Text Cleaned] : {task.status.value}")

    except Exception as e:
        print(f"❌ API  [Text Cleaned] : {e}")


def main():
    """ [Text Cleaned] """
    print("🚀 BaseModel  [Text Cleaned] ")
    print(" [Text Cleaned]  BaseModel  [Text Cleaned] \n")

    example_basic_usage()
    example_json_persistence()
    example_data_validation()
    example_api_integration()

    print("\n🎉  [Text Cleaned] ！")
    print("\n💡  [Text Cleaned] :")
    print("   •  [Text Cleaned] （ [Text Cleaned]  ↔  [Text Cleaned] ）")
    print("   • JSON  [Text Cleaned] / [Text Cleaned] ")
    print("   •  [Text Cleaned] ")
    print("   • API  [Text Cleaned] ")
    print("   •  [Text Cleaned] ")


if __name__ == "__main__":
    main()
