# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
 [Text Cleaned] ：cluster [Text Cleaned] 

 [Text Cleaned] ：
1. clusterRound [Text Cleaned] 
2. Observer [Text Cleaned] 
3.  [Text Cleaned] 
4.  [Text Cleaned] 
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from cluster.session.cluster_session import clusterRound, clusterSession
from cluster.agents.cluster_agent import MockclusterWeaverAgent
from cluster.session.observers import networkProgressObserver
from cluster.network import Tasknetwork, TaskStar, create_simple_network
from cluster.core.events import EventType, TaskEvent, get_event_bus
from cluster.client.network_client import networkClient
from cluster.network.orchestrator import TasknetworkOrchestrator
from Alien.module.context import Context


class IntegrationTestHelper:
    """ [Text Cleaned] """
    
    @staticmethod
    def create_test_network() -> Tasknetwork:
        """ [Text Cleaned] network"""
        return create_simple_network(
            task_descriptions=["Task 1", "Task 2", "Task 3"],
            network_name="test_network",
            sequential=True
        )
    
    @staticmethod
    def create_mock_client() -> networkClient:
        """ [Text Cleaned] mock [Text Cleaned] """
        client = MagicMock(spec=networkClient)
        client.device_manager = MagicMock()
        return client
    
    @staticmethod
    def create_mock_orchestrator() -> TasknetworkOrchestrator:
        """ [Text Cleaned] mock [Text Cleaned] """
        orchestrator = MagicMock(spec=TasknetworkOrchestrator)
        orchestrator.assign_devices_automatically = AsyncMock()
        orchestrator.orchestrate_network = AsyncMock()
        return orchestrator


class TestclusterRoundStateMachineIntegration:
    """ [Text Cleaned] clusterRound [Text Cleaned] """
    
    def setup_method(self):
        """ [Text Cleaned] """
        self.agent = MockclusterWeaverAgent()
        self.context = Context()
        self.orchestrator = IntegrationTestHelper.create_mock_orchestrator()
        
        self.test_network = IntegrationTestHelper.create_test_network()
        self.agent.process_initial_request = AsyncMock(return_value=self.test_network)
    
    @pytest.mark.asyncio
    async def test_round_state_machine_execution(self):
        """ [Text Cleaned] round [Text Cleaned] """
        round_instance = clusterRound(
            request="test request",
            agent=self.agent,
            context=self.context,
            should_evaluate=False,
            id=1,
            orchestratior=self.orchestrator
        )
        
        with patch.object(round_instance, 'is_finished') as mock_finished:
            mock_finished.side_effect = [False, False, True]
            
            await round_instance.run()
            
            self.orchestrator.assign_devices_automatically.assert_called_once()
            self.orchestrator.orchestrate_network.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_round_state_transitions(self):
        """ [Text Cleaned] round [Text Cleaned] """
        round_instance = clusterRound(
            request="test request",
            agent=self.agent,
            context=self.context,
            should_evaluate=False,
            id=1,
            orchestratior=self.orchestrator
        )
        
        assert round_instance.agent._status == "creating"
        
        await round_instance.agent.handle(round_instance._context)
        
        assert round_instance.agent._status == "monitoring"
        assert round_instance.agent.current_network is not None
    
    @pytest.mark.asyncio
    async def test_round_handles_agent_failure(self):
        """ [Text Cleaned] round [Text Cleaned] agent [Text Cleaned] """
        self.agent.process_initial_request = AsyncMock(side_effect=Exception("Test failure"))
        
        round_instance = clusterRound(
            request="test request",
            agent=self.agent,
            context=self.context,
            should_evaluate=False,
            id=1,
            orchestratior=self.orchestrator
        )
        
        await round_instance.agent.handle(round_instance._context)
        
        assert round_instance.agent._status == "failed"


class TestObserverStateMachineIntegration:
    """ [Text Cleaned] Observer [Text Cleaned] """
    
    def setup_method(self):
        """ [Text Cleaned] """
        self.agent = MockclusterWeaverAgent()
        self.context = Context()
        self.event_bus = get_event_bus()
        
        self.observer = networkProgressObserver(
            agent=self.agent,
            context=self.context
        )
        
        self.event_bus.subscribe(self.observer)
        
        self.test_network = IntegrationTestHelper.create_test_network()
        self.agent._current_network = self.test_network
        self.agent._status = "monitoring"
    
    @pytest.mark.asyncio
    async def test_task_event_forwarding_to_state_machine(self):
        """ [Text Cleaned] """
        self.agent.queue_task_update_to_current_state = AsyncMock()
        
        task_event = TaskEvent(
            event_type=EventType.TASK_STARTED,
            source_id="test_source",
            timestamp=time.time(),
            data={},
            task_id="task_1",
            status="running"
        )
        
        await self.event_bus.publish_event(task_event)
        
        await asyncio.sleep(0.1)
        
        self.agent.queue_task_update_to_current_state.assert_called_once()
        call_args = self.agent.queue_task_update_to_current_state.call_args[0][0]
        assert call_args["task_id"] == "task_1"
        assert call_args["event_type"] == EventType.TASK_STARTED.value
    
    @pytest.mark.asyncio
    async def test_task_lifecycle_event_sequence(self):
        """ [Text Cleaned] """
        self.agent.queue_task_update_to_current_state = AsyncMock()
        
        events = [
            TaskEvent(
                event_type=EventType.TASK_STARTED,
                source_id="test_source",
                timestamp=time.time(),
                data={},
                task_id="task_1",
                status="running"
            ),
            TaskEvent(
                event_type=EventType.TASK_COMPLETED,
                source_id="test_source",
                timestamp=time.time() + 1,
                data={},
                task_id="task_1",
                status="completed",
                result={"output": "success"}
            )
        ]
        
        for event in events:
            await self.event_bus.publish_event(event)
            await asyncio.sleep(0.05)        
        await asyncio.sleep(0.1)
        
        assert self.agent.queue_task_update_to_current_state.call_count == 2
    
    @pytest.mark.asyncio
    async def test_observer_error_handling(self):
        """ [Text Cleaned] observer [Text Cleaned] """
        self.agent.queue_task_update_to_current_state = AsyncMock(
            side_effect=Exception("State machine error")
        )
        
        task_event = TaskEvent(
            event_type=EventType.TASK_STARTED,
            source_id="test_source",
            timestamp=time.time(),
            data={},
            task_id="task_1",
            status="running"
        )
        
        await self.event_bus.publish_event(task_event)
        await asyncio.sleep(0.1)
        
        self.agent.queue_task_update_to_current_state.assert_called_once()


class TestEndToEndExecution:
    """ [Text Cleaned] """
    
    def setup_method(self):
        """ [Text Cleaned] """
        self.agent = MockclusterWeaverAgent()
        self.client = IntegrationTestHelper.create_mock_client()
        self.event_bus = get_event_bus()
        
        self.session = clusterSession(
            task="test_task",
            should_evaluate=False,
            id="test_session",
            agent=self.agent,
            client=self.client
        )
    
    @pytest.mark.asyncio
    async def test_complete_execution_flow(self):
        """ [Text Cleaned] """
        test_network = IntegrationTestHelper.create_test_network()
        self.agent.process_initial_request = AsyncMock(return_value=test_network)
        
        # Mock orchestrator
        with patch.object(self.session._orchestrator, 'assign_devices_automatically') as mock_assign, \
             patch.object(self.session._orchestrator, 'orchestrate_network') as mock_orchestrate:
            
            mock_assign.return_value = asyncio.coroutine(lambda: None)()
            mock_orchestrate.return_value = asyncio.coroutine(lambda: None)()
            
            await self.session.run()
            
            assert self.agent.current_network is not None
            mock_assign.assert_called_once()
            mock_orchestrate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_race_condition_resolution(self):
        """ [Text Cleaned] """
        
        from cluster.agents.cluster_agent_state import MonitoringclusterAgentState
        
        monitoring_state = MonitoringclusterAgentState()
        self.agent._state = monitoring_state
        self.agent._status = "monitoring"
        
        test_network = IntegrationTestHelper.create_test_network()
        test_network.is_complete = MagicMock(return_value=False)
        self.agent._current_network = test_network
        
        task_events = [
            {"task_id": "task_1", "event_type": EventType.TASK_STARTED.value, "status": "running"},
            {"task_id": "task_2", "event_type": EventType.TASK_STARTED.value, "status": "running"},
            {"task_id": "task_1", "event_type": EventType.TASK_COMPLETED.value, "status": "completed"},
            {"task_id": "task_2", "event_type": EventType.TASK_COMPLETED.value, "status": "completed"},
        ]
        
        for event in task_events:
            await monitoring_state.queue_task_update(event)
        
        def mock_is_complete():
            return monitoring_state._pending_task_updates.empty() and len(monitoring_state._running_tasks) == 0
        
        test_network.is_complete.side_effect = mock_is_complete
        self.agent.should_continue = AsyncMock(return_value=False)
        self.agent.update_network_with_lock = AsyncMock()
        
        await monitoring_state._process_pending_updates(self.agent, None)
        
        assert len(monitoring_state._running_tasks) == 0        assert monitoring_state._pending_task_updates.empty()        
        is_complete = await monitoring_state._check_true_completion(self.agent, None)
        assert is_complete    
    @pytest.mark.asyncio
    async def test_concurrent_task_updates(self):
        """ [Text Cleaned] """
        from cluster.agents.cluster_agent_state import MonitoringclusterAgentState
        
        monitoring_state = MonitoringclusterAgentState()
        self.agent._state = monitoring_state
        self.agent.update_network_with_lock = AsyncMock()
        
        async def add_task_updates():
            for i in range(10):
                await monitoring_state.queue_task_update({
                    "task_id": f"task_{i}",
                    "event_type": EventType.TASK_STARTED.value,
                    "status": "running"
                })
                await asyncio.sleep(0.001)        
        async def process_updates():
            await asyncio.sleep(0.05)            await monitoring_state._process_pending_updates(self.agent, None)
        
        await asyncio.gather(add_task_updates(), process_updates())
        
        assert len(monitoring_state._running_tasks) == 10


class TestErrorScenarios:
    """ [Text Cleaned] """
    
    @pytest.mark.asyncio
    async def test_network_creation_failure_handling(self):
        """ [Text Cleaned] network [Text Cleaned] """
        agent = MockclusterWeaverAgent()
        agent.process_initial_request = AsyncMock(side_effect=Exception("Creation failed"))
        
        from cluster.agents.cluster_agent_state import CreatingclusterAgentState
        
        creating_state = CreatingclusterAgentState()
        context = Context()
        from Alien.module.context import ContextNames
        context.set(ContextNames.REQUEST, "test request")
        
        await creating_state.handle(agent, context)
        
        assert agent._status == "failed"
    
    @pytest.mark.asyncio
    async def test_monitoring_state_with_no_network(self):
        """ [Text Cleaned] network"""
        agent = MockclusterWeaverAgent()
        agent._current_network = None
        
        from cluster.agents.cluster_agent_state import MonitoringclusterAgentState
        
        monitoring_state = MonitoringclusterAgentState()
        
        await monitoring_state.handle(agent, None)
        
        assert agent._status == "failed"
    
    @pytest.mark.asyncio
    async def test_invalid_task_update_handling(self):
        """ [Text Cleaned] """
        from cluster.agents.cluster_agent_state import MonitoringclusterAgentState
        
        monitoring_state = MonitoringclusterAgentState()
        agent = MockclusterWeaverAgent()
        agent.update_network_with_lock = AsyncMock(side_effect=Exception("Update failed"))
        
        await monitoring_state.queue_task_update({
            "task_id": "invalid_task",
            "event_type": EventType.TASK_COMPLETED.value,
            "status": "completed"
        })
        
        await monitoring_state._process_pending_updates(agent, None)
        
        assert monitoring_state._pending_task_updates.empty()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
