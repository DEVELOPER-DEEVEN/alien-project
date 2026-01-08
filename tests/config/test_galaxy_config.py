"""
Test cluster Configuration Loading and Access

Tests the new cluster configuration system with structured attribute access.
"""

import pytest
from config.config_loader import get_cluster_config


def test_cluster_config_basic_loading():
    """Test that cluster config loads successfully"""
    config = get_cluster_config()
    assert config is not None
    print("✅ cluster config loaded successfully")


def test_cluster_agent_config_access():
    """Test accessing agent configuration through structured attributes"""
    config = get_cluster_config()

    # Test agent.network_AGENT access
    assert hasattr(config, "agent")
    assert hasattr(config.agent, "network_AGENT")

    network_agent = config.agent.network_AGENT

    # Test typed fields
    assert hasattr(network_agent, "API_MODEL")
    assert hasattr(network_agent, "API_TYPE")
    assert hasattr(network_agent, "API_BASE")

    print(f"✅ Agent API Model: {network_agent.API_MODEL}")
    print(f"✅ Agent API Type: {network_agent.API_TYPE}")
    print(f"✅ Agent API Base: {network_agent.API_BASE}")

    # Test prompt configurations
    assert hasattr(network_agent, "network_CREATION_PROMPT")
    assert hasattr(network_agent, "network_EDITING_PROMPT")
    assert hasattr(network_agent, "network_CREATION_EXAMPLE_PROMPT")
    assert hasattr(network_agent, "network_EDITING_EXAMPLE_PROMPT")

    print(f"✅ Creation Prompt: {network_agent.network_CREATION_PROMPT}")
    print(f"✅ Editing Prompt: {network_agent.network_EDITING_PROMPT}")


def test_cluster_network_config_access():
    """Test accessing network runtime configuration"""
    config = get_cluster_config()

    # Test network attribute access
    assert hasattr(config, "network")

    # Test typed fields
    assert hasattr(config.network, "network_ID")
    assert hasattr(config.network, "HEARTBEAT_INTERVAL")
    assert hasattr(config.network, "RECONNECT_DELAY")
    assert hasattr(config.network, "MAX_CONCURRENT_TASKS")
    assert hasattr(config.network, "MAX_STEP")
    assert hasattr(config.network, "DEVICE_INFO")

    print(f"✅ network ID: {config.network.network_ID}")
    print(f"✅ Heartbeat Interval: {config.network.HEARTBEAT_INTERVAL}")
    print(f"✅ Reconnect Delay: {config.network.RECONNECT_DELAY}")
    print(f"✅ Max Concurrent Tasks: {config.network.MAX_CONCURRENT_TASKS}")
    print(f"✅ Max Step: {config.network.MAX_STEP}")
    print(f"✅ Device Info: {config.network.DEVICE_INFO}")


def test_cluster_lowercase_attribute_access():
    """Test lowercase attribute access (snake_case)"""
    config = get_cluster_config()

    # Test network config lowercase access
    assert (
        config.network.network_id == config.network.network_ID
    )
    assert (
        config.network.heartbeat_interval
        == config.network.HEARTBEAT_INTERVAL
    )
    assert config.network.reconnect_delay == config.network.RECONNECT_DELAY
    assert (
        config.network.max_concurrent_tasks
        == config.network.MAX_CONCURRENT_TASKS
    )
    assert config.network.max_step == config.network.MAX_STEP
    assert config.network.device_info == config.network.DEVICE_INFO

    print("✅ Lowercase attribute access works correctly")


def test_cluster_backward_compatible_dict_access():
    """Test backward compatible dictionary-style access"""
    config = get_cluster_config()

    # Test dict-style access
    assert "network_AGENT" in config
    assert config["network_AGENT"] is not None

    assert "network_ID" in config
    assert config["network_ID"] == config.network.network_ID

    assert "MAX_STEP" in config
    assert config["MAX_STEP"] == config.network.MAX_STEP

    assert "DEVICE_INFO" in config
    assert config["DEVICE_INFO"] == config.network.DEVICE_INFO

    print("✅ Backward compatible dict access works")


def test_cluster_config_usage_in_code():
    """Test typical usage patterns in actual code"""
    config = get_cluster_config()

    # Pattern 1: Access device info path (like in cluster_client.py)
    device_info_path = config.network.DEVICE_INFO
    assert device_info_path is not None
    assert isinstance(device_info_path, str)
    print(f"✅ Device info path retrieval: {device_info_path}")

    # Pattern 2: Access MAX_STEP (like in cluster_session.py)
    max_step = config.network.MAX_STEP
    assert max_step is not None
    assert isinstance(max_step, int)
    print(f"✅ Max step retrieval: {max_step}")

    # Pattern 3: Access agent config (like in base_network_prompter.py)
    agent_config = config.agent.network_AGENT
    creation_prompt = agent_config.network_CREATION_PROMPT
    editing_prompt = agent_config.network_EDITING_PROMPT
    creation_example = agent_config.network_CREATION_EXAMPLE_PROMPT
    editing_example = agent_config.network_EDITING_EXAMPLE_PROMPT

    assert creation_prompt is not None
    assert editing_prompt is not None
    assert creation_example is not None
    assert editing_example is not None

    print(f"✅ Prompt templates retrieval successful")


def test_cluster_config_types():
    """Test that configuration values have correct types"""
    config = get_cluster_config()

    # network runtime config types
    assert isinstance(config.network.network_ID, str)
    assert isinstance(config.network.HEARTBEAT_INTERVAL, (int, float))
    assert isinstance(config.network.RECONNECT_DELAY, (int, float))
    assert isinstance(config.network.MAX_CONCURRENT_TASKS, int)
    assert isinstance(config.network.MAX_STEP, int)
    assert isinstance(config.network.DEVICE_INFO, str)

    # Agent config types
    agent = config.agent.network_AGENT
    assert isinstance(agent.API_MODEL, str)
    assert isinstance(agent.API_TYPE, str)
    assert isinstance(agent.VISUAL_MODE, bool)

    print("✅ All config values have correct types")


def test_cluster_config_caching():
    """Test that config is properly cached"""
    config1 = get_cluster_config()
    config2 = get_cluster_config()

    # Should return the same instance
    assert config1 is config2
    print("✅ Config caching works correctly")


def test_cluster_config_reload():
    """Test that config can be reloaded"""
    config1 = get_cluster_config()
    config2 = get_cluster_config(reload=True)

    # Should return different instances when reloaded
    assert config1 is not config2

    # But values should be the same
    assert config1.network.MAX_STEP == config2.network.MAX_STEP
    assert (
        config1.agent.network_AGENT.API_MODEL
        == config2.agent.network_AGENT.API_MODEL
    )

    print("✅ Config reload works correctly")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Testing cluster Configuration System")
    print("=" * 70 + "\n")

    try:
        test_cluster_config_basic_loading()
        print()

        test_cluster_agent_config_access()
        print()

        test_cluster_network_config_access()
        print()

        test_cluster_lowercase_attribute_access()
        print()

        test_cluster_backward_compatible_dict_access()
        print()

        test_cluster_config_usage_in_code()
        print()

        test_cluster_config_types()
        print()

        test_cluster_config_caching()
        print()

        test_cluster_config_reload()
        print()

        print("=" * 70)
        print("✅ All cluster Configuration Tests Passed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
