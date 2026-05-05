FEATURE_KEY = "admin_profile_tools"

import subprocess
from pathlib import Path

from chino_rasa.restart import repo_root, schedule_restart
from plugins.core.help_template import build_version_check_flex


VERSION_FILE = repo_root() / "VERSION"


def handle(ctx):
    command = ctx.cmd.strip()
    if command not in {"版本檢查", "檢查更新", "版本更新"}:
        return False
    if not (getattr(ctx, "is_admin", False) or getattr(ctx, "is_creator", False)):
        ctx.reply("此功能只有管理員可以使用。")
        return True
    if command == "版本更新":
        return handle_update(ctx)
    return handle_check(ctx)


def handle_check(ctx):
    local_version = read_version(VERSION_FILE)
    try:
        git("fetch", "origin", "main")
        local_head = git_text("rev-parse", "--short", "HEAD")
        remote_head = git_text("rev-parse", "--short", "origin/main")
        remote_version = f"{read_remote_version()} ({remote_head})"
        local_display = f"{local_version} ({local_head})"
        prs = [{"number": "-", "title": line} for line in git_lines("log", "--oneline", "--max-count=5", "HEAD..origin/main")]
        ctx.reply(build_version_check_flex(local_display, remote_version=remote_version, prs=prs))
    except Exception as exc:
        ctx.log_error(exc)
        ctx.reply(build_version_check_flex(local_version, error=str(exc)))
    return True


def handle_update(ctx):
    try:
        git("fetch", "origin", "main")
        local_head = git_text("rev-parse", "HEAD")
        remote_head = git_text("rev-parse", "origin/main")
        if local_head == remote_head:
            ctx.reply("目前已是最新版本，不需要更新。")
            return True
        output = git_text("pull", "--ff-only", "origin", "main")
        ok, restart_message = schedule_restart()
        ctx.reply("版本更新完成，正在重啟。\n\n" + output[-3000:] + "\n\n" + restart_message)
    except Exception as exc:
        ctx.log_error(exc)
        ctx.reply(f"版本更新失敗：{exc}")
    return True


def read_version(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip() or "unknown"
    except OSError:
        return "unknown"


def read_remote_version() -> str:
    try:
        return git_text("show", "origin/main:VERSION")
    except Exception:
        return "unknown"


def git(*args):
    return subprocess.run(["git", *args], cwd=repo_root(), text=True, capture_output=True, timeout=120, check=True)


def git_text(*args) -> str:
    result = git(*args)
    return (result.stdout or result.stderr or "").strip()


def git_lines(*args) -> list[str]:
    return [line.strip() for line in git_text(*args).splitlines() if line.strip()]
