"""
Production-ready cascade client.

Tries providers in priority order with automatic failover, retry logic,
rate limit awareness, and health tracking.

Usage as a library:
    from tools.cascade import CascadeClient

    client = CascadeClient()
    response = client.chat("What is the meaning of life?")
    print(response.content)
    print(f"Provider: {response.provider}")

Usage as CLI:
    python -m tools.cascade "What is the meaning of life?"
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv

load_dotenv()


@dataclass
class CascadeResponse:
    content: str
    provider: str
    model: str
    latency_ms: float
    tokens_used: int | None = None


@dataclass
class ProviderSlot:
    name: str
    base_url: str
    key_env: str
    model: str
    priority: int = 0
    # Health tracking
    consecutive_failures: int = 0
    last_failure_time: float = 0
    cooldown_seconds: float = 60


# Default cascade order (all free, no credit card)
DEFAULT_CASCADE: list[dict[str, Any]] = [
    {"name": "Groq", "base_url": "https://api.groq.com/openai/v1", "key_env": "GROQ_API_KEY", "model": "llama-3.3-70b-versatile"},
    {"name": "Cerebras", "base_url": "https://api.cerebras.ai/v1", "key_env": "CEREBRAS_API_KEY", "model": "llama-3.3-70b"},
    {"name": "Gemini", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key_env": "GEMINI_API_KEY", "model": "gemini-2.0-flash"},
    {"name": "Mistral", "base_url": "https://api.mistral.ai/v1", "key_env": "MISTRAL_API_KEY", "model": "mistral-small-latest"},
    {"name": "SambaNova", "base_url": "https://api.sambanova.ai/v1", "key_env": "SAMBANOVA_API_KEY", "model": "Meta-Llama-3.3-70B-Instruct"},
    {"name": "GitHub Models", "base_url": "https://models.inference.ai.azure.com", "key_env": "GITHUB_TOKEN", "model": "gpt-4o"},
    {"name": "HuggingFace", "base_url": "https://router.huggingface.co/v1", "key_env": "HUGGINGFACE_API_KEY", "model": "Qwen/Qwen2.5-72B-Instruct"},
    {"name": "Cloudflare", "base_url": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1", "key_env": "CLOUDFLARE_API_TOKEN", "model": "@cf/meta/llama-3.3-70b-instruct-fp8-fast"},
    {"name": "Cohere", "base_url": "https://api.cohere.com/v2", "key_env": "COHERE_API_KEY", "model": "command-r"},
    {"name": "OpenRouter", "base_url": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY", "model": "deepseek/deepseek-r1:free"},
]


class CascadeClient:
    """Cascading LLM client with automatic failover."""

    def __init__(
        self,
        providers: list[dict[str, Any]] | None = None,
        max_retries: int = 1,
        timeout: float = 30,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.slots: list[ProviderSlot] = []

        for i, p in enumerate(providers or DEFAULT_CASCADE):
            api_key = os.environ.get(p["key_env"], "").strip()
            if not api_key:
                continue

            # Resolve Cloudflare account ID
            base_url = p["base_url"]
            if "{account_id}" in base_url:
                acct = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
                if not acct:
                    continue
                base_url = base_url.replace("{account_id}", acct)

            self.slots.append(ProviderSlot(
                name=p["name"],
                base_url=base_url,
                key_env=p["key_env"],
                model=p["model"],
                priority=i,
            ))

        if not self.slots:
            raise RuntimeError(
                "No providers configured. Set at least one API key in .env"
            )

    def chat(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> CascadeResponse:
        """Send a chat completion through the cascade."""
        from openai import OpenAI

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        errors: list[str] = []
        available = self._get_available_slots()

        for slot in available:
            api_key = os.environ.get(slot.key_env, "")
            for attempt in range(1 + self.max_retries):
                try:
                    client = OpenAI(
                        base_url=slot.base_url,
                        api_key=api_key,
                        timeout=self.timeout,
                    )
                    start = time.perf_counter()
                    response = client.chat.completions.create(
                        model=slot.model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs,
                    )
                    latency = (time.perf_counter() - start) * 1000

                    content = response.choices[0].message.content or ""
                    slot.consecutive_failures = 0

                    return CascadeResponse(
                        content=content,
                        provider=slot.name,
                        model=slot.model,
                        latency_ms=round(latency, 1),
                        tokens_used=response.usage.total_tokens if response.usage else None,
                    )

                except Exception as e:
                    slot.consecutive_failures += 1
                    slot.last_failure_time = time.time()
                    err = f"{slot.name} (attempt {attempt+1}): {type(e).__name__}: {str(e)[:100]}"
                    errors.append(err)

        raise RuntimeError(
            f"All providers failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    def _get_available_slots(self) -> list[ProviderSlot]:
        """Return slots sorted by priority, skipping those in cooldown."""
        now = time.time()
        available = []
        for slot in sorted(self.slots, key=lambda s: s.priority):
            if slot.consecutive_failures >= 3:
                elapsed = now - slot.last_failure_time
                if elapsed < slot.cooldown_seconds:
                    continue
                slot.consecutive_failures = 0
            available.append(slot)
        return available

    def chat_stream(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 500,
        **kwargs: Any,
    ):
        """Stream a chat completion through the cascade. Yields content chunks."""
        from openai import OpenAI

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        for slot in self._get_available_slots():
            api_key = os.environ.get(slot.key_env, "")
            try:
                client = OpenAI(
                    base_url=slot.base_url,
                    api_key=api_key,
                    timeout=self.timeout,
                )
                stream = client.chat.completions.create(
                    model=slot.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    stream=True,
                    **kwargs,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        yield delta.content

                slot.consecutive_failures = 0
                return

            except Exception:
                slot.consecutive_failures += 1
                slot.last_failure_time = time.time()
                continue

        raise RuntimeError("All providers failed for streaming")


def main() -> None:
    """CLI entry point: python -m tools.cascade 'your prompt'"""
    if len(sys.argv) < 2:
        print("Usage: python -m tools.cascade 'your prompt here'")
        print("       python -m tools.cascade --stream 'your prompt here'")
        sys.exit(1)

    streaming = "--stream" in sys.argv
    prompt = " ".join(a for a in sys.argv[1:] if a != "--stream")

    client = CascadeClient()

    if streaming:
        for chunk in client.chat_stream(prompt):
            print(chunk, end="", flush=True)
        print()
    else:
        response = client.chat(prompt)
        print(response.content)
        print(f"\n[Provider: {response.provider} | Model: {response.model} | {response.latency_ms:.0f}ms]")


if __name__ == "__main__":
    main()
