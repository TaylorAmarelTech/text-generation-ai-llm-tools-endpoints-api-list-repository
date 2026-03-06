"""Conversation manager for saving, loading, and exporting chat histories.

Supports JSON and Markdown export formats.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Message:
    """A single message in a conversation."""
    role: str
    content: str
    timestamp: str = ""
    provider: str = ""
    model: str = ""
    latency_ms: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class Conversation:
    """A complete conversation with metadata."""
    id: str = ""
    title: str = ""
    messages: list[Message] = field(default_factory=list)
    created_at: str = ""
    provider: str = ""
    model: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.id:
            self.id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content, **kwargs))

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Export conversation as readable Markdown."""
        lines = [f"# {self.title or 'Conversation'}", ""]
        if self.provider or self.model:
            lines.append(f"**Provider:** {self.provider} | **Model:** {self.model}")
            lines.append(f"**Date:** {self.created_at}")
            lines.append("")
        lines.append("---")
        lines.append("")
        for msg in self.messages:
            role_label = {"system": "System", "user": "User", "assistant": "Assistant"}.get(
                msg.role, msg.role.title()
            )
            lines.append(f"### {role_label}")
            lines.append("")
            lines.append(msg.content)
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def from_dict(cls, data: dict) -> Conversation:
        messages = [Message(**m) for m in data.pop("messages", [])]
        return cls(messages=messages, **data)

    @classmethod
    def from_json(cls, json_str: str) -> Conversation:
        return cls.from_dict(json.loads(json_str))


class ConversationManager:
    """Manage multiple conversations with save/load support.

    Usage:
        manager = ConversationManager("data/conversations")
        conv = manager.new("My Chat", provider="groq")
        conv.add_message("user", "Hello!")
        conv.add_message("assistant", "Hi there!")
        manager.save(conv)

        # Later...
        loaded = manager.load("20240315_143022")
        all_convs = manager.list_conversations()
    """

    def __init__(self, directory: str = "data/conversations"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def new(self, title: str = "", **kwargs) -> Conversation:
        """Create a new conversation."""
        return Conversation(title=title, **kwargs)

    def save(self, conversation: Conversation, format: str = "json"):
        """Save a conversation to disk."""
        if format == "json":
            path = self.directory / f"{conversation.id}.json"
            path.write_text(conversation.to_json(), encoding="utf-8")
        elif format == "md":
            path = self.directory / f"{conversation.id}.md"
            path.write_text(conversation.to_markdown(), encoding="utf-8")
        return str(path)

    def load(self, conversation_id: str) -> Conversation:
        """Load a conversation from disk."""
        path = self.directory / f"{conversation_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Conversation not found: {path}")
        return Conversation.from_json(path.read_text(encoding="utf-8"))

    def list_conversations(self) -> list[dict]:
        """List all saved conversations with basic metadata."""
        results = []
        for path in sorted(self.directory.glob("*.json"), reverse=True):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                results.append({
                    "id": data.get("id", path.stem),
                    "title": data.get("title", ""),
                    "created_at": data.get("created_at", ""),
                    "messages": len(data.get("messages", [])),
                    "provider": data.get("provider", ""),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return results

    def delete(self, conversation_id: str):
        """Delete a conversation."""
        path = self.directory / f"{conversation_id}.json"
        if path.exists():
            path.unlink()
        md_path = self.directory / f"{conversation_id}.md"
        if md_path.exists():
            md_path.unlink()

    def export_all(self, format: str = "md") -> str:
        """Export all conversations to a single file."""
        convs = []
        for path in sorted(self.directory.glob("*.json")):
            try:
                convs.append(Conversation.from_json(path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, KeyError):
                continue

        if format == "md":
            parts = [conv.to_markdown() for conv in convs]
            return "\n\n---\n\n".join(parts)
        else:
            return json.dumps([conv.to_dict() for conv in convs], indent=2)
