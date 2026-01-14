"""
Summary of orion parsing test results from response.log

ISSUE IDENTIFIED:
================
The orion_before field in lines 2-5 contains INVALID data where the "tasks"
field is a Python string representation instead of a proper JSON object/dict.

WORKING CASES:
- Line 1: orion_after [OK] (tasks is dict)
- Line 2: orion_after [OK] (tasks is dict)
- Line 3: orion_after [OK] (tasks is dict)
- Line 4: orion_after [OK] (tasks is dict)

FAILING CASES:
- Line 2: orion_before [FAIL] (tasks is string: "{'t1': {...}}")
- Line 3: orion_before [FAIL] (tasks is string: "{'t1': {...}}")
- Line 4: orion_before [FAIL] (tasks is string: "{'t1': {...}}")
- Line 5: orion_before [FAIL] (tasks is string: "{'t1': {...}}")
- Line 5: orion_after [FAIL] (tasks is string: "{'t1': {...}}")

ROOT CAUSE:
===========
When creating orion_before, the code is using str() or repr() on the tasks
dictionary instead of properly serializing it to JSON. This results in:

  WRONG:  "tasks": "{'t1': {'task_id': 't1', ...}}"  <- Python str representation
  RIGHT:  "tasks": {"t1": {"task_id": "t1", ...}}    <- Proper JSON

IMPACT:
=======
TaskOrion.from_json() CANNOT parse orion_before from lines 2-5
because from_dict() expects tasks to be a dictionary, not a string.

RECOMMENDATION:
===============
Fix the code that generates orion_before to use json.dumps() or
TaskOrion.to_json() instead of str() or repr().

The issue is likely in the code that logs orion_before. Look for:
  - str(orion.to_dict())
  - repr(orion.to_dict())
  - or manual dictionary construction with str() on nested objects

Should be:
  - orion.to_json()
  - json.dumps(orion.to_dict())
"""

print(__doc__)

# Now let's verify with actual test
import json
import sys
from pathlib import Path

# Add project root to path (go up 3 levels: orion -> network -> tests -> root)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from network.orion.task_orion import TaskOrion


def test_working_vs_broken():
    """Test both working and broken cases"""

    log_file = project_root / "logs" / "network" / "task_1" / "response.log"
    with open(log_file, "r") as f:
        lines = f.readlines()

    print("\n" + "=" * 80)
    print("ACTUAL TEST RESULTS")
    print("=" * 80 + "\n")

    # Test working case: Line 1 orion_after
    print("[OK] WORKING CASE: Line 1 - orion_after")
    log1 = json.loads(lines[0])
    const_after_str = log1["orion_after"]
    try:
        orion = TaskOrion.from_json(json_data=const_after_str)
        print(f"  Successfully parsed!")
        print(f"  - ID: {orion.orion_id}")
        print(f"  - Tasks: {orion.task_count}")
        print(f"  - State: {orion.state.value}\n")
    except Exception as e:
        print(f"  Failed: {e}\n")

    # Test broken case: Line 2 orion_before
    print("[FAIL] BROKEN CASE: Line 2 - orion_before")
    log2 = json.loads(lines[1])
    const_before_str = log2["orion_before"]
    try:
        orion = TaskOrion.from_json(json_data=const_before_str)
        print(f"  Unexpectedly succeeded!\n")
    except Exception as e:
        print(f"  Failed as expected: {type(e).__name__}: {e}\n")

    # Show the problematic data
    print("=" * 80)
    print("PROBLEMATIC DATA EXAMPLE (Line 2 orion_before)")
    print("=" * 80)
    const_before = json.loads(const_before_str)
    print(f"Type of 'tasks' field: {type(const_before['tasks'])}")
    print(f"Value (first 300 chars): {str(const_before['tasks'])[:300]}...")


if __name__ == "__main__":
    test_working_vs_broken()
