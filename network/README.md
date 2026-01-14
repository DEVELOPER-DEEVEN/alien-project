# ALIEN3 Network: Multi-Device Orchestration

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Status: Experimental](https://img.shields.io/badge/Status-Experimental-orange.svg)]()

**Created by Deeven Seru**

## Table of Contents

1.  [What is the ALIEN Network?](#what-is-the-alien-network)
2.  [How It Works](#how-it-works)
3.  [Getting Started](#getting-started)
4.  [Visualizing the Network](#visualizing-the-network)

## What is the ALIEN Network?

While ALIEN2 controls a *single* computer, the ALIEN3 Network connects *multiple* devices together. It allows you to give a single command that requires actions across different computers—like a Windows PC and a Linux Server.

Imagine telling your main computer: *"Get the logs from the Linux server and make a chart in Excel here."* The Network handles the communication and coordination for you.

## How It Works

The system creates a "Task Orion"—a plan that maps out which device does what.

1.  **OrionAgent**: The central brain. It receives your request and splits it into sub-tasks.
2.  **Device Agents**: The workers. Each computer runs a small agent that listens for tasks from the OrionAgent.
3.  **Synchronization**: The devices talk to each other in real-time to share files and status updates.

## Getting Started

### 1. Start the Server

On your main computer (the coordinator), run:

```bash
python -m alien.server.app
```

### 2. Connect a Client

On any computer you want to control (including the main one), run:

```bash
python -m alien.client.client --server-address ws://[SERVER_IP]:5000
```

### 3. Send a Command

You can now send commands to the server, and it will dispatch them to the connected clients!

## Visualizing the Network

We provide a beautiful Web Dashboard to see your network in action.

Run this command to open the dashboard:
```bash
python -m network --webui
```

You'll see a live graph of your tasks and devices!

---
*© 2026 Deeven Seru. All Rights Reserved.*
