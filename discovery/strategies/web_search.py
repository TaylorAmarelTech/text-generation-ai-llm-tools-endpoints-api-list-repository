"""
Web search strategy using Brave Search API, Serper, or Google Custom Search.

Searches the web for new LLM API endpoints, then uses an LLM (or regex
heuristics) to extract provider information from the results.
"""

from __future__ import annotations

import re

import httpx

from config import Config
from discovery.engine import Candidate
from discovery.strategies.base import BaseStrategy


class WebSearchStrategy(BaseStrategy):
    """Discover LLM endpoints via web search APIs."""

    @property
    def name(self) -> str:
        return "web_search"

    async def search(self, config: Config) -> list[Candidate]:
        candidates: list[Candidate] = []

        for query in config.search.search_queries:
            results = await self._search_web(query, config)
            for result in results:
                extracted = self._extract_candidates(result)
                candidates.extend(extracted)

        return candidates

    async def _search_web(self, query: str, config: Config) -> list[dict]:
        """Try search APIs in priority order: Brave > Serper > Google."""
        if config.search.brave_api_key:
            return await self._brave_search(query, config)
        elif config.search.serper_api_key:
            return await self._serper_search(query, config)
        elif config.search.google_api_key and config.search.google_cse_id:
            return await self._google_search(query, config)
        return []

    async def _brave_search(self, query: str, config: Config) -> list[dict]:
        """Search using Brave Search API."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={
                    "q": query,
                    "count": config.search.max_results_per_query,
                },
                headers={
                    "X-Subscription-Token": config.search.brave_api_key,
                    "Accept": "application/json",
                },
                timeout=15,
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "description": r.get("description", ""),
                }
                for r in data.get("web", {}).get("results", [])
            ]

    async def _serper_search(self, query: str, config: Config) -> list[dict]:
        """Search using Serper.dev API."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": config.search.max_results_per_query},
                headers={
                    "X-API-KEY": config.search.serper_api_key,
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "description": r.get("snippet", ""),
                }
                for r in data.get("organic", [])
            ]

    async def _google_search(self, query: str, config: Config) -> list[dict]:
        """Search using Google Custom Search API."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "q": query,
                    "key": config.search.google_api_key,
                    "cx": config.search.google_cse_id,
                    "num": min(config.search.max_results_per_query, 10),
                },
                timeout=15,
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "description": r.get("snippet", ""),
                }
                for r in data.get("items", [])
            ]

    def _extract_candidates(self, result: dict) -> list[Candidate]:
        """Extract potential API endpoints from a search result."""
        candidates: list[Candidate] = []
        text = f"{result.get('title', '')} {result.get('description', '')}"
        url = result.get("url", "")

        # Look for API endpoint URLs in the text
        api_patterns = [
            r'(https?://api\.[a-zA-Z0-9.-]+(?:/v\d+)?(?:/openai)?)',
            r'(https?://[a-zA-Z0-9.-]+/(?:v\d+|api/v\d+|inference/v\d+))',
            r'(https?://[a-zA-Z0-9.-]+\.ai/v\d+)',
        ]
        found_urls: set[str] = set()
        for pattern in api_patterns:
            for match in re.finditer(pattern, text):
                found_urls.add(match.group(1))

        for api_url in found_urls:
            # Try to infer a name from the domain
            domain = re.search(r'https?://(?:api\.)?([a-zA-Z0-9.-]+)', api_url)
            name = domain.group(1).split(".")[0].title() if domain else "Unknown"

            candidates.append(Candidate(
                name=name,
                endpoint=api_url,
                source=self.name,
                confidence=0.3,
                notes=f"Found via web search: {result.get('title', '')[:80]}",
                signup_url=url if "signup" in url.lower() or "register" in url.lower() else "",
            ))

        # Even if no API URL found, if the page title mentions "free LLM API",
        # create a low-confidence candidate from the page URL
        keywords = ["free api", "llm api", "inference api", "text generation api"]
        if not candidates and any(kw in text.lower() for kw in keywords):
            domain = re.search(r'https?://(?:www\.)?([a-zA-Z0-9.-]+)', url)
            if domain:
                candidates.append(Candidate(
                    name=domain.group(1).split(".")[0].title(),
                    endpoint=url,
                    source=self.name,
                    confidence=0.15,
                    notes=f"Needs manual review: {result.get('title', '')[:80]}",
                ))

        return candidates
