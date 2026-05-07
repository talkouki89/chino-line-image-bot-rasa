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
from chino_rasa.store import group_sender, recent_messages


LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_CONTENT_URL = "https://api-data.line.me/v2/bot/message/{message_id}/content"
LINE_PROFILE_URL = "https://api.line.me/v2/bot/profile/{user_id}"
LINE_GROUP_SUMMARY_URL = "https://api.line.me/v2/bot/group/{group_id}/summary"
LINE_GROUP_MEMBER_COUNT_URL = "https://api.line.me/v2/bot/group/{group_id}/members/count"
LINE_ROOM_MEMBER_COUNT_URL = "https://api.line.me/v2/bot/room/{room_id}/members/count"
LINE_GROUP_MEMBER_PROFILE_URL = "https://api.line.me/v2/bot/group/{group_id}/member/{user_id}"
LINE_ROOM_MEMBER_PROFILE_URL = "https://api.line.me/v2/bot/room/{room_id}/member/{user_id}"
LINE_INSIGHT_FOLLOWERS_URL = "https://api.line.me/v2/bot/insight/followers"
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

    def reply_messages(self, reply_token: str, messages: list[dict[str, Any]], chat_id: str | None = None) -> None:
        if not reply_token:
            return
        self._post(LINE_REPLY_URL, {"replyToken": reply_token, "messages": self._with_sender(messages[:5], chat_id)})

    def push_messages(self, to: str, messages: list[dict[str, Any]]) -> None:
        logger.warning("LINE push message skipped to avoid push quota usage: to=%s count=%s", to, len(messages))

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

    def get_group_summary(self, group_id: str) -> SimpleNamespace:
        response = requests.get(LINE_GROUP_SUMMARY_URL.format(group_id=group_id), headers=self.headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        return SimpleNamespace(
            groupId=data.get("groupId", group_id),
            groupName=data.get("groupName", group_id),
            pictureUrl=data.get("pictureUrl", ""),
        )

    def get_followers(self, date: str) -> SimpleNamespace:
        response = requests.get(
            LINE_INSIGHT_FOLLOWERS_URL,
            headers=self.headers,
            params={"date": date},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return SimpleNamespace(
            status=data.get("status", ""),
            followers=data.get("followers"),
            targetedReaches=data.get("targetedReaches"),
            blocks=data.get("blocks"),
        )

    def get_group_member_count(self, group_id: str) -> int:
        response = requests.get(LINE_GROUP_MEMBER_COUNT_URL.format(group_id=group_id), headers=self.headers, timeout=20)
        response.raise_for_status()
        return int(response.json().get("count", 0))

    def get_room_member_count(self, room_id: str) -> int:
        response = requests.get(LINE_ROOM_MEMBER_COUNT_URL.format(room_id=room_id), headers=self.headers, timeout=20)
        response.raise_for_status()
        return int(response.json().get("count", 0))

    def get_group_member_profile(self, group_id: str, user_id: str) -> SimpleNamespace:
        response = requests.get(
            LINE_GROUP_MEMBER_PROFILE_URL.format(group_id=group_id, user_id=user_id),
            headers=self.headers,
            timeout=20,
        )
        response.raise_for_status()
        return self._profile_from_response(response, user_id)

    def get_room_member_profile(self, room_id: str, user_id: str) -> SimpleNamespace:
        response = requests.get(
            LINE_ROOM_MEMBER_PROFILE_URL.format(room_id=room_id, user_id=user_id),
            headers=self.headers,
            timeout=20,
        )
        response.raise_for_status()
        return self._profile_from_response(response, user_id)

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

    def _with_sender(self, messages: list[dict[str, Any]], chat_id: str | None) -> list[dict[str, Any]]:
        sender = group_sender(chat_id or "")
        if not sender:
            return messages
        patched = []
        for message in messages:
            if not isinstance(message, dict):
                patched.append(message)
                continue
            item = dict(message)
            item.setdefault("sender", sender)
            patched.append(item)
        return patched

    def _profile_from_response(self, response, user_id: str) -> SimpleNamespace:
        data = response.json()
        return SimpleNamespace(
            mid=user_id,
            userId=user_id,
            displayName=data.get("displayName", user_id),
            pictureStatus=data.get("pictureUrl", ""),
            pictureUrl=data.get("pictureUrl", ""),
        )


def text_message(text: str) -> dict[str, str]:
    return {"type": "text", "text": str(text)[:5000]}


def normalize_template(template: Any) -> dict[str, Any]:
    if isinstance(template, dict):
        if template.get("type") in {"flex", "text", "image", "video"}:
            return template
        return {"type": "flex", "altText": template.get("altText", "Chino Bot"), "contents": template}
    return text_message(str(template))
