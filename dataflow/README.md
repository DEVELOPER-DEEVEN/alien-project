# Dataflow: Training Data Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/downloads/)

**Created by Deeven Seru**

## Table of Contents

1.  [Purpose](#purpose)
2.  [The Workflow](#the-workflow)
3.  [How to Use](#how-to-use)
4.  [Output Data](#output-data)

## Purpose

The Dataflow tool helps researchers and developers build **Large Action Models (LAMs)**. It automates the process of collecting high-quality training data by recording the agent performing tasks in a controlled environment.

Instead of manually recording thousands of videos, Dataflow lets the agent "play" through tasks automatically and saves the results.

## The Workflow

The process mimics how we teach humans:

1.  **Instantiation (Setup)**: The system prepares the computer for the task (e.g., opens a specific document, loads a webpage).
2.  **Execution (Action)**: The agent attempts to solve the task while we record its every move (clicks, reasoning, screenshots).
3.  **Evaluation (Grading)**: We check if the agent succeeded and give it a score.

## How to Use

### Basic Execution

To run a data collection session for a specific task file:

```bash
python -m dataflow --dataflow --task_path ./tasks/sample_task.json
```

### Advanced Modes

You can run individual parts of the pipeline if you are debugging:

*   **Setup Only**: `python -m dataflow --instantiation ...`
*   **Run Only**: `python -m dataflow --execution ...`

## Output Data

All recordings are saved in the `results/` folder. Each session includes:
*   **Screenshots**: Visual history of the task.
*   **Action Logs**: User-friendly list of what the agent did.
*   **Performance Metrics**: How fast and accurate the agent was.

---
*© 2026 Deeven Seru. All Rights Reserved.*
