# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
cluster service for cluster Web UI.

This service handles interactions with the cluster client,
including request processing, session management, and task control.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from cluster.webui.dependencies import AppState


class clusterService:
    """
    Service for interacting with the cluster client.

    Provides methods to process requests, manage sessions, and control
    task execution in the cluster framework.
    """

    def __init__(self, app_state: AppState) -> None:
        """
        Initialize the cluster service.

        :param app_state: Application state containing cluster client references
        """
        self.app_state = app_state
        self.logger: logging.Logger = logging.getLogger(__name__)

    def is_client_available(self) -> bool:
        """
        Check if the cluster client is available.

        :return: True if client is initialized, False otherwise
        """
        return self.app_state.cluster_client is not None

    async def process_request(self, request_text: str) -> Any:
        """
        Process a user request through the cluster client.

        Updates the task name with a timestamp and counter, then processes
        the request through the cluster framework.

        :param request_text: The natural language request to process
        :return: Result from the cluster client
        :raises ValueError: If cluster client is not initialized
        """
        cluster_client = self.app_state.cluster_client
        if not cluster_client:
            raise ValueError("cluster client not initialized")

        # Increment counter and update task_name for this request with timestamp
        counter = self.app_state.increment_request_counter()
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_name = f"request_{timestamp}_{counter}"
        cluster_client.task_name = task_name

        self.logger.info(f"🚀 Processing request #{counter}: {request_text}")

        try:
            result = await cluster_client.process_request(request_text)
            self.logger.info(f"✅ Request processing completed for #{counter}")
            return result
        except Exception as e:
            self.logger.error(
                f"❌ Error processing request #{counter}: {e}", exc_info=True
            )
            raise

    async def reset_session(self) -> Dict[str, Any]:
        """
        Reset the current cluster session.

        Clears the session state and resets the request counter.

        :return: Dictionary with status, message, and timestamp
        :raises ValueError: If cluster client is not initialized
        """
        cluster_client = self.app_state.cluster_client
        if not cluster_client:
            raise ValueError("cluster client not initialized")

        self.logger.info("Resetting cluster session...")

        try:
            result = await cluster_client.reset_session()

            # Reset request counter on session reset
            self.app_state.reset_request_counter()

            self.logger.info(f"✅ Session reset completed: {result.get('message')}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to reset session: {e}", exc_info=True)
            raise

    async def create_next_session(self) -> Dict[str, Any]:
        """
        Create a new cluster session.

        Creates a new session while potentially maintaining some context
        from the previous session.

        :return: Dictionary with status, message, session_name, task_name, and timestamp
        :raises ValueError: If cluster client is not initialized
        """
        cluster_client = self.app_state.cluster_client
        if not cluster_client:
            raise ValueError("cluster client not initialized")

        self.logger.info("Creating next cluster session...")

        try:
            result = await cluster_client.create_next_session()
            self.logger.info(f"✅ Next session created: {result.get('session_name')}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to create next session: {e}", exc_info=True)
            raise

    async def stop_task_and_restart(self) -> Dict[str, Any]:
        """
        Stop the current task and restart the cluster client.

        Shuts down the cluster client to properly clean up device agent tasks,
        then reinitializes the client and creates a new session.

        :return: Dictionary with status, message, session_name, and timestamp
        :raises ValueError: If cluster client is not initialized
        """
        cluster_client = self.app_state.cluster_client
        if not cluster_client:
            raise ValueError("cluster client not initialized")

        try:
            # 🟢 Use force=True to immediately cancel any running tasks
            self.logger.info("🛑 Shutting down cluster client with force=True...")
            await cluster_client.shutdown(force=True)
            self.logger.info("✅ cluster client shutdown completed")

            # Reinitialize the client to restore device connections
            self.logger.info("🔄 Reinitializing cluster client...")
            await cluster_client.initialize()
            self.logger.info("✅ cluster client reinitialized")

            # Reset request counter on stop
            self.app_state.reset_request_counter()

            # Create a new session
            new_session_result = await cluster_client.create_next_session()
            self.logger.info(f"✅ New session created: {new_session_result}")

            return new_session_result

        except Exception as e:
            self.logger.error(
                f"Failed to stop task and restart client: {e}", exc_info=True
            )
            raise
