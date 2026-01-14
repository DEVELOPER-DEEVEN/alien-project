
"""
Network Agent State Machine

This module implements the state machine for Orion to handle
orion orchestration with proper synchronization between task completion
events and agent updates.
"""

import asyncio
from enum import Enum
from typing import TYPE_CHECKING, Dict, Type

from network.agents.schema import WeavingMode
from alien.agents.states.basic import AgentState, AgentStateManager
from alien.module.context import Context, ContextNames

if TYPE_CHECKING:
    from network.agents.orion_agent import OrionAgent


class OrionAgentStatus(Enum):
    """Network Agent states"""

    START = "START"
    CONTINUE = "CONTINUE"
    FINISH = "FINISH"
    FAIL = "FAIL"


class OrionAgentStateManager(AgentStateManager):
    """State manager for Network Agent"""

    _state_mapping: Dict[str, Type[AgentState]] = {}

    @property
    def none_state(self) -> AgentState:
        return StartOrionAgentState()


class OrionAgentState(AgentState):
    """Base state for Network Agent"""

    @classmethod
    def agent_class(cls):
        from .orion_agent import OrionAgent

        return OrionAgent

    def next_state(self, agent: "OrionAgent") -> AgentState:
        """
        Get the next state of the agent.
        :param agent: The current agent.
        """
        status = agent.status

        state = OrionAgentStateManager().get_state(status)
        return state


@OrionAgentStateManager.register
class StartOrionAgentState(OrionAgentState):
    """Start state - create and execute orion"""

    async def handle(self, agent: "OrionAgent", context: Context) -> None:
        try:
            agent.logger.info("Starting orion orchestration")

            if agent.status in [
                OrionAgentStatus.FINISH.value,
                OrionAgentStatus.FAIL.value,
            ]:
                return

            # Initialize timing_info to avoid UnboundLocalError
            timing_info = {}

            # Create orion if not exists
            if not agent.current_orion:
                context.set(ContextNames.WEAVING_MODE, WeavingMode.CREATION)

                agent._current_orion, timing_info = (
                    await agent.process_creation(context)
                )

            # Start orchestration in background (non-blocking)
            if agent.current_orion:

                asyncio.create_task(
                    agent.orchestrator.orchestrate_orion(
                        agent.current_orion, metadata=timing_info
                    )
                )

                agent.logger.info(
                    f"Started orchestration for orion {agent.current_orion.orion_id}"
                )
                agent.status = OrionAgentStatus.CONTINUE.value
            elif agent.status == OrionAgentStatus.CONTINUE.value:
                agent.status = OrionAgentStatus.FAIL.value
                agent.logger.error("Failed to create orion")

        except AttributeError as e:
            import traceback

            agent.logger.error(
                f"Attribute error in start state: {traceback.format_exc()}",
                exc_info=True,
            )
            agent.status = OrionAgentStatus.FAIL.value
        except KeyError as e:
            import traceback

            agent.logger.error(
                f"Missing key in start state: {traceback.format_exc()}", exc_info=True
            )
            agent.status = OrionAgentStatus.FAIL.value
        except Exception as e:
            import traceback

            agent.logger.error(
                f"Unexpected error in start state: {traceback.format_exc()}",
                exc_info=True,
            )
            agent.status = OrionAgentStatus.FAIL.value

    def next_agent(self, agent):
        return agent

    def is_round_end(self) -> bool:
        return False

    def is_subtask_end(self) -> bool:
        return False

    @classmethod
    def name(cls) -> str:
        return OrionAgentStatus.START.value


@OrionAgentStateManager.register
class ContinueOrionAgentState(OrionAgentState):
    """Continue state - wait for task completion events"""

    async def _get_merged_orion(
        self, agent: "OrionAgent", orchestrator_orion
    ):
        """
        Get real-time merged orion from synchronizer.

        This ensures that the agent always processes with the most up-to-date
        orion state, including any structural modifications from previous
        editing sessions that may have completed while this task was running.

        :param agent: The OrionAgent instance
        :param orchestrator_orion: The orion from orchestrator's event
        :return: Merged orion with latest agent modifications + orchestrator state
        """
        synchronizer = agent.orchestrator._modification_synchronizer

        if not synchronizer:
            agent.logger.debug(
                "No modification synchronizer available, using orchestrator orion"
            )
            return orchestrator_orion

        # Get real-time merged orion from synchronizer
        merged_orion = synchronizer.merge_and_sync_orion_states(
            orchestrator_orion=orchestrator_orion
        )

        agent.logger.info(
            f"[CONTINUE] Real-time merged orion for editing. "
            f"Tasks before: {len(orchestrator_orion.tasks)}, "
            f"Tasks after merge: {len(merged_orion.tasks)}"
        )

        return merged_orion

    async def handle(self, agent: "OrionAgent", context=None) -> None:
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

            # Get the latest orion from the last event
            # (orchestrator updates the same orion object)
            latest_orion = completed_task_events[-1].data.get("orion")

            # ⭐ NEW: Get real-time merged orion before processing
            # This ensures task_2 editing sees task_1's modifications even if
            # task_1 editing completed while task_2 was running
            merged_orion = await self._get_merged_orion(
                agent, latest_orion
            )

            # Update orion based on task completion
            await agent.process_editing(
                context=context,
                task_ids=task_ids,  # Pass all collected task IDs
                before_orion=merged_orion,  # Use merged version
            )

            # Sleep for waiting
            await asyncio.sleep(0.5)

        except Exception as e:
            agent.logger.error(f"Error in continue state: {e}")
            agent.status = OrionAgentStatus.FAIL.value

    def next_agent(self, agent):
        return agent

    def is_round_end(self) -> bool:
        return False

    def is_subtask_end(self) -> bool:
        return False

    @classmethod
    def name(cls) -> str:
        return OrionAgentStatus.CONTINUE.value


@OrionAgentStateManager.register
class FinishOrionAgentState(OrionAgentState):
    """Finish state - task completed successfully"""

    async def handle(self, agent: "OrionAgent", context=None) -> None:
        agent.logger.info("Network task completed successfully")
        agent._status = OrionAgentStatus.FINISH.value

    def next_state(self, agent: "OrionAgent") -> AgentState:
        return self  # Terminal state

    def next_agent(self, agent: "OrionAgent"):
        return agent

    def is_round_end(self) -> bool:
        return True

    def is_subtask_end(self) -> bool:
        return True

    @classmethod
    def name(cls) -> str:
        return OrionAgentStatus.FINISH.value


@OrionAgentStateManager.register
class FailOrionAgentState(OrionAgentState):
    """Fail state - task failed"""

    async def handle(self, agent: "OrionAgent", context=None) -> None:
        agent.logger.error("Network task failed")
        agent._status = OrionAgentStatus.FAIL.value

    def next_state(self, agent: "OrionAgent") -> AgentState:
        return self  # Terminal state

    def next_agent(self, agent: "OrionAgent"):
        return agent

    def is_round_end(self) -> bool:
        return True

    def is_subtask_end(self) -> bool:
        return True

    @classmethod
    def name(cls) -> str:
        return OrionAgentStatus.FAIL.value
