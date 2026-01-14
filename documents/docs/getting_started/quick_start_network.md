# Quick Start Guide - ALIEN³ Network

Welcome to **ALIEN³ Network** – the Multi-Device AgentOS! This guide will help you orchestrate complex cross-platform workflows across multiple devices in just a few steps.

**What is ALIEN³ Network?**

ALIEN³ Network is a multi-tier orchestration framework that coordinates distributed agents across Windows and Linux devices. It enables complex workflows that span multiple machines, combining desktop automation, server operations, and heterogeneous device capabilities into unified task execution.

---

## 🛠️ Step 1: Installation

### Requirements

- **Python** >= 3.10
- **Windows OS** >= 10 (for Windows agents)
- **Linux** (for Linux agents)
- **Git** (for cloning the repository)
- **Network connectivity** between all devices

### Installation Steps

```powershell
# [Optional] Create conda environment
conda create -n alien python=3.10
conda activate alien

# Clone the repository
git clone https://github.com/DEVELOPER-DEEVEN/alien-project.git
cd ALIEN

# Install dependencies
pip install -r requirements.txt
```

> **💡 Tip:** If you want to use Qwen as your LLM, uncomment the related libraries in `requirements.txt` before installing.

---

## ⚙️ Step 2: Configure OrionAgent LLM

ALIEN³ Network uses a **OrionAgent** that orchestrates all device agents. You need to configure its LLM settings.

### Configure Orion Agent

```powershell
# Copy template to create orion agent config
copy config\network\agent.yaml.template config\network\agent.yaml
notepad config\network\agent.yaml   # Edit your LLM API credentials
```

**Configuration File Location:**
```
config/network/
├── agent.yaml.template    # Template - COPY THIS
├── agent.yaml             # Your config with API keys (DO NOT commit)
└── devices.yaml           # Device pool configuration (Step 4)
```

### LLM Configuration Examples

#### Azure OpenAI Configuration

**Edit `config/network/agent.yaml`:**

```yaml
ORION_AGENT:
  REASONING_MODEL: false
  API_TYPE: "aoai"
  API_BASE: "https://YOUR_RESOURCE.openai.azure.com"
  API_KEY: "YOUR_AOAI_KEY"
  API_VERSION: "2024-02-15-preview"
  API_MODEL: "gpt-4o"
  API_DEPLOYMENT_ID: "YOUR_DEPLOYMENT_ID"
```

> **ℹ️ More LLM Options:** Network supports various LLM providers including Qwen, Gemini, Claude, DeepSeek, and more. See the [Model Configuration Guide](../configuration/models/overview.md) for complete details.

---
  
  # Prompt configurations (use defaults)
  ORION_CREATION_PROMPT: "network/prompts/orion/share/orion_creation.yaml"
  ORION_EDITING_PROMPT: "network/prompts/orion/share/orion_editing.yaml"
  ORION_CREATION_EXAMPLE_PROMPT: "network/prompts/orion/examples/orion_creation_example.yaml"
  ORION_EDITING_EXAMPLE_PROMPT: "network/prompts/orion/examples/orion_editing_example.yaml"
```

#### OpenAI Configuration

```yaml
ORION_AGENT:
  REASONING_MODEL: false
  API_TYPE: "openai"
  API_BASE: "https://api.openai.com/v1/chat/completions"
  API_KEY: "sk-YOUR_KEY_HERE"
  API_VERSION: "2025-02-01-preview"
  API_MODEL: "gpt-4o"
  
  # Prompt configurations (use defaults)
  ORION_CREATION_PROMPT: "network/prompts/orion/share/orion_creation.yaml"
  ORION_EDITING_PROMPT: "network/prompts/orion/share/orion_editing.yaml"
  ORION_CREATION_EXAMPLE_PROMPT: "network/prompts/orion/examples/orion_creation_example.yaml"
  ORION_EDITING_EXAMPLE_PROMPT: "network/prompts/orion/examples/orion_editing_example.yaml"
```

!!!info "More LLM Options"
    Network supports various LLM providers including **Qwen**, **Gemini**, **Claude**, **DeepSeek**, and more. See the **[Model Configuration Guide](../configuration/models/overview.md)** for complete details.

---

## 🖥️ Step 3: Set Up Device Agents

Network orchestrates **device agents** that execute tasks on individual machines. You need to start the appropriate device agents based on your needs.

### Supported Device Agents

| Device Agent | Platform | Documentation | Use Cases |
|--------------|----------|---------------|-----------|
| **WindowsAgent (ALIEN²)** | Windows 10/11 | [ALIEN² as Network Device](../alien2/as_network_device.md) | Desktop automation, Office apps, GUI operations |
| **LinuxAgent** | Linux | [Linux as Network Device](../linux/as_network_device.md) | Server management, CLI operations, log analysis |
| **MobileAgent** | Android | [Mobile as Network Device](../mobile/as_network_device.md) | Mobile app automation, UI testing, device control |

> **💡 Choose Your Devices:** You can use any combination of Windows, Linux, and Mobile agents. Network will intelligently route tasks based on device capabilities.

### Quick Setup Overview

For each device agent you want to use, you need to:

1. **Start the Device Agent Server** (manages tasks)
2. **Start the Device Agent Client** (executes commands)
3. **Start MCP Services** (provides automation tools, if needed)

**Detailed Setup Instructions:**

- **For Windows devices (ALIEN²):** See [ALIEN² as Network Device](../alien2/as_network_device.md) for complete step-by-step instructions.
- **For Linux devices:** See [Linux as Network Device](../linux/as_network_device.md) for complete step-by-step instructions.
- **For Mobile devices:** See [Mobile as Network Device](../mobile/as_network_device.md) for complete step-by-step instructions.

### Example: Quick Windows Device Setup

**On your Windows machine:**

```powershell
# Terminal 1: Start ALIEN² Server
python -m alien.server.app --port 5000

# Terminal 2: Start ALIEN² Client (connect to server)
python -m alien.client.client `
  --ws `
  --ws-server ws://localhost:5000/ws `
  --client-id windows_device_1 `
  --platform windows
```

> **💡 Important:** Always include `--platform windows` for Windows devices and `--platform linux` for Linux devices!

### Example: Quick Linux Device Setup

**On your Linux machine:**

```bash
# Terminal 1: Start Device Agent Server
python -m alien.server.app --port 5001

# Terminal 2: Start Linux Client (connect to server)
python -m alien.client.client \
  --ws \
  --ws-server ws://localhost:5001/ws \
  --client-id linux_device_1 \
  --platform linux

# Terminal 3: Start HTTP MCP Server (for Linux tools)
python -m alien.client.mcp.http_servers.linux_mcp_server
```

> **💡 Note:** For detailed Mobile Agent setup with ADB and Android device configuration, see [Mobile Quick Start](quick_start_mobile.md).

---

## 🔌 Step 4: Configure Device Pool

After starting your device agents, register them in Network's device pool configuration.

### Option 1: Add Devices via Configuration File

### Edit Device Configuration

```powershell
notepad config\network\devices.yaml
```

### Example Device Pool Configuration

```yaml
# Device Configuration for Network
# Each device agent must be registered here

devices:
  # Windows Device (ALIEN²)
  - device_id: "windows_device_1"              # Must match --client-id
    server_url: "ws://localhost:5000/ws"       # Must match server WebSocket URL
    os: "windows"
    capabilities:
      - "desktop_automation"
      - "office_applications"
      - "excel"
      - "word"
      - "outlook"
      - "email"
      - "web_browsing"
    metadata:
      os: "windows"
      version: "11"
      performance: "high"
      installed_apps:
        - "Microsoft Excel"
        - "Microsoft Word"
        - "Microsoft Outlook"
        - "Google Chrome"
      description: "Primary Windows desktop for office automation"
    auto_connect: true
    max_retries: 5

  # Linux Device
  - device_id: "linux_device_1"                # Must match --client-id
    server_url: "ws://localhost:5001/ws"       # Must match server WebSocket URL
    os: "linux"
    capabilities:
      - "server_management"
      - "log_analysis"
      - "file_operations"
      - "database_operations"
    metadata:
      os: "linux"
      performance: "medium"
      logs_file_path: "/var/log/myapp/app.log"
      dev_path: "/home/user/projects/"
      warning_log_pattern: "WARN"
      error_log_pattern: "ERROR|FATAL"
      description: "Development server for backend operations"
    auto_connect: true
    max_retries: 5

  # Mobile Device (Android)
  - device_id: "mobile_phone_1"                # Must match --client-id
    server_url: "ws://localhost:5001/ws"       # Must match server WebSocket URL
    os: "mobile"
    capabilities:
      - "mobile"
      - "android"
      - "ui_automation"
      - "messaging"
      - "camera"
      - "location"
    metadata:
      os: "mobile"
      device_type: "phone"
      android_version: "13"
      screen_size: "1080x2400"
      installed_apps:
        - "com.android.chrome"
        - "com.google.android.apps.maps"
        - "com.whatsapp"
      description: "Android phone for mobile automation and testing"
    auto_connect: true
    max_retries: 5
```

> **⚠️ Critical:** IDs and URLs must match exactly:
> 
> - `device_id` must exactly match the `--client-id` flag
> - `server_url` must exactly match the server WebSocket URL
> - Otherwise, Network cannot control the device!

**Complete Configuration Guide:** For detailed information about all configuration options, capabilities, and metadata, see [Network Devices Configuration](../configuration/system/network_devices.md).

### Option 2: Add Devices via WebUI (When Using --webui Mode)

If you start Network with the `--webui` flag (see Step 5), you can add new device agents directly through the web interface without editing configuration files.

**Steps to Add Device via WebUI:**

1. **Launch Network with WebUI** (as shown in Step 5):
   ```powershell
   python -m network --webui
   ```

2. **Click the "+" button** in the top-right corner of the Device Agent panel (left sidebar)

3. **Fill in the device information** in the Add Device Modal:

<div align="center">
  <img src="../img/add_device.png" alt="Add Device Modal" width="70%">
  <p><em>➕ Add Device Modal - Register new device agents through the WebUI</em></p>
</div>

**Required Fields:**
- **Device ID**: Unique identifier (must match `--client-id` in device agent)
- **Server URL**: WebSocket endpoint (e.g., `ws://localhost:5000/ws`)
- **Operating System**: Select Windows, Linux, macOS, or enter custom OS
- **Capabilities**: Add at least one capability (e.g., `excel`, `outlook`, `log_analysis`)

**Optional Fields:**
- **Auto-connect**: Enable to automatically connect after registration (default: enabled)
- **Max Retries**: Maximum connection attempts (default: 5)
- **Metadata**: Add custom key-value pairs (e.g., `region: us-east-1`)

**Benefits of WebUI Device Management:**
- ✅ No need to manually edit YAML files
- ✅ Real-time validation of device ID uniqueness
- ✅ Automatic connection after registration
- ✅ Immediate visual feedback on device status
- ✅ Form validation prevents configuration errors

**After Adding:**
The device will be:
1. Saved to `config/network/devices.yaml` automatically
2. Registered with Network's Device Manager
3. Connected automatically (if auto-connect is enabled)
4. Displayed in the Device Agent panel with real-time status

> **💡 Tip:** You can add devices while Network is running! No need to restart the server.

---

## 🎉 Step 5: Start ALIEN³ Network

With all device agents running and configured, you can now launch Network!

### Pre-Launch Checklist

Before starting Network, ensure:

1. ✅ All Device Agent Servers are running
2. ✅ All Device Agent Clients are connected
3. ✅ MCP Services are running (for Linux devices)
4. ✅ LLM configured in `config/network/agent.yaml`
5. ✅ Devices configured in `config/network/devices.yaml`
6. ✅ Network connectivity between all components

### 🎨 Launch Network - WebUI Mode (Recommended)

Start Network with an interactive web interface for real-time orion visualization and monitoring:

```powershell
# Assume you are in the cloned ALIEN folder
python -m network --webui
```

This will start the Network server with WebUI and automatically open your browser to the interactive interface:

<div align="center">
  <img src="../img/webui.png" alt="ALIEN³ Network WebUI Interface" width="90%">
  <p><em>🎨 Network WebUI - Interactive orion visualization and chat interface</em></p>
</div>

**WebUI Features:**

- 🗣️ **Chat Interface**: Submit requests and interact with OrionAgent in real-time
- 📊 **Live DAG Visualization**: Watch task orion formation and execution
- 🎯 **Task Status Tracking**: Monitor each TaskStar's progress and completion
- 🔄 **Dynamic Updates**: See orion evolution as tasks complete
- 📱 **Responsive Design**: Works on desktop and tablet devices

**Default URL:** `http://localhost:8000` (automatically finds next available port if 8000 is occupied)

---

### 💬 Launch Network - Interactive Terminal Mode

Start Network in interactive mode where you can enter requests dynamically:

```powershell
# Assume you are in the cloned ALIEN folder
python -m network --interactive
```

**Expected Output:**

```
🌌 Welcome to ALIEN³ Network Framework
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Multi-Device AI Orchestration System

📡 Initializing Network...
✅ OrionAgent initialized
✅ Connected to device: windows_device_1 (windows)
✅ Connected to device: linux_device_1 (linux)

🌟 Network Ready - 2 devices online

Please enter your request 🛸:
```

---

### ⚡ Launch Network - Direct Request Mode

Invoke Network with a specific request directly:

```powershell
python -m network --request "Your task description here"
```

**Example:**

```powershell
python -m network --request "Generate a sales report from the database and create an Excel dashboard"
```

---

### 🎬 Launch Network - Demo Mode

Run Network in demo mode to see example workflows:

```powershell
python -m network --demo
```

---

## 🎯 Step 6: Try Your First Multi-Device Workflow

### Example 1: Simple Cross-Platform Task

**User Request:**
> "Check the server logs for errors and email me a summary"

**Network orchestrates:**

1. **Linux Device**: Analyze server logs for error patterns
2. **Windows Device**: Open Outlook, create email with log summary
3. **Windows Device**: Send email

**How to run:**

```powershell
python -m network --request "Check the server logs for errors and email me a summary"
```

### Example 2: Data Processing Pipeline

**User Request:**
> "Export sales data from the database, create an Excel report with charts, and email it to the team"

**Network orchestrates:**

1. **Linux Device**: Query database, export CSV
2. **Windows Device**: Open Excel, import CSV, create charts
3. **Windows Device**: Open Outlook, attach Excel file, send email

**How to run:**

```powershell
python -m network --request "Export sales data from the database, create an Excel report with charts, and email it to the team"
```

### Example 3: Multi-Server Monitoring

**User Request:**
> "Check all servers for disk usage and alert if any are above 80%"

**Network orchestrates:**

1. **Linux Device 1**: Check disk usage on server 1
2. **Linux Device 2**: Check disk usage on server 2
3. **Network**: Aggregate results, check thresholds
4. **Windows Device**: Send alert email if needed

---

## 📔 Step 7: Understanding Device Routing

Network uses **capability-based routing** to intelligently assign tasks to appropriate devices.

### How Network Selects Devices

| Factor | Description | Example |
|--------|-------------|---------|
| **Capabilities** | Matches task requirements | `"excel"` → Windows device with Excel |
| **OS Requirement** | Platform-specific tasks | Linux commands → Linux device |
| **Metadata** | Device-specific context | Email task → device with Outlook |
| **Status** | Online and healthy devices only | Skips offline devices |

### Example Task Decomposition

**User Request:**
> "Prepare monthly reports and distribute to team"

**Network Decomposition:**

```yaml
Subtask 1:
  Description: "Extract monthly data from database"
  Target Device: linux_device_1
  Reason: Has "database_operations" capability

Subtask 2:
  Description: "Create Excel report with visualizations"
  Target Device: windows_device_1
  Reason: Has "excel" capability

Subtask 3:
  Description: "Email reports to distribution list"
  Target Device: windows_device_1
  Reason: Has "email" and "outlook" capabilities
```

---

## 🔄 Step 8: Execution Logs

Network automatically saves execution logs, task graphs, and device traces for debugging and analysis.

**Log Location:**

```
./logs/<session_name>/
```

**Log Contents:**

| File/Folder | Description |
|-------------|-------------|
| `orion/` | DAG visualization and task decomposition |
| `device_logs/` | Individual device execution logs |
| `screenshots/` | Screenshots from Windows devices (if enabled) |
| `task_results/` | Task execution results |
| `request_response.log` | Complete LLM request/response logs |

> **Analyzing Logs:** Use the logs to debug task routing, identify bottlenecks, replay execution flow, and analyze orchestration decisions.

---

## 🔧 Advanced Configuration

### Custom Session Name

```powershell
python -m network --request "Your task" --session-name "my_project"
```

### Custom Output Directory

```powershell
python -m network --request "Your task" --output-dir "./custom_results"
```

### Debug Mode

```powershell
python -m network --interactive --log-level DEBUG
```

### Limit Maximum Rounds

```powershell
python -m network --interactive --max-rounds 20
```

---

## ❓ Troubleshooting

### Issue 1: Device Not Appearing in Network

**Error:** Device not found in configuration

```log
ERROR - Device 'windows_device_1' not found in configuration
```

**Solutions:**

1. Verify `devices.yaml` configuration:
   ```powershell
   notepad config\network\devices.yaml
   ```

2. Check device ID matches:
   - In `devices.yaml`: `device_id: "windows_device_1"`
   - In client command: `--client-id windows_device_1`

3. Check server URL matches:
   - In `devices.yaml`: `server_url: "ws://localhost:5000/ws"`
   - In client command: `--ws-server ws://localhost:5000/ws`

### Issue 2: Device Agent Not Connecting

**Error:** Connection refused

```log
ERROR - [WS] Failed to connect to ws://localhost:5000/ws
Connection refused
```

**Solutions:**

1. Verify server is running:
   ```powershell
   curl http://localhost:5000/api/health
   ```

2. Check port number is correct:
   - Server: `--port 5000`
   - Client: `ws://localhost:5000/ws`

3. Ensure platform flag is set:
   ```powershell
   # For Windows devices
   --platform windows
   
   # For Linux devices
   --platform linux
   ```

### Issue 3: Network Cannot Find Orion Agent Config

**Error:** Configuration file not found

```log
ERROR - Cannot find config/network/agent.yaml
```

**Solution:**
```powershell
# Copy template to create configuration file
copy config\network\agent.yaml.template config\network\agent.yaml

# Edit with your LLM credentials
notepad config\network\agent.yaml
```

### Issue 4: Task Not Routed to Expected Device

**Issue:** Wrong device selected for task

**Diagnosis:** Check device capabilities in `devices.yaml`:

```yaml
capabilities:
  - "desktop_automation"
  - "office_applications"
  - "excel"  # Required for Excel tasks
  - "outlook"  # Required for email tasks
```

**Solution:** Add appropriate capabilities to your device configuration.

---

## 📚 Additional Resources

### Core Documentation

**Architecture & Concepts:**

- [Network Overview](../network/overview.md) - System architecture and design principles
- [Orion Orchestrator](../network/orion_orchestrator/overview.md) - Task orchestration and DAG management
- [Agent Interaction Protocol (AIP)](../aip/overview.md) - Communication substrate

### Device Agent Setup

**Device Agent Guides:**

- [ALIEN² as Network Device](../alien2/as_network_device.md) - Complete Windows device setup
- [Linux as Network Device](../linux/as_network_device.md) - Complete Linux device setup
- [Mobile as Network Device](../mobile/as_network_device.md) - Complete Android device setup
- [ALIEN² Overview](../alien2/overview.md) - Windows desktop automation capabilities
- [Linux Agent Overview](../linux/overview.md) - Linux server automation capabilities
- [Mobile Agent Overview](../mobile/overview.md) - Android mobile automation capabilities

### Configuration

**Configuration Guides:**

- [Network Devices Configuration](../configuration/system/network_devices.md) - Complete device pool configuration
- [Network Orion Configuration](../configuration/system/network_orion.md) - Runtime settings
- [Agents Configuration](../configuration/system/agents_config.md) - LLM settings for all agents
- [Model Configuration](../configuration/models/overview.md) - Supported LLM providers

### Advanced Features

**Advanced Topics:**

- [Task Orion](../network/orion/task_orion.md) - DAG-based task planning
- [Orion Orchestrator](../network/orion_orchestrator/overview.md) - Multi-device orchestration
- [Device Registry](../network/agent_registration/device_registry.md) - Device management
- [Agent Profiles](../network/agent_registration/agent_profile.md) - Multi-source profiling

---

## ❓ Getting Help

- 📖 **Documentation**: [https://github.com/DEVELOPER-DEEVEN/alien-project](https://github.com/DEVELOPER-DEEVEN/alien-project)
- 🐛 **GitHub Issues**: [https://github.com/DEVELOPER-DEEVEN/alien-project/issues](https://github.com/DEVELOPER-DEEVEN/alien-project/issues) (preferred)
- 📧 **Email**: [alien-agent@microsoft.com](mailto:alien-agent@microsoft.com)

---

## 🎯 Next Steps

Now that Network is set up, explore these guides to unlock its full potential:

1. **[Add More Devices](../configuration/system/network_devices.md)** - Expand your device pool
2. **[Configure Capabilities](../configuration/system/network_devices.md)** - Optimize task routing
3. **[Orion Agent](../network/orion_agent/overview.md)** - Deep dive into orchestration agent
4. **[Advanced Orchestration](../network/orion_orchestrator/overview.md)** - Deep dive into DAG planning

Happy orchestrating with ALIEN³ Network! 🌌🚀
