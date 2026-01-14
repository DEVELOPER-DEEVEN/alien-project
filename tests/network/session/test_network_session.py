#!/usr/bin/env python
"""
Comprehensive test for NetworkSession functionality.
"""

import asyncio
import logging
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Add ALIEN path - adjust for tests/network/session subdirectory
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from network.session.network_session import NetworkSession
from network.client.orion_client import OrionClient
from network.orion import TaskOrion


async def test_network_session_basic_functionality():
    """Test basic NetworkSession functionality."""
    print(" Testing NetworkSession Basic Functionality\n")

    # Mock client with device manager
    mock_client = MagicMock(spec=OrionClient)
    mock_client.device_manager = MagicMock()

    print("=== Test 1: NetworkSession Initialization ===")

    try:
        # Create NetworkSession
        session = NetworkSession(
            task="Test task for network session",
            should_evaluate=True,
            id="test-session-001",
            client=mock_client,
            initial_request="Create a simple task workflow",
        )

        print("[OK] NetworkSession created successfully")
        print(f"   Task: {session.task}")
        print(f"   ID: {session._id}")
        print(f"   Agent: {type(session.agent).__name__}")
        print(f"   Orchestrator: {type(session.orchestrator).__name__}")
        print(f"   Observers count: {len(session._observers)}")

    except Exception as e:
        print(f"[FAIL] Failed to create NetworkSession: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n=== Test 2: Session Properties ===")

    try:
        # Test properties
        print(f"[OK] Current orion: {session.current_orion}")
        print(f"[OK] Session finished: {session.is_finished()}")
        print(f"[OK] Session error: {session.is_error()}")
        print(f"[OK] Next request: '{session.next_request()}'")
        print(f"[OK] Request to evaluate: '{session.request_to_evaluate()}'")

    except Exception as e:
        print(f"[FAIL] Error testing properties: {e}")
        return

    print("\n=== Test 3: Round Creation ===")

    try:
        # Create a new round
        round_obj = session.create_new_round()

        if round_obj:
            print("[OK] Round created successfully")
            print(f"   Round ID: {round_obj._id}")
            print(f"   Round request: {round_obj._request}")
            print(f"   Round type: {type(round_obj).__name__}")
        else:
            print("[INFO] No round created (expected if no more requests)")

    except Exception as e:
        print(f"[FAIL] Error creating round: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n=== Test 4: Event System Integration ===")

    try:
        # Test event bus and observers
        event_bus = session._event_bus
        observers = session._observers

        print(f"[OK] Event bus available: {event_bus is not None}")
        print(f"[OK] Observers registered: {len(observers)}")

        for i, observer in enumerate(observers):
            print(f"   Observer {i+1}: {type(observer).__name__}")

    except Exception as e:
        print(f"[FAIL] Error testing event system: {e}")
        return

    print("\n=== Test 5: Session Control ===")

    try:
        # Test force finish
        await session.force_finish("Test termination")

        print("[OK] Force finish works")
        print(f"   Session finished: {session.is_finished()}")
        print(f"   Agent status: {session.agent.status}")
        print(f"   Session results: {list(session.session_results.keys())}")

    except Exception as e:
        print(f"[FAIL] Error testing session control: {e}")
        return

    print("\n[OK] All NetworkSession basic functionality tests completed!")


async def test_network_session_mock_execution():
    """Test NetworkSession with mock execution."""
    print("\n Testing NetworkSession Mock Execution\n")

    # Mock client
    mock_client = MagicMock(spec=OrionClient)
    mock_client.device_manager = MagicMock()

    print("=== Mock Execution Test ===")

    try:
        # Create session with MockOrionAgent
        session = NetworkSession(
            task="Mock task execution test",
            should_evaluate=False,
            id="mock-session-001",
            client=mock_client,
            initial_request="Execute a mock task workflow",
        )

        print("[OK] Mock session created")

        # Check if agent is properly configured
        agent = session.agent
        print(f"   Agent type: {type(agent).__name__}")
        print(f"   Agent status: {agent.status}")

        # Test orion access
        orion = session.current_orion
        print(f"   Current orion: {orion}")

        # Test context
        context = session._context
        print(f"   Context available: {context is not None}")

    except Exception as e:
        print(f"[FAIL] Error in mock execution test: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n[OK] Mock execution test completed!")


async def test_network_session_issues():
    """Test for potential issues in NetworkSession."""
    print("\n Testing for Potential Issues in NetworkSession\n")

    issues_found = []

    print("=== Checking for Common Issues ===")

    # Test 1: Missing imports
    try:
        from network.session.network_session import NetworkSession, NetworkRound
        from network.agents.orion_agent import OrionAgent
        from network.orion import TaskOrionOrchestrator

        print("[OK] All imports available")
    except ImportError as e:
        issues_found.append(f"Import error: {e}")
        print(f"[FAIL] Import error: {e}")

    # Test 2: Abstract method issues
    try:
        mock_client = MagicMock()
        mock_client.device_manager = MagicMock()

        session = NetworkSession(
            task="Test",
            should_evaluate=False,
            id="test",
            client=mock_client,
            initial_request="Test",
        )

        # Try to access agent
        agent = session.agent
        print(f"[OK] Agent accessible: {type(agent).__name__}")

    except TypeError as e:
        if "abstract" in str(e):
            issues_found.append(f"Abstract method issue: {e}")
            print(f"[FAIL] Abstract method issue: {e}")
        else:
            raise
    except Exception as e:
        issues_found.append(f"Initialization error: {e}")
        print(f"[FAIL] Initialization error: {e}")

    # Test 3: Missing attributes or methods
    try:
        mock_client = MagicMock()
        mock_client.device_manager = MagicMock()

        session = NetworkSession(
            task="Test",
            should_evaluate=False,
            id="test",
            client=mock_client,
            initial_request="Test",
        )

        # Check required attributes
        required_attrs = [
            "_agent",
            "_orchestrator",
            "_event_bus",
            "_observers",
            "_context",
            "_session_results",
        ]

        for attr in required_attrs:
            if hasattr(session, attr):
                print(f"[OK] Has attribute: {attr}")
            else:
                issues_found.append(f"Missing attribute: {attr}")
                print(f"[FAIL] Missing attribute: {attr}")

    except Exception as e:
        issues_found.append(f"Attribute check error: {e}")
        print(f"[FAIL] Attribute check error: {e}")

    print(f"\n[STATUS] Issues Summary:")
    if issues_found:
        print(f"[FAIL] Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
    else:
        print("[OK] No critical issues found!")

    return issues_found


async def main():
    """Run all NetworkSession tests."""
    print("[START] NetworkSession Comprehensive Testing\n")

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Basic functionality test
        await test_network_session_basic_functionality()

        # Mock execution test
        await test_network_session_mock_execution()

        # Issues detection test
        issues = await test_network_session_issues()

        print("\n" + "=" * 80)
        print(" NetworkSession Testing Summary")
        print("=" * 80)

        if issues:
            print(f"️  Found {len(issues)} issues that need attention")
            print("\n[CONFIG] Recommendations:")
            for issue in issues:
                print(f"   • Fix: {issue}")
        else:
            print("[OK] NetworkSession appears to be working correctly!")

        print("\n Testing completed!")

    except Exception as e:
        print(f" Critical error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
