#!/usr/bin/env python3
"""Interactive agent with tool use (function calling).

Demonstrates calculator, weather, and unit conversion tools.

Usage:
    python examples/agent_tool_use.py
    python examples/agent_tool_use.py --provider gemini
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from agents import BaseAgent


def calculator(expression: str) -> str:
    """Safely evaluate a math expression."""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "Error: Invalid characters"
    try:
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def get_weather(city: str) -> str:
    """Simulated weather lookup."""
    data = {
        "new york": "72F, Partly Cloudy",
        "london": "58F, Rainy",
        "tokyo": "68F, Clear",
        "paris": "64F, Overcast",
        "sydney": "80F, Sunny",
    }
    return data.get(city.lower(), f"Weather data not available for {city}")


def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units."""
    conversions = {
        ("km", "miles"): 0.621371,
        ("miles", "km"): 1.60934,
        ("kg", "lbs"): 2.20462,
        ("lbs", "kg"): 0.453592,
        ("celsius", "fahrenheit"): lambda v: v * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda v: (v - 32) * 5/9,
        ("meters", "feet"): 3.28084,
        ("feet", "meters"): 0.3048,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        factor = conversions[key]
        result = factor(value) if callable(factor) else value * factor
        return f"{value} {from_unit} = {result:.4f} {to_unit}"
    return f"Cannot convert {from_unit} to {to_unit}"


def main():
    provider = sys.argv[1] if len(sys.argv) > 1 else "groq"
    agent = BaseAgent(provider)
    agent.config.system_prompt = (
        "You are a helpful assistant with tools. Use them when needed."
    )

    agent.register_tool("calculator", "Evaluate a math expression", {
        "type": "object",
        "properties": {"expression": {"type": "string", "description": "Math expression (e.g. '2+2*3')"}},
        "required": ["expression"],
    }, calculator)

    agent.register_tool("get_weather", "Get current weather for a city", {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name"}},
        "required": ["city"],
    }, get_weather)

    agent.register_tool("unit_convert", "Convert between units", {
        "type": "object",
        "properties": {
            "value": {"type": "number"},
            "from_unit": {"type": "string"},
            "to_unit": {"type": "string"},
        },
        "required": ["value", "from_unit", "to_unit"],
    }, unit_convert)

    print(f"Agent ready ({agent.config.provider_name} / {agent.config.model})")
    print("Tools: calculator, get_weather, unit_convert")
    print("Type 'quit' to exit\n")

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not query or query.lower() in ("quit", "exit", "q"):
            break
        response = agent.chat(query)
        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    main()
