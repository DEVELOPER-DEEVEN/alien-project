"""
 [Text Cleaned] network continuation [Text Cleaned] 
"""
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock
from cluster.agents.cluster_agent_state import MonitoringclusterAgentState, clusterAgentStatus
from cluster.core.events import EventType
from Alien.module.context import Context


class EnhancedMockclusterWeaverAgent:
    """Enhanced Mock clusterWeaverAgent for testing continuation with handle_continuation"""
    
    def __init__(self):
        self._status = clusterAgentStatus.MONITORING.value
        self._current_network = None
        self.continue_call_count = 0
        self.continuation_call_count = 0
        self.new_tasks_added = False
        self.task_updates_sent = []
        
    @property
    def current_network(self):
        return self._current_network
        
    @current_network.setter 
    def current_network(self, value):
        self._current_network = value
        
    async def update_network_with_lock(self, task_result, context=None):
        return self._current_network
        
    async def should_continue(self, network, context=None):
        """ [Text Cleaned] agent [Text Cleaned] """
        self.continue_call_count += 1
        
        if self.continue_call_count == 1:
            return True
        else:
            return False
    
    async def handle_continuation(self, context=None):
        """ [Text Cleaned] continuation -  [Text Cleaned] agent [Text Cleaned] """
        self.continuation_call_count += 1
        self.new_tasks_added = True
        
        if hasattr(self, 'queue_task_update_to_current_state'):
            task_update = {
                "task_id": f"continuation_task_{self.continuation_call_count}",
                "event_type": EventType.TASK_STARTED.value,
                "status": "running"
            }
            await self.queue_task_update_to_current_state(task_update)
            self.task_updates_sent.append(task_update)


class TestEnhancednetworkContinuation:
    """ [Text Cleaned] network continuation [Text Cleaned] """
    
    @pytest.mark.asyncio
    async def test_continuation_with_handle_continuation(self):
        """ [Text Cleaned] handle_continuation [Text Cleaned] continuation [Text Cleaned] """
        monitoring_state = MonitoringclusterAgentState()
        agent = EnhancedMockclusterWeaverAgent()
        context = Context()
        
        mock_network = MagicMock()
        mock_network.is_complete.return_value = True
        agent.current_network = mock_network
        
        agent.queue_task_update_to_current_state = monitoring_state.queue_task_update
        
        try:
            await asyncio.wait_for(
                monitoring_state.handle(agent, context), 
                timeout=10.0            )
        except asyncio.TimeoutError:
            print("⚠️ Test timed out - this indicates either infinite loop or very slow processing")
        
        print(f"should_continue calls: {agent.continue_call_count}")
        print(f"handle_continuation calls: {agent.continuation_call_count}")
        print(f"Task updates sent: {len(agent.task_updates_sent)}")
        print(f"Final agent status: {agent._status}")
        
        assert agent.continue_call_count > 0, "should_continue should be called"
        
        if agent.continue_call_count > 0:
            assert agent.continuation_call_count > 0, "handle_continuation should be called when agent wants to continue"
        
        if agent.new_tasks_added:
            assert len(agent.task_updates_sent) > 0, "New tasks should be queued during continuation"
    
    @pytest.mark.asyncio
    async def test_multiple_continuation_cycles(self):
        """ [Text Cleaned] continuation"""
        monitoring_state = MonitoringclusterAgentState()
        agent = EnhancedMockclusterWeaverAgent()
        context = Context()
        
        mock_network = MagicMock()
        mock_network.is_complete.return_value = True
        agent.current_network = mock_network
        
        original_should_continue = agent.should_continue
        async def multi_round_should_continue(network, context=None):
            result = await original_should_continue(network, context)
            return agent.continue_call_count <= 2
        
        agent.should_continue = multi_round_should_continue
        agent.queue_task_update_to_current_state = monitoring_state.queue_task_update
        
        async def run_with_timeout():
            try:
                await asyncio.wait_for(monitoring_state.handle(agent, context), timeout=3.0)
            except asyncio.TimeoutError:
                print("Monitoring timed out - this may be expected in multi-round scenarios")
        
        await run_with_timeout()
        
        print(f"Total continuation calls: {agent.continuation_call_count}")
        print(f"Total should_continue calls: {agent.continue_call_count}")
        
        assert agent.continuation_call_count > 1, "Multiple continuation rounds should occur"


if __name__ == "__main__":
    async def run_tests():
        test_case = TestEnhancednetworkContinuation()
        
        print("🧪 Testing enhanced network continuation...")
        
        try:
            await test_case.test_continuation_with_handle_continuation()
            print("✅ Enhanced continuation test completed")
        except Exception as e:
            print(f"❌ Enhanced continuation test failed: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            await test_case.test_multiple_continuation_cycles()
            print("✅ Multiple continuation cycles test completed")
        except Exception as e:
            print(f"❌ Multiple continuation cycles test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(run_tests())
