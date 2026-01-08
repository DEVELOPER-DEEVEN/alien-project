# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Creation mode strategies for network Agent processing.

This module provides specific strategies for network creation mode,
implementing the abstract methods defined in the base strategies.
"""

import asyncio
import time
from typing import TYPE_CHECKING, List

from cluster.agents.processors.strategies.base_network_strategy import (
    BasenetworkActionExecutionStrategy,
)
from cluster.agents.schema import networkAgentResponse, WeavingMode
from cluster.network.task_network import Tasknetwork
from cluster.core.events import AgentEvent, EventType, get_event_bus
from Alien.agents.processors.context.processing_context import ProcessingContext
from Alien.agents.processors.schemas.actions import (
    ActionCommandInfo,
    ListActionCommandInfo,
)
from aip.messages import Result
from Alien.module.context import ContextNames

if TYPE_CHECKING:
    from cluster.agents.network_agent import networkAgent


class networkCreationActionExecutionStrategy(
    BasenetworkActionExecutionStrategy
):
    """
    Action execution strategy specifically for network creation mode.

    This strategy handles:
    - Creation-specific action generation
    - New network building commands
    """

    def __init__(self, fail_fast: bool = False) -> None:
        """
        Initialize network creation action execution strategy.
        :param fail_fast: Whether to raise exceptions immediately on errors
        """
        super().__init__(weaving_mode=WeavingMode.CREATION, fail_fast=fail_fast)

    async def _create_mode_specific_action_info(
        self, agent: "networkAgent", parsed_response: networkAgentResponse
    ) -> List[ActionCommandInfo]:
        """
        Create creation-specific action information for network building.
        """
        if not parsed_response.network:
            self.logger.warning("No valid network found in response.")
            return []

        try:
            # For creation mode, we create a network building action
            action_info = [
                ActionCommandInfo(
                    function=agent._network_creation_tool_name,
                    arguments={"config": parsed_response.network},
                )
            ]

            return action_info

        except Exception as e:
            self.logger.warning(f"Failed to create creation action info: {str(e)}")
            # Return basic action info on failure
            return [
                ActionCommandInfo(
                    function=agent._network_creation_tool_name,
                    arguments={
                        "config": (
                            parsed_response.network
                            if parsed_response.network
                            else "{}"
                        )
                    },
                    status=(
                        parsed_response.status if parsed_response.status else "FAILED"
                    ),
                )
            ]

    async def publish_actions(
        self, agent: "networkAgent", actions: ListActionCommandInfo
    ) -> None:
        """
        Publish network creation actions as events.
        For creation mode, publish a simplified action event for WebUI display.

        :param agent: The network agent
        :param actions: List of action command information
        """
        if not actions or not actions.actions:
            return

        # Extract task and dependency counts from the build_network action
        task_count = 0
        dep_count = 0
        for action in actions.actions:
            if action.function == agent._network_creation_tool_name:
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

        # Determine status - if actions.status is empty or CONTINUE, default to FINISH for build_network
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
            agent_type="network",
            output_type="action",
            output_data={
                "actions": [
                    {
                        "function": "build_network",
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

    def sync_network(
        self, results: List[Result], context: ProcessingContext
    ) -> None:
        """
        Synchronize the network state. Do nothing for editing mode.
        :param results: List of execution results
        :param context: Processing context to access and update network state
        """
        network_json = results[0].result if results else None
        if network_json:
            network = Tasknetwork.from_json(network_json)
            context.global_context.set(ContextNames.network, network)
