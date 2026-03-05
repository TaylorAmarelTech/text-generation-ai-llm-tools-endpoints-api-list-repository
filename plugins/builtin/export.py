"""
Export plugin.

Exports provider data and scan results to multiple formats:
JSON, CSV, YAML, and a minimal HTML report.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from config import Config
from plugins.base import BasePlugin
from providers import Provider, get_unique_providers
from scanner import ScanResult


DATA_DIR = Path(__file__).parent.parent.parent / "data"


class ExportPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "export"

    @property
    def description(self) -> str:
        return "Export provider data to JSON, CSV, YAML"

    def register_commands(self) -> dict:
        return {"export": self._cmd_export}

    def on_scan_complete(
        self, results: list[ScanResult], providers: list[Provider], config: Config
    ) -> None:
        """Auto-export after scan if plugin is enabled."""
        self._export_json(providers, results)

    async def _cmd_export(
        self, providers: list[Provider], config: Config, fmt: str = "all"
    ) -> None:
        """Export providers to various formats."""
        DATA_DIR.mkdir(exist_ok=True)
        results = self._load_results()

        if fmt in ("all", "json"):
            self._export_json(providers, results)
        if fmt in ("all", "csv"):
            self._export_csv(providers, results)
        if fmt in ("all", "yaml"):
            self._export_yaml(providers)
        if fmt in ("all", "html"):
            self._export_html(providers, results)

    def _load_results(self) -> list[ScanResult]:
        results_file = DATA_DIR.parent / "scan_results.json"
        if results_file.exists():
            data = json.loads(results_file.read_text())
            return [ScanResult(**r) for r in data.get("results", [])]
        return []

    def _export_json(
        self, providers: list[Provider], results: list[ScanResult]
    ) -> None:
        results_map = {r.provider_name: r for r in results}
        data = []
        for p in providers:
            r = results_map.get(p.name)
            entry = {
                "name": p.name,
                "tier": p.tier.value,
                "endpoint": p.endpoint,
                "free_limits": p.free_limits,
                "models": p.models,
                "openai_compatible": p.openai_compatible,
                "signup_url": p.signup_url,
                "notes": p.notes,
                "status": r.status if r else "unknown",
                "latency_ms": r.latency_ms if r else None,
            }
            data.append(entry)

        out = DATA_DIR / "providers.json"
        out.write_text(json.dumps(data, indent=2))
        print(f"  Exported JSON: {out}")

    def _export_csv(
        self, providers: list[Provider], results: list[ScanResult]
    ) -> None:
        results_map = {r.provider_name: r for r in results}
        out = DATA_DIR / "providers.csv"

        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Name", "Tier", "Endpoint", "Free Limits", "Models",
                "OpenAI Compatible", "Sign Up", "Status", "Latency (ms)", "Notes",
            ])
            for p in providers:
                r = results_map.get(p.name)
                writer.writerow([
                    p.name,
                    p.tier.value,
                    p.endpoint,
                    p.free_limits,
                    "; ".join(p.models[:3]),
                    "Yes" if p.openai_compatible else "No",
                    p.signup_url,
                    r.status if r else "unknown",
                    r.latency_ms if r else "",
                    p.notes,
                ])

        print(f"  Exported CSV: {out}")

    def _export_yaml(self, providers: list[Provider]) -> None:
        try:
            import yaml
        except ImportError:
            print("  YAML export requires: pip install pyyaml")
            return

        data = []
        for p in providers:
            data.append({
                "name": p.name,
                "tier": p.tier.value,
                "endpoint": p.endpoint,
                "env_key": p.env_key,
                "free_limits": p.free_limits,
                "models": p.models,
                "openai_compatible": p.openai_compatible,
                "signup_url": p.signup_url,
                "notes": p.notes,
            })

        out = DATA_DIR / "providers.yaml"
        with open(out, "w") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        print(f"  Exported YAML: {out}")

    def _export_html(
        self, providers: list[Provider], results: list[ScanResult]
    ) -> None:
        results_map = {r.provider_name: r for r in results}
        rows = []
        for p in providers:
            r = results_map.get(p.name)
            status = r.status if r else "unknown"
            status_class = "working" if status == "working" else "other"
            latency = f"{r.latency_ms:.0f}ms" if r and r.latency_ms else "-"
            rows.append(
                f'<tr class="{status_class}">'
                f"<td>{p.name}</td>"
                f"<td>{p.tier.label}</td>"
                f"<td><code>{p.endpoint}</code></td>"
                f"<td>{p.free_limits}</td>"
                f"<td>{status}</td>"
                f"<td>{latency}</td>"
                f"</tr>"
            )

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>LLM Endpoints</title>
<style>
body {{ font-family: system-ui; margin: 2rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #333; color: white; }}
tr.working {{ background: #e6ffe6; }}
code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
</style></head><body>
<h1>LLM API Endpoints Directory</h1>
<table>
<tr><th>Provider</th><th>Tier</th><th>Endpoint</th><th>Free Limits</th><th>Status</th><th>Latency</th></tr>
{"".join(rows)}
</table></body></html>"""

        out = DATA_DIR / "providers.html"
        out.write_text(html, encoding="utf-8")
        print(f"  Exported HTML: {out}")
