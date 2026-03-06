"""Serper.dev Google Search API wrapper.

Get a free API key at: https://serper.dev
Free tier: 2,500 queries (one-time credits).
"""
from __future__ import annotations
import os
import httpx
from .base import BaseSearchProvider, SearchResult


class SerperSearch(BaseSearchProvider):
    """Search Google via the Serper.dev API."""

    API_URL = "https://google.serper.dev/search"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("SERPER_API_KEY", "")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.API_URL,
                json={"q": query, "num": max_results},
                headers={
                    "X-API-KEY": self.api_key,
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("organic", [])[:max_results]:
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                raw=item,
            ))
        return results
