# Project Directory Structure

This repository implements **Alien³**, a multi-tier AgentOS architecture spanning from single-device automation (Alien²) to cross-device orchestration (cluster). This document provides an overview of the directory structure to help you understand the codebase organization.

> **New to Alien³?** Start with the [Documentation Home](index.md) for an introduction and [Quick Start Guide](getting_started/quick_start_cluster.md) to get up and running.

**Architecture Overview:**

- **🌌 cluster**: Multi-device DAG-based orchestration framework that coordinates agents across different platforms
- **🎯 Alien²**: Single-device Windows desktop agent system that can serve as cluster's sub-agent
- **🔌 AIP**: Agent Integration Protocol for cross-device communication
- **⚙️ Modular Configuration**: Type-safe configs in `config/cluster/` and `config/Alien/`

---

## 📦 Root Directory Structure

```
Alien/
├── cluster/                 # 🌌 Multi-device orchestration framework
├── Alien/                    # 🎯 Desktop AgentOS (can be cluster sub-agent)
├── config/                 # ⚙️ Modular configuration system
├── aip/                    # 🔌 Agent Integration Protocol
├── documents/              # 📖 MkDocs documentation site
├── vectordb/               # 🗄️ Vector database for RAG
├── learner/                # 📚 Help document indexing tools
├── record_processor/       # 🎥 Human demonstration parser
├── dataflow/               # 📊 Data collection pipeline
├── model_worker/           # 🤖 Custom LLM deployment tools
├── logs/                   # 📝 Execution logs (auto-generated)
├── scripts/                # 🛠️ Utility scripts
├── tests/                  # 🧪 Unit and integration tests
└── requirements.txt        # 📦 Python dependencies
```

---

## 🌌 cluster Framework (`cluster/`)

The cross-device orchestration framework that transforms natural language requests into executable DAG workflows distributed across heterogeneous devices.

### Directory Structure

```
cluster/
├── agents/                 # 🤖 network orchestration agents
│   ├── agent/              # networkAgent and basic agent classes
│   ├── states/             # Agent state machines
│   ├── processors/         # Request/result processing
│   └── presenters/         # Response formatting
│
├── network/          # 🌟 Core DAG management system
│   ├── task_network.py    # Tasknetwork - DAG container
│   ├── task_star.py        # TaskStar - Task nodes
│   ├── task_star_line.py   # TaskStarLine - Dependency edges
│   ├── enums.py            # Enums for network components
│   ├── editor/             # Interactive DAG editing with undo/redo
│   └── orchestrator/       # Event-driven execution coordination
│
├── session/                # 📊 Session lifecycle management
│   ├── cluster_session.py   # clusterSession implementation
│   └── observers/          # Event-driven observers
│
├── client/                 # 📡 Device management
│   ├── network_client.py              # Device registration interface
│   ├── device_manager.py                    # Device management coordinator
│   ├── config_loader.py                     # Configuration loading
│   ├── components/         # Device registry, connection manager, etc.
│   └── support/            # Client support utilities
│
├── core/                   # ⚡ Foundational components
│   ├── types.py            # Type system (protocols, dataclasses, enums)
│   ├── interfaces.py       # Interface definitions
│   ├── di_container.py     # Dependency injection container
│   └── events.py           # Event system
│
├── visualization/          # 🎨 Rich console visualization
│   ├── dag_visualizer.py   # DAG topology visualization
│   ├── task_display.py     # Task status displays
│   └── components/         # Visualization components
│
├── prompts/                # 💬 Prompt templates
│   ├── network_agent/ # networkAgent prompts
│   └── share/              # Shared examples
│
├── trajectory/             # 📈 Execution trajectory parsing
│
├── __main__.py             # 🚀 Entry point: python -m cluster
├── cluster.py               # Main cluster orchestrator
├── cluster_client.py        # cluster client interface
├── README.md               # cluster overview
└── README_ZH.md            # cluster overview (Chinese)
```

### Key Components

| Component | Description | Documentation |
|-----------|-------------|---------------|
| **networkAgent** | AI-powered agent that generates and modifies task DAGs | [cluster Overview](cluster/overview.md) |
| **Tasknetwork** | DAG container with validation and state management | [network](cluster/network/overview.md) |
| **TaskOrchestrator** | Event-driven execution coordinator | [network Orchestrator](cluster/network_orchestrator/overview.md) |
| **DeviceManager** | Multi-device coordination and assignment | [Device Manager](cluster/client/device_manager.md) |
| **Visualization** | Rich console DAG monitoring | [cluster Overview](cluster/overview.md) |

**cluster Documentation:**

- [cluster Overview](cluster/overview.md) - Architecture and concepts
- [Quick Start](getting_started/quick_start_cluster.md) - Get started with cluster
- [network Agent](cluster/network_agent/overview.md) - AI-powered task planning
- [network Orchestrator](cluster/network_orchestrator/overview.md) - Event-driven coordination
- [Device Manager](cluster/client/device_manager.md) - Multi-device management

---

## 🎯 Alien² Desktop AgentOS (`Alien/`)

Single-device desktop automation system implementing a two-tier agent architecture (HostAgent + AppAgent) with hybrid GUI-API automation.

### Directory Structure

```
Alien/
├── agents/                 # Two-tier agent implementation
│   ├── agent/              # Base agent classes (HostAgent, AppAgent)
│   ├── states/             # State machine implementations
│   ├── processors/         # Processing strategy pipelines
│   ├── memory/             # Agent memory and blackboard
│   └── presenters/         # Response presentation logic
│
├── server/                 # Server-client architecture components
│   ├── websocket_server.py # WebSocket server for remote agent control
│   └── handlers/           # Request handlers
│
├── client/                 # MCP client and device management
│   ├── mcp/                # MCP server manager
│   │   ├── local_servers/  # Built-in MCP servers (UI, CLI, Office COM)
│   │   └── http_servers/   # Remote MCP servers (hardware, Linux)
│   ├── Alien_client.py       # Alien² client implementation
│   └── computer.py         # Computer/device abstraction
│
├── automator/              # GUI and API automation layer
│   ├── ui_control/         # GUI automation (inspector, controller)
│   ├── puppeteer/          # Execution orchestration
│   └── *_automator.py      # App-specific automators (Excel, Word, etc.)
│
├── prompter/               # Prompt construction engines
├── prompts/                # Jinja2 prompt templates
│   ├── host_agent/         # HostAgent prompts
│   ├── app_agent/          # AppAgent prompts
│   └── share/              # Shared components
│
├── llm/                    # LLM provider integrations
├── rag/                    # Retrieval-Augmented Generation
├── trajectory/             # Task trajectory parsing
├── experience/             # Self-experience learning
├── module/                 # Core modules (session, round, context)
├── config/                 # Legacy config support
├── logging/                # Logging utilities
├── utils/                  # Utility functions
├── tools/                  # CLI tools (config conversion, etc.)
│
├── __main__.py             # Entry point: python -m Alien
└── Alien.py                  # Main Alien² orchestrator
```

### Key Components

| Component | Description | Documentation |
|-----------|-------------|---------------|
| **HostAgent** | Desktop-level orchestration with 7-state FSM | [HostAgent Overview](Alien-Unis/host_agent/overview.md) |
| **AppAgent** | Application-level execution with 6-state FSM | [AppAgent Overview](Alien-Unis/app_agent/overview.md) |
| **MCP System** | Extensible command execution framework | [MCP Overview](mcp/overview.md) |
| **Automator** | Hybrid GUI-API automation with fallback | [Core Features](Alien-Unis/core_features/hybrid_actions.md) |
| **RAG** | Knowledge retrieval from multiple sources | [Knowledge Substrate](Alien-Unis/core_features/knowledge_substrate/overview.md) |

**Alien² Documentation:**

- [Alien² Overview](Alien-Unis/overview.md) - Architecture and concepts
- [Quick Start](getting_started/quick_start_Alien-Unis.md) - Get started with Alien²
- [HostAgent States](Alien-Unis/host_agent/state.md) - Desktop orchestration states
- [AppAgent States](Alien-Unis/app_agent/state.md) - Application execution states
- [As cluster Device](Alien-Unis/as_cluster_device.md) - Using Alien² as cluster sub-agent
- [Creating Custom Agents](tutorials/creating_app_agent/overview.md) - Build your own application agents

---

## 🔌 Agent Integration Protocol (`aip/`)

Standardized message passing protocol for cross-device communication between cluster and Alien² agents.

```
aip/
├── messages.py             # Message types (Command, Result, Event, Error)
├── protocol/               # Protocol definitions
├── transport/              # Transport layers (HTTP, WebSocket, MQTT)
├── endpoints/              # API endpoints
├── extensions/             # Protocol extensions
└── resilience/             # Retry and error handling
```

**Purpose**: Enables cluster to coordinate Alien² agents running on different devices and platforms through standardized messaging over HTTP/WebSocket.

**Documentation**: See [AIP Overview](aip/overview.md) for protocol details and [Message Types](aip/messages.md) for message specifications.

---

## 🐧 Linux Agent

Lightweight CLI-based agent for Linux devices that integrates with cluster as a third-party device agent.

**Key Features**:
- **CLI Execution**: Execute shell commands on Linux systems
- **cluster Integration**: Register as device in cluster's multi-device orchestration
- **Simple Architecture**: Minimal dependencies, easy deployment
- **Cross-Platform Tasks**: Enable Windows + Linux workflows in cluster

**Configuration**: Configured in `config/Alien/third_party.yaml` under `THIRD_PARTY_AGENT_CONFIG.LinuxAgent`

**Linux Agent Documentation:**

- [Linux Agent Overview](linux/overview.md) - Architecture and capabilities
- [Quick Start](getting_started/quick_start_linux.md) - Setup and deployment
- [As cluster Device](linux/as_cluster_device.md) - Integration with cluster

---

## 📱 Mobile Agent

Android device automation agent that enables UI automation, app control, and mobile-specific operations through ADB integration.

**Key Features**:
- **UI Automation**: Touch, swipe, and text input via ADB
- **Visual Context**: Screenshot capture and UI hierarchy analysis
- **App Management**: Launch apps, navigate between applications
- **cluster Integration**: Serve as mobile device in cross-platform workflows
- **Platform Support**: Android devices (physical and emulators)

**Configuration**: Configured in `config/Alien/third_party.yaml` under `THIRD_PARTY_AGENT_CONFIG.MobileAgent`

**Mobile Agent Documentation:**

- [Mobile Agent Overview](mobile/overview.md) - Architecture and capabilities
- [Quick Start](getting_started/quick_start_mobile.md) - Setup and deployment
- [As cluster Device](mobile/as_cluster_device.md) - Integration with cluster

---

## ⚙️ Configuration (`config/`)

Modular configuration system with type-safe schemas and auto-discovery.

```
config/
├── cluster/                 # cluster configuration
│   ├── agent.yaml.template     # networkAgent LLM settings template
│   ├── agent.yaml              # networkAgent LLM settings (active)
│   ├── network.yaml      # network orchestration settings
│   ├── devices.yaml            # Multi-device registry
│   └── dag_templates/          # Pre-built DAG templates (future)
│
├── Alien/                    # Alien² configuration
│   ├── agents.yaml.template    # Agent LLM configs template
│   ├── agents.yaml             # Agent LLM configs (active)
│   ├── system.yaml             # System settings
│   ├── rag.yaml                # RAG settings
│   ├── mcp.yaml                # MCP server configs
│   ├── third_party.yaml        # Third-party agent configs (LinuxAgent, etc.)
│   └── prices.yaml             # API pricing data
│
├── config_loader.py        # Auto-discovery config loader
└── config_schemas.py       # Pydantic validation schemas
```

**Configuration Files:**

- Template files (`.yaml.template`) should be copied to `.yaml` and edited
- Active config files (`.yaml`) contain API keys and should NOT be committed
- **cluster**: Uses `config/cluster/agent.yaml` for networkAgent LLM settings
- **Alien²**: Uses `config/Alien/agents.yaml` for HostAgent/AppAgent LLM settings
- **Third-Party**: Configure LinuxAgent and HardwareAgent in `config/Alien/third_party.yaml`
- Use `python -m Alien.tools.convert_config` to migrate from legacy configs

**Configuration Documentation:**

- [Configuration Overview](configuration/system/overview.md) - System architecture
- [Agents Configuration](configuration/system/agents_config.md) - LLM and agent settings
- [System Configuration](configuration/system/system_config.md) - Runtime and execution settings
- [RAG Configuration](configuration/system/rag_config.md) - Knowledge retrieval
- [Third-Party Configuration](configuration/system/third_party_config.md) - LinuxAgent and external agents
- [MCP Configuration](configuration/system/mcp_reference.md) - MCP server setup
- [Model Configuration](configuration/models/overview.md) - LLM provider setup

---

## 📖 Documentation (`documents/`)

MkDocs documentation site with comprehensive guides and API references.

```
documents/
├── docs/                   # Markdown documentation source
│   ├── getting_started/    # Installation and quick starts
│   ├── cluster/             # cluster framework docs
│   ├── Alien-Unis/               # Alien² architecture docs
│   ├── linux/              # Linux agent documentation
│   ├── mcp/                # MCP server documentation
│   ├── aip/                # Agent Interaction Protocol docs
│   ├── configuration/      # Configuration guides
│   ├── infrastructure/     # Core infrastructure (agents, modules)
│   ├── server/             # Server-client architecture docs
│   ├── client/             # Client components docs
│   ├── tutorials/          # Step-by-step tutorials
│   ├── modules/            # Module-specific docs
│   └── about/              # Project information
│
├── mkdocs.yml              # MkDocs configuration
└── site/                   # Generated static site
```

**Documentation Sections**:

| Section | Description |
|---------|-------------|
| **Getting Started** | Installation, quick starts, migration guides |
| **cluster** | Multi-device orchestration, DAG workflows, device management |
| **Alien²** | Desktop agents, automation features, benchmarks |
| **Linux** | Linux agent integration, CLI executor for cluster |
| **MCP** | Server documentation, custom server development |
| **AIP** | Agent Interaction Protocol, message types, transport layers |
| **Configuration** | System settings, model configs, deployment |
| **Infrastructure** | Core components, agent design, server-client architecture |
| **Tutorials** | Creating agents, custom automators, advanced usage |

---

## 🗄️ Supporting Modules

### VectorDB (`vectordb/`)
Vector database storage for RAG knowledge sources (help documents, execution traces, user demonstrations). See [RAG Configuration](configuration/system/rag_config.md) for setup details.

### Learner (`learner/`)
Tools for indexing help documents into vector database for RAG retrieval. Integrates with the [Knowledge Substrate](Alien-Unis/core_features/knowledge_substrate/overview.md) feature.

### Record Processor (`record_processor/`)
Parses human demonstrations from Windows Step Recorder for learning from user actions.

### Dataflow (`dataflow/`)
Data collection pipeline for Large Action Model (LAM) training. See the [Dataflow](Alien-Unis/dataflow/overview.md) documentation for workflow details.

### Model Worker (`model_worker/`)
Custom LLM deployment tools for running local models. See [Model Configuration](configuration/models/overview.md) for supported providers.

### Logs (`logs/`)
Auto-generated execution logs organized by task and timestamp, including screenshots, UI trees, and agent actions.

---

## 🎯 cluster vs Alien² vs Linux Agent vs Mobile Agent: When to Use What?

| Aspect | cluster | Alien² | Linux Agent | Mobile Agent |
|--------|--------|------|-------------|--------------|
| **Scope** | Multi-device orchestration | Single-device Windows automation | Single-device Linux CLI | Single-device Android automation |
| **Use Cases** | Cross-platform workflows, distributed tasks | Desktop automation, Office tasks | Server management, CLI operations | Mobile app testing, UI automation |
| **Architecture** | DAG-based task workflows | Two-tier state machines | Simple CLI executor | UI automation via ADB |
| **Platform** | Orchestrator (platform-agnostic) | Windows | Linux | Android |
| **Complexity** | Complex multi-step workflows | Simple to moderate tasks | Simple command execution | UI interaction and app control |
| **Best For** | Cross-device collaboration | Windows desktop tasks | Linux server operations | Mobile app automation |
| **Integration** | Orchestrates all agents | Can be cluster device | Can be cluster device | Can be cluster device |

**Choosing the Right Framework:**

- **Use cluster** when: Tasks span multiple devices/platforms, complex workflows with dependencies
- **Use Alien² Standalone** when: Single-device Windows automation, rapid prototyping
- **Use Linux Agent** when: Linux server/CLI operations needed in cluster workflows
- **Use Mobile Agent** when: Android device automation, mobile app testing, UI interactions
- **Best Practice**: cluster orchestrates Alien² (Windows) + Linux Agent (Linux) + Mobile Agent (Android) for comprehensive cross-platform tasks

---

## 🚀 Quick Start

### cluster Multi-Device Orchestration

```bash
# Interactive mode
python -m cluster --interactive

# Single request
python -m cluster --request "Your cross-device task"
```

**Documentation**: [cluster Quick Start](getting_started/quick_start_cluster.md)

### Alien² Desktop Automation

```bash
# Interactive mode
python -m Alien --task <task_name>

# With custom config
python -m Alien --task <task_name> --config_path config/Alien/
```

**Documentation**: [Alien² Quick Start](getting_started/quick_start_Alien-Unis.md)

---

## 📚 Key Documentation Links

### Getting Started
- [Installation & Setup](getting_started/quick_start_cluster.md)
- [cluster Quick Start](getting_started/quick_start_cluster.md)
- [Alien² Quick Start](getting_started/quick_start_Alien-Unis.md)
- [Linux Agent Quick Start](getting_started/quick_start_linux.md)
- [Mobile Agent Quick Start](getting_started/quick_start_mobile.md)
- [Migration Guide](getting_started/migration_Alien-Unis_to_cluster.md)

### cluster Framework
- [cluster Overview](cluster/overview.md)
- [network Agent](cluster/network_agent/overview.md)
- [network Orchestrator](cluster/network_orchestrator/overview.md)
- [Task network](cluster/network/overview.md)
- [Device Manager](cluster/client/device_manager.md)

### Alien² Desktop AgentOS
- [Alien² Overview](Alien-Unis/overview.md)
- [HostAgent](Alien-Unis/host_agent/overview.md)
- [AppAgent](Alien-Unis/app_agent/overview.md)
- [Core Features](Alien-Unis/core_features/hybrid_actions.md)
- [As cluster Device](Alien-Unis/as_cluster_device.md)

### Linux Agent
- [Linux Agent Overview](linux/overview.md)
- [As cluster Device](linux/as_cluster_device.md)

### Mobile Agent
- [Mobile Agent Overview](mobile/overview.md)
- [As cluster Device](mobile/as_cluster_device.md)

### MCP System
- [MCP Overview](mcp/overview.md)
- [Local Servers](mcp/local_servers.md)
- [Creating MCP Servers](tutorials/creating_mcp_servers.md)

### Agent Integration Protocol
- [AIP Overview](aip/overview.md)
- [Message Types](aip/messages.md)
- [Transport Layers](aip/transport.md)

### Configuration
- [Configuration Overview](configuration/system/overview.md)
- [Agents Configuration](configuration/system/agents_config.md)
- [System Configuration](configuration/system/system_config.md)
- [Model Configuration](configuration/models/overview.md)
- [MCP Configuration](configuration/system/mcp_reference.md)

---

## 🏗️ Architecture Principles

Alien³ follows **SOLID principles** and established software engineering patterns:

- **Single Responsibility**: Each component has a focused purpose
- **Open/Closed**: Extensible through interfaces and plugins
- **Interface Segregation**: Focused interfaces for different capabilities
- **Dependency Inversion**: Dependency injection for loose coupling
- **Event-Driven**: Observer pattern for real-time monitoring
- **State Machines**: Well-defined states and transitions for agents
- **Command Pattern**: Encapsulated DAG editing with undo/redo

---

## 📝 Additional Resources

- **[GitHub Repository](https://github.com/microsoft/Alien)** - Source code and issues
- **[Research Paper](https://arxiv.org/abs/2504.14603)** - Alien³ technical details
- **[Documentation Site](https://microsoft.github.io/Alien/)** - Full documentation
- **[Video Demo](https://www.youtube.com/watch?v=QT_OhygMVXU)** - YouTube demonstration

---

**Next Steps:**

1. Start with [cluster Quick Start](getting_started/quick_start_cluster.md) for multi-device orchestration
2. Or explore [Alien² Quick Start](getting_started/quick_start_Alien-Unis.md) for single-device automation
3. Check [FAQ](faq.md) for common questions
4. Join our community and contribute!
