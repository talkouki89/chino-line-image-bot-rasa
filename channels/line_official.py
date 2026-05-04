from __future__ import annotations

import base64
import hashlib
import hmac
import logging
from pathlib import Path
from typing import Any, Text
from urllib.parse import parse_qs

from rasa.core.channels.channel import CollectingOutputChannel, InputChannel, UserMessage
from sanic import Blueprint, response

from chino_rasa.context import build_context
from chino_rasa.line_client import LineOfficialClient
from chino_rasa.plugin_runtime import PluginRuntime
from chino_rasa.settings import Settings
from chino_rasa.store import welcome_message


logger = logging.getLogger(__name__)


class LineOfficialOutput(CollectingOutputChannel):
    @classmethod
    def name(cls) -> Text:
        return "line"

    def __init__(self, client: LineOfficialClient, reply_token: str | None = None, chat_id: str | None = None):
        super().__init__()
        self.client = client
        self.reply_token = reply_token
        self.chat_id = chat_id

    async def send_text_message(self, recipient_id: Text, text: Text, **kwargs: Any) -> None:
        messages = [{"type": "text", "text": text[:5000]}]
        if self.reply_token:
            self.client.reply_messages(self.reply_token, messages, chat_id=self.chat_id or recipient_id)
            self.reply_token = None
        else:
            self.client.push_messages(recipient_id, messages)

    async def send_custom_json(self, recipient_id: Text, json_message: dict[str, Any], **kwargs: Any) -> None:
        if self.reply_token:
            self.client.reply_messages(self.reply_token, [json_message], chat_id=self.chat_id or recipient_id)
            self.reply_token = None
        else:
            self.client.push_messages(recipient_id, [json_message])


class LineOfficialInput(InputChannel):
    @classmethod
    def name(cls) -> Text:
        return "line"

    def __init__(self, channel_access_token: str | None = None, channel_secret: str | None = None, **kwargs: Any):
        self.settings = Settings.from_env()
        if channel_access_token:
            object.__setattr__(self.settings, "line_access_token", channel_access_token)
        if channel_secret:
            object.__setattr__(self.settings, "line_channel_secret", channel_secret)
        self.client = LineOfficialClient(self.settings)
        self.plugins = PluginRuntime(self.settings)

    def blueprint(self, on_new_message):
        line_webhook = Blueprint("line_official_webhook", __name__)

        @line_webhook.route("/", methods=["GET"])
        async def health(request):
            return response.json({"status": "ok", "channel": self.name()})

        @line_webhook.route("/public/media/<filename:path>", methods=["GET"])
        async def public_media(request, filename: str):
            path = (self.settings.public_media_dir / filename).resolve()
            root = self.settings.public_media_dir.resolve()
            if not str(path).startswith(str(root)) or not path.is_file():
                return response.text("not found", status=404)
            return await response.file(str(path))

        @line_webhook.route("/webhook", methods=["POST"])
        async def webhook(request):
            body = request.body or b""
            if not self._valid_signature(body, request.headers.get("X-Line-Signature", "")):
                logger.warning("LINE webhook rejected: invalid signature, body_size=%s", len(body))
                return response.text("invalid signature", status=403)
            payload = request.json or {}
            events = payload.get("events", [])
            logger.info("LINE webhook accepted: events=%s", len(events))
            for event in events:
                try:
                    await self._handle_event(event, on_new_message)
                except Exception:
                    logger.exception("LINE webhook event failed: type=%s", event.get("type"))
            return response.text("OK")

        return line_webhook

    async def _handle_event(self, event: dict[str, Any], on_new_message) -> None:
        event_type = event.get("type")
        if event_type == "postback":
            await self._handle_postback(event, on_new_message)
            return
        if event_type == "memberJoined":
            self._handle_member_joined(event)
            return
        if event_type != "message":
            logger.info("LINE event ignored: type=%s", event_type)
            return
        await self._handle_text_event(event, on_new_message)

    async def _handle_text_event(self, event: dict[str, Any], on_new_message) -> None:
        reply_token = event.get("replyToken")
        context = build_context(event=event, client=self.client, settings=self.settings, reply_token=reply_token)
        message = event.get("message") or {}
        source = event.get("source") or {}
        chat_id = source.get("groupId") or source.get("roomId") or source.get("userId")
        sender = source.get("userId") or chat_id
        logger.info(
            "LINE message received: message_type=%s sender=%s text=%r",
            message.get("type"),
            chat_id,
            message.get("text", ""),
        )
        if context and self.plugins.dispatch(context):
            logger.info("LINE message handled by plugin: sender=%s text=%r", sender, message.get("text", ""))
            return

        if message.get("type") != "text":
            logger.info("LINE non-text message stored but not sent to Rasa: message_type=%s", message.get("type"))
            return
        logger.info("LINE message forwarded to Rasa: sender=%s text=%r", sender, message.get("text", ""))
        output = LineOfficialOutput(self.client, reply_token, chat_id=chat_id)
        await on_new_message(
            UserMessage(
                text=message.get("text", ""),
                output_channel=output,
                sender_id=sender,
                input_channel=self.name(),
                metadata={"line_event": event},
            )
        )

    async def _handle_postback(self, event: dict[str, Any], on_new_message) -> None:
        data = ((event.get("postback") or {}).get("data") or "").strip()
        values = parse_qs(data, keep_blank_values=True)
        command = first(values, "cmd") or first(values, "command")
        if not command and first(values, "action") == "toggle_feature":
            key = first(values, "key")
            if key:
                command = f"功能切換 {key}"
        if not command:
            logger.info("LINE postback ignored: data=%r", data)
            return
        synthetic = dict(event)
        synthetic["type"] = "message"
        synthetic["message"] = {
            "id": f"postback-{event.get('webhookEventId', '')}",
            "type": "text",
            "text": command,
        }
        logger.info("LINE postback converted to command: %r", command)
        await self._handle_text_event(synthetic, on_new_message)

    def _handle_member_joined(self, event: dict[str, Any]) -> None:
        source = event.get("source") or {}
        chat_id = source.get("groupId") or source.get("roomId")
        if not chat_id:
            return
        template = welcome_message(chat_id)
        if not template:
            logger.info("LINE memberJoined without welcome message: chat_id=%s", chat_id)
            return
        group_name = self._group_name(source)
        for member in (event.get("joined") or {}).get("members", []):
            user_id = member.get("userId")
            user_name = self._member_name(source, user_id)
            text = template.replace("{UserName}", user_name).replace("{GroupName}", group_name)
            self.client.push_messages(chat_id, [{"type": "text", "text": text[:5000]}])

    def _group_name(self, source: dict[str, Any]) -> str:
        group_id = source.get("groupId")
        if not group_id:
            return source.get("roomId") or "此聊天室"
        try:
            return self.client.get_group_summary(group_id).groupName
        except Exception:
            logger.exception("Failed to get LINE group summary: group_id=%s", group_id)
            return group_id

    def _member_name(self, source: dict[str, Any], user_id: str | None) -> str:
        if not user_id:
            return "新成員"
        try:
            if source.get("groupId"):
                return self.client.get_group_member_profile(source["groupId"], user_id).displayName
            if source.get("roomId"):
                return self.client.get_room_member_profile(source["roomId"], user_id).displayName
        except Exception:
            logger.exception("Failed to get LINE member profile: user_id=%s", user_id)
        return user_id

    def _valid_signature(self, body: bytes, signature: str) -> bool:
        if not self.settings.line_channel_secret:
            logging.warning("LINE_CHANNEL_SECRET is empty; signature verification is disabled.")
            return True
        digest = hmac.new(self.settings.line_channel_secret.encode("utf-8"), body, hashlib.sha256).digest()
        expected = base64.b64encode(digest).decode("utf-8")
        return hmac.compare_digest(expected, signature)


def first(values: dict[str, list[str]], key: str) -> str:
    items = values.get(key) or []
    return items[0] if items else ""
