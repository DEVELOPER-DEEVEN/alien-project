#!/usr/bin/env python3

"""
Run all cancellation-related tests.

This script runs all unit and integration tests for the task cancellation mechanism.
"""

import subprocess
import sys
from pathlib import Path

# Test files to run
TEST_FILES = [
    "tests/network/client/test_network_client_cancellation.py",
    "tests/network/session/test_session_cancellation.py",
    "tests/network/orion/test_orchestrator_cancellation.py",
    "tests/network/webui/test_webui_stop_integration.py",
]


def run_tests():
    """Run all cancellation tests."""
    print("=" * 80)
    print("Running Task Cancellation Tests")
    print("=" * 80)
    print()

    all_passed = True

    for test_file in TEST_FILES:
        print(f"\n{'=' * 80}")
        print(f"Running: {test_file}")
        print(f"{'=' * 80}\n")

        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "-s"],
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode != 0:
            all_passed = False
            print(f"\n[FAIL] FAILED: {test_file}\n")
        else:
            print(f"\n[OK] PASSED: {test_file}\n")

    print("\n" + "=" * 80)
    if all_passed:
        print("[OK] All cancellation tests PASSED!")
    else:
        print("[FAIL] Some tests FAILED. Please check the output above.")
    print("=" * 80)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_tests())
