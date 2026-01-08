# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
cluster Agent State Machine

This module implements the state machine for network to handle
network orchestration with proper synchronization between task completion
events and agent updates.
"""

import asyncio
from enum import Enum
from typing import TYPE_CHECKING, Dict, Type

from cluster.agents.schema import WeavingMode
from Alien.agents.states.basic import AgentState, AgentStateManager
from Alien.module.context import Context, ContextNames

if TYPE_CHECKING:
    from cluster.agents.network_agent import networkAgent


class networkAgentStatus(Enum):
    """cluster Agent states"""

    START = "START"
    CONTINUE = "CONTINUE"
    FINISH = "FINISH"
    FAIL = "FAIL"


class networkAgentStateManager(AgentStateManager):
    """State manager for cluster Agent"""

    _state_mapping: Dict[str, Type[AgentState]] = {}

    @property
    def none_state(self) -> AgentState:
        return StartnetworkAgentState()


class networkAgentState(AgentState):
    """Base state for cluster Agent"""

    @classmethod
    def agent_class(cls):
        from .network_agent import networkAgent

        return networkAgent

    def next_state(self, agent: "networkAgent") -> AgentState:
        """
        Get the next state of the agent.
        :param agent: The current agent.
        """
        status = agent.status

        state = networkAgentStateManager().get_state(status)
        return state


@networkAgentStateManager.register
class StartnetworkAgentState(networkAgentState):
    """Start state - create and execute network"""

    async def handle(self, agent: "networkAgent", context: Context) -> None:
        try:
            agent.logger.info("Starting network orchestration")

            if agent.status in [
                networkAgentStatus.FINISH.value,
                networkAgentStatus.FAIL.value,
            ]:
                return

            # Initialize timing_info to avoid UnboundLocalError
            timing_info = {}

            # Create network if not exists
            if not agent.current_network:
                context.set(ContextNames.WEAVING_MODE, WeavingMode.CREATION)

                agent._current_network, timing_info = (
                    await agent.process_creation(context)
                )

            # Start orchestration in background (non-blocking)
            if agent.current_network:

                asyncio.create_task(
                    agent.orchestrator.orchestrate_network(
                        agent.current_network, metadata=timing_info
                    )
                )

                agent.logger.info(
                    f"Started orchestration for network {agent.current_network.network_id}"
                )
                agent.status = networkAgentStatus.CONTINUE.value
            elif agent.status == networkAgentStatus.CONTINUE.value:
                agent.status = networkAgentStatus.FAIL.value
                agent.logger.error("Failed to create network")

        except AttributeError as e:
            import traceback

            agent.logger.error(
                f"Attribute error in start state: {traceback.format_exc()}",
                exc_info=True,
            )
            agent.status = networkAgentStatus.FAIL.value
        except KeyError as e:
            import traceback

            agent.logger.error(
                f"Missing key in start state: {traceback.format_exc()}", exc_info=True
            )
            agent.status = networkAgentStatus.FAIL.value
        except Exception as e:
            import traceback

            agent.logger.error(
                f"Unexpected error in start state: {traceback.format_exc()}",
                exc_info=True,
            )
            agent.status = networkAgentStatus.FAIL.value

    def next_agent(self, agent):
        return agent

    def is_round_end(self) -> bool:
        return False

    def is_subtask_end(self) -> bool:
        return False

    @classmethod
    def name(cls) -> str:
        return networkAgentStatus.START.value


@networkAgentStateManager.register
class ContinuenetworkAgentState(networkAgentState):
    """Continue state - wait for task completion events"""

    async def _get_merged_network(
        self, agent: "networkAgent", orchestrator_network
    ):
        """
        Get real-time merged network from synchronizer.

        This ensures that the agent always processes with the most up-to-date
        network state, including any structural modifications from previous
        editing sessions that may have completed while this task was running.

        :param agent: The networkAgent instance
        :param orchestrator_network: The network from orchestrator's event
        :return: Merged network with latest agent modifications + orchestrator state
        """
        synchronizer = agent.orchestrator._modification_synchronizer

        if not synchronizer:
            agent.logger.debug(
                "No modification synchronizer available, using orchestrator network"
            )
            return orchestrator_network

        # Get real-time merged network from synchronizer
        merged_network = synchronizer.merge_and_sync_network_states(
            orchestrator_network=orchestrator_network
        )

        agent.logger.info(
            f"🔄 Real-time merged network for editing. "
            f"Tasks before: {len(orchestrator_network.tasks)}, "
            f"Tasks after merge: {len(merged_network.tasks)}"
        )

        return merged_network

    async def handle(self, agent: "networkAgent", context=None) -> None:
        try:

            # Wait for task completion event - NO timeout here
            # The timeout is handled at task execution level
            agent.logger.info("Continue monitoring for task completion events...")
            context.set(ContextNames.WEAVING_MODE, WeavingMode.EDITING)

            # Collect all pending task completion events in queue
            completed_task_events = []

            # Wait for at least one event (blocking)
            first_event = await agent.task_completion_queue.get()
            completed_task_events.append(first_event)

            # Collect any other pending events (non-blocking)
            while not agent.task_completion_queue.empty():
                try:
                    event = agent.task_completion_queue.get_nowait()
                    completed_task_events.append(event)
                except asyncio.QueueEmpty:
                    break

            # Log collected events
            task_ids = [event.task_id for event in completed_task_events]
            agent.logger.info(
                f"Collected {len(completed_task_events)} task completion event(s): {task_ids}"
            )

            # Get the latest network from the last event
            # (orchestrator updates the same network object)
            latest_network = completed_task_events[-1].data.get("network")

            # ⭐ NEW: Get real-time merged network before processing
            # This ensures task_2 editing sees task_1's modifications even if
            # task_1 editing completed while task_2 was running
            merged_network = await self._get_merged_network(
                agent, latest_network
            )

            # Update network based on task completion
            await agent.process_editing(
                context=context,
                task_ids=task_ids,  # Pass all collected task IDs
                before_network=merged_network,  # Use merged version
            )

            # Sleep for waiting
            await asyncio.sleep(0.5)

        except Exception as e:
            agent.logger.error(f"Error in continue state: {e}")
            agent.status = networkAgentStatus.FAIL.value

    def next_agent(self, agent):
        return agent

    def is_round_end(self) -> bool:
        return False

    def is_subtask_end(self) -> bool:
        return False

    @classmethod
    def name(cls) -> str:
        return networkAgentStatus.CONTINUE.value


@networkAgentStateManager.register
class FinishnetworkAgentState(networkAgentState):
    """Finish state - task completed successfully"""

    async def handle(self, agent: "networkAgent", context=None) -> None:
        agent.logger.info("cluster task completed successfully")
        agent._status = networkAgentStatus.FINISH.value

    def next_state(self, agent: "networkAgent") -> AgentState:
        return self  # Terminal state

    def next_agent(self, agent: "networkAgent"):
        return agent

    def is_round_end(self) -> bool:
        return True

    def is_subtask_end(self) -> bool:
        return True

    @classmethod
    def name(cls) -> str:
        return networkAgentStatus.FINISH.value


@networkAgentStateManager.register
class FailnetworkAgentState(networkAgentState):
    """Fail state - task failed"""

    async def handle(self, agent: "networkAgent", context=None) -> None:
        agent.logger.error("cluster task failed")
        agent._status = networkAgentStatus.FAIL.value

    def next_state(self, agent: "networkAgent") -> AgentState:
        return self  # Terminal state

    def next_agent(self, agent: "networkAgent"):
        return agent

    def is_round_end(self) -> bool:
        return True

    def is_subtask_end(self) -> bool:
        return True

    @classmethod
    def name(cls) -> str:
        return networkAgentStatus.FAIL.value
