# Orion Scheduler Logic Tests

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Scope: Logic](https://img.shields.io/badge/Scope-Logic_Validation-green.svg)]()

**Architect: Deeven Seru**

---

## 1. Overview

The Orion Scheduler builds Directed Acyclic Graphs (DAGs) from LLM output. Since LLMs can hallucinate, the output is often non-deterministic.

These tests validate the **Parser Logic** that converts messy JSON into a strict DAG structure.

---

## 2. Validation Scenarios

### Cycle Detection
**Input**: `Task A -> Task B -> Task A`
**Expected Behavior**: Parser throws `CyclicDependencyError` (Deadlock prevention).

### Topological Sort
**Input**: `Task B depends on A`, `Task C depends on A`
**Expected Behavior**: Execution Order `[A, B, C]` or `[A, C, B]`. NEVER `[B, ...]`.

---

## 3. Execution

```bash
python -m pytest tests/network/orion/test_orion_parsing.py
```

---
*© 2026 Deeven Seru. All Rights Reserved.*
