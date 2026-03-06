"""Base agent framework for LLM-powered agents.

Provides a BaseAgent class with:
- Tool/function registration and dispatch
- Conversation history management
- Automatic tool calling loop
- Presets for 8 free LLM providers
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable

from openai import OpenAI


@dataclass
class Tool:
    """A callable tool that the agent can use."""
    name: str
    description: str
    parameters: dict
    function: Callable

    def to_openai_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class AgentConfig:
    """Configuration for an agent's LLM backend."""
    provider_name: str = "Groq"
    base_url: str = "https://api.groq.com/openai/v1"
    api_key_env: str = "GROQ_API_KEY"
    model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 1024
    temperature: float = 0.7
    max_iterations: int = 10
    system_prompt: str = "You are a helpful AI assistant."


# Presets for popular free providers
AGENT_PRESETS: dict[str, AgentConfig] = {
    "groq": AgentConfig(
        provider_name="Groq",
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        model="llama-3.3-70b-versatile",
    ),
    "gemini": AgentConfig(
        provider_name="Gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key_env="GEMINI_API_KEY",
        model="gemini-2.0-flash",
    ),
    "cerebras": AgentConfig(
        provider_name="Cerebras",
        base_url="https://api.cerebras.ai/v1",
        api_key_env="CEREBRAS_API_KEY",
        model="llama-3.3-70b",
    ),
    "openrouter": AgentConfig(
        provider_name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        model="deepseek/deepseek-r1:free",
    ),
    "mistral": AgentConfig(
        provider_name="Mistral",
        base_url="https://api.mistral.ai/v1",
        api_key_env="MISTRAL_API_KEY",
        model="mistral-small-latest",
    ),
    "github": AgentConfig(
        provider_name="GitHub Models",
        base_url="https://models.inference.ai.azure.com",
        api_key_env="GITHUB_TOKEN",
        model="gpt-4o",
    ),
    "sambanova": AgentConfig(
        provider_name="SambaNova",
        base_url="https://api.sambanova.ai/v1",
        api_key_env="SAMBANOVA_API_KEY",
        model="Meta-Llama-3.3-70B-Instruct",
    ),
    "huggingface": AgentConfig(
        provider_name="HuggingFace",
        base_url="https://router.huggingface.co/v1",
        api_key_env="HUGGINGFACE_API_KEY",
        model="Qwen/Qwen2.5-72B-Instruct",
    ),
}


class BaseAgent:
    """Base class for LLM-powered agents with tool use.

    Usage:
        agent = BaseAgent("groq")  # or pass an AgentConfig
        agent.register_tool("my_tool", "Does something", {...}, my_func)
        response = agent.chat("Hello!")
    """

    def __init__(self, config: AgentConfig | str = "groq"):
        if isinstance(config, str):
            config = AGENT_PRESETS.get(config, AGENT_PRESETS["groq"])
        self.config = config
        self.tools: dict[str, Tool] = {}
        self.messages: list[dict] = []
        self.client = OpenAI(
            base_url=config.base_url,
            api_key=os.environ.get(config.api_key_env, ""),
        )

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: dict,
        function: Callable,
    ):
        """Register a tool the agent can call."""
        self.tools[name] = Tool(
            name=name,
            description=description,
            parameters=parameters,
            function=function,
        )

    def reset(self):
        """Clear conversation history."""
        self.messages = []

    def _get_system_message(self) -> dict:
        return {"role": "system", "content": self.config.system_prompt}

    def _call_llm(self, messages: list[dict], tools: list[dict] | None = None) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        return self.client.chat.completions.create(**kwargs)

    def _execute_tool(self, name: str, arguments: str) -> str:
        """Execute a registered tool by name."""
        tool = self.tools.get(name)
        if not tool:
            return f"Error: Unknown tool '{name}'"
        try:
            args = json.loads(arguments) if arguments else {}
            result = tool.function(**args)
            return str(result)
        except Exception as e:
            return f"Error executing {name}: {e}"

    def chat(self, user_message: str) -> str:
        """Send a message and get a response, automatically handling tool calls."""
        self.messages.append({"role": "user", "content": user_message})

        all_messages = [self._get_system_message()] + self.messages
        openai_tools = [t.to_openai_tool() for t in self.tools.values()] if self.tools else None

        for _ in range(self.config.max_iterations):
            response = self._call_llm(all_messages, openai_tools)
            choice = response.choices[0]
            message = choice.message

            if not message.tool_calls:
                content = message.content or ""
                self.messages.append({"role": "assistant", "content": content})
                return content

            # Handle tool calls
            all_messages.append(message.model_dump())
            for tool_call in message.tool_calls:
                result = self._execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments,
                )
                all_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        return "Max iterations reached without a final response."
