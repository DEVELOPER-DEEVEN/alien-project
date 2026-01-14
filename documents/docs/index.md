# Welcome to ALIEN³ Documentation

<div align="center">
  <h1>
    <b>ALIEN³</b> <img src="./img/logo3.png" alt="ALIEN logo" width="80" style="vertical-align: -30px;"> : Weaving the Digital Agent Network
  </h1>
  <p><em>A Multi-Device Orchestration Framework for Cross-Platform Intelligent Automation</em></p>
</div>

[![arxiv](https://img.shields.io/badge/Paper-arXiv:2511.11332-b31b1b.svg)](https://arxiv.org/abs/2511.11332)
[![arxiv](https://img.shields.io/badge/Paper-arXiv:2504.14603-b31b1b.svg)](https://arxiv.org/abs/2504.14603)
![Python Version](https://img.shields.io/badge/Python-3776AB?&logo=python&logoColor=white-blue&label=3.10%20%7C%203.11)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/github/stars/microsoft/ALIEN)](https://github.com/DEVELOPER-DEEVEN/alien-project)
[![YouTube](https://img.shields.io/badge/YouTube-white?logo=youtube&logoColor=%23FF0000)](https://www.youtube.com/watch?v=QT_OhygMVXU)


---

<div align="center">
  <img src="./img/poster.png" width="100%" alt="ALIEN³ Evolution"/> 
</div>


## [LANG] About This Documentation

Welcome to the official documentation for **ALIEN³**, Microsoft's open-source framework for intelligent automation across devices and platforms. Whether you're looking to automate Windows applications or orchestrate complex workflows across multiple devices, this documentation will guide you through every step.

**What you'll find here:**

- [START] **[Quick Start Guides](getting_started/quick_start_network.md)** – Get up and running in minutes
- [PLAN] **[Core Concepts](network/overview.md)** – Understand the architecture and key components  
- ️ **[Configuration](configuration/system/agents_config.md)** – Set up your agents and models
- [CONFIG] **[Advanced Features](alien2/core_features/multi_action.md)** – Deep dive into powerful capabilities
- [THOUGHT] **[FAQ](faq.md)** – Common questions and troubleshooting

---

##  Choose Your Path

ALIEN³ consists of two complementary frameworks. Choose the one that best fits your needs, or use both together!

| Framework | Best For | Key Strength | Get Started |
|-----------|----------|--------------|-------------|
| **[ORION] Network** <br> <sub>[NEW] NEW & RECOMMENDED</sub> | Cross-device workflows<br>Complex automation<br>Parallel execution | Multi-device orchestration<br>DAG-based planning<br>Real-time monitoring | [Quick Start →](getting_started/quick_start_network.md) |
| **🪟 ALIEN²** <br> <sub> STABLE & LTS</sub> | Windows automation<br>Quick tasks<br>Learning basics | Deep Windows integration<br>Hybrid GUI + API<br>Stable & reliable | [Quick Start →](getting_started/quick_start_alien2.md) |

### [REASON] Decision Guide

| Question | Network | ALIEN² |
|----------|:------:|:----:|
| Need cross-device collaboration? | [OK] | [FAIL] |
| Complex multi-step workflows? | [OK] | ️ Limited |
| Windows-only automation? | [OK] | [OK] Optimized |
| Quick setup & learning? | ️ Moderate | [OK] Easy |
| Stable & reliable? |  Active Dev | [OK] LTS |

---

##  What's New in ALIEN³?

**ALIEN³ is a scalable, universal cross-device agent framework** that enables you to develop new device agents for different platforms and applications. Through the **Agent Interaction Protocol (AIP)**, custom device agents can seamlessly integrate into ALIEN³ Network for coordinated multi-device orchestration.

### Evolution Timeline

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#E8F4F8','primaryTextColor':'#1A1A1A','primaryBorderColor':'#7CB9E8','lineColor':'#A8D5E2','secondaryColor':'#B8E6F0','tertiaryColor':'#D4F1F4','fontSize':'16px','fontFamily':'Segoe UI, Arial, sans-serif'}}}%%
graph LR
    A["<b> ALIEN</b><br/><span style='font-size:14px'>February 2024</span><br/><span style='font-size:13px; color:#666'><i>GUI Agent for Windows</i></span>"] 
    B["<b>️ ALIEN²</b><br/><span style='font-size:14px'>April 2025</span><br/><span style='font-size:13px; color:#666'><i>Desktop AgentOS</i></span>"]
    C["<b>[ORION] ALIEN³ Network</b><br/><span style='font-size:14px'>November 2025</span><br/><span style='font-size:13px; color:#666'><i>Multi-Device Orchestration</i></span>"]
    
    A -->|Evolve| B
    B -->|Scale| C
    
    style A fill:#E8F4F8,stroke:#7CB9E8,stroke-width:2.5px,color:#1A1A1A,rx:15,ry:15
    style B fill:#C5E8F5,stroke:#5BA8D0,stroke-width:2.5px,color:#1A1A1A,rx:15,ry:15
    style C fill:#A4DBF0,stroke:#3D96BE,stroke-width:2.5px,color:#1A1A1A,rx:15,ry:15
```

### [START] ALIEN³ = **Network** (Multi-Device Orchestration) + **ALIEN²** (Device Agent)

ALIEN³ introduces **Network**, a revolutionary multi-device orchestration framework that coordinates intelligent agents across heterogeneous platforms. Built on five tightly integrated design principles:

1. ** Declarative Decomposition into Dynamic DAG** - Requests decomposed into structured DAG with TaskStars and dependencies for automated scheduling and runtime rewriting

2. **[CONTINUE] Continuous Result-Driven Graph Evolution** - Living orion that adapts to execution feedback through controlled rewrites and dynamic adjustments

3. ** Heterogeneous, Asynchronous & Safe Orchestration** - Capability-based device matching with async execution, safe locking, and formally verified correctness

4. ** Unified Agent Interaction Protocol (AIP)** - WebSocket-based secure coordination layer with fault tolerance and automatic reconnection

5. **️ Template-Driven MCP-Empowered Device Agents** - Lightweight toolkit for rapid agent development with MCP integration for tool augmentation

| Aspect | ALIEN² | ALIEN³ Network |
|--------|------|-------------|
| **Architecture** | Single Windows Agent | Multi-Device Orchestration |
| **Task Model** | Sequential ReAct Loop | DAG-based Orion Workflows |
| **Scope** | Single device, multi-app | Multi-device, cross-platform |
| **Coordination** | HostAgent + AppAgents | OrionAgent + TaskOrchestrator |
| **Device Support** | Windows Desktop | Windows, Linux, macOS, Android, Web |
| **Task Planning** | Application-level | Device-level with dependencies |
| **Execution** | Sequential | Parallel DAG execution |
| **Device Agent Role** | Standalone | Can serve as Network device agent |
| **Complexity** | Simple to Moderate | Simple to Very Complex |
| **Learning Curve** | Low | Moderate |
| **Cross-Device Collaboration** | [FAIL] Not Supported | [OK] Core Feature |
| **Setup Difficulty** | [OK] Easy | ️ Moderate |
| **Status** | [OK] LTS (Long-Term Support) |  Active Development |

###  Migration Path

**For ALIEN² Users:**
1. [OK] **Keep using ALIEN²** – Fully supported, actively maintained
2. [CONTINUE] **Gradual adoption** – Network can use ALIEN² as Windows device agent
3.  **Scale up** – Move to Network when you need multi-device capabilities
4. [PLAN] **Learning resources** – [Migration Guide](./getting_started/migration_alien2_to_network.md)

---

## [NEW] Capabilities at a Glance

### [ORION] Network Framework – What's Different?

####  Orion Planning

```
User Request
     ↓
OrionAgent
     ↓
  [Task DAG]
   /   |   \
Task1 Task2 Task3
(Win) (Linux)(Mac)
```

**Benefits:**
- Cross-device dependency tracking
- Parallel execution optimization
- Cross-device dataflow management

####  Device Assignment

```
Selection Criteria
  • Platform
  • Resource
  • Task requirements
  • Performance history
        ↓
  Auto-Assignment
        ↓
  Optimal Devices
```

**Smart Matching:**
- Capability-based selection
- Real-time resource monitoring
- Dynamic reallocation

#### [STATUS] Orchestration

```
Task1 → Running  [OK]
Task2 → Pending  [PAUSE]
Task3 → Running  [CONTINUE]
        ↓
   Completion
        ↓
   Final Report
```

**Orchestration:**
- Real-time status updates
- Automatic error recovery
- Progress tracking with feedback

---

### 🪟 ALIEN² Desktop AgentOS – Core Strengths

ALIEN² serves dual roles: **standalone Windows automation** and **Network device agent** for Windows platforms.

| Feature | Description | Documentation |
|---------|-------------|---------------|
| **Deep OS Integration** | Windows UIA, Win32, WinCOM native control | [Learn More](alien2/overview.md) |
| **Hybrid Actions** | GUI clicks + API calls for optimal performance | [Learn More](alien2/core_features/hybrid_actions.md) |
| **Speculative Multi-Action** | Batch predictions → **51% fewer LLM calls** | [Learn More](alien2/core_features/multi_action.md) |
| **Visual + UIA Detection** | Hybrid control detection for robustness | [Learn More](alien2/core_features/control_detection/hybrid_detection.md) |
| **Knowledge Substrate** | RAG with docs, demos, execution traces | [Learn More](alien2/core_features/knowledge_substrate/overview.md) |
| **Device Agent Role** | Can serve as Windows executor in Network orchestration | [Learn More](network/overview.md) |

**As Network Device Agent:**
- Receives tasks from OrionAgent through Network orchestration layer
- Executes Windows-specific operations using proven ALIEN² capabilities
- Reports status and results back to TaskOrchestrator
- Seamlessly participates in cross-device workflows

---

## ️ Architecture

### ALIEN³ Network – Multi-Device Orchestration

<div align="center">
  <img src="./img/overview2.png" alt="ALIEN³ Network Architecture" width="70%"/>
</div>

| Component | Role |
|-----------|------|
| **OrionAgent** | Plans and decomposes tasks into DAG workflows |
| **TaskOrion** | DAG representation with TaskStar nodes and dependencies |
| **Device Pool Manager** | Matches tasks to capable devices dynamically |
| **TaskOrchestrator** | Coordinates parallel execution and handles data flow |
| **Event System** | Real-time monitoring with observer pattern |

[[LANG] Learn More →](network/overview.md)

### ALIEN² – Desktop AgentOS

<div align="center">
  <img src="./img/framework2.png" alt="ALIEN² Architecture" width="75%"/>
</div>

| Component | Role |
|-----------|------|
| **HostAgent** | Desktop orchestrator, application lifecycle management |
| **AppAgents** | Per-application executors with hybrid GUI–API actions |
| **Knowledge Substrate** | RAG-enhanced learning from docs & execution history |
| **Speculative Executor** | Multi-action prediction for efficiency |

[[LANG] Learn More →](alien2/overview.md)

---

## [START] Quick Start

Ready to dive in? Follow these guides to get started with your chosen framework:

### [ORION] Network Quick Start (Multi-Device Orchestration)

Perfect for complex workflows across multiple devices and platforms.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure agents (see detailed guide for API key setup)
copy config\network\agent.yaml.template config\network\agent.yaml
copy config\alien\agents.yaml.template config\alien\agents.yaml

# 3. Start device agents
python -m alien.server.app --port 5000
python -m alien.client.client --ws --ws-server ws://localhost:5000/ws --client-id device_1 --platform windows

# 4. Launch Network
python -m network --interactive
```

**[LANG] [Complete Network Quick Start Guide →](getting_started/quick_start_network.md)**  
**️ [Network Configuration Details →](configuration/system/network_devices.md)**

### 🪟 ALIEN² Quick Start (Windows Automation)

Perfect for Windows-only automation tasks with quick setup.

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure (add your API keys)
copy config\alien\agents.yaml.template config\alien\agents.yaml

# 3. Run
python -m alien --task <task_name>
```

**[LANG] [Complete ALIEN² Quick Start Guide →](getting_started/quick_start_alien2.md)**  
**️ [ALIEN² Configuration Details →](configuration/system/agents_config.md)**

---

## [PLAN] Documentation Navigation

###  Getting Started

Start here if you're new to ALIEN³:

| Guide | Description | Framework |
|-------|-------------|-----------|
| [Network Quick Start](getting_started/quick_start_network.md) | Set up multi-device orchestration in 10 minutes | [ORION] Network |
| [ALIEN² Quick Start](getting_started/quick_start_alien2.md) | Start automating Windows in 5 minutes | 🪟 ALIEN² |
| [Linux Agent Quick Start](getting_started/quick_start_linux.md) | Automate Linux systems |  Linux |
| [Mobile Agent Quick Start](getting_started/quick_start_mobile.md) | Automate Android devices via ADB |  Mobile |
| [Choosing Your Path](choose_path.md) | Decision guide for selecting the right framework | Both |

### ️ Core Architecture

Understand how ALIEN³ works under the hood:

| Topic | Description | Framework |
|-------|-------------|-----------|
| [Network Overview](network/overview.md) | Multi-device orchestration architecture | [ORION] Network |
| [ALIEN² Overview](alien2/overview.md) | Desktop AgentOS architecture and concepts | 🪟 ALIEN² |
| [Task Orion](network/orion/overview.md) | DAG-based workflow representation | [ORION] Network |
| [OrionAgent](network/orion_agent/overview.md) | Intelligent task planner and decomposer | [ORION] Network |
| [Task Orchestrator](network/orion_orchestrator/overview.md) | Execution engine and coordinator | [ORION] Network |
| [AIP Protocol](aip/overview.md) | Agent communication protocol | [ORION] Network |

### ️ Configuration & Setup

Configure your agents, models, and environments:

| Topic | Description | Framework |
|-------|-------------|-----------|
| [Agent Configuration](configuration/system/agents_config.md) | LLM and agent settings | Both |
| [Network Devices](configuration/system/network_devices.md) | Device pool and capability management | [ORION] Network |
| [Model Providers](configuration/models/overview.md) | Supported LLMs (OpenAI, Azure, Qwen, etc.) | Both |

###  Tutorials & Examples

Learn through practical examples in the documentation:

| Topic | Description | Framework |
|-------|-------------|-----------|
| [Creating App Agents](tutorials/creating_app_agent/overview.md) | Build custom application agents | 🪟 ALIEN² |
| [Multi-Action Prediction](alien2/core_features/multi_action.md) | Efficient batch predictions | 🪟 ALIEN² |
| [Knowledge Substrate](alien2/core_features/knowledge_substrate/overview.md) | RAG-enhanced learning | 🪟 ALIEN² |

### [CONFIG] Advanced Topics

Deep dive into powerful features:

| Topic | Description | Framework |
|-------|-------------|-----------|
| [Multi-Action Prediction](alien2/core_features/multi_action.md) | Batch actions for 51% fewer LLM calls | 🪟 ALIEN² |
| [Hybrid Detection](alien2/core_features/control_detection/hybrid_detection.md) | Visual + UIA control detection | 🪟 ALIEN² |
| [Knowledge Substrate](alien2/core_features/knowledge_substrate/overview.md) | RAG-enhanced learning | 🪟 ALIEN² |
| [Orion Agent](network/orion_agent/overview.md) | Task planning and decomposition | [ORION] Network |
| [Task Orchestrator](network/orion_orchestrator/overview.md) | Execution coordination | [ORION] Network |

### ️ Development & Extension

Customize and extend ALIEN³:

| Topic | Description |
|-------|-------------|
| [Project Structure](project_directory_structure.md) | Understand the codebase layout |
| [Creating Custom Device Agents](tutorials/creating_device_agent/overview.md) | Build device agents for new platforms (mobile, web, IoT, etc.) |
| [Creating App Agents](tutorials/creating_app_agent/overview.md) | Build custom application agents |
| [Contributing Guide](about/CONTRIBUTING.md) | How to contribute to ALIEN³ |

###  Support & Troubleshooting

Get help when you need it:

| Resource | What You'll Find |
|----------|------------------|
| [FAQ](faq.md) | Common questions and answers |
| [GitHub Discussions](https://github.com/DEVELOPER-DEEVEN/alien-project/discussions) | Community Q&A |
| [GitHub Issues](https://github.com/DEVELOPER-DEEVEN/alien-project/issues) | Bug reports and feature requests |

---

## [STATUS] Feature Matrix

| Feature | ALIEN² Desktop AgentOS | ALIEN³ Network | Winner |
|---------|:--------------------:|:-----------:|:------:|
| **Windows Automation** | ⭐⭐⭐⭐⭐ Optimized | ⭐⭐⭐⭐ Supported | ALIEN² |
| **Cross-Device Tasks** | [FAIL] Not supported | ⭐⭐⭐⭐⭐ Core feature | Network |
| **Setup Complexity** | ⭐⭐⭐⭐⭐ Very easy | ⭐⭐⭐ Moderate | ALIEN² |
| **Learning Curve** | ⭐⭐⭐⭐⭐ Gentle | ⭐⭐⭐ Moderate | ALIEN² |
| **Task Complexity** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | Network |
| **Parallel Execution** | [FAIL] Sequential | ⭐⭐⭐⭐⭐ Native DAG | Network |
| **Stability** | ⭐⭐⭐⭐⭐ Stable | ⭐⭐⭐ Active dev | ALIEN² |
| **Monitoring Tools** | ⭐⭐⭐ Logs | ⭐⭐⭐⭐⭐ Real-time viz | Network |
| **API Flexibility** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Extensive | Network |

---

##  Use Cases & Examples

Explore what you can build with ALIEN³:

### [ORION] Network Use Cases (Cross-Device)

Perfect for complex, multi-device workflows:

- **Cross-Platform Data Pipelines**: Extract from Windows Excel → Process on Linux → Visualize on Mac
- **Distributed Testing**: Run tests on Windows → Deploy to Linux → Update mobile app
- **Multi-Device Monitoring**: Collect logs from multiple devices → Aggregate centrally
- **Complex Automation**: Orchestrate workflows across heterogeneous platforms

### 🪟 ALIEN² Use Cases (Windows)

Perfect for Windows automation and rapid task execution:

- **Office Automation**: Excel/Word/PowerPoint report generation and data processing
- **Web Automation**: Browser-based research, form filling, data extraction
- **File Management**: Organize, rename, convert files based on rules
- **System Tasks**: Windows configuration, software installation, backups

---

## [WEB] Community & Resources

###  Media & Videos

Check out our official deep dive of ALIEN on [YouTube](https://www.youtube.com/watch?v=QT_OhygMVXU).

### Media Coverage:
- [微软正式开源ALIEN²，Windows桌面迈入「AgentOS 时代」](https://www.jiqizhixin.com/articles/2025-05-06-13)
- [Microsoft's ALIEN: Smarter Windows Experience](https://the-decoder.com/microsofts-alien-abducts-traditional-user-interfaces-for-a-smarter-windows-experience/)
- [下一代Windows系统曝光：基于GPT-4V](https://baijiahao.baidu.com/s?id=1790938358152188625)

### [COMMENT] Get Help & Connect
- **[LANG] Documentation**: You're here! Browse the navigation above
- **[COMMENT] Discussions**: [GitHub Discussions](https://github.com/DEVELOPER-DEEVEN/alien-project/discussions)
- ** Issues**: [GitHub Issues](https://github.com/DEVELOPER-DEEVEN/alien-project/issues)
- ** Email**: [alien-agent@microsoft.com](mailto:alien-agent@microsoft.com)

###  Related Projects
- **[TaskWeaver](https://github.com/microsoft/TaskWeaver)** – Code-first LLM agent framework
- **[Windows Agent Arena](https://github.com/nice-mee/WindowsAgentArena)** – Evaluation benchmark
- **[GUI Agents Survey](https://vyokky.github.io/LLM-Brained-GUI-Agents-Survey/)** – Latest research

---

## [PLAN] Research & Citation

ALIEN³ is built on cutting-edge research in multi-agent systems and GUI automation.

### Papers

If you use ALIEN³ in your research, please cite:

**ALIEN³ Network Framework (2025)**
```bibtex
@article{zhang2025alien3,
  title={ALIEN$^3$: Weaving the Digital Agent Network}, 
  author = {Zhang, Chaoyun and Li, Liqun and Huang, He and Ni, Chiming and Qiao, Bo and Qin, Si and Kang, Yu and Ma, Minghua and Lin, Qingwei and Rajmohan, Saravan and Zhang, Dongmei},
  journal = {arXiv preprint arXiv:2511.11332},
  year    = {2025},
}
```

**ALIEN² Desktop AgentOS (2025)**
```bibtex
@article{zhang2025alien2,
  title   = {{ALIEN2: The Desktop AgentOS}},
  author  = {Zhang, Chaoyun and Huang, He and Ni, Chiming and Mu, Jian and Qin, Si and He, Shilin and Wang, Lu and Yang, Fangkai and Zhao, Pu and Du, Chao and Li, Liqun and Kang, Yu and Jiang, Zhao and Zheng, Suzhen and Wang, Rujia and Qian, Jiaxu and Ma, Minghua and Lou, Jian-Guang and Lin, Qingwei and Rajmohan, Saravan and Zhang, Dongmei},
  journal = {arXiv preprint arXiv:2504.14603},
  year    = {2025}
}
```

**Original ALIEN (2024)**
```bibtex
@article{zhang2024alien,
  title   = {{ALIEN: A UI-Focused Agent for Windows OS Interaction}},
  author  = {Zhang, Chaoyun and Li, Liqun and He, Shilin and Zhang, Xu and Qiao, Bo and Qin, Si and Ma, Minghua and Kang, Yu and Lin, Qingwei and Rajmohan, Saravan and Zhang, Dongmei and Zhang, Qi},
  journal = {arXiv preprint arXiv:2402.07939},
  year    = {2024}
}
```

**[LANG] [Read the Papers →](https://arxiv.org/abs/2504.14603)**

---


## ️ Roadmap & Future

### ALIEN² Desktop AgentOS (Stable/LTS)
- [OK] Long-term support and maintenance  
- [OK] Windows device agent integration
-  Enhanced device capabilities
-  Picture-in-Picture mode

### ALIEN³ Network (Active Development)
- [OK] Orion Framework
- [OK] Multi-device coordination
- [CONTINUE] Mobile, Web, IoT agents
- [CONTINUE] Interactive visualization
-  Advanced fault tolerance

**Legend:** [OK] Done | [CONTINUE] In Progress |  Planned

---

## ️ License & Legal

- **License**: [MIT License](https://github.com/DEVELOPER-DEEVEN/alien-project/blob/main/LICENSE)
- **Disclaimer**: [Read our disclaimer](https://github.com/DEVELOPER-DEEVEN/alien-project/blob/main/DISCLAIMER.md)
- **Trademarks**: [Microsoft Trademark Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks)
- **Contributing**: [Contribution Guidelines](about/CONTRIBUTING.md)

---


## [START] Ready to Start?

Choose your framework and begin your automation journey:


### [ORION] Start with Network
**For multi-device orchestration**

[![Network Quick Start](https://img.shields.io/badge/Quick_Start-Network-blue?style=for-the-badge)](getting_started/quick_start_network.md)


### 🪟 Start with ALIEN²
**For Windows automation**

[![ALIEN² Quick Start](https://img.shields.io/badge/Quick_Start-ALIEN²-green?style=for-the-badge)](getting_started/quick_start_alien2.md)


### [LANG] Explore the Documentation

[Core Concepts](network/overview.md) | [Configuration](configuration/system/agents_config.md) | [FAQ](faq.md) | [GitHub](https://github.com/DEVELOPER-DEEVEN/alien-project)


---

<p align="center">
  <img src="./img/logo3.png" alt="ALIEN logo" width="60">
  <br>
  <em>From Single Agent to Digital Network</em>
  <br>
  <strong>ALIEN³ - Weaving the Future of Intelligent Automation</strong>
</p>

---
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-FX17ZGJYGC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-FX17ZGJYGC');
</script>