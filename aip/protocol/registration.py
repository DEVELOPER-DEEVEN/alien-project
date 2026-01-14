
"""
Registration Protocol

Handles agent registration and capability advertisement in the AIP system.
"""

import datetime
import logging
from typing import Any, Dict, Optional

from aip.messages import (
    ClientMessage,
    ClientMessageType,
    ClientType,
    ServerMessage,
    ServerMessageType,
    TaskStatus,
)
from aip.protocol.base import AIPProtocol


class RegistrationProtocol(AIPProtocol):
    """
    Registration protocol for AIP.

    Handles:
    - Device agent registration
    - Orion client registration
    - Capability advertisement
    - Metadata exchange
    """

    def __init__(self, *args, **kwargs):
        """Initialize registration protocol."""
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"{__name__}.RegistrationProtocol")

    async def register_as_device(
        self,
        device_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        platform: str = "windows",
    ) -> bool:
        """
        Register as a device agent.

        :param device_id: Unique device identifier
        :param metadata: Optional device metadata (system info, capabilities, etc.)
        :param platform: Platform type (windows, linux, etc.)
        :return: True if registration successful, False otherwise
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}

            # Add platform to metadata
            if "platform" not in metadata:
                metadata["platform"] = platform

            # Add registration timestamp
            metadata["registration_time"] = datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat()

            # Create registration message
            reg_msg = ClientMessage(
                type=ClientMessageType.REGISTER,
                client_id=device_id,
                client_type=ClientType.DEVICE,
                status=TaskStatus.OK,
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                metadata=metadata,
            )

            # Send registration
            await self.send_message(reg_msg)
            self.logger.info(f"Sent device registration for {device_id}")

            # Wait for server response
            response = await self.receive_message(ServerMessage)

            if response.status == TaskStatus.OK:
                self.logger.info(f"Device {device_id} registered successfully")
                return True
            else:
                self.logger.error(
                    f"Device registration failed: {response.error or 'Unknown error'}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error during device registration: {e}", exc_info=True)
            return False

    async def register_as_orion(
        self,
        orion_id: str,
        target_device: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register as a orion client.

        :param orion_id: Unique orion identifier
        :param target_device: Target device ID for this orion
        :param metadata: Optional orion metadata
        :return: True if registration successful, False otherwise
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}

            # Add orion-specific metadata
            metadata.update(
                {
                    "type": "orion_client",
                    "targeted_device_id": target_device,
                    "registration_time": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                }
            )

            # Create registration message
            reg_msg = ClientMessage(
                type=ClientMessageType.REGISTER,
                client_id=orion_id,
                client_type=ClientType.ORION,
                target_id=target_device,
                status=TaskStatus.OK,
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                metadata=metadata,
            )

            # Send registration
            await self.send_message(reg_msg)
            self.logger.info(
                f"Sent orion registration for {orion_id} → {target_device}"
            )

            # Wait for server response
            response = await self.receive_message(ServerMessage)

            if response.status == TaskStatus.OK:
                self.logger.info(
                    f"Orion {orion_id} registered successfully"
                )
                return True
            elif response.status == TaskStatus.ERROR:
                self.logger.error(
                    f"Orion registration failed: {response.error or 'Unknown error'}"
                )
                return False
            else:
                self.logger.warning(
                    f"Unexpected registration response: {response.status}"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Error during orion registration: {e}", exc_info=True
            )
            return False

    async def send_registration_confirmation(
        self, response_id: Optional[str] = None
    ) -> None:
        """
        Send registration confirmation (server-side).

        :param response_id: Optional response ID for correlation
        """
        confirmation = ServerMessage(
            type=ServerMessageType.HEARTBEAT,
            status=TaskStatus.OK,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            response_id=response_id or self._generate_response_id(),
        )
        await self.send_message(confirmation)

    async def send_registration_error(
        self, error: str, response_id: Optional[str] = None
    ) -> None:
        """
        Send registration error (server-side).

        :param error: Error message
        :param response_id: Optional response ID for correlation
        """
        error_msg = ServerMessage(
            type=ServerMessageType.ERROR,
            status=TaskStatus.ERROR,
            error=error,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            response_id=response_id or self._generate_response_id(),
        )
        await self.send_message(error_msg)

    @staticmethod
    def _generate_response_id() -> str:
        """Generate a unique response ID."""
        import uuid

        return str(uuid.uuid4())
