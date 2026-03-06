"""Google Custom Search Engine API wrapper.

Setup: https://programmablesearchengine.google.com/
Free tier: 100 queries/day.
"""
from __future__ import annotations
import os
import httpx
from .base import BaseSearchProvider, SearchResult


class GoogleCSESearch(BaseSearchProvider):
    """Search using Google Custom Search Engine."""

    API_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, api_key: str | None = None, cse_id: str | None = None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        self.cse_id = cse_id or os.environ.get("GOOGLE_CSE_ID", "")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.cse_id)

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self.API_URL,
                params={
                    "key": self.api_key,
                    "cx": self.cse_id,
                    "q": query,
                    "num": min(max_results, 10),
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("items", [])[:max_results]:
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                raw=item,
            ))
        return results
