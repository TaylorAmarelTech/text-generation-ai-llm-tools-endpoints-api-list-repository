"""
GitHub search strategy.

Searches GitHub for awesome-lists, API directories, and repos that catalog
free LLM endpoints. Uses the GitHub API (with GITHUB_TOKEN for auth).
"""

from __future__ import annotations

import os
import re

import httpx

from config import Config
from discovery.engine import Candidate
from discovery.strategies.base import BaseStrategy

# Well-known awesome-lists and directories to check
KNOWN_REPOS = [
    "cheahjs/free-llm-api-resources",
    "zukixa/cool-ai-stuff",
    "LiLittleCat/awesome-free-chatgpt",
    "ai-boost/awesome-prompts",
]

SEARCH_QUERIES = [
    "free LLM API endpoint list",
    "awesome free AI API",
    "openai compatible free endpoint",
    "free inference API directory",
]


class GitHubSearchStrategy(BaseStrategy):
    """Discover LLM endpoints by searching GitHub repos."""

    @property
    def name(self) -> str:
        return "github_search"

    async def search(self, config: Config) -> list[Candidate]:
        token = os.environ.get("GITHUB_TOKEN", "")
        candidates: list[Candidate] = []

        async with httpx.AsyncClient(timeout=20) as client:
            headers = {"Accept": "application/vnd.github.v3+json"}
            if token:
                headers["Authorization"] = f"token {token}"

            # Search known repos for endpoint lists
            for repo in KNOWN_REPOS:
                repo_candidates = await self._search_repo(client, headers, repo)
                candidates.extend(repo_candidates)

            # Search GitHub code for API endpoints
            for query in SEARCH_QUERIES:
                code_candidates = await self._search_code(client, headers, query)
                candidates.extend(code_candidates)

        return candidates

    async def _search_repo(
        self, client: httpx.AsyncClient, headers: dict, repo: str
    ) -> list[Candidate]:
        """Fetch README from a repo and extract API endpoints."""
        candidates: list[Candidate] = []

        # Try common readme files
        for filename in ["README.md", "readme.md"]:
            url = f"https://raw.githubusercontent.com/{repo}/main/{filename}"
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code != 200:
                    url = url.replace("/main/", "/master/")
                    resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    extracted = self._extract_from_markdown(resp.text, repo)
                    candidates.extend(extracted)
                    break
            except Exception:
                continue

        return candidates

    async def _search_code(
        self, client: httpx.AsyncClient, headers: dict, query: str
    ) -> list[Candidate]:
        """Search GitHub code for API endpoint references."""
        candidates: list[Candidate] = []

        try:
            resp = await client.get(
                "https://api.github.com/search/code",
                params={"q": query, "per_page": 5},
                headers=headers,
            )
            if resp.status_code != 200:
                return []

            for item in resp.json().get("items", []):
                # Check file content for API URLs
                raw_url = item.get("html_url", "").replace(
                    "github.com", "raw.githubusercontent.com"
                ).replace("/blob/", "/")
                try:
                    content_resp = await client.get(raw_url, headers=headers)
                    if content_resp.status_code == 200:
                        extracted = self._extract_from_text(
                            content_resp.text[:5000], f"github:{item.get('repository', {}).get('full_name', '')}"
                        )
                        candidates.extend(extracted)
                except Exception:
                    continue
        except Exception:
            pass

        return candidates

    def _extract_from_markdown(self, text: str, source: str) -> list[Candidate]:
        """Extract API endpoints from markdown content."""
        return self._extract_from_text(text, f"github:{source}")

    def _extract_from_text(self, text: str, source: str) -> list[Candidate]:
        """Extract API endpoint URLs from arbitrary text."""
        candidates: list[Candidate] = []

        # Find API-looking URLs
        patterns = [
            r'(https?://api\.[a-zA-Z0-9.-]+(?:/v\d+)?(?:/openai)?(?:/chat/completions)?)',
            r'(https?://[a-zA-Z0-9.-]+(?:\.[a-z]{2,})/(?:v\d+|api/v\d+|inference/v\d+))',
        ]

        found: set[str] = set()
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                url = match.group(1)
                # Clean up: remove /chat/completions suffix
                url = re.sub(r'/chat/completions/?$', '', url)
                found.add(url)

        for url in found:
            domain = re.search(r'https?://(?:api\.)?([a-zA-Z0-9-]+)', url)
            name = domain.group(1).title() if domain else "Unknown"
            candidates.append(Candidate(
                name=name,
                endpoint=url,
                source=source,
                confidence=0.4,
                notes=f"Found in GitHub: {source}",
            ))

        return candidates
