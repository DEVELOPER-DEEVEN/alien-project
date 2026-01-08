# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
network - DAG-based Task Orchestration Agent

This module provides the network interface for managing DAG-based task orchestration
in the cluster framework. The network is responsible for processing user requests,
generating and updating DAGs, and managing task execution status.

Optimized for type safety, maintainability, and follows SOLID principles.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Union

from cluster.agents.network_agent_states import networkAgentStatus
from cluster.agents.processors.processor import networkAgentProcessor
from cluster.agents.prompters.base_network_prompter import (
    BasenetworkPrompter,
    networkPrompterFactory,
)
from cluster.agents.schema import networkAgentResponse, WeavingMode
from cluster.client.components.types import AgentProfile
from cluster.network.orchestrator.orchestrator import TasknetworkOrchestrator
from cluster.core.events import (
    AgentEvent,
    networkEvent,
    EventType,
    TaskEvent,
    get_event_bus,
)

# Import BasicAgent and networkAgentStatus here to avoid circular import at module level
from Alien.agents.agent.basic import BasicAgent
from aip.messages import Command, MCPToolInfo, ResultStatus
from Alien.module.context import Context, ContextNames

from ..network import Tasknetwork
from ..core.interfaces import IRequestProcessor, IResultProcessor


class networkAgent(BasicAgent, IRequestProcessor, IResultProcessor):
    """
    network - A specialized agent for DAG-based task orchestration.

    The network extends BasicAgent and implements multiple interfaces:
    - IRequestProcessor: Process user requests to generate initial DAGs
    - IResultProcessor: Process task execution results and update DAGs

    Key responsibilities:
    - Process user requests to generate initial DAGs
    - Update DAGs based on task execution results
    - Manage task status and network state
    - Coordinate with TasknetworkOrchestrator for execution

    This class follows the Interface Segregation Principle by implementing
    focused interfaces rather than one large interface.
    """

    _network_creation_tool_name: str = "build_network"

    def __init__(
        self,
        orchestrator: TasknetworkOrchestrator,
        name: str = "network_agent",
    ):
        """
        Initialize the network.

        :param name: Agent name (default: "network_agent")
        :param orchestrator: Task orchestrator instance
        """

        super().__init__(name)

        self._current_network: Optional[Tasknetwork] = None
        self._status: str = "START"  # start, continue, finish, fail
        self.logger = logging.getLogger(__name__)

        # Add state machine support
        self.current_request: str = ""
        self._orchestrator = orchestrator

        self._task_completion_queue = asyncio.Queue()
        self._network_completion_queue = asyncio.Queue()

        self._context_provision_executed = False
        self._event_bus = get_event_bus()

        self.prompter = None  # Will be initialized when weaving_mode is known

        # Initialize with start state
        from .network_agent_states import StartnetworkAgentState

        self.set_state(StartnetworkAgentState())

    @property
    def current_network(self) -> Optional[Tasknetwork]:
        """
        Get the current network being managed.

        :return: Current network instance or None
        """
        return self._current_network

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
        self.processor = networkAgentProcessor(agent=self, global_context=context)

        start_time = time.time()
        await self.processor.process()
        end_time = time.time()

        return start_time, end_time, end_time - start_time

    def _update_agent_status(self) -> None:
        """
        Update agent status from processor context.
        """
        self.status = self.processor.processing_context.get_local("status").upper()
        self.logger.info(f"network agent status updated to: {self.status}")

    async def _validate_and_update_network(
        self, network: Tasknetwork
    ) -> Tasknetwork:
        """
        Validate network DAG structure and update status if invalid.

        :param network: The network to validate
        :return: The validated network
        """
        is_dag, errors = network.validate_dag()

        if not is_dag:
            self.logger.error(f"The created network is not a valid DAG: {errors}")
            self.status = networkAgentStatus.FAIL.value

        self._current_network = network
        return network

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

    async def _sync_network_to_mcp(
        self, network: Tasknetwork, context: Context
    ) -> None:
        """
        Sync network to MCP server.

        :param network: The network to sync
        :param context: Processing context
        """
        await context.command_dispatcher.execute_commands(
            commands=[
                Command(
                    tool_name="build_network",
                    parameters={
                        "config": network.to_basemodel(),
                        "clear_existing": True,
                    },
                    tool_type="action",
                )
            ]
        )

    def _log_network_state(
        self, network: Tasknetwork, prefix: str = ""
    ) -> None:
        """
        Log network state information.

        :param network: The network to log
        :param prefix: Prefix for log messages
        """
        self.logger.info(f"{prefix}Task ID: {network.tasks.keys()}")
        self.logger.info(f"{prefix}Dependency ID: {network.dependencies.keys()}")

    def _log_task_statuses(
        self, network: Tasknetwork, task_ids: List[str], stage: str
    ) -> None:
        """
        Log status for specific tasks.

        :param network: The network containing the tasks
        :param task_ids: List of task IDs to log
        :param stage: Stage description (e.g., 'before editing', 'after editing')
        """
        for tid in task_ids:
            task = network.get_task(tid)
            if task:
                self.logger.info(f"📊 Status for task {stage} {tid}: {task.status}")

    async def _publish_network_modified_event(
        self,
        before_network: Tasknetwork,
        after_network: Tasknetwork,
        task_ids: List[str],
        timing_info: Dict[str, float],
    ) -> None:
        """
        Publish network modified event.

        :param before_network: The network before modification
        :param after_network: The network after modification
        :param task_ids: List of task IDs that were modified
        :param timing_info: Timing information for the modification
        """
        await self._event_bus.publish_event(
            networkEvent(
                event_type=EventType.network_MODIFIED,
                source_id=self.name,
                timestamp=time.time(),
                data={
                    "old_network": before_network,
                    "new_network": after_network,
                    "modification_type": f"Edited by {self.name}",
                    "on_task_id": task_ids,
                    **timing_info,
                },
                network_id=after_network.network_id,
                network_state=(
                    after_network.state.value
                    if after_network.state
                    else "unknown"
                ),
            )
        )

    async def _handle_network_completion(
        self,
        before_network: Tasknetwork,
        after_network: Tasknetwork,
    ) -> None:
        """
        Handle network completion logic.

        :param before_network: The network before completion
        :param after_network: The network after completion
        """
        try:
            await asyncio.wait_for(
                self.network_completion_queue.get(), timeout=1.0
            )

            self.logger.info(
                f"The old network {before_network.network_id} is completed."
            )

            if (
                self.status == networkAgentStatus.CONTINUE.value
                and not after_network.is_complete()
            ):
                self.logger.info(
                    f"New update to the network {before_network.network_id} needed, restart the orchestration"
                )
                self.status = networkAgentStatus.START.value

        except asyncio.TimeoutError:
            pass

    # ==================== Public Interface Methods ====================

    # IRequestProcessor implementation
    async def process_creation(
        self,
        context: Context,
    ) -> Tuple[Tasknetwork, Dict[str, float]]:
        """
        Process a user request and generate a network.

        :param request: User request string
        :param context: Optional processing context
        :return: Tuple of (Generated network, processing timing info)
        :raises networkError: If network generation fails
        """
        # Initialize
        await self._initialize_prompter(context)
        await self._ensure_context_provision(context)

        # Process
        start_time, end_time, duration = await self._create_and_process(context)

        # Update status and get network
        self._update_agent_status()
        created_network = context.get(ContextNames.network)

        # Validate
        if created_network:
            await self._validate_and_update_network(created_network)

        # Return result with timing
        return self._current_network, self._create_timing_info(
            start_time, end_time, duration
        )

    # IResultProcessor implementation
    async def process_editing(
        self,
        context: Context = None,
        task_ids: Optional[List[str]] = None,
        before_network: Optional[Tasknetwork] = None,
    ) -> Tasknetwork:
        """
        Process task completion events and potentially update the network.

        :param context: Optional processing context
        :param task_ids: List of task IDs that were just completed
        :param before_network: The network before editing
        :return: Updated network
        :raises TaskExecutionError: If result processing fails
        """
        # Initialize
        await self._initialize_prompter(context)
        await self.context_provision(context=context)

        # Prepare network
        if not before_network:
            before_network = context.get(ContextNames.network)
        else:
            context.set(ContextNames.network, before_network)

        task_ids = task_ids or []

        # Log and sync before state
        self.logger.debug(
            f"Tasks {task_ids} marked as completed, Agent's network updated, completed tasks ids: "
            f"{[t.task_id for t in before_network.get_completed_tasks()]}"
        )
        await self._sync_network_to_mcp(before_network, context)
        self._log_network_state(
            before_network, "Task ID for network before editing: "
        )
        self._log_task_statuses(before_network, task_ids, "before editing")
        self._log_network_state(
            before_network, "Dependency ID for network before editing: "
        )

        # Process
        start_time, end_time, duration = await self._create_and_process(context)

        # Update status and get network
        self._update_agent_status()
        after_network = context.get(ContextNames.network)

        # Log after state
        self._log_task_statuses(after_network, task_ids, "after editing")

        # Handle completion
        await self._handle_network_completion(
            before_network, after_network
        )

        # Validate
        await self._validate_and_update_network(after_network)

        # Sync and publish event
        await self._sync_network_to_mcp(after_network, context)
        self._log_network_state(
            after_network, "Task ID for network after editing: "
        )
        self._log_network_state(
            after_network, "Dependency ID for network after editing: "
        )

        await self._publish_network_modified_event(
            before_network,
            after_network,
            task_ids,
            self._create_timing_info(start_time, end_time, duration),
        )

        return after_network

    async def context_provision(
        self, context: Context, mask_creation: bool = True
    ) -> None:
        """
        Provide the context for the agent.

        :param context: The context for the agent
        :param mask_creation: Whether to mask the tool for creation of network
        """
        await self._load_mcp_context(context, mask_creation)

    async def _load_mcp_context(
        self, context: Context, mask_creation: bool = True
    ) -> None:
        """
        Load MCP context information for the current application.

        :param context: The context for the agent
        :param mask_creation: Whether to mask the tool for creation of network
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
                if tool.get("tool_name") != self._network_creation_tool_name
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

    def get_prompter(self, weaving_mode: WeavingMode) -> BasenetworkPrompter:
        """
        Get the prompter for the agent using factory pattern.

        :param weaving_mode: The weaving mode for the agent
        :return: The prompter for the agent
        """
        self.logger.info(f"Creating prompter for {weaving_mode}")
        return networkPrompterFactory.create_prompter(weaving_mode=weaving_mode)

    def message_constructor(
        self,
        request: str,
        device_info: Dict[str, AgentProfile],
        network: Tasknetwork,
    ) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        """
        Construct the message for LLM interaction.

        :param request: The user request
        :param device_info: Information about the user's device
        :param network: The current task network
        :return: A list of message dictionaries for LLM interaction
        """

        if not self.prompter:
            raise ValueError("Prompter is not initialized")

        system_message = self.prompter.system_prompt_construction()
        user_message = self.prompter.user_content_construction(
            request=request, device_info=device_info, network=network
        )

        prompt = self.prompter.prompt_construction(system_message, user_message)

        return prompt

    async def process_confirmation(self, context: Context = None) -> bool:
        """
        Process confirmation for network operations.

        :param context: Processing context
        :return: True if confirmed, False otherwise
        """
        # For now, always confirm for network operations
        # This can be extended with actual confirmation logic
        return True

    def print_response(
        self, response: networkAgentResponse, print_action: bool = False
    ) -> None:
        """
        Publish agent response as an event instead of directly printing.
        :param response: The networkAgentResponse object to display
        :param print_action: Flag to indicate if action details should be printed
        """
        # Publish agent response event
        event = AgentEvent(
            event_type=EventType.AGENT_RESPONSE,
            source_id=self.name,
            timestamp=time.time(),
            data={},
            agent_name=self.name,
            agent_type="network",
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
        Get the default state of the network Agent.

        :return: The default StartnetworkAgentState
        """
        from .network_agent_states import StartnetworkAgentState

        return StartnetworkAgentState()

    @property
    def status_manager(self):
        """Get the status manager."""

        return networkAgentStatus

    @property
    def orchestrator(self) -> TasknetworkOrchestrator:
        """
        The orchestrator for managing network tasks.
        :return: The task network orchestrator.
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
    def network_completion_queue(self) -> asyncio.Queue[networkEvent]:
        """
        Get the network completion queue.
        :return: The network completion queue.
        """
        return self._network_completion_queue

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

    async def add_network_completion_event(
        self, event: networkEvent
    ) -> None:
        """
        Add a network event to the network completion queue.

        :param event: networkEvent instance to add to the queue
        :raises TypeError: If the event is not a networkEvent instance
        :raises RuntimeError: If failed to add event to queue
        """
        if not isinstance(event, networkEvent):
            raise TypeError(
                f"Expected networkEvent instance, got {type(event).__name__}. "
                f"Only networkEvent instances can be added to the network completion queue."
            )

        if event.event_type != EventType.network_COMPLETED:
            raise TypeError(
                f"Expected networkEvent with event_type of [network_COMPLETED], "
                f"got {event.event_type}."
            )

        try:
            await self._network_completion_queue.put(event)
            self.logger.info(
                f"Added network event for network '{event.network_id}' "
                f"with state '{event.network_state}' to completion queue"
            )
        except asyncio.QueueFull as e:
            self.logger.error(
                f"network completion queue is full: {str(e)}", exc_info=True
            )
            raise RuntimeError(
                f"network completion queue is full: {str(e)}"
            ) from e
        except Exception as e:
            self.logger.error(
                f"Unexpected error adding network event to queue: {str(e)}",
                exc_info=True,
            )
            raise RuntimeError(
                f"Failed to add network event to queue: {str(e)}"
            ) from e
