#!/usr/bin/env python3

"""
End-to-end integration test for the Network framework orion system.

This test validates the complete flow from task orion creation through execution,
including DAG visualization at each step.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any

# Add the ALIEN2 directory to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Core framework imports
from network.orion.task_orion import TaskOrion
from network.orion.task_star import TaskStar
from network.orion.task_star_line import TaskStarLine
from network.orion.enums import OrionState, TaskPriority, TaskStatus

# Configure logging to be less verbose
import logging

logging.getLogger("alien").setLevel(logging.WARNING)


def print_with_color(message: str, color: str = "white"):
    """Simple color print function."""
    color_codes = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m",
    }

    color_code = color_codes.get(color, color_codes["white"])
    reset_code = color_codes["reset"]
    print(f"{color_code}{message}{reset_code}")


def test_basic_orion_workflow():
    """Test basic orion creation and visualization."""
    print_with_color(" Test 1: Basic orion workflow...", "cyan")

    try:
        # Create orion with visualization
        orion = TaskOrion(
            name="Integration Test Workflow", enable_visualization=True
        )

        # Create test tasks
        tasks = [
            TaskStar(
                task_id="setup_task",
                name="Environment Setup",
                description="Initialize the testing environment",
                priority=TaskPriority.HIGH,
            ),
            TaskStar(
                task_id="data_task",
                name="Data Preparation",
                description="Prepare test data",
                priority=TaskPriority.MEDIUM,
            ),
            TaskStar(
                task_id="process_task",
                name="Data Processing",
                description="Process the prepared data",
                priority=TaskPriority.MEDIUM,
            ),
            TaskStar(
                task_id="validate_task",
                name="Validation",
                description="Validate processing results",
                priority=TaskPriority.HIGH,
            ),
        ]

        # Add tasks
        for task in tasks:
            orion.add_task(task)

        # Add dependencies
        dependencies = [
            TaskStarLine.create_success_only(
                "setup_task", "data_task", "Setup required"
            ),
            TaskStarLine.create_success_only(
                "data_task", "process_task", "Data needed"
            ),
            TaskStarLine.create_success_only(
                "process_task", "validate_task", "Results needed"
            ),
        ]

        for dep in dependencies:
            orion.add_dependency(dep)

        print(f"[OK] Orion created: {orion.name}")
        print(f"[STATUS] Tasks: {orion.task_count}")
        print(f"[DEP] Dependencies: {len(orion.dependencies)}")

        # Test execution
        print_with_color("[START] Starting orion execution...", "yellow")
        orion.start_execution()

        # Simulate task completion
        orion.mark_task_completed("setup_task", True)
        orion.mark_task_completed("data_task", True)
        orion.mark_task_completed("process_task", True)
        orion.mark_task_completed("validate_task", True)

        orion.complete_execution()

        return True

    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_real_time_dag_updates():
    """Test real-time DAG updates during execution."""
    print_with_color(" Test 2: Real-time DAG updates during execution...", "cyan")

    try:
        # Create orion
        orion = TaskOrion(
            name="Dynamic Update Test", enable_visualization=True
        )

        # Add initial task
        initial_task = TaskStar(
            task_id="initial_task",
            name="Initial Task",
            description="Starting task for dynamic testing",
            priority=TaskPriority.MEDIUM,
        )
        orion.add_task(initial_task)

        # Start execution and simulate updates
        orion.start_execution()

        # Add more tasks dynamically
        for i in range(2, 5):
            new_task = TaskStar(
                task_id=f"dynamic_task_{i}",
                name=f"Dynamic Task {i}",
                description=f"Dynamically added task {i}",
                priority=TaskPriority.LOW,
            )
            orion.add_task(new_task)

            # Add dependency from previous task
            if i == 2:
                dep = TaskStarLine.create_success_only(
                    "initial_task", f"dynamic_task_{i}", "Sequential flow"
                )
            else:
                dep = TaskStarLine.create_success_only(
                    f"dynamic_task_{i-1}", f"dynamic_task_{i}", "Sequential flow"
                )
            orion.add_dependency(dep)

        # Complete tasks
        orion.mark_task_completed("initial_task", True)
        orion.mark_task_completed("dynamic_task_2", True)
        orion.mark_task_completed("dynamic_task_3", False)  # Simulate failure
        orion.mark_task_completed("dynamic_task_4", True)

        orion.complete_execution()

        print("[OK] Real-time updates test completed")
        return True

    except Exception as e:
        print(f"[FAIL] Real-time updates test failed: {e}")
        return False


def test_complex_dag_structure():
    """Test complex DAG structure with multiple dependencies."""
    print_with_color(" Test 3: Complex DAG structure...", "cyan")

    try:
        # Create orion
        orion = TaskOrion(
            name="Complex DAG Test", enable_visualization=True
        )

        # Create tasks for a complex workflow
        tasks = [
            TaskStar("start", "Start Process", "Initial task", TaskPriority.HIGH),
            TaskStar("fetch_a", "Fetch Data A", "Fetch dataset A", TaskPriority.MEDIUM),
            TaskStar("fetch_b", "Fetch Data B", "Fetch dataset B", TaskPriority.MEDIUM),
            TaskStar(
                "process_a", "Process A", "Process dataset A", TaskPriority.MEDIUM
            ),
            TaskStar(
                "process_b", "Process B", "Process dataset B", TaskPriority.MEDIUM
            ),
            TaskStar(
                "merge", "Merge Results", "Merge processed data", TaskPriority.HIGH
            ),
            TaskStar("validate", "Validate", "Validate merged data", TaskPriority.HIGH),
            TaskStar("deploy", "Deploy", "Deploy final results", TaskPriority.HIGH),
        ]

        # Add all tasks
        for task in tasks:
            orion.add_task(task)

        # Create complex dependencies
        deps = [
            TaskStarLine.create_success_only("start", "fetch_a", "Start triggers A"),
            TaskStarLine.create_success_only("start", "fetch_b", "Start triggers B"),
            TaskStarLine.create_success_only("fetch_a", "process_a", "Data A ready"),
            TaskStarLine.create_success_only("fetch_b", "process_b", "Data B ready"),
            TaskStarLine.create_success_only("process_a", "merge", "A processed"),
            TaskStarLine.create_success_only("process_b", "merge", "B processed"),
            TaskStarLine.create_success_only("merge", "validate", "Data merged"),
            TaskStarLine.create_success_only("validate", "deploy", "Validation passed"),
        ]

        for dep in deps:
            orion.add_dependency(dep)

        # Execute workflow
        orion.start_execution()

        # Simulate parallel execution
        orion.mark_task_completed("start", True)
        orion.mark_task_completed("fetch_a", True)
        orion.mark_task_completed("fetch_b", True)
        orion.mark_task_completed("process_a", True)
        orion.mark_task_completed("process_b", True)
        orion.mark_task_completed("merge", True)
        orion.mark_task_completed("validate", True)
        orion.mark_task_completed("deploy", True)

        orion.complete_execution()

        print("[OK] Complex DAG structure test completed")
        return True

    except Exception as e:
        print(f"[FAIL] Complex DAG test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and failure scenarios."""
    print_with_color(" Test 4: Error handling scenarios...", "cyan")

    try:
        # Create orion
        orion = TaskOrion(
            name="Error Handling Test", enable_visualization=True
        )

        # Create tasks that will include failures
        tasks = [
            TaskStar("task_1", "First Task", "Will succeed", TaskPriority.HIGH),
            TaskStar("task_2", "Second Task", "Will fail", TaskPriority.MEDIUM),
            TaskStar(
                "task_3", "Third Task", "Dependent on task_2", TaskPriority.MEDIUM
            ),
            TaskStar("task_4", "Fourth Task", "Independent task", TaskPriority.LOW),
        ]

        for task in tasks:
            orion.add_task(task)

        # Add dependencies
        deps = [
            TaskStarLine.create_success_only("task_1", "task_2", "Sequential"),
            TaskStarLine.create_success_only("task_2", "task_3", "Sequential"),
        ]

        for dep in deps:
            orion.add_dependency(dep)

        # Execute with failures
        orion.start_execution()

        orion.mark_task_completed("task_1", True)
        orion.mark_task_completed("task_2", False)  # This should fail
        orion.mark_task_completed("task_4", True)  # Independent task
        # task_3 should not be executed due to dependency failure

        orion.complete_execution()

        # Verify the state
        stats = orion.get_statistics()
        if stats["failed_tasks"] > 0 and stats["completed_tasks"] > 0:
            print("[OK] Error handling test completed - mixed results as expected")
            return True
        else:
            print("[FAIL] Error handling didn't work as expected")
            return False

    except Exception as e:
        print(f"[FAIL] Error handling test failed: {e}")
        return False


def save_test_results(results: Dict[str, Any]):
    """Save test results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"e2e_test_results_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f" Test results saved to: {filename}")


def main():
    """Run comprehensive integration tests."""
    print_with_color("[ORION] Network Framework E2E Integration Tests", "blue")
    print("=" * 60)

    start_time = time.time()

    # Test suite
    tests = [
        ("Basic Orion Workflow", test_basic_orion_workflow),
        ("Real-time DAG Updates", test_real_time_dag_updates),
        ("Complex DAG Structure", test_complex_dag_structure),
        ("Error Handling", test_error_handling),
    ]

    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(tests),
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": {},
    }

    # Run tests
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")

        try:
            test_start = time.time()
            success = test_func()
            test_time = time.time() - test_start

            results["test_details"][test_name] = {
                "status": "PASSED" if success else "FAILED",
                "execution_time": test_time,
            }

            if success:
                results["passed_tests"] += 1
                print_with_color(f"[OK] {test_name}: PASSED ({test_time:.2f}s)", "green")
            else:
                results["failed_tests"] += 1
                print_with_color(f"[FAIL] {test_name}: FAILED ({test_time:.2f}s)", "red")

        except Exception as e:
            results["failed_tests"] += 1
            results["test_details"][test_name] = {
                "status": "ERROR",
                "error": str(e),
                "execution_time": time.time() - test_start,
            }
            print_with_color(f" {test_name}: ERROR - {e}", "red")

    # Calculate final results
    total_time = time.time() - start_time
    success_rate = (results["passed_tests"] / results["total_tests"]) * 100

    results["total_execution_time"] = total_time
    results["success_rate"] = success_rate

    # Print summary
    print("\n" + "=" * 60)
    print_with_color("[ORION] Network Framework Test Summary:", "blue")
    print(f"   - Total tests: {results['total_tests']}")
    print(f"   - Successful: {results['passed_tests']}")
    print(f"   - Success rate: {success_rate:.1f}%")
    print(f"   - Total time: {total_time:.2f}s")

    # Save results
    save_test_results(results)

    # Print overall status
    if results["failed_tests"] == 0:
        print_with_color("\n OVERALL TEST SUITE SUMMARY:", "green")
        print("   - Orion Tests: [OK] SUCCESS")
        print("   - Network Framework Tests: [OK] SUCCESS")
        print(f"   - Total Execution Time: {total_time:.2f}s")
    else:
        print_with_color("\n️ OVERALL TEST SUITE SUMMARY:", "yellow")
        print(f"   - Tests Passed: {results['passed_tests']}")
        print(f"   - Tests Failed: {results['failed_tests']}")
        print(f"   - Success Rate: {success_rate:.1f}%")


if __name__ == "__main__":
    main()
