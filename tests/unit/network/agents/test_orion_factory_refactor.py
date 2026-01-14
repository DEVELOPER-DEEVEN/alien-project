
"""
Test cases for the refactored Orion Agent factory and strategy pattern implementation.

This test suite verifies:
1. Strategy factory pattern implementation
2. Prompter factory pattern implementation
3. WeavingMode-specific behavior differentiation
4. Base class inheritance and shared logic
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

from network.agents.schema import WeavingMode
from network.agents.processors.strategies.orion_factory import (
    OrionStrategyFactory,
    OrionPrompterFactory,
)
from network.agents.processors.strategies.base_orion_strategy import (
    BaseOrionLLMInteractionStrategy,
    BaseOrionActionExecutionStrategy,
)
from network.agents.processors.strategies.orion_creation_strategy import (
    OrionCreationLLMInteractionStrategy,
    OrionCreationActionExecutionStrategy,
)
from network.agents.processors.strategies.orion_editing_strategy import (
    OrionEditingLLMInteractionStrategy,
    OrionEditingActionExecutionStrategy,
)
from network.agents.prompters.base_orion_prompter import (
    BaseOrionPrompter,
)
from network.agents.prompters.orion_creation_prompter import (
    OrionCreationPrompter,
)
from network.agents.prompters.orion_editing_prompter import (
    OrionEditingPrompter,
)
from alien.agents.processors.core.processor_framework import (
    ProcessingContext,
    ProcessingPhase,
)


class TestOrionStrategyFactory:
    """Test cases for OrionStrategyFactory."""

    def test_create_llm_interaction_strategy_creation_mode(self):
        """Test creating LLM interaction strategy for CREATION mode."""
        strategy = OrionStrategyFactory.create_llm_interaction_strategy(
            WeavingMode.CREATION
        )

        assert isinstance(strategy, OrionCreationLLMInteractionStrategy)
        assert isinstance(strategy, BaseOrionLLMInteractionStrategy)
        assert strategy.name == "orion_llm_interaction_creation"

    def test_create_llm_interaction_strategy_editing_mode(self):
        """Test creating LLM interaction strategy for EDITING mode."""
        strategy = OrionStrategyFactory.create_llm_interaction_strategy(
            WeavingMode.EDITING
        )

        assert isinstance(strategy, OrionEditingLLMInteractionStrategy)
        assert isinstance(strategy, BaseOrionLLMInteractionStrategy)
        assert strategy.name == "orion_llm_interaction_editing"

    def test_create_action_execution_strategy_creation_mode(self):
        """Test creating action execution strategy for CREATION mode."""
        strategy = OrionStrategyFactory.create_action_execution_strategy(
            WeavingMode.CREATION
        )

        assert isinstance(strategy, OrionCreationActionExecutionStrategy)
        assert isinstance(strategy, BaseOrionActionExecutionStrategy)
        assert strategy.name == "orion_action_execution_creation"

    def test_create_action_execution_strategy_editing_mode(self):
        """Test creating action execution strategy for EDITING mode."""
        strategy = OrionStrategyFactory.create_action_execution_strategy(
            WeavingMode.EDITING
        )

        assert isinstance(strategy, OrionEditingActionExecutionStrategy)
        assert isinstance(strategy, BaseOrionActionExecutionStrategy)
        assert strategy.name == "orion_action_execution_editing"

    def test_unsupported_weaving_mode_llm_interaction(self):
        """Test that unsupported weaving mode raises ValueError for LLM interaction."""
        with pytest.raises(ValueError, match="Unsupported weaving mode"):
            OrionStrategyFactory.create_llm_interaction_strategy("INVALID_MODE")

    def test_unsupported_weaving_mode_action_execution(self):
        """Test that unsupported weaving mode raises ValueError for action execution."""
        with pytest.raises(ValueError, match="Unsupported weaving mode"):
            OrionStrategyFactory.create_action_execution_strategy(
                "INVALID_MODE"
            )

    def test_get_all_strategies_creation_mode(self):
        """Test getting all strategies for CREATION mode."""
        strategies = OrionStrategyFactory.create_all_strategies(
            WeavingMode.CREATION
        )

        assert ProcessingPhase.LLM_INTERACTION in strategies
        assert ProcessingPhase.ACTION_EXECUTION in strategies
        assert isinstance(
            strategies[ProcessingPhase.LLM_INTERACTION],
            OrionCreationLLMInteractionStrategy,
        )
        assert isinstance(
            strategies[ProcessingPhase.ACTION_EXECUTION],
            OrionCreationActionExecutionStrategy,
        )

    def test_get_all_strategies_editing_mode(self):
        """Test getting all strategies for EDITING mode."""
        strategies = OrionStrategyFactory.create_all_strategies(
            WeavingMode.EDITING
        )

        assert ProcessingPhase.LLM_INTERACTION in strategies
        assert ProcessingPhase.ACTION_EXECUTION in strategies
        assert isinstance(
            strategies[ProcessingPhase.LLM_INTERACTION],
            OrionEditingLLMInteractionStrategy,
        )
        assert isinstance(
            strategies[ProcessingPhase.ACTION_EXECUTION],
            OrionEditingActionExecutionStrategy,
        )


class TestOrionPrompterFactory:
    """Test cases for OrionPrompterFactory."""

    def test_create_prompter_creation_mode(self):
        """Test creating prompter for CREATION mode."""
        main_prompt = "Test main prompt"
        example_prompt = "Test example prompt"

        prompter = OrionPrompterFactory.create_prompter(
            WeavingMode.CREATION,
            main_prompt,
            example_prompt,
            example_prompt,
            example_prompt,
        )

        assert isinstance(prompter, OrionCreationPrompter)
        assert isinstance(prompter, BaseOrionPrompter)

    def test_create_prompter_editing_mode(self):
        """Test creating prompter for EDITING mode."""
        main_prompt = "Test main prompt"
        example_prompt = "Test example prompt"

        prompter = OrionPrompterFactory.create_prompter(
            WeavingMode.EDITING,
            main_prompt,
            example_prompt,
            example_prompt,
            example_prompt,
        )

        assert isinstance(prompter, OrionEditingPrompter)
        assert isinstance(prompter, BaseOrionPrompter)

    def test_unsupported_weaving_mode_prompter(self):
        """Test that unsupported weaving mode raises ValueError for prompter."""
        with pytest.raises(ValueError, match="Unsupported weaving mode"):
            OrionPrompterFactory.create_prompter(
                "INVALID_MODE", "prompt", "example", "example", "example"
            )


class TestBaseOrionStrategy:
    """Test cases for base orion strategies."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock OrionAgent."""
        agent = Mock()
        agent.message_constructor = Mock(return_value={"test": "message"})
        agent.get_response = Mock(return_value=("response_text", 0.1))
        agent.response_to_dict = Mock(
            return_value={"status": "CONTINUE", "thought": "test"}
        )
        agent.print_response = Mock()
        return agent

    @pytest.fixture
    def mock_context(self):
        """Create a mock ProcessingContext."""
        context = Mock(spec=ProcessingContext)
        context.get_local = Mock()
        context.get_global = Mock()
        context.get = Mock()
        return context

    def test_base_llm_interaction_strategy_inheritance(self):
        """Test that base LLM interaction strategy has expected methods."""
        # Test through concrete implementation
        strategy = OrionCreationLLMInteractionStrategy()
        assert isinstance(strategy, BaseOrionLLMInteractionStrategy)
        assert hasattr(strategy, "execute")
        assert hasattr(strategy, "_build_comprehensive_prompt")
        assert hasattr(strategy, "_get_llm_response_with_retry")

    def test_base_action_execution_strategy_inheritance(self):
        """Test that base action execution strategy has expected methods."""
        # Test through concrete implementation
        strategy = OrionCreationActionExecutionStrategy()
        assert isinstance(strategy, BaseOrionActionExecutionStrategy)
        assert hasattr(strategy, "execute")


class TestStrategyBehaviorDifferentiation:
    """Test cases to verify that different weaving modes have different behaviors."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock OrionAgent."""
        agent = Mock()
        agent.message_constructor = Mock(return_value={"test": "message"})
        agent.get_response = Mock(return_value=("response_text", 0.1))
        agent.response_to_dict = Mock(
            return_value={"status": "CONTINUE", "thought": "test"}
        )
        agent.print_response = Mock()
        return agent

    @pytest.fixture
    def mock_context(self):
        """Create a mock ProcessingContext."""
        context = Mock(spec=ProcessingContext)
        context.get_local = Mock(
            side_effect=lambda key, default=None: {
                "session_step": 1,
                "device_info": [],
                "weaving_mode": WeavingMode.CREATION,
            }.get(key, default)
        )
        context.get_global = Mock(
            side_effect=lambda key: {
                "ORION": Mock(),
                "request_logger": Mock(),
            }.get(key)
        )
        context.get = Mock(return_value="test_request")
        return context

    @pytest.mark.asyncio
    @patch("alien.network.agents.processors.strategies.base_orion_strategy.json")
    async def test_creation_vs_editing_llm_strategies_different_behavior(
        self, mock_json, mock_agent, mock_context
    ):
        """Test that creation and editing strategies have different behaviors."""
        mock_json.dumps = Mock(return_value='{"test": "json"}')

        # Create strategies
        creation_strategy = (
            OrionStrategyFactory.create_llm_interaction_strategy(
                WeavingMode.CREATION
            )
        )
        editing_strategy = OrionStrategyFactory.create_llm_interaction_strategy(
            WeavingMode.EDITING
        )

        # Execute both strategies
        creation_result = await creation_strategy.execute(mock_agent, mock_context)
        editing_result = await editing_strategy.execute(mock_agent, mock_context)

        # Both should succeed but may have different internal logic
        assert creation_result.success
        assert editing_result.success

        # Verify they are different strategy instances
        assert type(creation_strategy) != type(editing_strategy)
        assert creation_strategy.name != editing_strategy.name


class TestPrompterBehaviorDifferentiation:
    """Test cases to verify that different prompters have different behaviors."""

    def test_creation_vs_editing_prompters_different_behavior(self):
        """Test that creation and editing prompters have different behaviors."""
        main_prompt = "Test main prompt"
        example_prompt = "Test example prompt"

        # Create prompters
        creation_prompter = OrionPrompterFactory.create_prompter(
            WeavingMode.CREATION,
            main_prompt,
            example_prompt,
            example_prompt,
            example_prompt,
        )
        editing_prompter = OrionPrompterFactory.create_prompter(
            WeavingMode.EDITING,
            main_prompt,
            example_prompt,
            example_prompt,
            example_prompt,
        )

        # Verify they are different prompter instances
        assert type(creation_prompter) != type(editing_prompter)

        # Both should have the same base functionality
        assert hasattr(creation_prompter, "get_prompt_template")
        assert hasattr(editing_prompter, "get_prompt_template")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
