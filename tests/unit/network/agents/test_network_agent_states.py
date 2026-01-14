
"""
Unit tests for Network Agent State Machine

Tests cover all state transitions, edge cases, and error handling
for the Orion state machine implementation.
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

from network.agents.orion_agent_states import (
    StartOrionAgentState,
    MonitorOrionAgentState,
    FinishOrionAgentState,
    FailOrionAgentState,
    OrionAgentStateManager,
    OrionAgentStatus,
)
from tests.network.mocks import MockOrionAgent
from network.orion import TaskOrion, TaskStar, TaskStatus
from network.orion.enums import OrionState, TaskPriority
from network.orion.task_star_line import TaskStarLine
from network.core.events import TaskEvent, EventType
from alien.module.context import Context


class TestAgentStateMachine:
    """Test the agent state machine implementation."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = MockOrionAgent()
        agent.current_request = "Test request"
        agent.orchestrator = Mock()
        agent.orchestrator.orchestrate_orion = AsyncMock()
        agent.logger = Mock()
        return agent

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing."""
        return Mock(spec=Context)

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

    @pytest.mark.asyncio
    async def test_start_state_success(
        self, mock_agent, mock_context, simple_orion
    ):
        """Test successful start state execution."""
        # Arrange
        state = StartOrionAgentState()
        mock_agent.process_initial_request = AsyncMock(
            return_value=simple_orion
        )

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "executing"
        assert mock_agent.current_orion == simple_orion
        assert mock_agent._orchestration_task is not None
        mock_agent.orchestrator.orchestrate_orion.assert_called_once_with(
            simple_orion
        )

    @pytest.mark.asyncio
    async def test_start_state_no_orion(self, mock_agent, mock_context):
        """Test start state when orion creation fails."""
        # Arrange
        state = StartOrionAgentState()
        mock_agent.process_initial_request = AsyncMock(return_value=None)

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "failed"
        assert mock_agent.current_orion is None

    @pytest.mark.asyncio
    async def test_start_state_exception(self, mock_agent, mock_context):
        """Test start state with exception."""
        # Arrange
        state = StartOrionAgentState()
        mock_agent.process_initial_request = AsyncMock(
            side_effect=Exception("Test error")
        )

        # Act
        await state.handle(mock_agent, mock_context)

        # Assert
        assert mock_agent._status == "failed"

    def test_start_state_transitions(self, mock_agent):
        """Test start state transitions."""
        state = StartOrionAgentState()

        # Test transition to fail
        mock_agent._status = "failed"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, FailOrionAgentState)

        # Test transition to finish
        mock_agent._status = "finished"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, FinishOrionAgentState)

        # Test transition to monitor
        mock_agent._status = "executing"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, MonitorOrionAgentState)

    @pytest.mark.asyncio
    async def test_monitor_state_task_completion(
        self, mock_agent, mock_context, simple_orion
    ):
        """Test monitor state handling task completion."""
        # Arrange
        state = MonitorOrionAgentState()
        mock_agent._current_orion = simple_orion
        mock_agent.task_completion_queue = asyncio.Queue()
        mock_agent.update_orion_with_lock = AsyncMock(
            return_value=simple_orion
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
        mock_agent.update_orion_with_lock.assert_called_once()
        mock_agent.should_continue.assert_called_once()

    @pytest.mark.asyncio
    async def test_monitor_state_continue_processing(
        self, mock_agent, mock_context, simple_orion
    ):
        """Test monitor state when agent decides to continue."""
        # Arrange
        state = MonitorOrionAgentState()
        mock_agent._current_orion = simple_orion
        mock_agent.task_completion_queue = asyncio.Queue()
        mock_agent.update_orion_with_lock = AsyncMock(
            return_value=simple_orion
        )
        mock_agent.should_continue = AsyncMock(return_value=True)

        # Set orion state to completed but agent wants to continue
        simple_orion._state = OrionState.COMPLETED

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
        self, mock_agent, mock_context, simple_orion
    ):
        """Test monitor state when agent decides task is finished."""
        # Arrange
        state = MonitorOrionAgentState()
        mock_agent._current_orion = simple_orion
        mock_agent.task_completion_queue = asyncio.Queue()
        mock_agent.update_orion_with_lock = AsyncMock(
            return_value=simple_orion
        )
        mock_agent.should_continue = AsyncMock(return_value=False)

        # Set orion to completed
        simple_orion._state = OrionState.COMPLETED

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
        state = MonitorOrionAgentState()
        mock_agent.task_completion_queue = asyncio.Queue()
        mock_agent.update_orion_with_lock = AsyncMock(
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
        state = MonitorOrionAgentState()

        # Test transition to fail
        mock_agent._status = "failed"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, FailOrionAgentState)

        # Test transition to finish
        mock_agent._status = "finished"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, FinishOrionAgentState)

        # Test transition to continue (restart)
        mock_agent._status = "continue"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, StartOrionAgentState)

        # Test stay in monitor
        mock_agent._status = "monitoring"
        next_state = state.next_state(mock_agent)
        assert isinstance(next_state, MonitorOrionAgentState)

    @pytest.mark.asyncio
    async def test_finish_state(self, mock_agent, mock_context):
        """Test finish state execution."""
        # Arrange
        state = FinishOrionAgentState()
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
        state = FailOrionAgentState()
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
        manager = OrionAgentStateManager()

        # Test none_state
        none_state = manager.none_state
        assert isinstance(none_state, StartOrionAgentState)

        # Test state registration
        assert (
            StartOrionAgentState.name() == OrionAgentStatus.START.value
        )
        assert (
            MonitorOrionAgentState.name()
            == OrionAgentStatus.MONITOR.value
        )
        assert (
            FinishOrionAgentState.name()
            == OrionAgentStatus.FINISH.value
        )
        assert FailOrionAgentState.name() == OrionAgentStatus.FAIL.value

    def test_state_properties(self):
        """Test state properties."""
        start_state = StartOrionAgentState()
        assert not start_state.is_round_end()
        assert not start_state.is_subtask_end()

        monitor_state = MonitorOrionAgentState()
        assert not monitor_state.is_round_end()
        assert not monitor_state.is_subtask_end()

        finish_state = FinishOrionAgentState()
        assert finish_state.is_round_end()
        assert finish_state.is_subtask_end()

        fail_state = FailOrionAgentState()
        assert fail_state.is_round_end()
        assert fail_state.is_subtask_end()


class TestTaskTimeoutConfiguration:
    """Test task timeout configuration in start state."""

    @pytest.fixture
    def mock_config(self):
        """Mock config for timeout testing."""
        config_data = {
            "NETWORK_TASK_TIMEOUT": 1800.0,
            "NETWORK_CRITICAL_TASK_TIMEOUT": 3600.0,
        }

        with patch("alien.config.Config.get_instance") as mock_config_instance:
            mock_config_instance.return_value.config_data = config_data
            yield config_data

    @pytest.fixture
    def simple_orion(self):
        """Create simple orion for testing."""
        orion = TaskOrion("test_orion")
        task1 = TaskStar("task1", "Test task 1", TaskPriority.MEDIUM)
        task2 = TaskStar("task2", "Test task 2", TaskPriority.MEDIUM)
        orion.add_task(task1)
        orion.add_task(task2)

        # Create dependency using TaskStarLine
        dependency = TaskStarLine.create_unconditional("task1", "task2")
        orion.add_dependency(dependency)
        return orion

    @pytest.mark.asyncio
    async def test_timeout_configuration(self, mock_config, simple_orion):
        """Test task timeout configuration."""
        # Arrange
        state = StartOrionAgentState()

        # Set different priorities
        task1 = simple_orion.tasks["task1"]
        task2 = simple_orion.tasks["task2"]
        task1.priority = TaskPriority.HIGH  # Should get critical timeout
        task2.priority = TaskPriority.LOW  # Should get default timeout

        # Clear existing timeouts
        task1._timeout = None
        task2._timeout = None

        # Act
        state._configure_task_timeouts(simple_orion)

        # Assert
        assert task1._timeout == 3600.0  # Critical timeout
        assert task2._timeout == 1800.0  # Default timeout

    @pytest.mark.asyncio
    async def test_timeout_configuration_preserves_existing(
        self, mock_config, simple_orion
    ):
        """Test that existing timeouts are preserved."""
        # Arrange
        state = StartOrionAgentState()
        task1 = simple_orion.tasks["task1"]
        task1._timeout = 5000.0  # Existing timeout

        # Act
        state._configure_task_timeouts(simple_orion)

        # Assert
        assert task1._timeout == 5000.0  # Should preserve existing


class TestAgentIntegration:
    """Test agent integration with state machine."""

    @pytest.fixture
    def agent_with_states(self):
        """Create agent with state machine support."""
        agent = MockOrionAgent()
        agent.orchestrator = Mock()
        agent.orchestrator.orchestrate_orion = AsyncMock()
        return agent

    @pytest.fixture
    def simple_orion(self):
        """Create simple orion for testing."""
        orion = TaskOrion("test_orion")
        task1 = TaskStar("task1", "Test task 1", TaskPriority.MEDIUM)
        task2 = TaskStar("task2", "Test task 2", TaskPriority.MEDIUM)
        orion.add_task(task1)
        orion.add_task(task2)

        # Create dependency using TaskStarLine
        dependency = TaskStarLine.create_unconditional("task1", "task2")
        orion.add_dependency(dependency)
        return orion

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_with_states):
        """Test agent initializes with correct state."""
        assert isinstance(agent_with_states.state, StartOrionAgentState)
        assert hasattr(agent_with_states, "task_completion_queue")
        assert hasattr(agent_with_states, "current_request")
        assert hasattr(agent_with_states, "orchestrator")

    @pytest.mark.asyncio
    async def test_agent_status_manager(self, agent_with_states):
        """Test agent status manager."""
        manager = agent_with_states.status_manager
        assert isinstance(manager, OrionAgentStateManager)

    @pytest.mark.asyncio
    async def test_full_state_cycle_success(
        self, agent_with_states, simple_orion
    ):
        """Test full successful state cycle."""
        # Mock methods
        agent_with_states.process_initial_request = AsyncMock(
            return_value=simple_orion
        )
        agent_with_states.update_orion_with_lock = AsyncMock(
            return_value=simple_orion
        )
        agent_with_states.should_continue = AsyncMock(return_value=False)

        # Start -> Monitor (simulate task completion) -> Finish

        # 1. Start state
        assert isinstance(agent_with_states.state, StartOrionAgentState)
        await agent_with_states.handle(None)

        # Should transition to monitor
        next_state = agent_with_states.state.next_state(agent_with_states)
        agent_with_states.set_state(next_state)
        assert isinstance(agent_with_states.state, MonitorOrionAgentState)

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
        simple_orion._state = OrionState.COMPLETED

        await agent_with_states.handle(None)

        # Should transition to finish
        next_state = agent_with_states.state.next_state(agent_with_states)
        agent_with_states.set_state(next_state)
        assert isinstance(agent_with_states.state, FinishOrionAgentState)

        # 3. Finish state
        await agent_with_states.handle(None)
        assert agent_with_states._status == "finished"
        assert agent_with_states.state.is_round_end()

    @pytest.mark.asyncio
    async def test_full_state_cycle_with_continue(
        self, agent_with_states, simple_orion
    ):
        """Test state cycle with continuation."""
        # Mock methods
        agent_with_states.process_initial_request = AsyncMock(
            return_value=simple_orion
        )
        agent_with_states.update_orion_with_lock = AsyncMock(
            return_value=simple_orion
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
        simple_orion._state = OrionState.COMPLETED

        await agent_with_states.handle(None)

        # Should transition back to start
        next_state = agent_with_states.state.next_state(agent_with_states)
        assert isinstance(next_state, StartOrionAgentState)
        assert agent_with_states._status == "continue"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
