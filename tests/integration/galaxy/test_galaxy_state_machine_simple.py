# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Simplified Integration tests for cluster Agent State Machine

Focuses on testing the core state machine logic without complex orchestration.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from cluster.agents.cluster_agent import MockclusterWeaverAgent
from cluster.agents.cluster_agent_states import (
    StartclusterAgentState,
    MonitorclusterAgentState,
    FinishclusterAgentState,
    FailclusterAgentState,
)
from cluster.network import Tasknetwork, TaskStar, TaskStatus
from cluster.network.task_star_line import TaskStarLine
from cluster.network.enums import networkState, TaskPriority
from cluster.core.events import TaskEvent, EventType
from Alien.module.context import Context


class TestclusterAgentStateMachineSimple:
    """Simplified tests for agent state machine core functionality."""

    @pytest.fixture
    def simple_network(self):
        """Create a simple network for testing."""
        network = Tasknetwork("test_network")
        task1 = TaskStar("task1", "Test task 1", TaskPriority.MEDIUM)
        task2 = TaskStar("task2", "Test task 2", TaskPriority.MEDIUM)
        network.add_task(task1)
        network.add_task(task2)

        # Create dependency using TaskStarLine
        dependency = TaskStarLine.create_unconditional("task1", "task2")
        network.add_dependency(dependency)
        return network

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = MockclusterWeaverAgent()
        agent.orchestrator = Mock()
        agent.orchestrator.orchestrate_network = AsyncMock()
        return agent

    @pytest.mark.asyncio
    async def test_agent_completes_successfully(self, simple_network, mock_agent):
        """Test that agent completes successfully when network is done."""
        # Setup
        mock_agent.process_initial_request = AsyncMock(
            return_value=simple_network
        )
        mock_agent.update_network_with_lock = AsyncMock(
            return_value=simple_network
        )
        mock_agent.should_continue = AsyncMock(return_value=False)

        # Simulate the network completing
        simple_network._state = networkState.COMPLETED

        # Run the state machine cycle manually
        # 1. Start state
        assert isinstance(mock_agent.state, StartclusterAgentState)
        await mock_agent.handle(None)

        # Should transition to monitor
        next_state = mock_agent.state.next_state(mock_agent)
        mock_agent.set_state(next_state)
        assert isinstance(mock_agent.state, MonitorclusterAgentState)

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
        assert isinstance(mock_agent.state, FinishclusterAgentState)

        # 3. Finish state
        await mock_agent.handle(None)
        assert mock_agent._status == "finished"

    @pytest.mark.asyncio
    async def test_agent_continues_processing(self, simple_network, mock_agent):
        """Test that agent continues when it decides to add more tasks."""
        # Setup
        mock_agent.process_initial_request = AsyncMock(
            return_value=simple_network
        )
        mock_agent.update_network_with_lock = AsyncMock(
            return_value=simple_network
        )
        mock_agent.should_continue = AsyncMock(
            return_value=True
        )  # Agent wants to continue

        # Simulate the network completing
        simple_network._state = networkState.COMPLETED

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
        assert isinstance(next_state, StartclusterAgentState)
        assert mock_agent._status == "continue"

    @pytest.mark.asyncio
    async def test_agent_handles_failure(self, simple_network, mock_agent):
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
        assert isinstance(mock_agent.state, FailclusterAgentState)

        # Run fail state
        await mock_agent.handle(None)
        assert mock_agent._status == "failed"
