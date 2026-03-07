"""
Configuration system for the LLM Endpoint Scanner.

Loads settings from config.yaml with environment variable overrides.
Users can customize scan behavior, discovery strategies, plugin loading,
search API keys, and report formatting.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

CONFIG_FILE = Path(__file__).parent / "config.yaml"
DATA_DIR = Path(__file__).parent / "data"


@dataclass
class ScanConfig:
    concurrency: int = 10
    timeout_seconds: int = 30
    test_prompt: str = "Say 'hello' in one word."
    max_tokens: int = 10
    retry_count: int = 1
    skip_local: bool = False


@dataclass
class SearchConfig:
    """Configuration for web search APIs used by the discovery engine."""
    brave_api_key: str = ""
    serper_api_key: str = ""
    google_api_key: str = ""
    google_cse_id: str = ""
    max_results_per_query: int = 10
    search_queries: list[str] = field(default_factory=lambda: [
        "free LLM API endpoint 2026",
        "free text generation API no credit card",
        "OpenAI compatible free API endpoint",
        "free inference API LLM open source",
        "new AI API provider free tier launch",
    ])


@dataclass
class DiscoveryConfig:
    """Configuration for the AI-powered discovery engine."""
    enabled: bool = True
    strategies: list[str] = field(default_factory=lambda: [
        "web_search", "github_search", "llm_search",
    ])
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    auto_verify: bool = True
    save_candidates: bool = True


@dataclass
class PluginConfig:
    enabled_plugins: list[str] = field(default_factory=lambda: [
        "benchmark", "model_list", "export",
    ])
    custom_plugin_dir: str = "plugins/custom"


@dataclass
class ReportConfig:
    output_file: str = "README.md"
    include_quick_start: bool = True
    include_cascade_example: bool = True
    include_scanner_docs: bool = True
    github_repo_url: str = ""


@dataclass
class Config:
    scan: ScanConfig = field(default_factory=ScanConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    discovery: DiscoveryConfig = field(default_factory=DiscoveryConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)
    report: ReportConfig = field(default_factory=ReportConfig)


def _deep_update(base: dict, overrides: dict) -> dict:
    """Recursively merge overrides into base dict."""
    for key, val in overrides.items():
        if isinstance(val, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_update(base[key], val)
        else:
            base[key] = val
    return base


def _apply_env_overrides(cfg: Config) -> None:
    """Override config values from environment variables."""
    env_map = {
        "BRAVE_API_KEY": ("search", "brave_api_key"),
        "SERPER_API_KEY": ("search", "serper_api_key"),
        "GOOGLE_API_KEY": ("search", "google_api_key"),
        "GOOGLE_CSE_ID": ("search", "google_cse_id"),
        "SCAN_CONCURRENCY": ("scan", "concurrency"),
        "SCAN_TIMEOUT": ("scan", "timeout_seconds"),
        "DISCOVERY_LLM_PROVIDER": ("discovery", "llm_provider"),
        "DISCOVERY_LLM_MODEL": ("discovery", "llm_model"),
        "GITHUB_REPO_URL": ("report", "github_repo_url"),
    }
    for env_var, (section, key) in env_map.items():
        val = os.environ.get(env_var, "").strip()
        if val:
            sub = getattr(cfg, section)
            current = getattr(sub, key)
            if isinstance(current, int):
                val = int(val)
            elif isinstance(current, bool):
                val = val.lower() in ("true", "1", "yes")
            setattr(sub, key, val)


def _dict_to_config(data: dict[str, Any]) -> Config:
    """Convert a raw dict (from YAML) into a Config dataclass."""
    cfg = Config()
    if "scan" in data:
        for k, v in data["scan"].items():
            if hasattr(cfg.scan, k):
                setattr(cfg.scan, k, v)
    if "search" in data:
        for k, v in data["search"].items():
            if hasattr(cfg.search, k):
                setattr(cfg.search, k, v)
    if "discovery" in data:
        for k, v in data["discovery"].items():
            if hasattr(cfg.discovery, k):
                setattr(cfg.discovery, k, v)
    if "plugins" in data:
        for k, v in data["plugins"].items():
            if hasattr(cfg.plugins, k):
                setattr(cfg.plugins, k, v)
    if "report" in data:
        for k, v in data["report"].items():
            if hasattr(cfg.report, k):
                setattr(cfg.report, k, v)
    return cfg


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from YAML file + environment overrides."""
    path = config_path or CONFIG_FILE

    if path.exists() and HAS_YAML:
        with open(path) as f:
            raw = yaml.safe_load(f) or {}
        cfg = _dict_to_config(raw)
    else:
        cfg = Config()

    _apply_env_overrides(cfg)
    DATA_DIR.mkdir(exist_ok=True)
    return cfg
