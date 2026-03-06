#!/usr/bin/env python3
"""Simple RAG (Retrieval-Augmented Generation) pipeline.

Uses a local TF-IDF vector store (no external deps) and any free LLM.

Usage:
    python examples/rag_pipeline.py
    python examples/rag_pipeline.py --query "Which provider is fastest?"
"""
import argparse
import math
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI


def tokenize(text: str) -> list[str]:
    return re.findall(r'\b\w+\b', text.lower())


class SimpleVectorStore:
    """Minimal TF-IDF retriever. Zero external dependencies."""

    def __init__(self):
        self.documents: list[str] = []
        self.doc_tokens: list[list[str]] = []
        self.idf: dict[str, float] = {}

    def add_documents(self, docs: list[str]):
        self.documents.extend(docs)
        self.doc_tokens = [tokenize(d) for d in self.documents]
        n = len(self.documents)
        df: Counter = Counter()
        for tokens in self.doc_tokens:
            df.update(set(tokens))
        self.idf = {word: math.log(n / (count + 1)) for word, count in df.items()}

    def _tfidf(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        total = len(tokens) or 1
        return {w: (c / total) * self.idf.get(w, 0) for w, c in tf.items()}

    def _cosine_sim(self, a: dict, b: dict) -> float:
        keys = set(a) & set(b)
        dot = sum(a[k] * b[k] for k in keys)
        mag_a = math.sqrt(sum(v**2 for v in a.values())) or 1
        mag_b = math.sqrt(sum(v**2 for v in b.values())) or 1
        return dot / (mag_a * mag_b)

    def search(self, query: str, top_k: int = 3) -> list[tuple[str, float]]:
        q_vec = self._tfidf(tokenize(query))
        scores = []
        for i, tokens in enumerate(self.doc_tokens):
            d_vec = self._tfidf(tokens)
            scores.append((self.documents[i], self._cosine_sim(q_vec, d_vec)))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# Sample knowledge base about LLM providers
DOCUMENTS = [
    "Groq uses custom LPU hardware for extremely fast inference. Free tier: ~1000 RPD for 70B models.",
    "Google Gemini offers 250 RPD Flash, 100 RPD Pro. Supports OpenAI SDK compatibility layer.",
    "Cerebras uses wafer-scale chips. Free tier: 1M tokens/day, 8K context. Very fast throughput.",
    "OpenRouter aggregates 100+ models. 25+ permanently free variants at 50 RPD each.",
    "Mistral AI is French, offering 1B tokens/month/model free. Excellent multilingual support.",
    "DeepSeek has the cheapest frontier model: $0.014/M for cache hits. V3 is 685B MoE.",
    "The OpenAI SDK is the standard. Most providers offer compatible endpoints -- just swap base_url.",
    "SambaNova uses custom RDU hardware. Offers $5 credits + free tier for 3 months.",
    "HuggingFace Inference API: ~300 req/hr, thousands of models, free serverless endpoints.",
    "Cloudflare Workers AI runs at the edge. 10K neurons/day free. Needs account ID + token.",
]


PROVIDERS = {
    "groq":   {"base_url": "https://api.groq.com/openai/v1",       "key": "GROQ_API_KEY",     "model": "llama-3.3-70b-versatile"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key": "GEMINI_API_KEY", "model": "gemini-2.0-flash"},
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", "-p", default="groq", choices=PROVIDERS.keys())
    parser.add_argument("--query", "-q", default="Which provider is the fastest and how does it work?")
    args = parser.parse_args()

    cfg = PROVIDERS[args.provider]
    api_key = os.environ.get(cfg["key"], "")
    if not api_key:
        print(f"Error: {cfg['key']} not set")
        sys.exit(1)

    # Build index
    store = SimpleVectorStore()
    store.add_documents(DOCUMENTS)
    print(f"Indexed {len(DOCUMENTS)} documents\n")

    # Retrieve
    results = store.search(args.query, top_k=3)
    print(f"Query: {args.query}\n")
    print("Retrieved context:")
    for i, (doc, score) in enumerate(results, 1):
        print(f"  {i}. [{score:.3f}] {doc[:80]}...")

    # Generate with context
    context = "\n\n".join(doc for doc, _ in results)
    prompt = (
        f"Answer using ONLY the provided context. Cite specific facts.\n\n"
        f"Context:\n{context}\n\nQuestion: {args.query}\n\nAnswer:"
    )

    client = OpenAI(base_url=cfg["base_url"], api_key=api_key)
    response = client.chat.completions.create(
        model=cfg["model"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3,
    )
    print(f"\n{'='*60}")
    print(f"[{args.provider}] RAG Response:")
    print(f"{'='*60}")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
