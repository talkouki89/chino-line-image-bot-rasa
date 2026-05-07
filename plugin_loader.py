import importlib.util
import traceback
from pathlib import Path
from types import SimpleNamespace

from plugins.core.features import FEATURE_INDEX


DISABLED_COMMANDS = {
    "help_templates": {
        "exact": {"圖搜說明", "說明", "help", "功能說明", "指令", "指令說明", "功能狀態", "狀態", "功能設定", "功能開關"},
        "prefixes": ("功能切換 ",),
    },
    "image_search": {
        "exact": {
            "回覆搜圖", "回覆搜1", "回覆搜2", "回覆搜3", "回覆搜4", "回覆搜5", "回覆搜6", "回覆搜7",
            "模板搜", "模板搜1", "模板搜2", "模板搜3", "#1", "#2", "#3",
        },
    },
    "x_download": {"exact": {"回覆搜x"}, "prefixes": ("x:", "X:")},
    "ytdlp_download": {"exact": {"回覆搜yt"}, "prefixes": ("yt:", "YT:")},
    "facebook_download": {"exact": {"回覆搜fb"}, "prefixes": ("fb:", "FB:")},
    "pornhub_download": {"exact": {"回覆搜ph"}, "prefixes": ("ph:", "PH:")},
    "instagram_download": {"exact": {"回覆搜ig"}, "prefixes": ("ig:", "IG:")},
    "tiktok_download": {"prefixes": ("tk:", "TK:")},
    "admin_profile_tools": {
        "exact": {"mymid", "myid", "我是誰", "gid", "群組id", "機器人一覽", "botinfo", "bot info", "bot狀態", "bot 狀態", "speedtest", "測速", "版本檢查", "檢查更新", "版本更新", "reb", "reb@bot", "reb @bot", "重啟bot", "重啟 bot", "重啟機器人"},
        "prefixes": ("mid:", "contact "),
    },
    "runtime_tools": {"exact": {"ren"}},
    "image_draw_template": {
        "exact": {"抽圖", "抽圖片", "抽色圖", "抽圖模板", "抽圖說明", "抽圖功能", "隨機圖", "隨機色圖", "一般抽圖", "一般色圖", "色圖", "r18色圖", "R18色圖"},
        "prefixes": ("tag色圖", "色圖tag", "找色圖", "標籤抽圖"),
    },
    "freeimage_upload": {"exact": {"#圖片上傳"}},
    "nhentai": {"exact": {"n:popular"}, "prefixes": ("n:", "N:")},
    "wnacg": {"prefixes": ("w:", "W:")},
    "jmcomic": {"prefixes": ("c:", "C:")},
    "pixiv": {"prefixes": ("p:", "P:")},
    "group_settings": {
        "exact": {"查看歡迎訊息", "歡迎訊息", "清除歡迎訊息", "查看機器人外觀", "機器人外觀", "清除機器人外觀"},
        "prefixes": ("設定歡迎訊息 ", "設定機器人名稱 ", "設定機器人頭像 "),
    },
}


class PluginManager:
    def __init__(self, plugin_dir, enabled=True):
        self.plugin_dir = Path(plugin_dir)
        self.enabled = enabled
        self.modules = {}
        self.mtimes = {}
        self.errors = {}
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

    def dispatch(self, context):
        if not self.enabled:
            return False
        handled = False
        for path in sorted(self.plugin_dir.glob("*.py")):
            if path.name.startswith("_"):
                continue
            module = self._load_if_changed(path)
            if module is None or not hasattr(module, "handle"):
                if path.name in self.errors:
                    context.log_error(f"{path.name}\n{self.errors[path.name]}")
                continue
            feature_key = getattr(module, "FEATURE_KEY", None)
            is_feature_enabled = getattr(context, "is_feature_enabled", None)
            if feature_key and is_feature_enabled and not is_feature_enabled(feature_key):
                if disabled_command_matches(feature_key, getattr(context, "cmd", "")):
                    context.reply(f"{feature_name(feature_key)} 目前已被管理員關閉。")
                    handled = True
                    break
                continue
            try:
                if module.handle(context):
                    handled = True
                    break
            except Exception:
                self.errors[path.name] = traceback.format_exc()
                context.log_error(self.errors[path.name])
        return handled

    def _load_if_changed(self, path):
        mtime = path.stat().st_mtime
        cached = self.modules.get(path)
        if cached is not None and self.mtimes.get(path) == mtime:
            return cached

        module_name = f"bot_plugin_{path.stem}_{int(mtime * 1000)}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:
            self.errors[path.name] = traceback.format_exc()
            return None

        self.modules[path] = module
        self.mtimes[path] = mtime
        self.errors.pop(path.name, None)
        return module


def make_context(**kwargs):
    return SimpleNamespace(**kwargs)


def disabled_command_matches(feature_key, command):
    config = DISABLED_COMMANDS.get(feature_key)
    if not config:
        return False
    command = str(command or "").strip()
    lowered = command.lower()
    exact = {str(item).lower() for item in config.get("exact", set())}
    if lowered in exact:
        return True
    return any(lowered.startswith(prefix.lower()) for prefix in config.get("prefixes", ()))


def feature_name(feature_key):
    return FEATURE_INDEX.get(feature_key, {}).get("name") or feature_key
