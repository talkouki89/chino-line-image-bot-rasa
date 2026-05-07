from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from chino_rasa.settings import ROOT_DIR


RECENT_PATH = ROOT_DIR / "json" / "recent_messages.json"
FEATURE_PATH = ROOT_DIR / "json" / "features.json"
GROUP_SETTINGS_PATH = ROOT_DIR / "json" / "group_settings.json"
CHAT_REGISTRY_PATH = ROOT_DIR / "json" / "chat_registry.json"


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def remember_message(chat_id: str, message: dict[str, Any], limit: int = 1000) -> None:
    if not chat_id:
        return
    data = read_json(RECENT_PATH, {})
    items = data.setdefault(chat_id, [])
    items.append(message)
    data[chat_id] = items[-limit:]
    write_json(RECENT_PATH, data)


def remember_chat(source: dict[str, Any]) -> None:
    chat_type = source.get("type") or ""
    chat_id = source.get("groupId") or source.get("roomId") or source.get("userId") or ""
    if not chat_id:
        return
    data = read_json(CHAT_REGISTRY_PATH, {"groups": {}, "rooms": {}, "users": {}})
    if chat_type == "group" or source.get("groupId"):
        bucket = "groups"
    elif chat_type == "room" or source.get("roomId"):
        bucket = "rooms"
    else:
        bucket = "users"
    items = data.setdefault(bucket, {})
    items[chat_id] = {
        "id": chat_id,
        "type": bucket[:-1],
        "last_seen": str(message_timestamp()),
    }
    write_json(CHAT_REGISTRY_PATH, data)


def bot_chat_counts() -> dict[str, Any]:
    data = read_json(CHAT_REGISTRY_PATH, {"groups": {}, "rooms": {}, "users": {}})
    groups = data.get("groups") or {}
    rooms = data.get("rooms") or {}
    users = data.get("users") or {}
    return {
        "groups": len(groups),
        "rooms": len(rooms),
        "users": len(users),
        "group_ids": sorted(groups.keys()),
        "room_ids": sorted(rooms.keys()),
    }


def recent_messages(chat_id: str, limit: int = 1000) -> list[SimpleNamespace]:
    data = read_json(RECENT_PATH, {})
    items = data.get(chat_id, [])[-limit:]
    return [SimpleNamespace(**item) for item in reversed(items)]


def group_settings(chat_id: str) -> dict[str, Any]:
    if not chat_id:
        return {}
    data = read_json(GROUP_SETTINGS_PATH, {})
    settings = data.setdefault(chat_id, {})
    write_json(GROUP_SETTINGS_PATH, data)
    return settings


def update_group_settings(chat_id: str, **values: Any) -> dict[str, Any]:
    data = read_json(GROUP_SETTINGS_PATH, {})
    settings = data.setdefault(chat_id, {})
    for key, value in values.items():
        if value is None:
            settings.pop(key, None)
        else:
            settings[key] = value
    if settings:
        data[chat_id] = settings
    else:
        data.pop(chat_id, None)
    write_json(GROUP_SETTINGS_PATH, data)
    return settings


def group_sender(chat_id: str) -> dict[str, str]:
    settings = group_settings(chat_id)
    sender = {}
    name = str(settings.get("bot_name") or "").strip()
    icon_url = str(settings.get("bot_icon_url") or "").strip()
    if name:
        sender["name"] = name[:20]
    if icon_url:
        sender["iconUrl"] = icon_url
    return sender


def welcome_message(chat_id: str) -> str:
    return str(group_settings(chat_id).get("welcome_message") or "").strip()


def message_timestamp() -> str:
    from datetime import datetime

    return datetime.now().isoformat(timespec="seconds")
