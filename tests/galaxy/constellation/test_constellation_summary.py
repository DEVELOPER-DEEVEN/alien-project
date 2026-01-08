"""
Summary of network parsing test results from response.log

ISSUE IDENTIFIED:
================
The network_before field in lines 2-5 contains INVALID data where the "tasks"
field is a Python string representation instead of a proper JSON object/dict.

WORKING CASES:
- Line 1: network_after [OK] (tasks is dict)
- Line 2: network_after [OK] (tasks is dict)
- Line 3: network_after [OK] (tasks is dict)
- Line 4: network_after [OK] (tasks is dict)

FAILING CASES:
- Line 2: network_before [FAIL] (tasks is string: "{'t1': {...}}")
- Line 3: network_before [FAIL] (tasks is string: "{'t1': {...}}")
- Line 4: network_before [FAIL] (tasks is string: "{'t1': {...}}")
- Line 5: network_before [FAIL] (tasks is string: "{'t1': {...}}")
- Line 5: network_after [FAIL] (tasks is string: "{'t1': {...}}")

ROOT CAUSE:
===========
When creating network_before, the code is using str() or repr() on the tasks
dictionary instead of properly serializing it to JSON. This results in:

  WRONG:  "tasks": "{'t1': {'task_id': 't1', ...}}"  <- Python str representation
  RIGHT:  "tasks": {"t1": {"task_id": "t1", ...}}    <- Proper JSON

IMPACT:
=======
Tasknetwork.from_json() CANNOT parse network_before from lines 2-5
because from_dict() expects tasks to be a dictionary, not a string.

RECOMMENDATION:
===============
Fix the code that generates network_before to use json.dumps() or
Tasknetwork.to_json() instead of str() or repr().

The issue is likely in the code that logs network_before. Look for:
  - str(network.to_dict())
  - repr(network.to_dict())
  - or manual dictionary construction with str() on nested objects

Should be:
  - network.to_json()
  - json.dumps(network.to_dict())
"""

print(__doc__)

# Now let's verify with actual test
import json
import sys
from pathlib import Path

# Add project root to path (go up 3 levels: network -> cluster -> tests -> root)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from cluster.network.task_network import Tasknetwork


def test_working_vs_broken():
    """Test both working and broken cases"""

    log_file = project_root / "logs" / "cluster" / "task_1" / "response.log"
    with open(log_file, "r") as f:
        lines = f.readlines()

    print("\n" + "=" * 80)
    print("ACTUAL TEST RESULTS")
    print("=" * 80 + "\n")

    # Test working case: Line 1 network_after
    print("[OK] WORKING CASE: Line 1 - network_after")
    log1 = json.loads(lines[0])
    const_after_str = log1["network_after"]
    try:
        network = Tasknetwork.from_json(json_data=const_after_str)
        print(f"  Successfully parsed!")
        print(f"  - ID: {network.network_id}")
        print(f"  - Tasks: {network.task_count}")
        print(f"  - State: {network.state.value}\n")
    except Exception as e:
        print(f"  Failed: {e}\n")

    # Test broken case: Line 2 network_before
    print("[FAIL] BROKEN CASE: Line 2 - network_before")
    log2 = json.loads(lines[1])
    const_before_str = log2["network_before"]
    try:
        network = Tasknetwork.from_json(json_data=const_before_str)
        print(f"  Unexpectedly succeeded!\n")
    except Exception as e:
        print(f"  Failed as expected: {type(e).__name__}: {e}\n")

    # Show the problematic data
    print("=" * 80)
    print("PROBLEMATIC DATA EXAMPLE (Line 2 network_before)")
    print("=" * 80)
    const_before = json.loads(const_before_str)
    print(f"Type of 'tasks' field: {type(const_before['tasks'])}")
    print(f"Value (first 300 chars): {str(const_before['tasks'])[:300]}...")


if __name__ == "__main__":
    test_working_vs_broken()
