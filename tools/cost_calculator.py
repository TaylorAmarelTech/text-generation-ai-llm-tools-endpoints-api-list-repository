"""Cost calculator for LLM API providers.

Compares costs across providers for a given workload, helping route
to the cheapest option.

Usage:
    from tools.cost_calculator import CostCalculator, estimate_monthly_cost

    calc = CostCalculator()
    cheapest = calc.cheapest_for(input_tokens=1000, output_tokens=500)
    print(f"Use {cheapest['provider']} at ${cheapest['cost']:.6f}/request")

    monthly = estimate_monthly_cost("groq", requests_per_day=100, avg_input=500, avg_output=200)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProviderPricing:
    """Per-million token pricing for a provider/model combo."""
    provider: str
    model: str
    input_per_m: float   # $/1M input tokens
    output_per_m: float  # $/1M output tokens
    free_tier: str       # description of free allowance
    notes: str = ""


# Pricing data (as of March 2026, approximate)
# Free-tier providers show $0 since they have free quotas
PRICING: list[ProviderPricing] = [
    # Truly free (within limits)
    ProviderPricing("Groq", "llama-3.3-70b", 0.00, 0.00, "~1K RPD", "Free within rate limits"),
    ProviderPricing("Google Gemini", "gemini-2.0-flash", 0.00, 0.00, "500 RPD", "Free within rate limits"),
    ProviderPricing("Cerebras", "llama-3.3-70b", 0.00, 0.00, "1M tokens/day", "Free within rate limits"),
    ProviderPricing("Mistral", "mistral-small-latest", 0.00, 0.00, "1B tokens/mo", "Free within rate limits"),
    ProviderPricing("OpenRouter", "deepseek-r1:free", 0.00, 0.00, "200 RPD", "Free models only"),

    # Paid (after free tier)
    ProviderPricing("DeepSeek", "deepseek-chat", 0.14, 0.28, "5M tokens", "Cheapest frontier model"),
    ProviderPricing("DeepSeek", "deepseek-chat (cache)", 0.014, 0.28, "5M tokens", "Cache hit pricing"),
    ProviderPricing("OpenAI", "gpt-4o-mini", 0.15, 0.60, "$5 credits", ""),
    ProviderPricing("OpenAI", "gpt-4o", 2.50, 10.00, "$5 credits", ""),
    ProviderPricing("Anthropic", "claude-haiku-4-5", 0.80, 4.00, "$5 credits", ""),
    ProviderPricing("Anthropic", "claude-sonnet-4-6", 3.00, 15.00, "$5 credits", ""),
    ProviderPricing("Together AI", "llama-3.3-70b-turbo", 0.88, 0.88, "$5 credits", ""),
    ProviderPricing("Fireworks AI", "llama-3.3-70b", 0.90, 0.90, "$1 credits", ""),
    ProviderPricing("DeepInfra", "llama-3.3-70b", 0.35, 0.40, "$5 credits", ""),
    ProviderPricing("xAI / Grok", "grok-3-mini", 0.30, 0.50, "$25 credits", ""),
    ProviderPricing("Moonshot / Kimi", "moonshot-v1-128k", 0.10, 0.10, "None", "Cache hits $0.01/M"),
    ProviderPricing("MiniMax", "abab6.5s-chat", 0.24, 0.24, "None", "~8% of Sonnet pricing"),
]


class CostCalculator:
    """Compare costs across providers."""

    def __init__(self, pricing: list[ProviderPricing] | None = None):
        self.pricing = pricing or PRICING

    def cost_per_request(
        self,
        provider_model: ProviderPricing,
        input_tokens: int = 500,
        output_tokens: int = 200,
    ) -> float:
        """Calculate cost for a single request."""
        return (
            input_tokens * provider_model.input_per_m
            + output_tokens * provider_model.output_per_m
        ) / 1_000_000

    def rank_by_cost(
        self,
        input_tokens: int = 500,
        output_tokens: int = 200,
        include_free: bool = True,
    ) -> list[dict]:
        """Rank all providers by cost for a given request size."""
        results = []
        for p in self.pricing:
            if not include_free and p.input_per_m == 0 and p.output_per_m == 0:
                continue
            cost = self.cost_per_request(p, input_tokens, output_tokens)
            results.append({
                "provider": p.provider,
                "model": p.model,
                "cost": cost,
                "free_tier": p.free_tier,
                "notes": p.notes,
            })
        results.sort(key=lambda x: x["cost"])
        return results

    def cheapest_for(
        self,
        input_tokens: int = 500,
        output_tokens: int = 200,
        include_free: bool = True,
    ) -> dict:
        """Return the cheapest provider for a given request."""
        ranked = self.rank_by_cost(input_tokens, output_tokens, include_free)
        return ranked[0] if ranked else {}

    def cheapest_paid(
        self,
        input_tokens: int = 500,
        output_tokens: int = 200,
    ) -> dict:
        """Return the cheapest paid provider (excluding free-tier models)."""
        return self.cheapest_for(input_tokens, output_tokens, include_free=False)

    def summary(
        self,
        input_tokens: int = 1000,
        output_tokens: int = 500,
        top_n: int = 10,
    ) -> str:
        """Return a formatted cost comparison table."""
        ranked = self.rank_by_cost(input_tokens, output_tokens)[:top_n]
        lines = [
            f"Cost comparison for {input_tokens} input + {output_tokens} output tokens:",
            f"{'Provider':<20} {'Model':<30} {'Cost':>10} {'Free Tier':<20}",
            "-" * 82,
        ]
        for r in ranked:
            cost_str = "FREE" if r["cost"] == 0 else f"${r['cost']:.6f}"
            lines.append(
                f"{r['provider']:<20} {r['model']:<30} {cost_str:>10} {r['free_tier']:<20}"
            )
        return "\n".join(lines)


def estimate_monthly_cost(
    provider: str,
    requests_per_day: int = 100,
    avg_input: int = 500,
    avg_output: int = 200,
) -> dict:
    """Estimate monthly cost for a given usage pattern."""
    calc = CostCalculator()
    matching = [p for p in calc.pricing if p.provider.lower() == provider.lower()]
    if not matching:
        return {"error": f"Provider '{provider}' not found in pricing data"}

    p = matching[0]
    cost_per_req = calc.cost_per_request(p, avg_input, avg_output)
    monthly_requests = requests_per_day * 30
    monthly_cost = cost_per_req * monthly_requests

    return {
        "provider": p.provider,
        "model": p.model,
        "cost_per_request": cost_per_req,
        "monthly_requests": monthly_requests,
        "monthly_cost": monthly_cost,
        "free_tier": p.free_tier,
    }
