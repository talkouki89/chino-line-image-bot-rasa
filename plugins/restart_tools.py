FEATURE_KEY = "admin_profile_tools"

from chino_rasa.restart import schedule_restart


COMMANDS = {"reb", "reb@bot", "reb @bot", "重啟bot", "重啟 bot", "重啟機器人"}


def handle(ctx):
    command = ctx.cmd.strip().lower().replace("　", " ")
    if command not in COMMANDS:
        return False
    if not (getattr(ctx, "is_admin", False) or getattr(ctx, "is_creator", False)):
        ctx.reply("此功能只有管理員可以使用。")
        return True
    ok, message = schedule_restart()
    ctx.reply(message if ok else f"重啟失敗：{message}")
    return True
