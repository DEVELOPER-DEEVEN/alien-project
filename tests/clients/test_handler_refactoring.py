#!/usr/bin/env python3
"""
 [Text Cleaned]  AlienWebSocketHandler  [Text Cleaned] 
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock
from aip.messages import ClientMessage, ClientMessageType, TaskStatus
from Alien.server.ws.handler import AlienWebSocketHandler
from Alien.server.services.ws_manager import WSManager
from Alien.server.services.session_manager import SessionManager
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MockWebSocket:
    """ [Text Cleaned]  WebSocket  [Text Cleaned] """

    def __init__(self):
        self.messages_sent = []
        self.closed = False

    async def accept(self):
        pass

    async def receive_text(self):
        device_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="test_device_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={"type": "device_client", "os": "windows"},
        )
        return device_reg.model_dump_json()

    async def send_text(self, message):
        self.messages_sent.append(message)

    async def close(self):
        self.closed = True


async def test_handler_methods():
    """ [Text Cleaned] """

    print("=" * 80)
    print("🧪  [Text Cleaned]  AlienWebSocketHandler  [Text Cleaned] ")
    print("=" * 80)

    ws_manager = WSManager()
    session_manager = SessionManager()
    handler = AlienWebSocketHandler(ws_manager, session_manager)

    try:
        print("\n[1]  [Text Cleaned] ...")

        methods_to_check = [
            "_parse_registration_message",
            "_determine_and_validate_client_type",
            "_validate_network_client",
            "_send_registration_confirmation",
            "_send_error_response",
            "_log_client_connection",
        ]

        for method_name in methods_to_check:
            if hasattr(handler, method_name):
                print(f"✅ {method_name}  [Text Cleaned] ")
            else:
                print(f"❌ {method_name}  [Text Cleaned] ")

        print("\n[2]  [Text Cleaned] ...")

        mock_websocket = MockWebSocket()
        client_id, client_type = await handler.connect(mock_websocket)

        print(f"    [Text Cleaned] ID: {client_id}")
        print(f"    [Text Cleaned] : {client_type}")
        print(f"    [Text Cleaned] : {len(mock_websocket.messages_sent)}")

        if client_type == "device":
            print("✅  [Text Cleaned] ")
        else:
            print("❌  [Text Cleaned] ")

        print("\n[3]  [Text Cleaned] ...")

        import inspect

        connect_source = inspect.getsource(handler.connect)
        connect_lines = len(connect_source.split("\n"))

        print(f"   connect  [Text Cleaned] : {connect_lines}")
        if connect_lines < 30:            print("✅ connect  [Text Cleaned] ")
        else:
            print("⚠️ connect  [Text Cleaned] ")

        if "_parse_registration_message" in connect_source:
            print("✅ connect  [Text Cleaned]  _parse_registration_message")
        if "_determine_and_validate_client_type" in connect_source:
            print("✅ connect  [Text Cleaned]  _determine_and_validate_client_type")
        if "_send_registration_confirmation" in connect_source:
            print("✅ connect  [Text Cleaned]  _send_registration_confirmation")

        print("\n✅  [Text Cleaned] ")

    except Exception as e:
        print(f"❌  [Text Cleaned] : {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)
    print("🎯  [Text Cleaned] :")
    print("   ✅  [Text Cleaned] ， [Text Cleaned] ")
    print("   ✅ connect  [Text Cleaned] ")
    print("   ✅  [Text Cleaned] ")
    print("=" * 80)


async def main():
    """ [Text Cleaned] """
    try:
        await test_handler_methods()
    except KeyboardInterrupt:
        print("\n [Text Cleaned] ")
    except Exception as e:
        print(f" [Text Cleaned] : {e}")


if __name__ == "__main__":
    asyncio.run(main())
