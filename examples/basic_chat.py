#!/usr/bin/env python3
"""Basic chat with any free LLM provider.

Usage:
    python examples/basic_chat.py
    python examples/basic_chat.py --provider cerebras
    python examples/basic_chat.py --provider gemini --prompt "Write a haiku"
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

PROVIDERS = {
    "groq":       {"base_url": "https://api.groq.com/openai/v1",       "key": "GROQ_API_KEY",       "model": "llama-3.3-70b-versatile"},
    "gemini":     {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key": "GEMINI_API_KEY", "model": "gemini-2.0-flash"},
    "cerebras":   {"base_url": "https://api.cerebras.ai/v1",           "key": "CEREBRAS_API_KEY",   "model": "llama-3.3-70b"},
    "mistral":    {"base_url": "https://api.mistral.ai/v1",            "key": "MISTRAL_API_KEY",    "model": "mistral-small-latest"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1",         "key": "OPENROUTER_API_KEY", "model": "deepseek/deepseek-r1:free"},
    "github":     {"base_url": "https://models.inference.ai.azure.com","key": "GITHUB_TOKEN",       "model": "gpt-4o"},
    "sambanova":  {"base_url": "https://api.sambanova.ai/v1",          "key": "SAMBANOVA_API_KEY",  "model": "Meta-Llama-3.3-70B-Instruct"},
}


def main():
    parser = argparse.ArgumentParser(description="Chat with a free LLM provider")
    parser.add_argument("--provider", "-p", default="groq", choices=PROVIDERS.keys())
    parser.add_argument("--prompt", default="Explain quantum computing in 3 sentences.")
    parser.add_argument("--max-tokens", type=int, default=500)
    args = parser.parse_args()

    cfg = PROVIDERS[args.provider]
    api_key = os.environ.get(cfg["key"], "")
    if not api_key:
        print(f"Error: {cfg['key']} not set in .env")
        sys.exit(1)

    client = OpenAI(base_url=cfg["base_url"], api_key=api_key)
    print(f"[{args.provider}] {cfg['model']}")
    print("-" * 40)

    response = client.chat.completions.create(
        model=cfg["model"],
        messages=[{"role": "user", "content": args.prompt}],
        max_tokens=args.max_tokens,
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
