"""Document and text summarization agent.

Handles long texts by chunking them and summarizing each chunk,
then producing a final consolidated summary.
"""
from __future__ import annotations

from .base import BaseAgent, AgentConfig


SUMMARIZER_SYSTEM_PROMPT = """You are an expert summarizer. Your summaries are:
- Concise but comprehensive (capture all key points)
- Well-structured with clear organization
- Faithful to the source (no invented information)
- Written in clear, accessible language

When summarizing long content that has been split into chunks,
synthesize across all chunks into a coherent unified summary."""


class SummarizerAgent(BaseAgent):
    """Agent for summarizing documents, articles, and long text.

    Handles long texts by chunking and hierarchical summarization.

    Usage:
        agent = SummarizerAgent("groq")
        summary = agent.summarize(long_text)
        bullets = agent.summarize(long_text, style="bullets")
        brief = agent.summarize(long_text, max_words=50)
    """

    def __init__(self, config: AgentConfig | str = "groq", chunk_size: int = 3000):
        super().__init__(config)
        self.config.system_prompt = SUMMARIZER_SYSTEM_PROMPT
        self.config.temperature = 0.3
        self.chunk_size = chunk_size

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into chunks, trying to break at paragraph boundaries."""
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        while text:
            if len(text) <= self.chunk_size:
                chunks.append(text)
                break
            # Try to break at a paragraph boundary
            break_point = text.rfind("\n\n", 0, self.chunk_size)
            if break_point == -1:
                break_point = text.rfind(". ", 0, self.chunk_size)
            if break_point == -1:
                break_point = self.chunk_size
            else:
                break_point += 2
            chunks.append(text[:break_point].strip())
            text = text[break_point:].strip()
        return chunks

    def summarize(
        self,
        text: str,
        style: str = "paragraph",
        max_words: int | None = None,
        focus: str = "",
    ) -> str:
        """Summarize text with configurable style and length.

        Args:
            text: The text to summarize
            style: "paragraph", "bullets", "tldr", or "executive"
            max_words: Optional word limit for the summary
            focus: Optional focus area (e.g., "technical details", "key decisions")
        """
        chunks = self._chunk_text(text)

        style_instructions = {
            "paragraph": "Write a clear paragraph summary.",
            "bullets": "Summarize as a bullet-point list of key points.",
            "tldr": "Write a single-sentence TL;DR.",
            "executive": "Write an executive summary with: Overview, Key Points, and Conclusions.",
        }
        style_text = style_instructions.get(style, style_instructions["paragraph"])

        if len(chunks) == 1:
            # Single chunk - direct summary
            prompt = f"{style_text}"
            if max_words:
                prompt += f" Keep it under {max_words} words."
            if focus:
                prompt += f" Focus on: {focus}"
            prompt += f"\n\nText to summarize:\n\n{chunks[0]}"
            self.reset()
            return self.chat(prompt)

        # Multiple chunks - hierarchical summarization
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            self.reset()
            prompt = f"Summarize this text (part {i+1}/{len(chunks)}):\n\n{chunk}"
            chunk_summaries.append(self.chat(prompt))

        # Final consolidation
        self.reset()
        combined = "\n\n---\n\n".join(
            f"Part {i+1} summary:\n{s}" for i, s in enumerate(chunk_summaries)
        )
        prompt = (
            f"These are summaries of different parts of a document. "
            f"Synthesize them into one unified summary.\n\n{style_text}"
        )
        if max_words:
            prompt += f" Keep it under {max_words} words."
        if focus:
            prompt += f" Focus on: {focus}"
        prompt += f"\n\n{combined}"
        return self.chat(prompt)

    def compare(self, text1: str, text2: str) -> str:
        """Compare two texts and summarize their similarities and differences."""
        self.reset()
        return self.chat(
            f"Compare these two texts. Highlight key similarities and differences.\n\n"
            f"--- Text 1 ---\n{text1[:2000]}\n\n--- Text 2 ---\n{text2[:2000]}"
        )
