from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional

from alien.agents.processors.context.processing_context import BasicProcessorContext
from alien.agents.processors.schemas.actions import ActionCommandInfo
from alien.agents.processors.schemas.target import TargetInfo


@dataclass
class OrionProcessorContext(BasicProcessorContext):
    """
    Orion specific processor context.

    This extends the basic context with Orion specific data including
    target management, application selection, and third-party agent coordination.
    """

    # Orion specific data
    agent_type: str = "OrionAgent"
    weaving_mode: str = "CREATION"

    device_info: List[Dict] = field(default_factory=list)

    orion_before: Optional[str] = None

    orion_after: Optional[str] = None

    # Action and control information
    action_info: Optional[ActionCommandInfo] = None

    target: Optional[TargetInfo] = None

    agent_step: int = 0
    action: List[Dict[str, Any]] = field(default_factory=list)

    agent_name: str = ""

    # LLM and cost tracking
    llm_cost: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0

    # Logging and debugging
    log_path: str = ""

    @property
    def selected_keys(self) -> List[str]:
        """
        The list of selected keys for to dict.
        Returns fields corresponding to HostAgentAdditionalMemory.
        """
        return [
            "step",  # Step
            "status",  # Status
            "round_step",  # RoundStep
            "agent_step",  # AgentStep
            "round_num",  # RoundNum
            "action",  # Action
            "function_call",  # FunctionCall
            "action_representation",
            "arguments",  # Arguments
            "action_type",  # ActionType
            "request",  # Request
            "agent_type",  # Agent
            "agent_name",  # AgentName
            "cost",  # Cost
            "results",  # Results
            "execution_times",  # time_cost (mapped to execution_times)
            "total_time",
            "device_info",
            "orion_before",
            "orion_after",
            "weaving_mode",
        ]

    def to_dict(self, selective: bool = True) -> Dict[str, Any]:
        """
        Convert context to dictionary, properly handling JSON string fields.

        This method extends BasicProcessorContext.to_dict() to parse
        orion_before and orion_after from JSON strings
        back to dictionaries to avoid double serialization.

        :param selective: Whether to include only selected keys
        :return: Dictionary representation of context data
        """
        # Get base dictionary from parent class
        result = super().to_dict(selective)

        # Parse JSON string fields back to dictionaries to avoid double serialization
        # when json.dumps() is called on the result
        if "orion_before" in result and isinstance(
            result["orion_before"], str
        ):
            try:
                result["orion_before"] = json.loads(
                    result["orion_before"]
                )
            except (json.JSONDecodeError, TypeError):
                # Keep as string if parsing fails
                pass

        if "orion_after" in result and isinstance(
            result["orion_after"], str
        ):
            try:
                result["orion_after"] = json.loads(
                    result["orion_after"]
                )
            except (json.JSONDecodeError, TypeError):
                # Keep as string if parsing fails
                pass

        return result
