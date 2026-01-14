# ALIEN2: Intelligent Desktop Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://github.com/deevenseru/UFO-main)

**Created by Deeven Seru**

## Table of Contents

1.  [What is ALIEN2?](#what-is-alien2)
2.  [Why Use ALIEN2?](#why-use-alien2)
3.  [Getting Started](#getting-started)
4.  [How It Works](#how-it-works)
5.  [Core Components](#core-components)
6.  [Need Help?](#need-help)

## What is ALIEN2?

ALIEN2 is a smart assistant for your Windows desktop. Instead of clicking buttons yourself, you can simply type what you want to do in plain English, and ALIEN2 will do it for you. It uses advanced visual AI to "see" your screen and control your mouse and keyboard, just like a human would.

Whether you need to copy data between apps, organize files, or automate repetitive tasks, ALIEN2 turns complex workflows into simple commands.

## Why Use ALIEN2?

*   **Save Time**: Automate boring, repetitive tasks instantly.
*   **No Coding Required**: If you can write a sentence, you can use this tool.
*   **Works with Any App**: Since it looks at the screen, it works with Word, Chrome, Outlook, and almost any other Windows application.
*   **Safe & Secure**: You remain in control. The agent asks for permission before taking major actions.

## Getting Started

Follow these simple steps to get ALIEN2 running on your computer.

### Prerequisites

*   **OS**: Windows 10 or Windows 11.
*   **Python**: You need Python 3.10 or newer installed.
*   **API Key**: An OpenAI API key (for GPT-4o or GPT-4V).

### Installation Guide

1.  **Download the Code**
    Open your terminal and run:
    ```bash
    git clone https://github.com/deevenseru/UFO-main.git
    cd UFO-main
    ```

2.  **Install Requirements**
    This installs all the necessary libraries:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Your Agent**
    Set up your API key so the agent can "think":
    ```bash
    cp config/alien/agents.yaml.template config/alien/agents.yaml
    ```
    Open `config/alien/agents.yaml` in a text editor and paste your API key where indicated.

### Running Your First Task

To start the agent, simply type:

```bash
python -m alien
```

You will see a prompt. Try typing: *"Open Notepad and write a poem about robots."*

## How It Works

1.  **You Ask**: You type a request (e.g., "Delete all emails from yesterday").
2.  **It Plans**: The **HostAgent** breaks your request into smaller steps and decides which app to open.
3.  **It Acts**: The **AppAgent** takes over. It looks at the screen, finds the right buttons, and clicks them.
4.  **It Learns**: If you use the optional "Knowledge" features, it can learn from your previous tasks to get faster over time.

## Core Components

The project includes several powerful modules:

*   **ALIEN2 (Desktop Agent)**: The main tool for controlling your PC.
*   **ALIEN3 (Network)**: An experimental feature for connecting multiple computers together.
*   **Dataflow**: A tool for recording tasks to train even smarter AI models.

## Need Help?

If you run into issues or have questions, please check the following resources:
*   [Full Documentation](alien/README.md)
*   [Configuration Guide](alien/tools/README_CONFIG.md)

---
*© 2026 Deeven Seru. All Rights Reserved.*
