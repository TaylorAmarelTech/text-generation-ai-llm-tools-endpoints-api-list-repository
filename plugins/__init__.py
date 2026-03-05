"""
Plugin system for extending the LLM Endpoint Scanner.

Plugins can add new commands, post-processing steps, export formats,
and integrations. Drop a .py file in plugins/custom/ to add your own.
"""

from plugins.base import BasePlugin, PluginManager

__all__ = ["BasePlugin", "PluginManager"]
