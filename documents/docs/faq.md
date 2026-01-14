# Frequently Asked Questions (FAQ)

Quick answers to common questions about ALIEN³ Network, ALIEN², Linux Agents, and general troubleshooting.

---

##  General Questions

### Q: What is ALIEN³?

**A:** ALIEN³ is the third iteration of the ALIEN project, encompassing three major frameworks:

- **ALIEN²** - Desktop AgentOS for Windows automation
- **ALIEN³ Network** - Multi-device orchestration framework  
- **Linux Agent** - Server and CLI automation for Linux

### Q: Why is it called ALIEN?

**A:** ALIEN stands for **U**I **Fo**cused agent. The name was given to the first version of the project and has been retained through all iterations (ALIEN v1, ALIEN², ALIEN³) as the project evolved from a simple UI-focused agent to a comprehensive multi-device orchestration framework.

### Q: Which version should I use?

**A:** Choose based on your needs:

| Use Case | Recommended Version |
|----------|-------------------|
| Windows desktop automation only | [ALIEN²](getting_started/quick_start_alien2.md) |
| Cross-device workflows (Windows + Linux) | [ALIEN³ Network](getting_started/quick_start_network.md) |
| Linux server management only | [Linux Agent](getting_started/quick_start_linux.md) |
| Multi-device orchestration | [ALIEN³ Network](getting_started/quick_start_network.md) |

### Q: What's the difference between ALIEN² and ALIEN³ Network?

**A: ALIEN²** is for single Windows desktop automation with:
- Deep Windows OS integration (UIA, Win32, COM)
- Office application automation
- GUI + API hybrid execution

**ALIEN³ Network** orchestrates multiple devices with:
- Cross-platform support (Windows + Linux)
- Distributed task execution
- Device capability-based routing
- Orion-based DAG orchestration

See [Migration Guide](getting_started/migration_alien2_to_network.md) for details.

### Q: Can I use ALIEN on Linux or macOS?

**A:** Yes and No:

- **[OK] Linux:** Supported via Linux Agent for server/CLI automation
- **[FAIL] macOS:** Not currently supported (Windows and Linux only)
- **Windows:** Full ALIEN² desktop automation support

---

## [CONFIG] Installation & Setup

### Q: Which Python version do I need?

**A:** Python **3.10 or higher** is required for all ALIEN³ components.

```bash
# Check your Python version
python --version
```

### Q: What models does ALIEN support?

**A:** ALIEN³ supports multiple LLM providers:

- **OpenAI** - GPT-4o, GPT-4, GPT-3.5
- **Azure OpenAI** - All Azure-hosted models
- **Google Gemini** - Gemini Pro, Gemini Flash
- **Anthropic Claude** - Claude 3.5, Claude 3
- **Qwen** - Local or API deployment
- **DeepSeek** - DeepSeek models
- **Ollama** - Local model hosting
- And more...

See [Model Configuration Guide](configuration/models/overview.md) for the complete list and setup instructions.

### Q: Can I use non-vision models in ALIEN?

**A:** Yes! You can disable visual mode:

```yaml
# config/alien/system.yaml
VISUAL_MODE: false
```

However, ALIEN² is designed for vision models. Non-vision models may have reduced performance for GUI automation tasks.

### Q: Can I host my own LLM endpoint?

**A:** Yes! ALIEN³ supports custom endpoints:

```yaml
# config/alien/agents.yaml
HOST_AGENT:
  API_TYPE: "openai"  # Or compatible API
  API_BASE: "http://your-endpoint.com/v1/chat/completions"
  API_KEY: "your-key"
  API_MODEL: "your-model-name"
```

See [Model Configuration](configuration/models/overview.md) for details.

### Q: Do I need API keys for all agents?

**A:** No, only for LLM-powered agents:

| Component | Requires API Key | Purpose |
|-----------|-----------------|---------|
| **OrionAgent** (Network) | [OK] Yes | Orchestration reasoning |
| **HostAgent** (ALIEN²) | [OK] Yes | Task planning |
| **AppAgent** (ALIEN²) | [OK] Yes | Action execution |
| **LinuxAgent** | [OK] Yes | Command planning |
| **Device Server** | [FAIL] No | Message routing only |
| **MCP Servers** | [FAIL] No | Tool provider only |

---

## ️ Configuration

### Q: Where are configuration files located?

**A:** ALIEN³ uses a modular configuration system in `config/`:

```
config/
├── alien/                    # ALIEN² configuration
│   ├── agents.yaml         # LLM and agent settings
│   ├── system.yaml         # Runtime settings
│   ├── rag.yaml           # Knowledge retrieval
│   └── mcp.yaml           # MCP server configuration
└── network/                 # Network configuration
    ├── agent.yaml          # OrionAgent LLM
    ├── devices.yaml        # Device pool
    └── orion.yaml  # Runtime settings
```

### Q: Can I still use the old `alien/config/config.yaml`?

**A:** Yes, for backward compatibility, but we recommend migrating to the new modular system:

```bash
# Check current configuration
python -m alien.tools.validate_config alien --show-config

# Migrate from legacy to new
python -m alien.tools.migrate_config
```

See [Configuration Migration Guide](configuration/system/migration.md) for details.

### Q: How do I protect my API keys?

**A:** Best practices for API key security:

1. **Never commit `.yaml` files with keys** - Use `.template` files
   ```bash
   # Good pattern
   config/alien/agents.yaml.template  # Commit this (with placeholders)
   config/alien/agents.yaml           # DON'T commit (has real keys)
   ```

2. **Use environment variables** for sensitive data:
   ```yaml
   # In agents.yaml
   HOST_AGENT:
     API_KEY: ${OPENAI_API_KEY}  # Reads from environment
   ```

3. **Add to `.gitignore`**:
   ```
   config/**/agents.yaml
   config/**/agent.yaml
   !**/*.template
   ```

---

## [ORION] ALIEN³ Network Questions

### Q: What's the minimum number of devices for Network?

**A:** Network requires **at least 1 device agent** (Windows or Linux) to be useful, but you can start with just one device and add more later.

```yaml
# Minimal Network setup (1 device)
devices:
  - device_id: "my_windows_pc"
    server_url: "ws://localhost:5000/ws"
    os: "windows"
```

### Q: Can Network mix Windows and Linux devices?

**A:** Yes! Network can orchestrate heterogeneous devices:

```yaml
devices:
  - device_id: "windows_desktop"
    os: "windows"
    capabilities: ["office", "excel", "outlook"]
    
  - device_id: "linux_server"
    os: "linux"
    capabilities: ["server", "database", "log_analysis"]
```

Network automatically routes tasks based on device capabilities.

### Q: Do all devices need to be on the same network?

**A:** No, devices can be distributed across networks using SSH tunneling:

- **Same network:** Direct WebSocket connections
- **Different networks:** Use SSH tunnels (reverse/forward)
- **Cloud + local:** SSH tunnels with public gateways

See [Linux Quick Start - SSH Tunneling](getting_started/quick_start_linux.md#network-connectivity-ssh-tunneling) for examples.

### Q: How does Network decide which device to use?

**A:** Network uses **capability-based routing**:

1. Analyzes the task requirements
2. Matches against device `capabilities` in `devices.yaml`
3. Considers device `metadata` (OS, performance, etc.)
4. Selects the best-fit device(s)

Example:
```yaml
# Task: "Analyze error logs on the production server"
# → Network routes to device with:
capabilities:
  - "log_analysis"
  - "server_management"
os: "linux"
```

---

##  Linux Agent Questions

### Q: Does the Linux Agent require a GUI?

**A:** No! The Linux Agent is designed for headless servers:

- Executes CLI commands via MCP
- No X11/desktop environment needed
- Works over SSH
- Perfect for remote servers

### Q: Can I run multiple Linux Agents on one machine?

**A:** Yes, using different ports and client IDs:

```bash
# Agent 1
python -m alien.server.app --port 5001
python -m alien.client.client --ws --client-id linux_1 --platform linux

# Agent 2 (same machine)
python -m alien.server.app --port 5002
python -m alien.client.client --ws --client-id linux_2 --platform linux
```

### Q: What's the MCP service for?

**A:** The MCP (Model Context Protocol) service provides the **actual command execution tools** for the Linux Agent:

```
Linux Agent (LLM reasoning)
     ↓
MCP Service (tool provider)
     ↓
Bash commands (actual execution)
```

Without MCP, the Linux Agent can't execute commands - it can only plan them.

---

## 🪟 ALIEN² Questions

### Q: Does ALIEN² work on Windows 10?

**A:** Yes! ALIEN² supports:
- [OK] Windows 11 (recommended)
- [OK] Windows 10 (fully supported)
- [FAIL] Windows 8.1 or earlier (not tested)

### Q: Can ALIEN² automate Office apps?

**A:** Yes! ALIEN² has enhanced Office support through:
- **MCP Office servers** - Direct API access to Excel, Word, Outlook, PowerPoint
- **GUI automation** - Fallback for unsupported operations
- **Hybrid execution** - Automatically chooses API or GUI

Enable MCP in `config/alien/mcp.yaml` for better Office automation.

### Q: Does ALIEN² interrupt my work?

**A:** ALIEN² can run automation tasks on your current desktop. For non-disruptive operation, you can run it on a separate machine or virtual desktop environment.

> **Note:** Picture-in-Picture mode is planned for future releases.

### Q: Can I use ALIEN² without MCP?

**A:** ALIEN² requires MCP (Model Context Protocol) servers for tool execution. MCP provides the interface between the LLM agents and system operations (Windows APIs, Office automation, etc.). Without MCP, ALIEN² cannot perform actions.

---

##  Common Issues & Troubleshooting

### Issue: "Configuration file not found"

**Error:**
```
FileNotFoundError: config/alien/agents.yaml not found
```

**Solution:**
```bash
# Copy template files
cp config/alien/agents.yaml.template config/alien/agents.yaml

# Edit with your API keys
notepad config/alien/agents.yaml  # Windows
nano config/alien/agents.yaml     # Linux
```

### Issue: "API Authentication Error"

**Error:**
```
openai.AuthenticationError: Invalid API key
```

**Solutions:**

1. **Check API key format:**
   ```yaml
   API_KEY: "sk-..."  # OpenAI starts with sk-
   API_KEY: "..."     # Azure uses deployment key
   ```

2. **Verify API_TYPE matches your provider:**
   ```yaml
   API_TYPE: "openai"  # For OpenAI
   API_TYPE: "aoai"    # For Azure OpenAI
   ```

3. **Check for extra spaces/quotes** in YAML

4. **For Azure:** Verify `API_DEPLOYMENT_ID` is set

### Issue: "Connection aborted / Remote end closed connection"

**Error:**
```
Error making API request: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**Solutions:**

- Check network connection (VPN, proxy, firewall)
- Verify LLM endpoint is accessible: `curl https://api.openai.com/v1/models`
- Check endpoint status (Azure, OpenAI, etc.)
- Try increasing timeout in config
- Verify API base URL is correct

### Issue: "Device not connecting to Network"

**Error:**
```
ERROR - [WS] Failed to connect to ws://localhost:5000/ws
Connection refused
```

**Checklist:**

- [ ] Is the server running? (`curl http://localhost:5000/api/health`)
- [ ] Port number correct? (Server: `--port 5000`, Client: `ws://...:5000/ws`)
- [ ] Platform flag set? (`--platform windows` or `--platform linux`)
- [ ] Firewall blocking? (Allow port 5000)
- [ ] SSH tunnel established? (If using remote devices)

### Issue: "device_id mismatch in Network"

**Error:**
```
ERROR - Device 'linux_agent_1' not found in configuration
```

**Cause:** Mismatch between `devices.yaml` and client command

**Solution:** Ensure exact match:

| Location | Field | Example |
|----------|-------|---------|
| `devices.yaml` | `device_id:` | `"linux_agent_1"` |
| Client command | `--client-id` | `linux_agent_1` |

**Critical:** IDs must match **exactly** (case-sensitive, no typos).

### Issue: "MCP service not responding (Linux)"

**Error:**
```
ERROR - Cannot connect to MCP server at http://127.0.0.1:8010
```

**Solutions:**

1. **Check if MCP service is running:**
   ```bash
   curl http://localhost:8010/health
   ps aux | grep linux_mcp_server
   ```

2. **Restart MCP service:**
   ```bash
   pkill -f linux_mcp_server
   python -m alien.client.mcp.http_servers.linux_mcp_server
   ```

3. **Check port conflict:**
   ```bash
   lsof -i :8010
   # If port taken, use different port:
   python -m alien.client.mcp.http_servers.linux_mcp_server --port 8011
   ```

### Issue: "Tasks failing after X steps"

**Cause:** `MAX_STEP` limit reached

**Solution:** Increase step limit in `config/alien/system.yaml`:

```yaml
# Default is 50
MAX_STEP: 100  # For complex tasks

# Or disable limit (not recommended)
MAX_STEP: -1
```

### Issue: "Too many LLM calls / high cost"

**Solutions:**

1. **Enable action sequences** (bundles actions):
   ```yaml
   # config/alien/system.yaml
   ACTION_SEQUENCE: true
   ```

2. **Use vision-capable models for GUI tasks:**
   ```yaml
   # config/alien/agents.yaml
   APP_AGENT:
     API_MODEL: "gpt-4o"  # Use vision models for GUI automation
   ```
   
   > **Note:** Non-vision models like gpt-3.5-turbo cannot process screenshots and should not be used for GUI automation tasks.

3. **Enable experience learning** (reuse patterns):
   ```yaml
   # config/alien/rag.yaml
   RAG_EXPERIENCE: true
   ```

### Issue: "Why is the latency high?"

**A:** Latency depends on several factors:

- **LLM response time** - GPT-4o typically takes 10-30 seconds per step
- **Network speed** - API calls to OpenAI/Azure endpoints
- **Endpoint workload** - Provider server load
- **Visual mode** - Image processing adds overhead

**To reduce latency:**
- Use faster models (gpt-3.5-turbo vs gpt-4o)
- Enable action sequences to batch operations
- Use local models (Ollama) if acceptable
- Disable visual mode if not needed

### Issue: "Can I use non-English requests?"

**A:** Yes! Most modern LLMs support multiple languages:

- GPT-4o, GPT-4: Excellent multilingual support
- Gemini: Good multilingual support
- Qwen: Excellent for Chinese
- Claude: Good multilingual support

Performance may vary by language and model. Test with your specific language and model combination.

---

## [PLAN] Where to Find More Help

### Documentation

| Topic | Link |
|-------|------|
| **Getting Started** | [ALIEN² Quick Start](getting_started/quick_start_alien2.md), [Network Quick Start](getting_started/quick_start_network.md), [Linux Quick Start](getting_started/quick_start_linux.md) |
| **Configuration** | [Configuration Overview](configuration/system/overview.md) |
| **Troubleshooting** | Quick start guides have detailed troubleshooting sections |
| **Architecture** | [Project Structure](project_directory_structure.md) |
| **More Guidance** | [User & Developer Guide](getting_started/more_guidance.md) |

### Community & Support

- **GitHub Discussions:** [https://github.com/DEVELOPER-DEEVEN/alien-project/discussions](https://github.com/DEVELOPER-DEEVEN/alien-project/discussions)
- **GitHub Issues:** [https://github.com/DEVELOPER-DEEVEN/alien-project/issues](https://github.com/DEVELOPER-DEEVEN/alien-project/issues)
- **Email:** alien-agent@microsoft.com

### Debugging Tips

1. **Enable debug logging:**
   ```yaml
   # config/alien/system.yaml
   LOG_LEVEL: "DEBUG"
   ```

2. **Check log files:**
   ```
   logs/<task-name>/
   ├── request.log                    # Request logs
   ├── response.log                   # Response logs
   ├── action_step*.png               # Screenshots at each step
   └── action_step*_annotated.png     # Annotated screenshots
   ```

3. **Validate configuration:**
   ```bash
   python -m alien.tools.validate_config alien --show-config
   python -m alien.tools.validate_config network --show-config
   ```

4. **Test LLM connectivity:**
   ```python
   # Test your API key
   from openai import OpenAI
   client = OpenAI(api_key="your-key")
   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Hello"}]
   )
   print(response.choices[0].message.content)
   ```

---

> **[THOUGHT] Still have questions?** Check the [More Guidance](getting_started/more_guidance.md) page for additional resources, or reach out to the community!
