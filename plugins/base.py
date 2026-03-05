"""
Plugin base class and loader.

Plugins extend the scanner with additional capabilities:
- benchmark: measure latency, throughput, TTFT
- model_list: fetch available models from each provider
- export: export data to JSON/CSV/YAML
- pricing: track and compare pricing
- notify: send alerts via webhooks/Slack/email
"""

from __future__ import annotations

import importlib
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from config import Config
from providers import Provider
from scanner import ScanResult


class BasePlugin(ABC):
    """Base class for all plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin name."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description."""
        return ""

    def on_scan_complete(
        self, results: list[ScanResult], providers: list[Provider], config: Config
    ) -> None:
        """Called after a scan completes. Override to process results."""
        pass

    def on_discovery_complete(
        self, candidates: list[Any], config: Config
    ) -> None:
        """Called after discovery completes. Override to process candidates."""
        pass

    def register_commands(self) -> dict[str, Any]:
        """Return a dict of CLI command names -> handler functions."""
        return {}


class PluginManager:
    """Loads and manages plugins."""

    def __init__(self, config: Config):
        self.config = config
        self.plugins: list[BasePlugin] = []

    def load_plugins(self) -> None:
        """Load all enabled plugins from builtin and custom dirs."""
        for plugin_name in self.config.plugins.enabled_plugins:
            plugin = self._load_builtin(plugin_name)
            if plugin:
                self.plugins.append(plugin)

        # Load custom plugins
        custom_dir = Path(self.config.plugins.custom_plugin_dir)
        if custom_dir.exists():
            for py_file in custom_dir.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                plugin = self._load_custom(py_file)
                if plugin:
                    self.plugins.append(plugin)

    def _load_builtin(self, name: str) -> BasePlugin | None:
        """Load a built-in plugin by name."""
        try:
            module = importlib.import_module(f"plugins.builtin.{name}")
            # Convention: plugin class is named <Name>Plugin
            class_name = name.title().replace("_", "") + "Plugin"
            cls = getattr(module, class_name, None)
            if cls and issubclass(cls, BasePlugin):
                return cls()
        except (ImportError, AttributeError) as e:
            print(f"  Could not load plugin '{name}': {e}")
        return None

    def _load_custom(self, path: Path) -> BasePlugin | None:
        """Load a custom plugin from a .py file."""
        try:
            module_name = f"plugins.custom.{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            if not spec or not spec.loader:
                return None
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find the first BasePlugin subclass in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                ):
                    return attr()
        except Exception as e:
            print(f"  Could not load custom plugin '{path.name}': {e}")
        return None

    def run_on_scan_complete(
        self, results: list[ScanResult], providers: list[Provider]
    ) -> None:
        """Notify all plugins that a scan completed."""
        for plugin in self.plugins:
            try:
                plugin.on_scan_complete(results, providers, self.config)
            except Exception as e:
                print(f"  Plugin '{plugin.name}' error: {e}")

    def run_on_discovery_complete(self, candidates: list) -> None:
        """Notify all plugins that discovery completed."""
        for plugin in self.plugins:
            try:
                plugin.on_discovery_complete(candidates, self.config)
            except Exception as e:
                print(f"  Plugin '{plugin.name}' error: {e}")

    def get_commands(self) -> dict[str, Any]:
        """Collect CLI commands from all plugins."""
        commands: dict[str, Any] = {}
        for plugin in self.plugins:
            commands.update(plugin.register_commands())
        return commands
