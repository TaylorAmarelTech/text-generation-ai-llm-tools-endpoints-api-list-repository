#!/usr/bin/env python3
"""Free embeddings from various providers.

Providers with free embedding APIs:
- Google Gemini (text-embedding-004)
- HuggingFace (sentence-transformers models)
- Cohere (embed-english-v3.0, embed-multilingual-v3.0)
- NVIDIA NIM (various embedding models)

Usage:
    python examples/embeddings.py
"""
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


PROVIDERS = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key": "GEMINI_API_KEY",
        "model": "text-embedding-004",
    },
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "key": "NVIDIA_API_KEY",
        "model": "nvidia/nv-embedqa-e5-v5",
    },
}


def main():
    provider = sys.argv[1] if len(sys.argv) > 1 else "gemini"
    cfg = PROVIDERS.get(provider)
    if not cfg:
        print(f"Unknown provider. Available: {list(PROVIDERS.keys())}")
        sys.exit(1)

    api_key = os.environ.get(cfg["key"], "")
    if not api_key:
        print(f"Error: {cfg['key']} not set")
        sys.exit(1)

    client = OpenAI(base_url=cfg["base_url"], api_key=api_key)
    print(f"[{provider}] Using {cfg['model']}\n")

    # Texts to embed
    texts = [
        "The cat sat on the mat.",
        "A kitten was resting on the rug.",
        "The stock market crashed today.",
        "Python is a programming language.",
        "Machine learning uses neural networks.",
    ]

    # Get embeddings
    response = client.embeddings.create(model=cfg["model"], input=texts)
    embeddings = [item.embedding for item in response.data]
    dim = len(embeddings[0])
    print(f"Embedding dimension: {dim}\n")

    # Compute similarity matrix
    print("Similarity Matrix:")
    print(f"{'':30s}", end="")
    for i in range(len(texts)):
        print(f"  [{i}]  ", end="")
    print()

    for i, text_i in enumerate(texts):
        label = text_i[:28] + ".." if len(text_i) > 30 else text_i
        print(f"[{i}] {label:28s}", end="")
        for j in range(len(texts)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            print(f" {sim:.3f}", end=" ")
        print()

    # Find most similar pair (excluding self)
    best_sim = -1
    best_pair = (0, 0)
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim > best_sim:
                best_sim = sim
                best_pair = (i, j)

    print(f"\nMost similar pair (score={best_sim:.3f}):")
    print(f"  [{best_pair[0]}] {texts[best_pair[0]]}")
    print(f"  [{best_pair[1]}] {texts[best_pair[1]]}")


if __name__ == "__main__":
    main()
