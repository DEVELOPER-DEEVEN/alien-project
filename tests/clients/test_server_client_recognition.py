#!/usr/bin/env python3
"""
 [Text Cleaned] 
 [Text Cleaned] 
"""

import asyncio
import json
import logging
import sys
import websockets
from datetime import datetime, timezone
from aip.messages import ClientMessage, ClientMessageType, TaskStatus

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_server_client_recognition():
    """ [Text Cleaned] """

    print("=" * 80)
    print("🔍  [Text Cleaned] ")
    print("=" * 80)

    server_url = "ws://localhost:5000/ws"

    print("\n[1]  [Text Cleaned] ...")

    try:
        device_ws = await websockets.connect(server_url)

        device_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="test_device_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "device_client",
                "os": "windows",
                "capabilities": ["web_browsing", "file_management"],
            },
        )

        await device_ws.send(device_reg.model_dump_json())
        print("📱  [Text Cleaned] ")

        await asyncio.sleep(1)
        heartbeat = ClientMessage(
            type=ClientMessageType.HEARTBEAT,
            client_id="test_device_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await device_ws.send(heartbeat.model_dump_json())
        print("💓  [Text Cleaned] ")

        await device_ws.close()
        print("✅  [Text Cleaned] ")

    except Exception as e:
        print(f"❌  [Text Cleaned] : {e}")

    print("\n[2]  [Text Cleaned] ...")

    try:
        network_ws = await websockets.connect(server_url)

        network_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="test_network@client_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "network_client",
                "network_id": "test_network",
                "device_id": "client_001",
                "capabilities": ["task_distribution", "session_management"],
                "version": "2.0",
            },
        )

        await network_ws.send(network_reg.model_dump_json())
        print("🌟  [Text Cleaned] ")

        await asyncio.sleep(1)
        heartbeat = ClientMessage(
            type=ClientMessageType.HEARTBEAT,
            client_id="test_network@client_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await network_ws.send(heartbeat.model_dump_json())
        print("💓  [Text Cleaned] ")

        await network_ws.close()
        print("✅  [Text Cleaned] ")

    except Exception as e:
        print(f"❌  [Text Cleaned] : {e}")

    print("\n" + "=" * 80)
    print("🎯  [Text Cleaned] ！ [Text Cleaned] :")
    print("   -  [Text Cleaned] : 📱 Device client test_device_001 connected")
    print(
        "   -  [Text Cleaned] : 🌟 network client test_network@client_001 connected"
    )
    print("   -  [Text Cleaned] emoji [Text Cleaned] ")
    print("=" * 80)


async def main():
    """ [Text Cleaned] """
    try:
        await test_server_client_recognition()
    except KeyboardInterrupt:
        print("\n [Text Cleaned] ")
    except Exception as e:
        print(f" [Text Cleaned] : {e}")


if __name__ == "__main__":
    asyncio.run(main())
