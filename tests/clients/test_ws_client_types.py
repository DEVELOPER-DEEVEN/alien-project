#!/usr/bin/env python3
"""
 [Text Cleaned]  WebSocket  [Text Cleaned] 
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


class TestWSClient:
    """ [Text Cleaned]  WebSocket  [Text Cleaned] """

    def __init__(
        self,
        client_id: str,
        client_type: str = "device",
        server_url: str = "ws://localhost:5000/ws",
    ):
        self.client_id = client_id
        self.client_type = client_type
        self.server_url = server_url
        self.websocket = None

    async def connect(self):
        """ [Text Cleaned] """
        try:
            self.websocket = await websockets.connect(self.server_url)

            metadata = {}
            if self.client_type == "network":
                metadata = {
                    "type": "network_client",
                    "network_id": "test_network",
                    "device_id": (
                        self.client_id.split("@")[-1]
                        if "@" in self.client_id
                        else self.client_id
                    ),
                    "capabilities": ["task_distribution", "session_management"],
                    "version": "2.0",
                }
            else:
                metadata = {
                    "type": "device_client",
                    "capabilities": ["web_browsing", "file_management"],
                    "os": "windows",
                    "version": "1.0",
                }

            registration_message = ClientMessage(
                type=ClientMessageType.REGISTER,
                client_id=self.client_id,
                status=TaskStatus.OK,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata=metadata,
            )

            await self.websocket.send(registration_message.model_dump_json())
            logger.info(
                f"[{self.client_type.upper()}] {self.client_id} registered successfully"
            )
            return True

        except Exception as e:
            logger.error(
                f"[{self.client_type.upper()}] Failed to connect {self.client_id}: {e}"
            )
            return False

    async def send_heartbeat(self):
        """ [Text Cleaned] """
        if not self.websocket:
            return False

        try:
            heartbeat_message = ClientMessage(
                type=ClientMessageType.HEARTBEAT,
                client_id=self.client_id,
                status=TaskStatus.OK,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            await self.websocket.send(heartbeat_message.model_dump_json())
            logger.info(f"[{self.client_type.upper()}] {self.client_id} sent heartbeat")
            return True

        except Exception as e:
            logger.error(
                f"[{self.client_type.upper()}] Failed to send heartbeat from {self.client_id}: {e}"
            )
            return False

    async def disconnect(self):
        """ [Text Cleaned] """
        if self.websocket:
            await self.websocket.close()
            logger.info(f"[{self.client_type.upper()}] {self.client_id} disconnected")


async def test_client_types():
    """ [Text Cleaned] """

    print("=" * 80)
    print("🧪  [Text Cleaned]  WebSocket  [Text Cleaned] ")
    print("=" * 80)

    device_client = TestWSClient("device_001", "device")
    network_client = TestWSClient(
        "test_network@client_001", "network"
    )

    try:
        print("\n[1]  [Text Cleaned] ...")
        device_connected = await device_client.connect()
        if device_connected:
            print("✅  [Text Cleaned] ")
        else:
            print("❌  [Text Cleaned] ")
            return

        print("\n[2]  [Text Cleaned] ...")
        network_connected = await network_client.connect()
        if network_connected:
            print("✅  [Text Cleaned] ")
        else:
            print("❌  [Text Cleaned] ")
            return

        print("\n[3]  [Text Cleaned] ...")
        await device_client.send_heartbeat()
        await network_client.send_heartbeat()

        print("\n[4]  [Text Cleaned]  5  [Text Cleaned] ...")
        await asyncio.sleep(5)

        print("\n✅  [Text Cleaned] ")

    except Exception as e:
        logger.error(f" [Text Cleaned] : {e}")

    finally:
        print("\n[5]  [Text Cleaned] ...")
        await device_client.disconnect()
        await network_client.disconnect()


async def main():
    """ [Text Cleaned] """
    try:
        await test_client_types()
    except KeyboardInterrupt:
        print("\n [Text Cleaned] ")
    except Exception as e:
        print(f" [Text Cleaned] : {e}")


if __name__ == "__main__":
    asyncio.run(main())
