"""
Directory scraping strategy.

Fetches known API directory pages and extracts provider information.
"""

from __future__ import annotations

import re

import httpx

from config import Config
from discovery.engine import Candidate
from discovery.strategies.base import BaseStrategy

# Public API directories to check
DIRECTORIES = [
    {
        "name": "OpenRouter models",
        "url": "https://openrouter.ai/api/v1/models",
        "type": "json_api",
    },
]


class DirectoryScrapeStrategy(BaseStrategy):
    """Scrape known API directories for providers."""

    @property
    def name(self) -> str:
        return "directory_scrape"

    async def search(self, config: Config) -> list[Candidate]:
        candidates: list[Candidate] = []

        async with httpx.AsyncClient(timeout=15) as client:
            for directory in DIRECTORIES:
                try:
                    if directory["type"] == "json_api":
                        results = await self._fetch_json(client, directory)
                    else:
                        results = await self._fetch_html(client, directory)
                    candidates.extend(results)
                except Exception as e:
                    print(f"  Directory '{directory['name']}' failed: {e}")

        return candidates

    async def _fetch_json(self, client: httpx.AsyncClient, directory: dict) -> list[Candidate]:
        """Fetch a JSON API directory and extract free models/providers."""
        resp = await client.get(directory["url"])
        if resp.status_code != 200:
            return []

        data = resp.json()
        candidates: list[Candidate] = []

        # Handle OpenRouter-style model list
        if isinstance(data, dict) and "data" in data:
            free_models = [
                m for m in data["data"]
                if isinstance(m, dict) and m.get("pricing", {}).get("prompt") == "0"
            ]
            # Group by unique provider (first part of model ID)
            providers: dict[str, list[str]] = {}
            for m in free_models:
                model_id = m.get("id", "")
                provider = model_id.split("/")[0] if "/" in model_id else model_id
                providers.setdefault(provider, []).append(model_id)

            for prov, models in providers.items():
                candidates.append(Candidate(
                    name=f"{prov} (via OpenRouter)",
                    endpoint="https://openrouter.ai/api/v1",
                    free_limits="Free on OpenRouter",
                    models=models[:5],
                    source="directory:openrouter",
                    confidence=0.8,
                    notes=f"{len(models)} free models available",
                ))

        return candidates

    async def _fetch_html(self, client: httpx.AsyncClient, directory: dict) -> list[Candidate]:
        """Fetch an HTML page and extract API URLs."""
        resp = await client.get(directory["url"])
        if resp.status_code != 200:
            return []

        candidates: list[Candidate] = []
        text = resp.text

        # Find API endpoint URLs
        for match in re.finditer(r'(https?://api\.[a-zA-Z0-9.-]+/v\d+)', text):
            url = match.group(1)
            domain = re.search(r'api\.([a-zA-Z0-9-]+)', url)
            name = domain.group(1).title() if domain else "Unknown"
            candidates.append(Candidate(
                name=name,
                endpoint=url,
                source=f"directory:{directory['name']}",
                confidence=0.3,
            ))

        return candidates
