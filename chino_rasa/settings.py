from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_environment() -> None:
    load_dotenv(ROOT_DIR / ".env", override=False)


def parse_timezone(value: str | None) -> ZoneInfo:
    raw = (value or "Asia/Taipei").strip()
    if raw.upper() in {"UTC+8", "UTC+08", "UTC+08:00", "TAIWAN"}:
        return ZoneInfo("Asia/Taipei")
    if raw.upper().startswith("UTC"):
        sign = "-" if "-" in raw else "+"
        hours = raw.split(sign, 1)[1].split(":", 1)[0]
        name = f"Etc/GMT{'-' if sign == '+' else '+'}{int(hours)}"
        return ZoneInfo(name)
    return ZoneInfo(raw)


@dataclass(frozen=True)
class Settings:
    line_access_token: str
    line_channel_secret: str
    creator: str
    admin_user_ids: set[str]
    port: int
    public_base_url: str
    public_media_dir: Path
    hot_reload_plugins: bool
    timezone: ZoneInfo

    @classmethod
    def from_env(cls) -> "Settings":
        load_environment()
        admins = {
            item.strip()
            for item in (os.getenv("ADMIN_USER_IDS") or os.getenv("ADMIN_MIDS") or "").split(",")
            if item.strip()
        }
        creator = os.getenv("Creator", "").strip()
        if creator:
            admins.add(creator)
        return cls(
            line_access_token=(os.getenv("LINE_CHANNEL_ACCESS_TOKEN") or os.getenv("LINE_ACCESS_TOKEN") or "").strip(),
            line_channel_secret=(os.getenv("LINE_CHANNEL_SECRET") or "").strip(),
            creator=creator,
            admin_user_ids=admins,
            port=int(os.getenv("PORT", "5005")),
            public_base_url=os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/"),
            public_media_dir=ROOT_DIR / "public" / "media",
            hot_reload_plugins=env_bool("HOT_RELOAD_PLUGINS", True),
            timezone=parse_timezone(os.getenv("BOT_TIMEZONE") or os.getenv("TZ") or "Asia/Taipei"),
        )
