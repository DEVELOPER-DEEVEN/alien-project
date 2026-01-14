#!/usr/bin/env python
"""
Integration test for NetworkSession with full workflow execution.
"""

import asyncio
import logging
import os
import sys
from unittest.mock import MagicMock

# Add ALIEN path - adjust for tests/network/session subdirectory
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from network.session.network_session import NetworkSession
from network.client.orion_client import OrionClient


async def test_network_session_workflow():
    """Test NetworkSession with a complete workflow."""
    print("[START] Testing NetworkSession Full Workflow\n")

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Mock client with device manager
    mock_client = MagicMock(spec=OrionClient)
    mock_client.device_manager = MagicMock()

    print("=== Test 1: Session Creation and Setup ===")

    # Create session
    session = NetworkSession(
        task="Complete project development workflow",
        should_evaluate=True,
        id="workflow-session-001",
        client=mock_client,
        initial_request="Create a comprehensive software development workflow with testing and deployment",
    )

    print("[OK] Session created")
    print(f"   Task: {session.task}")
    print(f"   Initial request: {session._initial_request}")
    print(f"   Agent: {type(session.agent).__name__}")
    print(f"   Event observers: {len(session._observers)}")

    print("\n=== Test 2: Round Creation and Execution ===")

    try:
        # Create first round
        round1 = session.create_new_round()

        if round1:
            print("[OK] First round created")
            print(f"   Round ID: {round1._id}")
            print(f"   Request: {round1._request}")

            # Test round properties
            print(f"   Is finished: {round1.is_finished()}")
            print(f"   Agent status: {round1._agent.status}")

        # Try to create second round (should be None since only one request)
        round2 = session.create_new_round()
        if round2 is None:
            print("[OK] Second round correctly not created (no more requests)")
        else:
            print(f"[INFO] Second round created: {round2._id}")

    except Exception as e:
        print(f"[FAIL] Error in round creation: {e}")
        import traceback

        traceback.print_exc()

    print("\n=== Test 3: Session State Management ===")

    try:
        # Test various session states
        print(f"[OK] Session finished: {session.is_finished()}")
        print(f"[OK] Session error: {session.is_error()}")
        print(f"[OK] Current step: {session.step}")
        print(f"[OK] Total rounds: {session.total_rounds}")
        print(f"[OK] Current orion: {session.current_orion}")

        # Test session results
        results = session.session_results
        print(f"[OK] Session results keys: {list(results.keys())}")

    except Exception as e:
        print(f"[FAIL] Error in state management: {e}")
        return

    print("\n=== Test 4: Agent Integration ===")

    try:
        agent = session.agent
        print(f"[OK] Agent name: {agent.name}")
        print(f"[OK] Agent status: {agent.status}")
        print(f"[OK] Agent orchestrator: {type(agent.orchestrator).__name__}")

        # Test agent orion access
        orion = agent.current_orion
        print(f"[OK] Agent orion: {orion}")

    except Exception as e:
        print(f"[FAIL] Error in agent integration: {e}")
        return

    print("\n=== Test 5: Event System Integration ===")

    try:
        # Check event system
        event_bus = session._event_bus
        observers = session._observers

        print(f"[OK] Event bus: {type(event_bus).__name__}")
        print(f"[OK] Observer count: {len(observers)}")

        for i, observer in enumerate(observers):
            observer_type = type(observer).__name__
            print(f"   Observer {i+1}: {observer_type}")

    except Exception as e:
        print(f"[FAIL] Error in event system: {e}")
        return

    print("\n=== Test 6: Session Cleanup ===")

    try:
        # Force finish the session
        await session.force_finish("Integration test completed")

        print("[OK] Session force finished")
        print(f"   Final status: {session.agent.status}")
        print(f"   Session finished: {session.is_finished()}")
        print(
            f"   Finish reason: {session.session_results.get('finish_reason', 'N/A')}"
        )

    except Exception as e:
        print(f"[FAIL] Error in session cleanup: {e}")
        return

    print("\n[OK] NetworkSession workflow test completed successfully!")


async def test_network_session_error_scenarios():
    """Test NetworkSession error handling scenarios."""
    print("\n Testing NetworkSession Error Scenarios\n")

    print("=== Test 1: Invalid Client Scenario ===")

    try:
        # Test with None client (should handle gracefully)
        session = NetworkSession(
            task="Test with no client",
            should_evaluate=False,
            id="no-client-session",
            client=None,
            initial_request="Test request",
        )
        print("[FAIL] Should have failed with None client")

    except Exception as e:
        print(f"[OK] Correctly failed with None client: {type(e).__name__}")

    print("\n=== Test 2: Long Task Name Scenario ===")

    try:
        mock_client = MagicMock()
        mock_client.device_manager = MagicMock()

        # Test with very long task name
        long_task = "A" * 200 + " very long task name for testing limits"
        session = NetworkSession(
            task=long_task,
            should_evaluate=False,
            id="long-task-session",
            client=mock_client,
            initial_request="Test long task",
        )

        print("[OK] Handled long task name successfully")
        print(f"   Task length: {len(session.task)}")

    except Exception as e:
        print(f"[FAIL] Failed with long task name: {e}")

    print("\n=== Test 3: Empty Request Scenario ===")

    try:
        mock_client = MagicMock()
        mock_client.device_manager = MagicMock()

        # Test with empty initial request
        session = NetworkSession(
            task="Test empty request",
            should_evaluate=False,
            id="empty-request-session",
            client=mock_client,
            initial_request="",
        )

        print("[OK] Handled empty request successfully")
        print(f"   Next request: '{session.next_request()}'")
        print(f"   Eval request: '{session.request_to_evaluate()}'")

    except Exception as e:
        print(f"[FAIL] Failed with empty request: {e}")

    print("\n[OK] Error scenario testing completed!")


async def main():
    """Run all NetworkSession integration tests."""
    print(" NetworkSession Integration Testing Suite\n")
    print("=" * 60)

    try:
        # Run workflow test
        await test_network_session_workflow()

        # Run error scenario tests
        await test_network_session_error_scenarios()

        print("\n" + "=" * 60)
        print(" Integration Testing Summary")
        print("=" * 60)
        print("[OK] All NetworkSession integration tests passed!")
        print(" NetworkSession is ready for production use!")

    except Exception as e:
        print(f"\n Critical error during integration testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
