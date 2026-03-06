"""Base adapter interface for normalizing LLM API formats."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    """Unified message format across all adapters."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ChatResponse:
    """Unified response format across all adapters."""
    content: str
    model: str = ""
    finish_reason: str = ""
    usage: dict = field(default_factory=dict)  # {"prompt_tokens": N, "completion_tokens": N}
    raw: dict = field(default_factory=dict)  # Original provider response


@dataclass
class AdapterConfig:
    """Configuration for an adapter."""
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    max_tokens: int = 1024
    temperature: float = 0.7
    timeout: int = 30


class BaseAdapter(ABC):
    """Abstract base class for LLM API adapters.

    All adapters accept and return the same ChatMessage/ChatResponse types,
    regardless of the underlying API format.
    """

    def __init__(self, config: AdapterConfig | None = None, **kwargs):
        if config:
            self.config = config
        else:
            self.config = AdapterConfig(**{
                k: v for k, v in kwargs.items()
                if k in AdapterConfig.__dataclass_fields__
            })

    @abstractmethod
    def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        """Send messages and get a response."""
        ...

    @abstractmethod
    async def achat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        """Async version of chat."""
        ...

    def simple_chat(self, prompt: str, system: str = "") -> str:
        """Convenience method: send a single prompt, get text back."""
        messages = []
        if system:
            messages.append(ChatMessage(role="system", content=system))
        messages.append(ChatMessage(role="user", content=prompt))
        return self.chat(messages).content

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.config.model!r})"
