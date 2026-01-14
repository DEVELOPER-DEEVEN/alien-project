#!/usr/bin/env python3

"""
Demo Script: NetworkClient with Mock AgentProfile for Log Collection

This script demonstrates how to use NetworkClient with mock AgentProfile objects
to simulate the log collection and Excel generation scenario.

Usage:
    python demo_network_client_log_collection.py
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from unittest.mock import Mock, AsyncMock, patch

from network.network_client import NetworkClient
from network.client.components.types import AgentProfile, DeviceStatus
from network.client.config_loader import OrionConfig, DeviceConfig

# Suppress debug logs for cleaner demo output
logging.getLogger("alien.network.network_client").setLevel(logging.WARNING)


def create_mock_devices():
    """Create mock AgentProfile objects for demonstration."""

    # Linux Server 1 - Web Server
    linux_server_1 = AgentProfile(
        device_id="linux_server_001",
        server_url="ws://192.168.1.101:5000/ws",
        os="linux",
        capabilities=[
            "log_collection",
            "file_operations",
            "system_monitoring",
            "bash_scripting",
            "ssh_access",
        ],
        metadata={
            "hostname": "web-server-01",
            "location": "datacenter_rack_a",
            "os_version": "Ubuntu 22.04 LTS",
            "performance": "high",
            "cpu_cores": 16,
            "memory_gb": 64,
            "services": ["nginx", "postgresql", "redis"],
            "log_paths": [
                "/var/log/nginx/access.log",
                "/var/log/nginx/error.log",
                "/var/log/postgresql/postgresql.log",
                "/var/log/syslog",
            ],
        },
        status=DeviceStatus.CONNECTED,
        last_heartbeat=datetime.now(timezone.utc),
        connection_attempts=1,
        max_retries=5,
    )

    # Linux Server 2 - API Server
    linux_server_2 = AgentProfile(
        device_id="linux_server_002",
        server_url="ws://192.168.1.102:5000/ws",
        os="linux",
        capabilities=[
            "log_collection",
            "file_operations",
            "system_monitoring",
            "bash_scripting",
            "database_operations",
        ],
        metadata={
            "hostname": "api-server-01",
            "location": "datacenter_rack_b",
            "os_version": "CentOS 8",
            "performance": "high",
            "cpu_cores": 12,
            "memory_gb": 32,
            "services": ["apache", "mysql", "mongodb"],
            "log_paths": [
                "/var/log/httpd/access_log",
                "/var/log/httpd/error_log",
                "/var/log/mysql/mysql.log",
                "/var/log/mongodb/mongod.log",
                "/var/log/messages",
            ],
        },
        status=DeviceStatus.CONNECTED,
        last_heartbeat=datetime.now(timezone.utc),
        connection_attempts=1,
        max_retries=5,
    )

    # Windows Workstation - Analyst PC
    windows_workstation = AgentProfile(
        device_id="windows_workstation_001",
        server_url="ws://192.168.1.100:5000/ws",
        os="windows",
        capabilities=[
            "office_applications",
            "excel_processing",
            "file_management",
            "data_analysis",
            "report_generation",
            "email_operations",
        ],
        metadata={
            "hostname": "analyst-pc-01",
            "location": "office_floor_2",
            "os_version": "Windows 11 Pro",
            "performance": "high",
            "cpu_cores": 8,
            "memory_gb": 32,
            "installed_software": [
                "Microsoft Office 365",
                "Python 3.11",
                "Excel",
                "Power BI",
                "Visual Studio Code",
            ],
            "excel_version": "16.0",
            "python_packages": ["pandas", "openpyxl", "xlsxwriter"],
        },
        status=DeviceStatus.CONNECTED,
        last_heartbeat=datetime.now(timezone.utc),
        connection_attempts=1,
        max_retries=5,
    )

    return linux_server_1, linux_server_2, windows_workstation


def create_mock_orion_config(devices):
    """Create OrionConfig with mock devices."""
    device_configs = []

    for device in devices:
        device_config = DeviceConfig(
            device_id=device.device_id,
            server_url=device.server_url,
            capabilities=device.capabilities,
            metadata=device.metadata,
            auto_connect=True,
            max_retries=5,
        )
        device_configs.append(device_config)

    return OrionConfig(
        orion_id="log_collection_demo_orion",
        heartbeat_interval=30.0,
        reconnect_delay=5.0,
        max_concurrent_tasks=3,
        devices=device_configs,
    )


def create_mock_orion_client(devices):
    """Create mock OrionClient with devices."""
    mock_client = AsyncMock()

    # Mock device registry
    mock_device_registry = Mock()
    device_dict = {device.device_id: device for device in devices}

    mock_device_registry.get_all_devices.return_value = device_dict
    mock_device_registry.get_connected_devices.return_value = [
        d.device_id for d in devices
    ]

    mock_client.device_manager = Mock()
    mock_client.device_manager.device_registry = mock_device_registry
    mock_client.device_manager.get_connected_devices.return_value = [
        d.device_id for d in devices
    ]

    # Mock initialization and shutdown
    mock_client.initialize = AsyncMock()
    mock_client.shutdown = AsyncMock()

    return mock_client


def create_mock_network_session():
    """Create mock NetworkSession for demonstration."""
    mock_session = AsyncMock()
    mock_session._rounds = []
    mock_session.log_path = "./logs/demo_log_collection_session.log"

    # Mock orion result
    mock_orion = Mock()
    mock_orion.orion_id = "demo_orion_001"
    mock_orion.name = "Log Collection Demo Orion"
    mock_orion.tasks = [
        "collect_nginx_logs_server1",
        "collect_postgresql_logs_server1",
        "collect_apache_logs_server2",
        "collect_mysql_logs_server2",
        "aggregate_log_data",
        "generate_excel_report",
        "send_email_notification",
    ]
    mock_orion.dependencies = [
        "collect_logs -> aggregate_log_data",
        "aggregate_log_data -> generate_excel_report",
        "generate_excel_report -> send_email_notification",
    ]
    mock_orion.state = Mock()
    mock_orion.state.value = "completed"

    mock_session._current_orion = mock_orion

    # Mock run method with realistic execution simulation
    async def mock_run_side_effect():
        print("  [CONTINUE] Analyzing user request...")
        mock_session._rounds.append(
            {"round": 1, "action": "analyze_request", "duration": 2.1}
        )

        print("  ️  Creating task orion...")
        mock_session._rounds.append(
            {"round": 2, "action": "create_orion", "duration": 1.8}
        )

        print("  [TASK] Planning device assignments...")
        mock_session._rounds.append(
            {"round": 3, "action": "plan_assignments", "duration": 1.5}
        )

        print("  [START] Executing tasks across devices...")
        mock_session._rounds.append(
            {"round": 4, "action": "execute_tasks", "duration": 15.3}
        )

        print("  [STATUS] Generating final report...")
        mock_session._rounds.append(
            {"round": 5, "action": "generate_report", "duration": 3.2}
        )

    mock_session.run = AsyncMock(side_effect=mock_run_side_effect)
    mock_session.force_finish = AsyncMock()

    return mock_session


async def demo_network_client_log_collection():
    """Demonstrate NetworkClient with mock devices for log collection."""

    print(" Network Client Log Collection Demo")
    print("=" * 50)

    # Create mock devices
    print("\n Creating mock devices...")
    devices = create_mock_devices()
    linux1, linux2, windows = devices

    print(f"  [OK] Linux Server 1: {linux1.metadata['hostname']} ({linux1.device_id})")
    print(f"  [OK] Linux Server 2: {linux2.metadata['hostname']} ({linux2.device_id})")
    print(
        f"  [OK] Windows Workstation: {windows.metadata['hostname']} ({windows.device_id})"
    )

    # Create orion config
    orion_config = create_mock_orion_config(devices)
    print(f"\n️  Created orion: {orion_config.orion_id}")
    print(f"    [STATUS] Total devices: {len(orion_config.devices)}")
    print(f"     Max concurrent tasks: {orion_config.max_concurrent_tasks}")

    # Create mocks for dependencies
    mock_orion_client = create_mock_orion_client(devices)
    mock_network_session = create_mock_network_session()

    # Setup patches and run demo
    with patch(
        "alien.network.network_client.OrionConfig.from_yaml"
    ) as mock_from_yaml, patch(
        "alien.network.network_client.OrionClient"
    ) as mock_client_class, patch(
        "alien.network.network_client.NetworkSession"
    ) as mock_session_class:

        mock_from_yaml.return_value = orion_config
        mock_client_class.return_value = mock_orion_client
        mock_session_class.return_value = mock_network_session

        # Initialize NetworkClient
        print("\n[START] Initializing Network Client...")
        with tempfile.TemporaryDirectory() as temp_dir:
            client = NetworkClient(
                session_name="demo_log_collection_session",
                max_rounds=10,
                log_level="WARNING",  # Reduce noise for demo
                output_dir=temp_dir,
            )

            await client.initialize()
            print("    [OK] Network Client initialized successfully")

            # Verify device availability
            print("\n Checking device availability...")
            connected_devices = client._client.device_manager.get_connected_devices()
            print(f"     Connected devices: {len(connected_devices)}")

            all_devices = (
                client._client.device_manager.device_registry.get_all_devices()
            )
            for device_id, device in all_devices.items():
                capabilities_summary = ", ".join(device.capabilities[:3])
                if len(device.capabilities) > 3:
                    capabilities_summary += f" (+{len(device.capabilities)-3} more)"
                print(f"      • {device_id}: {device.os} - {capabilities_summary}")

            # Process log collection request
            print("\n Processing log collection request...")

            log_collection_request = (
                "Collect comprehensive logs from both Linux servers (web-server-01 and api-server-01). "
                "From web-server-01, gather nginx access/error logs, PostgreSQL logs, and system logs. "
                "From api-server-01, collect Apache logs, MySQL logs, MongoDB logs, and system messages. "
                "Then, on the Windows workstation, create a detailed Excel report with log analysis, "
                "error statistics, performance metrics, and trend analysis. "
                "Finally, email the report to the operations team."
            )

            print(f"    Request: {log_collection_request[:100]}...")

            print("\n[CONTINUE] Executing session...")
            result = await client.process_request(
                request=log_collection_request,
                task_name="comprehensive_log_collection_and_reporting",
            )

            # Display results
            print("\n[STATUS] Session Results:")
            print(f"    [OK] Status: {result['status']}")
            print(f"    ⏱️  Execution time: {result['execution_time']:.2f} seconds")
            print(f"    [CONTINUE] Total rounds: {result['rounds']}")
            print(f"    [DATE] Start time: {result['start_time']}")

            if "orion" in result:
                orion_info = result["orion"]
                print(f"\n️  Orion Details:")
                print(f"     ID: {orion_info['id']}")
                print(f"     Name: {orion_info['name']}")
                print(f"    [TASK] Tasks: {orion_info['task_count']}")
                print(f"    [DEP] Dependencies: {orion_info['dependency_count']}")
                print(f"    [STATUS] State: {orion_info['state']}")

            # Show mock task execution details
            print(f"\n[TASK] Task Execution Summary:")
            tasks = mock_network_session._current_orion.tasks
            for i, task in enumerate(tasks, 1):
                print(f"    {i}. {task}")

            print(f"\n[DEP] Dependency Chain:")
            dependencies = mock_network_session._current_orion.dependencies
            for dep in dependencies:
                print(f"    • {dep}")

            # Cleanup
            print("\n Shutting down...")
            await client.shutdown()
            print("    [OK] Network Client shutdown complete")

    print("\n Demo completed successfully!")
    print("\nKey Behaviors Demonstrated:")
    print("  [OK] Mock AgentProfile creation and configuration")
    print("  [OK] OrionConfig setup with multiple devices")
    print("  [OK] NetworkClient initialization and request processing")
    print("  [OK] Cross-platform task orchestration simulation")
    print("  [OK] Session lifecycle management")
    print("  [OK] Error handling and resource cleanup")


if __name__ == "__main__":
    print("[ORION] Starting Network Client Demo with Mock AgentProfile")
    print(
        " Scenario: Log Collection from Linux Servers + Excel Generation on Windows"
    )
    print()

    try:
        asyncio.run(demo_network_client_log_collection())
    except KeyboardInterrupt:
        print("\n Demo interrupted by user")
    except Exception as e:
        print(f"\n[FAIL] Demo failed: {e}")
        import traceback

        traceback.print_exc()
