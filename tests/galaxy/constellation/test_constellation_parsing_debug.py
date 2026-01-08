"""
Debug script to examine the network_before and network_after fields
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def debug_network_fields(log_file_path: str):
    """Debug the network fields to see their actual format"""

    print(f"Reading log file: {log_file_path}\n")

    with open(log_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        try:
            log_entry = json.loads(line.strip())

            print(f"=" * 80)
            print(f"LINE {line_num}")
            print(f"=" * 80)

            # Check network_before
            if "network_before" in log_entry:
                const_before = log_entry["network_before"]
                print(f"\nnetwork_before:")
                print(f"  Type: {type(const_before)}")
                if const_before:
                    print(f"  Is None: False")
                    if isinstance(const_before, str):
                        print(f"  Length: {len(const_before)}")
                        print(f"  First 200 chars: {const_before[:200]}")
                        # Try to detect if it's JSON or Python repr
                        if const_before.strip().startswith("{"):
                            print(f"  Format: Looks like JSON")
                            try:
                                parsed = json.loads(const_before)
                                print(f"  [OK] Valid JSON")
                            except json.JSONDecodeError as e:
                                print(f"  [FAIL] Invalid JSON: {e}")
                        else:
                            print(f"  Format: Looks like Python repr/str")
                else:
                    print(f"  Is None: True")

            # Check network_after
            if "network_after" in log_entry:
                const_after = log_entry["network_after"]
                print(f"\nnetwork_after:")
                print(f"  Type: {type(const_after)}")
                if const_after:
                    print(f"  Is None: False")
                    if isinstance(const_after, str):
                        print(f"  Length: {len(const_after)}")
                        print(f"  First 200 chars: {const_after[:200]}")
                        # Try to detect if it's JSON or Python repr
                        if const_after.strip().startswith("{"):
                            print(f"  Format: Looks like JSON")
                            try:
                                parsed = json.loads(const_after)
                                print(f"  [OK] Valid JSON")
                            except json.JSONDecodeError as e:
                                print(f"  [FAIL] Invalid JSON: {e}")
                        else:
                            print(f"  Format: Looks like Python repr/str")
                else:
                    print(f"  Is None: True")

            print()

        except json.JSONDecodeError as e:
            print(f"Line {line_num}: Failed to parse JSON: {e}\n")


if __name__ == "__main__":
    log_file = project_root / "logs" / "cluster" / "task_1" / "response.log"
    debug_network_fields(str(log_file))
