# ALIEN2: The Desktop Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/downloads/)

**Created by Deeven Seru**

## Table of Contents

1.  [Overview](#overview)
2.  [Key Capabilities](#key-capabilities)
3.  [Inside the Agent](#inside-the-agent)
4.  [Installation & Setup](#installation--setup)
5.  [Using the Agent](#using-the-agent)

## Overview

ALIEN2 is the core engine of the UFO project. It acts as an "Operating System Agent" that sits on top of Windows. It understands what is happening on your screen and can click buttons, type text, and navigate menus to complete tasks you give it.

Think of it as a helpful digital intern that sits at your computer and follows your instructions.

## Key Capabilities

*   **See & Interact**: It uses advanced computer vision to recognize icons, buttons, and text, even if they move around.
*   **Smart Planning**: It breaks complex requests (like "Send an email about X") into simple, logical steps.
*   **Safety First**: It asks for confirmation before doing anything risky, so you're always in control.
*   **Continuous Learning**: It can read help documents or watch you perform a task to learn new skills.

## Inside the Agent

The system works using two main "brains":

1.  **HostAgent**: The Manager. It listens to your request, picks the right app for the job, and supervises the process.
2.  **AppAgent**: The Worker. It specializes in using specific applications (like Word or Chrome) to get the job done.

## Installation & Setup

### 1. Simple Install

Open your terminal and run:

```bash
git clone https://github.com/deevenseru/UFO-main.git
cd UFO-main
pip install -r requirements.txt
```

### 2. Configuration

You need to give the agent a "brain" (an API key).

1.  Copy the template: `cp config/alien/agents.yaml.template config/alien/agents.yaml`
2.  Edit `config/alien/agents.yaml` and add your OpenAI or Azure API key.

## Using the Agent

### Command Line Mode

The fastest way to use ALIEN2 is via the command line.

**Example:**
```bash
python -m alien --task "Look up the weather in Tokyo and save it to a notepad file"
```

### Interactive Mode

Just run `python -m alien` and chat with the agent directly. It will guide you through the process.

> **Tip**: Make sure the application you want to use (e.g., Chrome) is installed on your computer.

---
*© 2026 Deeven Seru. All Rights Reserved.*
