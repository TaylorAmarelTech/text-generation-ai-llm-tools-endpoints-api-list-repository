"""Code generation, review, and debugging agent.

Specialized agent with a system prompt tuned for software engineering tasks.
Uses lower temperature for more deterministic code output.
"""
from __future__ import annotations

from .base import BaseAgent, AgentConfig


CODE_SYSTEM_PROMPT = """You are an expert software engineer. You help users with:
- Writing clean, efficient, well-structured code
- Reviewing and improving existing code
- Debugging issues and explaining errors
- Explaining code and architectural concepts
- Suggesting best practices and design patterns

When writing code:
- Use clear variable names
- Follow language conventions and idioms
- Include error handling where appropriate
- Keep it simple and readable

When reviewing code:
- Point out bugs, security issues, and performance problems
- Suggest specific improvements with code examples
- Explain the reasoning behind suggestions"""


class CodeAgent(BaseAgent):
    """Agent specialized for code generation, review, and debugging.

    Usage:
        agent = CodeAgent("groq", language="python")
        code = agent.generate("a function that finds prime numbers up to N")
        review = agent.review("def foo(x): return x+1")
    """

    def __init__(self, config: AgentConfig | str = "groq", language: str = "python"):
        super().__init__(config)
        self.language = language
        self.config.system_prompt = CODE_SYSTEM_PROMPT
        self.config.temperature = 0.3  # More deterministic for code

    def generate(self, description: str) -> str:
        """Generate code from a natural language description."""
        return self.chat(
            f"Write {self.language} code for the following:\n\n{description}"
        )

    def review(self, code: str) -> str:
        """Review code and suggest improvements."""
        return self.chat(
            f"Review this {self.language} code and suggest improvements:\n\n"
            f"```{self.language}\n{code}\n```"
        )

    def debug(self, code: str, error: str) -> str:
        """Debug code given an error message."""
        return self.chat(
            f"Debug this {self.language} code. The error is: {error}\n\n"
            f"```{self.language}\n{code}\n```"
        )

    def explain(self, code: str) -> str:
        """Explain what code does step by step."""
        return self.chat(
            f"Explain this {self.language} code step by step:\n\n"
            f"```{self.language}\n{code}\n```"
        )
