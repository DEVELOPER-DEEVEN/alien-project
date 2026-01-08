# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
 [Text Cleaned] ：cluster [Text Cleaned] 

 [Text Cleaned] ：
1. clusterAgentState [Text Cleaned] 
2. clusterAgentStateManager [Text Cleaned] 
3. MonitoringclusterAgentState [Text Cleaned] 
4. Observer [Text Cleaned] 
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from cluster.agents.cluster_agent_state import (
    clusterAgentStatus,
    clusterAgentState,
    CreatingclusterAgentState,
    MonitoringclusterAgentState,
    FinishedclusterAgentState,
    FailedclusterAgentState,
)
from cluster.agents.cluster_agent_state_manager import clusterAgentStateManager
from cluster.core.events import EventType
from Alien.module.context import Context


class MockclusterWeaverAgent:
    """Mock clusterWeaverAgent for testing"""
    
    def __init__(self):
        self._status = clusterAgentStatus.CREATING.value
        self._current_network = None
        
    @property
    def current_network(self):
        return self._current_network
        
    @current_network.setter
    def current_network(self, value):
        self._current_network = value
        
    async def process_initial_request(self, request, context=None):
        # Mock network creation
        mock_network = MagicMock()
        mock_network.task_count = 3
        mock_network.is_complete.return_value = False
        self._current_network = mock_network
        return mock_network
        
    async def update_network_with_lock(self, task_result, context=None):
        # Mock network update
        return self._current_network
        
    async def should_continue(self, network, context=None):
        # Mock decision logic
        return False  # Default to stop


class TestclusterAgentStateManager:
    """ [Text Cleaned] """
    
    def test_state_manager_initialization(self):
        """ [Text Cleaned] """
        manager = clusterAgentStateManager()
        
        creating_state = manager.get_state(clusterAgentStatus.CREATING.value)
        monitoring_state = manager.get_state(clusterAgentStatus.MONITORING.value)
        finished_state = manager.get_state(clusterAgentStatus.FINISHED.value)
        failed_state = manager.get_state(clusterAgentStatus.FAILED.value)
        
        assert isinstance(creating_state, CreatingclusterAgentState)
        assert isinstance(monitoring_state, MonitoringclusterAgentState)
        assert isinstance(finished_state, FinishedclusterAgentState)
        assert isinstance(failed_state, FailedclusterAgentState)
    
    def test_state_caching(self):
        """ [Text Cleaned] """
        manager = clusterAgentStateManager()
        
        state1 = manager.get_state(clusterAgentStatus.CREATING.value)
        state2 = manager.get_state(clusterAgentStatus.CREATING.value)
        
        assert state1 is state2
    
    def test_unknown_status_handling(self):
        """ [Text Cleaned] """
        manager = clusterAgentStateManager()
        
        unknown_state = manager.get_state("unknown_status")
        assert isinstance(unknown_state, CreatingclusterAgentState)


class TestCreatingclusterAgentState:
    """ [Text Cleaned] """
    
    @pytest.mark.asyncio
    async def test_successful_network_creation(self):
        """ [Text Cleaned] network"""
        state = CreatingclusterAgentState()
        agent = MockclusterWeaverAgent()
        context = MagicMock()
        context.get.return_value = "test request"
        
        await state.handle(agent, context)
        
        assert agent._status == clusterAgentStatus.MONITORING.value
        assert agent.current_network is not None
    
    @pytest.mark.asyncio
    async def test_failed_network_creation(self):
        """ [Text Cleaned] network [Text Cleaned] """
        state = CreatingclusterAgentState()
        agent = MockclusterWeaverAgent()
        context = MagicMock()
        context.get.return_value = "test request"
        
        agent.process_initial_request = AsyncMock(return_value=None)
        
        await state.handle(agent, context)
        
        assert agent._status == clusterAgentStatus.FAILED.value
    
    @pytest.mark.asyncio
    async def test_existing_network_handling(self):
        """ [Text Cleaned] network [Text Cleaned] """
        state = CreatingclusterAgentState()
        agent = MockclusterWeaverAgent()
        
        mock_network = MagicMock()
        agent._current_network = mock_network
        
        await state.handle(agent, None)
        
        assert agent._status == clusterAgentStatus.MONITORING.value
    
    def test_state_properties(self):
        """ [Text Cleaned] """
        state = CreatingclusterAgentState()
        
        assert state.name() == clusterAgentStatus.CREATING.value
        assert not state.is_round_end()
        assert not state.is_subtask_end()


class TestMonitoringclusterAgentState:
    """ [Text Cleaned] """
    
    def setup_method(self):
        """ [Text Cleaned] """
        self.state = MonitoringclusterAgentState()
        self.agent = MockclusterWeaverAgent()
        self.agent._status = clusterAgentStatus.MONITORING.value
        
        self.mock_network = MagicMock()
        self.mock_network.is_complete.return_value = False
        self.agent._current_network = self.mock_network
    
    @pytest.mark.asyncio
    async def test_task_started_tracking(self):
        """ [Text Cleaned] """
        task_update = {
            "task_id": "task_1",
            "event_type": EventType.TASK_STARTED.value,
            "status": "running",
        }
        
        await self.state.queue_task_update(task_update)
        
        await self.state._process_pending_updates(self.agent, None)
        
        assert "task_1" in self.state._running_tasks
    
    @pytest.mark.asyncio
    async def test_task_completed_tracking(self):
        """ [Text Cleaned] """
        self.state._running_tasks.add("task_1")
        
        task_update = {
            "task_id": "task_1",
            "event_type": EventType.TASK_COMPLETED.value,
            "status": "completed",
            "result": {"output": "success"}
        }
        
        await self.state.queue_task_update(task_update)
        
        # Mock update_network_with_lock
        self.agent.update_network_with_lock = AsyncMock()
        
        await self.state._process_pending_updates(self.agent, None)
        
        assert "task_1" not in self.state._running_tasks
        self.agent.update_network_with_lock.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_completion_check_with_running_tasks(self):
        """ [Text Cleaned] """
        self.mock_network.is_complete.return_value = True
        self.state._running_tasks.add("task_1")
        
        is_complete = await self.state._check_true_completion(self.agent, None)
        
        assert not is_complete    
    @pytest.mark.asyncio
    async def test_completion_check_with_pending_updates(self):
        """ [Text Cleaned] """
        self.mock_network.is_complete.return_value = True
        await self.state.queue_task_update({"task_id": "task_1", "status": "completed"})
        
        is_complete = await self.state._check_true_completion(self.agent, None)
        
        assert not is_complete    
    @pytest.mark.asyncio
    async def test_true_completion(self):
        """ [Text Cleaned] """
        self.mock_network.is_complete.return_value = True
        self.agent.should_continue = AsyncMock(return_value=False)
        
        is_complete = await self.state._check_true_completion(self.agent, None)
        
        assert is_complete
        self.agent.should_continue.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_wants_to_continue(self):
        """ [Text Cleaned] agent [Text Cleaned] """
        self.mock_network.is_complete.return_value = True
        self.agent.should_continue = AsyncMock(return_value=True)
        
        is_complete = await self.state._check_true_completion(self.agent, None)
        
        assert not is_complete    
    def test_state_properties(self):
        """ [Text Cleaned] """
        assert self.state.name() == clusterAgentStatus.MONITORING.value
        assert not self.state.is_round_end()
        assert not self.state.is_subtask_end()


class TestFinishedAndFailedStates:
    """ [Text Cleaned] """
    
    @pytest.mark.asyncio
    async def test_finished_state(self):
        """ [Text Cleaned] """
        state = FinishedclusterAgentState()
        agent = MockclusterWeaverAgent()
        
        await state.handle(agent, None)
        
        assert state.name() == clusterAgentStatus.FINISHED.value
        assert state.is_round_end()
        assert not state.is_subtask_end()
    
    @pytest.mark.asyncio
    async def test_failed_state(self):
        """ [Text Cleaned] """
        state = FailedclusterAgentState()
        agent = MockclusterWeaverAgent()
        
        await state.handle(agent, None)
        
        assert state.name() == clusterAgentStatus.FAILED.value
        assert state.is_round_end()
        assert not state.is_subtask_end()


class TestStateTransitions:
    """ [Text Cleaned] """
    
    def test_creating_to_monitoring_transition(self):
        """ [Text Cleaned] """
        agent = MockclusterWeaverAgent()
        agent._status = clusterAgentStatus.MONITORING.value
        
        creating_state = CreatingclusterAgentState()
        next_state = creating_state.next_state(agent)
        
        assert isinstance(next_state, MonitoringclusterAgentState)
    
    def test_monitoring_to_finished_transition(self):
        """ [Text Cleaned] """
        agent = MockclusterWeaverAgent()
        agent._status = clusterAgentStatus.FINISHED.value
        
        monitoring_state = MonitoringclusterAgentState()
        next_state = monitoring_state.next_state(agent)
        
        assert isinstance(next_state, FinishedclusterAgentState)
    
    def test_any_to_failed_transition(self):
        """ [Text Cleaned] """
        agent = MockclusterWeaverAgent()
        agent._status = clusterAgentStatus.FAILED.value
        
        creating_state = CreatingclusterAgentState()
        next_state = creating_state.next_state(agent)
        
        assert isinstance(next_state, FailedclusterAgentState)


class TestTaskUpdateQueueing:
    """ [Text Cleaned] """
    
    @pytest.mark.asyncio
    async def test_queue_multiple_updates(self):
        """ [Text Cleaned] """
        state = MonitoringclusterAgentState()
        
        updates = [
            {"task_id": "task_1", "event_type": EventType.TASK_STARTED.value},
            {"task_id": "task_2", "event_type": EventType.TASK_STARTED.value},
            {"task_id": "task_1", "event_type": EventType.TASK_COMPLETED.value},
        ]
        
        for update in updates:
            await state.queue_task_update(update)
        
        assert state._pending_task_updates.qsize() == 3
    
    @pytest.mark.asyncio
    async def test_process_updates_in_order(self):
        """ [Text Cleaned] """
        state = MonitoringclusterAgentState()
        agent = MockclusterWeaverAgent()
        agent.update_network_with_lock = AsyncMock()
        
        await state.queue_task_update({
            "task_id": "task_1", 
            "event_type": EventType.TASK_STARTED.value
        })
        await state.queue_task_update({
            "task_id": "task_1", 
            "event_type": EventType.TASK_COMPLETED.value
        })
        
        await state._process_pending_updates(agent, None)
        
        assert "task_1" not in state._running_tasks        agent.update_network_with_lock.assert_called_once()    
    @pytest.mark.asyncio
    async def test_queue_update_on_non_monitoring_state(self):
        """ [Text Cleaned] """
        state = CreatingclusterAgentState()
        
        await state.queue_task_update({"task_id": "task_1"})
        
        assert not hasattr(state, '_pending_task_updates') or state._pending_task_updates.empty()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
