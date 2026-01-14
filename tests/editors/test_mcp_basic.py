#!/usr/bin/env python3
"""
Simplified test script for the Orion Editor MCP Server.
Tests core functionality without complex state management.
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


def test_basic_operations():
    """Test basic CRUD operations for tasks and dependencies."""
    print("=== Testing Basic MCP Operations ===")

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
        return tool.fn(*args, **kwargs)

    success_count = 0
    total_tests = 0

    # Test 1: Add Task
    print("\n1. Testing add_task...")
    total_tests += 1
    try:
        result = call_tool(
            "add_task",
            task_id="test_task",
            name="Test Task",
            description="A simple test task for validation",
            target_device_id="test_device",
            tips="Complete this task carefully and verify results",
        )
        task = json.loads(result)
        print(f"   ✓ Added task: {task['task_id']} - {task['name']}")
        success_count += 1
    except Exception as e:
        print(f"   ✗ Failed to add task: {e}")

    # Test 2: Update Task
    print("\n2. Testing update_task...")
    total_tests += 1
    try:
        result = call_tool(
            "update_task",
            task_id="test_task",
            name="Updated Test Task",
            description="Updated description with more details",
            target_device_id="updated_device",
            tips="Updated tips with enhanced guidance",
        )
        task = json.loads(result)
        print(f"   ✓ Updated task: {task['name']}")
        success_count += 1
    except Exception as e:
        print(f"   ✗ Failed to update task: {e}")

    # Test 3: Add Second Task for Dependency
    print("\n3. Testing add second task...")
    total_tests += 1
    try:
        result = call_tool(
            "add_task",
            task_id="second_task",
            name="Second Task",
            description="Second task for dependency testing",
            tips="This will depend on the first task",
        )
        task = json.loads(result)
        print(f"   ✓ Added second task: {task['task_id']}")
        success_count += 1
    except Exception as e:
        print(f"   ✗ Failed to add second task: {e}")

    # Test 4: Add Dependency
    print("\n4. Testing add_dependency...")
    total_tests += 1
    try:
        result = call_tool(
            "add_dependency",
            from_task_id="test_task",
            to_task_id="second_task",
            condition_description="Second task waits for first task to complete successfully",
        )
        dep = json.loads(result)
        print(f"   ✓ Added dependency: {dep['from_task_id']} -> {dep['to_task_id']}")
        dep_id = dep["line_id"]
        success_count += 1
    except Exception as e:
        print(f"   ✗ Failed to add dependency: {e}")
        dep_id = None

    # Test 5: Update Dependency
    print("\n5. Testing update_dependency...")
    total_tests += 1
    if dep_id:
        try:
            result = call_tool(
                "update_dependency",
                dependency_id=dep_id,
                condition_description="Updated: Second task must wait for first task with validation",
            )
            dep = json.loads(result)
            print(f"   ✓ Updated dependency description")
            success_count += 1
        except Exception as e:
            print(f"   ✗ Failed to update dependency: {e}")
    else:
        print(f"   ⚠ Skipped (no dependency ID)")

    # Test 6: Build Orion
    print("\n6. Testing build_orion...")
    total_tests += 1
    try:
        config = {
            "tasks": [
                {
                    "task_id": "batch_task",
                    "name": "Batch Task",
                    "description": "Task created via batch operation",
                    "priority": 2,
                }
            ],
            "dependencies": [],
            "metadata": {"test": True},
        }
        result = call_tool("build_orion", config)
        orion = json.loads(result)
        print(
            f"   ✓ Built orion with {len(orion['tasks'])} total tasks"
        )
        success_count += 1
    except Exception as e:
        print(f"   ✗ Failed to build orion: {e}")

    return success_count, total_tests


def main():
    """Run basic MCP server tests."""
    print("Testing Orion Editor MCP Server (Basic Operations)")
    print("=" * 70)

    try:
        success, total = test_basic_operations()

        print(f"\n" + "=" * 70)
        print(f"Test Results: {success}/{total} tests passed")

        if success == total:
            print("✓ All basic operations working correctly!")
            return 0
        else:
            print(f"⚠ {total - success} tests failed")
            return 1

    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
