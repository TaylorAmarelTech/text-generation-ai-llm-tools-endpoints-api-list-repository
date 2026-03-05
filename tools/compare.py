"""
Provider comparison tool.

Sends the same prompt to multiple providers and compares responses
side-by-side: latency, output quality, token usage, etc.

Usage:
    python -m tools.compare "Explain recursion" --providers groq cerebras mistral
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

from providers import PROVIDERS, Provider, get_unique_providers
from scanner import _get_api_key, _resolve_endpoint, _build_headers


@dataclass
class CompareResult:
    provider_name: str
    model: str
    response: str
    latency_ms: float
    char_count: int
    error: str = ""


async def compare_providers(
    prompt: str,
    provider_names: list[str] | None = None,
    max_tokens: int = 300,
) -> list[CompareResult]:
    """Send the same prompt to multiple providers and collect results."""
    import httpx

    providers = get_unique_providers()
    if provider_names:
        names_lower = [n.lower() for n in provider_names]
        providers = [
            p for p in providers
            if any(n in p.name.lower() for n in names_lower)
        ]

    # Only test providers we have keys for
    testable = []
    for p in providers:
        if not p.test_model or not p.openai_compatible:
            continue
        api_key = _get_api_key(p)
        if not api_key and p.env_key and p.auth_style != "none":
            continue
        testable.append(p)

    results: list[CompareResult] = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [_query_provider(client, p, prompt, max_tokens) for p in testable]
        results = await asyncio.gather(*tasks)

    return sorted(results, key=lambda r: r.latency_ms if not r.error else 999999)


async def _query_provider(
    client, provider: Provider, prompt: str, max_tokens: int
) -> CompareResult:
    """Send a prompt to a single provider."""
    endpoint = _resolve_endpoint(provider)
    api_key = _get_api_key(provider)
    headers = _build_headers(provider, api_key)

    payload = {
        "model": provider.test_model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    start = time.perf_counter()
    try:
        resp = await client.post(
            f"{endpoint}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
        )
        latency = (time.perf_counter() - start) * 1000

        if resp.status_code != 200:
            return CompareResult(
                provider_name=provider.name,
                model=provider.test_model,
                response="",
                latency_ms=round(latency, 1),
                char_count=0,
                error=f"HTTP {resp.status_code}",
            )

        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        return CompareResult(
            provider_name=provider.name,
            model=provider.test_model,
            response=content,
            latency_ms=round(latency, 1),
            char_count=len(content),
        )

    except Exception as e:
        return CompareResult(
            provider_name=provider.name,
            model=provider.test_model,
            response="",
            latency_ms=(time.perf_counter() - start) * 1000,
            char_count=0,
            error=str(e)[:200],
        )


def main() -> None:
    """CLI: python -m tools.compare 'prompt' [--providers name1 name2]"""
    import argparse
    parser = argparse.ArgumentParser(description="Compare LLM providers")
    parser.add_argument("prompt", help="The prompt to send")
    parser.add_argument("--providers", nargs="*", help="Provider names to compare")
    parser.add_argument("--max-tokens", type=int, default=300)
    args = parser.parse_args()

    results = asyncio.run(compare_providers(
        args.prompt,
        args.providers,
        args.max_tokens,
    ))

    print(f"\nPrompt: {args.prompt}\n")
    print("=" * 80)

    for r in results:
        if r.error:
            print(f"\n[{r.provider_name}] ({r.model}) -- ERROR: {r.error}")
        else:
            print(f"\n[{r.provider_name}] ({r.model}) -- {r.latency_ms:.0f}ms, {r.char_count} chars")
            print("-" * 40)
            print(r.response[:500])
        print()

    # Summary table
    print("=" * 80)
    print(f"{'Provider':<20} {'Model':<30} {'Latency':<10} {'Chars':<8} {'Status'}")
    print("-" * 80)
    for r in results:
        status = "OK" if not r.error else r.error[:20]
        print(f"{r.provider_name:<20} {r.model:<30} {r.latency_ms:>7.0f}ms {r.char_count:>6} {status}")


if __name__ == "__main__":
    main()
