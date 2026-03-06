#!/usr/bin/env python3
"""Full research agent demo with web search integration.

Demonstrates the ResearchAgent using search tools to answer questions.
Requires at least one search API key (BRAVE_API_KEY, SERPER_API_KEY, or GOOGLE_API_KEY).

Usage:
    python examples/research_demo.py "What are the latest AI developments?"
    python examples/research_demo.py --provider gemini "Compare React vs Vue in 2026"
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from agents import ResearchAgent
from search import get_available_search


def main():
    parser = argparse.ArgumentParser(description="Research agent with web search")
    parser.add_argument("query", nargs="?", default="What are the most popular free LLM APIs in 2026?")
    parser.add_argument("--provider", "-p", default="groq")
    args = parser.parse_args()

    # Check for search provider
    search = get_available_search()
    if not search:
        print("No search provider configured.")
        print("Set one of: BRAVE_API_KEY, SERPER_API_KEY, or GOOGLE_API_KEY + GOOGLE_CSE_ID")
        print("\nRunning without search (agent will use its training knowledge only)...\n")

    # Create agent
    agent = ResearchAgent(args.provider, search_provider=search)
    print(f"Research Agent ({agent.config.provider_name} / {agent.config.model})")
    if search:
        print(f"Search: {search}")
    print(f"\nQuery: {args.query}\n")
    print("Researching...\n")

    # Run research
    answer = agent.chat(args.query)

    print("=" * 60)
    print("RESEARCH RESULTS")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()
