"""Search tool integrations for LLM agents and discovery."""
from .base import BaseSearchProvider, SearchResult
from .brave_search import BraveSearch
from .serper_search import SerperSearch
from .google_cse import GoogleCSESearch
from .web_scraper import fetch_url


def get_available_search() -> BaseSearchProvider | None:
    """Return the first configured search provider, or None."""
    for cls in [BraveSearch, SerperSearch, GoogleCSESearch]:
        provider = cls()
        if provider.is_configured():
            return provider
    return None


__all__ = [
    "BaseSearchProvider", "SearchResult",
    "BraveSearch", "SerperSearch", "GoogleCSESearch",
    "fetch_url", "get_available_search",
]
