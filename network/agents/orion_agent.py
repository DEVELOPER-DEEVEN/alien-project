
"""
Orion - DAG-based Task Orchestration Agent

This module provides the Orion interface for managing DAG-based task orchestration
in the Network framework. The Orion is responsible for processing user requests,
generating and updating DAGs, and managing task execution status.

Optimized for type safety, maintainability, and follows SOLID principles.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Union

from network.agents.orion_agent_states import OrionAgentStatus
from network.agents.processors.processor import OrionAgentProcessor
from network.agents.prompters.base_orion_prompter import (
    BaseOrionPrompter,
    OrionPrompterFactory,
)
from network.agents.schema import OrionAgentResponse, WeavingMode
from network.client.components.types import AgentProfile
from network.orion.orchestrator.orchestrator import TaskOrionOrchestrator
from network.core.events import (
    AgentEvent,
    OrionEvent,
    EventType,
    TaskEvent,
    get_event_bus,
)

# Import BasicAgent and OrionAgentStatus here to avoid circular import at module level
from alien.agents.agent.basic import BasicAgent
from aip.messages import Command, MCPToolInfo, ResultStatus
from alien.module.context import Context, ContextNames

from ..orion import TaskOrion
from ..core.interfaces import IRequestProcessor, IResultProcessor


class OrionAgent(BasicAgent, IRequestProcessor, IResultProcessor):
    """
    Orion - A specialized agent for DAG-based task orchestration.

    The Orion extends BasicAgent and implements multiple interfaces:
    - IRequestProcessor: Process user requests to generate initial DAGs
    - IResultProcessor: Process task execution results and update DAGs

    Key responsibilities:
    - Process user requests to generate initial DAGs
    - Update DAGs based on task execution results
    - Manage task status and orion state
    - Coordinate with TaskOrionOrchestrator for execution

    This class follows the Interface Segregation Principle by implementing
    focused interfaces rather than one large interface.
    """

    _orion_creation_tool_name: str = "build_orion"

    def __init__(
        self,
        orchestrator: TaskOrionOrchestrator,
        name: str = "orion_agent",
    ):
        """
        Initialize the Orion.

        :param name: Agent name (default: "orion_agent")
        :param orchestrator: Task orchestrator instance
        """

        super().__init__(name)

        self._current_orion: Optional[TaskOrion] = None
        self._status: str = "START"  # start, continue, finish, fail
        self.logger = logging.getLogger(__name__)

        # Add state machine support
        self.current_request: str = ""
        self._orchestrator = orchestrator

        self._task_completion_queue = asyncio.Queue()
        self._orion_completion_queue = asyncio.Queue()

        self._context_provision_executed = False
        self._event_bus = get_event_bus()

        self.prompter = None  # Will be initialized when weaving_mode is known

        # Initialize with start state
        from .orion_agent_states import StartOrionAgentState

        self.set_state(StartOrionAgentState())

    @property
    def current_orion(self) -> Optional[TaskOrion]:
        """
        Get the current orion being managed.

        :return: Current orion instance or None
        """
        return self._current_orion

    # ==================== Private Helper Methods ====================

    async def _initialize_prompter(self, context: Context) -> None:
        """
        Initialize prompter based on weaving mode.

        :param context: Processing context containing weaving mode
        """
        weaving_mode = context.get(ContextNames.WEAVING_MODE)
        self.prompter = self.get_prompter(weaving_mode)

    async def _ensure_context_provision(self, context: Context) -> None:
        """
        Ensure context provision is executed once for creation.

        :param context: Processing context
        """
        if not self._context_provision_executed:
            await self.context_provision(context=context)
            self._context_provision_executed = True

    async def _create_and_process(self, context: Context) -> Tuple[float, float, float]:
        """
        Create processor and execute processing.

        :param context: Processing context
        :return: Tuple of (start_time, end_time, duration)
        """
        self.processor = OrionAgentProcessor(agent=self, global_context=context)

        start_time = time.time()
        await self.processor.process()
        end_time = time.time()

        return start_time, end_time, end_time - start_time

    def _update_agent_status(self) -> None:
        """
        Update agent status from processor context.
        """
        self.status = self.processor.processing_context.get_local("status").upper()
        self.logger.info(f"Orion agent status updated to: {self.status}")

    async def _validate_and_update_orion(
        self, orion: TaskOrion
    ) -> TaskOrion:
        """
        Validate orion DAG structure and update status if invalid.

        :param orion: The orion to validate
        :return: The validated orion
        """
        is_dag, errors = orion.validate_dag()

        if not is_dag:
            self.logger.error(f"The created orion is not a valid DAG: {errors}")
            self.status = OrionAgentStatus.FAIL.value

        self._current_orion = orion
        return orion

    def _create_timing_info(
        self, start_time: float, end_time: float, duration: float
    ) -> Dict[str, float]:
        """
        Create timing information dictionary.

        :param start_time: Processing start time
        :param end_time: Processing end time
        :param duration: Processing duration
        :return: Dictionary containing timing information
        """
        return {
            "processing_start_time": start_time,
            "processing_end_time": end_time,
            "processing_duration": duration,
        }

    async def _sync_orion_to_mcp(
        self, orion: TaskOrion, context: Context
    ) -> None:
        """
        Sync orion to MCP server.

        :param orion: The orion to sync
        :param context: Processing context
        """
        await context.command_dispatcher.execute_commands(
            commands=[
                Command(
                    tool_name="build_orion",
                    parameters={
                        "config": orion.to_basemodel(),
                        "clear_existing": True,
                    },
                    tool_type="action",
                )
            ]
        )

    def _log_orion_state(
        self, orion: TaskOrion, prefix: str = ""
    ) -> None:
        """
        Log orion state information.

        :param orion: The orion to log
        :param prefix: Prefix for log messages
        """
        self.logger.info(f"{prefix}Task ID: {orion.tasks.keys()}")
        self.logger.info(f"{prefix}Dependency ID: {orion.dependencies.keys()}")

    def _log_task_statuses(
        self, orion: TaskOrion, task_ids: List[str], stage: str
    ) -> None:
        """
        Log status for specific tasks.

        :param orion: The orion containing the tasks
        :param task_ids: List of task IDs to log
        :param stage: Stage description (e.g., 'before editing', 'after editing')
        """
        for tid in task_ids:
            task = orion.get_task(tid)
            if task:
                self.logger.info(f"[STATUS] Status for task {stage} {tid}: {task.status}")

    async def _publish_orion_modified_event(
        self,
        before_orion: TaskOrion,
        after_orion: TaskOrion,
        task_ids: List[str],
        timing_info: Dict[str, float],
    ) -> None:
        """
        Publish orion modified event.

        :param before_orion: The orion before modification
        :param after_orion: The orion after modification
        :param task_ids: List of task IDs that were modified
        :param timing_info: Timing information for the modification
        """
        await self._event_bus.publish_event(
            OrionEvent(
                event_type=EventType.ORION_MODIFIED,
                source_id=self.name,
                timestamp=time.time(),
                data={
                    "old_orion": before_orion,
                    "new_orion": after_orion,
                    "modification_type": f"Edited by {self.name}",
                    "on_task_id": task_ids,
                    **timing_info,
                },
                orion_id=after_orion.orion_id,
                orion_state=(
                    after_orion.state.value
                    if after_orion.state
                    else "unknown"
                ),
            )
        )

    async def _handle_orion_completion(
        self,
        before_orion: TaskOrion,
        after_orion: TaskOrion,
    ) -> None:
        """
        Handle orion completion logic.

        :param before_orion: The orion before completion
        :param after_orion: The orion after completion
        """
        try:
            await asyncio.wait_for(
                self.orion_completion_queue.get(), timeout=1.0
            )

            self.logger.info(
                f"The old orion {before_orion.orion_id} is completed."
            )

            if (
                self.status == OrionAgentStatus.CONTINUE.value
                and not after_orion.is_complete()
            ):
                self.logger.info(
                    f"New update to the orion {before_orion.orion_id} needed, restart the orchestration"
                )
                self.status = OrionAgentStatus.START.value

        except asyncio.TimeoutError:
            pass

    # ==================== Public Interface Methods ====================

    # IRequestProcessor implementation
    async def process_creation(
        self,
        context: Context,
    ) -> Tuple[TaskOrion, Dict[str, float]]:
        """
        Process a user request and generate a orion.

        :param request: User request string
        :param context: Optional processing context
        :return: Tuple of (Generated orion, processing timing info)
        :raises OrionError: If orion generation fails
        """
        # Initialize
        await self._initialize_prompter(context)
        await self._ensure_context_provision(context)

        # Process
        start_time, end_time, duration = await self._create_and_process(context)

        # Update status and get orion
        self._update_agent_status()
        created_orion = context.get(ContextNames.ORION)

        # Validate
        if created_orion:
            await self._validate_and_update_orion(created_orion)

        # Return result with timing
        return self._current_orion, self._create_timing_info(
            start_time, end_time, duration
        )

    # IResultProcessor implementation
    async def process_editing(
        self,
        context: Context = None,
        task_ids: Optional[List[str]] = None,
        before_orion: Optional[TaskOrion] = None,
    ) -> TaskOrion:
        """
        Process task completion events and potentially update the orion.

        :param context: Optional processing context
        :param task_ids: List of task IDs that were just completed
        :param before_orion: The orion before editing
        :return: Updated orion
        :raises TaskExecutionError: If result processing fails
        """
        # Initialize
        await self._initialize_prompter(context)
        await self.context_provision(context=context)

        # Prepare orion
        if not before_orion:
            before_orion = context.get(ContextNames.ORION)
        else:
            context.set(ContextNames.ORION, before_orion)

        task_ids = task_ids or []

        # Log and sync before state
        self.logger.debug(
            f"Tasks {task_ids} marked as completed, Agent's orion updated, completed tasks ids: "
            f"{[t.task_id for t in before_orion.get_completed_tasks()]}"
        )
        await self._sync_orion_to_mcp(before_orion, context)
        self._log_orion_state(
            before_orion, "Task ID for orion before editing: "
        )
        self._log_task_statuses(before_orion, task_ids, "before editing")
        self._log_orion_state(
            before_orion, "Dependency ID for orion before editing: "
        )

        # Process
        start_time, end_time, duration = await self._create_and_process(context)

        # Update status and get orion
        self._update_agent_status()
        after_orion = context.get(ContextNames.ORION)

        # Log after state
        self._log_task_statuses(after_orion, task_ids, "after editing")

        # Handle completion
        await self._handle_orion_completion(
            before_orion, after_orion
        )

        # Validate
        await self._validate_and_update_orion(after_orion)

        # Sync and publish event
        await self._sync_orion_to_mcp(after_orion, context)
        self._log_orion_state(
            after_orion, "Task ID for orion after editing: "
        )
        self._log_orion_state(
            after_orion, "Dependency ID for orion after editing: "
        )

        await self._publish_orion_modified_event(
            before_orion,
            after_orion,
            task_ids,
            self._create_timing_info(start_time, end_time, duration),
        )

        return after_orion

    async def context_provision(
        self, context: Context, mask_creation: bool = True
    ) -> None:
        """
        Provide the context for the agent.

        :param context: The context for the agent
        :param mask_creation: Whether to mask the tool for creation of orion
        """
        await self._load_mcp_context(context, mask_creation)

    async def _load_mcp_context(
        self, context: Context, mask_creation: bool = True
    ) -> None:
        """
        Load MCP context information for the current application.

        :param context: The context for the agent
        :param mask_creation: Whether to mask the tool for creation of orion
        """

        self.logger.info("Loading MCP tool information...")
        result = await context.command_dispatcher.execute_commands(
            [
                Command(
                    tool_name="list_tools",
                    parameters={
                        "tool_type": "action",
                    },
                    tool_type="action",
                )
            ]
        )

        if result[0].status == ResultStatus.FAILURE:
            tool_list = []
            self.logger.warning(
                f"Failed to load MCP tool information: {result[0].result}"
            )
        else:
            tool_list = result[0].result if result else []

        # Mask the creation tool for the prompt
        if mask_creation:
            tool_list = [
                tool
                for tool in tool_list
                if tool.get("tool_name") != self._orion_creation_tool_name
            ]

        tool_name_list = (
            [tool.get("tool_name") for tool in tool_list if tool.get("tool_name")]
            if tool_list
            else []
        )

        self.logger.info(f"Loaded tool list: {tool_name_list} for {self.name}.")

        tools_info = [MCPToolInfo(**tool) for tool in tool_list]
        self.logger.debug(f"Loaded tool tools_info: {tools_info}.")

        self.prompter.create_api_prompt_template(tools=tools_info)

    def get_prompter(self, weaving_mode: WeavingMode) -> BaseOrionPrompter:
        """
        Get the prompter for the agent using factory pattern.

        :param weaving_mode: The weaving mode for the agent
        :return: The prompter for the agent
        """
        self.logger.info(f"Creating prompter for {weaving_mode}")
        return OrionPrompterFactory.create_prompter(weaving_mode=weaving_mode)

    def message_constructor(
        self,
        request: str,
        device_info: Dict[str, AgentProfile],
        orion: TaskOrion,
    ) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        """
        Construct the message for LLM interaction.

        :param request: The user request
        :param device_info: Information about the user's device
        :param orion: The current task orion
        :return: A list of message dictionaries for LLM interaction
        """

        if not self.prompter:
            raise ValueError("Prompter is not initialized")

        system_message = self.prompter.system_prompt_construction()
        user_message = self.prompter.user_content_construction(
            request=request, device_info=device_info, orion=orion
        )

        prompt = self.prompter.prompt_construction(system_message, user_message)

        return prompt

    async def process_confirmation(self, context: Context = None) -> bool:
        """
        Process confirmation for orion operations.

        :param context: Processing context
        :return: True if confirmed, False otherwise
        """
        # For now, always confirm for orion operations
        # This can be extended with actual confirmation logic
        return True

    def print_response(
        self, response: OrionAgentResponse, print_action: bool = False
    ) -> None:
        """
        Publish agent response as an event instead of directly printing.
        :param response: The OrionAgentResponse object to display
        :param print_action: Flag to indicate if action details should be printed
        """
        # Publish agent response event
        event = AgentEvent(
            event_type=EventType.AGENT_RESPONSE,
            source_id=self.name,
            timestamp=time.time(),
            data={},
            agent_name=self.name,
            agent_type="orion",
            output_type="response",
            output_data={
                **response.model_dump(),
                "print_action": print_action,
            },
        )

        # Publish event asynchronously (non-blocking)
        asyncio.create_task(get_event_bus().publish_event(event))

    @property
    def default_state(self):
        """
        Get the default state of the Orion Agent.

        :return: The default StartOrionAgentState
        """
        from .orion_agent_states import StartOrionAgentState

        return StartOrionAgentState()

    @property
    def status_manager(self):
        """Get the status manager."""

        return OrionAgentStatus

    @property
    def orchestrator(self) -> TaskOrionOrchestrator:
        """
        The orchestrator for managing orion tasks.
        :return: The task orion orchestrator.
        """
        return self._orchestrator

    @property
    def task_completion_queue(self) -> asyncio.Queue[TaskEvent]:
        """
        Get the task completion queue.
        :return: The task completion queue.
        """
        return self._task_completion_queue

    @property
    def orion_completion_queue(self) -> asyncio.Queue[OrionEvent]:
        """
        Get the orion completion queue.
        :return: The orion completion queue.
        """
        return self._orion_completion_queue

    async def add_task_completion_event(self, event: TaskEvent) -> None:
        """
        Add a task event to the task completion queue.

        :param event: TaskEvent instance to add to the queue
        :raises TypeError: If the event is not a TaskEvent instance
        :raises RuntimeError: If failed to add event to queue
        """
        if not isinstance(event, TaskEvent):
            raise TypeError(
                f"Expected TaskEvent instance, got {type(event).__name__}. "
                f"Only TaskEvent instances can be added to the task completion queue."
            )

        if event.event_type not in [
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
        ]:
            raise TypeError(
                f"Expected TaskEvent with event_type in [TASK_COMPLETED, TASK_FAILED], "
                f"got {event.event_type}."
            )

        try:
            await self._task_completion_queue.put(event)
            self.logger.info(
                f"Added task event for task '{event.task_id}' with status '{event.status}' to completion queue"
            )
        except asyncio.QueueFull as e:
            self.logger.error(f"Task completion queue is full: {str(e)}", exc_info=True)
            raise RuntimeError(f"Task completion queue is full: {str(e)}") from e
        except Exception as e:
            self.logger.error(
                f"Unexpected error adding task event to queue: {str(e)}", exc_info=True
            )
            raise RuntimeError(f"Failed to add task event to queue: {str(e)}") from e

    async def add_orion_completion_event(
        self, event: OrionEvent
    ) -> None:
        """
        Add a orion event to the orion completion queue.

        :param event: OrionEvent instance to add to the queue
        :raises TypeError: If the event is not a OrionEvent instance
        :raises RuntimeError: If failed to add event to queue
        """
        if not isinstance(event, OrionEvent):
            raise TypeError(
                f"Expected OrionEvent instance, got {type(event).__name__}. "
                f"Only OrionEvent instances can be added to the orion completion queue."
            )

        if event.event_type != EventType.ORION_COMPLETED:
            raise TypeError(
                f"Expected OrionEvent with event_type of [ORION_COMPLETED], "
                f"got {event.event_type}."
            )

        try:
            await self._orion_completion_queue.put(event)
            self.logger.info(
                f"Added orion event for orion '{event.orion_id}' "
                f"with state '{event.orion_state}' to completion queue"
            )
        except asyncio.QueueFull as e:
            self.logger.error(
                f"Orion completion queue is full: {str(e)}", exc_info=True
            )
            raise RuntimeError(
                f"Orion completion queue is full: {str(e)}"
            ) from e
        except Exception as e:
            self.logger.error(
                f"Unexpected error adding orion event to queue: {str(e)}",
                exc_info=True,
            )
            raise RuntimeError(
                f"Failed to add orion event to queue: {str(e)}"
            ) from e
