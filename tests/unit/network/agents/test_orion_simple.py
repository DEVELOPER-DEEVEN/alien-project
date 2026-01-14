
"""
Simplified test cases for the refactored Orion Agent factory patterns.

This test suite focuses on verifying the core factory functionality works.
"""

import pytest
from network.agents.schema import WeavingMode
from network.agents.processors.strategies.orion_factory import (
    OrionStrategyFactory,
    OrionPrompterFactory,
)


class TestOrionRefactor:
    """Simplified test cases for orion refactor."""

    def test_strategy_factory_creates_different_strategies(self):
        """Test that factory creates different strategies for different modes."""
        creation_llm = OrionStrategyFactory.create_llm_interaction_strategy(
            WeavingMode.CREATION
        )
        editing_llm = OrionStrategyFactory.create_llm_interaction_strategy(
            WeavingMode.EDITING
        )

        creation_action = OrionStrategyFactory.create_action_execution_strategy(
            WeavingMode.CREATION
        )
        editing_action = OrionStrategyFactory.create_action_execution_strategy(
            WeavingMode.EDITING
        )

        # Different strategy types
        assert type(creation_llm) != type(editing_llm)
        assert type(creation_action) != type(editing_action)

        # Different names
        assert creation_llm.name != editing_llm.name
        assert creation_action.name != editing_action.name

    def test_prompter_factory_creates_different_prompters(self):
        """Test that factory creates different prompters for different modes."""
        main_prompt = "test"
        example_prompt = "example"

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

        # Different prompter types
        assert type(creation_prompter) != type(editing_prompter)

    def test_strategy_factory_handles_invalid_mode(self):
        """Test that factory handles invalid weaving modes properly."""
        with pytest.raises(ValueError, match="Unsupported weaving mode"):
            OrionStrategyFactory.create_llm_interaction_strategy("INVALID")

        with pytest.raises(ValueError, match="Unsupported weaving mode"):
            OrionStrategyFactory.create_action_execution_strategy("INVALID")

    def test_prompter_factory_handles_invalid_mode(self):
        """Test that prompter factory handles invalid weaving modes properly."""
        with pytest.raises(ValueError, match="Unsupported weaving mode"):
            OrionPrompterFactory.create_prompter(
                "INVALID", "test", "test", "test", "test"
            )

    def test_create_all_strategies_works(self):
        """Test that create_all_strategies works for both modes."""
        creation_strategies = OrionStrategyFactory.create_all_strategies(
            WeavingMode.CREATION
        )
        editing_strategies = OrionStrategyFactory.create_all_strategies(
            WeavingMode.EDITING
        )

        # Both should have the required processing phases
        from alien.agents.processors.core.processor_framework import ProcessingPhase

        assert "llm_interaction" in creation_strategies
        assert "action_execution" in creation_strategies
        assert "llm_interaction" in editing_strategies
        assert "action_execution" in editing_strategies

        # Different strategy instances
        assert type(creation_strategies["llm_interaction"]) != type(
            editing_strategies["llm_interaction"]
        )
        assert type(creation_strategies["action_execution"]) != type(
            editing_strategies["action_execution"]
        )


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
