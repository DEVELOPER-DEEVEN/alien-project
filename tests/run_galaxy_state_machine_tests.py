# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
cluster [Text Cleaned] 

 [Text Cleaned] ， [Text Cleaned] 
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cluster.agents.cluster_agent import MockclusterWeaverAgent
from cluster.agents.cluster_agent_state import (
    clusterAgentStatus,
    CreatingclusterAgentState,
    MonitoringclusterAgentState,
    FinishedclusterAgentState,
    FailedclusterAgentState
)
from cluster.agents.cluster_agent_state_manager import clusterAgentStateManager
from cluster.session.observers import networkProgressObserver
from cluster.core.events import EventType, TaskEvent, get_event_bus
from cluster.network import create_simple_network
from Alien.module.context import Context


class clusterStateMachineTestRunner:
    """cluster [Text Cleaned] """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results: Dict[str, Any] = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "execution_time": 0
        }
    
    def setup_logging(self):
        """ [Text Cleaned] """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """ [Text Cleaned] """
        self.setup_logging()
        start_time = time.time()
        
        print("🚀  [Text Cleaned] cluster [Text Cleaned] ...")
        print("=" * 60)
        
        await self.test_state_manager()
        await self.test_state_transitions()
        await self.test_monitoring_state_task_tracking()
        await self.test_observer_integration()
        
        await self.test_complete_workflow()
        await self.test_race_condition_resolution()
        await self.test_error_handling()
        
        await self.test_concurrent_operations()
        
        self.results["execution_time"] = time.time() - start_time
        
        self.generate_report()
        
        return self.results
    
    async def test_state_manager(self):
        """ [Text Cleaned] """
        print("📋  [Text Cleaned] ...")
        
        try:
            manager = clusterAgentStateManager()
            
            creating_state = manager.get_state(clusterAgentStatus.CREATING.value)
            monitoring_state = manager.get_state(clusterAgentStatus.MONITORING.value)
            finished_state = manager.get_state(clusterAgentStatus.FINISHED.value)
            failed_state = manager.get_state(clusterAgentStatus.FAILED.value)
            
            assert isinstance(creating_state, CreatingclusterAgentState)
            assert isinstance(monitoring_state, MonitoringclusterAgentState)
            assert isinstance(finished_state, FinishedclusterAgentState)
            assert isinstance(failed_state, FailedclusterAgentState)
            
            same_state = manager.get_state(clusterAgentStatus.CREATING.value)
            assert creating_state is same_state
            
            self._record_success(" [Text Cleaned] ")
            
        except Exception as e:
            self._record_failure(" [Text Cleaned] ", e)
    
    async def test_state_transitions(self):
        """ [Text Cleaned] """
        print("🔄  [Text Cleaned] ...")
        
        try:
            agent = MockclusterWeaverAgent()
            context = Context()
            from Alien.module.context import ContextNames
            context.set(ContextNames.REQUEST, "test request")
            
            creating_state = CreatingclusterAgentState()
            await creating_state.handle(agent, context)
            
            assert agent._status == clusterAgentStatus.MONITORING.value
            assert agent.current_network is not None
            
            next_state = creating_state.next_state(agent)
            assert isinstance(next_state, MonitoringclusterAgentState)
            
            self._record_success(" [Text Cleaned] ")
            
        except Exception as e:
            self._record_failure(" [Text Cleaned] ", e)
    
    async def test_monitoring_state_task_tracking(self):
        """ [Text Cleaned] """
        print("📊  [Text Cleaned] ...")
        
        try:
            monitoring_state = MonitoringclusterAgentState()
            agent = MockclusterWeaverAgent()
            
            network = create_simple_network(
                task_descriptions=["Task 1", "Task 2"],
                network_name="test",
                sequential=True
            )
            network.is_complete = lambda: False
            agent._current_network = network
            agent.update_network_with_lock = lambda *args: asyncio.coroutine(lambda: network)()
            agent.should_continue = lambda *args: asyncio.coroutine(lambda: False)()
            
            await monitoring_state.queue_task_update({
                "task_id": "task_1",
                "event_type": EventType.TASK_STARTED.value,
                "status": "running"
            })
            
            await monitoring_state._process_pending_updates(agent, None)
            assert "task_1" in monitoring_state._running_tasks
            
            await monitoring_state.queue_task_update({
                "task_id": "task_1",
                "event_type": EventType.TASK_COMPLETED.value,
                "status": "completed"
            })
            
            await monitoring_state._process_pending_updates(agent, None)
            assert "task_1" not in monitoring_state._running_tasks
            
            self._record_success(" [Text Cleaned] ")
            
        except Exception as e:
            self._record_failure(" [Text Cleaned] ", e)
    
    async def test_observer_integration(self):
        """ [Text Cleaned] """
        print("👁️  [Text Cleaned] ...")
        
        try:
            agent = MockclusterWeaverAgent()
            context = Context()
            event_bus = get_event_bus()
            
            from cluster.agents.cluster_agent_state import MonitoringclusterAgentState
            monitoring_state = MonitoringclusterAgentState()
            agent._state = monitoring_state
            agent.queue_task_update_to_current_state = monitoring_state.queue_task_update
            
            observer = networkProgressObserver(agent, context)
            event_bus.subscribe(observer)
            
            task_event = TaskEvent(
                event_type=EventType.TASK_STARTED,
                source_id="test_source",
                timestamp=time.time(),
                data={},
                task_id="task_1",
                status="running"
            )
            
            await event_bus.publish_event(task_event)
            await asyncio.sleep(0.1)            
            await monitoring_state._process_pending_updates(agent, context)
            
            assert "task_1" in monitoring_state._running_tasks
                
            self._record_success(" [Text Cleaned] ")
            
        except Exception as e:
            self._record_failure(" [Text Cleaned] ", e)
    
    async def test_complete_workflow(self):
        """ [Text Cleaned] """
        print("🔄  [Text Cleaned] ...")
        
        try:
            agent = MockclusterWeaverAgent()
            context = Context()
            from Alien.module.context import ContextNames
            context.set(ContextNames.REQUEST, "complete workflow test")
            
            state_manager = clusterAgentStateManager()
            
            agent._status = clusterAgentStatus.CREATING.value
            state = state_manager.get_state(agent._status)
            await state.handle(agent, context)
            
            assert agent._status == clusterAgentStatus.MONITORING.value
            
            state = state_manager.get_state(agent._status)
            monitoring_state = state
            
            await monitoring_state.queue_task_update({
                "task_id": "task_1",
                "event_type": EventType.TASK_STARTED.value,
            })
            
            await monitoring_state.queue_task_update({
                "task_id": "task_1",
                "event_type": EventType.TASK_COMPLETED.value,
            })
            
            agent.current_network.is_complete = lambda: True
            agent.should_continue = lambda *args: asyncio.coroutine(lambda: False)()
            
            await state.handle(agent, context)
            
            assert agent._status == clusterAgentStatus.FINISHED.value
            
            self._record_success(" [Text Cleaned] ")
            
        except Exception as e:
            self._record_failure(" [Text Cleaned] ", e)
    
    async def test_race_condition_resolution(self):
        """ [Text Cleaned] """
        print("⚡  [Text Cleaned] ...")
        
        try:
            monitoring_state = MonitoringclusterAgentState()
            agent = MockclusterWeaverAgent()
            
            network = create_simple_network(
                task_descriptions=["Task 1", "Task 2"],
                network_name="race_test",
                sequential=True
            )
            agent._current_network = network
            agent.update_network_with_lock = lambda *args: asyncio.coroutine(lambda: network)()
            
            tasks = [
                {"task_id": "task_1", "event_type": EventType.TASK_STARTED.value},
                {"task_id": "task_2", "event_type": EventType.TASK_STARTED.value},
                {"task_id": "task_1", "event_type": EventType.TASK_COMPLETED.value},
                {"task_id": "task_2", "event_type": EventType.TASK_COMPLETED.value},
            ]
            
            for task in tasks:
                await monitoring_state.queue_task_update(task)
            
            def mock_is_complete():
                return (monitoring_state._pending_task_updates.empty() and 
                       len(monitoring_state._running_tasks) == 0)
            
            network.is_complete = mock_is_complete
            agent.should_continue = lambda *args: asyncio.coroutine(lambda: False)()
            
            await monitoring_state._process_pending_updates(agent, None)
            
            assert len(monitoring_state._running_tasks) == 0
            assert monitoring_state._pending_task_updates.empty()
            
            is_complete = await monitoring_state._check_true_completion(agent, None)
            assert is_complete
            
            self._record_success(" [Text Cleaned] ")
            
        except Exception as e:
            self._record_failure(" [Text Cleaned] ", e)
    
    async def test_error_handling(self):
        """ [Text Cleaned] """
        print("🚨  [Text Cleaned] ...")
        
        try:
            agent = MockclusterWeaverAgent()
            agent.process_initial_request = lambda *args: asyncio.coroutine(
                lambda: exec('raise Exception("Test error")')
            )()
            
            creating_state = CreatingclusterAgentState()
            context = Context()
            from Alien.module.context import ContextNames
            context.set(ContextNames.REQUEST, "error test")
            
            await creating_state.handle(agent, context)
            
            assert agent._status == clusterAgentStatus.FAILED.value
            
            monitoring_state = MonitoringclusterAgentState()
            agent._current_network = None
            
            await monitoring_state.handle(agent, None)
            
            assert agent._status == clusterAgentStatus.FAILED.value
            
            self._record_success(" [Text Cleaned] ")
            
        except Exception as e:
            self._record_failure(" [Text Cleaned] ", e)
    
    async def test_concurrent_operations(self):
        """ [Text Cleaned] """
        print("🏃‍♂️  [Text Cleaned] ...")
        
        try:
            monitoring_state = MonitoringclusterAgentState()
            agent = MockclusterWeaverAgent()
            agent.update_network_with_lock = lambda *args: asyncio.coroutine(lambda: None)()
            
            async def add_updates(start_id: int, count: int):
                for i in range(count):
                    await monitoring_state.queue_task_update({
                        "task_id": f"task_{start_id + i}",
                        "event_type": EventType.TASK_STARTED.value,
                        "status": "running"
                    })
                    await asyncio.sleep(0.001)
            
            await asyncio.gather(
                add_updates(0, 10),
                add_updates(10, 10),
                add_updates(20, 10)
            )
            
            await monitoring_state._process_pending_updates(agent, None)
            
            assert len(monitoring_state._running_tasks) == 30
            
            self._record_success(" [Text Cleaned] ")
            
        except Exception as e:
            self._record_failure(" [Text Cleaned] ", e)
    
    def _record_success(self, test_name: str):
        """ [Text Cleaned] """
        self.results["tests_run"] += 1
        self.results["tests_passed"] += 1
        print(f"✅ {test_name} -  [Text Cleaned] ")
    
    def _record_failure(self, test_name: str, error: Exception):
        """ [Text Cleaned] """
        self.results["tests_run"] += 1
        self.results["tests_failed"] += 1
        self.results["failures"].append({
            "test": test_name,
            "error": str(error),
            "type": type(error).__name__
        })
        print(f"❌ {test_name} -  [Text Cleaned] : {error}")
    
    def generate_report(self):
        """ [Text Cleaned] """
        print("\n" + "=" * 60)
        print("📊  [Text Cleaned] ")
        print("=" * 60)
        
        print(f" [Text Cleaned] : {self.results['tests_run']}")
        print(f" [Text Cleaned] : {self.results['tests_passed']}")
        print(f" [Text Cleaned] : {self.results['tests_failed']}")
        print(f" [Text Cleaned] : {self.results['execution_time']:.2f} [Text Cleaned] ")
        
        if self.results["failures"]:
            print("\n❌  [Text Cleaned] :")
            for failure in self.results["failures"]:
                print(f"  - {failure['test']}: {failure['error']}")
        
        success_rate = (self.results['tests_passed'] / self.results['tests_run']) * 100 if self.results['tests_run'] > 0 else 0
        print(f"\n [Text Cleaned] : {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉  [Text Cleaned] ！cluster [Text Cleaned] ！")
        else:
            print("⚠️  [Text Cleaned] ， [Text Cleaned] ")


async def main():
    """ [Text Cleaned] """
    runner = clusterStateMachineTestRunner()
    results = await runner.run_all_tests()
    
    exit_code = 0 if results["tests_failed"] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
