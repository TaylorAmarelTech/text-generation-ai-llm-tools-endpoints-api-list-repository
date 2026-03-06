"""Simple web content fetcher for agent use.

Fetches a URL and returns cleaned text content (HTML tags stripped).
No external dependencies beyond httpx.
"""
from __future__ import annotations
import re
import httpx


async def fetch_url(url: str, timeout: int = 15, max_chars: int = 10000) -> str:
    """Fetch a URL and return cleaned text content.

    Strips HTML tags, scripts, and styles. Limits output to max_chars.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LLMEndpointScanner/1.0)"},
        )
        resp.raise_for_status()
        html = resp.text

    # Strip scripts and styles
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    # Strip all HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars]
