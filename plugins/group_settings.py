FEATURE_KEY = "group_settings"

from urllib.parse import urlparse

from chino_rasa.store import group_settings, update_group_settings


def handle(ctx):
    command = ctx.cmd.strip()
    if command.startswith("設定歡迎訊息 "):
        if not require_group_chat(ctx):
            return True
        message = command.split(" ", 1)[1].strip()
        if not message:
            ctx.reply("請輸入歡迎訊息內容。")
            return True
        update_group_settings(ctx.to, welcome_message=message)
        ctx.reply("已設定目前群組的歡迎訊息。可使用 {UserName} 與 {GroupName}。")
        return True
    if command in {"查看歡迎訊息", "歡迎訊息"}:
        if not require_group_chat(ctx):
            return True
        message = group_settings(ctx.to).get("welcome_message")
        ctx.reply(f"目前歡迎訊息：\n{message}" if message else "目前群組尚未設定歡迎訊息。")
        return True
    if command == "清除歡迎訊息":
        if not require_group_chat(ctx):
            return True
        update_group_settings(ctx.to, welcome_message=None)
        ctx.reply("已清除目前群組的歡迎訊息。")
        return True
    if command.startswith("設定機器人名稱 "):
        if not require_group_admin(ctx):
            return True
        name = command.split(" ", 1)[1].strip()
        if not name:
            ctx.reply("請輸入名稱。")
            return True
        update_group_settings(ctx.to, bot_name=name[:20])
        ctx.reply(f"已設定目前群組的機器人訊息名稱：{name[:20]}")
        return True
    if command.startswith("設定機器人頭像 "):
        if not require_group_admin(ctx):
            return True
        icon_url = command.split(" ", 1)[1].strip()
        if not is_https_url(icon_url):
            ctx.reply("請輸入 https 圖片網址。")
            return True
        update_group_settings(ctx.to, bot_icon_url=icon_url)
        ctx.reply("已設定目前群組的機器人訊息頭像。")
        return True
    if command in {"查看機器人外觀", "機器人外觀"}:
        if not require_group_admin(ctx):
            return True
        settings = group_settings(ctx.to)
        name = settings.get("bot_name") or "未設定"
        icon_url = settings.get("bot_icon_url") or "未設定"
        ctx.reply(f"目前群組機器人外觀：\n名稱：{name}\n頭像：{icon_url}")
        return True
    if command == "清除機器人外觀":
        if not require_group_admin(ctx):
            return True
        update_group_settings(ctx.to, bot_name=None, bot_icon_url=None)
        ctx.reply("已清除目前群組的機器人訊息名稱與頭像。")
        return True
    return False


def require_group_admin(ctx):
    if not require_group_chat(ctx):
        return False
    if not (getattr(ctx, "is_admin", False) or getattr(ctx, "is_creator", False)):
        ctx.reply("此功能只有管理員可以使用。")
        return False
    return True


def require_group_chat(ctx):
    if getattr(ctx, "to", "") == getattr(ctx, "sender", ""):
        ctx.reply("此設定只能在群組或多人聊天室使用。")
        return False
    return True


def is_https_url(value):
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)
