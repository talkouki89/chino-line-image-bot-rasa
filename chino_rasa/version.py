from __future__ import annotations

from chino_rasa.settings import ROOT_DIR


VERSION_FILE = ROOT_DIR / "VERSION"


def current_version() -> str:
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip() or "unknown"
    except OSError:
        return "unknown"
