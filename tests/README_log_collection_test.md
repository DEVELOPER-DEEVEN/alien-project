# Scenario: Multi-OS Log Collection

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Created by Deeven Seru**

## Table of Contents

1.  [The Mission](#the-mission)
2.  [The Simulation](#the-simulation)
3.  [Executing the Mission](#executing-the-mission)

## The Mission

This is an end-to-end test capability. It simulates a common IT request:

> "Go to my Linux servers, grab the error logs, and compile a report on my Windows laptop."

This is difficult because it requires the agent to speak two languages (Linux Bash & Windows PowerShell) and coordinate file transfers.

## The Simulation

Instead of needing real servers, we use a simulation:
*   **Agents**: 2 Virtual Linux Servers + 1 Virtual Windows PC.
*   **Task**: Collect 5 log files.
*   **Outcome**: A collaborative Excel report.

## Executing the Mission

Run this command to watch the agents collaborate:

```bash
python -m pytest tests/test_linux_log_collection_excel_generation.py
```

---
*© 2026 Deeven Seru. All Rights Reserved.*
