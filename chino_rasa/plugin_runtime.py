from __future__ import annotations

from plugin_loader import PluginManager

from chino_rasa.settings import ROOT_DIR, Settings


class PluginRuntime:
    def __init__(self, settings: Settings):
        self.manager = PluginManager(ROOT_DIR / "plugins", enabled=settings.hot_reload_plugins)

    def dispatch(self, context) -> bool:
        return self.manager.dispatch(context)
