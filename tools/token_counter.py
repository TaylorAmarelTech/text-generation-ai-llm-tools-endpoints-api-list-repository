"""Approximate token counter for LLM cost estimation.

Uses a simple heuristic (words * 1.3) for quick estimates.
For exact counts, use tiktoken (OpenAI) or the provider's tokenizer.

Usage:
    from tools.token_counter import count_tokens, estimate_messages_tokens

    tokens = count_tokens("Hello, world!")  # ~4
    msg_tokens = estimate_messages_tokens([
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hi!"},
    ])
"""

from __future__ import annotations

import re


# Average English token is ~4 characters or ~0.75 words.
# We use a conservative 1.3 tokens/word multiplier.
TOKENS_PER_WORD = 1.3

# Overhead per message in chat format (role, delimiters, etc.)
MESSAGE_OVERHEAD = 4


def count_tokens(text: str) -> int:
    """Estimate token count for a string using word-based heuristic."""
    if not text:
        return 0
    words = len(re.findall(r'\S+', text))
    return max(1, int(words * TOKENS_PER_WORD))


def estimate_messages_tokens(messages: list[dict]) -> int:
    """Estimate tokens for a chat messages list (OpenAI format)."""
    total = 0
    for msg in messages:
        total += MESSAGE_OVERHEAD
        total += count_tokens(msg.get("content", ""))
        total += count_tokens(msg.get("role", ""))
        if msg.get("name"):
            total += count_tokens(msg["name"])
    total += 2  # reply priming
    return total


def tokens_to_cost(
    input_tokens: int,
    output_tokens: int,
    input_price_per_m: float,
    output_price_per_m: float,
) -> float:
    """Calculate cost in dollars given token counts and per-million pricing."""
    return (input_tokens * input_price_per_m + output_tokens * output_price_per_m) / 1_000_000


def format_tokens(count: int) -> str:
    """Format token count with K/M suffix."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)
