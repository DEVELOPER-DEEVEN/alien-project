# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Unit tests for cluster Agent State Machine

Tests cover all state transitions, edge cases, and error handling
for the network state machine implementation.
"""

import asyncio
import pytest
import time
import sys
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, Optional

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from cluster.agents.network_agent_states import (
    StartnetworkAgentState,
    MonitornetworkAgentState,
    FinishnetworkAgentState,
    FailnetworkAgentState,
    networkAgentStateManager,
    networkAgentStatus,
)
from tests.cluster.mocks import MocknetworkAgent
from cluster.network import Tasknetwork, TaskStar, TaskStatus
from cluster.network.enums import networkState, TaskPriority
from cluster.network.task_star_line import TaskStarLine
from cluster.core.events import TaskEvent, EventType
from Alien.module.context import Context


class TestAgentStateMachine:
    """Test the agent state machine implementation."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = MocknetworkAgent()
        agent.current_request = "Test request"
        agent.orchestrator = Mock()
        agent.orchestrator.orchestrate_network = AsyncMock()
        agent.logger = Mock()
        return agent

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing."""
        return Mock(spec=Context)

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

    @pytest.mark.asyncio
    async def test_start_state_success(
        self, mock_agent, mock_context, simple_network
    ):
        """Test successful start state execution."""
        # Arrange
        state = StartnetworkAgentState()
        mock_agent.process_initial_request = AsyncMock(
            return_value=simple_network
        )

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "executing"
        assert mock_agent.current_network == simple_network
        assert mock_agent._orchestration_task is not None
        mock_agent.orchestrator.orchestrate_network.assert_called_once_with(
            simple_network
        )

    @pytest.mark.asyncio
    async def test_start_state_no_network(self, mock_agent, mock_context):
        """Test start state when network creation fails."""
        # Arrange
        state = StartnetworkAgentState()
        mock_agent.process_initial_request = AsyncMock(return_value=None)

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "failed"
        assert mock_agent.current_network is None

    @pytest.mark.asyncio
    async def test_start_state_exception(self, mock_agent, mock_context):
        """Test start state with exception."""
        # Arrange
        state = StartnetworkAgentState()
        mock_agent.process_initial_request = AsyncMock(
            side_effect=Exception("Test error")
        )

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "failed"

    def test_start_state_transitions(self, mock_agent):
        """Test start state transitions."""
        state = StartnetworkAgentState()

        # Test transition to fail
        mock_agent._status = "failed"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, FailnetworkAgentState)

        # Test transition to finish
        mock_agent._status = "finished"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, FinishnetworkAgentState)

        # Test transition to monitor
        mock_agent._status = "executing"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, MonitornetworkAgentState)

    @pytest.mark.asyncio
    async def test_monitor_state_task_completion(
        self, mock_agent, mock_context, simple_network
    ):
        """Test monitor state handling task completion."""
        # Arrange
        state = MonitornetworkAgentState()
        mock_agent._current_network = simple_network
        mock_agent.task_completion_queue = asyncio.Queue()
        mock_agent.update_network_with_lock = AsyncMock(
            return_value=simple_network
        )
        mock_agent.should_continue = AsyncMock(return_value=False)

        # Create task event
        task_event = TaskEvent(
            event_type=EventType.TASK_COMPLETED,
            source_id="test_orchestrator",
            timestamp=time.time(),
            data={},
            task_id="task1",
            status="completed",
            result={"success": True},
            error=None,
        )

        # Put event in queue
        await mock_agent.task_completion_queue.put(task_event)

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        mock_agent.update_network_with_lock.assert_called_once()
        mock_agent.should_continue.assert_called_once()

    @pytest.mark.asyncio
    async def test_monitor_state_continue_processing(
        self, mock_agent, mock_context, simple_network
    ):
        """Test monitor state when agent decides to continue."""
        # Arrange
        state = MonitornetworkAgentState()
        mock_agent._current_network = simple_network
        mock_agent.task_completion_queue = asyncio.Queue()
        mock_agent.update_network_with_lock = AsyncMock(
            return_value=simple_network
        )
        mock_agent.should_continue = AsyncMock(return_value=True)

        # Set network state to completed but agent wants to continue
        simple_network._state = networkState.COMPLETED

        # Create task event
        task_event = TaskEvent(
            event_type=EventType.TASK_COMPLETED,
            source_id="test_orchestrator",
            timestamp=time.time(),
            data={},
            task_id="task1",
            status="completed",
            result={"success": True},
            error=None,
        )

        await mock_agent.task_completion_queue.put(task_event)

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "continue"

    @pytest.mark.asyncio
    async def test_monitor_state_agent_decides_finish(
        self, mock_agent, mock_context, simple_network
    ):
        """Test monitor state when agent decides task is finished."""
        # Arrange
        state = MonitornetworkAgentState()
        mock_agent._current_network = simple_network
        mock_agent.task_completion_queue = asyncio.Queue()
        mock_agent.update_network_with_lock = AsyncMock(
            return_value=simple_network
        )
        mock_agent.should_continue = AsyncMock(return_value=False)

        # Set network to completed
        simple_network._state = networkState.COMPLETED

        # Create task event
        task_event = TaskEvent(
            event_type=EventType.TASK_COMPLETED,
            source_id="test_orchestrator",
            timestamp=time.time(),
            data={},
            task_id="task1",
            status="completed",
            result={"success": True},
            error=None,
        )

        await mock_agent.task_completion_queue.put(task_event)

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "finished"

    @pytest.mark.asyncio
    async def test_monitor_state_exception_handling(self, mock_agent, mock_context):
        """Test monitor state exception handling."""
        # Arrange
        state = MonitornetworkAgentState()
        mock_agent.task_completion_queue = asyncio.Queue()
        mock_agent.update_network_with_lock = AsyncMock(
            side_effect=Exception("Test error")
        )

        # Create task event
        task_event = TaskEvent(
            event_type=EventType.TASK_COMPLETED,
            source_id="test_orchestrator",
            timestamp=time.time(),
            data={},
            task_id="task1",
            status="completed",
            result={"success": True},
            error=None,
        )

        await mock_agent.task_completion_queue.put(task_event)

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "failed"

    def test_monitor_state_transitions(self, mock_agent):
        """Test monitor state transitions."""
        state = MonitornetworkAgentState()

        # Test transition to fail
        mock_agent._status = "failed"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, FailnetworkAgentState)

        # Test transition to finish
        mock_agent._status = "finished"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, FinishnetworkAgentState)

        # Test transition to continue (restart)
        mock_agent._status = "continue"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, StartnetworkAgentState)

        # Test stay in monitor
        mock_agent._status = "monitoring"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, MonitornetworkAgentState)

    @pytest.mark.asyncio
    async def test_finish_state(self, mock_agent, mock_context):
        """Test finish state execution."""
        # Arrange
        state = FinishnetworkAgentState()
        mock_agent._orchestration_task = Mock()
        mock_agent._orchestration_task.done.return_value = False

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "finished"
        mock_agent._orchestration_task.cancel.assert_called_once()
        assert state.is_round_end()
        assert state.is_subtask_end()

    @pytest.mark.asyncio
    async def test_fail_state(self, mock_agent, mock_context):
        """Test fail state execution."""
        # Arrange
        state = FailnetworkAgentState()
        mock_agent._orchestration_task = Mock()
        mock_agent._orchestration_task.done.return_value = False

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "failed"
        mock_agent._orchestration_task.cancel.assert_called_once()
        assert state.is_round_end()
        assert state.is_subtask_end()

    def test_state_manager(self):
        """Test state manager functionality."""
        manager = networkAgentStateManager()

        # Test none_state
        none_state = manager.none_state
        assert isinstance(none_state, StartnetworkAgentState)

        # Test state registration
        assert (
            StartnetworkAgentState.name() == networkAgentStatus.START.value
        )
        assert (
            MonitornetworkAgentState.name()
            == networkAgentStatus.MONITOR.value
        )
        assert (
            FinishnetworkAgentState.name()
            == networkAgentStatus.FINISH.value
        )
        assert FailnetworkAgentState.name() == networkAgentStatus.FAIL.value

    def test_state_properties(self):
        """Test state properties."""
        start_state = StartnetworkAgentState()
        assert not start_state.is_round_end()
        assert not start_state.is_subtask_end()

        monitor_state = MonitornetworkAgentState()
        assert not monitor_state.is_round_end()
        assert not monitor_state.is_subtask_end()

        finish_state = FinishnetworkAgentState()
        assert finish_state.is_round_end()
        assert finish_state.is_subtask_end()

        fail_state = FailnetworkAgentState()
        assert fail_state.is_round_end()
        assert fail_state.is_subtask_end()


class TestTaskTimeoutConfiguration:
    """Test task timeout configuration in start state."""

    @pytest.fixture
    def mock_config(self):
        """Mock config for timeout testing."""
        config_data = {
            "cluster_TASK_TIMEOUT": 1800.0,
            "cluster_CRITICAL_TASK_TIMEOUT": 3600.0,
        }

        with patch("Alien.config.Config.get_instance") as mock_config_instance:
            mock_config_instance.return_value.config_data = config_data
            yield config_data

    @pytest.fixture
    def simple_network(self):
        """Create simple network for testing."""
        network = Tasknetwork("test_network")
        task1 = TaskStar("task1", "Test task 1", TaskPriority.MEDIUM)
        task2 = TaskStar("task2", "Test task 2", TaskPriority.MEDIUM)
        network.add_task(task1)
        network.add_task(task2)

        # Create dependency using TaskStarLine
        dependency = TaskStarLine.create_unconditional("task1", "task2")
        network.add_dependency(dependency)
        return network

    @pytest.mark.asyncio
    async def test_timeout_configuration(self, mock_config, simple_network):
        """Test task timeout configuration."""
        # Arrange
        state = StartnetworkAgentState()

        # Set different priorities
        task1 = simple_network.tasks["task1"]
        task2 = simple_network.tasks["task2"]
        task1.priority = TaskPriority.HIGH  # Should get critical timeout
        task2.priority = TaskPriority.LOW  # Should get default timeout

        # Clear existing timeouts
        task1._timeout = None
        task2._timeout = None

        # Act
        state._configure_task_timeouts(simple_network)

        # Assert
        assert task1._timeout == 3600.0  # Critical timeout
        assert task2._timeout == 1800.0  # Default timeout

    @pytest.mark.asyncio
    async def test_timeout_configuration_preserves_existing(
        self, mock_config, simple_network
    ):
        """Test that existing timeouts are preserved."""
        # Arrange
        state = StartnetworkAgentState()
        task1 = simple_network.tasks["task1"]
        task1._timeout = 5000.0  # Existing timeout

        # Act
        state._configure_task_timeouts(simple_network)

        # Assert
        assert task1._timeout == 5000.0  # Should preserve existing


class TestAgentIntegration:
    """Test agent integration with state machine."""

    @pytest.fixture
    def agent_with_states(self):
        """Create agent with state machine support."""
        agent = MocknetworkAgent()
        agent.orchestrator = Mock()
        agent.orchestrator.orchestrate_network = AsyncMock()
        return agent

    @pytest.fixture
    def simple_network(self):
        """Create simple network for testing."""
        network = Tasknetwork("test_network")
        task1 = TaskStar("task1", "Test task 1", TaskPriority.MEDIUM)
        task2 = TaskStar("task2", "Test task 2", TaskPriority.MEDIUM)
        network.add_task(task1)
        network.add_task(task2)

        # Create dependency using TaskStarLine
        dependency = TaskStarLine.create_unconditional("task1", "task2")
        network.add_dependency(dependency)
        return network

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_with_states):
        """Test agent initializes with correct state."""
        assert isinstance(agent_with_states.state, StartnetworkAgentState)
        assert hasattr(agent_with_states, "task_completion_queue")
        assert hasattr(agent_with_states, "current_request")
        assert hasattr(agent_with_states, "orchestrator")

    @pytest.mark.asyncio
    async def test_agent_status_manager(self, agent_with_states):
        """Test agent status manager."""
        manager = agent_with_states.status_manager
        assert isinstance(manager, networkAgentStateManager)

    @pytest.mark.asyncio
    async def test_full_state_cycle_success(
        self, agent_with_states, simple_network
    ):
        """Test full successful state cycle."""
        # Mock methods
        agent_with_states.process_initial_request = AsyncMock(
            return_value=simple_network
        )
        agent_with_states.update_network_with_lock = AsyncMock(
            return_value=simple_network
        )
        agent_with_states.should_continue = AsyncMock(return_value=False)

        # Start -> Monitor (simulate task completion) -> Finish

        # 1. Start state
        assert isinstance(agent_with_states.state, StartnetworkAgentState)
        await agent_with_states.handle(None)

        # Should transition to monitor
        next_state = agent_with_states.state.next_state(agent_with_states)
        agent_with_states.set_state(next_state)
        assert isinstance(agent_with_states.state, MonitornetworkAgentState)

        # 2. Monitor state - add task completion event
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

        await agent_with_states.task_completion_queue.put(task_event)
        simple_network._state = networkState.COMPLETED

        await agent_with_states.handle(None)

        # Should transition to finish
        next_state = agent_with_states.state.next_state(agent_with_states)
        agent_with_states.set_state(next_state)
        assert isinstance(agent_with_states.state, FinishnetworkAgentState)

        # 3. Finish state
        await agent_with_states.handle(None)
        assert agent_with_states._status == "finished"
        assert agent_with_states.state.is_round_end()

    @pytest.mark.asyncio
    async def test_full_state_cycle_with_continue(
        self, agent_with_states, simple_network
    ):
        """Test state cycle with continuation."""
        # Mock methods
        agent_with_states.process_initial_request = AsyncMock(
            return_value=simple_network
        )
        agent_with_states.update_network_with_lock = AsyncMock(
            return_value=simple_network
        )
        agent_with_states.should_continue = AsyncMock(return_value=True)

        # Start -> Monitor -> Continue -> Start (again)

        # 1. Start state
        await agent_with_states.handle(None)
        next_state = agent_with_states.state.next_state(agent_with_states)
        agent_with_states.set_state(next_state)

        # 2. Monitor state with continuation
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

        await agent_with_states.task_completion_queue.put(task_event)
        simple_network._state = networkState.COMPLETED

        await agent_with_states.handle(None)

        # Should transition back to start
        next_state = agent_with_states.state.next_state(agent_with_states)
        assert isinstance(next_state, StartnetworkAgentState)
        assert agent_with_states._status == "continue"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
