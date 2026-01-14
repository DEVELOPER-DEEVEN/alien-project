#!/usr/bin/env python3
"""
Test script for the Orion Editor MCP Server.
Tests all the implemented MCP tools to ensure they work correctly.
"""

import sys
import os
import json

# Add the ALIEN2 directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
alien_path = os.path.dirname(current_dir)
sys.path.insert(0, alien_path)

from alien.client.mcp.local_servers.orion_mcp_server import (
    create_orion_mcp_server,
)


def test_mcp_server():
    """Test all MCP server tools."""
    print("=== Testing Orion Editor MCP Server ===")

    # Create the MCP server instance
    mcp_server = create_orion_mcp_server()

    # Get all available tools using the tool manager
    tools_dict = mcp_server._tool_manager._tools
    print(f"\nAvailable tools: {len(tools_dict)}")
    for tool_name in tools_dict.keys():
        print(f"  - {tool_name}")

    # Helper function to call tools
    def call_tool(tool_name, *args, **kwargs):
        """Call a tool by name with arguments"""
        tool = tools_dict[tool_name]
        # Call the tool function directly
        return tool.fn(*args, **kwargs)

    # Test 1: Add tasks
    print("\n1. Testing add_task...")

    try:
        result1 = call_tool(
            "add_task",
            task_id="mcp_test_task1",
            name="MCP Test Task 1",
            description="First test task created through MCP server with detailed steps",
            target_device_id="test_device_1",
            tips="Make sure to complete this task before moving to the next one",
        )
        result2 = call_tool(
            "add_task",
            task_id="mcp_test_task2",
            name="MCP Test Task 2",
            description="Second test task created through MCP server for dependency testing",
            tips="This task depends on task1 completion",
        )
        print(f"    Added task1: {json.loads(result1)['task_id']}")
        print(f"    Added task2: {json.loads(result2)['task_id']}")
    except Exception as e:
        print(f"    Failed to add tasks: {e}")
        return False

    # Test 2: List tasks
    print("\n2. Testing list_tasks...")
    try:
        tasks_result = call_tool("list_tasks")
        tasks = json.loads(tasks_result)
        print(f"    Found {len(tasks)} tasks")
        for task in tasks:
            print(f"     - {task['task_id']}: {task['name']}")
    except Exception as e:
        print(f"    Failed to list tasks: {e}")
        return False

    # Test 3: Add dependency
    print("\n3. Testing add_dependency...")

    try:
        dep_result = call_tool(
            "add_dependency",
            from_task_id="mcp_test_task1",
            to_task_id="mcp_test_task2",
            condition_description="Task2 waits for Task1 to complete successfully before starting execution",
        )
        dep = json.loads(dep_result)
        print(f"    Added dependency: {dep['from_task_id']} -> {dep['to_task_id']}")
    except Exception as e:
        print(f"    Failed to add dependency: {e}")
        return False

    # Test 4: List dependencies
    print("\n4. Testing list_dependencies...")
    try:
        deps_result = call_tool("list_dependencies")
        deps = json.loads(deps_result)
        print(f"    Found {len(deps)} dependencies")
        for dep in deps:
            print(f"     - {dep['line_id']}: {dep['dependency_type']}")
    except Exception as e:
        print(f"    Failed to list dependencies: {e}")
        return False

    # Test 5: Update task
    print("\n5. Testing update_task...")

    try:
        updated_result = call_tool(
            "update_task",
            task_id="mcp_test_task1",
            name="MCP Test Task 1 (Updated)",
            description="This is an updated task description with more details",
            tips="Updated tips: Remember to validate results after completion",
        )
        updated_task = json.loads(updated_result)
        print(f"    Updated task: {updated_task['name']}")
    except Exception as e:
        print(f"    Failed to update task: {e}")
        return False

    # Test 6: Update dependency
    print("\n6. Testing update_dependency...")
    try:
        # First get the dependency ID from the list
        deps_result = call_tool("list_dependencies")
        deps = json.loads(deps_result)
        if deps:
            dependency_id = deps[0]["line_id"]
            updated_dep_result = call_tool(
                "update_dependency",
                dependency_id=dependency_id,
                condition_description="Updated condition: Task2 must wait for Task1 to complete successfully with validation",
            )
            updated_dep = json.loads(updated_dep_result)
            print(f"    Updated dependency condition description")
        else:
            print(f"    No dependencies found to update")
    except Exception as e:
        print(f"    Failed to update dependency: {e}")
        return False

    # Test 7: Get orion status
    print("\n7. Testing get_orion_status...")
    try:
        status_result = call_tool("get_orion_status")
        status = json.loads(status_result)
        print(f"    Orion status:")
        print(f"     - Task count: {status['task_count']}")
        print(f"     - Dependency count: {status['dependency_count']}")
        print(f"     - Is valid: {status['is_valid']}")
    except Exception as e:
        print(f"    Failed to get status: {e}")
        return False

    # Test 8: Build orion
    print("\n8. Testing build_orion...")
    config = {
        "tasks": [
            {
                "task_id": "batch_task1",
                "name": "批量任务1",
                "description": "批量创建的任务1",
                "priority": 1,
            },
            {
                "task_id": "batch_task2",
                "name": "批量任务2",
                "description": "批量创建的任务2",
                "priority": 2,
            },
        ],
        "dependencies": [
            {
                "from_task_id": "batch_task1",
                "to_task_id": "batch_task2",
                "dependency_type": "unconditional",
            }
        ],
        "metadata": {"batch_created": True, "test_orion": True},
    }

    try:
        build_result = call_tool("build_orion", config, False)
        built = json.loads(build_result)
        print(f"    Built orion with {len(built['tasks'])} total tasks")
    except Exception as e:
        print(f"    Failed to build orion: {e}")
        return False

    # Test 9: Undo/Redo operations
    print("\n9. Testing undo_last_operation...")
    try:
        undo_result = call_tool("undo_last_operation")
        print(f"    Undo result: {undo_result}")

        # Check task count after undo
        status_after_undo = json.loads(call_tool("get_orion_status"))
        print(f"   Tasks after undo: {status_after_undo['task_count']}")

    except Exception as e:
        print(f"    Failed to undo: {e}")
        return False

    print("\n10. Testing redo_last_operation...")
    try:
        redo_result = call_tool("redo_last_operation")
        print(f"    Redo result: {redo_result}")

        # Check task count after redo
        status_after_redo = json.loads(call_tool("get_orion_status"))
        print(f"   Tasks after redo: {status_after_redo['task_count']}")

    except Exception as e:
        print(f"    Failed to redo: {e}")
        return False

    # Test 11: Clear orion
    print("\n11. Testing clear_orion...")
    try:
        clear_result = call_tool("clear_orion")
        cleared = json.loads(clear_result)
        print(f"    Cleared orion, remaining tasks: {len(cleared['tasks'])}")
    except Exception as e:
        print(f"    Failed to clear orion: {e}")
        return False

    return True


def main():
    """Run all MCP server tests."""
    print("Testing Orion Editor MCP Server")
    print("=" * 50)

    try:
        success = test_mcp_server()

        if success:
            print("\n" + "=" * 50)
            print(" All MCP server tests completed successfully!")
        else:
            print("\n" + "=" * 50)
            print(" Some tests failed")
            return 1

    except Exception as e:
        print(f"\n Test suite failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
