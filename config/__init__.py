
"""
ALIEN² Configuration System

Modern, modular configuration system with type safety and backward compatibility.
"""

from config.config_loader import (
    ConfigLoader,
    get_alien_config,
    get_network_config,
    clear_config_cache,
)

from config.config_schemas import (
    ALIENConfig,
    NetworkConfig,
    AgentConfig,
    SystemConfig,
    RAGConfig,
)

__all__ = [
    "ConfigLoader",
    "get_alien_config",
    "get_network_config",
    "clear_config_cache",
    "ALIENConfig",
    "NetworkConfig",
    "AgentConfig",
    "SystemConfig",
    "RAGConfig",
]
