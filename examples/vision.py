#!/usr/bin/env python3
"""Multimodal/vision example using providers that support image input.

Providers with free vision support:
- Gemini (gemini-2.0-flash) - 250 RPD free
- GitHub Models (gpt-4o) - 50-150 RPD free
- OpenRouter (free vision models)

Usage:
    python examples/vision.py --url "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
    python examples/vision.py --provider github --url "https://example.com/image.jpg"
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

PROVIDERS = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key": "GEMINI_API_KEY",
        "model": "gemini-2.0-flash",
    },
    "github": {
        "base_url": "https://models.inference.ai.azure.com",
        "key": "GITHUB_TOKEN",
        "model": "gpt-4o",
    },
}


def main():
    parser = argparse.ArgumentParser(description="Analyze images with free vision models")
    parser.add_argument("--provider", "-p", default="gemini", choices=PROVIDERS.keys())
    parser.add_argument("--url", required=True, help="Image URL to analyze")
    parser.add_argument("--prompt", default="Describe this image in detail.")
    args = parser.parse_args()

    cfg = PROVIDERS[args.provider]
    api_key = os.environ.get(cfg["key"], "")
    if not api_key:
        print(f"Error: {cfg['key']} not set in .env")
        sys.exit(1)

    client = OpenAI(base_url=cfg["base_url"], api_key=api_key)
    print(f"[{args.provider}] Analyzing image with {cfg['model']}...\n")

    response = client.chat.completions.create(
        model=cfg["model"],
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": args.prompt},
                {"type": "image_url", "image_url": {"url": args.url}},
            ],
        }],
        max_tokens=500,
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
