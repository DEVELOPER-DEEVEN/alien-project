#!/usr/bin/env python3

"""
Test mock client functionality and visualization for NetworkClient.

This script tests:
1. Mock orion agent integration
2. Visualization display functions
3. Interactive mode with mock data
4. Client display formatting
"""

import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from network.network_client import NetworkClient
from network.visualization.client_display import ClientDisplay
from network.client.orion_client import OrionClient
from network.session.network_session import NetworkSession
from tests.network.mocks import MockOrionAgent, MockTaskOrionOrchestrator
from rich.console import Console


class MockNetworkClientTester:
    """Test class for NetworkClient with mock functionality."""

    def __init__(self):
        """Initialize the mock tester."""
        self.console = Console()
        self.display = ClientDisplay(self.console)

    async def test_mock_client_integration(self):
        """Test NetworkClient with mock components."""
        print("\n🧪 Testing Mock Client Integration")
        print("=" * 50)

        try:
            # Create mock orion client
            mock_client = MagicMock(spec=OrionClient)
            mock_client.device_manager = MagicMock()
            mock_client.initialize = AsyncMock()
            mock_client.shutdown = AsyncMock()

            # Create mock orchestrator
            mock_orchestrator = MockTaskOrionOrchestrator()

            # Create mock orion agent
            mock_agent = MockOrionAgent(
                orchestrator=mock_orchestrator,
                name="test_mock_agent"
            )

            # Create mock session
            mock_session = MagicMock(spec=NetworkSession)
            mock_session.task = "test_mock_workflow"
            mock_session._rounds = {"round1": {}, "round2": {}}
            mock_session.run = AsyncMock()
            mock_session.force_finish = AsyncMock()
            mock_session.log_path = "test/mock/path"
            
            # Create mock orion
            mock_orion = MagicMock()
            mock_orion.orion_id = "mock_orion_123"
            mock_orion.name = "Mock Test Orion"
            mock_orion.tasks = ["task1", "task2", "task3"]
            mock_orion.dependencies = []
            mock_orion.state = MagicMock()
            mock_orion.state.value = "completed"
            mock_session._current_orion = mock_orion

            # Test with mock components
            client = NetworkClient(session_name="mock_test_session")
            
            # Manually set mock components
            client._client = mock_client
            client._session = mock_session

            print("✅ Mock client created successfully")
            
            # Test process request with mock
            result = await client.process_request("Test mock request", "mock_task")
            
            print(f"✅ Request processed with mock: {result['status']}")
            print(f"   - Execution time: {result.get('execution_time', 'N/A')}")
            print(f"   - Orion: {result.get('orion', {}).get('name', 'N/A')}")
            
            # Test shutdown
            await client.shutdown()
            print("✅ Mock client shutdown completed")
            
            return True
            
        except Exception as e:
            print(f"❌ Mock client test failed: {e}")
            return False

    def test_visualization_display_functions(self):
        """Test all visualization display functions."""
        print("\n🎨 Testing Visualization Display Functions")
        print("=" * 50)

        try:
            # Test banner display
            print("\n1. Testing Network Banner:")
            self.display.show_network_banner()
            
            # Test interactive banner
            print("\n2. Testing Interactive Banner:")
            self.display.show_interactive_banner()
            
            # Test help display
            print("\n3. Testing Help Display:")
            self.display.show_help()
            
            # Test status display
            print("\n4. Testing Status Display:")
            session_info = {
                "rounds": 3,
                "initialized": True
            }
            self.display.show_status(
                "test_session",
                10,
                Path("./test_output"),
                session_info
            )
            
            # Test result display
            print("\n5. Testing Result Display:")
            mock_result = {
                "status": "completed",
                "execution_time": 12.34,
                "rounds": 3,
                "orion": {
                    "id": "test_orion",
                    "name": "Test Visualization Orion",
                    "task_count": 5,
                    "dependency_count": 4,
                    "state": "completed"
                },
                "trajectory_path": "test/path/trajectory.json"
            }
            self.display.display_result(mock_result)
            
            # Test error result display
            print("\n6. Testing Error Result Display:")
            error_result = {
                "status": "failed",
                "error": "Mock error for testing visualization",
                "timestamp": "2025-09-24T10:30:00"
            }
            self.display.display_result(error_result)
            
            print("\n✅ All visualization functions tested successfully")
            return True
            
        except Exception as e:
            print(f"❌ Visualization test failed: {e}")
            return False

    def test_display_formatting(self):
        """Test display formatting with various data."""
        print("\n📊 Testing Display Formatting")
        print("=" * 50)

        try:
            # Test success messages
            self.display.print_success("This is a success message")
            
            # Test error messages  
            self.display.print_error("This is an error message")
            
            # Test warning messages
            self.display.print_warning("This is a warning message")
            
            # Test info messages
            self.display.print_info("This is an info message")
            
            # Test progress indicator
            print("\n7. Testing Progress Indicator:")
            progress = self.display.show_initialization_progress()
            task = progress.add_task("Testing progress display...", total=None)
            
            # Simulate some work
            import time
            for i in range(3):
                progress.update(task, description=f"Step {i+1}: Processing...")
                time.sleep(0.5)
            
            progress.stop()
            
            print("\n✅ Display formatting tests completed")
            return True
            
        except Exception as e:
            print(f"❌ Display formatting test failed: {e}")
            return False

    async def test_mock_orion_agent(self):
        """Test the MockOrionAgent functionality."""
        print("\n🤖 Testing Mock Orion Agent")
        print("=" * 50)

        try:
            # Create mock orchestrator
            mock_orchestrator = MockTaskOrionOrchestrator(enable_logging=True)
            
            # Create mock agent
            mock_agent = MockOrionAgent(
                orchestrator=mock_orchestrator,
                name="test_mock_orion"
            )
            
            # Create mock context
            from alien.module.context import Context, ContextNames
            context = Context()
            context.set(ContextNames.REQUEST, "Create a complex parallel processing workflow")
            
            print("1. Testing orion creation...")
            orion = await mock_agent.process_creation(context)
            print(f"   ✅ Created orion: {orion.name}")
            print(f"   ✅ Task count: {orion.task_count}")
            print(f"   ✅ Tasks: {[task.description for task in orion.tasks.values()][:3]}...")
            
            print("2. Testing orion editing...")
            edited_orion = await mock_agent.process_editing(context)
            print(f"   ✅ Edited orion: {edited_orion.name}")
            print(f"   ✅ Updated task count: {edited_orion.task_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Mock orion agent test failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all mock and visualization tests."""
        print("🚀 Starting Mock Client and Visualization Tests")
        print("=" * 80)

        results = []
        
        # Test mock client integration
        results.append(await self.test_mock_client_integration())
        
        # Test visualization functions
        results.append(self.test_visualization_display_functions())
        
        # Test display formatting
        results.append(self.test_display_formatting())
        
        # Test mock orion agent
        results.append(await self.test_mock_orion_agent())
        
        # Summary
        print("\n" + "=" * 80)
        print("🏁 Test Results Summary")
        print("=" * 80)
        
        test_names = [
            "Mock Client Integration",
            "Visualization Display Functions", 
            "Display Formatting",
            "Mock Orion Agent"
        ]
        
        passed = sum(results)
        total = len(results)
        
        for i, (test_name, result) in enumerate(zip(test_names, results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{i+1}. {test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Mock client and visualization are working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the output above.")
        
        return passed == total


async def main():
    """Main test function."""
    tester = MockNetworkClientTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
