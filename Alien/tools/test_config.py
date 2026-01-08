#!/usr/bin/env python
# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
Test script for configuration loading with backward compatibility.

This script demonstrates the configuration loading behavior in different scenarios.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_Alien_config():
    """Test Alien configuration loading."""
    print("\n" + "=" * 70)
    print("Testing Alien Configuration Loading")
    print("=" * 70)

    try:
        from config.config_loader import get_Alien_config

        # Load configuration
        config = get_Alien_config()

        # Test typed access
        print("\n✓ Typed access (recommended):")
        print(f"  config.system.max_step = {config.system.max_step}")
        print(f"  config.system.timeout = {config.system.timeout}")
        print(f"  config.app_agent.api_type = {config.app_agent.api_type}")
        print(f"  config.app_agent.api_model = {config.app_agent.api_model}")

        # Test dict-style access (backward compatible)
        print("\n✓ Dict-style access (backward compatible):")
        print(f"  config['MAX_STEP'] = {config.get('MAX_STEP', 'N/A')}")
        print(f"  config['TIMEOUT'] = {config.get('TIMEOUT', 'N/A')}")

        # Test agent access
        if "HOST_AGENT" in config:
            host_agent = config["HOST_AGENT"]
            print(
                f"  config['HOST_AGENT']['API_TYPE'] = {host_agent.get('API_TYPE', 'N/A')}"
            )

        # Test dynamic access
        print("\n✓ Dynamic access:")
        print(f"  config keys count = {len(list(config.keys()))}")
        print(f"  Sample keys = {list(config.keys())[:5]}...")

        print("\n✅ Alien configuration loaded successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error loading Alien configuration: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_cluster_config():
    """Test cluster configuration loading."""
    print("\n" + "=" * 70)
    print("Testing cluster Configuration Loading")
    print("=" * 70)

    try:
        from config.config_loader import get_cluster_config

        # Load configuration
        config = get_cluster_config()

        # Test typed access
        print("\n✓ Typed access (recommended):")
        print(
            f"  config.network_agent.api_type = {config.network_agent.api_type}"
        )
        print(
            f"  config.network_agent.api_model = {config.network_agent.api_model}"
        )

        # Test dict-style access
        print("\n✓ Dict-style access (backward compatible):")
        if "network_AGENT" in config:
            agent = config["network_AGENT"]
            print(
                f"  config['network_AGENT']['API_TYPE'] = {agent.get('API_TYPE', 'N/A')}"
            )

        # Test dynamic access
        print("\n✓ Dynamic access:")
        print(f"  config keys count = {len(list(config.keys()))}")
        print(f"  Sample keys = {list(config.keys())[:5]}...")

        print("\n✅ cluster configuration loaded successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error loading cluster configuration: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_path_detection():
    """Test configuration path detection."""
    print("\n" + "=" * 70)
    print("Testing Path Detection")
    print("=" * 70)

    # Check Alien paths
    Alien_new = Path("config/Alien")
    Alien_legacy = Path("Alien/config")

    print("\nAlien Configuration Paths:")
    print(
        f"  New path (config/Alien/):     {'✓ EXISTS' if Alien_new.exists() else '✗ NOT FOUND'}"
    )
    if Alien_new.exists():
        yaml_files = list(Alien_new.glob("*.yaml"))
        print(f"    Files: {len(yaml_files)}")
        for f in yaml_files[:3]:
            print(f"      - {f.name}")

    print(
        f"  Legacy path (Alien/config/):  {'✓ EXISTS' if Alien_legacy.exists() else '✗ NOT FOUND'}"
    )
    if Alien_legacy.exists():
        yaml_files = list(Alien_legacy.glob("*.yaml"))
        print(f"    Files: {len(yaml_files)}")
        for f in yaml_files[:3]:
            print(f"      - {f.name}")

    # Check cluster paths
    cluster_new = Path("config/cluster")

    print("\ncluster Configuration Paths:")
    print(
        f"  New path (config/cluster/):  {'✓ EXISTS' if cluster_new.exists() else '✗ NOT FOUND'}"
    )
    if cluster_new.exists():
        yaml_files = list(cluster_new.glob("*.yaml"))
        print(f"    Files: {len(yaml_files)}")
        for f in yaml_files[:3]:
            print(f"      - {f.name}")


def main():
    """Main test function."""
    print("\n" + "=" * 70)
    print("Alien³ Configuration System Test")
    print("=" * 70)

    # Test path detection
    test_path_detection()

    # Test Alien config
    Alien_success = test_Alien_config()

    # Test cluster config
    cluster_success = test_cluster_config()

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"  Alien Configuration:    {'✅ PASS' if Alien_success else '❌ FAIL'}")
    print(f"  cluster Configuration: {'✅ PASS' if cluster_success else '❌ FAIL'}")
    print("=" * 70)

    return Alien_success and cluster_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
