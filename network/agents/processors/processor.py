
"""
Orion Agent Processor - Processor for Orion Agent using the new framework.
"""


import logging
import traceback
from typing import TYPE_CHECKING, Any, Dict, Type

from rich.console import Console
from rich.panel import Panel

from network.agents.processors.processor_context import OrionProcessorContext
from network.agents.processors.strategies.orion_factory import (
    OrionStrategyFactory,
)
from network.orion.task_orion import TaskOrion
from alien.agents.processors.core.processing_middleware import EnhancedLoggingMiddleware
from alien.agents.processors.core.processor_framework import (
    ProcessingContext,
    ProcessingPhase,
    ProcessorTemplate,
)
from alien.module.context import Context, ContextNames

if TYPE_CHECKING:
    from network.agents.orion_agent import OrionAgent


console = Console()


class OrionAgentProcessor(ProcessorTemplate):
    """
    Enhanced processor for Network Creator Agent with comprehensive functionality.

    This processor manages the complete workflow of a Network Creator Agent including:
    - Desktop environment analysis and screenshot capture
    - Application window detection and registration
    - Third-party agent integration and management
    - LLM-based decision making with context-aware prompting
    - Action execution including application selection and command dispatch
    - Memory management with detailed logging and state tracking

    This processor maintains compatibility with the original BaseProcessor
    interface while providing enhanced modularity and error handling.
    """

    # Override the processor context class to use OrionProcessorContext
    processor_context_class: Type[OrionProcessorContext] = (
        OrionProcessorContext
    )

    def __init__(self, agent: "OrionAgent", global_context: Context) -> None:
        """
        Initialize the Network Creator Agent Processor with enhanced capabilities.
        :param agent: The Network Creator Agent instance to be processed
        :param global_context: Global context shared across the session
        """

        # Initialize parent class
        super().__init__(agent, global_context)

    def _setup_strategies(self) -> None:
        """
        Configure processing strategies with enhanced error handling and logging capabilities.
        Uses factory pattern to create appropriate strategies based on weaving mode.
        """
        # Get weaving mode from global context
        weaving_mode = self.global_context.get(ContextNames.WEAVING_MODE)

        if not weaving_mode:
            raise ValueError("Weaving mode must be specified in global context")

        # Create strategies using factory based on weaving mode
        self.strategies[ProcessingPhase.LLM_INTERACTION] = (
            OrionStrategyFactory.create_llm_interaction_strategy(
                fail_fast=True,  # LLM interaction failure should trigger recovery
            )
        )
        self.strategies[ProcessingPhase.ACTION_EXECUTION] = (
            OrionStrategyFactory.create_action_execution_strategy(
                weaving_mode=weaving_mode,
                fail_fast=False,  # Action failures can be handled gracefully
            )
        )
        self.strategies[ProcessingPhase.MEMORY_UPDATE] = (
            OrionStrategyFactory.create_memory_update_strategy(
                fail_fast=False  # Memory update failures shouldn't stop the process
            )
        )

    def _setup_middleware(self) -> None:
        """
        Set up enhanced middleware chain with comprehensive monitoring and recovery.
        The middleware chain includes:
        - OrionLoggingMiddleware: Specialized logging for Orion Agent operations
        """
        self.middleware_chain = [
            OrionLoggingMiddleware(),  # Specialized logging for Orion Agent
        ]

    def _get_processor_specific_context_data(self) -> Dict[str, Any]:
        """
        Get processor-specific context data.

        Subclasses can override this method to provide additional context data
        specific to their processor type.

        :return: Dictionary of processor-specific context initialization data
        """

        before_orion: TaskOrion = self.global_context.get(
            ContextNames.ORION
        )

        if before_orion:
            orion_before_json = before_orion.to_json()
        else:
            orion_before_json = None

        return {
            "weaving_mode": self.global_context.get(ContextNames.WEAVING_MODE),
            "device_info": self.global_context.get(ContextNames.DEVICE_INFO),
            "orion_before": orion_before_json,
        }

    def _finalize_processing_context(
        self, processing_context: ProcessingContext
    ) -> None:
        """
        Finalize processing context by updating existing ContextNames fields.
        Instead of promoting arbitrary keys, we update the predefined ContextNames
        that the system actually uses.
        :param processing_context: The processing context to finalize.
        """

        super()._finalize_processing_context(processing_context)

        results = processing_context.get_local("results")
        if results:
            self.global_context.set(ContextNames.ROUND_RESULT, results)


class OrionLoggingMiddleware(EnhancedLoggingMiddleware):
    """
    Specialized logging middleware for Orion Agent with enhanced contextual information.

    This middleware provides:
    - Orion Agent specific progress messages with color coding
    - Detailed step information and context logging
    - Performance metrics and execution summaries
    - Enhanced error reporting with Orion Agent context
    """

    def __init__(self) -> None:
        """Initialize Orion Agent logging middleware with appropriate log level."""
        super().__init__(log_level=logging.INFO)

    async def before_process(
        self, processor: ProcessorTemplate, context: ProcessingContext
    ) -> None:
        """
        Log Orion Agent processing start with detailed context information.
        :param processor: Orion Agent processor instance
        :param context: Processing context with round and step information
        """
        # Call parent implementation for standard logging
        await super().before_process(processor, context)

        # Add Orion Agent specific logging
        round_num = context.get("round_num", 0)
        round_step = context.get("round_step", 0)
        request = context.get("request", "")

        # Log detailed context information
        self.logger.info(
            f"Orion Agent Processing Context - "
            f"Round: {round_num + 1}, Step: {round_step + 1}, "
            f"Request: '{request[:100]}{'...' if len(request) > 100 else ''}'"
        )
        weaving_mode = context.global_context.get(
            ContextNames.WEAVING_MODE
        ).value.upper()

        panel_title = f"🚀 Round {round_num + 1}, Step {round_step + 1}, Agent: {processor.agent.name}, Weaving Mode: {weaving_mode}"
        panel_content = f"Analyzing user intent and decomposing request of `{request}` into device agents..."

        console.print(Panel(panel_content, title=panel_title, style="magenta"))

        # Log available context data for debugging
        if self.logger.isEnabledFor(logging.DEBUG):
            context_keys = list(
                context.local_data.keys()
            )  # This uses the backward-compatible property
            self.logger.debug(f"Available context keys: {context_keys}")

    async def on_error(self, processor: ProcessorTemplate, error: Exception) -> None:
        """
        Enhanced error handling for Orion Agent with contextual information.
        :param processor: Orion Agent processor instance
        :param error: Exception that occurred
        """
        # Call parent implementation for standard error handling
        await super().on_error(processor, error)
        tb_str = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )

        self.logger.error(
            f"OrionAgent: Encountered error - {str(tb_str)}", "red"
        )
