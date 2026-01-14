"""
Test script to validate if orion_before and orion_after fields
from response.log can be parsed by TaskOrion.from_json
"""

import json
import sys
from pathlib import Path

# Add project root to path (go up 3 levels: orion -> network -> tests -> root)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from network.orion.task_orion import TaskOrion


def test_orion_parsing(log_file_path: str):
    """Test parsing orion_before and orion_after from log file"""

    print(f"Reading log file: {log_file_path}\n")

    with open(log_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"Total lines in log file: {len(lines)}\n")

    results = {
        "total_lines": len(lines),
        "lines_with_orion_before": 0,
        "lines_with_orion_after": 0,
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

            # Check for orion_before
            if (
                "orion_before" in log_entry
                and log_entry["orion_before"]
            ):
                results["lines_with_orion_before"] += 1
                orion_before_str = log_entry["orion_before"]

                print(f"Line {line_num}: Testing orion_before...")
                try:
                    # Test parsing with from_json
                    orion = TaskOrion.from_json(
                        json_data=orion_before_str
                    )
                    results["successful_before_parsing"] += 1
                    print(f"  [OK] Successfully parsed orion_before")
                    print(f"    - Orion ID: {orion.orion_id}")
                    print(f"    - Tasks: {orion.task_count}")
                    print(f"    - Dependencies: {orion.dependency_count}")
                    print(f"    - State: {orion.state.value}")
                except Exception as e:
                    results["failed_before_parsing"] += 1
                    error_msg = f"Line {line_num} - orion_before parsing failed: {type(e).__name__}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"  [FAIL] Failed to parse orion_before: {e}")

            # Check for orion_after
            if "orion_after" in log_entry and log_entry["orion_after"]:
                results["lines_with_orion_after"] += 1
                orion_after_str = log_entry["orion_after"]

                print(f"Line {line_num}: Testing orion_after...")
                try:
                    # Test parsing with from_json
                    orion = TaskOrion.from_json(
                        json_data=orion_after_str
                    )
                    results["successful_after_parsing"] += 1
                    print(f"  [OK] Successfully parsed orion_after")
                    print(f"    - Orion ID: {orion.orion_id}")
                    print(f"    - Tasks: {orion.task_count}")
                    print(f"    - Dependencies: {orion.dependency_count}")
                    print(f"    - State: {orion.state.value}")
                except Exception as e:
                    results["failed_after_parsing"] += 1
                    error_msg = f"Line {line_num} - orion_after parsing failed: {type(e).__name__}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"  [FAIL] Failed to parse orion_after: {e}")

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
        f"Lines with orion_before: {results['lines_with_orion_before']}"
    )
    print(
        f"Lines with orion_after: {results['lines_with_orion_after']}"
    )
    print()
    print(f"orion_before parsing:")
    print(f"  - Successful: {results['successful_before_parsing']}")
    print(f"  - Failed: {results['failed_before_parsing']}")
    print()
    print(f"orion_after parsing:")
    print(f"  - Successful: {results['successful_after_parsing']}")
    print(f"  - Failed: {results['failed_after_parsing']}")
    print()

    if results["errors"]:
        print("ERRORS:")
        print("-" * 80)
        for error in results["errors"]:
            print(f"  {error}")
    else:
        print("[OK] All orion fields parsed successfully!")

    return results


if __name__ == "__main__":
    log_file = project_root / "logs" / "network" / "task_1" / "response.log"

    print(
        "Testing TaskOrion.from_json with orion_before and orion_after fields"
    )
    print("=" * 80)
    print()

    results = test_orion_parsing(str(log_file))

    # Exit with error code if there were failures
    if results["failed_before_parsing"] > 0 or results["failed_after_parsing"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)
