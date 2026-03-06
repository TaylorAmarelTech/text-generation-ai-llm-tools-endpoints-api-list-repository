"""Base interface for search providers."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    snippet: str
    score: float = 0.0
    raw: dict = field(default_factory=dict)


class BaseSearchProvider(ABC):
    """Abstract base class for search providers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Search and return results."""
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if this provider has its required API keys set."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(configured={self.is_configured()})"
