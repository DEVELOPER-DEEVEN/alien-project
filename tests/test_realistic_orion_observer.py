
"""
Integration test to debug why OrionAgent logging doesn't work in real network session.
"""

import asyncio
import logging
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from network.session.observers.base_observer import OrionProgressObserver
from network.agents.orion_agent import OrionAgent
from network.core.events import TaskEvent, EventType, get_event_bus
from network.orion.orchestrator.orchestrator import (
    TaskOrionOrchestrator,
)


class TestRealisticsOrionObserverLogger:
    """Test class to verify logging behavior in realistic conditions."""

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

    @pytest.mark.asyncio
    async def test_realistic_scenario_with_logging_levels(
        self, mock_orchestrator, task_event, caplog
    ):
        """Test with realistic logging level configurations."""

        print(f"\n=== TESTING REALISTIC LOGGING SCENARIO ===")

        # Set different logging levels to simulate real environment
        caplog.set_level(logging.DEBUG)

        # Get the event bus
        event_bus = get_event_bus()

        # Create orion agent
        orion_agent = OrionAgent(orchestrator=mock_orchestrator)

        # Create observer
        observer = OrionProgressObserver(agent=orion_agent)

        print(f"Agent logger name: {orion_agent.logger.name}")
        print(f"Agent logger level: {orion_agent.logger.level}")
        print(
            f"Agent logger effective level: {orion_agent.logger.getEffectiveLevel()}"
        )

        # Clear logs
        caplog.clear()

        # Manually set the logger level to INFO to match real environment
        orion_agent.logger.setLevel(logging.INFO)
        observer.logger.setLevel(logging.INFO)

        print(f"After setting INFO level:")
        print(
            f"Agent logger effective level: {orion_agent.logger.getEffectiveLevel()}"
        )
        print(f"Observer logger effective level: {observer.logger.getEffectiveLevel()}")

        # Test the flow
        await observer.on_event(task_event)

        # Check captured logs
        observer_logs = [
            record for record in caplog.records if "Task progress:" in record.message
        ]
        agent_logs = [
            record
            for record in caplog.records
            if "Added task event for task" in record.message
        ]

        print(f"\n=== CAPTURED LOGS WITH INFO LEVEL ===")
        for i, record in enumerate(caplog.records):
            print(
                f"{i+1}. [{record.levelname}] {record.name}:{record.filename}:{record.lineno} - {record.message}"
            )

        print(f"\nObserver logs: {len(observer_logs)}")
        print(f"Agent logs: {len(agent_logs)}")

        if len(agent_logs) == 0:
            print("❌ Agent log still missing with INFO level!")
        else:
            print("✅ Agent log appears with INFO level")

    @pytest.mark.asyncio
    async def test_with_method_wrapping_to_check_calls(
        self, mock_orchestrator, task_event, caplog
    ):
        """Test by wrapping the add_task_completion_event method to see if it's called."""

        print(f"\n=== TESTING WITH METHOD WRAPPING ===")

        caplog.set_level(logging.INFO)
        caplog.clear()

        # Create orion agent
        orion_agent = OrionAgent(orchestrator=mock_orchestrator)

        # Wrap the method to track calls
        original_method = orion_agent.add_task_completion_event
        call_count = 0

        async def wrapped_add_task_completion_event(event):
            nonlocal call_count
            call_count += 1
            print(f"🔍 add_task_completion_event called! Count: {call_count}")
            print(f"🔍 Event type: {event.event_type}")
            print(f"🔍 Task ID: {event.task_id}")
            print(f"🔍 Status: {event.status}")

            # Call original method
            result = await original_method(event)

            print(f"🔍 Original method completed")
            return result

        orion_agent.add_task_completion_event = (
            wrapped_add_task_completion_event
        )

        # Create observer
        observer = OrionProgressObserver(agent=orion_agent)

        # Test the flow
        await observer.on_event(task_event)

        print(f"\n=== RESULTS ===")
        print(f"Method called {call_count} times")

        if call_count == 0:
            print("❌ CRITICAL: add_task_completion_event was never called!")
            print(
                "This means the issue is in the observer logic, not the agent logging"
            )
        else:
            print("✅ add_task_completion_event was called correctly")

        # Check the logs regardless
        agent_logs = [
            record
            for record in caplog.records
            if "Added task event for task" in record.message
        ]
        print(f"Agent logs captured: {len(agent_logs)}")

    @pytest.mark.asyncio
    async def test_exception_handling_in_observer(
        self, mock_orchestrator, task_event, caplog
    ):
        """Test if exceptions in add_task_completion_event are silently caught."""

        print(f"\n=== TESTING EXCEPTION HANDLING ===")

        caplog.set_level(logging.INFO)
        caplog.clear()

        # Create orion agent
        orion_agent = OrionAgent(orchestrator=mock_orchestrator)

        # Mock add_task_completion_event to raise an exception
        orion_agent.add_task_completion_event = AsyncMock(
            side_effect=Exception("Test exception")
        )

        # Create observer
        observer = OrionProgressObserver(agent=orion_agent)

        # Test the flow - should not raise exception
        try:
            await observer.on_event(task_event)
            print("✅ Observer handled exception gracefully")
        except Exception as e:
            print(f"❌ Observer did not handle exception: {e}")

        # Check if the method was called
        orion_agent.add_task_completion_event.assert_called_once()
        print("✅ add_task_completion_event was called despite exception")

    @pytest.mark.asyncio
    async def test_event_type_filtering(self, mock_orchestrator, caplog):
        """Test if event filtering is working correctly."""

        print(f"\n=== TESTING EVENT TYPE FILTERING ===")

        caplog.set_level(logging.INFO)
        caplog.clear()

        # Create orion agent with mock
        orion_agent = OrionAgent(orchestrator=mock_orchestrator)
        orion_agent.add_task_completion_event = AsyncMock()

        # Create observer
        observer = OrionProgressObserver(agent=orion_agent)

        # Test with TASK_STARTED (should not call add_task_completion_event)
        task_started_event = TaskEvent(
            event_type=EventType.TASK_STARTED,
            source_id="test_source",
            timestamp=time.time(),
            data={"orion_id": "test_orion"},
            task_id="task-collect-logs-2",
            status="started",
        )

        await observer.on_event(task_started_event)

        # Should not be called for TASK_STARTED
        orion_agent.add_task_completion_event.assert_not_called()
        print("✅ TASK_STARTED correctly does not call add_task_completion_event")

        # Test with TASK_COMPLETED (should call add_task_completion_event)
        task_completed_event = TaskEvent(
            event_type=EventType.TASK_COMPLETED,
            source_id="test_source",
            timestamp=time.time(),
            data={"orion_id": "test_orion"},
            task_id="task-collect-logs-2",
            status="completed",
        )

        await observer.on_event(task_completed_event)

        # Should be called once for TASK_COMPLETED
        orion_agent.add_task_completion_event.assert_called_once()
        print("✅ TASK_COMPLETED correctly calls add_task_completion_event")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
