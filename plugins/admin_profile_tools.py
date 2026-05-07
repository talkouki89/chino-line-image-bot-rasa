import ast
import subprocess
import sys
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from chino_rasa.store import bot_chat_counts
from chino_rasa.version import current_version

FEATURE_KEY = "admin_profile_tools"


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
    if command_lower.startswith("mid "):
        if not ctx.is_admin:
            ctx.reply("此功能只有管理員可以使用。")
            return True
        return handle_mid_mentions(ctx)
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


def handle_mid_mentions(ctx):
    mids = parse_mention_user_ids(getattr(ctx.msg, "contentMetadata", None))
    if not mids:
        ctx.reply("請標註要查詢的人，範例：mid @使用者")
        return True
    lines = ["標註對象 MID"]
    for index, mid in enumerate(mids, start=1):
        lines.append(f"{index}. {mid}")
    ctx.reply("\n".join(lines))
    return True


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


def parse_mention_user_ids(content_metadata):
    if not isinstance(content_metadata, dict):
        return []
    mids = []
    mention = content_metadata.get("mention") or {}
    for item in mention.get("mentionees") or []:
        user_id = item.get("userId")
        if user_id:
            mids.append(user_id)
    old_format = content_metadata.get("MENTION")
    if old_format:
        try:
            parsed = ast.literal_eval(old_format)
        except Exception:
            parsed = {}
        for item in parsed.get("MENTIONEES", []):
            user_id = item.get("M")
            if user_id:
                mids.append(user_id)
    return list(dict.fromkeys(mids))
