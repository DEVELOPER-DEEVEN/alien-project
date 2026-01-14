# Model Integration Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Created by Deeven Seru**

## Table of Contents

1.  [Supported Models](#supported-models)
2.  [Switching Providers](#switching-providers)
3.  [Local Models (Free)](#local-models-free)

## Supported Models

ALIEN is designed to be "Model Agnostic." This means you can swap out the brain of the agent easily. We support:

*   **OpenAI**: GPT-4o (Recommended for best performance).
*   **Google**: Gemini 1.5 Pro.
*   **Anthropic**: Claude 3 (Opus/Sonnet).
*   **Local**: Llama 3 or Mistral (via Ollama).

## Switching Providers

To switch the AI model, you don't need to change any code. Just update your `config.yaml` file.

**For Google Gemini:**
```yaml
API_TYPE: "Gemini"
API_KEY: "YOUR_GOOGLE_KEY"
API_MODEL: "gemini-1.5-pro"
```

**For Anthropic Claude:**
```yaml
API_TYPE: "claude"
API_KEY: "YOUR_ANTHROPIC_KEY"
API_MODEL: "claude-3-opus-20240229"
```

## Local Models (Free)

Want to run the agent for free without internet? You can use **Ollama**.

1.  Download Ollama from `ollama.com`.
2.  Run a vision-capable model: `ollama run llama3.2-vision`.
3.  Update Config:
    ```yaml
    API_TYPE: "Ollama"
    API_BASE: "http://localhost:11434"
    API_MODEL: "llama3.2-vision"
    ```

*Note: Local models might be slower and less accurate than GPT-4o.*

---
*© 2026 Deeven Seru. All Rights Reserved.*
