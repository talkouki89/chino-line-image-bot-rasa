from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

from chino_rasa.settings import ROOT_DIR


def schedule_restart() -> tuple[bool, str]:
    if platform.system().lower().startswith("win"):
        return schedule_windows_restart()
    return schedule_unix_restart()


def schedule_windows_restart() -> tuple[bool, str]:
    script = ROOT_DIR / "scripts" / "start_rasa_server.ps1"
    if not script.exists():
        return False, "找不到 scripts/start_rasa_server.ps1，無法自動重啟。"
    command = (
        "Start-Sleep -Seconds 2; "
        f"Stop-Process -Id {os.getpid()} -Force -ErrorAction SilentlyContinue; "
        "Start-Sleep -Seconds 1; "
        "Start-Process powershell.exe -WindowStyle Hidden "
        f"-ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File','{script}'"
    )
    subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=str(ROOT_DIR),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return True, "已排程重啟 Rasa server。"


def schedule_unix_restart() -> tuple[bool, str]:
    service = os.getenv("RASA_SYSTEMD_SERVICE", "").strip()
    if service:
        subprocess.Popen(["sh", "-c", f"sleep 2; systemctl restart {service}"], cwd=str(ROOT_DIR))
        return True, f"已排程 systemctl restart {service}。"
    script = ROOT_DIR / "scripts" / "start_rasa_server.sh"
    if script.exists():
        subprocess.Popen(["sh", "-c", f"sleep 2; kill {os.getpid()}; nohup '{script}' >/dev/null 2>&1 &"], cwd=str(ROOT_DIR))
        return True, "已排程使用 scripts/start_rasa_server.sh 重啟。"
    return False, "Linux/VPS 未設定 RASA_SYSTEMD_SERVICE，也找不到 scripts/start_rasa_server.sh，請手動重啟。"


def repo_root() -> Path:
    return ROOT_DIR
