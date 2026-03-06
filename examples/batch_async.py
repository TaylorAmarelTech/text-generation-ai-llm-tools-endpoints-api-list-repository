#!/usr/bin/env python3
"""Process many prompts in parallel using async HTTP.

Demonstrates efficient batch processing with concurrency control.

Usage:
    python examples/batch_async.py
"""
import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import httpx

PROMPTS = [
    "What is photosynthesis? (1 sentence)",
    "What is gravity? (1 sentence)",
    "What is DNA? (1 sentence)",
    "What is an atom? (1 sentence)",
    "What is evolution? (1 sentence)",
    "What is electricity? (1 sentence)",
    "What is a black hole? (1 sentence)",
    "What is the speed of light? (1 sentence)",
    "What is entropy? (1 sentence)",
    "What is plate tectonics? (1 sentence)",
]


async def complete(
    client: httpx.AsyncClient,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    semaphore: asyncio.Semaphore,
) -> dict:
    async with semaphore:
        start = time.time()
        try:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "prompt": prompt,
                "response": data["choices"][0]["message"]["content"].strip(),
                "latency": time.time() - start,
            }
        except Exception as e:
            return {"prompt": prompt, "error": str(e), "latency": time.time() - start}


async def main():
    base_url = "https://api.groq.com/openai/v1"
    api_key = os.environ.get("GROQ_API_KEY", "")
    model = "llama-3.3-70b-versatile"

    if not api_key:
        print("Error: GROQ_API_KEY not set")
        sys.exit(1)

    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent
    print(f"Processing {len(PROMPTS)} prompts (5 concurrent)...\n")

    start = time.time()
    async with httpx.AsyncClient() as client:
        tasks = [complete(client, base_url, api_key, model, p, semaphore) for p in PROMPTS]
        results = await asyncio.gather(*tasks)

    total = time.time() - start

    for r in results:
        if "error" in r:
            print(f"  [{r['latency']:.2f}s] ERROR: {r['error']}")
        else:
            print(f"  [{r['latency']:.2f}s] Q: {r['prompt']}")
            print(f"           A: {r['response'][:100]}")

    print(f"\nTotal: {total:.2f}s for {len(PROMPTS)} prompts ({len(PROMPTS)/total:.1f} prompts/sec)")


if __name__ == "__main__":
    asyncio.run(main())
