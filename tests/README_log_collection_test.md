# End-to-End Scenario: Multi-OS Log Collection

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Type: Integration](https://img.shields.io/badge/Type-System_Integration-orange.svg)]()

**Architect: Deeven Seru**

---

## 📑 Table of Contents

1.  [Scenario Description](#scenario-description)
2.  [Simulated Environment](#simulated-environment)
3.  [Success Criteria](#success-criteria)

---

## 1. Scenario Description

This test simulates a real-world IT Admin task:
**"Collect `/var/log/syslog` from three Linux servers and compile a summary Excel report on the Admin's Windows workstation."**

This requires:
1.  **Orchestration**: Splitting the task into 4 sub-tasks (3 downloads + 1 compile).
2.  **Cross-Platform Control**: SSH into Linux, Excel automation on Windows.
3.  **Data Transfer**: Moving files between nodes.

---

## 2. Simulated Environment

Instead of physical machines, we use `docker` containers and `mock` interfaces.

*   `Agent_Linux_1` (Mock SSH)
*   `Agent_Linux_2` (Mock SSH)
*   `Agent_Windows_Admin` (Local Machine)

---

## 3. Success Criteria

The test passes if and only if:
1.  `report.xlsx` is created on the Windows Desktop.
2.  The Excel file contains 3 generic log entries.
3.  Total token cost is under $0.50.

---
*© 2026 Deeven Seru. All Rights Reserved.*
