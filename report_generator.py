"""
Generates a comprehensive README.md report from provider data and scan results.
"""

from __future__ import annotations

from datetime import datetime, timezone
from providers import Provider, Tier, PROVIDERS, get_unique_providers, get_providers_by_tier
from scanner import ScanResult


REPO_URL = "https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository"
REPO_NAME = "text-generation-ai-llm-tools-endpoints-api-list-repository"

STATUS_ICONS = {
    "working": "✅",
    "reachable": "🟡",
    "auth_missing": "🔑",
    "auth_failed": "❌",
    "needs_credits": "💳",
    "rate_limited": "⏳",
    "timeout": "⏱️",
    "error": "❌",
    "offline": "⬛",
    "skipped": "⏭️",
    "unknown": "❓",
}


def _status_text(status: str) -> str:
    icon = STATUS_ICONS.get(status, "❓")
    labels = {
        "working": "Working",
        "reachable": "Reachable",
        "auth_missing": "Key Not Set",
        "auth_failed": "Auth Failed",
        "needs_credits": "Needs Credits",
        "rate_limited": "Rate Limited",
        "timeout": "Timeout",
        "error": "Error",
        "offline": "Offline",
        "skipped": "Skipped",
        "unknown": "Not Tested",
    }
    return f"{icon} {labels.get(status, status)}"


def _short_endpoint(endpoint: str) -> str:
    """Remove protocol prefix for compact table display."""
    return endpoint.replace("https://", "").replace("http://", "")


def _make_tier_table(
    providers: list[Provider],
    results: dict[str, ScanResult],
    tier: Tier,
) -> str:
    """Generate a markdown table for a tier."""
    lines: list[str] = []

    if tier == Tier.LOCAL:
        lines.append("| # | Provider | Endpoint | Models | Status |")
        lines.append("|:--|:---------|:---------|:-------|:-------|")
        for i, p in enumerate(providers, 1):
            r = results.get(p.name)
            status = _status_text(r.status) if r else _status_text("unknown")
            name = f"[**{p.name}**]({p.signup_url})" if p.signup_url else f"**{p.name}**"
            lines.append(
                f"| {i} | {name} | `{_short_endpoint(p.endpoint)}` | {', '.join(p.models[:2])} | {status} |"
            )
        return "\n".join(lines)

    if tier == Tier.ROUTER:
        lines.append("| # | Provider | Endpoint | Free? | Description |")
        lines.append("|:--|:---------|:---------|:------|:------------|")
        for i, p in enumerate(providers, 1):
            name = f"[**{p.name}**]({p.signup_url})" if p.signup_url else f"**{p.name}**"
            lines.append(
                f"| {i} | {name} | `{_short_endpoint(p.endpoint)}` | {p.free_limits} | {p.notes} |"
            )
        return "\n".join(lines)

    if tier == Tier.PAYG:
        lines.append("| # | Provider | Endpoint | Pricing | Top Models | SDK |")
        lines.append("|:--|:---------|:---------|:--------|:-----------|:----|")
        for i, p in enumerate(providers, 1):
            name = f"[**{p.name}**]({p.signup_url})" if p.signup_url else f"**{p.name}**"
            sdk = "✅" if p.openai_compatible else "❌"
            lines.append(
                f"| {i} | {name} | `{_short_endpoint(p.endpoint)}` | {p.free_limits} | {', '.join(p.models[:2])} | {sdk} |"
            )
        return "\n".join(lines)

    # Standard table for free / generous_free / free_credits / freemium
    lines.append("| # | Provider | Endpoint | Free Tier | Top Models | SDK | Status |")
    lines.append("|:--|:---------|:---------|:----------|:-----------|:----|:-------|")
    for i, p in enumerate(providers, 1):
        r = results.get(p.name)
        status = _status_text(r.status) if r else _status_text("unknown")
        sdk = "✅" if p.openai_compatible else "❌"
        latency = f" ({r.latency_ms:.0f}ms)" if r and r.latency_ms else ""
        name = f"[**{p.name}**]({p.signup_url})" if p.signup_url else f"**{p.name}**"
        lines.append(
            f"| {i} | {name} | `{_short_endpoint(p.endpoint)}` | {p.free_limits} | {', '.join(p.models[:2])} | {sdk} | {status}{latency} |"
        )
    return "\n".join(lines)


def _quick_start_snippet() -> str:
    return '''```python
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
```'''


def _cascade_snippet() -> str:
    return '''```python
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
```'''


def generate_readme(
    results: list[ScanResult] | None = None,
    scan_timestamp: str | None = None,
) -> str:
    """Generate the full README.md content."""
    results_map: dict[str, ScanResult] = {}
    if results:
        for r in results:
            results_map[r.provider_name] = r

    now = scan_timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    providers = get_unique_providers()

    total = len(providers)
    working = sum(1 for r in results_map.values() if r.status == "working") if results_map else 0
    free_count = len([p for p in providers if p.tier == Tier.FREE])

    tier_order = [
        Tier.FREE,
        Tier.GENEROUS_FREE,
        Tier.FREE_CREDITS,
        Tier.FREEMIUM,
        Tier.PAYG,
        Tier.ROUTER,
        Tier.LOCAL,
    ]

    sections: list[str] = []

    # ================================================================
    # HEADER WITH BADGES
    # ================================================================
    sections.append(f"""# Free & Open LLM API Endpoints Directory

<p align="center">
  <a href="{REPO_URL}/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/providers-{total}-brightgreen.svg" alt="Providers: {total}">
  <img src="https://img.shields.io/badge/free%20tier-{free_count}-success.svg" alt="Free: {free_count}">
  <a href="{REPO_URL}/stargazers"><img src="https://img.shields.io/github/stars/TaylorAmarelTech/{REPO_NAME}?style=social" alt="GitHub Stars"></a>
</p>

<p align="center">
  <strong>The most comprehensive, actively-maintained directory of free and affordable LLM API endpoints.</strong><br>
  {total} providers cataloged &bull; {free_count} truly free (no credit card) &bull; All OpenAI SDK compatible &bull; Updated: {now}
</p>

---""")

    # ================================================================
    # WHY THIS EXISTS
    # ================================================================
    sections.append("""
## Why This Exists

There are **dozens** of LLM API providers offering free tiers, trial credits, and affordable pricing -- but finding them, comparing limits, and knowing which ones actually work is a scattered mess. This repository maintains:

- A **curated, verified directory** of every provider with free or cheap LLM API access
- A **scanner toolkit** that automatically tests endpoints and reports status
- An **AI-powered discovery engine** that finds new providers as they launch
- **Production-ready code** (cascade client, local proxy, benchmarks) you can drop into your projects

Whether you're a hobbyist building a chatbot, a startup watching costs, or a researcher who needs diverse model access -- this saves you hours of research.

---""")

    # ================================================================
    # HIGHLIGHTS
    # ================================================================
    sections.append(f"""
## Highlights

| Feature | Details |
|:--------|:--------|
| **{total} Providers, 7 Tiers** | From completely free to pay-per-use, plus routers and local options |
| **OpenAI SDK Standard** | 90%+ of providers work with `from openai import OpenAI` -- just swap `base_url` |
| **Async Health Scanner** | Test all endpoints in parallel, get latency + status in seconds |
| **AI-Powered Discovery** | Find new providers via Brave, Serper, Google, GitHub, Reddit, HN, and LLM brainstorming |
| **Cascade Client** | Production-ready failover across providers with health tracking + cooldowns |
| **Local Proxy Server** | Route any OpenAI-compatible app through free providers at `localhost:8000/v1` |
| **Plugin Architecture** | Benchmarks, model catalogs, pricing, export (JSON/CSV/YAML/HTML), notifications |
| **Fully Configurable** | YAML config + env vars. Set your keys, pick your strategies, run |

---""")

    # ================================================================
    # TABLE OF CONTENTS
    # ================================================================
    sections.append("""
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
- [Architecture](#architecture)
- [Status Legend](#status-legend)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---""")

    # ================================================================
    # QUICK START
    # ================================================================
    sections.append(f"""
## Quick Start

All Tier 1 providers use the **OpenAI SDK format** -- just change the `base_url` and `api_key`:

{_quick_start_snippet()}

> **Tip:** Don't want to pick just one? Use the [Cascade Client](#cascade--fallback-example) to automatically try multiple providers with failover.

---""")

    # ================================================================
    # PROVIDER OVERVIEW
    # ================================================================
    tier_meta = {
        Tier.FREE:          ("Truly Free",          "No",     "Getting started, prototyping, hobby projects"),
        Tier.GENEROUS_FREE: ("Generous Free Tier",   "No",     "Moderate usage with rate limits"),
        Tier.FREE_CREDITS:  ("Free Credits",         "No*",    "Trying premium models, short-term projects"),
        Tier.FREEMIUM:      ("Freemium",             "Yes",    "Production apps, frontier models (GPT-4o, Claude)"),
        Tier.PAYG:          ("Pay-per-use",          "Yes",    "Budget-conscious production, Chinese models"),
        Tier.ROUTER:        ("Routers / Aggregators","Varies", "Multi-provider failover, observability"),
        Tier.LOCAL:         ("Local / Self-hosted",  "No",     "Privacy, offline use, unlimited generation"),
    }

    overview_rows = []
    for tier in tier_order:
        tier_providers = [p for p in providers if p.tier == tier]
        if not tier_providers:
            continue
        label, card, best_for = tier_meta[tier]
        count = len(tier_providers)
        overview_rows.append(f"| {label} | {count} | {card} | {best_for} |")

    sections.append(f"""
## Provider Overview

| Tier | Providers | Credit Card | Best For |
|:-----|:----------|:------------|:---------|
{chr(10).join(overview_rows)}

> *\\*Free Credits tier: credit card generally not required for signup, but credits are one-time and may expire.*

---""")

    # ================================================================
    # TIER TABLES
    # ================================================================
    for tier in tier_order:
        tier_providers = [p for p in providers if p.tier == tier]
        if not tier_providers:
            continue
        tier_num = tier_order.index(tier) + 1
        if tier in (Tier.ROUTER, Tier.LOCAL):
            heading = f"## {tier.label}"
        else:
            heading = f"## Tier {tier_num}: {tier.label}"

        sections.append("")
        sections.append(heading)
        sections.append("")
        sections.append(_make_tier_table(tier_providers, results_map, tier))
        sections.append("")

        # Provider notes in collapsible
        notes_lines = []
        for p in tier_providers:
            if p.notes:
                notes_lines.append(f"- **{p.name}**: {p.notes}")
        if notes_lines:
            sections.append("<details>")
            sections.append(f"<summary><strong>Provider Notes ({len(notes_lines)})</strong></summary>")
            sections.append("")
            sections.append("\n".join(notes_lines))
            sections.append("")
            sections.append("</details>")
            sections.append("")

        sections.append("---")

    # ================================================================
    # CASCADE EXAMPLE
    # ================================================================
    sections.append(f"""
## Cascade / Fallback Example

Chain multiple free providers so your app **never goes down**:

{_cascade_snippet()}

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

---""")

    # ================================================================
    # TOOLKIT
    # ================================================================
    sections.append(f"""
## Toolkit

This repository includes a full-featured Python toolkit for scanning, discovering, benchmarking, and using LLM endpoints.

### Setup

```bash
git clone {REPO_URL}.git
cd {REPO_NAME}
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

---""")

    # ================================================================
    # ARCHITECTURE
    # ================================================================
    sections.append("""
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
    └────────┬─────────┘ └──────┬───────┘  └──────────────────┘
             │                  │
             ▼                  ▼
    ┌──────────────────────────────────────┐
    │         report_generator.py          │
    │         (generates README.md)        │
    └──────────────────────────────────────┘

    ┌──────────────────────────────────────┐
    │          plugins/ + tools/           │
    │  benchmark | export | cascade |      │
    │  pricing | notify | proxy | compare  │
    └──────────────────────────────────────┘
```

---""")

    # ================================================================
    # STATUS LEGEND
    # ================================================================
    sections.append("""
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

---""")

    # ================================================================
    # PROJECT STRUCTURE
    # ================================================================
    sections.append(f"""
## Project Structure

```
{REPO_NAME}/
├── main.py                  # CLI entry point (9 subcommands)
├── config.py                # Config loader (YAML + env overrides)
├── config.yaml              # All settings (scan, search, discovery, plugins)
├── providers.py             # Provider registry ({total} providers, 7 tiers)
├── scanner.py               # Async endpoint health checker (httpx)
├── report_generator.py      # README/report generator
├── requirements.txt         # Python dependencies
├── .env.example             # API key template (50+ keys, all optional)
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

---""")

    # ================================================================
    # CONTRIBUTING
    # ================================================================
    sections.append(f"""
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

- Provider down or limits changed? [Open an issue]({REPO_URL}/issues)
- New provider suggestion? [Open an issue]({REPO_URL}/issues) with the endpoint URL and free tier details

---

## License

[MIT]({REPO_URL}/blob/main/LICENSE) -- use this however you want.

---

<p align="center">
  <sub>Auto-generated by <a href="{REPO_URL}">LLM Endpoint Scanner</a> &bull; Last updated: {now}</sub>
</p>
""")

    return "\n".join(sections)
