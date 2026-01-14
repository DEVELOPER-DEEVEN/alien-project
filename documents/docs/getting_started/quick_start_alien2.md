# Quick Start Guide

Welcome to **ALIEN²** – the Desktop AgentOS! This guide will help you get started with ALIEN² in just a few minutes.

**What is ALIEN²?**

ALIEN² is a Desktop AgentOS that turns natural-language requests into automatic, reliable, multi-application workflows on Windows. It goes beyond UI-focused automation by combining GUI actions with native API calls for faster and more robust execution.

---

## 🛠️ Step 1: Installation

### Requirements

- **Python** >= 3.10
- **Windows OS** >= 10
- **Git** (for cloning the repository)

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

---

## ⚙️ Step 2: Configure LLMs

> **📢 New Configuration System (Recommended)**  
> ALIEN² now uses a **new modular config system** located in `config/alien/` with auto-discovery and type validation. While the legacy `alien/config/config.yaml` is still supported for backward compatibility, we strongly recommend migrating to the new system for better maintainability.

### Option 1: New Config System (Recommended)

The new config files are organized in `config/alien/` with separate YAML files for different components:

```powershell
# Copy template to create your agent config file (contains API keys)
copy config\alien\agents.yaml.template config\alien\agents.yaml
notepad config\alien\agents.yaml   # Edit your LLM API credentials
```

**Directory Structure:**
```
config/alien/
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
copy alien\config\config.yaml.template alien\config\config.yaml
notepad alien\config\config.yaml   # Paste your key & endpoint
```

> **Config Precedence:** If both old and new configs exist, the new config in `config/alien/` takes precedence. A warning will be displayed during startup.

---

### LLM Configuration Examples

#### OpenAI Configuration

**New Config (`config/alien/agents.yaml`):**
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

**Legacy Config (`alien/config/config.yaml`):**
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

**New Config (`config/alien/agents.yaml`):**
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

> **ℹ️ More LLM Options:** ALIEN² supports various LLM providers including Qwen, Gemini, Claude, DeepSeek, and more. See the [Model Configuration Guide](../configuration/models/overview.md) for complete details.

---

---

## 📔 Step 3: Additional Settings (Optional)

### RAG Configuration

Enhance ALIEN's capabilities with external knowledge through Retrieval Augmented Generation (RAG):

**For New Config**: Edit `config/alien/rag.yaml` (already exists with default values)  
**For Legacy Config**: Edit `alien/config/config.yaml`

**Available RAG Options:**

| Feature | Documentation | Description |
|---------|--------------|-------------|
| **Offline Help Documents** | [Learning from Help Documents](../alien2/core_features/knowledge_substrate/learning_from_help_document.md) | Retrieve information from offline help documentation |
| **Online Bing Search** | [Learning from Bing Search](../alien2/core_features/knowledge_substrate/learning_from_bing_search.md) | Utilize up-to-date online search results |
| **Self-Experience** | [Experience Learning](../alien2/core_features/knowledge_substrate/experience_learning.md) | Save task trajectories into memory for future reference |
| **User Demonstrations** | [Learning from Demonstrations](../alien2/core_features/knowledge_substrate/learning_from_demonstration.md) | Learn from user-provided demonstrations |

**Example RAG Config (`config/alien/rag.yaml`):**
```yaml
# Enable Bing search
RAG_ONLINE_SEARCH: true
BING_API_KEY: "YOUR_BING_API_KEY"  # Get from https://www.microsoft.com/en-us/bing/apis

# Enable experience learning
RAG_EXPERIENCE: true
```

> **ℹ️ RAG Resources:** See [Knowledge Substrate Overview](../alien2/core_features/knowledge_substrate/overview.md) for complete RAG configuration and best practices.

---

---

## 🎉 Step 4: Start ALIEN²

### Interactive Mode

Start ALIEN² in interactive mode where you can enter requests dynamically:

```powershell
# Assume you are in the cloned ALIEN folder
python -m alien --task <your_task_name>
```

**Expected Output:**
```
Welcome to use ALIEN🛸, A UI-focused Agent for Windows OS Interaction. 
 _   _  _____   ___
| | | ||  ___| / _ \
| | | || |_   | | | |
| |_| ||  _|  | |_| |
 \___/ |_|     \___/
Please enter your request to be completed🛸:
```

### Direct Request Mode

Invoke ALIEN² with a specific task and request directly:

```powershell
python -m alien --task <your_task_name> -r "<your_request>"
```

**Example:**
```powershell
python -m alien --task email_demo -r "Send an email to john@example.com with subject 'Meeting Reminder'"
```

---


---

## 🎥 Step 5: Execution Logs

ALIEN² automatically saves execution logs, screenshots, and traces for debugging and analysis.

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

> **Privacy Notice:** Screenshots may contain sensitive or confidential information. Ensure no private data is visible during execution. See [DISCLAIMER.md](https://github.com/DEVELOPER-DEEVEN/alien-project/blob/main/DISCLAIMER.md) for details.

---

## 🔄 Migrating from Legacy Config

If you're upgrading from an older version that used `alien/config/config.yaml`, ALIEN² provides an **automated conversion tool**.

### Automatic Conversion (Recommended)

```powershell
# Interactive conversion with automatic backup
python -m alien.tools.convert_config

# Preview changes first (dry run)
python -m alien.tools.convert_config --dry-run

# Force conversion without confirmation
python -m alien.tools.convert_config --force
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

- [ALIEN² Overview](../alien2/overview.md) - System architecture and design principles
- [HostAgent](../alien2/host_agent/overview.md) - Desktop-level coordination agent
- [AppAgent](../alien2/app_agent/overview.md) - Application-level execution agent

### Configuration

**Configuration Guides:**

- [Configuration Overview](../configuration/system/overview.md) - Configuration system architecture
- [Agents Configuration](../configuration/system/agents_config.md) - LLM and agent settings
- [System Configuration](../configuration/system/system_config.md) - Runtime and execution settings
- [MCP Configuration](../configuration/system/mcp_reference.md) - MCP server settings
- [Model Configuration](../configuration/models/overview.md) - Supported LLM providers

### Advanced Features

**Advanced Topics:**

- [Hybrid Actions](../alien2/core_features/hybrid_actions.md) - GUI + API automation
- [Control Detection](../alien2/core_features/control_detection/overview.md) - UIA + Vision detection
- [Knowledge Substrate](../alien2/core_features/knowledge_substrate/overview.md) - RAG and learning
- [Multi-Action Execution](../alien2/core_features/multi_action.md) - Speculative action batching

### Evaluation & Benchmarks

**Benchmarking:**

- [Benchmark Overview](../alien2/evaluation/benchmark/overview.md) - Evaluation framework and datasets
- [Windows Agent Arena](../alien2/evaluation/benchmark/windows_agent_arena.md) - 154 real Windows tasks
- [OSWorld](../alien2/evaluation/benchmark/osworld.md) - Cross-application benchmarks

---

## ❓ Getting Help

- 📖 **Documentation**: [https://github.com/DEVELOPER-DEEVEN/alien-project](https://github.com/DEVELOPER-DEEVEN/alien-project)
- 🐛 **GitHub Issues**: [https://github.com/DEVELOPER-DEEVEN/alien-project/issues](https://github.com/DEVELOPER-DEEVEN/alien-project/issues) (preferred)
- 📧 **Email**: [alien-agent@microsoft.com](mailto:alien-agent@microsoft.com)

---

## 🎯 Next Steps

Now that ALIEN² is set up, explore these guides to unlock its full potential:

1. **[Configuration Customization](../configuration/system/overview.md)** - Fine-tune ALIEN² behavior
2. **[Knowledge Substrate Setup](../alien2/core_features/knowledge_substrate/overview.md)** - Enable RAG capabilities
3. **[Creating Custom Agents](../tutorials/creating_app_agent/overview.md)** - Build specialized agents
4. **[MCP Integration](../mcp/overview.md)** - Extend with custom MCP servers

Happy automating with ALIEN²! 🛸