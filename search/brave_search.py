"""Brave Search API wrapper.

Get a free API key at: https://brave.com/search/api/
Free tier: 2,000 queries/month.
"""
from __future__ import annotations
import os
import httpx
from .base import BaseSearchProvider, SearchResult


class BraveSearch(BaseSearchProvider):
    """Search the web using the Brave Search API."""

    API_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY", "")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self.API_URL,
                params={"q": query, "count": max_results},
                headers={
                    "X-Subscription-Token": self.api_key,
                    "Accept": "application/json",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("web", {}).get("results", [])[:max_results]:
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description", ""),
                raw=item,
            ))
        return results
