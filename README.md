# Free & Open LLM API Endpoints Directory

<p align="center">
  <a href="https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/providers-50-brightgreen.svg" alt="Providers: 50">
  <img src="https://img.shields.io/badge/free%20tier-15-success.svg" alt="Free: 15">
  <a href="https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository/stargazers"><img src="https://img.shields.io/github/stars/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository?style=social" alt="GitHub Stars"></a>
</p>

<p align="center">
  <strong>The most comprehensive, actively-maintained directory of free and affordable LLM API endpoints.</strong><br>
  50 providers cataloged &bull; 15 truly free (no credit card) &bull; All OpenAI SDK compatible &bull; Updated: 2026-03-06 02:35 UTC
</p>

---

## Why This Exists

There are **dozens** of LLM API providers offering free tiers, trial credits, and affordable pricing -- but finding them, comparing limits, and knowing which ones actually work is a scattered mess. This repository maintains:

- A **curated, verified directory** of every provider with free or cheap LLM API access
- A **scanner toolkit** that automatically tests endpoints and reports status
- An **AI-powered discovery engine** that finds new providers as they launch
- **Production-ready code** (cascade client, local proxy, benchmarks) you can drop into your projects

Whether you're a hobbyist building a chatbot, a startup watching costs, or a researcher who needs diverse model access -- this saves you hours of research.

---

## Highlights

| Feature | Details |
|:--------|:--------|
| **50 Providers, 7 Tiers** | From completely free to pay-per-use, plus routers and local options |
| **OpenAI SDK Standard** | 90%+ of providers work with `from openai import OpenAI` -- just swap `base_url` |
| **8 Ready-to-Run Examples** | Basic chat, streaming, multi-provider compare, RAG, agents, batch processing |
| **Agent Framework** | BaseAgent, ReAct, Research, and Code agents with 8 provider presets |
| **Search Tools** | Brave, Serper, Google CSE wrappers + web scraper for agent use |
| **AI-Powered Discovery** | Find new providers via web search, GitHub, Reddit, HN, and LLM brainstorming |
| **Cascade Client** | Production-ready failover across providers with health tracking + cooldowns |
| **Local Proxy Server** | Route any OpenAI-compatible app through free providers at `localhost:8000/v1` |
| **Plugin Architecture** | Benchmarks, model catalogs, pricing, export (JSON/CSV/YAML/HTML), notifications |
| **Fully Configurable** | YAML config + env vars. Set your keys, pick your strategies, run |

---

## Table of Contents

- [Quick Start](#quick-start)
- [Provider Overview](#provider-overview)
- [Tier 1: Truly Free](#tier-1-truly-free-no-credit-card-ongoing)
- [Tier 2: Generous Free Tier](#tier-2-generous-free-tier-notable-limitations)
- [Tier 3: Free Credits on Signup](#tier-3-free-credits-on-signup-one-time-may-expire)
- [Tier 4: Freemium](#tier-4-freemium-credit-card-required)
- [Tier 5: Pay-per-use](#tier-5-pay-per-use-no-free-tier-very-cheap)
- [Routers / Aggregators](#routers--aggregators)
- [Local / Self-hosted](#local--self-hosted-unlimited-free-forever)
- [Cascade / Fallback Example](#cascade--fallback-example)
- [Toolkit](#toolkit)
- [Examples](#examples)
- [Agent Framework](#agent-framework)
- [Search Tools](#search-tools)
- [Architecture](#architecture)
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

> **Tip:** Don't want to pick just one? Use the [Cascade Client](#cascade--fallback-example) to automatically try multiple providers with failover.

---

## Provider Overview

| Tier | Providers | Credit Card | Best For |
|:-----|:----------|:------------|:---------|
| Truly Free | 15 | No | Getting started, prototyping, hobby projects |
| Generous Free Tier | 5 | No | Moderate usage with rate limits |
| Free Credits | 17 | No* | Trying premium models, short-term projects |
| Freemium | 3 | Yes | Production apps, frontier models (GPT-4o, Claude) |
| Pay-per-use | 2 | Yes | Budget-conscious production, Chinese models |
| Routers / Aggregators | 4 | Varies | Multi-provider failover, observability |
| Local / Self-hosted | 4 | No | Privacy, offline use, unlimited generation |

> *\*Free Credits tier: credit card generally not required for signup, but credits are one-time and may expire.*

---

## Tier 1: Truly Free (no credit card, ongoing)

| # | Provider | Endpoint | Free Tier | Top Models | SDK | Status |
|:--|:---------|:---------|:----------|:-----------|:----|:-------|
| 1 | [**Google Gemini**](https://aistudio.google.com) | `generativelanguage.googleapis.com/v1beta/openai/` | 250 RPD Flash, 100 RPD Pro | gemini-2.5-flash, gemini-2.5-pro | ✅ | ❓ Not Tested |
| 2 | [**Groq**](https://console.groq.com) | `api.groq.com/openai/v1` | ~1K RPD 70B, 14K RPD 8B | llama-3.3-70b-versatile, llama-3.1-8b-instant | ✅ | ❓ Not Tested |
| 3 | [**Mistral**](https://console.mistral.ai) | `api.mistral.ai/v1` | 1B tokens/mo per model | mistral-large-latest, mistral-small-latest | ✅ | ❓ Not Tested |
| 4 | [**Cerebras**](https://cloud.cerebras.ai) | `api.cerebras.ai/v1` | 1M tokens/day, 8K context | llama-3.3-70b, llama-3.1-8b | ✅ | ❓ Not Tested |
| 5 | [**OpenRouter**](https://openrouter.ai) | `openrouter.ai/api/v1` | 25+ free models, 50 RPD each | deepseek/deepseek-r1:free, meta-llama/llama-3.3-70b-instruct:free | ✅ | ❓ Not Tested |
| 6 | [**Cloudflare Workers AI**](https://dash.cloudflare.com) | `api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1` | 10K neurons/day | @cf/meta/llama-3.3-70b-instruct-fp8-fast, @cf/qwen/qwen2.5-coder-32b-instruct | ✅ | ❓ Not Tested |
| 7 | [**GitHub Models**](https://github.com/marketplace/models) | `models.inference.ai.azure.com` | 50-150 RPD, 8K token limit | gpt-4o, Meta-Llama-3.1-70B-Instruct | ✅ | ❓ Not Tested |
| 8 | [**Zhipu (GLM)**](https://open.bigmodel.cn) | `open.bigmodel.cn/api/paas/v4` | GLM-4-Flash unlimited, no quota | glm-4-flash, glm-4-plus | ✅ | ❓ Not Tested |
| 9 | [**OVHcloud AI Endpoints**](https://ovhcloud.com) | `oai.endpoints.kepler.ai.cloud.ovh.net/v1` | 2 RPM anon, 400 RPM with auth | Meta-Llama-3_1-70B-Instruct, Qwen2.5-72B-Instruct | ✅ | ❓ Not Tested |
| 10 | [**HuggingFace Inference**](https://huggingface.co) | `router.huggingface.co/v1` | ~300 req/hr | Qwen/Qwen2.5-72B-Instruct, meta-llama/Llama-3.3-70B-Instruct | ✅ | ❓ Not Tested |
| 11 | [**Cohere**](https://dashboard.cohere.com) | `api.cohere.com/v2` | 1,000 calls/month forever | command-r-plus, command-r | ✅ | ❓ Not Tested |
| 12 | [**NVIDIA NIM**](https://build.nvidia.com) | `integrate.api.nvidia.com/v1` | 1K-5K credits, 40 RPM | meta/llama-3.3-70b-instruct, deepseek-ai/deepseek-r1 | ✅ | ❓ Not Tested |
| 13 | [**Glhf.chat**](https://glhf.chat) | `glhf.chat/api/openai/v1` | Free tier, 30 RPM | hf:meta-llama/Llama-3.3-70B-Instruct, hf:Qwen/Qwen2.5-72B-Instruct | ✅ | ❓ Not Tested |
| 14 | [**Chutes.ai**](https://chutes.ai) | `api.chutes.ai/v1` | ~200 RPD | deepseek-ai/DeepSeek-R1, meta-llama/Llama-3.3-70B-Instruct | ✅ | ❓ Not Tested |
| 15 | [**Venice.ai**](https://venice.ai) | `api.venice.ai/api/v1` | 10 prompts/day free | llama-3.3-70b, qwen-2.5-72b | ✅ | ❓ Not Tested |

<details>
<summary><strong>Provider Notes (15)</strong></summary>

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

| # | Provider | Endpoint | Free Tier | Top Models | SDK | Status |
|:--|:---------|:---------|:----------|:-----------|:----|:-------|
| 1 | [**Fireworks AI**](https://fireworks.ai) | `api.fireworks.ai/inference/v1` | 10 RPM, $1 trial credits | accounts/fireworks/models/llama-v3p3-70b-instruct, accounts/fireworks/models/deepseek-v3 | ✅ | ❓ Not Tested |
| 2 | [**AIMLAPI**](https://aimlapi.com) | `api.aimlapi.com/v1` | 10 req/hr, 50K credits | gpt-4o, claude-3-5-sonnet | ✅ | ❓ Not Tested |
| 3 | [**Inference.net**](https://inference.net) | `api.inference.net/v1` | $1 + $25 (survey) | deepseek-ai/DeepSeek-R1, meta-llama/Llama-3.1-70B-Instruct | ✅ | ❓ Not Tested |
| 4 | [**NLP Cloud**](https://nlpcloud.com) | `api.nlpcloud.io/v1` | 3 RPM ongoing, $15 credits | finetuned-llama-3-70b, chatdolphin | ❌ | ❓ Not Tested |
| 5 | [**Coze (ByteDance)**](https://coze.com) | `api.coze.com/v1` | Free tier (bot-based) | Via bots: GPT-4o, Gemini, Claude | ✅ | ❓ Not Tested |

<details>
<summary><strong>Provider Notes (5)</strong></summary>

- **Fireworks AI**: Very fast. Supports function calling on open models.
- **AIMLAPI**: Aggregator with 300+ models including GPT, Claude, open-source.
- **Inference.net**: Decentralized inference. Complete survey for extra credits.
- **NLP Cloud**: Also has NER, summarization, translation. Custom API format.
- **Coze (ByteDance)**: Build bots that call underlying LLMs. ByteDance platform.

</details>

---

## Tier 3: Free Credits on Signup (one-time, may expire)

| # | Provider | Endpoint | Free Tier | Top Models | SDK | Status |
|:--|:---------|:---------|:----------|:-----------|:----|:-------|
| 1 | [**xAI / Grok**](https://console.x.ai) | `api.x.ai/v1` | $25 + $150/mo (data sharing) | grok-3, grok-3-mini | ✅ | ❓ Not Tested |
| 2 | [**DeepSeek**](https://platform.deepseek.com) | `api.deepseek.com/v1` | 5M tokens (30 days) | deepseek-chat, deepseek-reasoner | ✅ | ❓ Not Tested |
| 3 | [**DeepInfra**](https://deepinfra.com) | `api.deepinfra.com/v1/openai` | $5 credits | meta-llama/Llama-3.3-70B-Instruct, deepseek-ai/DeepSeek-R1 | ✅ | ❓ Not Tested |
| 4 | [**SambaNova**](https://cloud.sambanova.ai) | `api.sambanova.ai/v1` | $5 credits + free tier (3 months) | Meta-Llama-3.1-405B-Instruct, Meta-Llama-3.3-70B-Instruct | ✅ | ❓ Not Tested |
| 5 | [**Together AI**](https://together.ai) | `api.together.xyz/v1` | $5 credits | meta-llama/Llama-3.3-70B-Instruct-Turbo, deepseek-ai/DeepSeek-R1 | ✅ | ❓ Not Tested |
| 6 | [**AI21 Labs**](https://studio.ai21.com) | `api.ai21.com/studio/v1` | $10 credits (3 months) | jamba-1.5-large, jamba-1.5-mini | ✅ | ❓ Not Tested |
| 7 | [**Upstage**](https://console.upstage.ai) | `api.upstage.ai/v1/solar` | $10 credits (3 months) | solar-pro | ✅ | ❓ Not Tested |
| 8 | [**Scaleway**](https://console.scaleway.com) | `api.scaleway.ai/v1` | 1M tokens (one-time) | llama-3.3-70b-instruct, deepseek-r1 | ✅ | ❓ Not Tested |
| 9 | [**Alibaba DashScope**](https://alibabacloud.com) | `dashscope-intl.aliyuncs.com/compatible-mode/v1` | 1M tokens/model | qwen-max, qwen-plus | ✅ | ❓ Not Tested |
| 10 | [**Nebius AI Studio**](https://studio.nebius.ai) | `api.studio.nebius.ai/v1` | $1 credits | meta-llama/Llama-3.1-70B-Instruct, mistralai/Mistral-7B-Instruct-v0.3 | ✅ | ❓ Not Tested |
| 11 | [**Kluster.ai**](https://kluster.ai) | `api.kluster.ai/v1` | $5 credits | Meta-Llama-3.1-405B-Instruct, Qwen2.5-72B-Instruct | ✅ | ❓ Not Tested |
| 12 | [**Friendli**](https://friendli.ai) | `api.friendli.ai/v1` | $10 credits | meta-llama-3.3-70b-instruct, mixtral-8x7b-instruct-v0-1 | ✅ | ❓ Not Tested |
| 13 | [**Hyperbolic**](https://app.hyperbolic.xyz) | `api.hyperbolic.xyz/v1` | $1-$50 credits | deepseek-ai/DeepSeek-V3, meta-llama/Llama-3.3-70B-Instruct | ✅ | ❓ Not Tested |
| 14 | [**Novita AI**](https://novita.ai) | `api.novita.ai/v3/openai` | $0.50 credits (1 year) | meta-llama/llama-3.3-70b-instruct | ✅ | ❓ Not Tested |
| 15 | [**SiliconCloud (SiliconFlow)**](https://siliconflow.com) | `api.siliconflow.cn/v1` | Small credits on signup | deepseek-ai/DeepSeek-V3, Qwen/Qwen2.5-72B-Instruct | ✅ | ❓ Not Tested |
| 16 | [**Eden AI**](https://edenai.co) | `api.edenai.co/v2` | $10 credits | Multi-provider aggregator | ❌ | ❓ Not Tested |
| 17 | [**Lepton AI**](https://lepton.ai) | `api.lepton.ai/v1` | Trial credits | llama-3.3-70b | ✅ | ❓ Not Tested |

<details>
<summary><strong>Provider Notes (17)</strong></summary>

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

| # | Provider | Endpoint | Free Tier | Top Models | SDK | Status |
|:--|:---------|:---------|:----------|:-----------|:----|:-------|
| 1 | [**OpenAI**](https://platform.openai.com) | `api.openai.com/v1` | $5 credits (3 months) | gpt-4o, gpt-4o-mini | ✅ | ❓ Not Tested |
| 2 | [**Anthropic**](https://console.anthropic.com) | `api.anthropic.com/v1` | $5-10 credits | claude-opus-4-6, claude-sonnet-4-6 | ❌ | ❓ Not Tested |
| 3 | [**Perplexity**](https://docs.perplexity.ai) | `api.perplexity.ai` | $5/mo (with Pro subscription) | sonar, sonar-pro | ✅ | ❓ Not Tested |

<details>
<summary><strong>Provider Notes (3)</strong></summary>

- **OpenAI**: Industry standard. Credit card required for API access.
- **Anthropic**: Not OpenAI-compatible. Uses Messages API + x-api-key header.
- **Perplexity**: Search-grounded LLM. Answers include citations.

</details>

---

## Tier 5: Pay-per-use (no free tier, very cheap)

| # | Provider | Endpoint | Pricing | Top Models | SDK |
|:--|:---------|:---------|:--------|:-----------|:----|
| 1 | [**Moonshot / Kimi**](https://platform.moonshot.ai) | `api.moonshot.cn/v1` | None (very cheap: $0.10/M cache hit) | moonshot-v1-128k, kimi-k2.5 | ✅ |
| 2 | [**MiniMax**](https://platform.minimax.io) | `api.minimax.chat/v1` | None (8% of Claude Sonnet pricing) | abab6.5s-chat, abab5.5-chat | ✅ |

<details>
<summary><strong>Provider Notes (2)</strong></summary>

- **Moonshot / Kimi**: Chinese AI. 256K context. Extremely cheap with caching.
- **MiniMax**: Chinese AI. Very cost-effective.

</details>

---

## Routers / Aggregators

| # | Provider | Endpoint | Free? | Description |
|:--|:---------|:---------|:------|:------------|
| 1 | [**Requesty**](https://requesty.ai) | `router.requesty.ai/v1` | Free credits | Auto-failover between providers. |
| 2 | [**Portkey**](https://portkey.ai) | `api.portkey.ai/v1` | Free tier | AI gateway with observability, guardrails, caching. |
| 3 | [**Unify.ai**](https://unify.ai) | `api.unify.ai/v0` | Free tier | ML-based model routing. Picks optimal provider per query. |
| 4 | [**LiteLLM (self-hosted)**](https://github.com/BerriAI/litellm) | `localhost:4000/v1` | Free (open source) | Open-source proxy. Unified format for all providers. |

<details>
<summary><strong>Provider Notes (4)</strong></summary>

- **Requesty**: Auto-failover between providers.
- **Portkey**: AI gateway with observability, guardrails, caching.
- **Unify.ai**: ML-based model routing. Picks optimal provider per query.
- **LiteLLM (self-hosted)**: Open-source proxy. Unified format for all providers.

</details>

---

## Local / Self-hosted (unlimited, free forever)

| # | Provider | Endpoint | Models | Status |
|:--|:---------|:---------|:-------|:-------|
| 1 | [**Ollama**](https://ollama.com) | `localhost:11434/v1` | llama3.3, qwen2.5 | ❓ Not Tested |
| 2 | [**LM Studio**](https://lmstudio.ai) | `localhost:1234/v1` | Any GGUF model from HuggingFace | ❓ Not Tested |
| 3 | [**llama.cpp**](https://github.com/ggerganov/llama.cpp) | `localhost:8080/v1` | Any GGUF model | ❓ Not Tested |
| 4 | [**Jan.ai**](https://jan.ai) | `localhost:1337/v1` | Any supported model | ❓ Not Tested |

<details>
<summary><strong>Provider Notes (4)</strong></summary>

- **Ollama**: Easiest local setup. 50+ models. OpenAI-compatible.
- **LM Studio**: Best GUI for local models. Drag-and-drop GGUF loading.
- **llama.cpp**: Foundation for most local inference tools.
- **Jan.ai**: 100% offline desktop app.

</details>

---

## Cascade / Fallback Example

Chain multiple free providers so your app **never goes down**:

```python
"""Cascade through free providers with automatic fallback."""
from openai import OpenAI
import os

PROVIDERS = [
    {"name": "Groq",       "base_url": "https://api.groq.com/openai/v1",       "key_env": "GROQ_API_KEY",       "model": "llama-3.3-70b-versatile"},
    {"name": "Cerebras",   "base_url": "https://api.cerebras.ai/v1",           "key_env": "CEREBRAS_API_KEY",   "model": "llama-3.3-70b"},
    {"name": "Mistral",    "base_url": "https://api.mistral.ai/v1",            "key_env": "MISTRAL_API_KEY",    "model": "mistral-small-latest"},
    {"name": "Gemini",     "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key_env": "GEMINI_API_KEY", "model": "gemini-2.0-flash"},
    {"name": "SambaNova",  "base_url": "https://api.sambanova.ai/v1",          "key_env": "SAMBANOVA_API_KEY",  "model": "Meta-Llama-3.3-70B-Instruct"},
    {"name": "GitHub",     "base_url": "https://models.inference.ai.azure.com","key_env": "GITHUB_TOKEN",       "model": "gpt-4o"},
    {"name": "HuggingFace","base_url": "https://router.huggingface.co/v1",     "key_env": "HUGGINGFACE_API_KEY","model": "Qwen/Qwen2.5-72B-Instruct"},
    {"name": "OpenRouter", "base_url": "https://openrouter.ai/api/v1",         "key_env": "OPENROUTER_API_KEY", "model": "deepseek/deepseek-r1:free"},
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

Or use the built-in production cascade client with health tracking, cooldowns, and streaming:

```python
from tools.cascade import CascadeClient

client = CascadeClient()  # Uses all configured providers from .env

# Simple call
response = client.chat("Explain quantum computing")
print(response)

# Streaming
for chunk in client.chat_stream("Write a haiku about AI"):
    print(chunk, end="", flush=True)
```

---

## Toolkit

This repository includes a full-featured Python toolkit for scanning, discovering, benchmarking, and using LLM endpoints.

### Setup

```bash
git clone https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository.git
cd text-generation-ai-llm-tools-endpoints-api-list-repository
pip install -r requirements.txt
cp .env.example .env   # Fill in your API keys (all optional)
python main.py scan     # Test all endpoints
```

### CLI Reference

| Command | Description |
|:--------|:------------|
| `python main.py scan` | Test all endpoints and print results |
| `python main.py scan --tier free` | Test only free-tier providers |
| `python main.py scan --provider Groq` | Test a specific provider |
| `python main.py scan --report` | Scan + regenerate this README |
| `python main.py report` | Generate README from last scan |
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

| Strategy | Source | API Key Required |
|:---------|:-------|:-----------------|
| `web_search` | Brave, Serper, or Google Custom Search | Yes (any one) |
| `github_search` | GitHub repos, awesome-lists, code search | Optional (higher limits with token) |
| `llm_search` | Ask an LLM to brainstorm new providers | Yes (any LLM provider key) |
| `community` | Reddit and Hacker News discussions | No |
| `directory_scrape` | API directories (e.g., OpenRouter /models) | No |

Configure strategies and API keys in `config.yaml` or via environment variables.

### Plugin System

| Plugin | Description | Auto-runs |
|:-------|:------------|:----------|
| `benchmark` | TTFT, tokens/sec, total latency with streaming | No |
| `model_list` | Fetch and catalog all models from each provider | No |
| `export` | Export to JSON, CSV, YAML, HTML | On scan complete |
| `pricing` | Track pricing via OpenRouter's public API | No |
| `notify` | Send alerts to Slack, Discord, or webhooks | On scan complete |

**Custom plugins:** Drop a `.py` file in `plugins/custom/` that subclasses `BasePlugin`.

### Local Proxy

Route any OpenAI-compatible app through your free providers:

```bash
python main.py proxy --port 8000

# Point your apps to:
export OPENAI_BASE_URL=http://localhost:8000/v1
export OPENAI_API_KEY=anything

# Works with any OpenAI SDK client, LangChain, LlamaIndex, etc.
```

---

## Examples

Ready-to-run scripts in the `examples/` directory:

| Example | Description | Run |
|:--------|:------------|:----|
| **basic_chat** | Simple single-turn chat | `python examples/basic_chat.py --provider groq` |
| **streaming_chat** | Streaming with TTFT/throughput stats | `python examples/streaming_chat.py` |
| **interactive_chat** | Multi-turn conversation with history | `python examples/interactive_chat.py` |
| **multi_provider** | Compare responses across providers in parallel | `python examples/multi_provider.py "your prompt"` |
| **structured_output** | JSON mode + function calling for extraction | `python examples/structured_output.py` |
| **rag_pipeline** | RAG with local TF-IDF retriever + LLM | `python examples/rag_pipeline.py --query "..."` |
| **agent_tool_use** | Interactive agent with calculator/weather/unit tools | `python examples/agent_tool_use.py` |
| **batch_async** | Process 10 prompts in parallel with concurrency control | `python examples/batch_async.py` |

All examples support `--provider` flag to switch between free providers (groq, gemini, cerebras, mistral, etc.).

---

## Agent Framework

The `agents/` module provides a lightweight agent framework that works with any free provider:

### BaseAgent

Core agent with tool registration, conversation history, and automatic function calling:

```python
from agents import BaseAgent

agent = BaseAgent("groq")  # or "gemini", "cerebras", "mistral", etc.
agent.register_tool("my_tool", "description", {params}, my_function)
response = agent.chat("Use my_tool to do something")
```

### ReActAgent

Reason + Act pattern using text parsing (works with ANY provider, even without native tool support):

```python
from agents import ReActAgent

agent = ReActAgent("gemini", verbose=True)
agent.register_tool("search", "Search the web", {...}, search_fn)
answer = agent.chat("Research the latest AI news")
# Prints: [Thought] -> [Action] -> [Observation] -> ... -> [Answer]
```

### ResearchAgent

Web research agent with built-in search and page fetching:

```python
from agents import ResearchAgent
from search import get_available_search

agent = ResearchAgent("groq", search_provider=get_available_search())
answer = agent.chat("What are the latest developments in fusion energy?")
```

### CodeAgent

Code generation, review, debugging, and explanation:

```python
from agents import CodeAgent

agent = CodeAgent("groq", language="python")
code = agent.generate("a binary search function")
review = agent.review("def foo(x): return x+1")
fix = agent.debug("def foo(): return 1/0", "ZeroDivisionError")
```

### Provider Presets

All agents accept a provider name string with 8 built-in presets:

| Preset | Provider | Model | Free Tier |
|:-------|:---------|:------|:----------|
| `groq` | Groq | llama-3.3-70b-versatile | ~1K RPD |
| `gemini` | Google Gemini | gemini-2.0-flash | 250 RPD |
| `cerebras` | Cerebras | llama-3.3-70b | 1M tokens/day |
| `mistral` | Mistral | mistral-small-latest | 1B tokens/mo |
| `openrouter` | OpenRouter | deepseek-r1:free | 50 RPD |
| `github` | GitHub Models | gpt-4o | 50-150 RPD |
| `sambanova` | SambaNova | Llama-3.3-70B | $5 credits |
| `huggingface` | HuggingFace | Qwen2.5-72B | ~300 req/hr |

---

## Search Tools

The `search/` module provides unified search provider wrappers for use with agents and discovery:

| Provider | API | Free Tier | Setup |
|:---------|:----|:----------|:------|
| **Brave Search** | `search/brave_search.py` | 2,000 queries/month | `BRAVE_API_KEY` from [brave.com/search/api](https://brave.com/search/api/) |
| **Serper.dev** | `search/serper_search.py` | 2,500 queries (one-time) | `SERPER_API_KEY` from [serper.dev](https://serper.dev) |
| **Google CSE** | `search/google_cse.py` | 100 queries/day | `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` |
| **Web Scraper** | `search/web_scraper.py` | Unlimited (direct fetch) | No key needed |

### Usage

```python
from search import get_available_search, BraveSearch, fetch_url

# Auto-detect first configured provider
search = get_available_search()
if search:
    import asyncio
    results = asyncio.run(search.search("free LLM API endpoints"))
    for r in results:
        print(f"{r.title}: {r.url}")

# Or use a specific provider
brave = BraveSearch()  # Uses BRAVE_API_KEY from env
results = asyncio.run(brave.search("best free AI APIs 2026"))

# Fetch and extract text from any URL
text = asyncio.run(fetch_url("https://example.com"))
```

All search providers implement the same `BaseSearchProvider` interface, making them interchangeable in agents and discovery strategies.

---

## Architecture

```
                          ┌─────────────────┐
                          │   config.yaml   │
                          │    + .env keys  │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │    main.py      │  CLI entry point
                          │   (argparse)    │  9 subcommands
                          └──┬────┬────┬────┘
                             │    │    │
              ┌──────────────┘    │    └──────────────┐
              ▼                   ▼                   ▼
    ┌──────────────────┐ ┌──────────────┐  ┌──────────────────┐
    │  providers.py    │ │  scanner.py  │  │ discovery/engine  │
    │  50+ providers   │ │  async HTTP  │  │  5 strategies     │
    │  7 tiers         │ │  health test │  │  AI-powered       │
    └────────┬─────────┘ └──────┬───────┘  └────────┬─────────┘
             │                  │                    │
             ▼                  ▼                    ▼
    ┌──────────────────────────────────────────────────────┐
    │              report_generator.py                     │
    │              (generates README.md)                   │
    └──────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────┐
    │                agents/ + search/                     │
    │  BaseAgent | ReActAgent | ResearchAgent | CodeAgent  │
    │  BraveSearch | SerperSearch | GoogleCSE | WebScraper │
    └──────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────┐
    │              plugins/ + tools/                       │
    │  benchmark | export | cascade | proxy | compare      │
    │  pricing | notify | model_list                       │
    └──────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────┐
    │                   examples/                          │
    │  basic_chat | streaming | multi_provider | RAG       │
    │  agent_tool_use | batch_async | structured_output    │
    └──────────────────────────────────────────────────────┘
```

---

## Status Legend

| Icon | Meaning |
|:-----|:--------|
| ✅ | **Working** -- endpoint responded with a valid completion |
| 🟡 | **Reachable** -- endpoint alive but completion not tested |
| 🔑 | **Key Not Set** -- API key not configured in `.env` |
| ❌ | **Error / Auth Failed** -- endpoint returned an error |
| 💳 | **Needs Credits** -- free credits exhausted |
| ⏳ | **Rate Limited** -- too many requests, try again later |
| ⏱️ | **Timeout** -- endpoint didn't respond in time |
| ⬛ | **Offline** -- local server not running |
| ⏭️ | **Skipped** -- no test model configured |

---

## Project Structure

```
text-generation-ai-llm-tools-endpoints-api-list-repository/
├── main.py                  # CLI entry point (9 subcommands)
├── config.py                # Config loader (YAML + env overrides)
├── config.yaml              # All settings (scan, search, discovery, plugins)
├── providers.py             # Provider registry (50 providers, 7 tiers)
├── scanner.py               # Async endpoint health checker (httpx)
├── report_generator.py      # README/report generator
├── requirements.txt         # Python dependencies
├── .env.example             # API key template (50+ keys, all optional)
│
├── examples/                # Ready-to-run sample scripts
│   ├── basic_chat.py        # Simple single-turn chat
│   ├── streaming_chat.py    # Streaming with perf stats
│   ├── interactive_chat.py  # Multi-turn conversation
│   ├── multi_provider.py    # Compare providers side-by-side
│   ├── structured_output.py # JSON mode + function calling
│   ├── rag_pipeline.py      # RAG with local TF-IDF + LLM
│   ├── agent_tool_use.py    # Agent with calculator/weather tools
│   └── batch_async.py       # Parallel prompt processing
│
├── agents/                  # LLM-powered agent framework
│   ├── base.py              # BaseAgent + provider presets
│   ├── react_agent.py       # ReAct (Reason + Act) agent
│   ├── research_agent.py    # Web research agent
│   └── code_agent.py        # Code gen/review/debug agent
│
├── search/                  # Search tool integrations
│   ├── base.py              # BaseSearchProvider interface
│   ├── brave_search.py      # Brave Search API
│   ├── serper_search.py     # Serper.dev Google Search
│   ├── google_cse.py        # Google Custom Search Engine
│   └── web_scraper.py       # URL content fetcher
│
├── discovery/               # AI-powered endpoint discovery
│   ├── engine.py            # Orchestrator (dedup, verify, save)
│   └── strategies/
│       ├── base.py          # Strategy interface
│       ├── web_search.py    # Brave / Serper / Google CSE
│       ├── github_search.py # GitHub repos & awesome-lists
│       ├── llm_search.py    # LLM-assisted brainstorming
│       ├── community.py     # Reddit & Hacker News
│       └── directory_scrape.py
│
├── plugins/                 # Plugin system
│   ├── base.py              # BasePlugin + PluginManager
│   ├── builtin/
│   │   ├── benchmark.py     # TTFT, tokens/sec, latency
│   │   ├── model_list.py    # Model catalog fetcher
│   │   ├── export.py        # JSON / CSV / YAML / HTML
│   │   ├── pricing.py       # Pricing tracker (OpenRouter)
│   │   └── notify.py        # Slack / Discord / webhook
│   └── custom/              # Drop your own plugins here
│
├── tools/                   # Standalone tools
│   ├── cascade.py           # Production cascade client
│   ├── compare.py           # Side-by-side comparison
│   └── proxy.py             # Local OpenAI-compatible proxy
│
└── data/                    # Generated data (gitignored)
    └── .gitkeep
```

---

## Contributing

Found a new free LLM endpoint? Provider changed their limits? Something broken? **Contributions welcome!**

### Adding a Provider

1. Edit `providers.py` -- add a new `Provider(...)` entry in the appropriate tier
2. Run `python main.py scan --provider YourProvider` to verify it works
3. Run `python main.py scan --report` to regenerate the README
4. Submit a PR

### Extending

- **Custom plugins** -- subclass `BasePlugin` in `plugins/custom/your_plugin.py`
- **Custom discovery strategies** -- subclass `BaseStrategy` in `discovery/strategies/your_strategy.py`
- **New export formats** -- extend `plugins/builtin/export.py`

### Reporting Issues

- Provider down or limits changed? [Open an issue](https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository/issues)
- New provider suggestion? [Open an issue](https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository/issues) with the endpoint URL and free tier details

---

## License

[MIT](https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository/blob/main/LICENSE) -- use this however you want.

---

<p align="center">
  <sub>Auto-generated by <a href="https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository">LLM Endpoint Scanner</a> &bull; Last updated: 2026-03-06 02:35 UTC</sub>
</p>
