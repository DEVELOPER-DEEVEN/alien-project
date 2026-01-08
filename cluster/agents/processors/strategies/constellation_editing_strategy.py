# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Editing mode strategies for network Agent processing.

This module provides specific strategies for network editing mode,
implementing the abstract methods defined in the base strategies.
"""

import time
from typing import TYPE_CHECKING, List

from cluster.agents.processors.strategies.base_network_strategy import (
    BasenetworkActionExecutionStrategy,
)
from cluster.agents.schema import networkAgentResponse, WeavingMode
from cluster.network.task_network import Tasknetwork
from cluster.core.events import AgentEvent, EventType, get_event_bus
from cluster.core.types import ProcessingContext
from Alien.agents.processors.schemas.actions import (
    ActionCommandInfo,
    ListActionCommandInfo,
)
from aip.messages import Result, ResultStatus
from Alien.module.context import ContextNames

if TYPE_CHECKING:
    from cluster.agents.network_agent import networkAgent


class networkEditingActionExecutionStrategy(
    BasenetworkActionExecutionStrategy
):
    """
    Action execution strategy specifically for network editing mode.

    This strategy handles:
    - Editing-specific action extraction
    - Existing network modification commands
    """

    def __init__(self, fail_fast: bool = False) -> None:
        """
        Initialize network editing action execution strategy.
        :param fail_fast: Whether to raise exceptions immediately on errors
        """
        super().__init__(weaving_mode=WeavingMode.EDITING, fail_fast=fail_fast)

    async def _create_mode_specific_action_info(
        self, agent: "networkAgent", parsed_response: networkAgentResponse
    ) -> ActionCommandInfo | List[ActionCommandInfo]:
        """
        Create editing-specific action information from LLM response.
        """
        try:
            # For editing mode, we use the actions from the response
            if parsed_response.action:
                return parsed_response.action
            else:
                # No action specified, return empty list
                return []

        except Exception as e:
            self.logger.warning(f"Failed to create editing action info: {str(e)}")
            # Return basic action info on failure
            return [
                ActionCommandInfo(
                    function="no_action",
                    arguments={},
                    status=(
                        parsed_response.status if parsed_response.status else "FAILED"
                    ),
                    result=Result(status="error", result={"error": str(e)}),
                )
            ]

    async def publish_actions(
        self, agent: "networkAgent", actions: ListActionCommandInfo
    ) -> None:
        """
        Publish network editing actions as events.

        :param agent: The network agent
        :param actions: List of action command information
        """
        # Publish agent action event
        event = AgentEvent(
            event_type=EventType.AGENT_ACTION,
            source_id=agent.name,
            timestamp=time.time(),
            data={},
            agent_name=agent.name,
            agent_type="network",
            output_type="action",
            output_data={
                "action_type": "network_editing",
                "actions": [action.model_dump() for action in actions.actions],
            },
        )

        # Publish event asynchronously
        await get_event_bus().publish_event(event)

    def sync_network(
        self, results: List[Result], context: ProcessingContext
    ) -> None:
        """
        Synchronize the network state from MCP tool execution results.

        Extracts the updated network from the last successful result and
        updates the global context.

        :param results: List of execution results from MCP tools
        :param context: Processing context to access and update network state
        """

        if not results:
            self.logger.debug("No results to sync network from")
            return

        # Find the last successful result that contains network data
        network_json = None
        for result in reversed(results):
            # Check if result status is SUCCESS
            if result.status == ResultStatus.SUCCESS and result.result:
                try:
                    # Check if result contains network JSON
                    # MCP tools return JSON strings
                    if isinstance(result.result, str):
                        # Try to parse as network JSON
                        # Valid network JSON should contain "network_id"
                        if (
                            '"network_id"' in result.result
                            or '"tasks"' in result.result
                        ):
                            network_json = result.result
                            break
                    elif isinstance(result.result, dict):
                        # If result is already a dict, check for network fields
                        if (
                            "network_id" in result.result
                            or "tasks" in result.result
                        ):
                            network_json = result.result
                            break
                except Exception as e:
                    self.logger.warning(f"Failed to parse result as network: {e}")
                    continue

        # If we found network data, sync it to context
        if network_json:
            try:
                # Parse network from JSON
                if isinstance(network_json, str):
                    network = Tasknetwork.from_json(
                        json_data=network_json
                    )
                else:
                    network = Tasknetwork.from_dict(network_json)

                # Update global context
                context.global_context.set(ContextNames.network, network)
                self.logger.info(
                    f"Successfully synced network from editing operation: "
                    f"network_id={network.network_id}"
                )
            except Exception as e:
                self.logger.error(f"Failed to sync network from result: {e}")
        else:
            self.logger.debug("No network data found in results to sync")
