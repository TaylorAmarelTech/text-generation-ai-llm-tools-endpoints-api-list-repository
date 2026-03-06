"""Rate limiter and quota tracker for LLM API providers.

Tracks request counts, token usage, and enforces rate limits
per provider to avoid hitting API quotas.
"""
from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ProviderQuota:
    """Rate limit configuration for a provider."""
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    tokens_per_minute: int = 100000
    tokens_per_day: int = 1000000


@dataclass
class UsageStats:
    """Usage statistics for a provider."""
    total_requests: int = 0
    total_tokens: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_errors: int = 0
    total_latency_ms: float = 0.0

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.total_requests if self.total_requests else 0


# Default quotas for known free providers
DEFAULT_QUOTAS: dict[str, ProviderQuota] = {
    "groq": ProviderQuota(requests_per_minute=30, requests_per_day=1000, tokens_per_day=500000),
    "gemini": ProviderQuota(requests_per_minute=15, requests_per_day=250),
    "cerebras": ProviderQuota(requests_per_minute=30, requests_per_day=1000, tokens_per_day=1000000),
    "mistral": ProviderQuota(requests_per_minute=60, tokens_per_day=1000000000),
    "openrouter": ProviderQuota(requests_per_minute=10, requests_per_day=50),
    "github": ProviderQuota(requests_per_minute=10, requests_per_day=150),
    "huggingface": ProviderQuota(requests_per_minute=5, requests_per_day=7200),
    "cohere": ProviderQuota(requests_per_minute=5, requests_per_day=33),
}


class RateLimiter:
    """Thread-safe rate limiter with per-provider quota tracking.

    Usage:
        limiter = RateLimiter()
        if limiter.can_request("groq"):
            # make request...
            limiter.record_request("groq", tokens=150, latency_ms=230)
        else:
            wait_time = limiter.wait_time("groq")
            print(f"Rate limited. Wait {wait_time:.1f}s")
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._quotas: dict[str, ProviderQuota] = dict(DEFAULT_QUOTAS)
        self._minute_requests: dict[str, list[float]] = defaultdict(list)
        self._day_requests: dict[str, list[float]] = defaultdict(list)
        self._minute_tokens: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._stats: dict[str, UsageStats] = defaultdict(UsageStats)

    def set_quota(self, provider: str, quota: ProviderQuota):
        """Set or override quota for a provider."""
        with self._lock:
            self._quotas[provider] = quota

    def _cleanup(self, provider: str, now: float):
        """Remove expired entries."""
        minute_ago = now - 60
        day_ago = now - 86400
        self._minute_requests[provider] = [
            t for t in self._minute_requests[provider] if t > minute_ago
        ]
        self._day_requests[provider] = [
            t for t in self._day_requests[provider] if t > day_ago
        ]
        self._minute_tokens[provider] = [
            (t, n) for t, n in self._minute_tokens[provider] if t > minute_ago
        ]

    def can_request(self, provider: str) -> bool:
        """Check if a request can be made without exceeding rate limits."""
        with self._lock:
            now = time.time()
            self._cleanup(provider, now)
            quota = self._quotas.get(provider)
            if not quota:
                return True  # No quota configured = unlimited

            if len(self._minute_requests[provider]) >= quota.requests_per_minute:
                return False
            if len(self._day_requests[provider]) >= quota.requests_per_day:
                return False

            minute_tokens = sum(n for _, n in self._minute_tokens[provider])
            if minute_tokens >= quota.tokens_per_minute:
                return False

            return True

    def wait_time(self, provider: str) -> float:
        """Seconds to wait before the next request is allowed."""
        with self._lock:
            now = time.time()
            self._cleanup(provider, now)
            quota = self._quotas.get(provider)
            if not quota:
                return 0

            if len(self._minute_requests[provider]) >= quota.requests_per_minute:
                oldest = self._minute_requests[provider][0]
                return max(0, 60 - (now - oldest))

            if len(self._day_requests[provider]) >= quota.requests_per_day:
                oldest = self._day_requests[provider][0]
                return max(0, 86400 - (now - oldest))

            return 0

    def record_request(
        self, provider: str, tokens: int = 0,
        prompt_tokens: int = 0, completion_tokens: int = 0,
        latency_ms: float = 0, error: bool = False,
    ):
        """Record a completed request."""
        with self._lock:
            now = time.time()
            self._minute_requests[provider].append(now)
            self._day_requests[provider].append(now)
            if tokens:
                self._minute_tokens[provider].append((now, tokens))

            stats = self._stats[provider]
            stats.total_requests += 1
            stats.total_tokens += tokens
            stats.total_prompt_tokens += prompt_tokens
            stats.total_completion_tokens += completion_tokens
            stats.total_latency_ms += latency_ms
            if error:
                stats.total_errors += 1

    def get_stats(self, provider: str) -> UsageStats:
        """Get usage statistics for a provider."""
        with self._lock:
            return self._stats.get(provider, UsageStats())

    def get_all_stats(self) -> dict[str, UsageStats]:
        """Get usage statistics for all providers."""
        with self._lock:
            return dict(self._stats)

    def remaining(self, provider: str) -> dict[str, int]:
        """Get remaining quota for a provider."""
        with self._lock:
            now = time.time()
            self._cleanup(provider, now)
            quota = self._quotas.get(provider)
            if not quota:
                return {"rpm": -1, "rpd": -1}  # -1 = unlimited

            rpm_used = len(self._minute_requests[provider])
            rpd_used = len(self._day_requests[provider])
            return {
                "rpm": max(0, quota.requests_per_minute - rpm_used),
                "rpd": max(0, quota.requests_per_day - rpd_used),
            }

    def summary(self) -> str:
        """Human-readable summary of all provider usage."""
        lines = ["Provider Usage Summary:", "=" * 60]
        for provider, stats in sorted(self._stats.items()):
            remaining = self.remaining(provider)
            lines.append(
                f"  {provider:15s} | {stats.total_requests:5d} reqs | "
                f"{stats.total_tokens:8d} tokens | "
                f"avg {stats.avg_latency_ms:.0f}ms | "
                f"remaining: {remaining['rpm']} RPM, {remaining['rpd']} RPD"
            )
        return "\n".join(lines)
