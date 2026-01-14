#!/usr/bin/env python3

"""
Mock implementations for Network Orion framework testing.

This module provides mock implementations of Network framework components
for testing purposes, without requiring actual LLM integration or external dependencies.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union

from network.agents.orion_agent import OrionAgent
from network.orion.orchestrator.orchestrator import (
    TaskOrionOrchestrator,
)
from network.core.events import get_event_bus, OrionEvent, EventType
from network.orion import TaskOrion, TaskStar
from network.orion.enums import OrionState, TaskPriority
from alien.module.context import Context, ContextNames


def create_simple_test_orion(
    task_descriptions: List[str],
    orion_name: str = "TestOrion",
    sequential: bool = True,
) -> TaskOrion:
    """
    Create a simple orion for testing purposes.

    :param task_descriptions: List of task descriptions
    :param orion_name: Name for the orion
    :param sequential: Whether tasks should be sequential
    :return: Created orion
    """
    orion = TaskOrion(
        orion_id=orion_name,
        name=orion_name,
    )

    tasks = []
    for i, desc in enumerate(task_descriptions):
        task = TaskStar(
            task_id=f"task_{i+1}",
            description=desc,
            priority=TaskPriority.MEDIUM,
        )
        tasks.append(task)
        orion.add_task(task)

    # Add sequential dependencies if requested
    if sequential and len(tasks) > 1:
        from network.orion.task_star_line import TaskStarLine

        for i in range(len(tasks) - 1):
            dependency = TaskStarLine(
                from_task_id=tasks[i].task_id, to_task_id=tasks[i + 1].task_id
            )
            orion.add_dependency(dependency)

    return orion


class MockOrionAgent(OrionAgent):
    """
    Mock implementation of Orion for testing and demonstration.

    This implementation provides basic DAG generation and update logic
    for testing the Network framework without requiring actual LLM integration.
    """

    def __init__(
        self,
        orchestrator: TaskOrionOrchestrator,
        name: str = "mock_orion_agent",
    ):
        """
        Initialize the MockOrionAgent.

        :param orchestrator: Task orchestrator instance
        :param name: Agent name (default: "mock_orion_agent")
        """
        super().__init__(orchestrator, name)

    def message_constructor(self) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        """
        Construct the message for LLM interaction.

        Returns:
            List of message dictionaries for LLM
        """
        return [
            {
                "role": "system",
                "content": "You are a mock Orion for testing purposes.",
            },
            {
                "role": "user",
                "content": "Mock user message for testing Network framework integration.",
            },
        ]

    async def process_confirmation(self, context: Context) -> bool:
        """
        Mock process confirmation.

        :param context: Processing context
        :return: Always returns True for mock
        """
        return True

    async def process_creation(
        self,
        context: Context,
    ) -> TaskOrion:
        """
        Process a user request and generate a orion (Mock implementation).

        :param context: Processing context
        :return: Generated orion
        :raises OrionError: If orion generation fails
        """
        # Get request from context or use a default
        request = "mock request"
        if context and hasattr(context, "get"):
            try:
                request = context.get(ContextNames.REQUEST) or "mock request"
            except (TypeError, AttributeError):
                request = "mock request"

        self.logger.info(f"Mock processing creation request: {request[:100]}...")

        # Generate tasks based on request content
        if "complex" in request.lower():
            tasks = [
                "Analyze user request and identify requirements",
                "Break down complex requirements into subtasks",
                "Design system architecture",
                "Implement core functionality",
                "Test and validate implementation",
                "Deploy and monitor system",
            ]
        elif "parallel" in request.lower():
            tasks = [
                "Initialize parallel processing framework",
                "Process data stream A",
                "Process data stream B",
                "Process data stream C",
                "Aggregate and finalize results",
            ]
        else:
            tasks = [
                "Understand user request",
                "Plan execution strategy",
                "Execute primary task",
                "Validate results",
            ]

        orion = create_simple_test_orion(
            task_descriptions=tasks,
            orion_name=f"MockDAG_{request[:20]}",
            sequential=True,
        )

        self._current_orion = orion
        self.status = "CONTINUE"

        self.logger.info(
            f"Generated mock orion with {orion.task_count} tasks"
        )

        return orion

    async def process_editing(
        self,
        context: Context = None,
    ) -> TaskOrion:
        """
        Process a task result and potentially update the orion (Mock implementation).

        :param context: Processing context
        :return: Updated orion
        :raises TaskExecutionError: If result processing fails
        """
        self.logger.info("Mock processing editing request...")

        if not self._current_orion:
            self.logger.warning("No current orion to edit in mock agent")
            return await self.process_creation(context)

        # Store before orion for event publishing
        before_orion = self._current_orion

        # Mock task result processing
        task_result = {
            "task_id": "mock_task",
            "status": "completed",
            "result": {"recommendations": ["optimize_performance", "add_monitoring"]},
        }

        orion = self._current_orion
        task_id = task_result.get("task_id")
        status = task_result.get("status")
        result_data = task_result.get("result", {})

        self.logger.info(f"Mock processing result for task {task_id}: {status}")

        # Enhanced logic for dynamic task generation based on result content
        if status == "completed" and isinstance(result_data, dict):
            new_tasks_added = 0

            # Check for specific triggers in the result
            if "trigger_tasks" in result_data:
                # Explicit task triggers from result
                for task_name in result_data["trigger_tasks"]:
                    new_task_id = f"{task_name}_{int(time.time() * 1000) % 10000}"
                    new_task = TaskStar(
                        task_id=new_task_id,
                        description=f"Execute {task_name.replace('_', ' ')} as triggered by {task_id}",
                        priority=TaskPriority.MEDIUM,
                    )

                    if new_task_id not in orion.tasks:
                        orion.add_task(new_task)
                        new_tasks_added += 1
                        self.logger.info(f"Added triggered task: {new_task_id}")

            # Check for recommendations in results
            if "recommendations" in result_data:
                for i, recommendation in enumerate(
                    result_data["recommendations"][:2]
                ):  # Limit to 2
                    rec_task = TaskStar(
                        task_id=f"implement_{recommendation}_{int(time.time() * 1000) % 10000}",
                        description=f"Implement recommendation: {recommendation.replace('_', ' ')}",
                        priority=TaskPriority.MEDIUM,
                    )
                    if rec_task.task_id not in orion.tasks:
                        orion.add_task(rec_task)
                        new_tasks_added += 1
                        self.logger.info(
                            f"Added recommendation task: {rec_task.task_id}"
                        )

            if new_tasks_added > 0:
                self.logger.info(
                    f"Total new tasks added based on mock result analysis: {new_tasks_added}"
                )

        # Handle error cases
        elif status == "failed" or "error" in str(result_data).lower():
            # Add error recovery task
            recovery_task = TaskStar(
                task_id=f"recovery_{task_id}_{int(time.time() * 1000) % 10000}",
                description=f"Handle error recovery for {task_id}",
                priority=TaskPriority.HIGH,
            )

            # Only add if not already exists and orion is not finished
            if (
                recovery_task.task_id not in orion.tasks
                and orion.state
                not in [OrionState.COMPLETED, OrionState.FAILED]
            ):
                orion.add_task(recovery_task)
                self.logger.info(f"Added recovery task: {recovery_task.task_id}")

        # Update agent status based on orion state
        stats = orion.get_statistics()
        status_counts = stats.get("task_status_counts", {})

        completed_tasks = status_counts.get("completed", 0)
        failed_tasks = status_counts.get("failed", 0)
        total_tasks = orion.task_count

        if (
            completed_tasks + failed_tasks >= total_tasks * 0.8
        ):  # 80% completion threshold
            if failed_tasks > completed_tasks * 0.3:  # More than 30% failed
                self.status = "FAIL"
            elif completed_tasks >= total_tasks * 0.9:  # 90% completed successfully
                self.status = "FINISH"
            else:
                self.status = "CONTINUE"
        else:
            self.status = "CONTINUE"

        # Publish DAG Modified Event for mock agent
        await self._event_bus.publish_event(
            OrionEvent(
                event_type=EventType.ORION_MODIFIED,
                source_id=self.name,
                timestamp=time.time(),
                data={
                    "old_orion": before_orion,
                    "new_orion": orion,
                    "modification_type": "mock_agent_processing",
                },
                orion_id=orion.orion_id,
                orion_state=(
                    orion.state.value if orion.state else "unknown"
                ),
            )
        )

        return orion


class MockTaskOrionOrchestrator:
    """Mock orchestrator for testing."""

    def __init__(self, device_manager=None, enable_logging=True):
        self.device_manager = device_manager
        self.enable_logging = enable_logging
        self.orion = None

    async def execute_orion(self, orion):
        """Mock execution of orion."""
        if self.enable_logging:
            print(
                f" Mock orchestrator executing orion: {orion.orion_id}"
            )

        # Mock execution by just returning success
        return {"status": "completed", "tasks_executed": orion.task_count}
