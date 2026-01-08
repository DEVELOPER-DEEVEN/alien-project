# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
clusterSession - DAG-based Task Orchestration Session

This module provides the clusterSession class that extends BaseSession to support
DAG-based task orchestration using the cluster framework. The session manages
the lifecycle of network execution and coordinates between network
and TasknetworkOrchestrator.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from config.config_loader import get_cluster_config
from Alien import utils
from Alien.client.mcp.mcp_server_manager import MCPServerManager
from Alien.module.basic import BaseRound, BaseSession
from Alien.module.context import Context, ContextNames
from Alien.module.dispatcher import LocalCommandDispatcher

from ..agents.network_agent import networkAgent
from ..client.network_client import networkClient
from ..network import Tasknetwork, TasknetworkOrchestrator
from ..network.enums import networkState
from ..core.events import get_event_bus
from ..trajectory.cluster_parser import clusterTrajectory
from .observers import (
    AgentOutputObserver,
    networkModificationSynchronizer,
    networkProgressObserver,
    DAGVisualizationObserver,
    SessionMetricsObserver,
)

# Load cluster configuration
cluster_config = get_cluster_config()


class clusterRound(BaseRound):
    """
    A round in clusterSession that manages network execution.
    """

    def __init__(
        self,
        request: str,
        agent: networkAgent,
        context: Context,
        should_evaluate: bool,
        id: int,
    ):
        """
        Initialize clusterRound with orchestrator support.

        :param request: User request string
        :param agent: networkAgent instance
        :param context: Context object for the round
        :param should_evaluate: Whether to evaluate the round
        :param id: Round identifier
        """
        super().__init__(request, agent, context, should_evaluate, id)

        self._execution_start_time: Optional[float] = None
        self._agent = agent
        self._is_finished = False

    async def run(self) -> None:
        """
        Run the round using agent state machine.

        Executes the agent state machine until completion,
        managing state transitions and error handling.
        """
        try:
            self.logger.info(
                f"Starting clusterRound {self._id} with request: {self._request[:100]}..."
            )

            # Set up agent with current request and orchestrator
            self._agent.current_request = self._request

            # Initialize agent in START state
            from ..agents.network_agent_states import StartnetworkAgentState

            self._agent.set_state(StartnetworkAgentState())

            # Run agent state machine until completion
            while not self.is_finished():
                # Execute current state
                await self._agent.handle(self._context)

                # Transition to next state
                self.state = self._agent.state.next_state(self._agent)
                self.logger.info(
                    f"Transitioning from {self._agent.state.name()} to {self.state.name()}"
                )

                # Update agent state
                self._agent.set_state(self.state)

                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)

            self.logger.info(
                f"clusterRound {self._id} completed with status: {self._agent._status}"
            )

            return self.context.get(ContextNames.ROUND_RESULT)

        except AttributeError as e:
            self.logger.error(
                f"Attribute error in clusterRound execution: {e}", exc_info=True
            )
            import traceback

            traceback.print_exc()
        except KeyError as e:
            self.logger.error(
                f"Missing context key in clusterRound execution: {e}", exc_info=True
            )
            import traceback

            traceback.print_exc()
        except Exception as e:
            self.logger.error(
                f"Unexpected error in clusterRound execution: {e}", exc_info=True
            )
            import traceback

            traceback.print_exc()

    def is_finished(self):
        """
        Verify if the round is finished.
        """
        # Check if force finished
        if self._is_finished:
            return True

        if (
            self.state.is_round_end()
            or self.context.get(ContextNames.SESSION_STEP)
            >= cluster_config.network.MAX_STEP
        ):
            return True

        return False

    def force_finish(self) -> None:
        """
        Force finish the round immediately.
        """
        self._agent.status = "FINISH"
        self._is_finished = True

    @property
    def network(self) -> Optional[Tasknetwork]:
        """
        Get the current network.

        :return: Tasknetwork instance if available, None otherwise
        """
        return self._network


class clusterSession(BaseSession):
    """
    cluster Session for DAG-based task orchestrator.

    This session extends BaseSession to support network-based task execution
    using network for DAG management and TasknetworkOrchestrator for execution.
    """

    def __init__(
        self,
        task: str,
        should_evaluate: bool,
        id: str,
        client: Optional[networkClient] = None,
        initial_request: str = "",
    ):
        """
        Initialize clusterSession.

        :param task: Task name/description
        :param should_evaluate: Whether to evaluate the session
        :param id: Session ID
        :param agent: networkAgent instance (creates MocknetworkAgent if None)
        :param client: networkClient for device management
        :param initial_request: Initial user request
        """
        self._should_evaluate = should_evaluate
        self._id = id
        self.task = task

        # Logging-related properties (sanitize task name for path)
        safe_task_name = "".join(
            c for c in task if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_task_name = safe_task_name[:50]  # Limit length to 50 characters
        if not safe_task_name:
            safe_task_name = f"cluster_session_{id}"
        self.log_path = f"logs/cluster/{safe_task_name}/"
        utils.create_folder(self.log_path)

        self._rounds: Dict[int, BaseRound] = {}

        self._context = Context()
        self._client = client
        self.logger = logging.getLogger(__name__)

        self._init_context()
        self._finish = False
        self._results = []

        # Cancellation support
        self._cancellation_requested = False

        # Set up client and orchestrator

        self._orchestrator = TasknetworkOrchestrator(
            device_manager=client.device_manager, enable_logging=True
        )

        self._init_agents()

        # Session state
        self._initial_request = initial_request
        self._current_network: Optional[Tasknetwork] = None
        self._session_start_time: Optional[float] = None
        self._session_results: Dict[str, Any] = {}

        # Event system
        self._event_bus = get_event_bus()
        self._observers = []
        self._modification_synchronizer: Optional[
            networkModificationSynchronizer
        ] = None

        # Set up observers
        self._setup_observers()

    def _init_context(self) -> None:
        """
        Initialize the context.
        """
        super()._init_context()

        # Get all devices from registry (both connected and disconnected)
        # This ensures LLM always knows about available devices even during reconnection
        all_devices = self._client.device_manager.get_all_devices(connected=False)

        self.logger.info(
            f"🔍 DEBUG: Retrieved {len(all_devices)} devices from registry: {list(all_devices.keys())}"
        )

        self.context.set(
            ContextNames.DEVICE_INFO,
            all_devices,
        )
        self.logger.info(
            f"The following devices has been registered and added to the context: {self.context.get(ContextNames.DEVICE_INFO)}"
        )

        mcp_server_manager = MCPServerManager()
        command_dispatcher = LocalCommandDispatcher(self, mcp_server_manager)
        self.context.attach_command_dispatcher(command_dispatcher)

    def _init_agents(self) -> None:
        """
        Initilize the agent.
        """
        self._agent = networkAgent(orchestrator=self._orchestrator)

    def _setup_observers(self) -> None:
        """
        Set up event observers for this round.

        Initializes progress, metrics, visualization, and agent output observers
        and subscribes them to the event bus.
        """
        # Progress observer for task updates
        progress_observer = networkProgressObserver(agent=self._agent)
        self._observers.append(progress_observer)

        # Metrics observer for performance tracking
        self._metrics_observer = SessionMetricsObserver(
            session_id=f"cluster_session_{self._id}", logger=self.logger
        )
        self._observers.append(self._metrics_observer)

        # DAG visualization observer for network visualization
        visualization_observer = DAGVisualizationObserver(enable_visualization=True)
        self._observers.append(visualization_observer)

        # Agent output observer for handling agent responses and actions
        agent_output_observer = AgentOutputObserver(presenter_type="rich")
        self._observers.append(agent_output_observer)

        # Modification synchronizer for coordinating network updates
        self._modification_synchronizer = networkModificationSynchronizer(
            orchestrator=self._orchestrator,
            logger=self.logger,
        )
        self._observers.append(self._modification_synchronizer)

        # Attach synchronizer to orchestrator
        self._orchestrator.set_modification_synchronizer(
            self._modification_synchronizer
        )

        # Subscribe observers to event bus
        for observer in self._observers:
            self._event_bus.subscribe(observer)

        self.logger.info(
            f"Set up {len(self._observers)} observers including modification synchronizer"
        )

    async def run(self) -> None:
        """
        Run the cluster session with network orchestrator.

        Executes the session using the base session logic with
        network support and tracks performance metrics.
        """
        try:
            self.logger.info(f"Starting clusterSession: {self.task}")
            self._session_start_time = time.time()

            # Run base session logic with network support
            final_results = await super().run()

            # Calculate total session time
            if self._session_start_time:
                total_time = time.time() - self._session_start_time
                self.logger.info(f"clusterSession completed in {total_time:.2f}s")
                self._session_results["total_execution_time"] = total_time

            self._current_network = self.context.get(ContextNames.network)
            # Final network status
            if self._current_network:
                self._session_results["final_network_stats"] = (
                    self._current_network.get_statistics()
                )

            self._session_results["status"] = self._agent.status
            self._session_results["final_results"] = final_results
            self._session_results["metrics"] = self._metrics_observer.get_metrics()

            if cluster_config.network.LOG_TO_MARKDOWN:

                file_path = self.log_path
                trajectory = clusterTrajectory(file_path)
                trajectory.to_markdown(file_path + "output.md")

        except AttributeError as e:
            self.logger.error(f"Attribute error in clusterSession: {e}", exc_info=True)
            import traceback

            traceback.print_exc()
        except KeyError as e:
            self.logger.error(
                f"Missing key in clusterSession context: {e}", exc_info=True
            )
            import traceback

            traceback.print_exc()
        except TypeError as e:
            self.logger.error(f"Type error in clusterSession: {e}", exc_info=True)
            import traceback

            traceback.print_exc()
        except Exception as e:
            self.logger.error(f"Unexpected error in clusterSession: {e}", exc_info=True)
            import traceback

            traceback.print_exc()
        # Note: Observer cleanup is now handled externally when creating a new session
        # to ensure observers remain active throughout the async network execution

    def is_error(self) -> bool:
        """
        Check if the session is in error state.

        Override base implementation to handle cluster-specific logic
        by checking weaver agent status and network state.

        :return: True if session is in error state, False otherwise
        """

        # Check if current network failed
        if self._current_network:
            return self._current_network.state == networkState.FAILED

        # Fall back to checking rounds if they exist
        if self.current_round is not None and self.current_round.state is not None:
            try:
                from Alien.agents.states.basic import AgentStatus

                return self.current_round.state.name() == AgentStatus.ERROR.value
            except (AttributeError, ImportError):
                pass

        return False

    def is_finished(self) -> bool:
        """
        Check if the session is finished.

        Override base implementation to handle cluster-specific logic
        by checking completion conditions, error states, and network status.

        :return: True if session is finished, False otherwise
        """
        # Check standard completion conditions
        if (
            self._finish
            or self.step >= cluster_config.network.MAX_STEP
            or self.total_rounds >= cluster_config.network.MAX_STEP
        ):
            return True

        return False

    def create_new_round(self) -> Optional[clusterRound]:
        """
        Create a new clusterRound.

        :return: clusterRound instance if request is available, None otherwise
        """
        request = self.next_request()
        if not request:
            return None

        round_id = len(self._rounds)

        cluster_round = clusterRound(
            request=request,
            agent=self._agent,
            context=self._context,
            should_evaluate=self._should_evaluate,
            id=round_id,
        )

        self.add_round(round_id, cluster_round)
        return cluster_round

    def next_request(self) -> str:
        """
        Get the next request for the session.

        :return: Request string for the next round, empty string if no more requests
        """
        # For now, only process one request per session
        if len(self._rounds) == 0:
            return self._initial_request
        return ""  # No more requests

    def request_to_evaluate(self) -> str:
        """
        Get the request for evaluation.

        :return: Request string to be used for evaluation
        """
        return self._initial_request or self.task

    def set_agent(self, agent: networkAgent) -> None:
        """
        Set the weaver agent.

        :param agent: networkAgent instance for task orchestration
        """
        self._agent = agent

    async def force_finish(self, reason: str = "Manual termination") -> None:
        """
        Force finish the session.

        :param reason: Reason for forcing the finish (default: "Manual termination")
        """
        self.logger.info(f"Force finishing session: {reason}")
        self._finish = True
        self._agent.status = "FINISH"
        self._session_results["finish_reason"] = reason

        # Force finish current round if it exists
        if self.current_round:
            self.current_round.force_finish()

    async def request_cancellation(self) -> None:
        """
        Request immediate cancellation of current execution.

        This method sets the cancellation flag and attempts to cancel
        the orchestrator's network execution.
        """
        self.logger.info("🛑 Cancellation requested for session")
        self._cancellation_requested = True
        self._finish = True

        # Force finish current round if it exists
        if self.current_round:
            self.current_round.force_finish()

        # Cancel the orchestrator's current execution if available
        if self._current_network:
            network_id = self._current_network.network_id
            self.logger.info(
                f"🛑 Requesting cancellation for network {network_id}"
            )
            await self._orchestrator.cancel_execution(network_id)

        # Clean up observers to prevent duplicate event transmission
        self._cleanup_observers()

    def reset(self) -> None:
        """
        Reset the session state for a new request.

        Clears network, tasks, rounds, and execution history
        while keeping the session instance, observers, and device info intact.
        """
        # Save device info before clearing (should not be cleared on reset)
        device_info = self._context.get(ContextNames.DEVICE_INFO)

        # Reset agent state to default if available
        default_state = self._agent.default_state
        if default_state is not None:
            self._agent.set_state(default_state)
        else:
            self.logger.warning(
                f"Agent {type(self._agent).__name__} has no default_state defined, skipping state reset"
            )

        # Clear rounds and results
        self._rounds.clear()
        self._results = []
        self._session_results = {}

        # Clear network reference
        self._current_network = None
        self._context.set(ContextNames.network, None)

        # Restore device info (devices should persist across resets)
        if device_info is not None:
            self._context.set(ContextNames.DEVICE_INFO, device_info)
            self.logger.info(f"Device info preserved: {len(device_info)} devices")

        # Reset finish flag
        self._finish = False

        # Reset cancellation flag
        self._cancellation_requested = False

        # Reset timing
        self._session_start_time = None

        self.logger.info("Session state reset - ready for new request")

    def _cleanup_observers(self) -> None:
        """
        Clean up event observers for this session.

        Unsubscribes all observers from the event bus to prevent
        duplicate event handling across multiple sessions.
        """
        for observer in self._observers:
            self._event_bus.unsubscribe(observer)
        self.logger.info(f"Cleaned up {len(self._observers)} observers from event bus")

    @property
    def current_network(self) -> Optional[Tasknetwork]:
        """
        Get the current network.

        :return: Tasknetwork instance from agent if available
        """
        return self._agent.current_network

    @property
    def agent(self) -> networkAgent:
        """
        Get the agent.

        :return: networkAgent instance for task orchestration
        """
        return self._agent

    @property
    def orchestrator(self) -> TasknetworkOrchestrator:
        """
        Get the task orchestrator.

        :return: TasknetworkOrchestrator instance for execution management
        """
        return self._orchestrator

    @property
    def session_results(self) -> Dict[str, Any]:
        """
        Get session results.

        :return: Dictionary containing session execution results and metrics
        """
        return self._session_results
