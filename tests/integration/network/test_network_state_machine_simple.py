
"""
Simplified Integration tests for Network Agent State Machine

Focuses on testing the core state machine logic without complex orchestration.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from network.agents.network_agent import MockNetworkWeaverAgent
from network.agents.network_agent_states import (
    StartNetworkAgentState,
    MonitorNetworkAgentState,
    FinishNetworkAgentState,
    FailNetworkAgentState,
)
from network.orion import TaskOrion, TaskStar, TaskStatus
from network.orion.task_star_line import TaskStarLine
from network.orion.enums import OrionState, TaskPriority
from network.core.events import TaskEvent, EventType
from alien.module.context import Context


class TestNetworkAgentStateMachineSimple:
    """Simplified tests for agent state machine core functionality."""

    @pytest.fixture
    def simple_orion(self):
        """Create a simple orion for testing."""
        orion = TaskOrion("test_orion")
        task1 = TaskStar("task1", "Test task 1", TaskPriority.MEDIUM)
        task2 = TaskStar("task2", "Test task 2", TaskPriority.MEDIUM)
        orion.add_task(task1)
        orion.add_task(task2)

        # Create dependency using TaskStarLine
        dependency = TaskStarLine.create_unconditional("task1", "task2")
        orion.add_dependency(dependency)
        return orion

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = MockNetworkWeaverAgent()
        agent.orchestrator = Mock()
        agent.orchestrator.orchestrate_orion = AsyncMock()
        return agent

    @pytest.mark.asyncio
    async def test_agent_completes_successfully(self, simple_orion, mock_agent):
        """Test that agent completes successfully when orion is done."""
        # Setup
        mock_agent.process_initial_request = AsyncMock(
            return_value=simple_orion
        )
        mock_agent.update_orion_with_lock = AsyncMock(
            return_value=simple_orion
        )
        mock_agent.should_continue = AsyncMock(return_value=False)

        # Simulate the orion completing
        simple_orion._state = OrionState.COMPLETED

        # Run the state machine cycle manually
        # 1. Start state
        assert isinstance(mock_agent.state, StartNetworkAgentState)
        await mock_agent.handle(None)

        # Should transition to monitor
        next_state = mock_agent.state.next_state(mock_agent)
        mock_agent.set_state(next_state)
        assert isinstance(mock_agent.state, MonitorNetworkAgentState)

        # 2. Simulate task completion event
        task_event = TaskEvent(
            event_type=EventType.TASK_COMPLETED,
            source_id="test",
            timestamp=time.time(),
            data={},
            task_id="task1",
            status="completed",
            result={"success": True},
            error=None,
        )
        await mock_agent.task_completion_queue.put(task_event)

        # Handle monitor state with timeout
        try:
            await asyncio.wait_for(mock_agent.handle(None), timeout=1.0)
        except asyncio.TimeoutError:
            pytest.fail("Monitor state timed out - possible deadlock")

        # Should transition to finish
        next_state = mock_agent.state.next_state(mock_agent)
        mock_agent.set_state(next_state)
        assert isinstance(mock_agent.state, FinishNetworkAgentState)

        # 3. Finish state
        await mock_agent.handle(None)
        assert mock_agent._status == "finished"

    @pytest.mark.asyncio
    async def test_agent_continues_processing(self, simple_orion, mock_agent):
        """Test that agent continues when it decides to add more tasks."""
        # Setup
        mock_agent.process_initial_request = AsyncMock(
            return_value=simple_orion
        )
        mock_agent.update_orion_with_lock = AsyncMock(
            return_value=simple_orion
        )
        mock_agent.should_continue = AsyncMock(
            return_value=True
        )  # Agent wants to continue

        # Simulate the orion completing
        simple_orion._state = OrionState.COMPLETED

        # Run the state machine cycle
        await mock_agent.handle(None)
        next_state = mock_agent.state.next_state(mock_agent)
        mock_agent.set_state(next_state)

        # Add task completion event
        task_event = TaskEvent(
            event_type=EventType.TASK_COMPLETED,
            source_id="test",
            timestamp=time.time(),
            data={},
            task_id="task1",
            status="completed",
            result={"success": True},
            error=None,
        )
        await mock_agent.task_completion_queue.put(task_event)

        # Handle monitor state with timeout
        try:
            await asyncio.wait_for(mock_agent.handle(None), timeout=1.0)
        except asyncio.TimeoutError:
            pytest.fail("Monitor state timed out - possible deadlock")

        # Should transition back to start (continue processing)
        next_state = mock_agent.state.next_state(mock_agent)
        assert isinstance(next_state, StartNetworkAgentState)
        assert mock_agent._status == "continue"

    @pytest.mark.asyncio
    async def test_agent_handles_failure(self, simple_orion, mock_agent):
        """Test that agent handles failures properly."""
        # Setup - mock process_initial_request to fail
        mock_agent.process_initial_request = AsyncMock(
            side_effect=Exception("Test error")
        )

        # Run start state which should fail
        await mock_agent.handle(None)

        # Should transition to fail state
        assert mock_agent._status == "failed"
        next_state = mock_agent.state.next_state(mock_agent)
        mock_agent.set_state(next_state)
        assert isinstance(mock_agent.state, FailNetworkAgentState)

        # Run fail state
        await mock_agent.handle(None)
        assert mock_agent._status == "failed"
