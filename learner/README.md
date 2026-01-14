# The Knowledge Base (RAG)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Created by Deeven Seru**

## Table of Contents

1.  [Concept](#concept)
2.  [How to Teach the Agent](#how-to-teach-the-agent)
3.  [Enabling Knowledge](#enabling-knowledge)

## Concept

Sometimes, even smart AI doesn't know how to do *everything*. For specialized tasks (like "How to change a setting in proprietary software"), you need to teach it.

This module allows you to feed **Help Documents** (User Manuals) to the agent. When you ask a question, the agent looks up the relevant manual page before acting. This is called **RAG** (Retrieval-Augmented Generation).

## How to Teach the Agent

### 1. Write a Guide
Create a simple JSON file that explains the steps.

*Example (`chrome_help.json`):*
```json
{
    "application": "Google Chrome",
    "request": "How to clear history",
    "guidance": [
        "Click the three dots menu",
        "Select History",
        "Click Clear Browsing Data"
    ]
}
```

### 2. Index the Guides
Run this command to make the guides searchable:

```bash
python -m learner --app "Google Chrome" --docs ./my_guides_folder
```

## Enabling Knowledge

Once indexed, turn on the feature in your config file (`config.yaml`):

```yaml
RAG_OFFLINE_DOCS: True
```

Now, whenever you ask about Chrome, the agent will check your guide first!

---
*© 2026 Deeven Seru. All Rights Reserved.*
