"""
Notification plugin.

Sends alerts when endpoints change status. Supports:
- Webhooks (generic HTTP POST)
- Slack incoming webhooks
- Discord webhooks
- Console summary
"""

from __future__ import annotations

import json
import os

import httpx

from config import Config
from plugins.base import BasePlugin
from providers import Provider
from scanner import ScanResult


class NotifyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "notify"

    @property
    def description(self) -> str:
        return "Send notifications when endpoint status changes"

    def on_scan_complete(
        self, results: list[ScanResult], providers: list[Provider], config: Config
    ) -> None:
        """Check for status changes and send notifications."""
        working = [r for r in results if r.status == "working"]
        failed = [r for r in results if r.status in ("error", "timeout", "auth_failed")]

        message = (
            f"LLM Endpoint Scan Complete\n"
            f"Working: {len(working)}/{len(results)}\n"
            f"Failed: {len(failed)}/{len(results)}\n"
        )

        if failed:
            message += "\nFailed endpoints:\n"
            for r in failed:
                message += f"  - {r.provider_name}: {r.status} ({r.error_detail[:60]})\n"

        # Send to configured channels
        webhook_url = os.environ.get("NOTIFY_WEBHOOK_URL", "")
        slack_url = os.environ.get("SLACK_WEBHOOK_URL", "")
        discord_url = os.environ.get("DISCORD_WEBHOOK_URL", "")

        if webhook_url:
            self._send_webhook(webhook_url, message)
        if slack_url:
            self._send_slack(slack_url, message)
        if discord_url:
            self._send_discord(discord_url, message)

    def _send_webhook(self, url: str, message: str) -> None:
        try:
            httpx.post(url, json={"text": message}, timeout=10)
        except Exception as e:
            print(f"  Webhook failed: {e}")

    def _send_slack(self, url: str, message: str) -> None:
        try:
            httpx.post(url, json={"text": message}, timeout=10)
        except Exception as e:
            print(f"  Slack notification failed: {e}")

    def _send_discord(self, url: str, message: str) -> None:
        try:
            httpx.post(url, json={"content": message}, timeout=10)
        except Exception as e:
            print(f"  Discord notification failed: {e}")
