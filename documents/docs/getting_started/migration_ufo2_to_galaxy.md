# Migration Guide: Alien² to Alien³ cluster

This guide helps you understand the evolution from **Alien²** (Desktop AgentOS) to **Alien³ cluster** (Multi-Device AgentOS), and provides practical steps for migrating your workflows to leverage cluster's cross-device orchestration capabilities.

---

## 🌟 Understanding the Alien Evolution

### The Alien Journey

The Alien project has evolved through three major iterations, each addressing increasingly complex automation challenges:

```mermaid
graph LR
    A[Alien v1<br/>2024-02] -->|Desktop Agent| B[Alien²<br/>2025-04]
    B -->|Multi-Device| C[Alien³ cluster<br/>2025-11]
    
    style A fill:#e3f2fd
    style B fill:#c8e6c9
    style C fill:#fff9c4
```

#### **Alien (v1.0)** — The Beginning
📅 *Released: February 2024*

- **Vision**: Screenshot-based Windows automation
- **Architecture**: Multi-agent (HostAgent + AppAgents)
- **Approach**: GPT-4V + pure GUI automation (click/type)
- **Scope**: Single Windows desktop, cross-app workflows
- **Limitation**: No deep OS integration

**Key Innovation:** First LLM-powered multi-agent GUI automation framework

---

#### **Alien² (v2.0)** — Desktop AgentOS
📅 *Released: April 2025*  
📄 *Paper:* [Alien²: A Windows Agent for Seamless OS Interaction](https://arxiv.org/abs/2504.14603)

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

#### **Alien³ cluster** — Multi-Device AgentOS
📅 *Released: November 2025*  
📄 *Paper:* Alien³: Weaving the Digital Agent cluster *(Coming Soon)*

- **Vision**: Cross-device orchestration at scale
- **Architecture**: network-based distributed DAG orchestration
- **Innovations**:
  - ✅ **Task network** (dynamic DAG decomposition)
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

#### Alien v1 Architecture

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

#### Alien² Architecture

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

#### Alien³ cluster Architecture

**network Model (Distributed)**

```
User Request
    ↓
networkAgent
    ↓
Task network (DAG)
    ↓
Device 1, 2, 3... (Alien² instances)
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

### Use **Alien²** (Desktop AgentOS) When:

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

### Use **Alien³ cluster** When:

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

**Yes!** Alien² can run as a **device agent** in the cluster:

```
cluster (Orchestrator)
    ├── Windows Device (Alien² instance)
    ├── Linux Device (Alien² instance)
    └── Server Device (Alien² instance)
```

This is the **recommended hybrid approach** for complex workflows.

---

## 🔄 Key Concept Mapping

Understanding how Alien² concepts map to cluster:

| Alien² Concept | cluster Equivalent | Relationship |
|--------------|-------------------|--------------|
| **HostAgent** | **networkAgent** | Global orchestrator (but across devices) |
| **AppAgent** | **Device Agent (HostAgent)** | Local executor on each device |
| **Session** | **clusterSession** | Workflow execution context |
| **Round** | **network Round** | Orchestration iteration |
| **Action** | **TaskStar** | Executable unit (but on specific device) |
| **Blackboard** | **Task Results** | Inter-task communication |
| **Config File** | `config/Alien/` → `config/cluster/` | Configuration location |
| **Execution Mode** | `python -m Alien.server.app --port <port>` | Device runs as WebSocket server |

### Architecture Translation

**Alien² (Single Device):**
```python
# Alien² executes locally
python -m Alien --task "Create report from data.xlsx"

# HostAgent coordinates AppAgents on one desktop
HostAgent
  ├── ExcelAgent (data.xlsx)
  ├── WordAgent (report.docx)
  └── OutlookAgent (send email)
```

**cluster (Multi-Device):**
```python
# cluster orchestrates across devices
python -m cluster --request "Create report from data on Server, generate PDF on Windows"

# networkAgent creates DAG, assigns to devices
networkAgent
  └── Tasknetwork (DAG)
      ├── TaskStar-1: Fetch data → Linux Server
      ├── TaskStar-2: Process → GPU Workstation
      └── TaskStar-3: Generate PDF → Windows Desktop
```

---

## ⚙️ Configuration Migration

### Step 1: Preserve Alien² Configuration

**Keep your existing Alien² config** — you'll use it for device agents:

```
config/Alien/
├── agents.yaml          # LLM config for device agents
├── app_agent.yaml       # AppAgent settings
├── host_agent.yaml      # HostAgent settings
└── ...
```

**No changes needed** — each cluster device will use its own Alien² config.

---

### Step 2: Create cluster Configuration

cluster adds **new orchestration-level config**:

#### A. networkAgent LLM Config

```bash
# Copy template
copy config\cluster\agent.yaml.template config\cluster\agent.yaml
```

Edit `config/cluster/agent.yaml`:

```yaml
# networkAgent LLM (orchestrator)
network_AGENT:
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

**New in cluster:** Define all available devices

```bash
# Create device registry
notepad config\cluster\devices.yaml
```

```yaml
devices:
  # Your Windows desktop (existing Alien² instance)
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

**Capability Matching:** networkAgent uses these capabilities to assign tasks intelligently.

---

#### C. network Runtime Config

```bash
notepad config\cluster\network.yaml
```

```yaml
# network Orchestration Settings
network_ID: "my_network"
HEARTBEAT_INTERVAL: 30.0      # Device health check (seconds)
RECONNECT_DELAY: 5.0          # Auto-reconnect delay
MAX_CONCURRENT_TASKS: 6       # Parallel task limit
MAX_STEP: 15                  # Max orchestration rounds

# Device Configuration
DEVICE_INFO: "config/cluster/devices.yaml"

# Logging
LOG_TO_MARKDOWN: true         # Generate trajectory reports
```

---

## 🚀 Migration Steps

### Option 1: Keep Alien² for Local, Add cluster for Multi-Device

**Best for:** Gradual adoption, maintaining existing workflows

1. **Continue using Alien² for single-device tasks**
   ```bash
   python -m Alien --task "Your local task"
   ```

2. **Use cluster only when you need multi-device orchestration**
   ```bash
   python -m cluster --request "Your cross-device task"
   ```

3. **No migration required** — both coexist independently

---

### Option 2: Convert Alien² Instance to cluster Device

**Best for:** Leveraging cluster's orchestration for all workflows

#### Step 1: Start Alien² as Agent Server

**On each device** (Windows, Linux, etc.), run Alien² server:

```bash
# Windows Desktop
python -m Alien.server.app --port 5005

# Linux Workstation  
python -m Alien.server.app --port 5001

# GPU Server
python -m Alien.server.app --port 5002
```

**What this does:**
- Starts WebSocket server on the device
- Listens for task assignments from cluster
- Uses existing Alien² agents (HostAgent/AppAgent) for local execution
- Reports results back to networkClient

---

#### Step 2: Configure cluster Client

Create `config/cluster/devices.yaml` with all your devices (see Configuration section above).

---

#### Step 3: Launch cluster Client

```bash
# Interactive mode
python -m cluster --interactive

# Direct request
python -m cluster --request "Clone repo on laptop, build on server, test on Windows"
```

**What happens:**
1. networkAgent decomposes request into DAG
2. TaskStars assigned to devices based on capabilities
3. Devices execute tasks using their local Alien² agents
4. Results aggregated and presented to user

---

### Option 3: Programmatic Migration

**Best for:** Custom workflows, CI/CD integration

#### Alien² API (Before):

```python
from Alien.module.session_pool import SessionFactory, SessionPool
import asyncio

async def main():
    # Create Alien² session on local device
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

#### cluster API (After):

```python
from cluster import clusterClient
import asyncio

async def main():
    # cluster session coordinating multiple devices
    client = clusterClient(session_name="my_workflow")
    await client.initialize()
    
    result = await client.process_request(
        "Clone repo on laptop, build on server, test on Windows"
    )
    
    print(f"Workflow completed: {result}")
    await client.shutdown()

asyncio.run(main())
```

**Key Differences:**
- Both are **async** (Alien² v2.0+ uses asyncio)
- Alien²: Uses `SessionFactory` + `SessionPool` pattern
- cluster: Uses `clusterClient` for multi-device orchestration
- cluster returns **network results** (multi-device)
- cluster requires **device registration** first

---

## 📊 Feature Comparison

### Preserved Alien² Features in cluster

When running Alien² as a cluster device, you **keep all Alien² capabilities**:

| Alien² Feature | Available in cluster Device? | Notes |
|--------------|----------------------------|-------|
| ✅ Hybrid GUI–API execution | ✅ Yes | Each device uses its native Alien² agent |
| ✅ Windows UIA/Win32/COM | ✅ Yes | Full OS integration preserved |
| ✅ MCP server integration | ✅ Yes | Devices can use custom MCP servers |
| ✅ Continuous learning | ✅ Yes | Each device maintains its own RAG |
| ✅ Picture-in-Picture | ✅ Yes | Non-disruptive execution on each device |
| ✅ AppAgent specialization | ✅ Yes | HostAgent manages local AppAgents |

---

### New cluster-Only Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Task network** | DAG-based task decomposition | Complex workflow planning |
| **Parallel Execution** | Asynchronous multi-device tasks | 3-5x faster for parallelizable work |
| **Dynamic Adaptation** | Runtime DAG modification | Self-healing workflows |
| **Device Assignment** | Capability-based task placement | Optimal resource utilization |
| **Cross-Platform** | Windows + Linux + macOS support | Heterogeneous orchestration |
| **Event-Driven Coordination** | Observer pattern for task events | Reactive workflow control |
| **Formal Safety Guarantees** | I1-I3 invariants | Provably correct concurrent execution |

---

## 🛠️ Practical Examples

### Example 1: Simple Local Task

**Alien² (Before):**
```bash
python -m Alien --task "Create a presentation from data.xlsx"
```

**cluster (After) — Option A: Keep Alien²**
```bash
# No change needed — continue using Alien² for local tasks
python -m Alien --task "Create a presentation from data.xlsx"
```

**cluster (After) — Option B: Use cluster**
```bash
# cluster will assign to local Windows device automatically
python -m cluster --request "Create a presentation from data.xlsx on my desktop"
```

**When to use which?**
- Use Alien² if you only have one Windows desktop (simpler)
- Use cluster if you want logging/monitoring features

---

### Example 2: Cross-Device Workflow

**Alien² (Before):**
```bash
# ❌ Not possible — Alien² is single-device only
# You'd need to manually:
# 1. SSH to server
# 2. Run build command
# 3. Copy results back
# 4. Open locally
```

**cluster (After):**
```bash
python -m cluster --request \
  "Clone https://github.com/myrepo on laptop, \
   build Docker image on gpu_server, \
   deploy to staging server, \
   open logs on my Windows desktop"
```

**cluster automatically:**
1. Creates 4-task DAG
2. Assigns tasks to capable devices
3. Executes in parallel where possible
4. Streams results back

---

### Example 3: Data Pipeline

**Alien² (Before):**
```python
# Alien² requires manual orchestration across multiple steps
from Alien.module.session_pool import SessionFactory, SessionPool
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

**cluster (After):**
```python
import asyncio
from cluster import clusterClient

async def main():
    client = clusterClient(session_name="data_pipeline")
    await client.initialize()
    
    # Single request — cluster handles orchestration
    await client.process_request(
        "Fetch dataset from cloud to laptop, "
        "preprocess on linux_workstation, "
        "train model on gpu_server, "
        "visualize results on my Windows desktop"
    )
    
    await client.shutdown()

asyncio.run(main())
```

**cluster automatically:**
- Creates dependency chain
- Transfers data between devices
- Executes pipeline stages in order
- Handles failures with retries

---

## 🎓 Learning Path

### For Alien² Users

1. **Week 1: Understand Concepts**
   - Read [cluster Overview](../cluster/overview.md)
   - Understand Task network and DAG model
   - Compare with Alien² two-tier hierarchy

2. **Week 2: Hands-On**
   - Set up one Windows device as cluster agent
   - Run simple multi-step workflow
   - Compare logs: Alien² vs cluster

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

- **[cluster Quick Start](./quick_start_cluster.md)** — Step-by-step cluster setup
- **[Alien² Quick Start](./quick_start_Alien-Unis.md)** — Alien² reference
- **[Device Configuration](../configuration/system/cluster_devices.md)** — Device pool setup
- **[Agent Registration](../cluster/agent_registration/overview.md)** — How devices join cluster

### Architecture Deep Dives

- **[cluster Overview](../cluster/overview.md)** — network architecture
- **[Alien² Overview](../Alien-Unis/overview.md)** — Desktop AgentOS design
- **[network Agent](../cluster/network_agent/overview.md)** — DAG orchestration
- **[Task network](../cluster/network/overview.md)** — DAG structure

### Operational Guides

- **[Trajectory Report](../cluster/evaluation/trajectory_report.md)** — Execution logs
- **[Performance Metrics](../cluster/evaluation/performance_metrics.md)** — Monitoring
- **[AIP Protocol](../aip/overview.md)** — Device communication

---

## 🤝 Getting Help

### Common Questions

**Q: Can I still use Alien² after migrating to cluster?**  
A: Yes! They coexist. Use Alien² for simple local tasks, cluster for multi-device workflows.

**Q: Do I need to rewrite my custom agents?**  
A: No. Existing Alien² agents work as-is when running as cluster devices.

**Q: Is cluster production-ready?**  
A: cluster is in active development. Alien² is more mature for mission-critical single-device workflows.

**Q: Can I mix Windows and Linux devices?**  
A: Yes! That's cluster's key feature. Each device uses its native Alien² implementation.

**Q: How do I debug failed cross-device workflows?**  
A: Check `logs/cluster/<session>/output.md` for step-by-step execution details and DAG visualizations.

---

## 🚦 Migration Checklist

Use this checklist to track your migration progress:

- [ ] **Understand Alien evolution** (v1 → Alien² → cluster)
- [ ] **Decide migration strategy** (hybrid vs full cluster)
- [ ] **Preserve Alien² config** (`config/Alien/` untouched)
- [ ] **Create cluster config** (`config/cluster/agent.yaml`, `devices.yaml`)
- [ ] **Start devices as servers** (each device runs `python -m Alien.server.app --port <port>`)
- [ ] **Test single-device workflow** (verify connectivity)
- [ ] **Test multi-device workflow** (cross-platform task)
- [ ] **Review trajectory reports** (`logs/cluster/*/output.md`)
- [ ] **Compare performance** (Alien² vs cluster for your use cases)
- [ ] **Update automation scripts** (if using programmatic API)
- [ ] **Train team** (share this guide!)

---

**🎉 Congratulations!** You're now ready to leverage the full power of Alien³ cluster's multi-device orchestration while preserving your existing Alien² workflows.

For questions or issues, please open an issue on [GitHub](https://github.com/microsoft/Alien) or check the [documentation](https://microsoft.github.io/Alien/).
