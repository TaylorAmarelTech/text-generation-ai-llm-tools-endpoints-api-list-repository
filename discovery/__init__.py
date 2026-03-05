"""
AI-powered discovery engine for finding new LLM API endpoints.

Combines multiple search strategies (web search, GitHub, LLM-assisted)
to discover and validate new free/cheap LLM providers.
"""

from discovery.engine import DiscoveryEngine, Candidate

__all__ = ["DiscoveryEngine", "Candidate"]
