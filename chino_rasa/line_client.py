from __future__ import annotations

import mimetypes
import shutil
import uuid
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import requests

from chino_rasa.settings import Settings
from chino_rasa.store import all_groups, recent_messages


LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
LINE_CONTENT_URL = "https://api-data.line.me/v2/bot/message/{message_id}/content"
LINE_PROFILE_URL = "https://api.line.me/v2/bot/profile/{user_id}"
logger = logging.getLogger(__name__)


class LineOfficialClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.line_access_token}",
            "Content-Type": "application/json",
        }

    def reply_messages(self, reply_token: str, messages: list[dict[str, Any]]) -> None:
        if not reply_token:
            return
        self._post(LINE_REPLY_URL, {"replyToken": reply_token, "messages": messages[:5]})

    def push_messages(self, to: str, messages: list[dict[str, Any]]) -> None:
        self._post(LINE_PUSH_URL, {"to": to, "messages": messages[:5]})

    def sendMessage(self, to: str, text: str) -> None:
        self.push_messages(to, [text_message(text)])

    def sendReplyMessage(self, msg_id: str, to: str, text: str) -> None:
        self.sendMessage(to, text)

    def relatedMessage(self, to: str, text: str, msg_id: str | None = None) -> None:
        self.sendMessage(to, text)

    def sendImageWithURL(self, to: str, image_url: str) -> None:
        self.push_messages(to, [image_message(image_url)])

    def sendVideoWithURL(self, to: str, video_url: str) -> None:
        self.push_messages(to, [video_message(video_url)])

    def sendImage(self, to: str, path: str) -> None:
        url = self.publish_local_file(path)
        self.sendImageWithURL(to, url)

    def sendVideo(self, to: str, path: str) -> None:
        url = self.publish_local_file(path)
        self.sendVideoWithURL(to, url)

    def sendFlex(self, to: str, alt_text: str, contents: dict[str, Any]) -> None:
        self.push_messages(to, [{"type": "flex", "altText": alt_text[:400], "contents": contents}])

    def sendTemplate(self, to: str, template: Any) -> None:
        message = normalize_template(template)
        self.push_messages(to, [message])

    def downloadReplyImage(self, to: str, message_id: str, saveAs: str, objFrom: str | None = None) -> str:
        return self.downloadObjectMsg(message_id, returnAs="path", saveAs=saveAs, objFrom=objFrom)

    def downloadObjectMsg(self, message_id: str, returnAs: str = "path", saveAs: str | None = None, objFrom: str | None = None):
        response = requests.get(
            LINE_CONTENT_URL.format(message_id=message_id),
            headers={"Authorization": f"Bearer {self.settings.line_access_token}"},
            timeout=60,
        )
        response.raise_for_status()
        if returnAs == "bytes":
            return response.content
        if not saveAs:
            saveAs = str(Path("json/images") / f"{message_id}.bin")
        Path(saveAs).parent.mkdir(parents=True, exist_ok=True)
        Path(saveAs).write_bytes(response.content)
        return saveAs

    def getRecentMessagesV2(self, to: str, limit: int = 1000) -> list[SimpleNamespace]:
        return recent_messages(to, limit)

    def getAllChatMids(self) -> list[str]:
        return all_groups()

    def getContact(self, user_id: str) -> SimpleNamespace:
        response = requests.get(LINE_PROFILE_URL.format(user_id=user_id), headers=self.headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        return SimpleNamespace(
            mid=user_id,
            displayName=data.get("displayName", user_id),
            pictureStatus=data.get("pictureUrl", ""),
            statusMessage=data.get("statusMessage", ""),
        )

    def getProfileCoverObjIdAndUrl(self, user_id: str) -> dict[str, str]:
        return {"url": ""}

    def publish_local_file(self, source: str) -> str:
        if not self.settings.public_base_url:
            raise RuntimeError("PUBLIC_BASE_URL 未設定，無法把本機媒體轉成 LINE 可讀取的 HTTPS URL。")
        src = Path(source)
        suffix = src.suffix or mimetypes.guess_extension(mimetypes.guess_type(str(src))[0] or "") or ".bin"
        name = f"{uuid.uuid4().hex}{suffix}"
        target = self.settings.public_media_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        return f"{self.settings.public_base_url}/webhooks/line/public/media/{name}"

    def _post(self, url: str, payload: dict[str, Any]) -> None:
        response = requests.post(url, headers=self.headers, json=payload, timeout=15)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.error("LINE API request failed: status=%s url=%s body=%s", response.status_code, url, response.text)
            raise


def text_message(text: str) -> dict[str, str]:
    return {"type": "text", "text": str(text)[:5000]}


def image_message(url: str) -> dict[str, str]:
    return {"type": "image", "originalContentUrl": url, "previewImageUrl": url}


def video_message(url: str) -> dict[str, str]:
    return {"type": "video", "originalContentUrl": url, "previewImageUrl": url}


def normalize_template(template: Any) -> dict[str, Any]:
    if isinstance(template, dict):
        if template.get("type") in {"flex", "text", "image", "video"}:
            return template
        return {"type": "flex", "altText": template.get("altText", "Chino Bot"), "contents": template}
    return text_message(str(template))
