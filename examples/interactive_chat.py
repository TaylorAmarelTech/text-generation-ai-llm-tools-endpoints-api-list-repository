#!/usr/bin/env python3
"""Interactive multi-turn chat with conversation history.

Usage:
    python examples/interactive_chat.py
    python examples/interactive_chat.py --provider gemini
    python examples/interactive_chat.py --system "You are a pirate."
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

PROVIDERS = {
    "groq":     {"base_url": "https://api.groq.com/openai/v1",       "key": "GROQ_API_KEY",     "model": "llama-3.3-70b-versatile"},
    "gemini":   {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key": "GEMINI_API_KEY", "model": "gemini-2.0-flash"},
    "cerebras": {"base_url": "https://api.cerebras.ai/v1",           "key": "CEREBRAS_API_KEY", "model": "llama-3.3-70b"},
    "mistral":  {"base_url": "https://api.mistral.ai/v1",            "key": "MISTRAL_API_KEY",  "model": "mistral-small-latest"},
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", "-p", default="groq", choices=PROVIDERS.keys())
    parser.add_argument("--system", "-s", default="You are a helpful assistant.")
    args = parser.parse_args()

    cfg = PROVIDERS[args.provider]
    api_key = os.environ.get(cfg["key"], "")
    if not api_key:
        print(f"Error: {cfg['key']} not set")
        sys.exit(1)

    client = OpenAI(base_url=cfg["base_url"], api_key=api_key)
    messages = [{"role": "system", "content": args.system}]

    print(f"Chat with {args.provider} ({cfg['model']})")
    print("Commands: /clear, /system <msg>, quit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "/q"):
            break
        if user_input == "/clear":
            messages = [messages[0]]
            print("[History cleared]\n")
            continue
        if user_input.startswith("/system "):
            messages[0]["content"] = user_input[8:]
            print("[System prompt updated]\n")
            continue

        messages.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model=cfg["model"],
            messages=messages,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print(f"\nAssistant: {reply}\n")


if __name__ == "__main__":
    main()
