"""
 [Text Cleaned] network [Text Cleaned] 
"""
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock
from cluster.agents.cluster_agent_state import MonitoringclusterAgentState, clusterAgentStatus
from cluster.core.events import EventType
from Alien.module.context import Context


class MockclusterWeaverAgent:
    """Mock clusterWeaverAgent for testing network continuation"""
    
    def __init__(self):
        self._status = clusterAgentStatus.MONITORING.value
        self._current_network = None
        self.continue_call_count = 0
        self.new_tasks_added = False
        
    @property
    def current_network(self):
        return self._current_network
        
    @current_network.setter
    def current_network(self, value):
        self._current_network = value
        
    async def update_network_with_lock(self, task_result, context=None):
        # Mock network update
        return self._current_network
        
    async def should_continue(self, network, context=None):
        """ [Text Cleaned] agent [Text Cleaned] """
        self.continue_call_count += 1
        
        if self.continue_call_count == 1:
            await self._add_new_tasks()
            return True
        else:
            return False
    
    async def _add_new_tasks(self):
        """ [Text Cleaned] network"""
        self.new_tasks_added = True


class TestnetworkContinuation:
    """ [Text Cleaned] network [Text Cleaned] """
    
    @pytest.mark.asyncio
    async def test_continuation_after_completion(self):
        """ [Text Cleaned] network [Text Cleaned] """
        monitoring_state = MonitoringclusterAgentState()
        agent = MockclusterWeaverAgent()
        context = Context()
        
        mock_network = MagicMock()
        mock_network.is_complete.return_value = True        agent.current_network = mock_network
        
        agent.queue_task_update_to_current_state = monitoring_state.queue_task_update
        
        try:
            await asyncio.wait_for(monitoring_state.handle(agent, context), timeout=2.0)
        except asyncio.TimeoutError:
            print("Handle method timed out - this indicates the busy waiting issue")
        
        assert agent.continue_call_count > 0
        
        assert agent.new_tasks_added
        
        print(f"should_continue called {agent.continue_call_count} times")
        print(f"New tasks added: {agent.new_tasks_added}")
    
    @pytest.mark.asyncio 
    async def test_network_continuation_with_new_tasks(self):
        """ [Text Cleaned] network [Text Cleaned] """
        monitoring_state = MonitoringclusterAgentState()
        agent = MockclusterWeaverAgent()
        context = Context()
        
        mock_network = MagicMock()
        agent.current_network = mock_network
        
        agent.queue_task_update_to_current_state = monitoring_state.queue_task_update
        
        mock_network.is_complete.return_value = True
        
        async def mock_should_continue(network, context=None):
            agent.continue_call_count += 1
            if agent.continue_call_count == 1:
                await monitoring_state.queue_task_update({
                    "task_id": "new_task_1",
                    "event_type": EventType.TASK_STARTED.value,
                    "status": "running"
                })
                return True
            else:
                return False
        
        agent.should_continue = mock_should_continue
        
        monitoring_task = asyncio.create_task(monitoring_state.handle(agent, context))
        
        await asyncio.sleep(0.1)
        
        await monitoring_state.queue_task_update({
            "task_id": "new_task_1", 
            "event_type": EventType.TASK_COMPLETED.value,
            "status": "completed"
        })
        
        try:
            await asyncio.wait_for(monitoring_task, timeout=1.0)
        except asyncio.TimeoutError:
            monitoring_task.cancel()
            pytest.fail("Monitoring did not complete in expected time")
        
        assert agent.continue_call_count >= 1
        assert agent._status == clusterAgentStatus.FINISHED.value


if __name__ == "__main__":
    async def run_tests():
        test_case = TestnetworkContinuation()
        
        print("🧪 Testing network completion continuation...")
        
        try:
            await test_case.test_continuation_after_completion()
            print("✅ Basic continuation test completed")
        except Exception as e:
            print(f"❌ Basic continuation test failed: {e}")
        
        try:
            await test_case.test_network_continuation_with_new_tasks()
            print("✅ Continuation with new tasks test completed") 
        except Exception as e:
            print(f"❌ Continuation with new tasks test failed: {e}")
    
    asyncio.run(run_tests())
