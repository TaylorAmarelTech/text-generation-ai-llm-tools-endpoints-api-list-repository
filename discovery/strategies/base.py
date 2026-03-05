"""
Base class for discovery strategies.

All strategies implement the same interface so the engine can
orchestrate them uniformly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from config import Config
from discovery.engine import Candidate


class BaseStrategy(ABC):
    """Base class for provider discovery strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this strategy."""
        ...

    @abstractmethod
    async def search(self, config: Config) -> list[Candidate]:
        """
        Run the search and return potential candidates.

        Each strategy should:
        1. Search its data source
        2. Parse results into Candidate objects
        3. Set confidence scores (0-1)
        4. Set the `source` field to self.name
        """
        ...
