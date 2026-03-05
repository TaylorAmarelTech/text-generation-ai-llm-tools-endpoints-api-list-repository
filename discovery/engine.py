"""
Discovery engine orchestrator.

Runs configured search strategies, deduplicates results, optionally verifies
endpoints, and produces a list of new provider candidates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from config import Config, load_config
from providers import PROVIDERS, Provider, Tier


@dataclass
class Candidate:
    """A potential new LLM API provider discovered by the engine."""
    name: str
    endpoint: str
    free_limits: str = ""
    models: list[str] = field(default_factory=list)
    openai_compatible: bool = True
    signup_url: str = ""
    notes: str = ""
    source: str = ""            # Which strategy found it
    confidence: float = 0.0     # 0-1 how confident we are this is real
    verified: bool = False      # Has the scanner confirmed it works?
    discovered_at: str = ""


CANDIDATES_FILE = Path(__file__).parent.parent / "data" / "candidates.json"


def _load_candidates() -> list[Candidate]:
    if not CANDIDATES_FILE.exists():
        return []
    data = json.loads(CANDIDATES_FILE.read_text())
    return [Candidate(**c) for c in data]


def _save_candidates(candidates: list[Candidate]) -> None:
    CANDIDATES_FILE.parent.mkdir(exist_ok=True)
    data = [asdict(c) for c in candidates]
    CANDIDATES_FILE.write_text(json.dumps(data, indent=2))


class DiscoveryEngine:
    """Orchestrates multiple discovery strategies to find new LLM endpoints."""

    def __init__(self, config: Config | None = None):
        self.config = config or load_config()
        self.known_endpoints: set[str] = {
            p.endpoint.lower().rstrip("/") for p in PROVIDERS
        }
        self.known_names: set[str] = {p.name.lower() for p in PROVIDERS}

    def _is_known(self, candidate: Candidate) -> bool:
        ep = candidate.endpoint.lower().rstrip("/")
        name = candidate.name.lower()
        return ep in self.known_endpoints or name in self.known_names

    async def run(self, strategies: list[str] | None = None) -> list[Candidate]:
        """Run discovery strategies and return new candidates."""
        strategy_names = strategies or self.config.discovery.strategies
        all_candidates: list[Candidate] = []

        for name in strategy_names:
            strategy = self._load_strategy(name)
            if strategy:
                try:
                    results = await strategy.search(self.config)
                    all_candidates.extend(results)
                except Exception as e:
                    print(f"  Strategy '{name}' failed: {e}")

        # Deduplicate and filter known providers
        seen: set[str] = set()
        new_candidates: list[Candidate] = []
        for c in all_candidates:
            key = c.endpoint.lower().rstrip("/")
            if key not in seen and not self._is_known(c):
                seen.add(key)
                c.discovered_at = datetime.now(timezone.utc).isoformat()
                new_candidates.append(c)

        # Optionally verify via scanner
        if self.config.discovery.auto_verify and new_candidates:
            new_candidates = await self._verify_candidates(new_candidates)

        # Save
        if self.config.discovery.save_candidates:
            existing = _load_candidates()
            existing_eps = {c.endpoint.lower().rstrip("/") for c in existing}
            for c in new_candidates:
                if c.endpoint.lower().rstrip("/") not in existing_eps:
                    existing.append(c)
            _save_candidates(existing)

        return new_candidates

    def _load_strategy(self, name: str):
        """Dynamically load a discovery strategy by name."""
        try:
            if name == "web_search":
                from discovery.strategies.web_search import WebSearchStrategy
                return WebSearchStrategy()
            elif name == "github_search":
                from discovery.strategies.github_search import GitHubSearchStrategy
                return GitHubSearchStrategy()
            elif name == "llm_search":
                from discovery.strategies.llm_search import LLMSearchStrategy
                return LLMSearchStrategy()
            elif name == "directory_scrape":
                from discovery.strategies.directory_scrape import DirectoryScrapeStrategy
                return DirectoryScrapeStrategy()
            elif name == "community":
                from discovery.strategies.community import CommunityStrategy
                return CommunityStrategy()
            else:
                print(f"  Unknown strategy: {name}")
                return None
        except ImportError as e:
            print(f"  Could not load strategy '{name}': {e}")
            return None

    async def _verify_candidates(self, candidates: list[Candidate]) -> list[Candidate]:
        """Use the scanner to verify candidate endpoints are reachable."""
        import httpx
        from scanner import _test_openai_compatible, _build_headers

        async with httpx.AsyncClient(follow_redirects=True) as client:
            for c in candidates:
                try:
                    # Quick check: hit /models
                    url = c.endpoint.rstrip("/") + "/models"
                    headers = {"Content-Type": "application/json"}
                    resp = await client.get(url, headers=headers, timeout=10)
                    if resp.status_code in (200, 401, 403):
                        c.verified = True
                        c.confidence = max(c.confidence, 0.7)
                except Exception:
                    pass

        return candidates

    def get_saved_candidates(self) -> list[Candidate]:
        """Load previously saved candidates."""
        return _load_candidates()

    def candidate_to_provider(self, candidate: Candidate, tier: Tier = Tier.FREE) -> Provider:
        """Convert a verified candidate into a Provider for the registry."""
        env_key = candidate.name.upper().replace(" ", "_").replace(".", "_") + "_API_KEY"
        return Provider(
            name=candidate.name,
            tier=tier,
            endpoint=candidate.endpoint,
            env_key=env_key,
            free_limits=candidate.free_limits,
            models=candidate.models,
            openai_compatible=candidate.openai_compatible,
            signup_url=candidate.signup_url,
            notes=candidate.notes,
        )
