import json
import os


FEATURE_DEFINITIONS = [
    {
        "key": "help_templates",
        "name": "說明模板",
        "description": "圖搜說明、功能狀態、功能設定等 Flex 模板。",
        "commands": "圖搜說明 / 功能狀態 / 功能設定",
    },
    {
        "key": "image_search",
        "name": "圖片搜尋總開關",
        "description": "控制所有回覆圖片搜尋與模板搜尋入口。",
        "commands": "回覆搜圖 / 模板搜 / #1 / #2 / #3",
    },
    {
        "key": "engine_saucenao",
        "name": "SauceNAO",
        "description": "使用 SauceNAO 做圖片來源搜尋。",
        "commands": "回覆搜圖 / 回覆搜1 / 模板搜1 / #1",
    },
    {
        "key": "engine_ascii2d",
        "name": "Ascii2D",
        "description": "使用 Ascii2D 搜尋二次元圖片來源。",
        "commands": "回覆搜2 / 模板搜2 / #2",
    },
    {
        "key": "engine_tracemoe",
        "name": "TraceMoe",
        "description": "使用 TraceMoe 辨識動畫截圖。",
        "commands": "回覆搜3 / 模板搜3 / #3",
    },
    {
        "key": "engine_yandex",
        "name": "Yandex",
        "description": "使用 Yandex 圖搜作為補充搜尋來源。",
        "commands": "回覆搜4",
    },
    {
        "key": "engine_iqdb",
        "name": "Iqdb",
        "description": "使用 Iqdb 搜尋圖片來源。",
        "commands": "回覆搜5",
    },
    {
        "key": "engine_animetrace",
        "name": "AnimeTrace",
        "description": "使用 AnimeTrace 辨識動畫或作品。",
        "commands": "回覆搜6",
    },
    {
        "key": "engine_ggjav",
        "name": "GGJAV",
        "description": "使用 GGJAV 做指定類型的網頁圖搜輔助。",
        "commands": "回覆搜7",
    },
    {
        "key": "x_download",
        "name": "X / Twitter 下載",
        "description": "解析並下載 X / Twitter 圖片或影片。",
        "commands": "x:URL / 回覆搜x",
    },
    {
        "key": "ytdlp_download",
        "name": "yt-dlp 下載",
        "description": "使用 yt-dlp 下載支援站台的影片。",
        "commands": "yt:URL / 回覆搜yt",
    },
    {
        "key": "facebook_download",
        "name": "Facebook 下載",
        "description": "下載 Facebook 影片。",
        "commands": "fb:URL / 回覆搜fb",
    },
    {
        "key": "pornhub_download",
        "name": "Pornhub 下載",
        "description": "下載 Pornhub 影片。",
        "commands": "ph:URL / 回覆搜ph",
    },
    {
        "key": "instagram_download",
        "name": "Instagram 下載",
        "description": "下載 Instagram 圖片或影片。",
        "commands": "ig:URL / 回覆搜ig",
    },
    {
        "key": "tiktok_download",
        "name": "TikTok 下載",
        "description": "下載 TikTok 圖片或影片。",
        "commands": "tk:URL",
    },
    {
        "key": "admin_profile_tools",
        "name": "管理員資料工具",
        "description": "查詢 MID、聯絡人資料、群組 ID 與 speedtest。",
        "commands": "mymid / gid / mid:MID / Contact @使用者 / speedtest",
    },
    {
        "key": "runtime_tools",
        "name": "運行時間模板",
        "description": "顯示 Bot 已運行時間。",
        "commands": "ren",
    },
    {
        "key": "mention_tools",
        "name": "標註工具",
        "description": "查詢誰標註我，或清空目前標註紀錄。",
        "commands": "誰標我 / 清空標註",
    },
    {
        "key": "image_draw_template",
        "name": "抽圖模板",
        "description": "Lolicon API 抽圖、R18 抽圖、標籤抽圖與常用標籤模板。",
        "commands": "抽圖 / 色圖 / r18色圖 / tag色圖 標籤",
    },
    {
        "key": "freeimage_upload",
        "name": "圖片上傳",
        "description": "回覆圖片後上傳至 Freeimage.host。",
        "commands": "#圖片上傳",
    },
    {
        "key": "nhentai",
        "name": "nHentai",
        "description": "nHentai 編號解析與 Popular Now。",
        "commands": "n:編號 / n:popular",
    },
    {
        "key": "wnacg",
        "name": "紳士漫畫",
        "description": "wnacg 編號解析。",
        "commands": "w:編號",
    },
    {
        "key": "jmcomic",
        "name": "禁漫天堂",
        "description": "禁漫天堂編號解析。",
        "commands": "c:編號",
    },
    {
        "key": "pixiv",
        "name": "Pixiv",
        "description": "Pixiv 作品解析。",
        "commands": "p:作品ID / p:URL",
    },
    {
        "key": "group_settings",
        "name": "群組設定",
        "description": "群組歡迎訊息與群組專用發話名稱/頭像。",
        "commands": "設定歡迎訊息 / 清除歡迎訊息 / 設定機器人名稱 / 設定機器人頭像",
    },
    {
        "key": "auto_friend",
        "name": "自動好友訊息",
        "description": "加入好友時的自動回覆訊息。",
        "commands": "AUTO_FRIEND_MESSAGE",
    },
    {
        "key": "group_min_member_check",
        "name": "群組最低人數檢查",
        "description": "限制 Bot 只在達到最低人數的群組內運作。",
        "commands": "GROUP_MIN_MEMBER_CHECK / GROUP_MIN_MEMBERS",
    },
    {
        "key": "search_quota",
        "name": "圖搜次數限制",
        "description": "限制一般使用者每日圖片搜尋次數；管理員不扣次數。",
        "commands": "回覆搜圖 / 模板搜",
    },
    {
        "key": "announcement_notify",
        "name": "公告通知",
        "description": "保留給公告/更新通知使用。",
        "commands": "公告通知",
        "default": False,
    },
]


DEFAULT_FEATURES = {item["key"]: item.get("default", True) for item in FEATURE_DEFINITIONS}
FEATURE_INDEX = {item["key"]: item for item in FEATURE_DEFINITIONS}


def load_feature_flags(path):
    data = DEFAULT_FEATURES.copy()
    try:
        with open(path, "r", encoding="utf-8") as fp:
            raw = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        save_feature_flags(path, data)
        return data
    if isinstance(raw, dict):
        for key, value in raw.items():
            if key in data:
                data[key] = bool(value)
    if data != raw:
        save_feature_flags(path, data)
    return data


def save_feature_flags(path, flags):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(flags, fp, sort_keys=True, indent=4, ensure_ascii=False)


def is_enabled(flags, key, default=True):
    if not key:
        return default
    return bool(flags.get(key, default))


def set_enabled(path, flags, key, enabled):
    if key not in FEATURE_INDEX:
        raise KeyError(key)
    flags[key] = bool(enabled)
    save_feature_flags(path, flags)
    return flags[key]


def toggle_feature(path, flags, key):
    return set_enabled(path, flags, key, not is_enabled(flags, key))
