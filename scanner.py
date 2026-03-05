"""
Endpoint health scanner.

Tests each provider by making a minimal chat completion request (or model list)
and records status, latency, and error details.
"""

from __future__ import annotations

import os
import time
import asyncio
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

from providers import Provider, Tier, PROVIDERS, get_unique_providers

load_dotenv()

# Maximum time to wait for a single provider test (seconds)
TIMEOUT = 30


@dataclass
class ScanResult:
    provider_name: str
    status: str  # "working", "auth_missing", "auth_failed", "error", "timeout", "skipped"
    latency_ms: float | None = None
    error_detail: str = ""
    model_used: str = ""
    response_preview: str = ""


def _get_api_key(provider: Provider) -> str | None:
    """Resolve the API key from environment."""
    if provider.env_key is None:
        return None
    return os.environ.get(provider.env_key, "").strip() or None


def _build_headers(provider: Provider, api_key: str | None) -> dict[str, str]:
    """Build request headers based on auth style."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        if provider.auth_style == "x-api-key":
            headers["x-api-key"] = api_key
        else:
            headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _resolve_endpoint(provider: Provider) -> str:
    """Resolve dynamic parts of the endpoint URL."""
    endpoint = provider.endpoint
    if "{account_id}" in endpoint:
        account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        endpoint = endpoint.replace("{account_id}", account_id)
    return endpoint.rstrip("/")


async def _test_openai_compatible(
    client: httpx.AsyncClient, provider: Provider, api_key: str | None
) -> ScanResult:
    """Test an OpenAI-compatible endpoint with a minimal chat completion."""
    endpoint = _resolve_endpoint(provider)
    headers = _build_headers(provider, api_key)

    if not provider.test_model:
        return ScanResult(
            provider_name=provider.name,
            status="skipped",
            error_detail="No test model configured",
        )

    # Try chat completion with a minimal prompt
    url = f"{endpoint}/chat/completions"
    payload = {
        "model": provider.test_model,
        "messages": [{"role": "user", "content": "Say 'hello' in one word."}],
        "max_tokens": 10,
        "temperature": 0,
    }

    start = time.perf_counter()
    try:
        resp = await client.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        latency = (time.perf_counter() - start) * 1000

        if resp.status_code == 200:
            data = resp.json()
            preview = ""
            try:
                preview = data["choices"][0]["message"]["content"][:100]
            except (KeyError, IndexError):
                preview = str(data)[:100]
            return ScanResult(
                provider_name=provider.name,
                status="working",
                latency_ms=round(latency, 1),
                model_used=provider.test_model,
                response_preview=preview.strip(),
            )
        elif resp.status_code in (401, 403):
            return ScanResult(
                provider_name=provider.name,
                status="auth_failed" if api_key else "auth_missing",
                latency_ms=round(latency, 1),
                error_detail=f"HTTP {resp.status_code}: {resp.text[:200]}",
            )
        elif resp.status_code == 402:
            return ScanResult(
                provider_name=provider.name,
                status="needs_credits",
                latency_ms=round(latency, 1),
                error_detail=f"HTTP 402: Payment required / credits exhausted",
            )
        elif resp.status_code == 429:
            return ScanResult(
                provider_name=provider.name,
                status="rate_limited",
                latency_ms=round(latency, 1),
                error_detail=f"HTTP 429: Rate limited",
            )
        else:
            return ScanResult(
                provider_name=provider.name,
                status="error",
                latency_ms=round(latency, 1),
                error_detail=f"HTTP {resp.status_code}: {resp.text[:200]}",
            )
    except httpx.TimeoutException:
        return ScanResult(
            provider_name=provider.name,
            status="timeout",
            error_detail=f"Request timed out after {TIMEOUT}s",
        )
    except Exception as e:
        return ScanResult(
            provider_name=provider.name,
            status="error",
            error_detail=f"{type(e).__name__}: {str(e)[:200]}",
        )


async def _test_anthropic(
    client: httpx.AsyncClient, provider: Provider, api_key: str | None
) -> ScanResult:
    """Test the Anthropic Messages API (not OpenAI-compatible)."""
    if not api_key:
        return ScanResult(
            provider_name=provider.name,
            status="auth_missing",
            error_detail="ANTHROPIC_API_KEY not set",
        )

    url = f"{provider.endpoint}/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": provider.test_model,
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Say hello."}],
    }

    start = time.perf_counter()
    try:
        resp = await client.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        latency = (time.perf_counter() - start) * 1000

        if resp.status_code == 200:
            data = resp.json()
            preview = ""
            try:
                preview = data["content"][0]["text"][:100]
            except (KeyError, IndexError):
                preview = str(data)[:100]
            return ScanResult(
                provider_name=provider.name,
                status="working",
                latency_ms=round(latency, 1),
                model_used=provider.test_model,
                response_preview=preview.strip(),
            )
        else:
            status = "auth_failed" if resp.status_code in (401, 403) else "error"
            return ScanResult(
                provider_name=provider.name,
                status=status,
                latency_ms=round(latency, 1),
                error_detail=f"HTTP {resp.status_code}: {resp.text[:200]}",
            )
    except httpx.TimeoutException:
        return ScanResult(
            provider_name=provider.name,
            status="timeout",
            error_detail=f"Request timed out after {TIMEOUT}s",
        )
    except Exception as e:
        return ScanResult(
            provider_name=provider.name,
            status="error",
            error_detail=f"{type(e).__name__}: {str(e)[:200]}",
        )


async def _test_models_endpoint(
    client: httpx.AsyncClient, provider: Provider, api_key: str | None
) -> ScanResult:
    """Fallback: just hit /models to see if the endpoint is alive."""
    endpoint = _resolve_endpoint(provider)
    headers = _build_headers(provider, api_key)
    url = f"{endpoint}/models"

    start = time.perf_counter()
    try:
        resp = await client.get(url, headers=headers, timeout=TIMEOUT)
        latency = (time.perf_counter() - start) * 1000

        if resp.status_code == 200:
            return ScanResult(
                provider_name=provider.name,
                status="reachable",
                latency_ms=round(latency, 1),
                error_detail="Models endpoint OK, but no test model configured",
            )
        else:
            return ScanResult(
                provider_name=provider.name,
                status="error",
                latency_ms=round(latency, 1),
                error_detail=f"HTTP {resp.status_code}",
            )
    except Exception as e:
        return ScanResult(
            provider_name=provider.name,
            status="error",
            error_detail=f"{type(e).__name__}: {str(e)[:200]}",
        )


async def scan_provider(
    client: httpx.AsyncClient, provider: Provider
) -> ScanResult:
    """Scan a single provider and return its result."""
    api_key = _get_api_key(provider)

    # Skip local providers unless they're running
    if provider.tier == Tier.LOCAL:
        try:
            endpoint = _resolve_endpoint(provider)
            resp = await client.get(f"{endpoint}/models", timeout=3)
            if resp.status_code == 200:
                return ScanResult(
                    provider_name=provider.name,
                    status="working",
                    error_detail="Local server detected",
                )
        except Exception:
            pass
        return ScanResult(
            provider_name=provider.name,
            status="offline",
            error_detail="Local server not running",
        )

    # For providers needing a key but without one
    if provider.env_key and not api_key and provider.auth_style != "none":
        # Some providers work without auth (OVHcloud)
        if provider.name not in ("OVHcloud AI Endpoints",):
            return ScanResult(
                provider_name=provider.name,
                status="auth_missing",
                error_detail=f"{provider.env_key} not set in environment",
            )

    # Route to the right test method
    if provider.name == "Anthropic":
        return await _test_anthropic(client, provider, api_key)
    elif provider.openai_compatible and provider.test_model:
        return await _test_openai_compatible(client, provider, api_key)
    elif provider.openai_compatible:
        return await _test_models_endpoint(client, provider, api_key)
    else:
        return ScanResult(
            provider_name=provider.name,
            status="skipped",
            error_detail="Non-OpenAI-compatible, no test model",
        )


async def scan_all(
    providers: list[Provider] | None = None,
    concurrency: int = 10,
) -> list[ScanResult]:
    """Scan all providers concurrently and return results."""
    if providers is None:
        providers = get_unique_providers()

    semaphore = asyncio.Semaphore(concurrency)
    results: list[ScanResult] = []

    async def _scan_with_sem(p: Provider) -> ScanResult:
        async with semaphore:
            return await scan_provider(client, p)

    async with httpx.AsyncClient(
        follow_redirects=True,
        limits=httpx.Limits(max_connections=concurrency * 2),
    ) as client:
        tasks = [_scan_with_sem(p) for p in providers]
        results = await asyncio.gather(*tasks)

    return list(results)


def scan_all_sync(providers: list[Provider] | None = None) -> list[ScanResult]:
    """Synchronous wrapper around scan_all."""
    return asyncio.run(scan_all(providers))
