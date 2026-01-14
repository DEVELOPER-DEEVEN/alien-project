
"""
Test to verify why OrionProgressObserver logs but OrionAgent add_task_completion_event doesn't log.
"""

import asyncio
import logging
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from network.session.observers.base_observer import OrionProgressObserver
from network.agents.orion_agent import OrionAgent
from network.core.events import TaskEvent, EventType
from network.orion.orchestrator.orchestrator import (
    TaskOrionOrchestrator,
)


class TestOrionObserverLogger:
    """Test class to verify logging behavior between observer and agent."""

    @pytest.fixture
    def task_event(self):
        """Create a test task event."""
        return TaskEvent(
            event_type=EventType.TASK_COMPLETED,
            source_id="test_source",
            timestamp=time.time(),
            data={"orion_id": "test_orion"},
            task_id="task-collect-logs-2",
            status="completed",
            result={"success": True},
            error=None,
        )

    @pytest.fixture
    def mock_orchestrator(self):
        """Create a mock orchestrator."""
        orchestrator = Mock(spec=TaskOrionOrchestrator)
        orchestrator.start = AsyncMock()
        orchestrator.stop = AsyncMock()
        return orchestrator

    @pytest.fixture
    def orion_agent(self, mock_orchestrator):
        """Create a OrionAgent instance."""
        agent = OrionAgent(orchestrator=mock_orchestrator)
        # Mock the add_task_completion_event method to capture calls
        agent.add_task_completion_event = AsyncMock(
            wraps=agent.add_task_completion_event
        )
        return agent

    @pytest.fixture
    def observer(self, orion_agent):
        """Create a OrionProgressObserver instance."""
        return OrionProgressObserver(agent=orion_agent)

    @pytest.mark.asyncio
    async def test_observer_calls_agent_add_task_completion_event(
        self, observer, orion_agent, task_event, caplog
    ):
        """Test that observer calls agent's add_task_completion_event method."""

        # Set up logging to capture both observer and agent logs
        caplog.set_level(logging.INFO)

        # Clear any existing logs
        caplog.clear()

        # Trigger the observer to handle the task event
        await observer.on_event(task_event)

        # Verify that the agent's add_task_completion_event was called
        orion_agent.add_task_completion_event.assert_called_once()

        # Get the actual call arguments
        call_args = orion_agent.add_task_completion_event.call_args
        actual_event = call_args[0][0]  # First positional argument

        # Verify the event is correct
        assert actual_event.task_id == "task-collect-logs-2"
        assert actual_event.status == "completed"
        assert actual_event.event_type == EventType.TASK_COMPLETED

        # Check what logs were captured
        observer_logs = [
            record for record in caplog.records if "Task progress:" in record.message
        ]
        agent_logs = [
            record
            for record in caplog.records
            if "Added task event for task" in record.message
        ]

        print(f"\n=== ALL CAPTURED LOGS ===")
        for i, record in enumerate(caplog.records):
            print(
                f"{i+1}. {record.name}:{record.filename}:{record.lineno} - {record.message}"
            )

        print(f"\n=== OBSERVER LOGS ===")
        for log in observer_logs:
            print(f"Observer: {log.message}")

        print(f"\n=== AGENT LOGS ===")
        for log in agent_logs:
            print(f"Agent: {log.message}")

        # Verify observer log exists
        assert len(observer_logs) == 1
        assert "task-collect-logs-2" in observer_logs[0].message
        assert "completed" in observer_logs[0].message

        # This is the test to see if agent log exists
        print(f"\nAgent logs count: {len(agent_logs)}")
        if len(agent_logs) == 0:
            print(
                "❌ PROBLEM FOUND: Agent's add_task_completion_event logger did not produce any logs!"
            )
        else:
            print("✅ Agent's add_task_completion_event logger works correctly")

    @pytest.mark.asyncio
    async def test_direct_agent_add_task_completion_event_logging(
        self, orion_agent, task_event, caplog
    ):
        """Test calling add_task_completion_event directly to isolate the logging issue."""

        # Set up logging to capture agent logs
        caplog.set_level(logging.INFO)
        caplog.clear()

        print(f"\n=== TESTING DIRECT CALL TO add_task_completion_event ===")
        print(f"Agent logger name: {orion_agent.logger.name}")
        print(f"Agent logger level: {orion_agent.logger.level}")
        print(
            f"Agent logger effective level: {orion_agent.logger.getEffectiveLevel()}"
        )
        print(f"Agent logger handlers: {orion_agent.logger.handlers}")
        print(f"Agent logger propagate: {orion_agent.logger.propagate}")

        # Call the method directly
        await orion_agent.add_task_completion_event(task_event)

        # Check captured logs
        agent_logs = [
            record
            for record in caplog.records
            if "Added task event for task" in record.message
        ]

        print(f"\n=== ALL CAPTURED LOGS FROM DIRECT CALL ===")
        for i, record in enumerate(caplog.records):
            print(
                f"{i+1}. {record.name}:{record.filename}:{record.lineno} - {record.message}"
            )

        print(f"\nDirect agent logs count: {len(agent_logs)}")
        if len(agent_logs) == 0:
            print(
                "❌ PROBLEM CONFIRMED: Direct call to add_task_completion_event doesn't log either!"
            )
            print(
                "This suggests the issue is with the logger configuration in OrionAgent"
            )
        else:
            print("✅ Direct call works - issue might be elsewhere")

    @pytest.mark.asyncio
    async def test_logger_configuration_comparison(
        self, observer, orion_agent, caplog
    ):
        """Compare logger configurations between observer and agent."""

        print(f"\n=== LOGGER CONFIGURATION COMPARISON ===")

        print(f"\nObserver logger:")
        print(f"  Name: {observer.logger.name}")
        print(f"  Level: {observer.logger.level}")
        print(f"  Effective level: {observer.logger.getEffectiveLevel()}")
        print(f"  Handlers: {observer.logger.handlers}")
        print(f"  Propagate: {observer.logger.propagate}")

        print(f"\nAgent logger:")
        print(f"  Name: {orion_agent.logger.name}")
        print(f"  Level: {orion_agent.logger.level}")
        print(f"  Effective level: {orion_agent.logger.getEffectiveLevel()}")
        print(f"  Handlers: {orion_agent.logger.handlers}")
        print(f"  Propagate: {orion_agent.logger.propagate}")

        # Test if both loggers can actually log
        caplog.set_level(logging.INFO)
        caplog.clear()

        observer.logger.info("TEST: Observer logger test message")
        orion_agent.logger.info("TEST: Agent logger test message")

        observer_test_logs = [
            record
            for record in caplog.records
            if "Observer logger test message" in record.message
        ]
        agent_test_logs = [
            record
            for record in caplog.records
            if "Agent logger test message" in record.message
        ]

        print(f"\nTest message results:")
        print(f"  Observer test logs captured: {len(observer_test_logs)}")
        print(f"  Agent test logs captured: {len(agent_test_logs)}")

        if len(observer_test_logs) > 0 and len(agent_test_logs) == 0:
            print(
                "❌ ISSUE FOUND: Agent logger is not properly configured for capturing logs!"
            )
        elif len(observer_test_logs) == 0 and len(agent_test_logs) == 0:
            print("❌ ISSUE: Both loggers are not capturing - might be caplog issue")
        else:
            print("✅ Both loggers work for test messages")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
