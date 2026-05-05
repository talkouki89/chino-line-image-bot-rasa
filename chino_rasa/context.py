from __future__ import annotations

import logging
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from plugins.core.features import is_enabled, load_feature_flags

from chino_rasa.line_client import LineOfficialClient, normalize_template, text_message
from chino_rasa.settings import ROOT_DIR, Settings
from chino_rasa.store import FEATURE_PATH, remember_message, save_user_settings, user_settings


START_TIME = datetime.now()


class PluginContext(SimpleNamespace):
    pass


def build_context(
    *,
    event: dict[str, Any],
    client: LineOfficialClient,
    settings: Settings,
    reply_token: str | None = None,
) -> PluginContext | None:
    message = event.get("message") or {}
    if message.get("type") != "text":
        remember_non_text_message(event)
        return None

    text = message.get("text", "")
    source = event.get("source") or {}
    sender = source.get("userId") or ""
    chat_id = source.get("groupId") or source.get("roomId") or sender
    msg = SimpleNamespace(
        id=message.get("id", ""),
        text=text,
        to=chat_id,
        _from=sender,
        toType=0 if source.get("type") == "user" else 2,
        relatedMessageId=message.get("quotedMessageId") or message.get("quoteToken"),
        contentMetadata=message,
    )
    remember_message(
        chat_id,
        {
            "id": msg.id,
            "text": text,
            "_from": sender,
            "to": chat_id,
            "contentType": 0,
            "relatedMessageId": msg.relatedMessageId,
        },
    )
    feature_flags = load_feature_flags(str(FEATURE_PATH))
    per_user_settings = user_settings(sender)

    def reply(payload: Any) -> None:
        messages = normalize_reply_payload(payload)
        if reply_token:
            client.reply_messages(reply_token, messages, chat_id=chat_id)
        else:
            logging.warning("Dropped reply because LINE replyToken is unavailable: chat_id=%s", chat_id)

    def send_template(to: str, payload: Any) -> None:
        messages = [normalize_template(payload)]
        if reply_token:
            client.reply_messages(reply_token, messages, chat_id=chat_id)
        else:
            logging.warning("Dropped template because LINE replyToken is unavailable: chat_id=%s", to)

    def send_flex(to: str, alt_text: str, contents: dict[str, Any]) -> None:
        messages = [{"type": "flex", "altText": alt_text[:400], "contents": contents}]
        if reply_token:
            client.reply_messages(reply_token, messages, chat_id=chat_id)
        else:
            logging.warning("Dropped flex because LINE replyToken is unavailable: chat_id=%s", to)

    def backup() -> None:
        save_user_settings(sender, per_user_settings)

    def log_error(error: Any) -> None:
        logging.exception("Plugin error: %s", error)

    return PluginContext(
        event=event,
        msg=msg,
        msg_id=msg.id,
        text=text,
        cmd=text.strip(),
        sender=sender,
        to=chat_id,
        cl=client,
        settings=per_user_settings,
        is_creator=bool(sender and sender == settings.creator),
        is_admin=bool(sender and sender in settings.admin_user_ids),
        start_time=START_TIME,
        tag_dir=str(ROOT_DIR / "tag"),
        reply=reply,
        send_template=send_template,
        send_flex=send_flex,
        backup=backup,
        log_error=log_error,
        is_feature_enabled=lambda key: is_enabled(feature_flags, key),
    )


def normalize_reply_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [normalize_template(item) for item in payload]
    if isinstance(payload, dict):
        return [normalize_template(payload)]
    return [text_message(str(payload))]


def remember_non_text_message(event: dict[str, Any]) -> None:
    message = event.get("message") or {}
    source = event.get("source") or {}
    sender = source.get("userId") or ""
    chat_id = source.get("groupId") or source.get("roomId") or sender
    if not chat_id:
        return
    remember_message(
        chat_id,
        {
            "id": message.get("id", ""),
            "_from": sender,
            "to": chat_id,
            "contentType": message.get("type"),
            "text": "",
        },
    )
