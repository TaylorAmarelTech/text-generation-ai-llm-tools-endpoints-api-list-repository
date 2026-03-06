"""OpenAI-compatible API adapter.

Works with: OpenAI, Groq, Cerebras, Mistral, Together, DeepSeek,
OpenRouter, GitHub Models, SambaNova, HuggingFace, and 30+ more.

This is the most common format -- most providers in the directory
are OpenAI-compatible.
"""
from __future__ import annotations

import os

import httpx

from .base import BaseAdapter, AdapterConfig, ChatMessage, ChatResponse


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI-compatible APIs (the majority of providers).

    Usage:
        adapter = OpenAIAdapter(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
        )
        response = adapter.chat([ChatMessage("user", "Hello!")])
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.config.api_key:
            self.config.api_key = os.environ.get("OPENAI_API_KEY", "")

    def _build_request(self, messages: list[ChatMessage], **kwargs) -> dict:
        return {
            "model": kwargs.get("model", self.config.model),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

    def _parse_response(self, data: dict) -> ChatResponse:
        choice = data["choices"][0]
        usage = data.get("usage", {})
        return ChatResponse(
            content=choice["message"]["content"],
            model=data.get("model", self.config.model),
            finish_reason=choice.get("finish_reason", ""),
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
            },
            raw=data,
        )

    def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        url = f"{self.config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self.config.timeout) as client:
            resp = client.post(url, json=self._build_request(messages, **kwargs), headers=headers)
            resp.raise_for_status()
            return self._parse_response(resp.json())

    async def achat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        url = f"{self.config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(url, json=self._build_request(messages, **kwargs), headers=headers)
            resp.raise_for_status()
            return self._parse_response(resp.json())
