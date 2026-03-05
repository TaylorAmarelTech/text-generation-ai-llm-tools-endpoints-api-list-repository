# Free & Open LLM API Endpoints Directory

> **The most comprehensive list of free and affordable LLM API endpoints for text generation.**
>
> 50 providers cataloged | 15 truly free (no credit card) | Last scanned: 2026-03-05 20:02 UTC

---

## Table of Contents

- [Quick Start](#quick-start)
- [Tier 1: Truly Free](#tier-1-truly-free-no-credit-card-ongoing)
- [Tier 2: Generous Free Tier](#tier-2-generous-free-tier-notable-limitations)
- [Tier 3: Free Credits on Signup](#tier-3-free-credits-on-signup-one-time-may-expire)
- [Tier 4: Freemium](#tier-4-freemium-credit-card-required)
- [Tier 5: Pay-per-use](#tier-5-pay-per-use-no-free-tier-very-cheap)
- [Routers / Aggregators](#routers--aggregators)
- [Local / Self-hosted](#local--self-hosted-unlimited-free-forever)
- [Cascade Example](#cascade-fallback-example)
- [Toolkit](#toolkit)
- [Status Legend](#status-legend)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## Quick Start

All Tier 1 providers use the **OpenAI SDK format** -- just change the `base_url` and `api_key`:

```python
"""Quick start: call any free LLM endpoint with the OpenAI SDK."""
from openai import OpenAI

# --- Pick any provider below (all free, no credit card) ---

# Groq (fastest, ~1K RPD for 70B models)
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key="YOUR_GROQ_KEY")
model = "llama-3.3-70b-versatile"

# Google Gemini (250 RPD Flash)
# client = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key="YOUR_GEMINI_KEY")
# model = "gemini-2.0-flash"

# Cerebras (1M tokens/day, blazing fast)
# client = OpenAI(base_url="https://api.cerebras.ai/v1", api_key="YOUR_CEREBRAS_KEY")
# model = "llama-3.3-70b"

# Mistral (1B tokens/mo per model)
# client = OpenAI(base_url="https://api.mistral.ai/v1", api_key="YOUR_MISTRAL_KEY")
# model = "mistral-small-latest"

# OpenRouter (25+ free models, 50 RPD)
# client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
# model = "deepseek/deepseek-r1:free"

response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Explain quantum computing in one paragraph."}],
    max_tokens=200,
)
print(response.choices[0].message.content)
```

---

## Tier 1: Truly Free (no credit card, ongoing)

| # | Provider | Endpoint | Free Limits | Best Models | OpenAI SDK | Status | Sign Up |
|---|----------|----------|-------------|-------------|------------|--------|---------|
| 1 | **Google Gemini** | `https://generativelanguage.googleapis.com/v1beta/openai/` | 250 RPD Flash, 100 RPD Pro | gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash | Yes | ❓ Not Tested | [Sign Up](https://aistudio.google.com) |
| 2 | **Groq** | `https://api.groq.com/openai/v1` | ~1K RPD 70B, 14K RPD 8B | llama-3.3-70b-versatile, llama-3.1-8b-instant, deepseek-r1-distill-llama-70b | Yes | ❓ Not Tested | [Sign Up](https://console.groq.com) |
| 3 | **Mistral** | `https://api.mistral.ai/v1` | 1B tokens/mo per model | mistral-large-latest, mistral-small-latest, open-mistral-nemo | Yes | ❓ Not Tested | [Sign Up](https://console.mistral.ai) |
| 4 | **Cerebras** | `https://api.cerebras.ai/v1` | 1M tokens/day, 8K context | llama-3.3-70b, llama-3.1-8b, qwen-3-32b | Yes | ❓ Not Tested | [Sign Up](https://cloud.cerebras.ai) |
| 5 | **OpenRouter** | `https://openrouter.ai/api/v1` | 25+ free models, 50 RPD each | deepseek/deepseek-r1:free, meta-llama/llama-3.3-70b-instruct:free, qwen/qwen3-235b-a22b:free | Yes | ❓ Not Tested | [Sign Up](https://openrouter.ai) |
| 6 | **Cloudflare Workers AI** | `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1` | 10K neurons/day | @cf/meta/llama-3.3-70b-instruct-fp8-fast, @cf/qwen/qwen2.5-coder-32b-instruct | Yes | ❓ Not Tested | [Sign Up](https://dash.cloudflare.com) |
| 7 | **GitHub Models** | `https://models.inference.ai.azure.com` | 50-150 RPD, 8K token limit | gpt-4o, Meta-Llama-3.1-70B-Instruct, Mistral-large-2411 | Yes | ❓ Not Tested | [Sign Up](https://github.com/marketplace/models) |
| 8 | **Zhipu (GLM)** | `https://open.bigmodel.cn/api/paas/v4` | GLM-4-Flash unlimited, no quota | glm-4-flash, glm-4-plus | Yes | ❓ Not Tested | [Sign Up](https://open.bigmodel.cn) |
| 9 | **OVHcloud AI Endpoints** | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` | 2 RPM anon, 400 RPM with auth | Meta-Llama-3_1-70B-Instruct, Qwen2.5-72B-Instruct | Yes | ❓ Not Tested | [Sign Up](https://ovhcloud.com) |
| 10 | **HuggingFace Inference** | `https://router.huggingface.co/v1` | ~300 req/hr | Qwen/Qwen2.5-72B-Instruct, meta-llama/Llama-3.3-70B-Instruct | Yes | ❓ Not Tested | [Sign Up](https://huggingface.co) |
| 11 | **Cohere** | `https://api.cohere.com/v2` | 1,000 calls/month forever | command-r-plus, command-r, command-light | Yes | ❓ Not Tested | [Sign Up](https://dashboard.cohere.com) |
| 12 | **NVIDIA NIM** | `https://integrate.api.nvidia.com/v1` | 1K-5K credits, 40 RPM | meta/llama-3.3-70b-instruct, deepseek-ai/deepseek-r1 | Yes | ❓ Not Tested | [Sign Up](https://build.nvidia.com) |
| 13 | **Glhf.chat** | `https://glhf.chat/api/openai/v1` | Free tier, 30 RPM | hf:meta-llama/Llama-3.3-70B-Instruct, hf:Qwen/Qwen2.5-72B-Instruct | Yes | ❓ Not Tested | [Sign Up](https://glhf.chat) |
| 14 | **Chutes.ai** | `https://api.chutes.ai/v1` | ~200 RPD | deepseek-ai/DeepSeek-R1, meta-llama/Llama-3.3-70B-Instruct | Yes | ❓ Not Tested | [Sign Up](https://chutes.ai) |
| 15 | **Venice.ai** | `https://api.venice.ai/api/v1` | 10 prompts/day free | llama-3.3-70b, qwen-2.5-72b | Yes | ❓ Not Tested | [Sign Up](https://venice.ai) |

<details>
<summary>Provider Notes (15)</summary>

- **Google Gemini**: Free tier is very generous. Supports OpenAI SDK via compatibility layer.
- **Groq**: Fastest inference. Custom LPU hardware.
- **Mistral**: French AI lab. Excellent multilingual support.
- **Cerebras**: Wafer-scale inference. Extremely fast.
- **OpenRouter**: Aggregator with 25+ permanently free model variants.
- **Cloudflare Workers AI**: Requires CLOUDFLARE_ACCOUNT_ID env var too. Edge inference.
- **GitHub Models**: Uses your GitHub PAT. Great for prototyping.
- **Zhipu (GLM)**: Chinese AI lab. GLM-4-Flash is completely free with no rate limits.
- **OVHcloud AI Endpoints**: European cloud. Can work without auth at reduced rate.
- **HuggingFace Inference**: Also offers free Inference Endpoints (serverless). Huge model catalog.
- **Cohere**: Great for RAG/search. Aya models for 23 languages.
- **NVIDIA NIM**: NVIDIA's inference microservices. Generous free credits.
- **Glhf.chat**: Run any HuggingFace model via vLLM. Prefix model IDs with 'hf:'.
- **Chutes.ai**: Decentralized GPU network. Free tier available.
- **Venice.ai**: Privacy-focused. Uncensored models. May need credits for API.

</details>

---

## Tier 2: Generous Free Tier (notable limitations)

| # | Provider | Endpoint | Free Limits | Best Models | OpenAI SDK | Status | Sign Up |
|---|----------|----------|-------------|-------------|------------|--------|---------|
| 1 | **Fireworks AI** | `https://api.fireworks.ai/inference/v1` | 10 RPM, $1 trial credits | accounts/fireworks/models/llama-v3p3-70b-instruct, accounts/fireworks/models/deepseek-v3 | Yes | ❓ Not Tested | [Sign Up](https://fireworks.ai) |
| 2 | **AIMLAPI** | `https://api.aimlapi.com/v1` | 10 req/hr, 50K credits | gpt-4o, claude-3-5-sonnet, meta-llama/Llama-3.3-70B-Instruct-Turbo | Yes | ❓ Not Tested | [Sign Up](https://aimlapi.com) |
| 3 | **Inference.net** | `https://api.inference.net/v1` | $1 + $25 (survey) | deepseek-ai/DeepSeek-R1, meta-llama/Llama-3.1-70B-Instruct | Yes | ❓ Not Tested | [Sign Up](https://inference.net) |
| 4 | **NLP Cloud** | `https://api.nlpcloud.io/v1` | 3 RPM ongoing, $15 credits | finetuned-llama-3-70b, chatdolphin | No | ❓ Not Tested | [Sign Up](https://nlpcloud.com) |
| 5 | **Coze (ByteDance)** | `https://api.coze.com/v1` | Free tier (bot-based) | Via bots: GPT-4o, Gemini, Claude | Yes | ❓ Not Tested | [Sign Up](https://coze.com) |

<details>
<summary>Provider Notes (5)</summary>

- **Fireworks AI**: Very fast. Supports function calling on open models.
- **AIMLAPI**: Aggregator with 300+ models including GPT, Claude, open-source.
- **Inference.net**: Decentralized inference. Complete survey for extra credits.
- **NLP Cloud**: Also has NER, summarization, translation. Custom API format.
- **Coze (ByteDance)**: Build bots that call underlying LLMs. ByteDance platform.

</details>

---

## Tier 3: Free Credits on Signup (one-time, may expire)

| # | Provider | Endpoint | Free Limits | Best Models | OpenAI SDK | Status | Sign Up |
|---|----------|----------|-------------|-------------|------------|--------|---------|
| 1 | **xAI / Grok** | `https://api.x.ai/v1` | $25 + $150/mo (data sharing) | grok-3, grok-3-mini, grok-2 | Yes | ❓ Not Tested | [Sign Up](https://console.x.ai) |
| 2 | **DeepSeek** | `https://api.deepseek.com/v1` | 5M tokens (30 days) | deepseek-chat, deepseek-reasoner | Yes | ❓ Not Tested | [Sign Up](https://platform.deepseek.com) |
| 3 | **DeepInfra** | `https://api.deepinfra.com/v1/openai` | $5 credits | meta-llama/Llama-3.3-70B-Instruct, deepseek-ai/DeepSeek-R1 | Yes | ❓ Not Tested | [Sign Up](https://deepinfra.com) |
| 4 | **SambaNova** | `https://api.sambanova.ai/v1` | $5 credits + free tier (3 months) | Meta-Llama-3.1-405B-Instruct, Meta-Llama-3.3-70B-Instruct | Yes | ❓ Not Tested | [Sign Up](https://cloud.sambanova.ai) |
| 5 | **Together AI** | `https://api.together.xyz/v1` | $5 credits | meta-llama/Llama-3.3-70B-Instruct-Turbo, deepseek-ai/DeepSeek-R1 | Yes | ❓ Not Tested | [Sign Up](https://together.ai) |
| 6 | **AI21 Labs** | `https://api.ai21.com/studio/v1` | $10 credits (3 months) | jamba-1.5-large, jamba-1.5-mini | Yes | ❓ Not Tested | [Sign Up](https://studio.ai21.com) |
| 7 | **Upstage** | `https://api.upstage.ai/v1/solar` | $10 credits (3 months) | solar-pro | Yes | ❓ Not Tested | [Sign Up](https://console.upstage.ai) |
| 8 | **Scaleway** | `https://api.scaleway.ai/v1` | 1M tokens (one-time) | llama-3.3-70b-instruct, deepseek-r1 | Yes | ❓ Not Tested | [Sign Up](https://console.scaleway.com) |
| 9 | **Alibaba DashScope** | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | 1M tokens/model | qwen-max, qwen-plus, qwen-turbo | Yes | ❓ Not Tested | [Sign Up](https://alibabacloud.com) |
| 10 | **Nebius AI Studio** | `https://api.studio.nebius.ai/v1` | $1 credits | meta-llama/Llama-3.1-70B-Instruct, mistralai/Mistral-7B-Instruct-v0.3 | Yes | ❓ Not Tested | [Sign Up](https://studio.nebius.ai) |
| 11 | **Kluster.ai** | `https://api.kluster.ai/v1` | $5 credits | Meta-Llama-3.1-405B-Instruct, Qwen2.5-72B-Instruct | Yes | ❓ Not Tested | [Sign Up](https://kluster.ai) |
| 12 | **Friendli** | `https://api.friendli.ai/v1` | $10 credits | meta-llama-3.3-70b-instruct, mixtral-8x7b-instruct-v0-1 | Yes | ❓ Not Tested | [Sign Up](https://friendli.ai) |
| 13 | **Hyperbolic** | `https://api.hyperbolic.xyz/v1` | $1-$50 credits | deepseek-ai/DeepSeek-V3, meta-llama/Llama-3.3-70B-Instruct | Yes | ❓ Not Tested | [Sign Up](https://app.hyperbolic.xyz) |
| 14 | **Novita AI** | `https://api.novita.ai/v3/openai` | $0.50 credits (1 year) | meta-llama/llama-3.3-70b-instruct | Yes | ❓ Not Tested | [Sign Up](https://novita.ai) |
| 15 | **SiliconCloud (SiliconFlow)** | `https://api.siliconflow.cn/v1` | Small credits on signup | deepseek-ai/DeepSeek-V3, Qwen/Qwen2.5-72B-Instruct | Yes | ❓ Not Tested | [Sign Up](https://siliconflow.com) |
| 16 | **Eden AI** | `https://api.edenai.co/v2` | $10 credits | Multi-provider aggregator | No | ❓ Not Tested | [Sign Up](https://edenai.co) |
| 17 | **Lepton AI** | `https://api.lepton.ai/v1` | Trial credits | llama-3.3-70b | Yes | ❓ Not Tested | [Sign Up](https://lepton.ai) |

<details>
<summary>Provider Notes (17)</summary>

- **xAI / Grok**: $150/mo free if you allow data sharing. 2M context window on Grok 3.
- **DeepSeek**: Cheapest frontier model. $0.014/M for cache hits. V3 is 685B MoE.
- **DeepInfra**: 100+ models. Very competitive pricing after credits.
- **SambaNova**: Custom RDU hardware. Fast inference on large models.
- **Together AI**: 200+ models. Great fine-tuning support.
- **AI21 Labs**: SSM-Transformer hybrid (Jamba). 256K context.
- **Upstage**: Korean AI lab. Solar Pro 3 is a 102B MoE model.
- **Scaleway**: European cloud provider. GDPR-compliant.
- **Alibaba DashScope**: Alibaba Cloud's AI platform. Qwen model family.
- **Nebius AI Studio**: Yandex spin-off. European GPU cloud.
- **Kluster.ai**: Batch inference specialist. Good for high-throughput.
- **Friendli**: Korean inference startup. Fast and cost-effective.
- **Hyperbolic**: Decentralized compute. Variable free credits.
- **Novita AI**: Also has image generation and training.
- **SiliconCloud (SiliconFlow)**: Chinese inference platform. Competitive pricing.
- **Eden AI**: Aggregates OpenAI, Google, Anthropic, etc. under one API.
- **Lepton AI**: Fast serverless inference.

</details>

---

## Tier 4: Freemium (credit card required)

| # | Provider | Endpoint | Free Limits | Best Models | OpenAI SDK | Status | Sign Up |
|---|----------|----------|-------------|-------------|------------|--------|---------|
| 1 | **OpenAI** | `https://api.openai.com/v1` | $5 credits (3 months) | gpt-4o, gpt-4o-mini, o3-mini | Yes | ❓ Not Tested | [Sign Up](https://platform.openai.com) |
| 2 | **Anthropic** | `https://api.anthropic.com/v1` | $5-10 credits | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001 | No | ❓ Not Tested | [Sign Up](https://console.anthropic.com) |
| 3 | **Perplexity** | `https://api.perplexity.ai` | $5/mo (with Pro subscription) | sonar, sonar-pro, sonar-reasoning | Yes | ❓ Not Tested | [Sign Up](https://docs.perplexity.ai) |

<details>
<summary>Provider Notes (3)</summary>

- **OpenAI**: Industry standard. Credit card required for API access.
- **Anthropic**: Not OpenAI-compatible. Uses Messages API + x-api-key header.
- **Perplexity**: Search-grounded LLM. Answers include citations.

</details>

---

## Tier 5: Pay-per-use (no free tier, very cheap)

| # | Provider | Endpoint | Cheapest Rate | Best Models | OpenAI SDK | Sign Up |
|---|----------|----------|---------------|-------------|------------|---------|
| 1 | **Moonshot / Kimi** | `https://api.moonshot.cn/v1` | None (very cheap: $0.10/M cache hit) | moonshot-v1-128k, kimi-k2.5 | Yes | [platform.moonshot.ai](https://platform.moonshot.ai) |
| 2 | **MiniMax** | `https://api.minimax.chat/v1` | None (8% of Claude Sonnet pricing) | abab6.5s-chat, abab5.5-chat | Yes | [platform.minimax.io](https://platform.minimax.io) |

<details>
<summary>Provider Notes (2)</summary>

- **Moonshot / Kimi**: Chinese AI. 256K context. Extremely cheap with caching.
- **MiniMax**: Chinese AI. Very cost-effective.

</details>

---

## Routers / Aggregators

| # | Provider | Endpoint | Free? | What It Does | Sign Up |
|---|----------|----------|-------|--------------|---------|
| 1 | **Requesty** | `https://router.requesty.ai/v1` | Free credits | Auto-failover between providers. | [requesty.ai](https://requesty.ai) |
| 2 | **Portkey** | `https://api.portkey.ai/v1` | Free tier | AI gateway with observability, guardrails, caching. | [portkey.ai](https://portkey.ai) |
| 3 | **Unify.ai** | `https://api.unify.ai/v0` | Free tier | ML-based model routing. Picks optimal provider per query. | [unify.ai](https://unify.ai) |
| 4 | **LiteLLM (self-hosted)** | `http://localhost:4000/v1` | Free (open source) | Open-source proxy. Unified format for all providers. | [github.com/BerriAI/litellm](https://github.com/BerriAI/litellm) |

<details>
<summary>Provider Notes (4)</summary>

- **Requesty**: Auto-failover between providers.
- **Portkey**: AI gateway with observability, guardrails, caching.
- **Unify.ai**: ML-based model routing. Picks optimal provider per query.
- **LiteLLM (self-hosted)**: Open-source proxy. Unified format for all providers.

</details>

---

## Local / Self-hosted (unlimited, free forever)

| # | Provider | Endpoint | Models | Status |
|---|----------|----------|--------|--------|
| 1 | **Ollama** | `http://localhost:11434/v1` | llama3.3, qwen2.5, deepseek-r1 | ⬛ Offline |
| 2 | **LM Studio** | `http://localhost:1234/v1` | Any GGUF model from HuggingFace | ⬛ Offline |
| 3 | **llama.cpp** | `http://localhost:8080/v1` | Any GGUF model | ⬛ Offline |
| 4 | **Jan.ai** | `http://localhost:1337/v1` | Any supported model | ⬛ Offline |

<details>
<summary>Provider Notes (4)</summary>

- **Ollama**: Easiest local setup. 50+ models. OpenAI-compatible.
- **LM Studio**: Best GUI for local models. Drag-and-drop GGUF loading.
- **llama.cpp**: Foundation for most local inference tools.
- **Jan.ai**: 100% offline desktop app.

</details>

---

## Cascade / Fallback Example

Chain multiple free providers with automatic failover:

```python
"""Cascade through free providers with automatic fallback."""
from openai import OpenAI
import os

PROVIDERS = [
    {"name": "Groq",      "base_url": "https://api.groq.com/openai/v1",       "key_env": "GROQ_API_KEY",      "model": "llama-3.3-70b-versatile"},
    {"name": "Cerebras",   "base_url": "https://api.cerebras.ai/v1",           "key_env": "CEREBRAS_API_KEY",  "model": "llama-3.3-70b"},
    {"name": "Mistral",    "base_url": "https://api.mistral.ai/v1",            "key_env": "MISTRAL_API_KEY",   "model": "mistral-small-latest"},
    {"name": "Gemini",     "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key_env": "GEMINI_API_KEY", "model": "gemini-2.0-flash"},
    {"name": "SambaNova",  "base_url": "https://api.sambanova.ai/v1",          "key_env": "SAMBANOVA_API_KEY", "model": "Meta-Llama-3.3-70B-Instruct"},
    {"name": "GitHub",     "base_url": "https://models.inference.ai.azure.com","key_env": "GITHUB_TOKEN",      "model": "gpt-4o"},
    {"name": "HuggingFace","base_url": "https://router.huggingface.co/v1",     "key_env": "HUGGINGFACE_API_KEY","model": "Qwen/Qwen2.5-72B-Instruct"},
    {"name": "OpenRouter", "base_url": "https://openrouter.ai/api/v1",         "key_env": "OPENROUTER_API_KEY","model": "deepseek/deepseek-r1:free"},
]


def ask(prompt: str, max_tokens: int = 500) -> str:
    """Try each provider in order until one succeeds."""
    for p in PROVIDERS:
        api_key = os.environ.get(p["key_env"], "")
        if not api_key:
            continue
        try:
            client = OpenAI(base_url=p["base_url"], api_key=api_key)
            resp = client.chat.completions.create(
                model=p["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            print(f"[Used: {p['name']}]")
            return resp.choices[0].message.content
        except Exception as e:
            print(f"[{p['name']} failed: {e}]")
            continue
    raise RuntimeError("All providers failed")


print(ask("What is the meaning of life?"))
```

---

## Toolkit

This repository includes a full-featured Python toolkit: scanner, AI-powered discovery, benchmarks, plugins, and a local proxy.

### Setup

```bash
# Clone the repo
git clone https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository.git
cd llm-endpoints-directory

# Install dependencies
pip install -r requirements.txt

# Copy and fill in your API keys (all optional)
cp .env.example .env

# Run the scanner
python main.py scan

# Regenerate this README with fresh results
python main.py scan --report
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `python main.py scan` | Test all endpoints and print results |
| `python main.py scan --tier free` | Test only free tier providers |
| `python main.py scan --provider Groq` | Test a specific provider |
| `python main.py scan --report` | Scan + regenerate README in one step |
| `python main.py report` | Generate README.md from last scan |
| `python main.py list` | List all providers with tier info |
| `python main.py discover` | AI-powered discovery of new endpoints |
| `python main.py discover --strategy llm_search` | Use a specific discovery strategy |
| `python main.py benchmark` | Measure latency, TTFT, tokens/sec |
| `python main.py models` | Fetch model catalogs from all providers |
| `python main.py export --format csv` | Export to JSON, CSV, YAML, or HTML |
| `python main.py compare "prompt"` | Compare providers side-by-side |
| `python main.py proxy --port 8000` | Start a local OpenAI-compatible proxy |

### AI-Powered Discovery

The discovery engine uses multiple strategies to find new LLM API endpoints:

- **web_search** -- Search the web via Brave, Serper, or Google Custom Search APIs
- **github_search** -- Search GitHub repos and awesome-lists for endpoint catalogs
- **llm_search** -- Ask an LLM to brainstorm new providers you might be missing
- **community** -- Scan Reddit and Hacker News for mentions of new APIs
- **directory_scrape** -- Check known API directories (e.g., OpenRouter model list)

Configure strategies and search API keys in `config.yaml` or via environment variables.

### Plugin System

Built-in plugins extend functionality:

| Plugin | Description |
|--------|-------------|
| `benchmark` | Measure TTFT, tokens/sec, total latency with streaming |
| `model_list` | Fetch and catalog all models from each provider |
| `export` | Export data to JSON, CSV, YAML, and HTML |
| `pricing` | Track pricing via OpenRouter's public API |
| `notify` | Send alerts to Slack, Discord, or generic webhooks |

Add custom plugins by dropping a `.py` file in `plugins/custom/`.

### Local Proxy

Route any OpenAI-compatible tool through your free providers:

```bash
python main.py proxy --port 8000

# Then point your apps to:
export OPENAI_BASE_URL=http://localhost:8000/v1
export OPENAI_API_KEY=anything
```

---

## Status Legend

| Icon | Meaning |
|------|---------|
| ✅ | Working -- endpoint responded successfully |
| 🟡 | Reachable -- endpoint alive but no completion test |
| 🔑 | Key Not Set -- API key not configured in `.env` |
| ❌ | Error / Auth Failed -- endpoint returned an error |
| 💳 | Needs Credits -- free credits exhausted |
| ⏳ | Rate Limited -- too many requests |
| ⏱️ | Timeout -- endpoint didn't respond in time |
| ⬛ | Offline -- local server not running |
| ⏭️ | Skipped -- no test model configured |

---

## Project Structure

```
llm-endpoints-directory/
|-- config.yaml              # All settings (scan, search, discovery, plugins)
|-- .env.example             # API key template (50+ keys, all optional)
|-- requirements.txt         # Python dependencies
|-- main.py                  # CLI entry point (scan, discover, benchmark, proxy, ...)
|-- config.py                # Configuration loader (YAML + env overrides)
|-- providers.py             # Provider registry (50+ providers, 7 tiers)
|-- scanner.py               # Async endpoint health checker
|-- report_generator.py      # README/report generator
|
|-- discovery/               # AI-powered endpoint discovery engine
|   |-- engine.py            # Orchestrator (dedup, verify, save candidates)
|   +-- strategies/
|       |-- base.py          # Strategy interface
|       |-- web_search.py    # Brave / Serper / Google Custom Search
|       |-- github_search.py # GitHub repos & awesome-lists
|       |-- llm_search.py    # Ask an LLM to find new providers
|       |-- community.py     # Reddit & Hacker News
|       +-- directory_scrape.py  # API directory scraping
|
|-- plugins/                 # Plugin system
|   |-- base.py              # Plugin base class + loader
|   |-- builtin/
|   |   |-- benchmark.py     # TTFT, tokens/sec, latency
|   |   |-- model_list.py    # Fetch model catalogs
|   |   |-- export.py        # JSON / CSV / YAML / HTML export
|   |   |-- pricing.py       # Pricing tracker (via OpenRouter)
|   |   +-- notify.py        # Slack / Discord / webhook alerts
|   +-- custom/              # Drop your own plugins here
|
|-- tools/                   # Standalone tools
|   |-- cascade.py           # Production cascade client with failover
|   |-- compare.py           # Side-by-side provider comparison
|   +-- proxy.py             # Local OpenAI-compatible proxy server
|
+-- data/                    # Generated data (gitignored)
    +-- .gitkeep
```

---

## Contributing

Found a new free LLM endpoint? Provider changed their free tier? Open an issue or PR!

1. Add the provider to `providers.py`
2. Run `python main.py scan --provider YourProvider`
3. Submit a PR with the updated `providers.py`

**Custom plugins:** Drop a `.py` file in `plugins/custom/` that subclasses `BasePlugin`.

**Custom strategies:** Add a new strategy in `discovery/strategies/` that subclasses `BaseStrategy`.

---

## License

MIT

---

*Auto-generated by [LLM Endpoint Scanner](https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository)*
