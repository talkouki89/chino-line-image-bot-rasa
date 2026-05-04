from urllib.parse import urlencode

from plugins.core.features import FEATURE_DEFINITIONS, FEATURE_INDEX, is_enabled


GITHUB_URL = "https://github.com/talkouki89/chino-line-image-bot-rasa"
GITHUB_PULLS_URL = "https://github.com/talkouki89/chino-line-image-bot-rasa/pulls?q=is%3Apr+is%3Amerged"

IMAGE_ENGINE_KEYS = [
    "image_search",
    "engine_saucenao",
    "engine_ascii2d",
    "engine_tracemoe",
    "engine_yandex",
    "engine_iqdb",
    "engine_animetrace",
    "engine_ggjav",
]

OTHER_FEATURE_KEYS = [
    "x_download",
    "ytdlp_download",
    "facebook_download",
    "pornhub_download",
    "instagram_download",
    "tiktok_download",
    "image_draw_template",
    "freeimage_upload",
    "nhentai",
    "wnacg",
    "jmcomic",
    "pixiv",
    "runtime_tools",
    "mention_tools",
    "group_settings",
    "search_quota",
]

ADMIN_FEATURE_KEYS = [
    "help_templates",
    "admin_profile_tools",
    "broadcast",
    "auto_friend",
    "group_min_member_check",
    "announcement_notify",
]


def build_help_flex(flags, is_admin=False, is_creator=False):
    role = "creator" if is_creator else "admin" if is_admin else "user"
    bubbles = [
        help_public_bubble(),
        help_search_bubble(),
        help_download_bubble(),
        help_gallery_bubble(),
    ]
    if role in {"admin", "creator"}:
        bubbles.append(help_admin_bubble(flags))
    if role == "creator":
        bubbles.append(help_creator_bubble(flags))
    return flex("ChinoBot 圖搜說明", bubbles)


def build_help_text(flags=None, is_admin=False, is_creator=False):
    lines = [
        "圖搜說明",
        "回覆圖片後輸入：回覆搜圖 / 回覆搜1 / 回覆搜2 / 回覆搜3",
        "模板搜尋：模板搜 / 模板搜1 / 模板搜2 / 模板搜3",
        "快捷：#1 / #2 / #3",
        "下載：yt:URL / fb:URL / ig:URL / tk:URL / x:URL / ph:URL",
        "抽圖：抽圖 / 色圖 / r18色圖 / tag色圖 標籤",
        "解析：n:編號 / n:popular / w:編號 / c:編號 / p:URL",
        "其他：#圖片上傳 / 誰標我 / 清空標註 / ren",
    ]
    if is_admin or is_creator:
        lines.extend([
            "",
            "管理員：功能狀態 / 功能設定 / 功能切換 <key>",
            "群組：設定歡迎訊息 / 清除歡迎訊息 / 設定機器人名稱 / 設定機器人頭像",
        ])
        if flags is not None:
            lines.append(f"功能狀態：{feature_status_text(flags)}")
    if is_creator:
        lines.extend(["", "創作者：保留所有管理員功能，並可管理 Bot 全域設定與部署資料。"])
    return "\n".join(lines)


def build_settings_flex(flags):
    messages = []
    for message in (
        flex("ChinoBot 圖搜功能開關", [
            settings_intro_bubble("圖搜功能開關"),
            *feature_bubbles(flags, IMAGE_ENGINE_KEYS),
        ]),
        flex("ChinoBot 其他功能開關", [
            settings_intro_bubble("其他功能開關"),
            *feature_bubbles(flags, OTHER_FEATURE_KEYS),
        ]),
        flex("ChinoBot 管理功能開關", [
            settings_intro_bubble("管理功能開關"),
            *feature_bubbles(flags, ADMIN_FEATURE_KEYS),
        ]),
    ):
        if isinstance(message, list):
            messages.extend(message)
        else:
            messages.append(message)
    return messages


def build_status_flex(flags):
    enabled = []
    disabled = []
    index = feature_index()
    for item in FEATURE_DEFINITIONS:
        target = enabled if is_enabled(flags, item["key"]) else disabled
        target.append(index[item["key"]]["name"])
    return flex("ChinoBot 功能狀態", [
        status_bubble("已開啟", enabled, "ON"),
        status_bubble("已關閉", disabled, "OFF"),
    ])


def build_version_check_flex(local_version, remote_version=None, prs=None, error=None, version_notes=""):
    prs = prs or []
    has_update = bool(remote_version and remote_version != local_version)
    if error:
        lines = ["版本檢查", f"本機版本：{local_version}", f"狀態：{error}"]
    else:
        lines = [
            "版本檢查",
            f"本機版本：{local_version}",
            f"遠端版本：{remote_version}",
            "狀態：有更新可套用" if has_update else "狀態：目前已是最新版本",
        ]
        if prs:
            lines.extend(["", "最近合併的 PR"])
            for pr in prs[:5]:
                line = f"#{pr['number']} {pr['title']}"
                if pr.get("summary"):
                    line += f"\n{pr['summary']}"
                lines.append(line)
        if version_notes:
            lines.extend(["", "版本說明"])
            lines.extend(version_notes_lines(version_notes))
    buttons = [uri_button("查看新功能 PR", GITHUB_PULLS_URL)]
    if has_update:
        buttons.append(postback_button("版本更新", "版本更新"))
    return simple_flex("ChinoBot 版本檢查", lines, footer_buttons=buttons)


def build_picsearch_api_version_check_flex(local_version, remote_version=None, error=None):
    has_update = bool(remote_version and remote_version != local_version)
    if error:
        lines = ["圖搜 API 版本檢查", f"本機版本：{local_version}", f"狀態：{error}"]
    else:
        lines = [
            "圖搜 API 版本檢查",
            f"本機版本：{local_version}",
            f"遠端版本：{remote_version}",
            "狀態：有 PicImageSearch 更新" if has_update else "狀態：目前已是最新版本",
        ]
    buttons = [postback_button("更新圖搜 API", "更新圖搜api")] if has_update else None
    return simple_flex("ChinoBot 圖搜 API 版本檢查", lines, footer_buttons=buttons)


def help_public_bubble():
    return simple_bubble([
        "一般用戶功能",
        "輸入圖搜說明可打開此模板。",
        "回覆圖片後可使用圖搜、模板搜與快捷 #1/#2/#3。",
        "可使用下載、作品解析、抽圖、圖片上傳、標註查詢與運行時間功能。",
    ], footer_buttons=[uri_button("GitHub", GITHUB_URL)])


def help_search_bubble():
    return simple_bubble([
        "圖片搜尋",
        "回覆搜圖 / 回覆搜1：SauceNAO",
        "回覆搜2：Ascii2D",
        "回覆搜3：TraceMoe",
        "回覆搜4：Yandex",
        "回覆搜5：Iqdb",
        "回覆搜6：AnimeTrace",
        "回覆搜7：GGJAV",
        "模板搜 / 模板搜1 / 模板搜2 / 模板搜3 可使用模板結果。",
    ])


def help_download_bubble():
    return simple_bubble([
        "下載功能",
        "yt:URL：YouTube 或 yt-dlp 支援站台",
        "fb:URL：Facebook 影片",
        "ig:URL：Instagram 圖片 / 影片",
        "tk:URL：TikTok 圖片 / 影片",
        "x:URL：X / Twitter 圖片 / 影片",
        "ph:URL：Pornhub 影片",
        "也可回覆含網址的訊息後輸入：回覆搜yt / fb / ig / x / ph。",
    ])


def help_gallery_bubble():
    return simple_bubble([
        "抽圖與作品解析",
        "抽圖 / 色圖：一般抽圖",
        "r18色圖：R18 抽圖",
        "tag色圖 標籤：指定標籤抽圖",
        "n:編號 / n:popular：nHentai",
        "w:編號：紳士漫畫",
        "c:編號：禁漫天堂",
        "p:作品ID 或 p:URL：Pixiv",
        "#圖片上傳：回覆圖片後上傳到 Freeimage.host",
    ])


def help_admin_bubble(flags):
    return simple_bubble([
        "管理員功能",
        "功能狀態：查看所有功能開關。",
        "功能設定：打開 postback 開關模板。",
        "功能切換 <key>：文字切換指定功能。",
        "設定歡迎訊息 內容：設定目前群組歡迎訊息。",
        "清除歡迎訊息：清除目前群組歡迎訊息。",
        "設定機器人名稱 名稱：設定目前群組訊息顯示名稱。",
        "設定機器人頭像 https://...：設定目前群組訊息頭像。",
        f"目前功能：{feature_status_text(flags)}",
    ])


def help_creator_bubble(flags):
    return simple_bubble([
        "創作者功能",
        "創作者擁有所有管理員功能。",
        "可管理部署、版本檢查、版本更新、圖搜 API 更新與全域資料。",
        "建議把 token、cookie、session 只放在 .env，不要提交到 Git。",
        f"目前功能：{feature_status_text(flags)}",
    ])


def version_notes_lines(value, limit=10):
    lines = []
    for line in str(value).replace("\r", "").split("\n"):
        line = line.strip()
        if not line:
            continue
        lines.append(line.lstrip("#").strip())
        if len(lines) >= limit:
            break
    return lines


def status_bubble(title_text, names, marker):
    lines = [title_text, "", f"共 {len(names)} 個"]
    lines.extend(f"{marker}  {name}" for name in names)
    return simple_bubble(lines)


def feature_bubbles(flags, keys):
    index = feature_index()
    return [feature_button_bubble(index[key], is_enabled(flags, key)) for key in keys if key in index]


def feature_index():
    return {item["key"]: item for item in FEATURE_DEFINITIONS}


def settings_intro_bubble(title_text):
    return bubble([
        title(title_text),
        text("按下按鈕會送出 postback，Bot 會直接切換功能，不會在聊天室洗出指令文字。"),
        text("只有管理員或創作者可以切換功能。", "#666666"),
    ])


def feature_button_bubble(item, enabled):
    state = "開啟" if enabled else "關閉"
    return {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#fff7fb"}, "footer": {"backgroundColor": "#fff7fb"}},
        "body": box([
            title(item["name"]),
            text(f"狀態：{state}", "#16a34a" if enabled else "#dc2626"),
            text(f"指令：{item['commands']}", "#555555"),
            text(item["description"], "#777777"),
        ]),
        "footer": footer_buttons([
            postback_button("切換", f"功能切換 {item['key']}", {"action": "toggle_feature", "key": item["key"]})
        ]),
    }


def simple_flex(alt_text, lines, footer_buttons=None):
    body = simple_bubble(lines)
    message = {"type": "flex", "altText": alt_text, "contents": body}
    if footer_buttons:
        message["contents"]["footer"] = {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": footer_buttons,
        }
    return message


def simple_bubble(lines, footer_buttons=None):
    contents = [title(lines[0])]
    for line in lines[1:]:
        contents.append(text(line or " ", "#555555"))
    bubble_data = {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#fff7fb"}, "footer": {"backgroundColor": "#fff7fb"}},
        "body": box(contents[:45]),
    }
    if footer_buttons:
        bubble_data["footer"] = {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": footer_buttons,
        }
    return bubble_data


def feature_status_text(flags):
    enabled_count = sum(1 for item in FEATURE_DEFINITIONS if is_enabled(flags, item["key"]))
    return f"{enabled_count}/{len(FEATURE_DEFINITIONS)} 開啟"


def flex(alt_text, bubbles):
    messages = []
    for index in range(0, len(bubbles), 10):
        messages.append({
            "type": "flex",
            "altText": alt_text if index == 0 else f"{alt_text} {index // 10 + 1}",
            "contents": {"type": "carousel", "contents": bubbles[index:index + 10]},
        })
    return messages[0] if len(messages) == 1 else messages


def bubble(contents):
    return {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#fff7fb"}},
        "body": box(contents),
    }


def box(contents):
    return {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "backgroundColor": "#fff7fb",
        "paddingAll": "18px",
        "contents": contents,
    }


def title(value):
    return {
        "type": "text",
        "text": str(value),
        "weight": "bold",
        "size": "lg",
        "color": "#5b3b73",
        "wrap": True,
    }


def text(value, color="#333333"):
    return {
        "type": "text",
        "text": str(value),
        "size": "sm",
        "color": color,
        "wrap": True,
    }


def footer_buttons(buttons):
    return {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "contents": buttons,
    }


def uri_button(label, uri):
    return {
        "type": "button",
        "style": "link",
        "color": "#f08ab8",
        "height": "sm",
        "action": {"type": "uri", "label": label, "uri": uri},
    }


def postback_button(label, display_text, data=None):
    data = data or {"cmd": display_text}
    return {
        "type": "button",
        "style": "primary",
        "color": "#f08ab8",
        "height": "sm",
        "action": {
            "type": "postback",
            "label": label,
            "data": encode_postback(data),
        },
    }


def command_button(label, command):
    return postback_button(label, command)


def encode_postback(data):
    return urlencode(data)
