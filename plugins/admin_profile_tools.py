import re
import subprocess
import sys
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from chino_rasa.store import bot_chat_counts
from chino_rasa.version import current_version

FEATURE_KEY = "admin_profile_tools"
MID_RE = re.compile(r"^mid:([A-Za-z0-9_-]+)$", re.IGNORECASE)
FALLBACK_IMAGE = "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png"


def handle(ctx):
    command = ctx.cmd.strip()
    command_lower = command.lower()
    if command_lower in {"機器人一覽", "botinfo", "bot info", "bot狀態", "bot 狀態"}:
        if not ctx.is_admin:
            ctx.reply("此功能只有管理員可以使用。")
            return True
        return handle_bot_overview(ctx)
    if command_lower in {"gid", "群組id"}:
        if not ctx.is_admin:
            ctx.reply("此功能只有管理員可以使用。")
            return True
        ctx.reply(f"目前聊天室 ID：{ctx.to or '未提供'}")
        return True
    if command_lower in {"speedtest", "測速"}:
        if not ctx.is_admin:
            ctx.reply("此功能只有管理員可以使用。")
            return True
        threading.Thread(target=run_speedtest, args=(ctx,), daemon=True).start()
        return True
    if command_lower.startswith("mid:"):
        if not ctx.is_admin:
            ctx.reply("此功能只有管理員可以使用。")
            return True
        return handle_mid_lookup(ctx)
    return False


def handle_bot_overview(ctx):
    counts = bot_chat_counts()
    follower_date = insight_date()
    lines = [
        "機器人一覽",
        f"目前版本：{current_version()}",
        f"好友數量：{followers_text(ctx, follower_date)}",
        f"群組數量：{counts['groups']} 個",
        f"多人聊天室數量：{counts['rooms']} 個",
        f"私聊用戶記錄：{counts['users']} 個",
    ]
    member_total, failed = observed_group_member_total(ctx, counts)
    if member_total is not None:
        lines.append(f"已知群組成員合計：{member_total} 人")
    if failed:
        lines.append(f"有 {failed} 個聊天室無法取得成員數。")
    lines.extend([
        "",
        "好友數來自 LINE 官方 Insights，通常是前一天資料。",
        "群組數是本機 webhook 已看過的群組，LINE 官方 API 不提供全域群組清單。",
    ])
    ctx.reply("\n".join(lines))
    return True


def insight_date():
    return (datetime.now(ZoneInfo("Asia/Tokyo")) - timedelta(days=1)).strftime("%Y%m%d")


def followers_text(ctx, date):
    try:
        data = ctx.cl.get_followers(date)
    except Exception as exc:
        ctx.log_error(exc)
        return f"讀取失敗（查詢日期 {date}）"
    if data.status and data.status != "ready":
        return f"尚未準備完成（status={data.status}, 查詢日期 {date}）"
    value = data.followers
    if value is None:
        return f"無資料（查詢日期 {date}）"
    return f"{value} 人（{date}）"


def observed_group_member_total(ctx, counts):
    total = 0
    failed = 0
    found = False
    for group_id in counts.get("group_ids", []):
        try:
            total += ctx.cl.get_group_member_count(group_id)
            found = True
        except Exception as exc:
            ctx.log_error(exc)
            failed += 1
    for room_id in counts.get("room_ids", []):
        try:
            total += ctx.cl.get_room_member_count(room_id)
            found = True
        except Exception as exc:
            ctx.log_error(exc)
            failed += 1
    return (total if found else None), failed


def handle_mid_lookup(ctx):
    match = MID_RE.match(ctx.text.strip())
    if not match:
        ctx.reply("請輸入 MID，範例：mid:u1234567890")
        return True
    send_profile_template(ctx, match.group(1))
    return True


def send_profile_template(ctx, mid):
    try:
        profile = ctx.cl.getContact(mid)
        ctx.send_template(ctx.to, build_profile_template(ctx, profile, mid))
    except Exception as exc:
        ctx.log_error(exc)
        ctx.reply("好友資料查詢失敗，請確認 userId 是否正確。")


def build_profile_template(ctx, profile, mid):
    name = value(profile, "displayName", "name", default="未知")
    status = value(profile, "statusMessage", default="未設定")
    picture = profile_image_url(profile)
    cover = profile_cover_url(ctx, mid) or picture
    return {
        "type": "flex",
        "altText": f"{name} 的好友資料",
        "contents": {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": cover or FALLBACK_IMAGE,
                "size": "full",
                "aspectRatio": "20:9",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "paddingAll": "18px",
                "contents": [
                    {"type": "text", "text": name, "weight": "bold", "size": "xl", "wrap": True, "color": "#111827"},
                    {"type": "text", "text": status or "未設定狀態消息", "size": "sm", "wrap": True, "color": "#6b7280"},
                    {"type": "separator"},
                    row("MID", mid),
                    row("名稱", name),
                    row("狀態消息", status or "未設定"),
                    row("頭貼", picture or "無"),
                    row("封面", cover or "無"),
                ],
            },
        },
    }


def row(label, text):
    return {
        "type": "box",
        "layout": "vertical",
        "spacing": "xs",
        "contents": [
            {"type": "text", "text": label, "size": "xs", "color": "#6b7280"},
            {"type": "text", "text": str(text), "size": "sm", "wrap": True, "color": "#111827"},
        ],
    }


def run_speedtest(ctx):
    try:
        result = subprocess.run(
            [sys.executable, "-m", "speedtest", "--share", "--simple"],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        output = (result.stdout or "") + "\n" + (result.stderr or "")
        image_url = find_speedtest_image(output)
        if image_url:
            ctx.reply([
                {"type": "image", "originalContentUrl": image_url, "previewImageUrl": image_url},
                {"type": "text", "text": cleanup_speedtest_text(output)[:5000]},
            ])
            return
        ctx.reply("測速失敗，無法取得結果圖片。\n請確認已安裝 speedtest-cli。")
    except Exception as exc:
        ctx.log_error(exc)
        ctx.reply("測速失敗，請稍後再試。")


def find_speedtest_image(output):
    for token in str(output).split():
        if "speedtest.net/result/" in token:
            token = token.strip()
            if not token.endswith(".png"):
                token = token.rstrip("/") + ".png"
            return token.replace("http://", "https://")
    return ""


def cleanup_speedtest_text(output):
    lines = [line.strip() for line in str(output).splitlines() if line.strip()]
    return "\n".join(lines[:8]) or "測速完成。"


def value(obj, *names, default=""):
    for name in names:
        try:
            data = getattr(obj, name)
        except Exception:
            data = None
        if data:
            return data
    return default


def profile_image_url(contact):
    thumbnail = value(contact, "thumbnailUrl", default="")
    if thumbnail:
        return str(thumbnail).replace("http://", "https://")
    picture_status = value(contact, "pictureStatus", default="")
    if picture_status:
        return f"https://dl.profile.line-cdn.net/{picture_status}"
    return FALLBACK_IMAGE


def profile_cover_url(ctx, mid):
    try:
        data = ctx.cl.getProfileCoverObjIdAndUrl(mid)
        if isinstance(data, (list, tuple)) and data:
            url = data[0]
            if url:
                return str(url).replace("http://", "https://")
    except Exception:
        return ""
    return ""
