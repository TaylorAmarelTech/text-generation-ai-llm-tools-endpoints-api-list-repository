#!/usr/bin/env python3
"""One-liner examples for every free LLM provider.

Each function is a complete, self-contained call to a single provider.
Copy-paste any one of these into your code to get started instantly.

Usage:
    python examples/oneliners.py groq
    python examples/oneliners.py gemini
    python examples/oneliners.py all
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI


def ask(base_url: str, api_key: str, model: str, prompt: str = "Say hello in one sentence.") -> str:
    """Universal one-liner helper."""
    return OpenAI(base_url=base_url, api_key=api_key).chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}], max_tokens=100
    ).choices[0].message.content


# --- Provider one-liners ---

PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
        "free": "~1K RPD for 70B",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GEMINI_API_KEY",
        "model": "gemini-2.0-flash",
        "free": "500 RPD",
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "key_env": "CEREBRAS_API_KEY",
        "model": "llama-3.3-70b",
        "free": "1M tokens/day",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "key_env": "MISTRAL_API_KEY",
        "model": "mistral-small-latest",
        "free": "1B tokens/mo",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "model": "deepseek/deepseek-r1:free",
        "free": "28+ free models, 200 RPD",
    },
    "github": {
        "base_url": "https://models.inference.ai.azure.com",
        "key_env": "GITHUB_TOKEN",
        "model": "gpt-4o",
        "free": "50-150 RPD",
    },
    "huggingface": {
        "base_url": "https://router.huggingface.co/v1",
        "key_env": "HUGGINGFACE_API_KEY",
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "free": "~300 req/hr",
    },
    "sambanova": {
        "base_url": "https://api.sambanova.ai/v1",
        "key_env": "SAMBANOVA_API_KEY",
        "model": "Meta-Llama-3.3-70B-Instruct",
        "free": "$5 credits",
    },
    "cohere": {
        "base_url": "https://api.cohere.com/v2",
        "key_env": "COHERE_API_KEY",
        "model": "command-r",
        "free": "1K calls/mo",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat",
        "free": "5M tokens",
    },
    "xai": {
        "base_url": "https://api.x.ai/v1",
        "key_env": "XAI_API_KEY",
        "model": "grok-3-mini",
        "free": "$25 credits",
    },
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "key_env": "NVIDIA_API_KEY",
        "model": "meta/llama-3.3-70b-instruct",
        "free": "1K-5K credits",
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "key_env": "TOGETHER_API_KEY",
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "free": "$5 credits",
    },
    "deepinfra": {
        "base_url": "https://api.deepinfra.com/v1/openai",
        "key_env": "DEEPINFRA_API_KEY",
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "free": "$5 credits",
    },
    "fireworks": {
        "base_url": "https://api.fireworks.ai/inference/v1",
        "key_env": "FIREWORKS_API_KEY",
        "model": "accounts/fireworks/models/llama-v3p3-70b-instruct",
        "free": "$1 credits",
    },
    "reka": {
        "base_url": "https://api.reka.ai/v1",
        "key_env": "REKA_API_KEY",
        "model": "reka-flash",
        "free": "$10/mo credits",
    },
}


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "help"
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Explain quantum computing in one sentence."

    if target == "help":
        print("Usage: python examples/oneliners.py <provider|all|list> [prompt]")
        print(f"\nAvailable: {', '.join(PROVIDERS.keys())}")
        return

    if target == "list":
        for name, cfg in PROVIDERS.items():
            key = os.environ.get(cfg["key_env"], "")
            status = "ready" if key else "no key"
            print(f"  {name:<14} {cfg['model']:<45} {cfg['free']:<20} [{status}]")
        return

    targets = PROVIDERS.keys() if target == "all" else [target]

    for name in targets:
        if name not in PROVIDERS:
            print(f"Unknown provider: {name}")
            continue
        cfg = PROVIDERS[name]
        api_key = os.environ.get(cfg["key_env"], "")
        if not api_key:
            print(f"[{name}] Skipped -- {cfg['key_env']} not set")
            continue
        try:
            result = ask(cfg["base_url"], api_key, cfg["model"], prompt)
            print(f"[{name}] {result}")
        except Exception as e:
            print(f"[{name}] Error: {e}")


if __name__ == "__main__":
    main()
