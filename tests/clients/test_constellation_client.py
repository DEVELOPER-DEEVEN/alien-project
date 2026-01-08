#!/usr/bin/env python3
"""
 [Text Cleaned]  networkClient  [Text Cleaned] 
"""

import asyncio
import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cluster.client.network_client import networkClient
from cluster.client.config_loader import networkConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


async def test_network_client():
    """ [Text Cleaned]  networkClient  [Text Cleaned] """

    print("=" * 80)
    print("[*] networkClient  [Text Cleaned] ")
    print("=" * 80)

    try:
        print("\n[1] 1.  [Text Cleaned] ...")
        config_path = "config/network_sample.yaml"
        config = networkConfig.from_yaml(config_path)

        print(f"[+]  [Text Cleaned] !")
        print(f"    [Text Cleaned] ID: {config.network_id}")
        print(f"    [Text Cleaned] : {len(config.devices)}")
        for i, device in enumerate(config.devices, 1):
            print(f"    [Text Cleaned] {i}: {device.device_id} -> {device.server_url}")

        print("\n[2] 2.  [Text Cleaned]  networkClient...")
        client = networkClient(config=config)

        print("\n[3] 3.  [Text Cleaned] ...")
        registration_results = await client.initialize()

        print("[*]  [Text Cleaned] :")
        success_count = 0
        for device_id, success in registration_results.items():
            status = "[+]  [Text Cleaned] " if success else "[-]  [Text Cleaned] "
            print(f"   {device_id}: {status}")
            if success:
                success_count += 1

        print(
            f"\n[*]  [Text Cleaned] : {success_count}/{len(registration_results)}  [Text Cleaned] "
        )

        if success_count == 0:
            print("[-]  [Text Cleaned] ， [Text Cleaned] ")
            return False

        print("\n[4] 4.  [Text Cleaned] ...")
        connected_devices = client.get_connected_devices()
        print(f" [Text Cleaned] : {connected_devices}")

        for device_id in connected_devices:
            status = client.get_device_status(device_id)
            print(f"   {device_id}: {status}")

        print("\n[5] 5.  [Text Cleaned] :")
        network_info = client.get_network_info()
        print(f"    [Text Cleaned] ID: {network_info['network_id']}")
        print(f"    [Text Cleaned] : {network_info['connected_devices']}")
        print(f"    [Text Cleaned] : {network_info['total_devices']}")
        print(
            f"    [Text Cleaned] : {network_info['configuration']['heartbeat_interval']}s"
        )
        print(
            f"    [Text Cleaned] : {network_info['configuration']['max_concurrent_tasks']}"
        )

        if connected_devices:
            print("\n[6] 6.  [Text Cleaned]  ( [Text Cleaned]  10  [Text Cleaned] )...")
            await asyncio.sleep(10)

            final_connected = client.get_connected_devices()
            print(f"10 [Text Cleaned] : {final_connected}")

            if len(final_connected) == len(connected_devices):
                print("[+]  [Text Cleaned] ")
            else:
                print("[!]  [Text Cleaned] ， [Text Cleaned] ")

        print("\n[7] 7.  [Text Cleaned] ...")
        validation = client.validate_config()
        if validation["valid"]:
            print("[+]  [Text Cleaned] ")
        else:
            print("[-]  [Text Cleaned] :")
            for error in validation["errors"]:
                print(f"    [Text Cleaned] : {error}")
            for warning in validation["warnings"]:
                print(f"    [Text Cleaned] : {warning}")

        print("\n[8] 8.  [Text Cleaned] ...")
        await client.shutdown()
        print("[+]  [Text Cleaned] ")

        return success_count > 0

    except Exception as e:
        print(f"\n[-]  [Text Cleaned] : {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_device_operations():
    """ [Text Cleaned] """

    print("\n" + "=" * 80)
    print("[*]  [Text Cleaned] ")
    print("=" * 80)

    try:
        config = networkConfig.from_yaml("config/network_sample.yaml")
        client = networkClient(config=config)

        print("\n[+]  [Text Cleaned] ...")
        added = await client.add_device_to_config(
            device_id="test_device_manual",
            server_url="ws://localhost:5001/ws",
            capabilities=["testing", "manual"],
            metadata={"test": True},
            auto_connect=False,            register_immediately=False,
        )

        if added:
            print("[+]  [Text Cleaned] ")
            config_summary = client.get_config_summary()
            print(f"    [Text Cleaned] : {config_summary['devices_count']}")
        else:
            print("[-]  [Text Cleaned] ")

        await client.shutdown()
        return True

    except Exception as e:
        print(f"[-]  [Text Cleaned] : {e}")
        return False


async def main():
    """ [Text Cleaned] """

    print("[*]  [Text Cleaned]  networkClient  [Text Cleaned] ")

    connection_test_passed = await test_network_client()

    operations_test_passed = await test_device_operations()

    print("\n" + "=" * 80)
    print("[*]  [Text Cleaned] ")
    print("=" * 80)

    tests = [
        (" [Text Cleaned] ", connection_test_passed),
        (" [Text Cleaned] ", operations_test_passed),
    ]

    passed_count = 0
    for test_name, passed in tests:
        status = "[+]  [Text Cleaned] " if passed else "[-]  [Text Cleaned] "
        print(f"   {test_name}: {status}")
        if passed:
            passed_count += 1

    print(f"\n [Text Cleaned] : {passed_count}/{len(tests)}  [Text Cleaned] ")

    if passed_count == len(tests):
        print("[+]  [Text Cleaned] ！networkClient  [Text Cleaned] 。")
    else:
        print("[!]  [Text Cleaned] ， [Text Cleaned] 。")


if __name__ == "__main__":
    asyncio.run(main())
