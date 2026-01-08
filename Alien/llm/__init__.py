# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

from enum import Enum


class AgentType(str, Enum):
    HOST = "HOST_AGENT"
    APP = "APP_AGENT"
    network = "network_AGENT"
    EVALUATION = "EVALUATION_AGENT"
    OPERATOR = "OPERATOR"
    PREFILL = "PREFILL_AGENT"
    FILTER = "FILTER_AGENT"
    BACKUP = "BACKUP_AGENT"
