"""Adapter modules that normalize different LLM API formats.

Different providers use different API formats:
- OpenAI format (majority of providers)
- Anthropic Messages API (x-api-key, different request/response shape)
- Cohere Chat API (custom format)
- Google Gemini native API (GenerateContent)

These adapters provide a unified interface so your code works
identically regardless of the underlying API format.
"""
from .base import BaseAdapter, ChatMessage, ChatResponse, AdapterConfig
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .cohere_adapter import CohereAdapter
from .google_adapter import GoogleNativeAdapter

ADAPTERS = {
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "cohere": CohereAdapter,
    "google": GoogleNativeAdapter,
}


def get_adapter(provider_type: str, **kwargs) -> BaseAdapter:
    """Get an adapter by provider type name.

    Args:
        provider_type: One of "openai", "anthropic", "cohere", "google"
        **kwargs: Passed to adapter constructor (api_key, model, etc.)
    """
    cls = ADAPTERS.get(provider_type)
    if not cls:
        raise ValueError(f"Unknown adapter type: {provider_type}. Available: {list(ADAPTERS.keys())}")
    return cls(**kwargs)


__all__ = [
    "BaseAdapter", "ChatMessage", "ChatResponse", "AdapterConfig",
    "OpenAIAdapter", "AnthropicAdapter", "CohereAdapter", "GoogleNativeAdapter",
    "get_adapter", "ADAPTERS",
]
