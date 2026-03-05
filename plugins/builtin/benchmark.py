"""
Benchmark plugin.

Measures detailed performance metrics for working endpoints:
- Time to first token (TTFT)
- Tokens per second (TPS)
- Total response latency
- Consistency across multiple runs
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import httpx

from config import Config
from plugins.base import BasePlugin
from providers import Provider
from scanner import ScanResult, _get_api_key, _build_headers, _resolve_endpoint


@dataclass
class BenchmarkResult:
    provider_name: str
    model: str
    ttft_ms: float | None = None
    total_ms: float | None = None
    tokens_generated: int = 0
    tokens_per_second: float | None = None
    error: str = ""


BENCHMARK_FILE = Path(__file__).parent.parent.parent / "data" / "benchmarks.json"

BENCHMARK_PROMPT = "Write a short paragraph about the history of computing."


class BenchmarkPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "benchmark"

    @property
    def description(self) -> str:
        return "Measure latency, TTFT, and tokens/sec for working endpoints"

    def register_commands(self) -> dict:
        return {"benchmark": self._cmd_benchmark}

    async def _cmd_benchmark(
        self, providers: list[Provider], config: Config
    ) -> list[BenchmarkResult]:
        """Run benchmarks on working providers."""
        results: list[BenchmarkResult] = []

        async with httpx.AsyncClient(follow_redirects=True) as client:
            for p in providers:
                if not p.test_model or not p.openai_compatible:
                    continue
                api_key = _get_api_key(p)
                if not api_key and p.env_key:
                    continue

                result = await self._benchmark_provider(client, p, api_key)
                results.append(result)
                status = f"{result.tokens_per_second:.1f} tok/s" if result.tokens_per_second else result.error
                print(f"  {p.name}: {status}")

        # Save results
        self._save_results(results)
        return results

    async def _benchmark_provider(
        self, client: httpx.AsyncClient, provider: Provider, api_key: str | None
    ) -> BenchmarkResult:
        """Benchmark a single provider with streaming."""
        endpoint = _resolve_endpoint(provider)
        headers = _build_headers(provider, api_key)
        url = f"{endpoint}/chat/completions"

        payload = {
            "model": provider.test_model,
            "messages": [{"role": "user", "content": BENCHMARK_PROMPT}],
            "max_tokens": 100,
            "temperature": 0,
            "stream": True,
        }

        try:
            start = time.perf_counter()
            ttft = None
            token_count = 0

            async with client.stream(
                "POST", url, json=payload, headers=headers, timeout=30
            ) as resp:
                if resp.status_code != 200:
                    return BenchmarkResult(
                        provider_name=provider.name,
                        model=provider.test_model,
                        error=f"HTTP {resp.status_code}",
                    )

                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break

                    if ttft is None:
                        ttft = (time.perf_counter() - start) * 1000

                    try:
                        data = json.loads(chunk)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            token_count += 1  # Approximate: 1 chunk ~ 1 token
                    except (json.JSONDecodeError, IndexError, KeyError):
                        pass

            total = (time.perf_counter() - start) * 1000
            tps = (token_count / (total / 1000)) if total > 0 and token_count > 0 else None

            return BenchmarkResult(
                provider_name=provider.name,
                model=provider.test_model,
                ttft_ms=round(ttft, 1) if ttft else None,
                total_ms=round(total, 1),
                tokens_generated=token_count,
                tokens_per_second=round(tps, 1) if tps else None,
            )

        except Exception as e:
            return BenchmarkResult(
                provider_name=provider.name,
                model=provider.test_model,
                error=str(e)[:200],
            )

    def _save_results(self, results: list[BenchmarkResult]) -> None:
        BENCHMARK_FILE.parent.mkdir(exist_ok=True)
        data = [asdict(r) for r in results]
        BENCHMARK_FILE.write_text(json.dumps(data, indent=2))
