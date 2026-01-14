# Migration Guide: ALIEN² to ALIEN³ Network

This guide helps you understand the evolution from **ALIEN²** (Desktop AgentOS) to **ALIEN³ Network** (Multi-Device AgentOS), and provides practical steps for migrating your workflows to leverage Network's cross-device orchestration capabilities.

---

## 🌟 Understanding the ALIEN Evolution

### The ALIEN Journey

The ALIEN project has evolved through three major iterations, each addressing increasingly complex automation challenges:

```mermaid
graph LR
    A[ALIEN v1<br/>2024-02] -->|Desktop Agent| B[ALIEN²<br/>2025-04]
    B -->|Multi-Device| C[ALIEN³ Network<br/>2025-11]
    
    style A fill:#e3f2fd
    style B fill:#c8e6c9
    style C fill:#fff9c4
```

#### **ALIEN (v1.0)** — The Beginning
📅 *Released: February 2024*

- **Vision**: Screenshot-based Windows automation
- **Architecture**: Multi-agent (HostAgent + AppAgents)
- **Approach**: GPT-4V + pure GUI automation (click/type)
- **Scope**: Single Windows desktop, cross-app workflows
- **Limitation**: No deep OS integration

**Key Innovation:** First LLM-powered multi-agent GUI automation framework

---

#### **ALIEN² (v2.0)** — Desktop AgentOS
📅 *Released: April 2025*  
📄 *Paper:* [ALIEN²: A Windows Agent for Seamless OS Interaction](https://arxiv.org/abs/2504.14603)

- **Vision**: Deep OS integration for robust automation
- **Architecture**: Two-tier hierarchy (HostAgent + AppAgents)
- **Innovations**:
  - ✅ **Hybrid GUI–API execution** (51% fewer LLM calls)
  - ✅ **Windows UIA + Win32 + WinCOM APIs**
  - ✅ **Continuous knowledge learning** from docs & experience
  - ✅ **Picture-in-Picture desktop** (non-disruptive automation)
  - ✅ **MCP server integration** for tool augmentation
- **Scope**: Single Windows desktop
- **Success**: 10%+ better than state-of-the-art CUAs

**Key Innovation:** First agent to deeply integrate with Windows OS internals

---

#### **ALIEN³ Network** — Multi-Device AgentOS
📅 *Released: November 2025*  
📄 *Paper:* ALIEN³: Weaving the Digital Agent Network *(Coming Soon)*

- **Vision**: Cross-device orchestration at scale
- **Architecture**: Orion-based distributed DAG orchestration
- **Innovations**:
  - ✅ **Task Orion** (dynamic DAG decomposition)
  - ✅ **Asynchronous parallel execution** across devices
  - ✅ **Event-driven coordination** with formal safety guarantees
  - ✅ **Dual-mode DAG evolution** (creation + editing)
  - ✅ **Agent Interaction Protocol** (persistent WebSocket)
  - ✅ **Heterogeneous device support** (Windows, Linux, macOS)
- **Scope**: Multi-device workflows across platforms
- **Capability**: Orchestrate 10+ devices simultaneously

**Key Innovation:** First LLM-powered multi-device orchestration framework with provable correctness

---

### Architecture Evolution

#### ALIEN v1 Architecture

**Multi-Agent (GUI-Only)**

```
User Request
    ↓
HostAgent
    ↓
AppAgent 1, 2, 3...
    ↓
Windows Apps (GUI)
```

**Capabilities:**

- Multi-app workflows
- Pure screenshot + click/type
- No API integration
- Single device

#### ALIEN² Architecture

**Two-Tier Hierarchy (Hybrid)**

```
User Request
    ↓
HostAgent
    ↓
AppAgent 1, 2, 3...
    ↓
Windows Apps (GUI + API)
```

**Capabilities:**

- Multi-app workflows
- Desktop orchestration
- Hybrid GUI–API execution
- Deep OS integration
- Single device

#### ALIEN³ Network Architecture

**Orion Model (Distributed)**

```
User Request
    ↓
OrionAgent
    ↓
Task Orion (DAG)
    ↓
Device 1, 2, 3... (ALIEN² instances)
    ↓
Cross-Platform Apps
```

**Capabilities:**

- Multi-device workflows
- Parallel execution
- Dynamic adaptation
- Heterogeneous platforms

---

## 🎯 When to Use Which?

### Use **ALIEN²** (Desktop AgentOS) When:

✅ You're automating tasks on a **single Windows desktop**  
✅ You need **deep Windows integration** (Office, File Explorer, etc.)  
✅ You want **fast, simple execution** without network overhead  
✅ You're learning agent automation basics  
✅ Your workflow is entirely **local** (no cross-device dependencies)

**Examples:**
- "Create a PowerPoint presentation from this Excel data"
- "Organize my Downloads folder by file type"
- "Send emails to all contacts in this spreadsheet"

---

### Use **ALIEN³ Network** When:

✅ Your workflow spans **multiple devices** (Windows, Linux, servers)  
✅ You need **parallel task execution** for performance  
✅ You have **complex dependencies** between subtasks  
✅ You want **dynamic workflow adaptation** based on results  
✅ You need **fault tolerance** and automatic recovery  
✅ You're orchestrating **heterogeneous systems** (desktop + server + cloud)

**Examples:**
- "Clone repo on my laptop, build Docker image on GPU server, deploy to staging, run tests on CI cluster"
- "Fetch data from cloud storage, preprocess on Linux workstation, train model on A100 node, visualize on my Windows machine"
- "Collect logs from all Linux servers, analyze for errors, generate report on Windows"

---

### Can You Use Both?

**Yes!** ALIEN² can run as a **device agent** in the Network:

```
Network (Orchestrator)
    ├── Windows Device (ALIEN² instance)
    ├── Linux Device (ALIEN² instance)
    └── Server Device (ALIEN² instance)
```

This is the **recommended hybrid approach** for complex workflows.

---

## 🔄 Key Concept Mapping

Understanding how ALIEN² concepts map to Network:

| ALIEN² Concept | Network Equivalent | Relationship |
|--------------|-------------------|--------------|
| **HostAgent** | **OrionAgent** | Global orchestrator (but across devices) |
| **AppAgent** | **Device Agent (HostAgent)** | Local executor on each device |
| **Session** | **NetworkSession** | Workflow execution context |
| **Round** | **Orion Round** | Orchestration iteration |
| **Action** | **TaskStar** | Executable unit (but on specific device) |
| **Blackboard** | **Task Results** | Inter-task communication |
| **Config File** | `config/alien/` → `config/network/` | Configuration location |
| **Execution Mode** | `python -m alien.server.app --port <port>` | Device runs as WebSocket server |

### Architecture Translation

**ALIEN² (Single Device):**
```python
# ALIEN² executes locally
python -m alien --task "Create report from data.xlsx"

# HostAgent coordinates AppAgents on one desktop
HostAgent
  ├── ExcelAgent (data.xlsx)
  ├── WordAgent (report.docx)
  └── OutlookAgent (send email)
```

**Network (Multi-Device):**
```python
# Network orchestrates across devices
python -m network --request "Create report from data on Server, generate PDF on Windows"

# OrionAgent creates DAG, assigns to devices
OrionAgent
  └── TaskOrion (DAG)
      ├── TaskStar-1: Fetch data → Linux Server
      ├── TaskStar-2: Process → GPU Workstation
      └── TaskStar-3: Generate PDF → Windows Desktop
```

---

## ⚙️ Configuration Migration

### Step 1: Preserve ALIEN² Configuration

**Keep your existing ALIEN² config** — you'll use it for device agents:

```
config/alien/
├── agents.yaml          # LLM config for device agents
├── app_agent.yaml       # AppAgent settings
├── host_agent.yaml      # HostAgent settings
└── ...
```

**No changes needed** — each Network device will use its own ALIEN² config.

---

### Step 2: Create Network Configuration

Network adds **new orchestration-level config**:

#### A. OrionAgent LLM Config

```bash
# Copy template
copy config\network\agent.yaml.template config\network\agent.yaml
```

Edit `config/network/agent.yaml`:

```yaml
# OrionAgent LLM (orchestrator)
ORION_AGENT:
  API_TYPE: "openai"  # or "azure", "qwen", etc.
  API_BASE: "https://api.openai.com/v1"
  API_KEY: "sk-your-api-key-here"
  API_MODEL: "gpt-4o"
  API_VERSION: null

# Optional: Use different model for orchestration
# Recommended: Use GPT-4o or Claude for complex DAG reasoning
```

---

#### B. Device Pool Configuration

**New in Network:** Define all available devices

```bash
# Create device registry
notepad config\network\devices.yaml
```

```yaml
devices:
  # Your Windows desktop (existing ALIEN² instance)
  - device_id: "my_windows_desktop"
    server_url: "ws://localhost:5005/ws"
    os: "windows"
    capabilities:
      - "office_applications"  # Excel, Word, PowerPoint
      - "web_browsing"
      - "file_management"
    metadata:
      location: "local"
      os: "windows"
      performance: "high"
    auto_connect: true
    max_retries: 5

  # Linux workstation
  - device_id: "linux_workstation"
    server_url: "ws://192.168.1.100:5001/ws"
    os: "linux"
    capabilities:
      - "python"
      - "docker"
      - "server"
    metadata:
      location: "office"
      os: "ubuntu_22.04"
      performance: "high"
      gpu: "nvidia_a100"
    auto_connect: true

  # GPU server
  - device_id: "gpu_server"
    server_url: "ws://192.168.1.200:5002/ws"
    os: "linux"
    capabilities:
      - "machine_learning"
      - "cuda"
      - "docker"
    metadata:
      os: "centos_7"
      gpu: "nvidia_v100"
      performance: "ultra"
```

**Capability Matching:** OrionAgent uses these capabilities to assign tasks intelligently.

---

#### C. Orion Runtime Config

```bash
notepad config\network\orion.yaml
```

```yaml
# Orion Orchestration Settings
ORION_ID: "my_orion"
HEARTBEAT_INTERVAL: 30.0      # Device health check (seconds)
RECONNECT_DELAY: 5.0          # Auto-reconnect delay
MAX_CONCURRENT_TASKS: 6       # Parallel task limit
MAX_STEP: 15                  # Max orchestration rounds

# Device Configuration
DEVICE_INFO: "config/network/devices.yaml"

# Logging
LOG_TO_MARKDOWN: true         # Generate trajectory reports
```

---

## 🚀 Migration Steps

### Option 1: Keep ALIEN² for Local, Add Network for Multi-Device

**Best for:** Gradual adoption, maintaining existing workflows

1. **Continue using ALIEN² for single-device tasks**
   ```bash
   python -m alien --task "Your local task"
   ```

2. **Use Network only when you need multi-device orchestration**
   ```bash
   python -m network --request "Your cross-device task"
   ```

3. **No migration required** — both coexist independently

---

### Option 2: Convert ALIEN² Instance to Network Device

**Best for:** Leveraging Network's orchestration for all workflows

#### Step 1: Start ALIEN² as Agent Server

**On each device** (Windows, Linux, etc.), run ALIEN² server:

```bash
# Windows Desktop
python -m alien.server.app --port 5005

# Linux Workstation  
python -m alien.server.app --port 5001

# GPU Server
python -m alien.server.app --port 5002
```

**What this does:**
- Starts WebSocket server on the device
- Listens for task assignments from Network
- Uses existing ALIEN² agents (HostAgent/AppAgent) for local execution
- Reports results back to OrionClient

---

#### Step 2: Configure Network Client

Create `config/network/devices.yaml` with all your devices (see Configuration section above).

---

#### Step 3: Launch Network Client

```bash
# Interactive mode
python -m network --interactive

# Direct request
python -m network --request "Clone repo on laptop, build on server, test on Windows"
```

**What happens:**
1. OrionAgent decomposes request into DAG
2. TaskStars assigned to devices based on capabilities
3. Devices execute tasks using their local ALIEN² agents
4. Results aggregated and presented to user

---

### Option 3: Programmatic Migration

**Best for:** Custom workflows, CI/CD integration

#### ALIEN² API (Before):

```python
from alien.module.session_pool import SessionFactory, SessionPool
import asyncio

async def main():
    # Create ALIEN² session on local device
    sessions = SessionFactory().create_session(
        task="my_task",
        mode="normal",
        plan="",
        request="Create a presentation from data.xlsx"
    )
    
    # Run session
    pool = SessionPool(sessions)
    await pool.run_all()

asyncio.run(main())
```

#### Network API (After):

```python
from network import NetworkClient
import asyncio

async def main():
    # Network session coordinating multiple devices
    client = NetworkClient(session_name="my_workflow")
    await client.initialize()
    
    result = await client.process_request(
        "Clone repo on laptop, build on server, test on Windows"
    )
    
    print(f"Workflow completed: {result}")
    await client.shutdown()

asyncio.run(main())
```

**Key Differences:**
- Both are **async** (ALIEN² v2.0+ uses asyncio)
- ALIEN²: Uses `SessionFactory` + `SessionPool` pattern
- Network: Uses `NetworkClient` for multi-device orchestration
- Network returns **orion results** (multi-device)
- Network requires **device registration** first

---

## 📊 Feature Comparison

### Preserved ALIEN² Features in Network

When running ALIEN² as a Network device, you **keep all ALIEN² capabilities**:

| ALIEN² Feature | Available in Network Device? | Notes |
|--------------|----------------------------|-------|
| ✅ Hybrid GUI–API execution | ✅ Yes | Each device uses its native ALIEN² agent |
| ✅ Windows UIA/Win32/COM | ✅ Yes | Full OS integration preserved |
| ✅ MCP server integration | ✅ Yes | Devices can use custom MCP servers |
| ✅ Continuous learning | ✅ Yes | Each device maintains its own RAG |
| ✅ Picture-in-Picture | ✅ Yes | Non-disruptive execution on each device |
| ✅ AppAgent specialization | ✅ Yes | HostAgent manages local AppAgents |

---

### New Network-Only Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Task Orion** | DAG-based task decomposition | Complex workflow planning |
| **Parallel Execution** | Asynchronous multi-device tasks | 3-5x faster for parallelizable work |
| **Dynamic Adaptation** | Runtime DAG modification | Self-healing workflows |
| **Device Assignment** | Capability-based task placement | Optimal resource utilization |
| **Cross-Platform** | Windows + Linux + macOS support | Heterogeneous orchestration |
| **Event-Driven Coordination** | Observer pattern for task events | Reactive workflow control |
| **Formal Safety Guarantees** | I1-I3 invariants | Provably correct concurrent execution |

---

## 🛠️ Practical Examples

### Example 1: Simple Local Task

**ALIEN² (Before):**
```bash
python -m alien --task "Create a presentation from data.xlsx"
```

**Network (After) — Option A: Keep ALIEN²**
```bash
# No change needed — continue using ALIEN² for local tasks
python -m alien --task "Create a presentation from data.xlsx"
```

**Network (After) — Option B: Use Network**
```bash
# Network will assign to local Windows device automatically
python -m network --request "Create a presentation from data.xlsx on my desktop"
```

**When to use which?**
- Use ALIEN² if you only have one Windows desktop (simpler)
- Use Network if you want logging/monitoring features

---

### Example 2: Cross-Device Workflow

**ALIEN² (Before):**
```bash
# ❌ Not possible — ALIEN² is single-device only
# You'd need to manually:
# 1. SSH to server
# 2. Run build command
# 3. Copy results back
# 4. Open locally
```

**Network (After):**
```bash
python -m network --request \
  "Clone https://github.com/myrepo on laptop, \
   build Docker image on gpu_server, \
   deploy to staging server, \
   open logs on my Windows desktop"
```

**Network automatically:**
1. Creates 4-task DAG
2. Assigns tasks to capable devices
3. Executes in parallel where possible
4. Streams results back

---

### Example 3: Data Pipeline

**ALIEN² (Before):**
```python
# ALIEN² requires manual orchestration across multiple steps
from alien.module.session_pool import SessionFactory, SessionPool
import asyncio

async def main():
    # Step 1: Fetch data (local)
    sessions_1 = SessionFactory().create_session(
        task="fetch_data",
        mode="normal",
        plan="",
        request="Download dataset from cloud storage"
    )
    pool_1 = SessionPool(sessions_1)
    await pool_1.run_all()

    # Step 2: Manually transfer to server
    # scp data.csv user@server:/data/

    # Step 3: SSH and run processing
    # ssh server "python process.py"

    # Step 4: Manually copy results back
    # scp server:/output/results.csv .

    # Step 5: Visualize locally
    sessions_2 = SessionFactory().create_session(
        task="visualize",
        mode="normal",
        plan="",
        request="Create charts from results.csv"
    )
    pool_2 = SessionPool(sessions_2)
    await pool_2.run_all()

asyncio.run(main())
```

**Network (After):**
```python
import asyncio
from network import NetworkClient

async def main():
    client = NetworkClient(session_name="data_pipeline")
    await client.initialize()
    
    # Single request — Network handles orchestration
    await client.process_request(
        "Fetch dataset from cloud to laptop, "
        "preprocess on linux_workstation, "
        "train model on gpu_server, "
        "visualize results on my Windows desktop"
    )
    
    await client.shutdown()

asyncio.run(main())
```

**Network automatically:**
- Creates dependency chain
- Transfers data between devices
- Executes pipeline stages in order
- Handles failures with retries

---

## 🎓 Learning Path

### For ALIEN² Users

1. **Week 1: Understand Concepts**
   - Read [Network Overview](../network/overview.md)
   - Understand Task Orion and DAG model
   - Compare with ALIEN² two-tier hierarchy

2. **Week 2: Hands-On**
   - Set up one Windows device as Network agent
   - Run simple multi-step workflow
   - Compare logs: ALIEN² vs Network

3. **Week 3: Multi-Device**
   - Add Linux device to pool
   - Create cross-platform workflow
   - Monitor with trajectory reports

4. **Week 4: Advanced**
   - Build custom device capabilities
   - Integrate MCP servers across devices
   - Optimize task assignment logic

---

## 📚 Related Documentation

### Migration Resources

- **[Network Quick Start](./quick_start_network.md)** — Step-by-step Network setup
- **[ALIEN² Quick Start](./quick_start_alien2.md)** — ALIEN² reference
- **[Device Configuration](../configuration/system/network_devices.md)** — Device pool setup
- **[Agent Registration](../network/agent_registration/overview.md)** — How devices join Network

### Architecture Deep Dives

- **[Network Overview](../network/overview.md)** — Orion architecture
- **[ALIEN² Overview](../alien2/overview.md)** — Desktop AgentOS design
- **[Orion Agent](../network/orion_agent/overview.md)** — DAG orchestration
- **[Task Orion](../network/orion/overview.md)** — DAG structure

### Operational Guides

- **[Trajectory Report](../network/evaluation/trajectory_report.md)** — Execution logs
- **[Performance Metrics](../network/evaluation/performance_metrics.md)** — Monitoring
- **[AIP Protocol](../aip/overview.md)** — Device communication

---

## 🤝 Getting Help

### Common Questions

**Q: Can I still use ALIEN² after migrating to Network?**  
A: Yes! They coexist. Use ALIEN² for simple local tasks, Network for multi-device workflows.

**Q: Do I need to rewrite my custom agents?**  
A: No. Existing ALIEN² agents work as-is when running as Network devices.

**Q: Is Network production-ready?**  
A: Network is in active development. ALIEN² is more mature for mission-critical single-device workflows.

**Q: Can I mix Windows and Linux devices?**  
A: Yes! That's Network's key feature. Each device uses its native ALIEN² implementation.

**Q: How do I debug failed cross-device workflows?**  
A: Check `logs/network/<session>/output.md` for step-by-step execution details and DAG visualizations.

---

## 🚦 Migration Checklist

Use this checklist to track your migration progress:

- [ ] **Understand ALIEN evolution** (v1 → ALIEN² → Network)
- [ ] **Decide migration strategy** (hybrid vs full Network)
- [ ] **Preserve ALIEN² config** (`config/alien/` untouched)
- [ ] **Create Network config** (`config/network/agent.yaml`, `devices.yaml`)
- [ ] **Start devices as servers** (each device runs `python -m alien.server.app --port <port>`)
- [ ] **Test single-device workflow** (verify connectivity)
- [ ] **Test multi-device workflow** (cross-platform task)
- [ ] **Review trajectory reports** (`logs/network/*/output.md`)
- [ ] **Compare performance** (ALIEN² vs Network for your use cases)
- [ ] **Update automation scripts** (if using programmatic API)
- [ ] **Train team** (share this guide!)

---

**🎉 Congratulations!** You're now ready to leverage the full power of ALIEN³ Network's multi-device orchestration while preserving your existing ALIEN² workflows.

For questions or issues, please open an issue on [GitHub](https://github.com/DEVELOPER-DEEVEN/alien-project) or check the [documentation](https://github.com/DEVELOPER-DEEVEN/alien-project).
