FEATURE_KEY = "admin_profile_tools"

import subprocess
from pathlib import Path

from chino_rasa.restart import repo_root, schedule_restart
from chino_rasa.version import VERSION_FILE, current_version
from plugins.core.help_template import build_version_check_flex


REMOTE_NAME = "origin"
REMOTE_BRANCH = "main"


class GitCommandError(RuntimeError):
    def __init__(self, args, returncode, stdout="", stderr=""):
        self.args_list = list(args)
        self.returncode = returncode
        self.stdout = (stdout or "").strip()
        self.stderr = (stderr or "").strip()
        super().__init__(format_git_error(self.args_list, returncode, self.stdout, self.stderr))


def handle(ctx):
    command = ctx.cmd.strip()
    command_lower = command.lower()
    if command_lower in {"版本", "version", "bot版本", "bot 版本"}:
        ctx.reply(f"目前版本：{current_version()}")
        return True
    if command_lower not in {"版本檢查", "檢查更新", "版本更新"}:
        return False
    if not (getattr(ctx, "is_admin", False) or getattr(ctx, "is_creator", False)):
        ctx.reply("此功能只有管理員可以使用。")
        return True
    if command_lower == "版本更新":
        return handle_update(ctx)
    return handle_check(ctx)


def handle_check(ctx):
    local_version = current_version()
    try:
        ensure_git_repo()
        git("fetch", REMOTE_NAME, REMOTE_BRANCH)
        local_head = git_text("rev-parse", "--short", "HEAD")
        remote_head = git_text("rev-parse", "--short", remote_ref())
        remote_version = f"{read_remote_version()} ({remote_head})"
        local_display = f"{local_version} ({local_head})"
        prs = [{"number": "-", "title": line} for line in git_lines("log", "--oneline", "--max-count=5", f"HEAD..{remote_ref()}")]
        ctx.reply(build_version_check_flex(local_display, remote_version=remote_version, prs=prs))
    except Exception as exc:
        ctx.log_error(exc)
        ctx.reply(build_version_check_flex(local_version, error=user_facing_error(exc)))
    return True


def handle_update(ctx):
    try:
        ensure_git_repo()
        git("fetch", REMOTE_NAME, REMOTE_BRANCH)
        local_head = git_text("rev-parse", "HEAD")
        remote_head = git_text("rev-parse", remote_ref())
        if local_head == remote_head:
            ctx.reply("目前已是最新版本，不需要更新。")
            return True
        output = git_text("pull", "--ff-only", REMOTE_NAME, REMOTE_BRANCH)
        ok, restart_message = schedule_restart()
        ctx.reply("版本更新完成，正在重啟。\n\n" + output[-3000:] + "\n\n" + restart_message)
    except Exception as exc:
        ctx.log_error(exc)
        ctx.reply(f"版本更新失敗：\n{user_facing_error(exc)}")
    return True


def read_version(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip() or "unknown"
    except OSError:
        return "unknown"


def read_remote_version() -> str:
    try:
        return git_text("show", f"{remote_ref()}:VERSION")
    except Exception:
        return "unknown"


def git(*args):
    command = ["git", *args]
    result = subprocess.run(command, cwd=repo_root(), text=True, capture_output=True, timeout=120, check=False)
    if result.returncode:
        raise GitCommandError(command, result.returncode, result.stdout, result.stderr)
    return result


def git_text(*args) -> str:
    result = git(*args)
    return (result.stdout or result.stderr or "").strip()


def git_lines(*args) -> list[str]:
    return [line.strip() for line in git_text(*args).splitlines() if line.strip()]


def ensure_git_repo():
    root = repo_root()
    if not (root / ".git").exists():
        raise RuntimeError(
            "目前部署目錄不是 Git repository，找不到 .git。\n"
            "VPS 請用 git clone 部署，或在專案目錄重新設定 origin 後再使用版本更新。"
        )
    git("rev-parse", "--is-inside-work-tree")
    remotes = git_text("remote").splitlines()
    if REMOTE_NAME not in {item.strip() for item in remotes}:
        raise RuntimeError(f"找不到 git remote `{REMOTE_NAME}`，請先設定：git remote add {REMOTE_NAME} <repo-url>")


def remote_ref():
    return f"{REMOTE_NAME}/{REMOTE_BRANCH}"


def format_git_error(args, returncode, stdout="", stderr=""):
    detail = stderr or stdout or "Git 沒有輸出錯誤內容。"
    command = " ".join(args)
    hint = git_error_hint(detail)
    parts = [
        f"Git 指令失敗（exit {returncode}）：{command}",
        detail[-2500:],
    ]
    if hint:
        parts.append(hint)
    return "\n".join(parts)


def git_error_hint(detail):
    text = str(detail or "").lower()
    if "dubious ownership" in text or "safe.directory" in text:
        return "修正方式：在 VPS 專案目錄執行 `git config --global --add safe.directory <專案絕對路徑>`。"
    if "not a git repository" in text:
        return "修正方式：VPS 請用 `git clone https://github.com/talkouki89/chino-line-image-bot-rasa.git` 部署，不要只上傳壓縮檔。"
    if "could not read username" in text or "authentication failed" in text or "permission denied" in text:
        return "修正方式：確認 remote URL 可讀取。公開 repo 可改用 HTTPS：`git remote set-url origin https://github.com/talkouki89/chino-line-image-bot-rasa.git`。"
    if "could not resolve host" in text or "failed to connect" in text:
        return "修正方式：確認 VPS 可以連線 GitHub，並檢查 DNS、防火牆或代理設定。"
    if "couldn't find remote ref" in text:
        return f"修正方式：確認遠端分支 `{REMOTE_BRANCH}` 存在，或調整版本更新使用的分支。"
    return ""


def user_facing_error(exc):
    return str(exc)[:4500]
