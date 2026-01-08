# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Test script for the new network formatter.
This demonstrates the enhanced display format for network results.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cluster.visualization.network_formatter import format_network_result


def test_formatter():
    """Test the network formatter with sample data."""

    print("\n" + "=" * 80)
    print("Testing New network Formatter")
    print("=" * 80 + "\n")

    # Sample network data (from your actual output)
    network_result = {
        "id": "network_8a657000_20251107_225225",
        "name": "network_8a657000_20251107_225225",
        "state": "completed",
        "created": "14:52:25",
        "started": "14:52:26",
        "ended": "14:52:51",
        "total_tasks": 3,
        "execution_duration": 24.953522,
        "statistics": {
            "network_id": "network_8a657000_20251107_225225",
            "name": "network_8a657000_20251107_225225",
            "state": "completed",
            "total_tasks": 3,
            "total_dependencies": 0,
            "task_status_counts": {"completed": 3},
            "longest_path_length": 1,
            "longest_path_tasks": [],
            "max_width": 3,
            "critical_path_length": 7.643585,
            "total_work": 21.733924,
            "parallelism_ratio": 2.84342020138456,
            "parallelism_calculation_mode": "actual_time",
            "critical_path_tasks": ["task-2"],
            "execution_duration": 24.953522,
            "created_at": "2025-11-07T14:52:25.985927+00:00",
            "updated_at": "2025-11-07T14:52:51.071804+00:00",
        },
        "network": "Tasknetwork(id=network_8a657000_20251107_225225, tasks=3, state=completed)",
    }

    # Display using the new formatter
    format_network_result(network_result)

    print("\n" + "=" * 80)
    print("Formatter test completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_formatter()
