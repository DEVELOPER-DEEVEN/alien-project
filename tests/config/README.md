# Configuration Testing

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Created by Deeven Seru**

## Table of Contents

1.  [Why Test Configuration?](#why-test-configuration)
2.  [Running the Tests](#running-the-tests)
3.  [What is Covered](#what-is-covered)

## Why Test Configuration?

A typing error in a settings file is the #1 reason complex systems fail. We built a robust test suite to ensure that:
1.  Your settings are loaded correctly.
2.  Missing keys trigger clear error messages (instead of crashing randomly).
3.  Updating from an old version doesn't break your setup.

## Running the Tests

To verify that the configuration system is working correctly on your machine:

```bash
python -m unittest discover tests/config
```

## What is Covered

*   **Loader Tests**: Checks if YAML files are read properly.
*   **Validation Tests**: Ensures "Required" fields are actually required.
*   **Migration Tests**: Verifies that the upgrade tool safely moves data.

---
*© 2026 Deeven Seru. All Rights Reserved.*
