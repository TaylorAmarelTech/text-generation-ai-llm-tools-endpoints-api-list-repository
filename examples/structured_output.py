#!/usr/bin/env python3
"""Get structured JSON output and use function calling for data extraction.

Usage:
    python examples/structured_output.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI


def main():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print("Error: GROQ_API_KEY not set")
        sys.exit(1)

    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)

    # --- Example 1: JSON Mode ---
    print("=== JSON Mode ===\n")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Respond in JSON format."},
            {"role": "user", "content": (
                "List the top 5 programming languages with their main use cases. "
                "Return as JSON with key 'languages', each item having: name, use_case, rank"
            )},
        ],
        response_format={"type": "json_object"},
        max_tokens=500,
    )
    data = json.loads(response.choices[0].message.content)
    print(json.dumps(data, indent=2))

    # --- Example 2: Function Calling ---
    print("\n=== Function Calling (Entity Extraction) ===\n")
    tools = [{
        "type": "function",
        "function": {
            "name": "extract_entities",
            "description": "Extract named entities from text",
            "parameters": {
                "type": "object",
                "properties": {
                    "people": {"type": "array", "items": {"type": "string"}},
                    "organizations": {"type": "array", "items": {"type": "string"}},
                    "locations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["people", "organizations", "locations"],
            },
        },
    }]

    text = (
        "On March 15, 2024, Elon Musk announced that SpaceX would launch Starship "
        "from Boca Chica, Texas. NASA Administrator Bill Nelson praised the effort."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Extract entities:\n\n{text}"}],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "extract_entities"}},
    )

    if response.choices[0].message.tool_calls:
        entities = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
        print(f"Text: {text}\n")
        for key, values in entities.items():
            print(f"  {key}: {values}")


if __name__ == "__main__":
    main()
