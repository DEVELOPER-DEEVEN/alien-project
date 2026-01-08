"""
Test script to validate if network_before and network_after fields
from response.log can be parsed by Tasknetwork.from_json
"""

import json
import sys
from pathlib import Path

# Add project root to path (go up 3 levels: network -> cluster -> tests -> root)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from cluster.network.task_network import Tasknetwork


def test_network_parsing(log_file_path: str):
    """Test parsing network_before and network_after from log file"""

    print(f"Reading log file: {log_file_path}\n")

    with open(log_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"Total lines in log file: {len(lines)}\n")

    results = {
        "total_lines": len(lines),
        "lines_with_network_before": 0,
        "lines_with_network_after": 0,
        "successful_before_parsing": 0,
        "failed_before_parsing": 0,
        "successful_after_parsing": 0,
        "failed_after_parsing": 0,
        "errors": [],
    }

    for line_num, line in enumerate(lines, 1):
        try:
            # Parse the JSON line
            log_entry = json.loads(line.strip())

            # Check for network_before
            if (
                "network_before" in log_entry
                and log_entry["network_before"]
            ):
                results["lines_with_network_before"] += 1
                network_before_str = log_entry["network_before"]

                print(f"Line {line_num}: Testing network_before...")
                try:
                    # Test parsing with from_json
                    network = Tasknetwork.from_json(
                        json_data=network_before_str
                    )
                    results["successful_before_parsing"] += 1
                    print(f"  [OK] Successfully parsed network_before")
                    print(f"    - network ID: {network.network_id}")
                    print(f"    - Tasks: {network.task_count}")
                    print(f"    - Dependencies: {network.dependency_count}")
                    print(f"    - State: {network.state.value}")
                except Exception as e:
                    results["failed_before_parsing"] += 1
                    error_msg = f"Line {line_num} - network_before parsing failed: {type(e).__name__}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"  [FAIL] Failed to parse network_before: {e}")

            # Check for network_after
            if "network_after" in log_entry and log_entry["network_after"]:
                results["lines_with_network_after"] += 1
                network_after_str = log_entry["network_after"]

                print(f"Line {line_num}: Testing network_after...")
                try:
                    # Test parsing with from_json
                    network = Tasknetwork.from_json(
                        json_data=network_after_str
                    )
                    results["successful_after_parsing"] += 1
                    print(f"  [OK] Successfully parsed network_after")
                    print(f"    - network ID: {network.network_id}")
                    print(f"    - Tasks: {network.task_count}")
                    print(f"    - Dependencies: {network.dependency_count}")
                    print(f"    - State: {network.state.value}")
                except Exception as e:
                    results["failed_after_parsing"] += 1
                    error_msg = f"Line {line_num} - network_after parsing failed: {type(e).__name__}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"  [FAIL] Failed to parse network_after: {e}")

            print()  # Empty line for readability

        except json.JSONDecodeError as e:
            error_msg = f"Line {line_num} - JSON decode error: {e}"
            results["errors"].append(error_msg)
            print(f"Line {line_num}: Failed to parse JSON line: {e}\n")

    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total lines processed: {results['total_lines']}")
    print(
        f"Lines with network_before: {results['lines_with_network_before']}"
    )
    print(
        f"Lines with network_after: {results['lines_with_network_after']}"
    )
    print()
    print(f"network_before parsing:")
    print(f"  - Successful: {results['successful_before_parsing']}")
    print(f"  - Failed: {results['failed_before_parsing']}")
    print()
    print(f"network_after parsing:")
    print(f"  - Successful: {results['successful_after_parsing']}")
    print(f"  - Failed: {results['failed_after_parsing']}")
    print()

    if results["errors"]:
        print("ERRORS:")
        print("-" * 80)
        for error in results["errors"]:
            print(f"  {error}")
    else:
        print("[OK] All network fields parsed successfully!")

    return results


if __name__ == "__main__":
    log_file = project_root / "logs" / "cluster" / "task_1" / "response.log"

    print(
        "Testing Tasknetwork.from_json with network_before and network_after fields"
    )
    print("=" * 80)
    print()

    results = test_network_parsing(str(log_file))

    # Exit with error code if there were failures
    if results["failed_before_parsing"] > 0 or results["failed_after_parsing"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)
