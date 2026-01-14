# Network WebUI Backend

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Created by Deeven Seru**

## Table of Contents

1.  [What is this?](#what-is-this)
2.  [How it Works](#how-it-works)
3.  [Running the Server](#running-the-server)

## What is this?

This is the "Engine Room" of the visual dashboard. It connects your browser to the actual ALIEN network using **WebSockets**. This ensures that when an agent finishes a task, you see it on your screen instantly, without needing to refresh the page.

## How it Works

1.  **FastAPI Server**: Handles the web connections.
2.  **Event Stream**: Listens to the agents.
3.  **Real-Time Push**: Sends updates to the React frontend immediately.

## Running the Server

You typically don't run this manually (the main launch script handles it), but if you need to start it separately for testing:

```bash
python -m network --webui
```

This starts the backend on port 8000.

---
*© 2026 Deeven Seru. All Rights Reserved.*
