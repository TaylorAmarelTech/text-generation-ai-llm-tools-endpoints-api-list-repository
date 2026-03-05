"""
Generates a comprehensive README.md report from provider data and scan results.
"""

from __future__ import annotations

from datetime import datetime, timezone
from providers import Provider, Tier, PROVIDERS, get_unique_providers, get_providers_by_tier
from scanner import ScanResult


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


def _make_tier_table(
    providers: list[Provider],
    results: dict[str, ScanResult],
    tier: Tier,
) -> str:
    """Generate a markdown table for a tier."""
    lines: list[str] = []

    if tier == Tier.LOCAL:
        lines.append("| # | Provider | Endpoint | Models | Status |")
        lines.append("|---|----------|----------|--------|--------|")
        for i, p in enumerate(providers, 1):
            r = results.get(p.name)
            status = _status_text(r.status) if r else _status_text("unknown")
            lines.append(
                f"| {i} | **{p.name}** | `{p.endpoint}` | {', '.join(p.models[:3])} | {status} |"
            )
        return "\n".join(lines)

    if tier == Tier.ROUTER:
        lines.append("| # | Provider | Endpoint | Free? | What It Does | Sign Up |")
        lines.append("|---|----------|----------|-------|--------------|---------|")
        for i, p in enumerate(providers, 1):
            r = results.get(p.name)
            status = _status_text(r.status) if r else ""
            lines.append(
                f"| {i} | **{p.name}** | `{p.endpoint}` | {p.free_limits} | {p.notes} | [{p.signup_url.split('//')[1] if '//' in p.signup_url else p.signup_url}]({p.signup_url}) |"
            )
        return "\n".join(lines)

    if tier == Tier.PAYG:
        lines.append("| # | Provider | Endpoint | Cheapest Rate | Best Models | OpenAI SDK | Sign Up |")
        lines.append("|---|----------|----------|---------------|-------------|------------|---------|")
        for i, p in enumerate(providers, 1):
            r = results.get(p.name)
            status = _status_text(r.status) if r else _status_text("unknown")
            sdk = "Yes" if p.openai_compatible else "No"
            signup = f"[{p.signup_url.split('//')[1] if '//' in p.signup_url else p.signup_url}]({p.signup_url})" if p.signup_url else ""
            lines.append(
                f"| {i} | **{p.name}** | `{p.endpoint}` | {p.free_limits} | {', '.join(p.models[:2])} | {sdk} | {signup} |"
            )
        return "\n".join(lines)

    # Standard table for free / generous_free / free_credits / freemium
    lines.append("| # | Provider | Endpoint | Free Limits | Best Models | OpenAI SDK | Status | Sign Up |")
    lines.append("|---|----------|----------|-------------|-------------|------------|--------|---------|")
    for i, p in enumerate(providers, 1):
        r = results.get(p.name)
        status = _status_text(r.status) if r else _status_text("unknown")
        sdk = "Yes" if p.openai_compatible else "No"
        latency = f" ({r.latency_ms:.0f}ms)" if r and r.latency_ms else ""
        signup = f"[Sign Up]({p.signup_url})" if p.signup_url else ""
        lines.append(
            f"| {i} | **{p.name}** | `{p.endpoint}` | {p.free_limits} | {', '.join(p.models[:3])} | {sdk} | {status}{latency} | {signup} |"
        )
    return "\n".join(lines)


def _quick_start_snippet() -> str:
    """Generate a Python quick-start code snippet."""
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
    """Generate a cascade/fallback code snippet."""
    return '''```python
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

    # Counts
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

    # Header
    sections.append(f"""# Free & Open LLM API Endpoints Directory

> **The most comprehensive list of free and affordable LLM API endpoints for text generation.**
>
> {total} providers cataloged | {free_count} truly free (no credit card) | Last scanned: {now}

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

{_quick_start_snippet()}

---
""")

    # Tier tables
    for tier in tier_order:
        tier_providers = [p for p in providers if p.tier == tier]
        if not tier_providers:
            continue
        tier_num = tier_order.index(tier) + 1
        if tier in (Tier.ROUTER, Tier.LOCAL):
            heading = f"## {tier.label}"
        else:
            heading = f"## Tier {tier_num}: {tier.label}"

        sections.append(heading)
        sections.append("")
        sections.append(_make_tier_table(tier_providers, results_map, tier))
        sections.append("")

        # Add notes for providers in this tier
        notes_lines = []
        for p in tier_providers:
            if p.notes:
                notes_lines.append(f"- **{p.name}**: {p.notes}")
        if notes_lines:
            sections.append("<details>")
            sections.append(f"<summary>Provider Notes ({len(notes_lines)})</summary>")
            sections.append("")
            sections.append("\n".join(notes_lines))
            sections.append("")
            sections.append("</details>")
            sections.append("")

        sections.append("---")
        sections.append("")

    # Cascade example
    sections.append(f"""## Cascade / Fallback Example

Chain multiple free providers with automatic failover:

{_cascade_snippet()}

---
""")

    # Scanner tool
    sections.append("""## Toolkit

This repository includes a full-featured Python toolkit: scanner, AI-powered discovery, benchmarks, plugins, and a local proxy.

### Setup

```bash
# Clone the repo
git clone https://gitlab.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository.git
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
""")

    # Status legend
    sections.append("""## Status Legend

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
""")

    # Project structure
    sections.append("""## Project Structure

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

*Auto-generated by [LLM Endpoint Scanner](https://gitlab.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository)*
""")

    return "\n".join(sections)
