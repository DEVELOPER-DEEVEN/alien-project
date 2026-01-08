#!/usr/bin/env python3
"""
Simple test for DAG visualization.
"""

import sys
import os

# Add the Alien-Unis directory to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

try:
    from cluster.network.task_network import Tasknetwork
    from cluster.network.task_star import TaskStar
    from cluster.network.enums import TaskPriority
    from cluster.visualization.dag_visualizer import DAGVisualizer

    print("✅ All imports successful!")

    # Create a simple network
    network = Tasknetwork(
        name="Test network", enable_visualization=True
    )

    # Add a simple task
    task = TaskStar(
        task_id="test_task",
        name="Test Task",
        description="This is a test task",
        priority=TaskPriority.MEDIUM,
    )

    print("📊 Adding task...")
    network.add_task(task)

    # Test manual visualization
    print("🎨 Testing manual visualization...")
    network.display_dag("overview", force=True)

    print("🎉 DAG visualization test completed successfully!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
