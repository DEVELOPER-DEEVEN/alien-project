
"""
Editing mode strategies for Orion Agent processing.

This module provides specific strategies for orion editing mode,
implementing the abstract methods defined in the base strategies.
"""

import time
from typing import TYPE_CHECKING, List

from network.agents.processors.strategies.base_orion_strategy import (
    BaseOrionActionExecutionStrategy,
)
from network.agents.schema import OrionAgentResponse, WeavingMode
from network.orion.task_orion import TaskOrion
from network.core.events import AgentEvent, EventType, get_event_bus
from network.core.types import ProcessingContext
from alien.agents.processors.schemas.actions import (
    ActionCommandInfo,
    ListActionCommandInfo,
)
from aip.messages import Result, ResultStatus
from alien.module.context import ContextNames

if TYPE_CHECKING:
    from network.agents.orion_agent import OrionAgent


class OrionEditingActionExecutionStrategy(
    BaseOrionActionExecutionStrategy
):
    """
    Action execution strategy specifically for orion editing mode.

    This strategy handles:
    - Editing-specific action extraction
    - Existing orion modification commands
    """

    def __init__(self, fail_fast: bool = False) -> None:
        """
        Initialize Orion editing action execution strategy.
        :param fail_fast: Whether to raise exceptions immediately on errors
        """
        super().__init__(weaving_mode=WeavingMode.EDITING, fail_fast=fail_fast)

    async def _create_mode_specific_action_info(
        self, agent: "OrionAgent", parsed_response: OrionAgentResponse
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
        self, agent: "OrionAgent", actions: ListActionCommandInfo
    ) -> None:
        """
        Publish orion editing actions as events.

        :param agent: The orion agent
        :param actions: List of action command information
        """
        # Publish agent action event
        event = AgentEvent(
            event_type=EventType.AGENT_ACTION,
            source_id=agent.name,
            timestamp=time.time(),
            data={},
            agent_name=agent.name,
            agent_type="orion",
            output_type="action",
            output_data={
                "action_type": "orion_editing",
                "actions": [action.model_dump() for action in actions.actions],
            },
        )

        # Publish event asynchronously
        await get_event_bus().publish_event(event)

    def sync_orion(
        self, results: List[Result], context: ProcessingContext
    ) -> None:
        """
        Synchronize the orion state from MCP tool execution results.

        Extracts the updated orion from the last successful result and
        updates the global context.

        :param results: List of execution results from MCP tools
        :param context: Processing context to access and update orion state
        """

        if not results:
            self.logger.debug("No results to sync orion from")
            return

        # Find the last successful result that contains orion data
        orion_json = None
        for result in reversed(results):
            # Check if result status is SUCCESS
            if result.status == ResultStatus.SUCCESS and result.result:
                try:
                    # Check if result contains orion JSON
                    # MCP tools return JSON strings
                    if isinstance(result.result, str):
                        # Try to parse as orion JSON
                        # Valid orion JSON should contain "orion_id"
                        if (
                            '"orion_id"' in result.result
                            or '"tasks"' in result.result
                        ):
                            orion_json = result.result
                            break
                    elif isinstance(result.result, dict):
                        # If result is already a dict, check for orion fields
                        if (
                            "orion_id" in result.result
                            or "tasks" in result.result
                        ):
                            orion_json = result.result
                            break
                except Exception as e:
                    self.logger.warning(f"Failed to parse result as orion: {e}")
                    continue

        # If we found orion data, sync it to context
        if orion_json:
            try:
                # Parse orion from JSON
                if isinstance(orion_json, str):
                    orion = TaskOrion.from_json(
                        json_data=orion_json
                    )
                else:
                    orion = TaskOrion.from_dict(orion_json)

                # Update global context
                context.global_context.set(ContextNames.ORION, orion)
                self.logger.info(
                    f"Successfully synced orion from editing operation: "
                    f"orion_id={orion.orion_id}"
                )
            except Exception as e:
                self.logger.error(f"Failed to sync orion from result: {e}")
        else:
            self.logger.debug("No orion data found in results to sync")
