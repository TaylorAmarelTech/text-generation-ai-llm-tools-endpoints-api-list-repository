"""Research agent that searches the web and synthesizes information.

Uses search tools (Brave, Serper, Google CSE) to find information,
then synthesizes comprehensive answers with source citations.
"""
from __future__ import annotations

import asyncio

from .base import BaseAgent, AgentConfig, AGENT_PRESETS


class ResearchAgent(BaseAgent):
    """Agent that uses web search to research topics and answer questions.

    Usage:
        from search import get_available_search
        agent = ResearchAgent("groq", search_provider=get_available_search())
        answer = agent.chat("What are the latest developments in fusion energy?")
    """

    def __init__(
        self,
        config: AgentConfig | str = "groq",
        search_provider=None,
    ):
        super().__init__(config)
        self.search_provider = search_provider
        self.config.system_prompt = (
            "You are a research assistant. Use the search tool to find information, "
            "then synthesize a comprehensive answer with source citations. "
            "Always cite sources with URLs. If you need more information, search "
            "again with different queries. Be thorough but concise."
        )
        self._register_tools()

    def _register_tools(self):
        self.register_tool(
            name="web_search",
            description="Search the web for information. Returns titles, URLs, and snippets.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                },
                "required": ["query"],
            },
            function=self._search,
        )
        self.register_tool(
            name="fetch_page",
            description="Fetch and read the text content of a web page.",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to fetch"},
                },
                "required": ["url"],
            },
            function=self._fetch_page,
        )

    def _search(self, query: str) -> str:
        if not self.search_provider:
            return (
                "Error: No search provider configured. "
                "Set BRAVE_API_KEY, SERPER_API_KEY, or GOOGLE_API_KEY in .env"
            )
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    results = pool.submit(
                        asyncio.run,
                        self.search_provider.search(query, max_results=5),
                    ).result()
            else:
                results = loop.run_until_complete(
                    self.search_provider.search(query, max_results=5)
                )
        except RuntimeError:
            results = asyncio.run(self.search_provider.search(query, max_results=5))

        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. [{r.title}]({r.url})\n   {r.snippet}")
        return "\n".join(lines)

    def _fetch_page(self, url: str) -> str:
        from search.web_scraper import fetch_url
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    text = pool.submit(asyncio.run, fetch_url(url)).result()
            else:
                text = loop.run_until_complete(fetch_url(url))
        except RuntimeError:
            text = asyncio.run(fetch_url(url))
        return text[:5000]
