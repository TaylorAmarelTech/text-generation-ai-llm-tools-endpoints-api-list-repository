"""
Community search strategy.

Searches Reddit, Hacker News, and developer forums for mentions of
new free LLM API endpoints. Uses public JSON APIs (no auth needed).
"""

from __future__ import annotations

import re

import httpx

from config import Config
from discovery.engine import Candidate
from discovery.strategies.base import BaseStrategy

REDDIT_SEARCHES = [
    "free LLM API endpoint",
    "free AI inference API",
    "OpenAI compatible free",
]

SUBREDDITS = [
    "LocalLLaMA",
    "MachineLearning",
    "artificial",
]


class CommunityStrategy(BaseStrategy):
    """Discover providers from community discussions."""

    @property
    def name(self) -> str:
        return "community"

    async def search(self, config: Config) -> list[Candidate]:
        candidates: list[Candidate] = []

        async with httpx.AsyncClient(
            timeout=15,
            headers={"User-Agent": "LLMEndpointScanner/1.0"},
        ) as client:
            # Search Reddit
            for query in REDDIT_SEARCHES:
                reddit_results = await self._search_reddit(client, query)
                candidates.extend(reddit_results)

            # Search Hacker News
            hn_results = await self._search_hn(client)
            candidates.extend(hn_results)

        return candidates

    async def _search_reddit(self, client: httpx.AsyncClient, query: str) -> list[Candidate]:
        """Search Reddit for API endpoint mentions."""
        candidates: list[Candidate] = []

        try:
            resp = await client.get(
                "https://www.reddit.com/search.json",
                params={
                    "q": query,
                    "sort": "new",
                    "limit": 10,
                    "t": "month",
                },
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                text = f"{post_data.get('title', '')} {post_data.get('selftext', '')}"
                extracted = self._extract_endpoints(text, "reddit")
                candidates.extend(extracted)
        except Exception:
            pass

        return candidates

    async def _search_hn(self, client: httpx.AsyncClient) -> list[Candidate]:
        """Search Hacker News via Algolia API."""
        candidates: list[Candidate] = []

        try:
            resp = await client.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": "free LLM API",
                    "tags": "story",
                    "hitsPerPage": 10,
                },
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            for hit in data.get("hits", []):
                text = f"{hit.get('title', '')} {hit.get('url', '')}"
                extracted = self._extract_endpoints(text, "hackernews")
                candidates.extend(extracted)
        except Exception:
            pass

        return candidates

    def _extract_endpoints(self, text: str, source: str) -> list[Candidate]:
        """Extract API endpoints from text."""
        candidates: list[Candidate] = []
        patterns = [
            r'(https?://api\.[a-zA-Z0-9.-]+(?:/v\d+)?)',
            r'(https?://[a-zA-Z0-9.-]+/(?:v\d+|api/v\d+|inference/v\d+))',
        ]

        found: set[str] = set()
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                found.add(match.group(1))

        for url in found:
            domain = re.search(r'https?://(?:api\.)?([a-zA-Z0-9-]+)', url)
            name = domain.group(1).title() if domain else "Unknown"
            candidates.append(Candidate(
                name=name,
                endpoint=url,
                source=f"community:{source}",
                confidence=0.25,
                notes=f"Mentioned in {source} discussion",
            ))

        return candidates
