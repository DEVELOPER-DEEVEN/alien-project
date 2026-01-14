#!/usr/bin/env python

"""
Test script for configuration loading with backward compatibility.

This script demonstrates the configuration loading behavior in different scenarios.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_alien_config():
    """Test ALIEN configuration loading."""
    print("\n" + "=" * 70)
    print("Testing ALIEN Configuration Loading")
    print("=" * 70)

    try:
        from config.config_loader import get_alien_config

        # Load configuration
        config = get_alien_config()

        # Test typed access
        print("\n Typed access (recommended):")
        print(f"  config.system.max_step = {config.system.max_step}")
        print(f"  config.system.timeout = {config.system.timeout}")
        print(f"  config.app_agent.api_type = {config.app_agent.api_type}")
        print(f"  config.app_agent.api_model = {config.app_agent.api_model}")

        # Test dict-style access (backward compatible)
        print("\n Dict-style access (backward compatible):")
        print(f"  config['MAX_STEP'] = {config.get('MAX_STEP', 'N/A')}")
        print(f"  config['TIMEOUT'] = {config.get('TIMEOUT', 'N/A')}")

        # Test agent access
        if "HOST_AGENT" in config:
            host_agent = config["HOST_AGENT"]
            print(
                f"  config['HOST_AGENT']['API_TYPE'] = {host_agent.get('API_TYPE', 'N/A')}"
            )

        # Test dynamic access
        print("\n Dynamic access:")
        print(f"  config keys count = {len(list(config.keys()))}")
        print(f"  Sample keys = {list(config.keys())[:5]}...")

        print("\n[OK] ALIEN configuration loaded successfully!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error loading ALIEN configuration: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_network_config():
    """Test Network configuration loading."""
    print("\n" + "=" * 70)
    print("Testing Network Configuration Loading")
    print("=" * 70)

    try:
        from config.config_loader import get_network_config

        # Load configuration
        config = get_network_config()

        # Test typed access
        print("\n Typed access (recommended):")
        print(
            f"  config.orion_agent.api_type = {config.orion_agent.api_type}"
        )
        print(
            f"  config.orion_agent.api_model = {config.orion_agent.api_model}"
        )

        # Test dict-style access
        print("\n Dict-style access (backward compatible):")
        if "ORION_AGENT" in config:
            agent = config["ORION_AGENT"]
            print(
                f"  config['ORION_AGENT']['API_TYPE'] = {agent.get('API_TYPE', 'N/A')}"
            )

        # Test dynamic access
        print("\n Dynamic access:")
        print(f"  config keys count = {len(list(config.keys()))}")
        print(f"  Sample keys = {list(config.keys())[:5]}...")

        print("\n[OK] Network configuration loaded successfully!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error loading Network configuration: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_path_detection():
    """Test configuration path detection."""
    print("\n" + "=" * 70)
    print("Testing Path Detection")
    print("=" * 70)

    # Check ALIEN paths
    alien_new = Path("config/alien")
    alien_legacy = Path("alien/config")

    print("\nALIEN Configuration Paths:")
    print(
        f"  New path (config/alien/):     {' EXISTS' if alien_new.exists() else ' NOT FOUND'}"
    )
    if alien_new.exists():
        yaml_files = list(alien_new.glob("*.yaml"))
        print(f"    Files: {len(yaml_files)}")
        for f in yaml_files[:3]:
            print(f"      - {f.name}")

    print(
        f"  Legacy path (alien/config/):  {' EXISTS' if alien_legacy.exists() else ' NOT FOUND'}"
    )
    if alien_legacy.exists():
        yaml_files = list(alien_legacy.glob("*.yaml"))
        print(f"    Files: {len(yaml_files)}")
        for f in yaml_files[:3]:
            print(f"      - {f.name}")

    # Check Network paths
    network_new = Path("config/network")

    print("\nNetwork Configuration Paths:")
    print(
        f"  New path (config/network/):  {' EXISTS' if network_new.exists() else ' NOT FOUND'}"
    )
    if network_new.exists():
        yaml_files = list(network_new.glob("*.yaml"))
        print(f"    Files: {len(yaml_files)}")
        for f in yaml_files[:3]:
            print(f"      - {f.name}")


def main():
    """Main test function."""
    print("\n" + "=" * 70)
    print("ALIEN³ Configuration System Test")
    print("=" * 70)

    # Test path detection
    test_path_detection()

    # Test ALIEN config
    alien_success = test_alien_config()

    # Test Network config
    network_success = test_network_config()

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"  ALIEN Configuration:    {'[OK] PASS' if alien_success else '[FAIL] FAIL'}")
    print(f"  Network Configuration: {'[OK] PASS' if network_success else '[FAIL] FAIL'}")
    print("=" * 70)

    return alien_success and network_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
