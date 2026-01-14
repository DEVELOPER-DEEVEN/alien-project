"""
Unified agent configuration getter for LLM calls.

This module provides a unified way to get agent configurations from different
config files based on AgentType.
"""

from typing import Dict, Any
from alien.llm import AgentType
from config.config_loader import get_alien_config, get_network_config


def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """
    Get agent configuration based on agent type.

    Maps AgentType to the appropriate configuration file:
    - HOST_AGENT, APP_AGENT, BACKUP_AGENT, EVALUATION_AGENT, OPERATOR → config/alien/agents.yaml
    - ORION_AGENT → config/network/agent.yaml
    - Third-party agents → config/alien/third_party.yaml (future)

    :param agent_type: AgentType enum value (e.g., AgentType.HOST, AgentType.ORION)
    :return: Agent configuration dictionary
    :raises ValueError: If agent type is not supported
    """

    # ALIEN agents (from config/alien/agents.yaml)
    if agent_type in [
        AgentType.HOST,
        AgentType.APP,
        AgentType.BACKUP,
        AgentType.EVALUATION,
        AgentType.OPERATOR,
        AgentType.PREFILL,
        AgentType.FILTER,
    ]:
        alien_config = get_alien_config()

        # Map AgentType to typed config attributes
        agent_config_map = {
            AgentType.HOST: alien_config.host_agent,
            AgentType.APP: alien_config.app_agent,
            AgentType.BACKUP: alien_config.backup_agent,
            AgentType.EVALUATION: alien_config.evaluation_agent,
            AgentType.OPERATOR: alien_config.operator,
            AgentType.PREFILL: alien_config.host_agent,  # Prefill uses HOST_AGENT config
            AgentType.FILTER: alien_config.host_agent,  # Filter uses HOST_AGENT config
        }

        agent_config = agent_config_map.get(agent_type)
        if agent_config is None:
            raise ValueError(f"Agent type {agent_type} not found in ALIEN config")

        # Convert to dict for backward compatibility
        return _config_to_dict(agent_config)

    # Network orion agent (from config/network/agent.yaml)
    elif agent_type == AgentType.ORION:
        network_config = get_network_config()
        orion_agent_config = network_config.agent.orion_agent

        if orion_agent_config is None:
            raise ValueError("ORION_AGENT not found in Network config")

        return _config_to_dict(orion_agent_config)

    else:
        raise ValueError(f"Unsupported agent type: {agent_type}")


def _config_to_dict(config_obj: Any) -> Dict[str, Any]:
    """
    Convert config object to dictionary with both uppercase and lowercase keys.

    This ensures backward compatibility with code expecting dict access while
    also supporting the new typed config objects.

    :param config_obj: Config object (AgentConfig or similar)
    :return: Dictionary representation with uppercase keys
    """
    if hasattr(config_obj, "to_dict"):
        return config_obj.to_dict()

    # Fallback: create dict from object attributes
    config_dict = {}
    for attr in dir(config_obj):
        if not attr.startswith("_") and not callable(getattr(config_obj, attr)):
            value = getattr(config_obj, attr)
            # Store with uppercase key for compatibility
            config_dict[attr.upper()] = value

    return config_dict


class AgentConfigAccessor:
    """
    Wrapper class that provides both dict-style and attribute access to agent configs.

    This class wraps the typed config objects to provide backward compatibility
    with code expecting dictionary access (config['API_TYPE']) while also
    supporting modern attribute access (config.api_type).
    """

    def __init__(self, config_obj: Any):
        """
        Initialize accessor with config object.

        :param config_obj: Config object (AgentConfig or similar)
        """
        self._config_obj = config_obj
        self._dict_cache = None

    def __getitem__(self, key: str) -> Any:
        """Support dict-style access: config['API_TYPE']"""
        # Try direct attribute access on config object (handles uppercase automatically)
        try:
            return getattr(self._config_obj, key)
        except AttributeError:
            pass

        # Try lowercase
        try:
            return getattr(self._config_obj, key.lower())
        except AttributeError:
            pass

        # Fallback to dict
        if self._dict_cache is None:
            self._dict_cache = _config_to_dict(self._config_obj)

        if key in self._dict_cache:
            return self._dict_cache[key]

        raise KeyError(f"Config key '{key}' not found")

    def __getattr__(self, name: str) -> Any:
        """Support attribute access: config.api_type"""
        if name.startswith("_"):
            return object.__getattribute__(self, name)
        return getattr(self._config_obj, name)

    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'API_TYPE' in config"""
        try:
            self[key]
            return True
        except (KeyError, AttributeError):
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get(): config.get('API_TYPE', 'default')"""
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        if self._dict_cache is None:
            self._dict_cache = _config_to_dict(self._config_obj)
        return self._dict_cache.copy()
