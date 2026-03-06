"""ReAct (Reason + Act) agent pattern.

Uses text-based reasoning instead of function calling, making it
compatible with any LLM provider (even those without tool_call support).

The agent follows a loop:
  Thought -> Action -> Observation -> Thought -> ... -> Final Answer
"""
from __future__ import annotations

import json
import re

from .base import BaseAgent, AgentConfig, AGENT_PRESETS


REACT_SYSTEM_PROMPT = """You are a ReAct agent. For each query, follow this loop:

1. **Thought**: Reason about what you need to do next.
2. **Action**: Choose a tool to call, OR give your final answer.
3. **Observation**: Read the tool result (provided by the system).

Format your responses EXACTLY like this when using a tool:

Thought: <your reasoning>
Action: <tool_name>
Action Input: <json arguments>

When you have the final answer:

Thought: <your reasoning>
Final Answer: <your response to the user>

Available tools:
{tool_descriptions}"""


class ReActAgent(BaseAgent):
    """Agent implementing the ReAct (Reason + Act) pattern.

    Works with any LLM provider since it uses text parsing
    instead of requiring native function calling support.
    """

    def __init__(self, config: AgentConfig | str = "groq", verbose: bool = True):
        super().__init__(config)
        self.config.system_prompt = ""  # Built dynamically
        self.verbose = verbose

    def _build_system_prompt(self) -> str:
        tool_descs = []
        for name, tool in self.tools.items():
            params = json.dumps(tool.parameters.get("properties", {}), indent=2)
            tool_descs.append(f"- **{name}**: {tool.description}\n  Parameters: {params}")
        desc_text = "\n".join(tool_descs) if tool_descs else "No tools registered."
        return REACT_SYSTEM_PROMPT.format(tool_descriptions=desc_text)

    def _get_system_message(self) -> dict:
        return {"role": "system", "content": self._build_system_prompt()}

    def _parse_react_response(self, text: str):
        """Parse ReAct-formatted text into components."""
        thought = None
        action = None
        action_input = None
        final_answer = None

        thought_match = re.search(
            r'Thought:\s*(.+?)(?=\n(?:Action|Final Answer)|\Z)', text, re.DOTALL
        )
        if thought_match:
            thought = thought_match.group(1).strip()

        final_match = re.search(r'Final Answer:\s*(.+)', text, re.DOTALL)
        if final_match:
            final_answer = final_match.group(1).strip()
            return thought, None, None, final_answer

        action_match = re.search(r'Action:\s*(.+?)(?:\n|$)', text)
        if action_match:
            action = action_match.group(1).strip()

        input_match = re.search(
            r'Action Input:\s*(.+?)(?:\n(?:Thought|Action|Final Answer)|\Z)',
            text, re.DOTALL,
        )
        if input_match:
            action_input = input_match.group(1).strip()

        return thought, action, action_input, final_answer

    def chat(self, user_message: str) -> str:
        """Run the ReAct loop until Final Answer or max iterations."""
        messages = [
            self._get_system_message(),
            {"role": "user", "content": user_message},
        ]

        for i in range(self.config.max_iterations):
            response = self._call_llm(messages)
            text = response.choices[0].message.content or ""

            thought, action, action_input, final_answer = self._parse_react_response(text)

            if self.verbose:
                if thought:
                    print(f"  [Thought] {thought}")
                if action:
                    print(f"  [Action] {action}({action_input})")

            if final_answer:
                if self.verbose:
                    print(f"  [Answer] {final_answer[:200]}...")
                return final_answer

            if action and action in self.tools:
                try:
                    args = json.loads(action_input) if action_input else {}
                except json.JSONDecodeError:
                    args = {"query": action_input} if action_input else {}

                result = self._execute_tool(action, json.dumps(args))
                if self.verbose:
                    print(f"  [Observation] {result[:200]}...")

                messages.append({"role": "assistant", "content": text})
                messages.append({"role": "user", "content": f"Observation: {result}"})
            else:
                return text

        return "Max iterations reached. Could not determine a final answer."
