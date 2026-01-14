
"""
单元测试：Network状态机系统

测试范围：
1. NetworkAgentState状态转换逻辑
2. NetworkAgentStateManager状态管理
3. MonitoringNetworkAgentState任务跟踪
4. Observer与状态机集成
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from network.agents.network_agent_state import (
    NetworkAgentStatus,
    NetworkAgentState,
    CreatingNetworkAgentState,
    MonitoringNetworkAgentState,
    FinishedNetworkAgentState,
    FailedNetworkAgentState,
)
from network.agents.network_agent_state_manager import NetworkAgentStateManager
from network.core.events import EventType
from alien.module.context import Context


class MockNetworkWeaverAgent:
    """Mock NetworkWeaverAgent for testing"""
    
    def __init__(self):
        self._status = NetworkAgentStatus.CREATING.value
        self._current_orion = None
        
    @property
    def current_orion(self):
        return self._current_orion
        
    @current_orion.setter
    def current_orion(self, value):
        self._current_orion = value
        
    async def process_initial_request(self, request, context=None):
        # Mock orion creation
        mock_orion = MagicMock()
        mock_orion.task_count = 3
        mock_orion.is_complete.return_value = False
        self._current_orion = mock_orion
        return mock_orion
        
    async def update_orion_with_lock(self, task_result, context=None):
        # Mock orion update
        return self._current_orion
        
    async def should_continue(self, orion, context=None):
        # Mock decision logic
        return False  # Default to stop


class TestNetworkAgentStateManager:
    """测试状态管理器"""
    
    def test_state_manager_initialization(self):
        """测试状态管理器初始化"""
        manager = NetworkAgentStateManager()
        
        # 检查所有状态都已注册
        creating_state = manager.get_state(NetworkAgentStatus.CREATING.value)
        monitoring_state = manager.get_state(NetworkAgentStatus.MONITORING.value)
        finished_state = manager.get_state(NetworkAgentStatus.FINISHED.value)
        failed_state = manager.get_state(NetworkAgentStatus.FAILED.value)
        
        assert isinstance(creating_state, CreatingNetworkAgentState)
        assert isinstance(monitoring_state, MonitoringNetworkAgentState)
        assert isinstance(finished_state, FinishedNetworkAgentState)
        assert isinstance(failed_state, FailedNetworkAgentState)
    
    def test_state_caching(self):
        """测试状态实例缓存"""
        manager = NetworkAgentStateManager()
        
        # 第一次获取
        state1 = manager.get_state(NetworkAgentStatus.CREATING.value)
        # 第二次获取应该是同一个实例
        state2 = manager.get_state(NetworkAgentStatus.CREATING.value)
        
        assert state1 is state2
    
    def test_unknown_status_handling(self):
        """测试未知状态处理"""
        manager = NetworkAgentStateManager()
        
        # 获取未知状态应该返回默认状态
        unknown_state = manager.get_state("unknown_status")
        assert isinstance(unknown_state, CreatingNetworkAgentState)


class TestCreatingNetworkAgentState:
    """测试创建状态"""
    
    @pytest.mark.asyncio
    async def test_successful_orion_creation(self):
        """测试成功创建orion"""
        state = CreatingNetworkAgentState()
        agent = MockNetworkWeaverAgent()
        context = MagicMock()
        context.get.return_value = "test request"
        
        await state.handle(agent, context)
        
        assert agent._status == NetworkAgentStatus.MONITORING.value
        assert agent.current_orion is not None
    
    @pytest.mark.asyncio
    async def test_failed_orion_creation(self):
        """测试创建orion失败"""
        state = CreatingNetworkAgentState()
        agent = MockNetworkWeaverAgent()
        context = MagicMock()
        context.get.return_value = "test request"
        
        # Mock失败场景
        agent.process_initial_request = AsyncMock(return_value=None)
        
        await state.handle(agent, context)
        
        assert agent._status == NetworkAgentStatus.FAILED.value
    
    @pytest.mark.asyncio
    async def test_existing_orion_handling(self):
        """测试已存在orion的处理"""
        state = CreatingNetworkAgentState()
        agent = MockNetworkWeaverAgent()
        
        # 预设orion
        mock_orion = MagicMock()
        agent._current_orion = mock_orion
        
        await state.handle(agent, None)
        
        assert agent._status == NetworkAgentStatus.MONITORING.value
    
    def test_state_properties(self):
        """测试状态属性"""
        state = CreatingNetworkAgentState()
        
        assert state.name() == NetworkAgentStatus.CREATING.value
        assert not state.is_round_end()
        assert not state.is_subtask_end()


class TestMonitoringNetworkAgentState:
    """测试监控状态"""
    
    def setup_method(self):
        """每个测试方法的设置"""
        self.state = MonitoringNetworkAgentState()
        self.agent = MockNetworkWeaverAgent()
        self.agent._status = NetworkAgentStatus.MONITORING.value
        
        # 创建mock orion
        self.mock_orion = MagicMock()
        self.mock_orion.is_complete.return_value = False
        self.agent._current_orion = self.mock_orion
    
    @pytest.mark.asyncio
    async def test_task_started_tracking(self):
        """测试任务开始跟踪"""
        task_update = {
            "task_id": "task_1",
            "event_type": EventType.TASK_STARTED.value,
            "status": "running",
        }
        
        await self.state.queue_task_update(task_update)
        
        # 处理更新
        await self.state._process_pending_updates(self.agent, None)
        
        # 检查任务被跟踪
        assert "task_1" in self.state._running_tasks
    
    @pytest.mark.asyncio
    async def test_task_completed_tracking(self):
        """测试任务完成跟踪"""
        # 先添加运行中任务
        self.state._running_tasks.add("task_1")
        
        task_update = {
            "task_id": "task_1",
            "event_type": EventType.TASK_COMPLETED.value,
            "status": "completed",
            "result": {"output": "success"}
        }
        
        await self.state.queue_task_update(task_update)
        
        # Mock update_orion_with_lock
        self.agent.update_orion_with_lock = AsyncMock()
        
        # 处理更新
        await self.state._process_pending_updates(self.agent, None)
        
        # 检查任务从跟踪中移除
        assert "task_1" not in self.state._running_tasks
        # 检查orion被更新
        self.agent.update_orion_with_lock.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_completion_check_with_running_tasks(self):
        """测试有运行中任务时的完成检查"""
        # 设置orion为完成但有运行中任务
        self.mock_orion.is_complete.return_value = True
        self.state._running_tasks.add("task_1")
        
        is_complete = await self.state._check_true_completion(self.agent, None)
        
        assert not is_complete  # 不应该完成因为还有运行中任务
    
    @pytest.mark.asyncio
    async def test_completion_check_with_pending_updates(self):
        """测试有待处理更新时的完成检查"""
        # 设置orion为完成但有待处理更新
        self.mock_orion.is_complete.return_value = True
        await self.state.queue_task_update({"task_id": "task_1", "status": "completed"})
        
        is_complete = await self.state._check_true_completion(self.agent, None)
        
        assert not is_complete  # 不应该完成因为有待处理更新
    
    @pytest.mark.asyncio
    async def test_true_completion(self):
        """测试真正完成的情况"""
        # 设置完成条件
        self.mock_orion.is_complete.return_value = True
        self.agent.should_continue = AsyncMock(return_value=False)
        
        is_complete = await self.state._check_true_completion(self.agent, None)
        
        assert is_complete
        self.agent.should_continue.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_wants_to_continue(self):
        """测试agent希望继续的情况"""
        # 设置完成条件但agent希望继续
        self.mock_orion.is_complete.return_value = True
        self.agent.should_continue = AsyncMock(return_value=True)
        
        is_complete = await self.state._check_true_completion(self.agent, None)
        
        assert not is_complete  # agent希望继续，所以不完成
    
    def test_state_properties(self):
        """测试状态属性"""
        assert self.state.name() == NetworkAgentStatus.MONITORING.value
        assert not self.state.is_round_end()
        assert not self.state.is_subtask_end()


class TestFinishedAndFailedStates:
    """测试完成和失败状态"""
    
    @pytest.mark.asyncio
    async def test_finished_state(self):
        """测试完成状态"""
        state = FinishedNetworkAgentState()
        agent = MockNetworkWeaverAgent()
        
        await state.handle(agent, None)
        
        assert state.name() == NetworkAgentStatus.FINISHED.value
        assert state.is_round_end()
        assert not state.is_subtask_end()
    
    @pytest.mark.asyncio
    async def test_failed_state(self):
        """测试失败状态"""
        state = FailedNetworkAgentState()
        agent = MockNetworkWeaverAgent()
        
        await state.handle(agent, None)
        
        assert state.name() == NetworkAgentStatus.FAILED.value
        assert state.is_round_end()
        assert not state.is_subtask_end()


class TestStateTransitions:
    """测试状态转换"""
    
    def test_creating_to_monitoring_transition(self):
        """测试从创建到监控的状态转换"""
        agent = MockNetworkWeaverAgent()
        agent._status = NetworkAgentStatus.MONITORING.value
        
        creating_state = CreatingNetworkAgentState()
        next_state = creating_state.next_state(agent)
        
        assert isinstance(next_state, MonitoringNetworkAgentState)
    
    def test_monitoring_to_finished_transition(self):
        """测试从监控到完成的状态转换"""
        agent = MockNetworkWeaverAgent()
        agent._status = NetworkAgentStatus.FINISHED.value
        
        monitoring_state = MonitoringNetworkAgentState()
        next_state = monitoring_state.next_state(agent)
        
        assert isinstance(next_state, FinishedNetworkAgentState)
    
    def test_any_to_failed_transition(self):
        """测试转换到失败状态"""
        agent = MockNetworkWeaverAgent()
        agent._status = NetworkAgentStatus.FAILED.value
        
        creating_state = CreatingNetworkAgentState()
        next_state = creating_state.next_state(agent)
        
        assert isinstance(next_state, FailedNetworkAgentState)


class TestTaskUpdateQueueing:
    """测试任务更新队列"""
    
    @pytest.mark.asyncio
    async def test_queue_multiple_updates(self):
        """测试队列多个更新"""
        state = MonitoringNetworkAgentState()
        
        updates = [
            {"task_id": "task_1", "event_type": EventType.TASK_STARTED.value},
            {"task_id": "task_2", "event_type": EventType.TASK_STARTED.value},
            {"task_id": "task_1", "event_type": EventType.TASK_COMPLETED.value},
        ]
        
        for update in updates:
            await state.queue_task_update(update)
        
        # 队列应该有3个更新
        assert state._pending_task_updates.qsize() == 3
    
    @pytest.mark.asyncio
    async def test_process_updates_in_order(self):
        """测试按顺序处理更新"""
        state = MonitoringNetworkAgentState()
        agent = MockNetworkWeaverAgent()
        agent.update_orion_with_lock = AsyncMock()
        
        # 添加一系列更新
        await state.queue_task_update({
            "task_id": "task_1", 
            "event_type": EventType.TASK_STARTED.value
        })
        await state.queue_task_update({
            "task_id": "task_1", 
            "event_type": EventType.TASK_COMPLETED.value
        })
        
        # 处理更新
        await state._process_pending_updates(agent, None)
        
        # 检查处理结果
        assert "task_1" not in state._running_tasks  # 任务应该被移除
        agent.update_orion_with_lock.assert_called_once()  # 只有完成事件触发更新
    
    @pytest.mark.asyncio
    async def test_queue_update_on_non_monitoring_state(self):
        """测试在非监控状态队列更新"""
        state = CreatingNetworkAgentState()
        
        # 创建状态不支持队列更新，应该警告但不抛异常
        await state.queue_task_update({"task_id": "task_1"})
        
        # 应该没有队列
        assert not hasattr(state, '_pending_task_updates') or state._pending_task_updates.empty()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
