# Orion Protocol Tests

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Created by Deeven Seru**

## Table of Contents

1.  [Overview](#overview)
2.  [Running the Logic Tests](#running-the-logic-tests)

## Overview

The "Task Orion" is a complex data structure that represents a distributed plan. It looks like a web of connected tasks.

Since Generative AI (LLMs) creates these plans, they can sometimes be "hallucinated" or malformed. These tests ensure that our parser is robust enough to handle messy data without crashing.

## Running the Logic Tests

We use real-world logs to validate the parser.

```bash
python tests/network/orion/test_orion_parsing.py
```

If this passes, it means the network core is stable.

---
*© 2026 Deeven Seru. All Rights Reserved.*
