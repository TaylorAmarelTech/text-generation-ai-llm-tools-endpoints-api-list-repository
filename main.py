#!/usr/bin/env python3
"""
LLM Endpoint Scanner, Discovery Engine & Report Generator

Usage:
    python main.py scan                        # Test all endpoints
    python main.py scan --tier free            # Test only free tier
    python main.py scan --report               # Scan + regenerate README
    python main.py report                      # Generate README from last scan
    python main.py list                        # List all providers
    python main.py discover                    # AI-powered endpoint discovery
    python main.py discover --strategy web_search  # Specific strategy
    python main.py benchmark                   # Benchmark working providers
    python main.py models                      # Fetch model catalogs
    python main.py export --format json        # Export to JSON/CSV/YAML/HTML
    python main.py compare "prompt"            # Compare providers side-by-side
    python main.py costs                       # Compare pricing across providers
    python main.py tokens "text"               # Estimate token count for text
    python main.py proxy                       # Start local proxy server
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Rich is optional for pretty terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from config import load_config, Config
from providers import Provider, Tier, PROVIDERS, get_unique_providers, get_providers_by_tier
from scanner import ScanResult, scan_all, scan_provider
from report_generator import generate_readme

RESULTS_FILE = Path(__file__).parent / "scan_results.json"


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def _serialize_results(results: list[ScanResult]) -> list[dict]:
    return [
        {
            "provider_name": r.provider_name,
            "status": r.status,
            "latency_ms": r.latency_ms,
            "error_detail": r.error_detail,
            "model_used": r.model_used,
            "response_preview": r.response_preview,
        }
        for r in results
    ]


def _deserialize_results(data: list[dict]) -> list[ScanResult]:
    return [ScanResult(**d) for d in data]


def _save_results(results: list[ScanResult], timestamp: str) -> None:
    payload = {"timestamp": timestamp, "results": _serialize_results(results)}
    RESULTS_FILE.write_text(json.dumps(payload, indent=2))


def _load_results() -> tuple[list[ScanResult], str] | None:
    if not RESULTS_FILE.exists():
        return None
    data = json.loads(RESULTS_FILE.read_text())
    return _deserialize_results(data["results"]), data["timestamp"]


# ---------------------------------------------------------------------------
# CLI output helpers
# ---------------------------------------------------------------------------

STATUS_ICONS = {
    "working": "[green]OK[/]",
    "reachable": "[yellow]REACH[/]",
    "auth_missing": "[blue]NO KEY[/]",
    "auth_failed": "[red]AUTH FAIL[/]",
    "needs_credits": "[magenta]NO CREDITS[/]",
    "rate_limited": "[yellow]RATE LIM[/]",
    "timeout": "[red]TIMEOUT[/]",
    "error": "[red]ERROR[/]",
    "offline": "[dim]OFFLINE[/]",
    "skipped": "[dim]SKIP[/]",
    "unknown": "[dim]???[/]",
}


def _print_results_rich(results: list[ScanResult], providers: list[Provider]) -> None:
    console = Console()
    tier_order = [Tier.FREE, Tier.GENEROUS_FREE, Tier.FREE_CREDITS, Tier.FREEMIUM, Tier.PAYG, Tier.ROUTER, Tier.LOCAL]
    results_by_name = {r.provider_name: r for r in results}

    for tier in tier_order:
        tier_providers = [p for p in providers if p.tier == tier]
        tier_results = [results_by_name[p.name] for p in tier_providers if p.name in results_by_name]
        if not tier_results:
            continue

        table = Table(title=f"\n{tier.label}", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=3)
        table.add_column("Provider", min_width=18)
        table.add_column("Status", min_width=12)
        table.add_column("Latency", justify="right", min_width=8)
        table.add_column("Model", min_width=20)
        table.add_column("Response Preview", max_width=40)

        for i, r in enumerate(tier_results, 1):
            status = STATUS_ICONS.get(r.status, r.status)
            latency = f"{r.latency_ms:.0f}ms" if r.latency_ms else "-"
            model = r.model_used or "-"
            preview = r.response_preview[:40] if r.response_preview else (r.error_detail[:40] if r.error_detail else "-")
            table.add_row(str(i), r.provider_name, status, latency, model, preview)

        console.print(table)

    working = sum(1 for r in results if r.status == "working")
    console.print(f"\n[bold]Summary:[/] {working}/{len(results)} endpoints working")


def _print_results_plain(results: list[ScanResult]) -> None:
    print(f"\n{'Provider':<25} {'Status':<15} {'Latency':<10} {'Model':<30} {'Detail'}")
    print("-" * 110)
    for r in results:
        latency = f"{r.latency_ms:.0f}ms" if r.latency_ms else "-"
        detail = r.response_preview[:30] or r.error_detail[:30] or "-"
        print(f"{r.provider_name:<25} {r.status:<15} {latency:<10} {r.model_used or '-':<30} {detail}")
    working = sum(1 for r in results if r.status == "working")
    print(f"\nSummary: {working}/{len(results)} endpoints working")


def _print_list_rich(providers: list[Provider]) -> None:
    console = Console()
    tier_order = [Tier.FREE, Tier.GENEROUS_FREE, Tier.FREE_CREDITS, Tier.FREEMIUM, Tier.PAYG, Tier.ROUTER, Tier.LOCAL]

    for tier in tier_order:
        tier_providers = [p for p in providers if p.tier == tier]
        if not tier_providers:
            continue

        table = Table(title=f"\n{tier.label}", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=3)
        table.add_column("Provider", min_width=18)
        table.add_column("Endpoint", min_width=30)
        table.add_column("Free Limits", min_width=20)
        table.add_column("Key Env Var", min_width=18)
        table.add_column("SDK", width=5)

        for i, p in enumerate(tier_providers, 1):
            sdk = "Yes" if p.openai_compatible else "No"
            env = p.env_key or "-"
            table.add_row(str(i), p.name, p.endpoint[:45], p.free_limits, env, sdk)

        console.print(table)


def _print_list_plain(providers: list[Provider]) -> None:
    current_tier = None
    for i, p in enumerate(providers, 1):
        if p.tier != current_tier:
            current_tier = p.tier
            print(f"\n=== {current_tier.label} ===")
        sdk = "OpenAI SDK" if p.openai_compatible else "Custom"
        env = p.env_key or "none"
        print(f"  {i:>2}. {p.name:<20} {p.endpoint:<50} [{env}] ({sdk})")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

async def cmd_scan(args: argparse.Namespace, config: Config) -> list[ScanResult]:
    providers = get_unique_providers()

    if args.tier:
        tier_map = {t.value: t for t in Tier}
        tier = tier_map.get(args.tier)
        if not tier:
            print(f"Unknown tier: {args.tier}. Valid: {', '.join(tier_map.keys())}")
            sys.exit(1)
        providers = [p for p in providers if p.tier == tier]

    if args.provider:
        providers = [p for p in providers if args.provider.lower() in p.name.lower()]
        if not providers:
            print(f"No provider matching '{args.provider}'")
            sys.exit(1)

    print(f"Scanning {len(providers)} providers...")

    if HAS_RICH:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            task = progress.add_task("Scanning endpoints...", total=None)
            results = await scan_all(providers, concurrency=config.scan.concurrency)
            progress.update(task, completed=True)
    else:
        results = await scan_all(providers, concurrency=config.scan.concurrency)

    if HAS_RICH:
        _print_results_rich(results, providers)
    else:
        _print_results_plain(results)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    _save_results(results, timestamp)
    print(f"\nResults saved to {RESULTS_FILE}")

    # Run plugin hooks
    from plugins.base import PluginManager
    pm = PluginManager(config)
    pm.load_plugins()
    pm.run_on_scan_complete(results, providers)

    if args.report:
        readme_content = generate_readme(results, timestamp)
        readme_path = Path(__file__).parent / config.report.output_file
        readme_path.write_text(readme_content, encoding="utf-8")
        print(f"{config.report.output_file} generated at {readme_path}")

    return results


def cmd_report(args: argparse.Namespace, config: Config) -> None:
    loaded = _load_results()
    if loaded:
        results, timestamp = loaded
        print(f"Using scan results from {timestamp}")
    else:
        results = None
        timestamp = None
        print("No scan results found. Generating report without status data.")
        print("Run 'python main.py scan' first for live status checks.")

    readme_content = generate_readme(results, timestamp)
    readme_path = Path(__file__).parent / config.report.output_file
    readme_path.write_text(readme_content, encoding="utf-8")
    print(f"{config.report.output_file} generated at {readme_path}")


def cmd_list(args: argparse.Namespace, config: Config) -> None:
    providers = get_unique_providers()
    if HAS_RICH:
        _print_list_rich(providers)
    else:
        _print_list_plain(providers)
    print(f"\nTotal: {len(providers)} providers")


async def cmd_discover(args: argparse.Namespace, config: Config) -> None:
    """Run the AI-powered discovery engine to find new providers."""
    from discovery.engine import DiscoveryEngine

    engine = DiscoveryEngine(config)

    strategies = [args.strategy] if args.strategy else None
    print(f"Running discovery with strategies: {strategies or config.discovery.strategies}")

    candidates = await engine.run(strategies)

    if not candidates:
        print("\nNo new providers discovered.")
        # Show saved candidates if any
        saved = engine.get_saved_candidates()
        if saved:
            print(f"({len(saved)} candidates saved from previous runs)")
        return

    print(f"\nDiscovered {len(candidates)} new candidates:\n")

    for i, c in enumerate(candidates, 1):
        verified = " [VERIFIED]" if c.verified else ""
        print(f"  {i}. {c.name}{verified}")
        print(f"     Endpoint: {c.endpoint}")
        print(f"     Source:   {c.source}")
        print(f"     Confidence: {c.confidence:.0%}")
        if c.free_limits:
            print(f"     Free:     {c.free_limits}")
        if c.notes:
            print(f"     Notes:    {c.notes}")
        print()

    if config.discovery.save_candidates:
        print(f"Candidates saved to data/candidates.json")


async def cmd_benchmark(args: argparse.Namespace, config: Config) -> None:
    """Run performance benchmarks on working endpoints."""
    from plugins.builtin.benchmark import BenchmarkPlugin

    providers = get_unique_providers()
    if args.provider:
        providers = [p for p in providers if args.provider.lower() in p.name.lower()]

    plugin = BenchmarkPlugin()
    print(f"Benchmarking {len(providers)} providers...\n")
    results = await plugin._cmd_benchmark(providers, config)

    # Print summary
    print(f"\n{'Provider':<20} {'Model':<25} {'TTFT':<10} {'Total':<10} {'Tok/s':<10}")
    print("-" * 75)
    for r in sorted(results, key=lambda x: x.tokens_per_second or 0, reverse=True):
        if r.error:
            print(f"{r.provider_name:<20} {r.model:<25} {'ERROR':<10} {r.error[:30]}")
        else:
            ttft = f"{r.ttft_ms:.0f}ms" if r.ttft_ms else "-"
            total = f"{r.total_ms:.0f}ms" if r.total_ms else "-"
            tps = f"{r.tokens_per_second:.1f}" if r.tokens_per_second else "-"
            print(f"{r.provider_name:<20} {r.model:<25} {ttft:<10} {total:<10} {tps:<10}")


async def cmd_models(args: argparse.Namespace, config: Config) -> None:
    """Fetch model catalogs from all providers."""
    from plugins.builtin.model_list import ModellistPlugin

    providers = get_unique_providers()
    if args.provider:
        providers = [p for p in providers if args.provider.lower() in p.name.lower()]

    plugin = ModellistPlugin()
    print(f"Fetching models from {len(providers)} providers...\n")
    await plugin._cmd_models(providers, config)


async def cmd_export(args: argparse.Namespace, config: Config) -> None:
    """Export data to various formats."""
    from plugins.builtin.export import ExportPlugin

    providers = get_unique_providers()
    plugin = ExportPlugin()
    fmt = args.format or "all"
    print(f"Exporting to {fmt}...\n")
    await plugin._cmd_export(providers, config, fmt)


async def cmd_compare(args: argparse.Namespace, config: Config) -> None:
    """Compare providers side-by-side."""
    from tools.compare import compare_providers

    results = await compare_providers(
        args.prompt,
        args.providers,
        args.max_tokens,
    )

    print(f"\nPrompt: {args.prompt}\n")
    print("=" * 80)

    for r in results:
        if r.error:
            print(f"\n[{r.provider_name}] ({r.model}) -- ERROR: {r.error}")
        else:
            print(f"\n[{r.provider_name}] ({r.model}) -- {r.latency_ms:.0f}ms, {r.char_count} chars")
            print("-" * 40)
            print(r.response[:500])
        print()

    print("=" * 80)
    print(f"{'Provider':<20} {'Model':<30} {'Latency':<10} {'Chars':<8} {'Status'}")
    print("-" * 80)
    for r in results:
        status = "OK" if not r.error else r.error[:20]
        print(f"{r.provider_name:<20} {r.model:<30} {r.latency_ms:>7.0f}ms {r.char_count:>6} {status}")


def cmd_costs(args: argparse.Namespace, config: Config) -> None:
    """Show cost comparison across providers."""
    from tools.cost_calculator import CostCalculator, estimate_monthly_cost

    calc = CostCalculator()
    print(calc.summary(
        input_tokens=args.input_tokens,
        output_tokens=args.output_tokens,
        top_n=args.top,
    ))

    if args.provider:
        monthly = estimate_monthly_cost(
            args.provider,
            requests_per_day=args.rpd,
            avg_input=args.input_tokens,
            avg_output=args.output_tokens,
        )
        if "error" in monthly:
            print(f"\n{monthly['error']}")
        else:
            print(f"\nMonthly estimate for {monthly['provider']} ({monthly['model']}):")
            print(f"  {monthly['monthly_requests']:,} requests/month")
            print(f"  ${monthly['cost_per_request']:.6f}/request")
            print(f"  ${monthly['monthly_cost']:.2f}/month")
            print(f"  Free tier: {monthly['free_tier']}")


def cmd_tokens(args: argparse.Namespace, config: Config) -> None:
    """Estimate token count for text."""
    from tools.token_counter import count_tokens, tokens_to_cost, format_tokens

    text = args.text
    tokens = count_tokens(text)
    print(f"Text: {text[:80]}{'...' if len(text) > 80 else ''}")
    print(f"Estimated tokens: {format_tokens(tokens)} ({tokens})")
    print(f"Words: {len(text.split())}")
    print(f"Characters: {len(text)}")

    if args.price_in and args.price_out:
        cost = tokens_to_cost(tokens, tokens, args.price_in, args.price_out)
        print(f"Estimated cost (as both input+output): ${cost:.6f}")


def cmd_proxy(args: argparse.Namespace, config: Config) -> None:
    """Start the local proxy server."""
    from tools.proxy import main as proxy_main
    # Override sys.argv for the proxy's argparser
    sys.argv = ["proxy"]
    if args.port:
        sys.argv.extend(["--port", str(args.port)])
    proxy_main()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()

    parser = argparse.ArgumentParser(
        description="LLM Endpoint Scanner, Discovery Engine & Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  scan        Test all endpoints for availability
  report      Generate README.md from last scan results
  list        List all known providers
  discover    AI-powered search for new LLM endpoints
  benchmark   Measure latency/throughput of working providers
  models      Fetch available model lists from providers
  export      Export data to JSON/CSV/YAML/HTML
  compare     Compare provider responses side-by-side
  costs       Compare pricing across all providers
  tokens      Estimate token count for text
  proxy       Start a local OpenAI-compatible proxy server

Examples:
  python main.py scan --tier free --report
  python main.py discover --strategy llm_search
  python main.py compare "Explain recursion" --providers groq cerebras
  python main.py costs --provider deepseek --rpd 100
  python main.py tokens "Hello, how are you?"
  python main.py proxy --port 8000
  python main.py export --format csv
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan endpoints for availability")
    p_scan.add_argument("--tier", type=str, help="Filter by tier")
    p_scan.add_argument("--provider", type=str, help="Filter by provider name")
    p_scan.add_argument("--report", action="store_true", help="Also regenerate README.md")

    # report
    subparsers.add_parser("report", help="Generate README.md from last scan")

    # list
    subparsers.add_parser("list", help="List all providers")

    # discover
    p_discover = subparsers.add_parser("discover", help="AI-powered endpoint discovery")
    p_discover.add_argument("--strategy", type=str, help="Specific strategy to run (web_search, github_search, llm_search, community)")

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Benchmark endpoint performance")
    p_bench.add_argument("--provider", type=str, help="Filter by provider name")

    # models
    p_models = subparsers.add_parser("models", help="Fetch model catalogs")
    p_models.add_argument("--provider", type=str, help="Filter by provider name")

    # export
    p_export = subparsers.add_parser("export", help="Export data to various formats")
    p_export.add_argument("--format", type=str, choices=["json", "csv", "yaml", "html", "all"], default="all")

    # compare
    p_compare = subparsers.add_parser("compare", help="Compare providers side-by-side")
    p_compare.add_argument("prompt", help="Prompt to send to all providers")
    p_compare.add_argument("--providers", nargs="*", help="Provider names to compare")
    p_compare.add_argument("--max-tokens", type=int, default=300)

    # costs
    p_costs = subparsers.add_parser("costs", help="Compare pricing across providers")
    p_costs.add_argument("--input-tokens", type=int, default=1000, help="Input tokens per request")
    p_costs.add_argument("--output-tokens", type=int, default=500, help="Output tokens per request")
    p_costs.add_argument("--top", type=int, default=15, help="Show top N providers")
    p_costs.add_argument("--provider", type=str, help="Show monthly estimate for a provider")
    p_costs.add_argument("--rpd", type=int, default=100, help="Requests per day (for monthly estimate)")

    # tokens
    p_tokens = subparsers.add_parser("tokens", help="Estimate token count for text")
    p_tokens.add_argument("text", help="Text to estimate tokens for")
    p_tokens.add_argument("--price-in", type=float, help="Input price per million tokens")
    p_tokens.add_argument("--price-out", type=float, help="Output price per million tokens")

    # proxy
    p_proxy = subparsers.add_parser("proxy", help="Start local OpenAI-compatible proxy")
    p_proxy.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "scan":
        asyncio.run(cmd_scan(args, config))
    elif args.command == "report":
        cmd_report(args, config)
    elif args.command == "list":
        cmd_list(args, config)
    elif args.command == "discover":
        asyncio.run(cmd_discover(args, config))
    elif args.command == "benchmark":
        asyncio.run(cmd_benchmark(args, config))
    elif args.command == "models":
        asyncio.run(cmd_models(args, config))
    elif args.command == "export":
        asyncio.run(cmd_export(args, config))
    elif args.command == "compare":
        asyncio.run(cmd_compare(args, config))
    elif args.command == "costs":
        cmd_costs(args, config)
    elif args.command == "tokens":
        cmd_tokens(args, config)
    elif args.command == "proxy":
        cmd_proxy(args, config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
