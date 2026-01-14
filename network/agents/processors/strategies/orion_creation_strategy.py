
"""
Creation mode strategies for Orion Agent processing.

This module provides specific strategies for orion creation mode,
implementing the abstract methods defined in the base strategies.
"""

import asyncio
import time
from typing import TYPE_CHECKING, List

from network.agents.processors.strategies.base_orion_strategy import (
    BaseOrionActionExecutionStrategy,
)
from network.agents.schema import OrionAgentResponse, WeavingMode
from network.orion.task_orion import TaskOrion
from network.core.events import AgentEvent, EventType, get_event_bus
from alien.agents.processors.context.processing_context import ProcessingContext
from alien.agents.processors.schemas.actions import (
    ActionCommandInfo,
    ListActionCommandInfo,
)
from aip.messages import Result
from alien.module.context import ContextNames

if TYPE_CHECKING:
    from network.agents.orion_agent import OrionAgent


class OrionCreationActionExecutionStrategy(
    BaseOrionActionExecutionStrategy
):
    """
    Action execution strategy specifically for orion creation mode.

    This strategy handles:
    - Creation-specific action generation
    - New orion building commands
    """

    def __init__(self, fail_fast: bool = False) -> None:
        """
        Initialize Orion creation action execution strategy.
        :param fail_fast: Whether to raise exceptions immediately on errors
        """
        super().__init__(weaving_mode=WeavingMode.CREATION, fail_fast=fail_fast)

    async def _create_mode_specific_action_info(
        self, agent: "OrionAgent", parsed_response: OrionAgentResponse
    ) -> List[ActionCommandInfo]:
        """
        Create creation-specific action information for orion building.
        """
        if not parsed_response.orion:
            self.logger.warning("No valid orion found in response.")
            return []

        try:
            # For creation mode, we create a orion building action
            action_info = [
                ActionCommandInfo(
                    function=agent._orion_creation_tool_name,
                    arguments={"config": parsed_response.orion},
                )
            ]

            return action_info

        except Exception as e:
            self.logger.warning(f"Failed to create creation action info: {str(e)}")
            # Return basic action info on failure
            return [
                ActionCommandInfo(
                    function=agent._orion_creation_tool_name,
                    arguments={
                        "config": (
                            parsed_response.orion
                            if parsed_response.orion
                            else "{}"
                        )
                    },
                    status=(
                        parsed_response.status if parsed_response.status else "FAILED"
                    ),
                )
            ]

    async def publish_actions(
        self, agent: "OrionAgent", actions: ListActionCommandInfo
    ) -> None:
        """
        Publish orion creation actions as events.
        For creation mode, publish a simplified action event for WebUI display.

        :param agent: The orion agent
        :param actions: List of action command information
        """
        if not actions or not actions.actions:
            return

        # Extract task and dependency counts from the build_orion action
        task_count = 0
        dep_count = 0
        for action in actions.actions:
            if action.function == agent._orion_creation_tool_name:
                config = action.arguments.get("config")
                if config and hasattr(config, "tasks"):
                    task_count = len(config.tasks)
                    dep_count = (
                        len(config.dependencies)
                        if hasattr(config, "dependencies")
                        else 0
                    )
                elif isinstance(config, dict):
                    task_count = len(config.get("tasks", []))
                    dep_count = len(config.get("dependencies", []))

        # Determine status - if actions.status is empty or CONTINUE, default to FINISH for build_orion
        status = actions.status
        if not status or status == "CONTINUE":
            status = "FINISH"

        # Publish simplified action event for WebUI
        event = AgentEvent(
            event_type=EventType.AGENT_ACTION,
            source_id=agent.name,
            timestamp=time.time(),
            data={},
            agent_name=agent.name,
            agent_type="orion",
            output_type="action",
            output_data={
                "actions": [
                    {
                        "function": "build_orion",
                        "arguments": {
                            "task_count": task_count,
                            "dependency_count": dep_count,
                        },
                        "status": "success",
                        "result": {
                            "status": "success",
                        },
                    }
                ],
                "status": status,
            },
        )

        # Publish event asynchronously (non-blocking)
        asyncio.create_task(get_event_bus().publish_event(event))

    def sync_orion(
        self, results: List[Result], context: ProcessingContext
    ) -> None:
        """
        Synchronize the orion state. Do nothing for editing mode.
        :param results: List of execution results
        :param context: Processing context to access and update orion state
        """
        orion_json = results[0].result if results else None
        if orion_json:
            orion = TaskOrion.from_json(orion_json)
            context.global_context.set(ContextNames.ORION, orion)
