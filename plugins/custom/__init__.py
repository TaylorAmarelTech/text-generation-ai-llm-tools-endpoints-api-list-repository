"""
Custom plugins directory.

Drop any .py file here that defines a class extending BasePlugin.
It will be automatically loaded if the file doesn't start with '_'.

Example custom plugin (my_plugin.py):

    from plugins.base import BasePlugin
    from scanner import ScanResult
    from providers import Provider
    from config import Config

    class MyPlugin(BasePlugin):
        @property
        def name(self) -> str:
            return "my_plugin"

        def on_scan_complete(self, results, providers, config):
            working = [r for r in results if r.status == "working"]
            print(f"My plugin: {len(working)} working endpoints!")
"""
