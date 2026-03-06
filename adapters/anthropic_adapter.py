"""Anthropic Messages API adapter.

Anthropic uses a different API format from OpenAI:
- Auth via x-api-key header (not Bearer token)
- System prompt is a top-level parameter (not a message)
- Different request/response structure
- anthropic-version header required

This adapter normalizes it to the same ChatMessage/ChatResponse interface.
"""
from __future__ import annotations

import os

import httpx

from .base import BaseAdapter, AdapterConfig, ChatMessage, ChatResponse


class AnthropicAdapter(BaseAdapter):
    """Adapter for the Anthropic Messages API.

    Usage:
        adapter = AnthropicAdapter(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            model="claude-sonnet-4-6",
        )
        response = adapter.chat([
            ChatMessage("system", "You are helpful."),
            ChatMessage("user", "Hello!"),
        ])
    """

    DEFAULT_BASE_URL = "https://api.anthropic.com"
    API_VERSION = "2023-06-01"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.config.base_url:
            self.config.base_url = self.DEFAULT_BASE_URL
        if not self.config.api_key:
            self.config.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.config.model:
            self.config.model = "claude-sonnet-4-6"

    def _build_request(self, messages: list[ChatMessage], **kwargs) -> dict:
        # Extract system message (Anthropic puts it at top level)
        system_text = ""
        api_messages = []
        for m in messages:
            if m.role == "system":
                system_text = m.content
            else:
                api_messages.append({"role": m.role, "content": m.content})

        body = {
            "model": kwargs.get("model", self.config.model),
            "messages": api_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        if system_text:
            body["system"] = system_text
        return body

    def _get_headers(self) -> dict:
        return {
            "x-api-key": self.config.api_key,
            "anthropic-version": self.API_VERSION,
            "Content-Type": "application/json",
        }

    def _parse_response(self, data: dict) -> ChatResponse:
        content_blocks = data.get("content", [])
        text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
        usage = data.get("usage", {})
        return ChatResponse(
            content=text,
            model=data.get("model", self.config.model),
            finish_reason=data.get("stop_reason", ""),
            usage={
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
            },
            raw=data,
        )

    def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        url = f"{self.config.base_url}/v1/messages"
        with httpx.Client(timeout=self.config.timeout) as client:
            resp = client.post(
                url,
                json=self._build_request(messages, **kwargs),
                headers=self._get_headers(),
            )
            resp.raise_for_status()
            return self._parse_response(resp.json())

    async def achat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        url = f"{self.config.base_url}/v1/messages"
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(
                url,
                json=self._build_request(messages, **kwargs),
                headers=self._get_headers(),
            )
            resp.raise_for_status()
            return self._parse_response(resp.json())
