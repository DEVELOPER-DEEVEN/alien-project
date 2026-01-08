# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
AIP Endpoints

Provides endpoint implementations for Device Server, Device Client, and network Client.
"""

from .base import AIPEndpoint
from .client_endpoint import DeviceClientEndpoint
from .network_endpoint import networkEndpoint
from .server_endpoint import DeviceServerEndpoint

__all__ = [
    "AIPEndpoint",
    "DeviceServerEndpoint",
    "DeviceClientEndpoint",
    "networkEndpoint",
]
