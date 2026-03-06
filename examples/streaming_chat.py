#!/usr/bin/env python3
"""Streaming chat with real-time token output and performance stats.

Usage:
    python examples/streaming_chat.py
    python examples/streaming_chat.py --provider gemini --prompt "Tell me a story"
"""
import argparse
import os
import sys
import time

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
    parser.add_argument("--prompt", default="Write a short poem about programming.")
    args = parser.parse_args()

    cfg = PROVIDERS[args.provider]
    api_key = os.environ.get(cfg["key"], "")
    if not api_key:
        print(f"Error: {cfg['key']} not set")
        sys.exit(1)

    client = OpenAI(base_url=cfg["base_url"], api_key=api_key)
    print(f"[{args.provider}] Streaming from {cfg['model']}...\n")

    start = time.time()
    ttft = None
    chunks = 0

    stream = client.chat.completions.create(
        model=cfg["model"],
        messages=[{"role": "user", "content": args.prompt}],
        max_tokens=500,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            if ttft is None:
                ttft = time.time() - start
            chunks += 1
            print(delta, end="", flush=True)

    elapsed = time.time() - start
    print(f"\n\n--- Stats ---")
    print(f"TTFT: {(ttft or 0)*1000:.0f}ms | Total: {elapsed:.2f}s | {chunks} chunks | ~{chunks/elapsed:.0f} chunks/s")


if __name__ == "__main__":
    main()
