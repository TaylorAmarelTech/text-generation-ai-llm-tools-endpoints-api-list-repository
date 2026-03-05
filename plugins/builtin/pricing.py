"""
Pricing tracker plugin.

Tracks and compares pricing across providers. Can fetch pricing from
OpenRouter's API or from manual configuration.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import httpx

from config import Config
from plugins.base import BasePlugin
from providers import Provider
from scanner import ScanResult


@dataclass
class PricingInfo:
    provider_name: str
    model_id: str
    input_price_per_m: float | None = None   # $/M input tokens
    output_price_per_m: float | None = None  # $/M output tokens
    is_free: bool = False
    source: str = ""


PRICING_FILE = Path(__file__).parent.parent.parent / "data" / "pricing.json"


class PricingPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "pricing"

    @property
    def description(self) -> str:
        return "Track and compare model pricing across providers"

    def register_commands(self) -> dict:
        return {"pricing": self._cmd_pricing}

    async def _cmd_pricing(
        self, providers: list[Provider], config: Config
    ) -> list[PricingInfo]:
        """Fetch pricing data from available sources."""
        all_pricing: list[PricingInfo] = []

        # Fetch from OpenRouter (has pricing for many models)
        or_pricing = await self._fetch_openrouter_pricing()
        all_pricing.extend(or_pricing)

        # Save
        PRICING_FILE.parent.mkdir(exist_ok=True)
        PRICING_FILE.write_text(json.dumps(
            [asdict(p) for p in all_pricing], indent=2
        ))
        print(f"Pricing data saved to {PRICING_FILE}")

        # Print summary
        free_count = sum(1 for p in all_pricing if p.is_free)
        print(f"Found {len(all_pricing)} model prices ({free_count} free)")

        return all_pricing

    async def _fetch_openrouter_pricing(self) -> list[PricingInfo]:
        """Fetch pricing from OpenRouter's public models endpoint."""
        pricing: list[PricingInfo] = []

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get("https://openrouter.ai/api/v1/models")
                if resp.status_code != 200:
                    return []

                data = resp.json()
                for model in data.get("data", []):
                    p = model.get("pricing", {})
                    prompt = p.get("prompt", "0")
                    completion = p.get("completion", "0")

                    try:
                        input_price = float(prompt) * 1_000_000
                        output_price = float(completion) * 1_000_000
                    except (ValueError, TypeError):
                        continue

                    pricing.append(PricingInfo(
                        provider_name="OpenRouter",
                        model_id=model.get("id", ""),
                        input_price_per_m=round(input_price, 4),
                        output_price_per_m=round(output_price, 4),
                        is_free=(input_price == 0 and output_price == 0),
                        source="openrouter",
                    ))

        except Exception as e:
            print(f"  Error fetching OpenRouter pricing: {e}")

        return pricing
