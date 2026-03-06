"""Google Gemini native API adapter.

While Gemini supports OpenAI-compatible endpoints, this adapter uses
Google's native GenerateContent API for access to Gemini-specific features
like grounding, safety settings, and code execution.

Auth: API key passed as query parameter.
"""
from __future__ import annotations

import os

import httpx

from .base import BaseAdapter, AdapterConfig, ChatMessage, ChatResponse


class GoogleNativeAdapter(BaseAdapter):
    """Adapter for Google's native Gemini API (GenerateContent).

    Usage:
        adapter = GoogleNativeAdapter(
            api_key=os.environ["GEMINI_API_KEY"],
            model="gemini-2.0-flash",
        )
        response = adapter.chat([ChatMessage("user", "Hello!")])
    """

    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.config.base_url:
            self.config.base_url = self.DEFAULT_BASE_URL
        if not self.config.api_key:
            self.config.api_key = os.environ.get("GEMINI_API_KEY", "")
        if not self.config.model:
            self.config.model = "gemini-2.0-flash"

    def _build_request(self, messages: list[ChatMessage], **kwargs) -> dict:
        system_text = ""
        contents = []
        for m in messages:
            if m.role == "system":
                system_text = m.content
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m.content}],
                })

        body = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
            },
        }
        if system_text:
            body["systemInstruction"] = {"parts": [{"text": system_text}]}
        return body

    def _parse_response(self, data: dict) -> ChatResponse:
        candidates = data.get("candidates", [])
        if not candidates:
            return ChatResponse(content="", raw=data)

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        usage = data.get("usageMetadata", {})
        return ChatResponse(
            content=text,
            model=self.config.model,
            finish_reason=candidates[0].get("finishReason", ""),
            usage={
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
            },
            raw=data,
        )

    def _get_url(self) -> str:
        return (
            f"{self.config.base_url}/v1beta/models/"
            f"{self.config.model}:generateContent?key={self.config.api_key}"
        )

    def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        with httpx.Client(timeout=self.config.timeout) as client:
            resp = client.post(
                self._get_url(),
                json=self._build_request(messages, **kwargs),
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return self._parse_response(resp.json())

    async def achat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(
                self._get_url(),
                json=self._build_request(messages, **kwargs),
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return self._parse_response(resp.json())
