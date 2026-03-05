"""
LLM-powered discovery strategy.

Uses a configured LLM (via OpenAI SDK) to brainstorm and suggest new
free LLM API providers, then validates the suggestions.
"""

from __future__ import annotations

import json
import os
import re

from config import Config
from discovery.engine import Candidate
from discovery.strategies.base import BaseStrategy
from providers import PROVIDERS

# Map config provider names to env keys and base URLs
LLM_PROVIDER_MAP = {
    "groq": ("GROQ_API_KEY", "https://api.groq.com/openai/v1"),
    "cerebras": ("CEREBRAS_API_KEY", "https://api.cerebras.ai/v1"),
    "mistral": ("MISTRAL_API_KEY", "https://api.mistral.ai/v1"),
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/"),
    "openrouter": ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
    "openai": ("OPENAI_API_KEY", "https://api.openai.com/v1"),
    "deepseek": ("DEEPSEEK_API_KEY", "https://api.deepseek.com/v1"),
    "sambanova": ("SAMBANOVA_API_KEY", "https://api.sambanova.ai/v1"),
    "github": ("GITHUB_TOKEN", "https://models.inference.ai.azure.com"),
}

DISCOVERY_PROMPT = """You are an expert on LLM API providers and free inference endpoints.

I already know about these providers:
{known_providers}

Please suggest NEW free or very cheap LLM API providers that I might be missing.
Focus on:
- Providers offering free API access (no credit card required)
- Providers with generous free credits on signup
- New startups or platforms that recently launched free tiers
- Chinese AI platforms with international API access
- Lesser-known inference platforms

For each provider, respond in this exact JSON format (array of objects):
```json
[
  {{
    "name": "Provider Name",
    "endpoint": "https://api.example.com/v1",
    "free_limits": "100 RPD free",
    "models": ["model-name-1", "model-name-2"],
    "openai_compatible": true,
    "signup_url": "https://example.com",
    "notes": "Brief description of what makes this provider notable"
  }}
]
```

Only include providers you are confident exist and have working APIs.
Return ONLY the JSON array, no other text."""


class LLMSearchStrategy(BaseStrategy):
    """Use an LLM to discover new providers."""

    @property
    def name(self) -> str:
        return "llm_search"

    async def search(self, config: Config) -> list[Candidate]:
        provider_key = config.discovery.llm_provider.lower()
        if provider_key not in LLM_PROVIDER_MAP:
            print(f"  LLM provider '{provider_key}' not configured in LLM_PROVIDER_MAP")
            return []

        env_key, base_url = LLM_PROVIDER_MAP[provider_key]
        api_key = os.environ.get(env_key, "").strip()
        if not api_key:
            print(f"  {env_key} not set, skipping LLM discovery")
            return []

        try:
            from openai import OpenAI
        except ImportError:
            print("  openai package not installed")
            return []

        known = ", ".join(p.name for p in PROVIDERS[:30])
        prompt = DISCOVERY_PROMPT.format(known_providers=known)

        try:
            client = OpenAI(base_url=base_url, api_key=api_key)
            response = client.chat.completions.create(
                model=config.discovery.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3,
            )
            text = response.choices[0].message.content or ""
        except Exception as e:
            print(f"  LLM call failed: {e}")
            return []

        return self._parse_response(text)

    def _parse_response(self, text: str) -> list[Candidate]:
        """Parse LLM response into Candidate objects."""
        # Try to extract JSON from the response
        json_match = re.search(r'\[[\s\S]*?\]', text)
        if not json_match:
            return []

        try:
            items = json.loads(json_match.group())
        except json.JSONDecodeError:
            return []

        candidates: list[Candidate] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("name", "").strip()
            endpoint = item.get("endpoint", "").strip()
            if not name or not endpoint:
                continue

            candidates.append(Candidate(
                name=name,
                endpoint=endpoint,
                free_limits=item.get("free_limits", ""),
                models=item.get("models", []),
                openai_compatible=item.get("openai_compatible", True),
                signup_url=item.get("signup_url", ""),
                notes=item.get("notes", ""),
                source="llm_search",
                confidence=0.5,  # LLM suggestions need verification
            ))

        return candidates
