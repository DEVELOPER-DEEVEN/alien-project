#!/usr/bin/env python3
"""
Network Session Test Runner

Convenient script to run all Network Session tests from the tests directory.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def run_test(test_file, description):
    """Run a single test file and report results."""
    print(f"\n{'=' * 60}")
    print(f" Running: {description}")
    print(f" File: {test_file}")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.returncode == 0:
            print(f"[OK] {description} - PASSED")
            return True
        else:
            print(f"[FAIL] {description} - FAILED (exit code: {result.returncode})")
            return False

    except Exception as e:
        print(f"[FAIL] {description} - ERROR: {e}")
        return False


def main():
    """Run all Network Session tests."""
    print("[START] Network Session Test Suite Runner")
    print("=" * 60)

    tests = [
        (
            "test_network_session_proper_mock.py",
            "Proper Mocking Tests",
        ),
        (
            "test_session_observers.py",
            "Session Observer Tests",
        ),
        (
            "test_session_visualization_integration.py",
            "Session-Visualization Integration",
        ),
        (
            "test_dag_visualization_observer_events.py",
            "DAG Visualization Observer Event Tests",
        ),
        (
            "test_color_fix.py",
            "Color Display Fix Tests",
        ),
        (
            "test_network_framework_summary.py",
            "Network Framework Summary",
        ),
    ]

    passed = 0
    total = len(tests)

    for test_file, description in tests:
        if os.path.exists(test_file):
            if run_test(test_file, description):
                passed += 1
        else:
            print(f"️  Test file not found: {test_file}")

    print(f"\n{'=' * 60}")
    print(f"[STATUS] Test Results: {passed}/{total} tests passed")

    if passed == total:
        print(" All tests passed!")
        return 0
    else:
        print("[FAIL] Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
