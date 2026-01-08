#!/usr/bin/env python3
"""
 [Text Cleaned]  WSManager  [Text Cleaned]  AlienWebSocketHandler  [Text Cleaned] 
"""

import asyncio
import json
import logging
import sys
import websockets
from datetime import datetime, timezone
from aip.messages import ClientMessage, ClientMessageType, TaskStatus
from Alien.server.services.ws_manager import WSManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def comprehensive_client_type_test():
    """ [Text Cleaned] """

    print("=" * 80)
    print("🧪  [Text Cleaned] ")
    print("=" * 80)

    server_url = "ws://localhost:5000/ws"
    connections = []

    try:
        print("\n[1]  [Text Cleaned] ...")

        device1_ws = await websockets.connect(server_url)
        connections.append(device1_ws)
        device1_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="device_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "device_client",
                "os": "windows",
                "capabilities": ["web_browsing", "file_management"],
            },
        )
        await device1_ws.send(device1_reg.model_dump_json())
        print("📱  [Text Cleaned]  device_001  [Text Cleaned] ")

        device2_ws = await websockets.connect(server_url)
        connections.append(device2_ws)
        device2_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="device_002",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "device_client",
                "os": "macos",
                "capabilities": ["office_applications", "text_editing"],
            },
        )
        await device2_ws.send(device2_reg.model_dump_json())
        print("📱  [Text Cleaned]  device_002  [Text Cleaned] ")

        network1_ws = await websockets.connect(server_url)
        connections.append(network1_ws)
        network1_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="network_alpha@client_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "network_client",
                "network_id": "network_alpha",
                "device_id": "client_001",
                "capabilities": ["task_distribution", "session_management"],
                "version": "2.0",
            },
        )
        await network1_ws.send(network1_reg.model_dump_json())
        print("🌟  [Text Cleaned]  network_alpha@client_001  [Text Cleaned] ")

        network2_ws = await websockets.connect(server_url)
        connections.append(network2_ws)
        network2_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="network_beta@client_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "network_client",
                "network_id": "network_beta",
                "device_id": "client_001",
                "capabilities": ["task_distribution", "device_coordination"],
                "version": "2.0",
            },
        )
        await network2_ws.send(network2_reg.model_dump_json())
        print("🌟  [Text Cleaned]  network_beta@client_001  [Text Cleaned] ")

        print("\n[2]  [Text Cleaned] ...")
        await asyncio.sleep(2)

        print("\n[3]  [Text Cleaned] ...")

        device_heartbeat = ClientMessage(
            type=ClientMessageType.HEARTBEAT,
            client_id="device_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await device1_ws.send(device_heartbeat.model_dump_json())
        print("💓  [Text Cleaned] ")

        network_heartbeat = ClientMessage(
            type=ClientMessageType.HEARTBEAT,
            client_id="network_alpha@client_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await network1_ws.send(network_heartbeat.model_dump_json())
        print("💓  [Text Cleaned] ")

        device_info_request = ClientMessage(
            type=ClientMessageType.DEVICE_INFO,
            client_id="network_alpha@client_001",
            target_id="device_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await network1_ws.send(device_info_request.model_dump_json())
        print("📊  [Text Cleaned] ")

        print("\n[4]  [Text Cleaned] ...")
        await asyncio.sleep(3)

        print("\n✅  [Text Cleaned] ")

    except Exception as e:
        print(f"❌  [Text Cleaned] : {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\n[5]  [Text Cleaned] ...")
        for ws in connections:
            try:
                await ws.close()
            except:
                pass
        print("🧹  [Text Cleaned] ")

    print("\n" + "=" * 80)
    print("🎯  [Text Cleaned] :")
    print("   📱  [Text Cleaned]  'Device client'  [Text Cleaned] ")
    print("   🌟  [Text Cleaned]  'network client'  [Text Cleaned] ")
    print("   💓  [Text Cleaned] ")
    print("   📊  [Text Cleaned] ")
    print("=" * 80)


async def main():
    """ [Text Cleaned] """
    try:
        await comprehensive_client_type_test()
    except KeyboardInterrupt:
        print("\n [Text Cleaned] ")
    except Exception as e:
        print(f" [Text Cleaned] : {e}")


if __name__ == "__main__":
    asyncio.run(main())
