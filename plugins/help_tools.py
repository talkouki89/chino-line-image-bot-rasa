from chino_rasa.store import FEATURE_PATH
from plugins.core.features import FEATURE_INDEX, load_feature_flags, toggle_feature
from plugins.core.help_template import build_help_flex, build_settings_flex, build_status_flex


HELP_COMMANDS = {"圖搜說明", "說明", "help", "功能說明", "指令", "指令說明"}
STATUS_COMMANDS = {"功能狀態", "狀態"}
SETTINGS_COMMANDS = {"功能設定", "功能開關"}


def handle(ctx):
    command = ctx.cmd.strip()
    flags = load_feature_flags(str(FEATURE_PATH))
    if command in HELP_COMMANDS:
        ctx.reply(build_help_flex(flags, is_admin=ctx.is_admin, is_creator=ctx.is_creator))
        return True
    if command in STATUS_COMMANDS:
        ctx.reply(build_status_flex(flags))
        return True
    if command in SETTINGS_COMMANDS:
        if not can_admin(ctx):
            ctx.reply("此功能只有管理員可以使用。")
            return True
        ctx.reply(build_settings_flex(flags))
        return True
    if command.startswith("功能切換 "):
        if not can_admin(ctx):
            ctx.reply("此功能只有管理員可以使用。")
            return True
        key = command.split(maxsplit=1)[1].strip()
        if key not in FEATURE_INDEX:
            ctx.reply(f"找不到功能 key：{key}")
            return True
        enabled = toggle_feature(str(FEATURE_PATH), flags, key)
        state = "開啟" if enabled else "關閉"
        ctx.reply(f"{FEATURE_INDEX[key]['name']} 已切換為：{state}")
        return True
    return False


def can_admin(ctx):
    return bool(getattr(ctx, "is_admin", False) or getattr(ctx, "is_creator", False))
