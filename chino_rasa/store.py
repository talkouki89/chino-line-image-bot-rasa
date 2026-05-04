from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from chino_rasa.settings import ROOT_DIR


STATE_PATH = ROOT_DIR / "json" / "state.json"
RECENT_PATH = ROOT_DIR / "json" / "recent_messages.json"
FEATURE_PATH = ROOT_DIR / "json" / "features.json"
GROUPS_PATH = ROOT_DIR / "json" / "group_ids.json"


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def user_settings(user_id: str) -> dict[str, Any]:
    state = read_json(STATE_PATH, {})
    users = state.setdefault("users", {})
    settings = users.setdefault(user_id, {"days": 30, "sc": 0})
    write_json(STATE_PATH, state)
    return settings


def save_user_settings(user_id: str, settings: dict[str, Any]) -> None:
    state = read_json(STATE_PATH, {})
    state.setdefault("users", {})[user_id] = settings
    write_json(STATE_PATH, state)


def remember_group(group_id: str) -> None:
    if not group_id:
        return
    groups = read_json(GROUPS_PATH, [])
    if group_id not in groups:
        groups.append(group_id)
        write_json(GROUPS_PATH, groups)


def all_groups() -> list[str]:
    groups = read_json(GROUPS_PATH, [])
    return [item for item in groups if isinstance(item, str)]


def remember_message(chat_id: str, message: dict[str, Any], limit: int = 1000) -> None:
    if not chat_id:
        return
    data = read_json(RECENT_PATH, {})
    items = data.setdefault(chat_id, [])
    items.append(message)
    data[chat_id] = items[-limit:]
    write_json(RECENT_PATH, data)


def recent_messages(chat_id: str, limit: int = 1000) -> list[SimpleNamespace]:
    data = read_json(RECENT_PATH, {})
    items = data.get(chat_id, [])[-limit:]
    return [SimpleNamespace(**item) for item in reversed(items)]
