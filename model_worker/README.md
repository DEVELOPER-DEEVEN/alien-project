# Model Worker: The Inference Backend

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Component: LLM](https://img.shields.io/badge/Component-Inference_Engine-purple.svg)]()

**Architect: Deeven Seru**

---

## 📑 Table of Contents

1.  [Overview](#overview)
2.  [Supported Models Registry](#supported-models-registry)
3.  [Configuration Guide](#configuration-guide)
4.  [Developer Extension Guide](#developer-extension-guide)

---

## 1. Overview

The `model_worker/` directory abstracts the interaction with Large Language Models (LLMs). It provides a unified interface for token streaming, cost calculation, and error handling across heterogeneous providers (OpenAI, Azure, Gemini, Ollama).

Crucially, it handles **Multimodal Input**, automatically resizing and encoding base64 images to meet specific provider constraints.

---

## 2. Supported Models Registry

The following models are fully validated with the ALIEN2 vision pipeline.

| Provider | Model ID | Capabilities | Recommended Use |
| :--- | :--- | :--- | :--- |
| **OpenAI** | `gpt-4o` | Text + Vision | **Primary Driver**. Best reasoning/cost ratio. |
| **OpenAI** | `gpt-4-turbo` | Text + Vision | Legacy backup. |
| **Azure** | `gpt-4` | Text + Vision | Enterprise deployments. |
| **Google** | `gemini-1.5-pro` | Text + Vision | Large context tasks. |
| **Local** | `llava-v1.6` | Text + Vision | Offline / Privacy-sensitive tasks. |

---

## 3. Configuration Guide

To switch providers, update `aliens/config/agents.yaml`.

**Example: Switching to Azure OpenAI**

```yaml
HOST_AGENT:
  API_TYPE: "azure"
  API_BASE: "https://my-resource.openai.azure.com/"
  API_VERSION: "2024-02-15-preview"
  API_KEY: "..."
  API_MODEL: "gpt-4-turbo-v"
```

---

## 4. Developer Extension Guide

To add a new provider (e.g., Anthropic Claude 3), you must implement the `BaseModel` interface.

**Steps:**
1.  Create `model_worker/clients/claude_client.py`.
2.  Inherit from `BaseModel`.
3.  Implement `chat_completion(messages, **kwargs)`.
4.  Register the new class in `model_worker/factory.py`.

```python
class ClaudeClient(BaseModel):
    def chat_completion(self, messages, **kwargs):
        # Transform OpenAI format to Anthropic format
        payload = self._transform_messages(messages)
        return self.client.messages.create(model="claude-3-opus", **payload)
```

---
*© 2026 Deeven Seru. All Rights Reserved.*
