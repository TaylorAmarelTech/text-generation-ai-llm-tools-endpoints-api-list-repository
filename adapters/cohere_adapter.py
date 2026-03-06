"""Cohere Chat API adapter.

Cohere uses its own API format:
- Auth via Authorization: Bearer header
- Different request body (message, chat_history, preamble)
- Different response shape

This adapter normalizes it to the same ChatMessage/ChatResponse interface.
"""
from __future__ import annotations

import os

import httpx

from .base import BaseAdapter, AdapterConfig, ChatMessage, ChatResponse


class CohereAdapter(BaseAdapter):
    """Adapter for the Cohere Chat API.

    Usage:
        adapter = CohereAdapter(
            api_key=os.environ["COHERE_API_KEY"],
            model="command-r-plus",
        )
        response = adapter.chat([ChatMessage("user", "Hello!")])
    """

    DEFAULT_BASE_URL = "https://api.cohere.com"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.config.base_url:
            self.config.base_url = self.DEFAULT_BASE_URL
        if not self.config.api_key:
            self.config.api_key = os.environ.get("COHERE_API_KEY", "")
        if not self.config.model:
            self.config.model = "command-r-plus"

    def _build_request(self, messages: list[ChatMessage], **kwargs) -> dict:
        # Cohere v2 chat format
        preamble = ""
        cohere_messages = []
        for m in messages:
            if m.role == "system":
                preamble = m.content
            else:
                role = "USER" if m.role == "user" else "CHATBOT"
                cohere_messages.append({"role": role, "content": m.content})

        # The last user message is the current query
        body = {
            "model": kwargs.get("model", self.config.model),
            "messages": cohere_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        if preamble:
            body["preamble"] = preamble
        return body

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def _parse_response(self, data: dict) -> ChatResponse:
        # Cohere v2 response
        text = data.get("message", {}).get("content", [{}])
        if isinstance(text, list) and text:
            text = text[0].get("text", "")
        elif isinstance(text, str):
            pass
        else:
            text = str(text)
        usage = data.get("usage", {}).get("tokens", {})
        return ChatResponse(
            content=text,
            model=data.get("model", self.config.model),
            finish_reason=data.get("finish_reason", ""),
            usage={
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
            },
            raw=data,
        )

    def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        url = f"{self.config.base_url}/v2/chat"
        with httpx.Client(timeout=self.config.timeout) as client:
            resp = client.post(
                url,
                json=self._build_request(messages, **kwargs),
                headers=self._get_headers(),
            )
            resp.raise_for_status()
            return self._parse_response(resp.json())

    async def achat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        url = f"{self.config.base_url}/v2/chat"
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(
                url,
                json=self._build_request(messages, **kwargs),
                headers=self._get_headers(),
            )
            resp.raise_for_status()
            return self._parse_response(resp.json())
