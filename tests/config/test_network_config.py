"""
Test Network Configuration Loading and Access

Tests the new Network configuration system with structured attribute access.
"""

import pytest
from config.config_loader import get_network_config


def test_network_config_basic_loading():
    """Test that Network config loads successfully"""
    config = get_network_config()
    assert config is not None
    print("[OK] Network config loaded successfully")


def test_network_agent_config_access():
    """Test accessing agent configuration through structured attributes"""
    config = get_network_config()

    # Test agent.ORION_AGENT access
    assert hasattr(config, "agent")
    assert hasattr(config.agent, "ORION_AGENT")

    orion_agent = config.agent.ORION_AGENT

    # Test typed fields
    assert hasattr(orion_agent, "API_MODEL")
    assert hasattr(orion_agent, "API_TYPE")
    assert hasattr(orion_agent, "API_BASE")

    print(f"[OK] Agent API Model: {orion_agent.API_MODEL}")
    print(f"[OK] Agent API Type: {orion_agent.API_TYPE}")
    print(f"[OK] Agent API Base: {orion_agent.API_BASE}")

    # Test prompt configurations
    assert hasattr(orion_agent, "ORION_CREATION_PROMPT")
    assert hasattr(orion_agent, "ORION_EDITING_PROMPT")
    assert hasattr(orion_agent, "ORION_CREATION_EXAMPLE_PROMPT")
    assert hasattr(orion_agent, "ORION_EDITING_EXAMPLE_PROMPT")

    print(f"[OK] Creation Prompt: {orion_agent.ORION_CREATION_PROMPT}")
    print(f"[OK] Editing Prompt: {orion_agent.ORION_EDITING_PROMPT}")


def test_network_orion_config_access():
    """Test accessing orion runtime configuration"""
    config = get_network_config()

    # Test orion attribute access
    assert hasattr(config, "orion")

    # Test typed fields
    assert hasattr(config.orion, "ORION_ID")
    assert hasattr(config.orion, "HEARTBEAT_INTERVAL")
    assert hasattr(config.orion, "RECONNECT_DELAY")
    assert hasattr(config.orion, "MAX_CONCURRENT_TASKS")
    assert hasattr(config.orion, "MAX_STEP")
    assert hasattr(config.orion, "DEVICE_INFO")

    print(f"[OK] Orion ID: {config.orion.ORION_ID}")
    print(f"[OK] Heartbeat Interval: {config.orion.HEARTBEAT_INTERVAL}")
    print(f"[OK] Reconnect Delay: {config.orion.RECONNECT_DELAY}")
    print(f"[OK] Max Concurrent Tasks: {config.orion.MAX_CONCURRENT_TASKS}")
    print(f"[OK] Max Step: {config.orion.MAX_STEP}")
    print(f"[OK] Device Info: {config.orion.DEVICE_INFO}")


def test_network_lowercase_attribute_access():
    """Test lowercase attribute access (snake_case)"""
    config = get_network_config()

    # Test orion config lowercase access
    assert (
        config.orion.orion_id == config.orion.ORION_ID
    )
    assert (
        config.orion.heartbeat_interval
        == config.orion.HEARTBEAT_INTERVAL
    )
    assert config.orion.reconnect_delay == config.orion.RECONNECT_DELAY
    assert (
        config.orion.max_concurrent_tasks
        == config.orion.MAX_CONCURRENT_TASKS
    )
    assert config.orion.max_step == config.orion.MAX_STEP
    assert config.orion.device_info == config.orion.DEVICE_INFO

    print("[OK] Lowercase attribute access works correctly")


def test_network_backward_compatible_dict_access():
    """Test backward compatible dictionary-style access"""
    config = get_network_config()

    # Test dict-style access
    assert "ORION_AGENT" in config
    assert config["ORION_AGENT"] is not None

    assert "ORION_ID" in config
    assert config["ORION_ID"] == config.orion.ORION_ID

    assert "MAX_STEP" in config
    assert config["MAX_STEP"] == config.orion.MAX_STEP

    assert "DEVICE_INFO" in config
    assert config["DEVICE_INFO"] == config.orion.DEVICE_INFO

    print("[OK] Backward compatible dict access works")


def test_network_config_usage_in_code():
    """Test typical usage patterns in actual code"""
    config = get_network_config()

    # Pattern 1: Access device info path (like in network_client.py)
    device_info_path = config.orion.DEVICE_INFO
    assert device_info_path is not None
    assert isinstance(device_info_path, str)
    print(f"[OK] Device info path retrieval: {device_info_path}")

    # Pattern 2: Access MAX_STEP (like in network_session.py)
    max_step = config.orion.MAX_STEP
    assert max_step is not None
    assert isinstance(max_step, int)
    print(f"[OK] Max step retrieval: {max_step}")

    # Pattern 3: Access agent config (like in base_orion_prompter.py)
    agent_config = config.agent.ORION_AGENT
    creation_prompt = agent_config.ORION_CREATION_PROMPT
    editing_prompt = agent_config.ORION_EDITING_PROMPT
    creation_example = agent_config.ORION_CREATION_EXAMPLE_PROMPT
    editing_example = agent_config.ORION_EDITING_EXAMPLE_PROMPT

    assert creation_prompt is not None
    assert editing_prompt is not None
    assert creation_example is not None
    assert editing_example is not None

    print(f"[OK] Prompt templates retrieval successful")


def test_network_config_types():
    """Test that configuration values have correct types"""
    config = get_network_config()

    # Orion runtime config types
    assert isinstance(config.orion.ORION_ID, str)
    assert isinstance(config.orion.HEARTBEAT_INTERVAL, (int, float))
    assert isinstance(config.orion.RECONNECT_DELAY, (int, float))
    assert isinstance(config.orion.MAX_CONCURRENT_TASKS, int)
    assert isinstance(config.orion.MAX_STEP, int)
    assert isinstance(config.orion.DEVICE_INFO, str)

    # Agent config types
    agent = config.agent.ORION_AGENT
    assert isinstance(agent.API_MODEL, str)
    assert isinstance(agent.API_TYPE, str)
    assert isinstance(agent.VISUAL_MODE, bool)

    print("[OK] All config values have correct types")


def test_network_config_caching():
    """Test that config is properly cached"""
    config1 = get_network_config()
    config2 = get_network_config()

    # Should return the same instance
    assert config1 is config2
    print("[OK] Config caching works correctly")


def test_network_config_reload():
    """Test that config can be reloaded"""
    config1 = get_network_config()
    config2 = get_network_config(reload=True)

    # Should return different instances when reloaded
    assert config1 is not config2

    # But values should be the same
    assert config1.orion.MAX_STEP == config2.orion.MAX_STEP
    assert (
        config1.agent.ORION_AGENT.API_MODEL
        == config2.agent.ORION_AGENT.API_MODEL
    )

    print("[OK] Config reload works correctly")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Testing Network Configuration System")
    print("=" * 70 + "\n")

    try:
        test_network_config_basic_loading()
        print()

        test_network_agent_config_access()
        print()

        test_network_orion_config_access()
        print()

        test_network_lowercase_attribute_access()
        print()

        test_network_backward_compatible_dict_access()
        print()

        test_network_config_usage_in_code()
        print()

        test_network_config_types()
        print()

        test_network_config_caching()
        print()

        test_network_config_reload()
        print()

        print("=" * 70)
        print("[OK] All Network Configuration Tests Passed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback

        traceback.print_exc()
