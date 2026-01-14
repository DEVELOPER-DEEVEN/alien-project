# Supported Models

ALIEN supports a wide variety of LLM models and APIs. You can configure different models for `HOST_AGENT`, `APP_AGENT`, `BACKUP_AGENT`, and `EVALUATION_AGENT` in the `config/alien/agents.yaml` file to optimize for performance, cost, or specific capabilities.

## Available Model Integrations

| Provider | Documentation | Visual Support | Authentication |
| --- | --- | --- | --- |
| **OpenAI** | [OpenAI API](./openai.md) | [OK] | API Key |
| **Azure OpenAI (AOAI)** | [Azure OpenAI API](./azure_openai.md) | [OK] | API Key / Azure AD |
| **Google Gemini** | [Gemini API](./gemini.md) | [OK] | API Key |
| **Anthropic Claude** | [Claude API](./claude.md) | [OK] | API Key |
| **Qwen (Alibaba)** | [Qwen API](./qwen.md) | [OK] | API Key |
| **DeepSeek** | [DeepSeek API](./deepseek.md) | [FAIL] | API Key |
| **Ollama** | [Ollama API](./ollama.md) | ️ Limited | Local |
| **OpenAI Operator** | [Operator (CUA)](./operator.md) | [OK] | Azure AD |
| **Custom Models** | [Custom API](./custom_model.md) | Depends | Varies |

## Model Selection Guide

### By Use Case

**For Production Deployments:**
- **Primary**: OpenAI GPT-4o or Azure OpenAI (enterprise features)
- **Cost-optimized**: GPT-4o-mini for APP_AGENT, GPT-4o for HOST_AGENT
- **Privacy-sensitive**: Ollama (local models)

**For Development & Testing:**
- **Fast iteration**: Gemini 2.0 Flash (high speed, low cost)
- **Local testing**: Ollama with llama2 or similar
- **Budget-friendly**: DeepSeek or Qwen models

**For Specialized Tasks:**
- **Computer control**: OpenAI Operator (CUA model)
- **Code generation**: DeepSeek-Coder or Claude
- **Long context**: Gemini 1.5 Pro (large context window)

### By Capability

**Vision Support (Screenshot Understanding):**
- [OK] OpenAI GPT-4o, GPT-4-turbo
- [OK] Azure OpenAI (vision-enabled deployments)
- [OK] Google Gemini (all 1.5+ models)
- [OK] Claude 3+ (all variants)
- [OK] Qwen-VL models
- ️ Ollama (llava models only)
- [FAIL] DeepSeek (text-only)

**JSON Schema Support:**
- [OK] OpenAI / Azure OpenAI
- [OK] Google Gemini
- ️ Limited: Claude, Qwen, Ollama

## Configuration Architecture

Each model is implemented as a separate class in the `alien/llm` directory, inheriting from the `BaseService` class in `alien/llm/base.py`. All models implement the `chat_completion` method to maintain a consistent interface.

**Key Configuration Files:**

- **`config/alien/agents.yaml`**: Primary agent configuration (HOST, APP, BACKUP, EVALUATION, OPERATOR)
- **`config/alien/system.yaml`**: System-wide LLM parameters (MAX_TOKENS, TEMPERATURE, etc.)
- **`config/alien/prices.yaml`**: Cost tracking for different models

## Multi-Provider Setup

You can mix and match providers for different agents to optimize cost and performance:

```yaml
# Use OpenAI for planning
HOST_AGENT:
  API_TYPE: "openai"
  API_MODEL: "gpt-4o"

# Use Azure OpenAI for execution (cost control)
APP_AGENT:
  API_TYPE: "aoai"
  API_MODEL: "gpt-4o-mini"

# Use Claude for evaluation
EVALUATION_AGENT:
  API_TYPE: "claude"
  API_MODEL: "claude-3-5-sonnet-20241022"
```

## Getting Started

1. Choose your LLM provider from the table above
2. Follow the provider-specific documentation to obtain API keys
3. Configure `config/alien/agents.yaml` with your credentials
4. Refer to the [Quick Start Guide](../../getting_started/quick_start_alien2.md) to begin

**For detailed configuration options:**

- [Agent Configuration Guide](../system/agents_config.md) - Complete configuration reference
- [System Configuration](../system/system_config.md) - LLM parameters and behavior
- [Quick Start Guide](../../getting_started/quick_start_alien2.md) - Step-by-step setup