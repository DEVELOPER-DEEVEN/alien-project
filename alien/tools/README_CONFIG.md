# Configuration Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Created by Deeven Seru**

## Table of Contents

1.  [Overview](#overview)
2.  [Validating Your Config](#validating-your-config)
3.  [Upgrading (Migration)](#upgrading-migration)

## Overview

Setting up complex AI agents can be tricky. One wrong API key or a missing setting can break everything. 
That's why I included a set of "Configuration Tools" to help you check your work automatically.

Think of these tools as a "Spell Check" for your settings.

## Validating Your Config

Before running the agent, it's a good idea to run the validator. It scans your files and alerts you if something is missing.

**How to run it:**

```bash
python -m alien.tools.validate_config all --show-config
```

**What it checks:**
*   Are all API keys present?
*   Are the file paths correct?
*   Is the YAML structure valid?

## Upgrading (Migration)

If you have an older version of the project, your config files might be in the wrong place. The Migration tool moves them to the new folder structure for you.

**How to run it:**

```bash
# Preview what will happen (Safe Mode)
python -m alien.tools.migrate_config --dry-run

# Apply changes
python -m alien.tools.migrate_config
```

It automatically creates a backup, so you don't have to worry about losing data!

---
*© 2026 Deeven Seru. All Rights Reserved.*
