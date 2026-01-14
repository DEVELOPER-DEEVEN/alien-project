# Third-Party Agent Configuration (third_party.yaml)

Configure third-party agents that extend ALIEN²'s capabilities beyond Windows GUI automation, such as LinuxAgent for CLI operations and HardwareAgent for physical device control.

---

## Overview

The `third_party.yaml` file configures external agents that integrate with ALIEN² to provide specialized capabilities. These agents work alongside the standard HostAgent and AppAgent to handle tasks that require non-GUI interactions.

**File Location**: `config/alien/third_party.yaml`

**Advanced Feature:** Third-party agent configuration is an **advanced optional feature**. Most users only need the core agents (HostAgent, AppAgent). Configure third-party agents only when you need specialized capabilities.

!!!tip "Creating Custom Third-Party Agents"
    Want to build your own third-party agent? See the **[Creating Custom Third-Party Agents Tutorial](../../tutorials/creating_third_party_agents.md)** for a complete step-by-step guide using HardwareAgent as an example.

---

## Quick Start

### Default Configuration

```yaml
# Enable third-party agents
ENABLED_THIRD_PARTY_AGENTS: ["LinuxAgent"]

THIRD_PARTY_AGENT_CONFIG:
  LinuxAgent:
    AGENT_NAME: "LinuxAgent"
    APPAGENT_PROMPT: "alien/prompts/third_party/linux_agent.yaml"
    APPAGENT_EXAMPLE_PROMPT: "alien/prompts/third_party/linux_agent_example.yaml"
    INTRODUCTION: "For Linux Use Only."
```

### Disable All Third-Party Agents

```yaml
# Disable all third-party agents
ENABLED_THIRD_PARTY_AGENTS: []
```

---

## Available Third-Party Agents

### LinuxAgent

**Purpose**: Execute Linux CLI commands and server operations.

!!!info "ALIEN³ Integration"
    LinuxAgent is used by **ALIEN³ Network** to orchestrate Linux devices as sub-agents in multi-device workflows. When Network routes a task to a Linux device, it uses LinuxAgent to execute commands via CLI.

**Configuration**:
```yaml
THIRD_PARTY_AGENT_CONFIG:
  LinuxAgent:
    AGENT_NAME: "LinuxAgent"
    APPAGENT_PROMPT: "alien/prompts/third_party/linux_agent.yaml"
    APPAGENT_EXAMPLE_PROMPT: "alien/prompts/third_party/linux_agent_example.yaml"
    INTRODUCTION: "For Linux Use Only."
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `AGENT_NAME` | String | Agent identifier (must be "LinuxAgent") |
| `APPAGENT_PROMPT` | String | Path to main prompt template |
| `APPAGENT_EXAMPLE_PROMPT` | String | Path to example prompt template |
| `INTRODUCTION` | String | Agent description for LLM context |

**When to Enable**:
- [OK] Using ALIEN³ Network with Linux devices
- [OK] Need to execute Linux CLI commands
- [OK] Managing Linux servers from Windows
- [OK] Cross-platform automation workflows

**Related Documentation**:
- [Linux Agent as Network Device](../../linux/as_network_device.md)
- [Linux Agent Quick Start](../../getting_started/quick_start_linux.md)

---

### HardwareAgent

**Purpose**: Control physical hardware components (robotic arms, USB devices, etc.).

!!!warning "Experimental Feature"
    HardwareAgent is an experimental feature for controlling physical hardware. Requires specialized hardware setup and is not commonly used.

**Configuration**:
```yaml
THIRD_PARTY_AGENT_CONFIG:
  HardwareAgent:
    VISUAL_MODE: True
    AGENT_NAME: "HardwareAgent"
    APPAGENT_PROMPT: "alien/prompts/share/base/app_agent.yaml"
    APPAGENT_EXAMPLE_PROMPT: "alien/prompts/examples/visual/app_agent_example.yaml"
    API_PROMPT: "alien/prompts/third_party/hardware_agent_api.yaml"
    INTRODUCTION: "The HardwareAgent is used to manipulate hardware components of the computer without using GUI, such as robotic arms for keyboard input and mouse control, plug and unplug devices such as USB drives, and other hardware-related tasks."
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `VISUAL_MODE` | Boolean | Enable visual mode (screenshot understanding) |
| `AGENT_NAME` | String | Agent identifier (must be "HardwareAgent") |
| `APPAGENT_PROMPT` | String | Path to main prompt template |
| `APPAGENT_EXAMPLE_PROMPT` | String | Path to example prompt template |
| `API_PROMPT` | String | Path to hardware API prompt template |
| `INTRODUCTION` | String | Agent description for LLM context |

**When to Enable**:
- [OK] Using robotic arms for physical input
- [OK] Automated USB device management
- [OK] Physical hardware testing/automation
- [OK] Research projects with hardware control

**Related Documentation**:
- [Creating Custom Third-Party Agents](../../tutorials/creating_third_party_agents.md) - Tutorial using HardwareAgent as example

---

## Configuration Fields

### ENABLED_THIRD_PARTY_AGENTS

**Type**: `List[String]`  
**Default**: `[]` (no third-party agents enabled)

List of third-party agent names to enable. Only agents listed here will be loaded and available.

**Options**:
- `"LinuxAgent"` - Linux CLI execution
- `"HardwareAgent"` - Physical hardware control

**Examples**:
```yaml
# Enable LinuxAgent only (recommended for ALIEN³)
ENABLED_THIRD_PARTY_AGENTS: ["LinuxAgent"]

# Enable both agents
ENABLED_THIRD_PARTY_AGENTS: ["LinuxAgent", "HardwareAgent"]

# Disable all third-party agents
ENABLED_THIRD_PARTY_AGENTS: []
```

### THIRD_PARTY_AGENT_CONFIG

**Type**: `Dict[String, Dict]`

Configuration dictionary for each third-party agent. Each agent has its own configuration block.

**Structure**:
```yaml
THIRD_PARTY_AGENT_CONFIG:
  AgentName:
    AGENT_NAME: "AgentName"
    # Agent-specific fields...
```

---

## Complete Configuration Example

### For ALIEN³ Network (Recommended)

```yaml
# Enable LinuxAgent for ALIEN³ Network multi-device orchestration
ENABLED_THIRD_PARTY_AGENTS: ["LinuxAgent"]

THIRD_PARTY_AGENT_CONFIG:
  LinuxAgent:
    AGENT_NAME: "LinuxAgent"
    APPAGENT_PROMPT: "alien/prompts/third_party/linux_agent.yaml"
    APPAGENT_EXAMPLE_PROMPT: "alien/prompts/third_party/linux_agent_example.yaml"
    INTRODUCTION: "For Linux Use Only."
```

### With Hardware Support

```yaml
# Enable both Linux and Hardware agents
ENABLED_THIRD_PARTY_AGENTS: ["LinuxAgent", "HardwareAgent"]

THIRD_PARTY_AGENT_CONFIG:
  LinuxAgent:
    AGENT_NAME: "LinuxAgent"
    APPAGENT_PROMPT: "alien/prompts/third_party/linux_agent.yaml"
    APPAGENT_EXAMPLE_PROMPT: "alien/prompts/third_party/linux_agent_example.yaml"
    INTRODUCTION: "For Linux Use Only."
  
  HardwareAgent:
    VISUAL_MODE: True
    AGENT_NAME: "HardwareAgent"
    APPAGENT_PROMPT: "alien/prompts/share/base/app_agent.yaml"
    APPAGENT_EXAMPLE_PROMPT: "alien/prompts/examples/visual/app_agent_example.yaml"
    API_PROMPT: "alien/prompts/third_party/hardware_agent_api.yaml"
    INTRODUCTION: "The HardwareAgent is used to manipulate hardware components of the computer without using GUI, such as robotic arms for keyboard input and mouse control, plug and unplug devices such as USB drives, and other hardware-related tasks."
```

### Minimal (No Third-Party Agents)

```yaml
# Disable all third-party agents (default for standalone ALIEN²)
ENABLED_THIRD_PARTY_AGENTS: []
```

---

## ALIEN³ Network Integration

When using ALIEN³ Network for multi-device orchestration, LinuxAgent must be enabled to support Linux devices.

### Setup for Network

**Step 1**: Enable LinuxAgent in `config/alien/third_party.yaml`

```yaml
ENABLED_THIRD_PARTY_AGENTS: ["LinuxAgent"]

THIRD_PARTY_AGENT_CONFIG:
  LinuxAgent:
    AGENT_NAME: "LinuxAgent"
    APPAGENT_PROMPT: "alien/prompts/third_party/linux_agent.yaml"
    APPAGENT_EXAMPLE_PROMPT: "alien/prompts/third_party/linux_agent_example.yaml"
    INTRODUCTION: "For Linux Use Only."
```

**Step 2**: Configure Linux devices in `config/network/devices.yaml`

```yaml
devices:
  - device_id: "linux_server_1"
    server_url: "ws://192.168.1.100:5001/ws"
    os: "linux"
    capabilities:
      - "server"
      - "cli"
      - "database"
```

**Step 3**: Start Linux Agent components

See [Linux Agent as Network Device](../../linux/as_network_device.md) for complete setup.

---

## Programmatic Access

```python
from config.config_loader import get_alien_config

config = get_alien_config()

# Check which third-party agents are enabled
enabled_agents = config.ENABLED_THIRD_PARTY_AGENTS
print(f"Enabled third-party agents: {enabled_agents}")

# Access agent configuration
if "LinuxAgent" in enabled_agents:
    linux_config = config.THIRD_PARTY_AGENT_CONFIG["LinuxAgent"]
    print(f"LinuxAgent prompt: {linux_config['APPAGENT_PROMPT']}")

# Check if specific agent is enabled
linux_enabled = "LinuxAgent" in config.ENABLED_THIRD_PARTY_AGENTS
print(f"LinuxAgent enabled: {linux_enabled}")
```

---

## Adding Custom Third-Party Agents

You can add your own third-party agents by following the patterns described below. For a complete tutorial, see **[Creating Custom Third-Party Agents](../../tutorials/creating_third_party_agents.md)**.

### Quick Overview

### Step 1: Create Agent Implementation

```python
# alien/agents/third_party/my_agent.py
class MyCustomAgent:
    def __init__(self, config):
        self.config = config
        # Initialize your agent
```

### Step 2: Add Configuration

```yaml
ENABLED_THIRD_PARTY_AGENTS: ["MyCustomAgent"]

THIRD_PARTY_AGENT_CONFIG:
  MyCustomAgent:
    AGENT_NAME: "MyCustomAgent"
    APPAGENT_PROMPT: "alien/prompts/third_party/my_agent.yaml"
    APPAGENT_EXAMPLE_PROMPT: "alien/prompts/third_party/my_agent_example.yaml"
    INTRODUCTION: "Custom agent description."
    # Your custom fields
    CUSTOM_FIELD: "value"
```

### Step 3: Register Agent

Add your agent to the third-party agent registry in ALIEN²'s agent loader.

---

## Troubleshooting

### Issue 1: LinuxAgent Not Working

!!!bug "Error Message"
    ```
    LinuxAgent not found or not enabled
    ```
    
    **Solution**: Check configuration
    ```yaml
    # Verify LinuxAgent is in enabled list
    ENABLED_THIRD_PARTY_AGENTS: ["LinuxAgent"]
    ```

### Issue 2: Prompt Files Not Found

!!!bug "Error Message"
    ```
    FileNotFoundError: alien/prompts/third_party/linux_agent.yaml
    ```
    
    **Solution**: Verify prompt files exist
    ```powershell
    # Check if prompt files exist
    Test-Path "alien\prompts\third_party\linux_agent.yaml"
    Test-Path "alien\prompts\third_party\linux_agent_example.yaml"
    ```

### Issue 3: Agent Configuration Not Loaded

!!!bug "Symptom"
    Third-party agent configuration changes not taking effect
    
    **Solution**: Restart ALIEN² application
    ```powershell
    # Configuration is loaded at startup
    # Restart ALIEN² to apply changes
    ```

---

## Best Practices

!!!tip "Recommendations"
    - [OK] **Enable only what you need** - Don't enable agents you're not using
    - [OK] **For ALIEN³ Network** - Always enable LinuxAgent when using Linux devices
    - [OK] **Keep prompts up to date** - Ensure prompt files exist and are current
    - [OK] **Document custom agents** - Add clear introduction text for LLM context
    - [OK] **Test configurations** - Verify agents load correctly after configuration changes

!!!danger "Warnings"
    - [FAIL] **Don't enable HardwareAgent** without proper hardware setup
    - [FAIL] **Don't modify AGENT_NAME** - Must match the agent class name
    - [FAIL] **Don't delete prompt files** - Agents will fail to initialize

---

## Related Documentation

- **[Creating Custom Third-Party Agents](../../tutorials/creating_third_party_agents.md)** - Complete tutorial for building third-party agents
- **[Linux Agent as Network Device](../../linux/as_network_device.md)** - Using LinuxAgent in ALIEN³
- **[Linux Agent Quick Start](../../getting_started/quick_start_linux.md)** - Setting up Linux Agent
- **[Agent Configuration](./agents_config.md)** - Core agent LLM settings
- **[Network Devices Configuration](./network_devices.md)** - Multi-device setup

---

## Summary

!!!success "Key Takeaways"
    [OK] **third_party.yaml is optional** - Only needed for specialized agents  
    [OK] **LinuxAgent for ALIEN³** - Required when using Linux devices in Network  
    [OK] **HardwareAgent is experimental** - For physical hardware control  
    [OK] **Enable selectively** - Only enable agents you actually use  
    [OK] **Configuration is simple** - Just add agent names to enabled list  
    
    **Extend ALIEN² with specialized capabilities!** [CONFIG]
