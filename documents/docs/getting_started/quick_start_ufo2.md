# Quick Start Guide

Welcome to **Alien²** – the Desktop AgentOS! This guide will help you get started with Alien² in just a few minutes.

**What is Alien²?**

Alien² is a Desktop AgentOS that turns natural-language requests into automatic, reliable, multi-application workflows on Windows. It goes beyond UI-focused automation by combining GUI actions with native API calls for faster and more robust execution.

---

## 🛠️ Step 1: Installation

### Requirements

- **Python** >= 3.10
- **Windows OS** >= 10
- **Git** (for cloning the repository)

### Installation Steps

```powershell
# [Optional] Create conda environment
conda create -n Alien python=3.10
conda activate Alien

# Clone the repository
git clone https://github.com/microsoft/Alien.git
cd Alien

# Install dependencies
pip install -r requirements.txt
```

> **💡 Tip:** If you want to use Qwen as your LLM, uncomment the related libraries in `requirements.txt` before installing.

---

---

## ⚙️ Step 2: Configure LLMs

> **📢 New Configuration System (Recommended)**  
> Alien² now uses a **new modular config system** located in `config/Alien/` with auto-discovery and type validation. While the legacy `Alien/config/config.yaml` is still supported for backward compatibility, we strongly recommend migrating to the new system for better maintainability.

### Option 1: New Config System (Recommended)

The new config files are organized in `config/Alien/` with separate YAML files for different components:

```powershell
# Copy template to create your agent config file (contains API keys)
copy config\Alien\agents.yaml.template config\Alien\agents.yaml
notepad config\Alien\agents.yaml   # Edit your LLM API credentials
```

**Directory Structure:**
```
config/Alien/
├── agents.yaml.template     # Template: Agent configs (HOST_AGENT, APP_AGENT) - COPY & EDIT THIS
├── agents.yaml              # Your agent configs with API keys (DO NOT commit to git)
├── rag.yaml                 # RAG and knowledge settings (default values, edit if needed)
├── system.yaml              # System settings (default values, edit if needed)
├── mcp.yaml                 # MCP integration settings (default values, edit if needed)
└── ...                      # Other modular configs with defaults
```

> **Configuration Files:** `agents.yaml` contains sensitive information (API keys) and must be configured. Other config files have default values and only need editing for customization.

**Migration Benefits:**

- ✅ **Type Safety**: Automatic validation with Pydantic schemas
- ✅ **Auto-Discovery**: No manual config loading needed
- ✅ **Modular**: Separate concerns into individual files
- ✅ **IDE Support**: Better autocomplete and error detection

### Option 2: Legacy Config (Backward Compatible)

For existing users, the old config path still works:

```powershell
copy Alien\config\config.yaml.template Alien\config\config.yaml
notepad Alien\config\config.yaml   # Paste your key & endpoint
```

> **Config Precedence:** If both old and new configs exist, the new config in `config/Alien/` takes precedence. A warning will be displayed during startup.

---

### LLM Configuration Examples

#### OpenAI Configuration

**New Config (`config/Alien/agents.yaml`):**
```yaml
HOST_AGENT:
  VISUAL_MODE: true
  API_TYPE: "openai"
  API_BASE: "https://api.openai.com/v1/chat/completions"
  API_KEY: "sk-YOUR_KEY_HERE"  # Replace with your actual API key
  API_VERSION: "2025-02-01-preview"
  API_MODEL: "gpt-4o"

APP_AGENT:
  VISUAL_MODE: true
  API_TYPE: "openai"
  API_BASE: "https://api.openai.com/v1/chat/completions"
  API_KEY: "sk-YOUR_KEY_HERE"  # Replace with your actual API key
  API_VERSION: "2025-02-01-preview"
  API_MODEL: "gpt-4o"
```

**Legacy Config (`Alien/config/config.yaml`):**
```yaml
HOST_AGENT:
  VISUAL_MODE: True
  API_TYPE: "openai"
  API_BASE: "https://api.openai.com/v1/chat/completions"
  API_KEY: "sk-YOUR_KEY_HERE"
  API_VERSION: "2024-02-15-preview"
  API_MODEL: "gpt-4o"
```

#### Azure OpenAI (AOAI) Configuration

**New Config (`config/Alien/agents.yaml`):**
```yaml
HOST_AGENT:
  VISUAL_MODE: true
  API_TYPE: "aoai"
  API_BASE: "https://YOUR_RESOURCE.openai.azure.com"
  API_KEY: "YOUR_AOAI_KEY"
  API_VERSION: "2024-02-15-preview"
  API_MODEL: "gpt-4o"
  API_DEPLOYMENT_ID: "YOUR_DEPLOYMENT_ID"

APP_AGENT:
  VISUAL_MODE: true
  API_TYPE: "aoai"
  API_BASE: "https://YOUR_RESOURCE.openai.azure.com"
  API_KEY: "YOUR_AOAI_KEY"
  API_VERSION: "2024-02-15-preview"
  API_MODEL: "gpt-4o"
  API_DEPLOYMENT_ID: "YOUR_DEPLOYMENT_ID"
```

> **ℹ️ More LLM Options:** Alien² supports various LLM providers including Qwen, Gemini, Claude, DeepSeek, and more. See the [Model Configuration Guide](../configuration/models/overview.md) for complete details.

---

---

## 📔 Step 3: Additional Settings (Optional)

### RAG Configuration

Enhance Alien's capabilities with external knowledge through Retrieval Augmented Generation (RAG):

**For New Config**: Edit `config/Alien/rag.yaml` (already exists with default values)  
**For Legacy Config**: Edit `Alien/config/config.yaml`

**Available RAG Options:**

| Feature | Documentation | Description |
|---------|--------------|-------------|
| **Offline Help Documents** | [Learning from Help Documents](../Alien-Unis/core_features/knowledge_substrate/learning_from_help_document.md) | Retrieve information from offline help documentation |
| **Online Bing Search** | [Learning from Bing Search](../Alien-Unis/core_features/knowledge_substrate/learning_from_bing_search.md) | Utilize up-to-date online search results |
| **Self-Experience** | [Experience Learning](../Alien-Unis/core_features/knowledge_substrate/experience_learning.md) | Save task trajectories into memory for future reference |
| **User Demonstrations** | [Learning from Demonstrations](../Alien-Unis/core_features/knowledge_substrate/learning_from_demonstration.md) | Learn from user-provided demonstrations |

**Example RAG Config (`config/Alien/rag.yaml`):**
```yaml
# Enable Bing search
RAG_ONLINE_SEARCH: true
BING_API_KEY: "YOUR_BING_API_KEY"  # Get from https://www.microsoft.com/en-us/bing/apis

# Enable experience learning
RAG_EXPERIENCE: true
```

> **ℹ️ RAG Resources:** See [Knowledge Substrate Overview](../Alien-Unis/core_features/knowledge_substrate/overview.md) for complete RAG configuration and best practices.

---

---

## 🎉 Step 4: Start Alien²

### Interactive Mode

Start Alien² in interactive mode where you can enter requests dynamically:

```powershell
# Assume you are in the cloned Alien folder
python -m Alien --task <your_task_name>
```

**Expected Output:**
```
Welcome to use Alien🛸, A UI-focused Agent for Windows OS Interaction. 
 _   _  _____   ___
| | | ||  ___| / _ \
| | | || |_   | | | |
| |_| ||  _|  | |_| |
 \___/ |_|     \___/
Please enter your request to be completed🛸:
```

### Direct Request Mode

Invoke Alien² with a specific task and request directly:

```powershell
python -m Alien --task <your_task_name> -r "<your_request>"
```

**Example:**
```powershell
python -m Alien --task email_demo -r "Send an email to john@example.com with subject 'Meeting Reminder'"
```

---


---

## 🎥 Step 5: Execution Logs

Alien² automatically saves execution logs, screenshots, and traces for debugging and analysis.

**Log Location:**
```
./logs/<your_task_name>/
```

**Log Contents:**

| File/Folder | Description |
|-------------|-------------|
| `screenshots/` | Screenshots captured during execution |
| `action_*.json` | Agent actions and responses |
| `ui_trees/` | UI control tree snapshots (if enabled) |
| `request_response.log` | Complete LLM request/response logs |

> **Analyzing Logs:** Use the logs to debug agent behavior, replay execution flow, and analyze agent decision-making patterns.

> **Privacy Notice:** Screenshots may contain sensitive or confidential information. Ensure no private data is visible during execution. See [DISCLAIMER.md](https://github.com/microsoft/Alien/blob/main/DISCLAIMER.md) for details.

---

## 🔄 Migrating from Legacy Config

If you're upgrading from an older version that used `Alien/config/config.yaml`, Alien² provides an **automated conversion tool**.

### Automatic Conversion (Recommended)

```powershell
# Interactive conversion with automatic backup
python -m Alien.tools.convert_config

# Preview changes first (dry run)
python -m Alien.tools.convert_config --dry-run

# Force conversion without confirmation
python -m Alien.tools.convert_config --force
```

**What the tool does:**

- ✅ Splits monolithic `config.yaml` into modular files
- ✅ Converts flow-style YAML (with braces) to block-style YAML
- ✅ Maps legacy file names to new structure
- ✅ Preserves all configuration values
- ✅ Creates timestamped backup for rollback
- ✅ Validates output files

**Conversion Mapping:**

| Legacy File | → | New File(s) | Transformation |
|-------------|---|-------------|----------------|
| `config.yaml` (monolithic) | → | `agents.yaml` + `rag.yaml` + `system.yaml` | Smart field splitting |
| `agent_mcp.yaml` | → | `mcp.yaml` | Rename + format conversion |
| `config_prices.yaml` | → | `prices.yaml` | Rename + format conversion |

> **Migration Guide:** For detailed migration instructions, rollback procedures, and troubleshooting, see the [Configuration Migration Guide](../configuration/system/migration.md).

---

## 📚 Additional Resources

### Core Documentation

**Architecture & Concepts:**

- [Alien² Overview](../Alien-Unis/overview.md) - System architecture and design principles
- [HostAgent](../Alien-Unis/host_agent/overview.md) - Desktop-level coordination agent
- [AppAgent](../Alien-Unis/app_agent/overview.md) - Application-level execution agent

### Configuration

**Configuration Guides:**

- [Configuration Overview](../configuration/system/overview.md) - Configuration system architecture
- [Agents Configuration](../configuration/system/agents_config.md) - LLM and agent settings
- [System Configuration](../configuration/system/system_config.md) - Runtime and execution settings
- [MCP Configuration](../configuration/system/mcp_reference.md) - MCP server settings
- [Model Configuration](../configuration/models/overview.md) - Supported LLM providers

### Advanced Features

**Advanced Topics:**

- [Hybrid Actions](../Alien-Unis/core_features/hybrid_actions.md) - GUI + API automation
- [Control Detection](../Alien-Unis/core_features/control_detection/overview.md) - UIA + Vision detection
- [Knowledge Substrate](../Alien-Unis/core_features/knowledge_substrate/overview.md) - RAG and learning
- [Multi-Action Execution](../Alien-Unis/core_features/multi_action.md) - Speculative action batching

### Evaluation & Benchmarks

**Benchmarking:**

- [Benchmark Overview](../Alien-Unis/evaluation/benchmark/overview.md) - Evaluation framework and datasets
- [Windows Agent Arena](../Alien-Unis/evaluation/benchmark/windows_agent_arena.md) - 154 real Windows tasks
- [OSWorld](../Alien-Unis/evaluation/benchmark/osworld.md) - Cross-application benchmarks

---

## ❓ Getting Help

- 📖 **Documentation**: [https://microsoft.github.io/Alien/](https://microsoft.github.io/Alien/)
- 🐛 **GitHub Issues**: [https://github.com/microsoft/Alien/issues](https://github.com/microsoft/Alien/issues) (preferred)
- 📧 **Email**: [Alien-agent@microsoft.com](mailto:Alien-agent@microsoft.com)

---

## 🎯 Next Steps

Now that Alien² is set up, explore these guides to unlock its full potential:

1. **[Configuration Customization](../configuration/system/overview.md)** - Fine-tune Alien² behavior
2. **[Knowledge Substrate Setup](../Alien-Unis/core_features/knowledge_substrate/overview.md)** - Enable RAG capabilities
3. **[Creating Custom Agents](../tutorials/creating_app_agent/overview.md)** - Build specialized agents
4. **[MCP Integration](../mcp/overview.md)** - Extend with custom MCP servers

Happy automating with Alien²! 🛸