#!/usr/bin/env python3
"""
综合测试 WSManager 和 ALIENWebSocketHandler 的客户端类型区分功能
"""

import asyncio
import json
import logging
import sys
import websockets
from datetime import datetime, timezone
from aip.messages import ClientMessage, ClientMessageType, TaskStatus
from alien.server.services.ws_manager import WSManager

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def comprehensive_client_type_test():
    """综合客户端类型测试"""

    print("=" * 80)
    print("🧪 综合客户端类型区分功能测试")
    print("=" * 80)

    server_url = "ws://localhost:5000/ws"
    connections = []

    try:
        # 1. 连接多个不同类型的客户端
        print("\n[1] 连接多个客户端...")

        # 设备客户端1
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
        print("📱 设备客户端 device_001 已连接")

        # 设备客户端2
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
        print("📱 设备客户端 device_002 已连接")

        # 星座客户端1
        orion1_ws = await websockets.connect(server_url)
        connections.append(orion1_ws)
        orion1_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="orion_alpha@client_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "orion_client",
                "orion_id": "orion_alpha",
                "device_id": "client_001",
                "capabilities": ["task_distribution", "session_management"],
                "version": "2.0",
            },
        )
        await orion1_ws.send(orion1_reg.model_dump_json())
        print("🌟 星座客户端 orion_alpha@client_001 已连接")

        # 星座客户端2
        orion2_ws = await websockets.connect(server_url)
        connections.append(orion2_ws)
        orion2_reg = ClientMessage(
            type=ClientMessageType.REGISTER,
            client_id="orion_beta@client_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "type": "orion_client",
                "orion_id": "orion_beta",
                "device_id": "client_001",
                "capabilities": ["task_distribution", "device_coordination"],
                "version": "2.0",
            },
        )
        await orion2_ws.send(orion2_reg.model_dump_json())
        print("🌟 星座客户端 orion_beta@client_001 已连接")

        # 2. 等待连接稳定
        print("\n[2] 等待连接稳定...")
        await asyncio.sleep(2)

        # 3. 发送不同类型的消息
        print("\n[3] 发送测试消息...")

        # 设备心跳
        device_heartbeat = ClientMessage(
            type=ClientMessageType.HEARTBEAT,
            client_id="device_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await device1_ws.send(device_heartbeat.model_dump_json())
        print("💓 设备客户端心跳已发送")

        # 星座心跳
        orion_heartbeat = ClientMessage(
            type=ClientMessageType.HEARTBEAT,
            client_id="orion_alpha@client_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await orion1_ws.send(orion_heartbeat.model_dump_json())
        print("💓 星座客户端心跳已发送")

        # 设备信息请求
        device_info_request = ClientMessage(
            type=ClientMessageType.DEVICE_INFO,
            client_id="orion_alpha@client_001",
            target_id="device_001",
            status=TaskStatus.OK,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await orion1_ws.send(device_info_request.model_dump_json())
        print("📊 星座客户端请求设备信息")

        # 4. 等待处理完成
        print("\n[4] 等待消息处理完成...")
        await asyncio.sleep(3)

        print("\n✅ 综合测试完成")

    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # 清理连接
        print("\n[5] 清理连接...")
        for ws in connections:
            try:
                await ws.close()
            except:
                pass
        print("🧹 连接已清理")

    print("\n" + "=" * 80)
    print("🎯 请检查服务器日志确认客户端类型被正确识别:")
    print("   📱 设备客户端应该有 'Device client' 标识")
    print("   🌟 星座客户端应该有 'Orion client' 标识")
    print("   💓 心跳消息应该有相应的客户端类型标识")
    print("   📊 设备信息请求应该正确处理")
    print("=" * 80)


async def main():
    """主函数"""
    try:
        await comprehensive_client_type_test()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
