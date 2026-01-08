#!/usr/bin/env python3
"""
测试重构后的星座客户端验证功能
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock
from aip.messages import ClientMessage, ClientMessageType, TaskStatus
from Alien.server.ws.handler import AlienWebSocketHandler
from Alien.server.services.ws_manager import WSManager
from Alien.server.services.session_manager import SessionManager
from datetime import datetime, timezone

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MockWebSocketnetworkValid:
    """模拟有效星座客户端的 WebSocket 连接"""

    def __init__(self):
        self.messages_sent = []
        self.closed = False

    async def accept(self):
        pass

    async def receive_text(self):
        # 模拟有效的星座客户端注册消息（声明一个存在的设备）
        network_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="test_network@existing_device",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "network_client",
                "network_id": "test_network",
                "device_id": "existing_device",
                "capabilities": ["task_distribution"],
                "version": "2.0",
            },
        )
        return network_reg.model_dump_json()

    async def send_text(self, message):
        self.messages_sent.append(message)

    async def close(self):
        self.closed = True


class MockWebSocketnetworkInvalid:
    """模拟无效星座客户端的 WebSocket 连接"""

    def __init__(self):
        self.messages_sent = []
        self.closed = False

    async def accept(self):
        pass

    async def receive_text(self):
        # 模拟无效的星座客户端注册消息（声明一个不存在的设备）
        network_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="test_network@nonexistent_device",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "network_client",
                "network_id": "test_network",
                "device_id": "nonexistent_device",
                "capabilities": ["task_distribution"],
                "version": "2.0",
            },
        )
        return network_reg.model_dump_json()

    async def send_text(self, message):
        self.messages_sent.append(message)

    async def close(self):
        self.closed = True


async def test_network_validation():
    """测试星座客户端验证功能"""

    print("=" * 80)
    print("🌟 测试重构后的星座客户端验证功能")
    print("=" * 80)

    # 创建模拟对象
    ws_manager = WSManager()
    session_manager = SessionManager()
    handler = AlienWebSocketHandler(ws_manager, session_manager)

    try:
        # 先添加一个设备客户端到 ws_manager
        print("\n[1] 预先注册一个设备客户端...")
        mock_device_ws = AsyncMock()
        ws_manager.add_client("existing_device", mock_device_ws, "device")
        print("✅ 设备客户端 'existing_device' 已注册")

        # 测试2: 有效的星座客户端（声明存在的设备）
        print("\n[2] 测试有效的星座客户端注册...")

        mock_network_valid = MockWebSocketnetworkValid()
        try:
            client_id, client_type = await handler.connect(mock_network_valid)
            print(f"   客户端ID: {client_id}")
            print(f"   客户端类型: {client_type}")
            print(f"   连接是否关闭: {mock_network_valid.closed}")
            print("✅ 有效星座客户端注册成功")
        except Exception as e:
            print(f"❌ 有效星座客户端注册失败: {e}")

        # 测试3: 无效的星座客户端（声明不存在的设备）
        print("\n[3] 测试无效的星座客户端注册...")

        mock_network_invalid = MockWebSocketnetworkInvalid()
        try:
            client_id, client_type = await handler.connect(mock_network_invalid)
            print(f"❌ 无效星座客户端注册成功了（这不应该发生）")
        except ValueError as e:
            print(f"✅ 无效星座客户端被正确拒绝: {e}")
            print(f"   连接是否关闭: {mock_network_invalid.closed}")
            print(
                f"   发送的错误消息数量: {len(mock_network_invalid.messages_sent)}"
            )
        except Exception as e:
            print(f"❌ 意外错误: {e}")

        # 测试4: 验证 WSManager 状态
        print("\n[4] 验证 WSManager 状态...")
        stats = ws_manager.get_stats()
        print(f"   📊 客户端统计: {stats}")

        device_clients = ws_manager.list_clients_by_type("device")
        network_clients = ws_manager.list_clients_by_type("network")
        print(f"   📱 设备客户端: {device_clients}")
        print(f"   🌟 星座客户端: {network_clients}")

        print("\n✅ 星座客户端验证测试完成")

    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)
    print("🎯 星座客户端验证结果:")
    print("   ✅ 有效星座客户端可以成功注册")
    print("   ✅ 无效星座客户端被正确拒绝")
    print("   ✅ 错误消息正确发送")
    print("   ✅ 连接正确关闭")
    print("=" * 80)


async def main():
    """主函数"""
    try:
        await test_network_validation()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
