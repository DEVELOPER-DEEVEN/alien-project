# ALIEN Dataflow: Large Action Model Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Component: Data](https://img.shields.io/badge/Component-Data_Pipeline-purple.svg)]()

**Architect: Deeven Seru**

---

## 📑 Table of Contents

1.  [Mission Statement](#mission-statement)
2.  [The Data Pipeline](#the-data-pipeline)
3.  [Trajectory Schema](#trajectory-schema)
4.  [Privacy & Scrubbing](#privacy--scrubbing)

---

## 1. Mission Statement

The `dataflow/` module is responsible for the **Imitation Learning** lifecycle. While GPT-4V provides excellent zero-shot reasoning, it is expensive and slow. To build small, fast, and local models (SLMs), we must record "expert demonstrations" and fine-tune specialized models.

This module handles the recording, cleaning, and formatting of those demonstrations.

---

## 2. The Data Pipeline

The flow from "User Action" to "Training Token" involves four stages.

```mermaid
graph LR
    Recorder[Recorder] --> Raw[Raw Logs (.json)]
    Raw --> Scrubber[PII Scrubber]
    Scrubber --> Clean[Clean Dataset]
    Clean --> Formatter[Formatter]
    Formatter --> Tokens[Training Tokens]
```

1.  **Recording**: The Reviewer/Human-in-the-Loop confirms an action. We log the *Observation* (Screenshot) and the *Action* (Click).
2.  **Scrubbing**: Automated removal of sensitive data (passwords, usernames) using Named Entity Recognition (NER).
3.  **Instruction Tuning**: Converting the raw (State, Action) pairs into "User Request -> Assistant Action" dialogue formats common in LLM training (e.g., ShareGPT format).

---

## 3. Trajectory Schema

A single step in a trajectory is a rich object containing multimodal data.

**File Format**: `trajectory.jsonl`

```json
{
  "task_id": "uuid-1234",
  "step_id": 1,
  "timestamp": 1678888,
  "observation": {
    "screenshot_path": "images/step_1.png",
    "dom_tree": "<xml>...</xml>",
    "active_window": "Notepad"
  },
  "thought_trace": "The user wants to save. I see the 'File' menu...",
  "action": {
    "type": "click",
    "coordinates": [100, 200],
    "element_id": 42
  }
}
```

---

## 4. Privacy & Scrubbing

Before data leaves the local environment for training, it passes through the `PrivacyFilter`.

*   **Visual Blurring**: Detects text regions in screenshots looking like emails/keys and applies Gaussian blur.
*   **Text Redaction**: Replaces regex-matched patterns (IP addresses, SSNs) with `<REDACTED>`.

To configure scrubbing rules, edit `dataflow/config/scrubber.yaml`.

---
*© 2026 Deeven Seru. All Rights Reserved.*
