# Learning from Demonstration (LfD)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Created by Deeven Seru**

## Table of Contents

1.  [Concept](#concept)
2.  [Step-by-Step Guide](#step-by-step-guide)
3.  [Enabling the Feature](#enabling-the-feature)

## Concept

Teaching an AI by writing code is hard. Teaching it by **showing** it what to do is easy.

Since ALIEN can't physically see you, we use the **Windows Steps Recorder** to capture your actions. This tool analyzes that recording and converts it into a "Memory" that the agent can use later.

**Example:** Record yourself sending a specific email *once*, and the agent will learn how to do it *forever*.

## Step-by-Step Guide

### 1. Record Yourself
1.  Open the **Steps Recorder** app on Windows.
2.  Click **Start Record**.
3.  Perform the task (e.g., "Open Spotify and play Jazz").
4.  Click **Stop Record** and save the ZIP file.

### 2. Process the Recording
Run the processor tool to teach the agent:

```bash
python -m record_processor -r "Open Spotify and play Jazz" -p C:\path\to\recording.zip
```

The tool will analyze your clicks and save the lesson to the database.

## Enabling the Feature

Ensure this setting is enabled in your `config.yaml`:

```yaml
RAG_DEMONSTRATION: True
```

Now, when you ask for "Jazz", the agent will remember your lesson!

---
*© 2026 Deeven Seru. All Rights Reserved.*
