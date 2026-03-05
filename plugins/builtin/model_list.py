"""
Model list plugin.

Fetches the full list of available models from each provider's /models
endpoint and saves a catalog.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import httpx

from config import Config
from plugins.base import BasePlugin
from providers import Provider
from scanner import ScanResult, _get_api_key, _build_headers, _resolve_endpoint


@dataclass
class ModelInfo:
    provider_name: str
    model_id: str
    owned_by: str = ""
    context_window: int | None = None


MODELS_FILE = Path(__file__).parent.parent.parent / "data" / "models.json"


class ModellistPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "model_list"

    @property
    def description(self) -> str:
        return "Fetch available models from each provider"

    def register_commands(self) -> dict:
        return {"models": self._cmd_models}

    async def _cmd_models(
        self, providers: list[Provider], config: Config
    ) -> dict[str, list[ModelInfo]]:
        """Fetch models from all providers."""
        catalog: dict[str, list[ModelInfo]] = {}

        async with httpx.AsyncClient(follow_redirects=True) as client:
            tasks = []
            for p in providers:
                if not p.openai_compatible:
                    continue
                api_key = _get_api_key(p)
                if not api_key and p.env_key and p.auth_style != "none":
                    continue
                tasks.append(self._fetch_models(client, p, api_key))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for p, result in zip(
                [p for p in providers if p.openai_compatible], results
            ):
                if isinstance(result, list) and result:
                    catalog[p.name] = result
                    print(f"  {p.name}: {len(result)} models")

        self._save_catalog(catalog)
        return catalog

    async def _fetch_models(
        self, client: httpx.AsyncClient, provider: Provider, api_key: str | None
    ) -> list[ModelInfo]:
        """Fetch models from a provider's /models endpoint."""
        endpoint = _resolve_endpoint(provider)
        headers = _build_headers(provider, api_key)
        url = f"{endpoint}/models"

        try:
            resp = await client.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                return []

            data = resp.json()
            models_data = data.get("data", data) if isinstance(data, dict) else data
            if not isinstance(models_data, list):
                return []

            models: list[ModelInfo] = []
            for m in models_data:
                if not isinstance(m, dict):
                    continue
                models.append(ModelInfo(
                    provider_name=provider.name,
                    model_id=m.get("id", ""),
                    owned_by=m.get("owned_by", ""),
                    context_window=m.get("context_window"),
                ))
            return models

        except Exception:
            return []

    def _save_catalog(self, catalog: dict[str, list[ModelInfo]]) -> None:
        MODELS_FILE.parent.mkdir(exist_ok=True)
        data = {
            name: [asdict(m) for m in models]
            for name, models in catalog.items()
        }
        MODELS_FILE.write_text(json.dumps(data, indent=2))
        print(f"\nModel catalog saved to {MODELS_FILE}")
