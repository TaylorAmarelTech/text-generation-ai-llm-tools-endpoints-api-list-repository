#!/usr/bin/env python3
"""Compare responses from multiple providers side-by-side in parallel.

Usage:
    python examples/multi_provider.py
    python examples/multi_provider.py "What is consciousness?"
"""
import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import httpx

PROVIDERS = [
    {"name": "Groq",     "base_url": "https://api.groq.com/openai/v1",       "key": "GROQ_API_KEY",     "model": "llama-3.3-70b-versatile"},
    {"name": "Cerebras", "base_url": "https://api.cerebras.ai/v1",           "key": "CEREBRAS_API_KEY", "model": "llama-3.3-70b"},
    {"name": "Mistral",  "base_url": "https://api.mistral.ai/v1",            "key": "MISTRAL_API_KEY",  "model": "mistral-small-latest"},
    {"name": "Gemini",   "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key": "GEMINI_API_KEY", "model": "gemini-2.0-flash"},
]


async def query_provider(provider: dict, prompt: str) -> dict:
    api_key = os.environ.get(provider["key"], "")
    if not api_key:
        return {"name": provider["name"], "error": f"{provider['key']} not set", "latency": 0}

    start = time.time()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{provider['base_url']}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": provider["model"],
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "name": provider["name"],
                "model": provider["model"],
                "response": data["choices"][0]["message"]["content"],
                "latency": time.time() - start,
            }
        except Exception as e:
            return {"name": provider["name"], "error": str(e), "latency": time.time() - start}


async def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else "In one paragraph, what makes a great software engineer?"
    print(f"Prompt: {prompt}\n")
    print("Querying providers in parallel...\n")

    results = await asyncio.gather(*[query_provider(p, prompt) for p in PROVIDERS])

    for r in sorted(results, key=lambda x: x.get("latency", 999)):
        name = r["name"]
        if "error" in r:
            print(f"{'='*60}\n[{name}] ERROR: {r['error']}\n")
        else:
            print(f"{'='*60}")
            print(f"[{name}] {r.get('model', '')} ({r['latency']:.2f}s)")
            print(f"{'-'*60}")
            print(r["response"])
            print()


if __name__ == "__main__":
    asyncio.run(main())
